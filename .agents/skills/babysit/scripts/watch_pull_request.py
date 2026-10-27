#!/usr/bin/env python3
"""Watches a GitHub pull request and prints one short update for each change worth acting on.

Each update is a block of lines on stdout, so a harness that turns output lines into
notifications (for example the Claude Code Monitor tool) can run it without a filter.
The watch state survives restarts, so a new run continues where the last one stopped.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.parse import urlparse

DEFAULT_POLL_SECONDS = 60

# Stops the watch after this many failed GitHub reads in a row.
READ_FAILURE_LIMIT = 8

# Stops the watch after this many comment-only updates in a row, to break bot reply loops.
COMMENT_ONLY_LIMIT = 10

# Limits how many checks or comments one update lists.
LISTED_ITEMS = 10

# Limits the length of a comment snippet in an update.
SNIPPET_LENGTH = 200

# Lists the check conclusions that count as a failure.
FAILED_CONCLUSIONS = {"failure", "timed_out", "cancelled", "action_required", "startup_failure", "stale"}


class GhError(RuntimeError):
    pass


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--pr", default="auto", help="PR URL, PR number, or auto for the current branch")
    parser.add_argument("--repo", help="OWNER/REPO, needed with a bare PR number outside the repository")
    parser.add_argument("--poll-seconds", type=int, default=DEFAULT_POLL_SECONDS)
    parser.add_argument("--state-file", help="Path to the watch state file")
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Discard saved state and report only changes after this start",
    )
    return parser.parse_args(argv)


# Caches the ETag and body of each REST GET. GitHub does not count a 304 reply against the rate limit.
_ETAG_CACHE = {}


def gh_api_get(endpoint):
    """Reads one REST endpoint with `gh api` and reuses the cached body when GitHub replies 304."""
    cached = _ETAG_CACHE.get(endpoint)
    cmd = ["gh", "api", "-i"]
    if cached:
        cmd.extend(["-H", f"If-None-Match: {cached[0]}"])
    cmd.append(endpoint)
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError as err:
        raise GhError("`gh` command not found") from err

    parts = re.split(r"\r?\n\r?\n", proc.stdout, maxsplit=1)
    head = parts[0]
    body = parts[1].strip() if len(parts) > 1 else ""
    status_line = head.splitlines()[0] if head else ""

    # `gh api` exits with an error for a 304 reply, so read the status line first.
    if cached and " 304" in status_line:
        return cached[1]

    if proc.returncode != 0:
        detail = (proc.stderr or body or status_line).strip().splitlines()
        raise GhError(f"gh api {endpoint} failed: {detail[0] if detail else proc.returncode}")

    data = json.loads(body) if body else None
    etag = re.search(r"(?im)^etag:\s*(.+?)\s*$", head)
    if etag:
        _ETAG_CACHE[endpoint] = (etag.group(1), data)
    return data


def gh_api_list(endpoint, list_key=None):
    """Reads every page of a REST list endpoint."""
    items = []
    page = 1
    while True:
        separator = "&" if "?" in endpoint else "?"
        payload = gh_api_get(f"{endpoint}{separator}per_page=100&page={page}")
        if list_key and isinstance(payload, dict):
            payload = payload.get(list_key) or []
        if not isinstance(payload, list):
            raise GhError(f"Unexpected payload from gh api {endpoint}")

        items.extend(payload)
        if len(payload) < 100:
            return items
        page += 1


def resolve_target(pr_spec, repo):
    """Finds the OWNER/REPO and number of the PR to watch."""
    if pr_spec.isdigit() and repo:
        return repo, int(pr_spec)

    url = pr_spec
    if not urlparse(pr_spec).netloc:
        cmd = ["gh", "pr", "view", "--json", "url", "--jq", ".url"]
        if pr_spec != "auto":
            cmd.insert(3, pr_spec)
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            raise GhError(f"Cannot find the PR: {proc.stderr.strip()}")
        url = proc.stdout.strip()

    parts = [part for part in urlparse(url).path.split("/") if part]
    if len(parts) < 4 or parts[2] != "pull" or not parts[3].isdigit():
        raise GhError(f"Not a pull request URL: {url}")
    return repo or f"{parts[0]}/{parts[1]}", int(parts[3])


def login_of(user):
    return str((user or {}).get("login") or "")


def check_from_run(run):
    """Converts a check run to the check shape that the watch compares."""
    if run.get("status") != "completed":
        result = "pending"
    elif run.get("conclusion") in FAILED_CONCLUSIONS:
        result = "failed"
    else:
        result = "passed"
    return {"name": str(run.get("name") or ""), "result": result, "url": run.get("details_url") or run.get("html_url")}


def check_from_status(status):
    """Converts a commit status to the check shape that the watch compares."""
    results = {"pending": "pending", "success": "passed"}
    return {
        "name": str(status.get("context") or ""),
        "result": results.get(status.get("state"), "failed"),
        "url": status.get("target_url"),
    }


def remarks_from(issue_comments, review_comments, reviews):
    """Builds one list of published comments and reviews."""
    unpublished_reviews = {review.get("id") for review in reviews if review.get("state") == "PENDING"}
    remarks = []

    for comment in issue_comments:
        remarks.append(
            {
                "kind": "issue_comment",
                "id": str(comment["id"]),
                "author": login_of(comment.get("user")),
                "created_at": comment.get("created_at") or "",
                "body": comment.get("body") or "",
                "url": comment.get("html_url"),
            }
        )

    for comment in review_comments:
        if comment.get("pull_request_review_id") in unpublished_reviews:
            continue
        remarks.append(
            {
                "kind": "review_comment",
                "id": str(comment["id"]),
                "thread_id": str(comment.get("in_reply_to_id") or comment["id"]),
                "author": login_of(comment.get("user")),
                "created_at": comment.get("created_at") or "",
                "body": comment.get("body") or "",
                "path": comment.get("path"),
                "line": comment.get("line") or comment.get("original_line"),
                "url": comment.get("html_url"),
            }
        )

    for review in reviews:
        state = review.get("state") or ""
        body = review.get("body") or ""

        # A comment-only review without a body only wraps inline comments, which are listed already.
        if state == "PENDING" or (state == "COMMENTED" and not body.strip()):
            continue
        remarks.append(
            {
                "kind": "review",
                "id": str(review["id"]),
                "author": login_of(review.get("user")),
                "created_at": review.get("submitted_at") or "",
                "body": body,
                "state": state.lower(),
                "url": review.get("html_url"),
            }
        )

    return remarks


def read_pull_request(repo, number):
    """Reads the PR, the checks on its head commit, and its published comments."""
    pr = gh_api_get(f"repos/{repo}/pulls/{number}")
    head_sha = pr["head"]["sha"]
    head_commit = gh_api_get(f"repos/{repo}/commits/{head_sha}")
    check_runs = gh_api_list(f"repos/{repo}/commits/{head_sha}/check-runs", list_key="check_runs")
    statuses = gh_api_list(f"repos/{repo}/commits/{head_sha}/status", list_key="statuses")
    reviews = gh_api_list(f"repos/{repo}/pulls/{number}/reviews")
    issue_comments = gh_api_list(f"repos/{repo}/issues/{number}/comments")
    review_comments = gh_api_list(f"repos/{repo}/pulls/{number}/comments")

    return {
        "number": number,
        "url": pr.get("html_url"),
        "base_branch": pr["base"]["ref"],
        "head_sha": head_sha,
        "head_author": login_of(head_commit.get("author")) or head_commit["commit"]["author"]["name"],
        "merged": bool(pr.get("merged") or pr.get("merged_at")),
        "closed": pr.get("state") == "closed",
        "mergeable": pr.get("mergeable"),
        "mergeable_state": pr.get("mergeable_state") or "",
        "checks": [check_from_run(run) for run in check_runs] + [check_from_status(status) for status in statuses],
        "remarks": remarks_from(issue_comments, review_comments, reviews),
    }


def initial_state(pr):
    """Builds a state that treats everything on the PR right now as already reported."""
    latest = max((remark["created_at"] for remark in pr["remarks"]), default="")
    checks = pr["checks"]
    return {
        "head_sha": pr["head_sha"],
        "failed_checks": [check["name"] for check in checks if check["result"] == "failed"],
        "checks_passed": bool(checks) and all(check["result"] == "passed" for check in checks),
        "remarks_through": latest,
        "remark_ids": [remark["id"] for remark in pr["remarks"] if remark["created_at"] == latest],
        "conflicting": pr["mergeable"] is False,
        "ready_reported": pr["mergeable_state"] == "clean",
        "comment_only_updates": 0,
    }


def evaluate(state, pr, viewer):
    """Compares the PR with the saved state and returns the changes and the next state."""
    changes = []
    head_moved = pr["head_sha"] != state["head_sha"]

    # The watcher's own pushes are not news; a push by someone else is.
    if head_moved and pr["head_author"].lower() != viewer.lower():
        changes.append({"kind": "pushed", "author": pr["head_author"]})

    failed_checks = [] if head_moved else state["failed_checks"]
    checks_passed = False if head_moved else state["checks_passed"]

    # An empty list is a head that has no checks yet, so keep what was known.
    checks = pr["checks"]
    if checks:
        failed = [check for check in checks if check["result"] == "failed"]
        newly_failed = [check for check in failed if check["name"] not in failed_checks]
        if newly_failed:
            changes.append({"kind": "checks_failed", "checks": newly_failed})
        failed_checks = [check["name"] for check in failed]

        passed_now = all(check["result"] == "passed" for check in checks)
        if passed_now and not checks_passed:
            changes.append({"kind": "checks_passed", "count": len(checks)})
        checks_passed = passed_now

    # Hosts stamp comments to the second, so a comment at the boundary time is told apart by ID.
    through = state["remarks_through"]
    fresh = [
        remark
        for remark in pr["remarks"]
        if (remark["created_at"] > through or (remark["created_at"] == through and remark["id"] not in state["remark_ids"]))
        and remark["author"].lower() != viewer.lower()
    ]
    if fresh:
        changes.append({"kind": "remarks", "remarks": sorted(fresh, key=lambda remark: remark["created_at"])})

    latest = max([through] + [remark["created_at"] for remark in fresh])
    remark_ids = state["remark_ids"] if latest == through else []
    remark_ids = remark_ids + [remark["id"] for remark in fresh if remark["created_at"] == latest]

    if pr["mergeable"] is False and not state["conflicting"]:
        changes.append({"kind": "conflicting"})

    # GitHub returns null while it computes mergeability after a push; only a clear answer changes it.
    conflicting = state["conflicting"] if pr["mergeable"] is None else pr["mergeable"] is False

    ready_reported = state["ready_reported"]
    if pr["mergeable_state"] == "clean" and not ready_reported:
        changes.append({"kind": "ready"})
        ready_reported = True

    comments_only = bool(changes) and all(change["kind"] == "remarks" for change in changes)
    if comments_only:
        comment_only_updates = state["comment_only_updates"] + 1
    elif changes:
        comment_only_updates = 0
    else:
        comment_only_updates = state["comment_only_updates"]

    next_state = {
        "head_sha": pr["head_sha"],
        "failed_checks": failed_checks,
        "checks_passed": checks_passed,
        "remarks_through": latest,
        "remark_ids": remark_ids,
        "conflicting": conflicting,
        "ready_reported": ready_reported,
        "comment_only_updates": comment_only_updates,
    }
    return changes, next_state


def snippet(body):
    """Shortens a comment body to one line without HTML comments."""
    text = " ".join(re.sub(r"<!--[\s\S]*?-->", " ", body).split())
    if len(text) <= SNIPPET_LENGTH:
        return text
    return text[: SNIPPET_LENGTH - 3] + "..."


def listed(items, line):
    lines = [line(item) for item in items[:LISTED_ITEMS]]
    if len(items) > LISTED_ITEMS:
        lines.append(f"  - and {len(items) - LISTED_ITEMS} more")
    return lines


def remark_line(remark):
    where = ""
    if remark.get("path"):
        where = f" on {remark['path']}" + (f":{remark['line']}" if remark.get("line") else "")

    body = snippet(remark["body"])
    said = f'"{body}"' if body else ""
    if remark.get("state"):
        said = f"{remark['state']}: {said}" if said else remark["state"]

    ids = f"{remark['kind']} {remark['id']}"
    if remark.get("thread_id"):
        ids += f", thread {remark['thread_id']}"
    return f"  - {remark['author']}{where}: {said} {remark['url']} ({ids})"


def change_lines(change, pr):
    kind = change["kind"]
    if kind == "pushed":
        return [f"- {change['author'] or 'Someone'} pushed new commits. The head is now {pr['head_sha'][:7]}."]
    if kind == "checks_failed":
        return ["- Checks failed:"] + listed(change["checks"], lambda check: f"  - {check['name']} {check['url'] or ''}".rstrip())
    if kind == "checks_passed":
        return [f"- All {change['count']} checks passed."]
    if kind == "remarks":
        count = len(change["remarks"])
        return [f"- {count} new {'comment' if count == 1 else 'comments'}:"] + listed(change["remarks"], remark_line)
    if kind == "conflicting":
        return [f"- The branch now conflicts with {pr['base_branch']}."]
    return ["- The PR is ready to merge."]


def format_update(pr, changes):
    """Builds the update text for one poll."""
    lines = [f"Update on PR #{pr['number']} ({pr['url']}) at {pr['head_sha'][:7]}:"]
    for change in changes:
        lines.extend(change_lines(change, pr))
    return "\n".join(lines)


def status_line(pr, resumed):
    """Builds the first line of a run, which shows that the watch works."""
    counts = {"passed": 0, "failed": 0, "pending": 0}
    for check in pr["checks"]:
        counts[check["result"]] += 1
    verb = "Resumed watching" if resumed else "Watching"
    return (
        f"{verb} PR #{pr['number']} ({pr['url']}) at {pr['head_sha'][:7]}: "
        f"{counts['passed']} checks passed, {counts['failed']} failed, {counts['pending']} pending; "
        f"merge state {pr['mergeable_state'] or 'unknown'}."
    )


def emit(text):
    sys.stdout.write(text + "\n")
    sys.stdout.flush()


def load_state(path):
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def save_state(path, state):
    """Writes the state through a temporary file, so a killed watcher never leaves half a file."""
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=path.name, suffix=".tmp")
    with os.fdopen(fd, "w") as tmp_file:
        json.dump(state, tmp_file, indent=2)
    os.replace(tmp_name, path)


def run(args):
    repo, number = resolve_target(args.pr, args.repo)
    viewer = gh_api_get("user")["login"]
    default_path = Path(tempfile.gettempdir()) / f"watch-pull-request-{repo.replace('/', '-')}-{number}.json"
    state_path = Path(args.state_file) if args.state_file else default_path
    state = None if args.fresh else load_state(state_path)
    first_poll = True
    read_failures = 0

    while True:
        try:
            pr = read_pull_request(repo, number)
            read_failures = 0
        except (GhError, KeyError, ValueError) as err:
            read_failures += 1
            print(f"Read failed ({read_failures}/{READ_FAILURE_LIMIT}): {err}", file=sys.stderr, flush=True)
            if read_failures >= READ_FAILURE_LIMIT:
                emit(f"Stopped watching PR #{number}: GitHub reads failed {read_failures} times in a row. Last error: {err}")
                return 1
            time.sleep(args.poll_seconds)
            continue

        if pr["merged"] or pr["closed"]:
            emit(f"PR #{number} ({pr['url']}) was {'merged' if pr['merged'] else 'closed'}. Stopped watching.")
            state_path.unlink(missing_ok=True)
            return 0

        if first_poll:
            emit(status_line(pr, resumed=state is not None))
            first_poll = False

        if state is None:
            state = initial_state(pr)
        else:
            changes, state = evaluate(state, pr, viewer)
            if changes:
                emit(format_update(pr, changes))

        save_state(state_path, state)
        if state["comment_only_updates"] >= COMMENT_ONLY_LIMIT:
            emit(f"Stopped watching PR #{number} after {COMMENT_ONLY_LIMIT} comment-only updates in a row. Start the watcher again to resume.")
            state["comment_only_updates"] = 0
            save_state(state_path, state)
            return 0

        time.sleep(args.poll_seconds)


def main():
    try:
        return run(parse_args())
    except GhError as err:
        emit(f"Cannot start the watch: {err}")
        return 1
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
