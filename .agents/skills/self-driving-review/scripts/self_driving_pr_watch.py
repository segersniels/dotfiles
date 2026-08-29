#!/usr/bin/env python3
"""Poll one GitHub PR for events owned by Self-driving Review."""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

STATE_VERSION = 1
DEFAULT_POLL_SECONDS = 30
DEFAULT_MAX_CONSECUTIVE_ERRORS = 5
DEFAULT_MAX_WAIT_SECONDS = 15
DEFAULT_SETTLE_SECONDS = 5
DEFAULT_MAX_SETTLE_SECONDS = 20
MARKER_RE = re.compile(r"<!--\s*self-driving-review\s+([^>]*)-->", re.IGNORECASE)
ATTRIBUTE_RE = re.compile(r"([a-zA-Z][a-zA-Z0-9_-]*)=([^\s>]+)")
PR_URL_RE = re.compile(r"^https?://[^/]+/([^/]+)/([^/]+)/pull/(\d+)(?:/.*)?$")


class WatchError(RuntimeError):
    pass


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Poll a GitHub PR for new heads, replies in Self-driving Review "
            "threads, thread-state changes, and terminal PR state."
        )
    )
    parser.add_argument("--pr", required=True, help="PR URL, PR number, or 'auto'")
    parser.add_argument("--repo", help="OWNER/REPO override for a number or auto")
    parser.add_argument("--state-file", help="Persistent JSON state path")
    parser.add_argument(
        "--reviewed-head",
        help="Exact reviewed HEAD for a new state file",
    )
    parser.add_argument(
        "--once", action="store_true", help="Emit one snapshot and exit"
    )
    parser.add_argument(
        "--watch", action="store_true", help="Continuously emit JSONL events"
    )
    parser.add_argument(
        "--wait-for-events",
        action="store_true",
        help=(
            "Wait for pending events, collect a short event burst, emit one "
            "bounded result, and exit"
        ),
    )
    parser.add_argument(
        "--ack-event",
        action="append",
        default=[],
        help="Acknowledge a completed event by ID; repeatable",
    )
    parser.add_argument(
        "--requeue-event",
        action="append",
        default=[],
        help="Move an acknowledged event back to pending; repeatable",
    )
    parser.add_argument(
        "--mark-reviewed",
        metavar="SHA",
        help="Set the reviewed HEAD after verifying the current remote HEAD",
    )
    parser.add_argument(
        "--poll-seconds",
        type=int,
        default=DEFAULT_POLL_SECONDS,
        help=f"Polling interval in seconds (default: {DEFAULT_POLL_SECONDS})",
    )
    parser.add_argument(
        "--max-consecutive-errors",
        type=int,
        default=DEFAULT_MAX_CONSECUTIVE_ERRORS,
        help=(
            "Stop after this many consecutive GitHub read failures "
            f"(default: {DEFAULT_MAX_CONSECUTIVE_ERRORS})"
        ),
    )
    parser.add_argument(
        "--max-wait-seconds",
        type=int,
        default=DEFAULT_MAX_WAIT_SECONDS,
        help=(
            "Maximum quiet wait before an idle result "
            f"(default: {DEFAULT_MAX_WAIT_SECONDS})"
        ),
    )
    parser.add_argument(
        "--settle-seconds",
        type=int,
        default=DEFAULT_SETTLE_SECONDS,
        help=(
            "Quiet time after the latest new event before returning its batch "
            f"(default: {DEFAULT_SETTLE_SECONDS})"
        ),
    )
    parser.add_argument(
        "--max-settle-seconds",
        type=int,
        default=DEFAULT_MAX_SETTLE_SECONDS,
        help=(
            f"Maximum total event-batching time (default: {DEFAULT_MAX_SETTLE_SECONDS})"
        ),
    )
    args = parser.parse_args()

    control_modes = sum(
        bool(value)
        for value in (args.ack_event, args.requeue_event, args.mark_reviewed)
    )
    if control_modes > 1:
        parser.error("Use only one state update operation at a time")
    run_modes = sum(
        bool(value) for value in (args.watch, args.once, args.wait_for_events)
    )
    if run_modes > 1:
        parser.error("Use only one of --watch, --once, or --wait-for-events")
    if control_modes and run_modes:
        parser.error(
            "State updates cannot be combined with --watch, --once, or --wait-for-events"
        )
    if args.poll_seconds <= 0:
        parser.error("--poll-seconds must be greater than zero")
    if args.max_consecutive_errors <= 0:
        parser.error("--max-consecutive-errors must be greater than zero")
    if args.max_wait_seconds <= 0:
        parser.error("--max-wait-seconds must be greater than zero")
    if args.settle_seconds < 0:
        parser.error("--settle-seconds must be zero or greater")
    if args.max_settle_seconds <= 0:
        parser.error("--max-settle-seconds must be greater than zero")
    if args.max_settle_seconds < args.settle_seconds:
        parser.error("--max-settle-seconds must be at least --settle-seconds")
    return args


def run_gh(args):
    command = ["gh", *args]
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as err:
        raise WatchError("GitHub CLI `gh` is not installed") from err
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise WatchError(
            f"gh command failed ({completed.returncode}): {' '.join(command)}: {detail}"
        )
    return completed.stdout


def gh_json(args):
    output = run_gh(args)
    try:
        return json.loads(output)
    except json.JSONDecodeError as err:
        raise WatchError(f"gh returned invalid JSON for: {' '.join(args)}") from err


def repo_from_pr_url(value):
    match = PR_URL_RE.match(value)
    if not match:
        return None
    return f"{match.group(1)}/{match.group(2)}"


def parse_pr_spec(value):
    if value == "auto":
        return None, None
    if value.isdigit():
        return value, None
    repo = repo_from_pr_url(value)
    if repo:
        return value, repo
    raise WatchError("--pr must be a PR URL, PR number, or 'auto'")


def resolve_pr(pr_spec, repo_override=None):
    value, url_repo = parse_pr_spec(pr_spec)
    command = ["pr", "view"]
    if value:
        command.append(value)
    repo = repo_override or url_repo
    if repo:
        command.extend(["--repo", repo])
    command.extend(
        [
            "--json",
            "number,url,state,mergedAt,closedAt,headRefName,headRefOid",
        ]
    )
    data = gh_json(command)
    if not isinstance(data, dict):
        raise WatchError("Unexpected payload from `gh pr view`")
    url = str(data.get("url") or "")
    repo = repo or repo_from_pr_url(url)
    if not repo:
        raise WatchError("Unable to determine OWNER/REPO for the PR")
    head_sha = str(data.get("headRefOid") or "")
    if not head_sha:
        raise WatchError("GitHub did not return the PR HEAD SHA")
    state = str(data.get("state") or "")
    merged = bool(data.get("mergedAt"))
    closed = bool(data.get("closedAt")) or state.upper() == "CLOSED"
    return {
        "repo": repo,
        "number": int(data["number"]),
        "url": url,
        "state": state,
        "merged": merged,
        "closed": closed,
        "head_branch": str(data.get("headRefName") or ""),
        "head_sha": head_sha,
    }


def default_state_file(pr):
    slug = re.sub(r"[^a-zA-Z0-9_.-]+", "-", pr["repo"])
    return Path(f"/tmp/codex-self-driving-review-{slug}-pr{pr['number']}.json")


def new_state(pr):
    return {
        "version": STATE_VERSION,
        "pr": {
            "repo": pr["repo"],
            "number": pr["number"],
            "url": pr["url"],
        },
        "started_at": int(time.time()),
        "last_snapshot_at": None,
        "last_reviewed_head": None,
        "last_seen_head": None,
        "reviewed_head_source": None,
        "automation_login": None,
        "owned_threads": {},
        "seen_review_activity": {},
        "pending_events": {},
        "acknowledged_events": {},
        "transition_sequence": 0,
    }


def load_state(path, pr):
    if not path.exists():
        return new_state(pr), True
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        raise WatchError(f"State file is not valid JSON: {path}") from err
    if not isinstance(state, dict):
        raise WatchError(f"State file must contain a JSON object: {path}")
    if state.get("version") != STATE_VERSION:
        raise WatchError(
            f"Unsupported state version in {path}: {state.get('version')!r}"
        )
    identity = state.get("pr") or {}
    if identity.get("repo") != pr["repo"] or identity.get("number") != pr["number"]:
        raise WatchError(f"State file belongs to a different PR: {path}")
    for key in (
        "owned_threads",
        "seen_review_activity",
        "pending_events",
        "acknowledged_events",
    ):
        if not isinstance(state.get(key), dict):
            state[key] = {}
    return state, False


def save_state(path, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(state, indent=2, sort_keys=True) + "\n"
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f"{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(payload)
        os.replace(temporary_path, path)
    except Exception:
        try:
            temporary_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise


def paginate_rest(endpoint):
    items = []
    page = 1
    while True:
        separator = "&" if "?" in endpoint else "?"
        payload = gh_json(["api", f"{endpoint}{separator}per_page=100&page={page}"])
        if not isinstance(payload, list):
            raise WatchError(f"Unexpected list payload from GitHub: {endpoint}")
        items.extend(payload)
        if len(payload) < 100:
            return items
        page += 1


def fetch_thread_states(pr):
    owner, repo_name = pr["repo"].split("/", 1)
    query = """
query($owner:String!, $repo:String!, $number:Int!, $cursor:String) {
  repository(owner:$owner, name:$repo) {
    pullRequest(number:$number) {
      reviewThreads(first:100, after:$cursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          isResolved
          isOutdated
          comments(first:1) {
            nodes { databaseId }
          }
        }
      }
    }
  }
}
""".strip()
    states = {}
    cursor = None
    while True:
        command = [
            "api",
            "graphql",
            "-f",
            f"query={query}",
            "-F",
            f"owner={owner}",
            "-F",
            f"repo={repo_name}",
            "-F",
            f"number={pr['number']}",
        ]
        if cursor:
            command.extend(["-F", f"cursor={cursor}"])
        payload = gh_json(command)
        try:
            threads = payload["data"]["repository"]["pullRequest"]["reviewThreads"]
        except (KeyError, TypeError) as err:
            raise WatchError("Unexpected GraphQL reviewThreads payload") from err
        for thread in threads.get("nodes") or []:
            comments = (thread.get("comments") or {}).get("nodes") or []
            if not comments:
                continue
            root_id = str(comments[0].get("databaseId") or "")
            if not root_id:
                continue
            states[root_id] = {
                "node_id": str(thread.get("id") or ""),
                "is_resolved": bool(thread.get("isResolved")),
                "is_outdated": bool(thread.get("isOutdated")),
            }
        page_info = threads.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            return states
        cursor = page_info.get("endCursor")
        if not cursor:
            raise WatchError("GitHub omitted the next review-thread cursor")


def extract_login(value):
    if isinstance(value, dict):
        return str(value.get("login") or "")
    return ""


def fetch_authenticated_login():
    payload = gh_json(["api", "user"])
    if not isinstance(payload, dict):
        raise WatchError("Unexpected payload from `gh api user`")
    login = str(payload.get("login") or "")
    if not login:
        raise WatchError("GitHub did not return the authenticated login")
    return login


def parse_marker(body):
    matches = MARKER_RE.findall(str(body or ""))
    if not matches:
        return None
    attributes = dict(ATTRIBUTE_RE.findall(matches[-1]))
    issue_id = attributes.get("issue")
    if not issue_id:
        return None
    attributes["issue"] = issue_id
    return attributes


def fetch_reviews(pr):
    return paginate_rest(f"repos/{pr['repo']}/pulls/{pr['number']}/reviews")


def normalize_comments(pr, reviews):
    review_states = {
        str(review.get("id") or ""): str(review.get("state") or "").upper()
        for review in reviews
        if isinstance(review, dict)
    }
    raw_comments = paginate_rest(f"repos/{pr['repo']}/pulls/{pr['number']}/comments")
    comments = []
    for comment in raw_comments:
        if not isinstance(comment, dict):
            continue
        review_id = str(comment.get("pull_request_review_id") or "")
        if review_states.get(review_id) == "PENDING":
            continue
        comment_id = str(comment.get("id") or "")
        if not comment_id:
            continue
        root_id = str(comment.get("in_reply_to_id") or comment_id)
        line = comment.get("line")
        if line is None:
            line = comment.get("original_line")
        comments.append(
            {
                "id": comment_id,
                "root_id": root_id,
                "author": extract_login(comment.get("user")),
                "body": str(comment.get("body") or ""),
                "created_at": str(comment.get("created_at") or ""),
                "updated_at": str(comment.get("updated_at") or ""),
                "path": str(comment.get("path") or ""),
                "line": line,
                "url": str(comment.get("html_url") or ""),
                "commit_id": str(comment.get("commit_id") or ""),
            }
        )
    comments.sort(key=lambda item: (item["created_at"], item["id"]))
    return comments


def normalize_review_activity(pr, reviews, comments):
    activity = []
    for comment in comments:
        activity.append(
            {
                "activity_id": f"inline_comment:{comment['id']}",
                "kind": "inline_comment",
                **comment,
            }
        )

    for review in reviews:
        if not isinstance(review, dict):
            continue
        review_id = str(review.get("id") or "")
        state = str(review.get("state") or "").upper()
        if not review_id or state == "PENDING":
            continue
        body = str(review.get("body") or "")
        if not body and state == "COMMENTED":
            continue
        activity.append(
            {
                "activity_id": f"review:{review_id}",
                "kind": "review",
                "id": review_id,
                "root_id": None,
                "author": extract_login(review.get("user")),
                "body": body,
                "state": state,
                "created_at": str(
                    review.get("submitted_at") or review.get("created_at") or ""
                ),
                "updated_at": str(review.get("submitted_at") or ""),
                "path": "",
                "line": None,
                "url": str(review.get("html_url") or ""),
                "commit_id": str(review.get("commit_id") or ""),
            }
        )

    issue_comments = paginate_rest(f"repos/{pr['repo']}/issues/{pr['number']}/comments")
    for comment in issue_comments:
        if not isinstance(comment, dict):
            continue
        comment_id = str(comment.get("id") or "")
        if not comment_id:
            continue
        activity.append(
            {
                "activity_id": f"issue_comment:{comment_id}",
                "kind": "issue_comment",
                "id": comment_id,
                "root_id": None,
                "author": extract_login(comment.get("user")),
                "body": str(comment.get("body") or ""),
                "state": None,
                "created_at": str(comment.get("created_at") or ""),
                "updated_at": str(comment.get("updated_at") or ""),
                "path": "",
                "line": None,
                "url": str(comment.get("html_url") or ""),
                "commit_id": "",
            }
        )

    activity.sort(key=lambda item: (item["created_at"], item["activity_id"]))
    return activity


def fetch_pr_commits(pr):
    raw_commits = paginate_rest(f"repos/{pr['repo']}/pulls/{pr['number']}/commits")
    commits = []
    for item in raw_commits:
        if not isinstance(item, dict):
            continue
        sha = str(item.get("sha") or "")
        if not sha:
            continue
        commit = item.get("commit") if isinstance(item.get("commit"), dict) else {}
        message = str(commit.get("message") or "")
        title, separator, body = message.partition("\n")
        commits.append(
            {
                "sha": sha,
                "title": title,
                "body": body.lstrip("\n") if separator else "",
                "author": extract_login(item.get("author")),
                "url": str(item.get("html_url") or ""),
            }
        )
    return commits


def build_owned_threads(comments, thread_states, automation_login):
    by_root = {}
    for comment in comments:
        by_root.setdefault(comment["root_id"], []).append(comment)

    owned = {}
    for root_id, thread_comments in by_root.items():
        root = next((item for item in thread_comments if item["id"] == root_id), None)
        if not root:
            continue
        root_marker = parse_marker(root["body"])
        if not root_marker or root["author"].casefold() != automation_login.casefold():
            continue

        latest_owned_index = -1
        latest_marker = root_marker
        for index, comment in enumerate(thread_comments):
            marker = parse_marker(comment["body"])
            is_automated_marker = (
                marker
                and marker.get("issue") == root_marker["issue"]
                and comment["author"].casefold() == automation_login.casefold()
            )
            if is_automated_marker:
                latest_owned_index = index
                latest_marker = marker

        state = thread_states.get(root_id) or {}
        external_replies = [
            comment
            for index, comment in enumerate(thread_comments)
            if index > latest_owned_index
            and not (
                comment["author"].casefold() == automation_login.casefold()
                and parse_marker(comment["body"])
            )
        ]
        owned[root_id] = {
            "issue_id": root_marker["issue"],
            "root_id": root_id,
            "path": root["path"],
            "line": root["line"],
            "url": root["url"],
            "review_head": latest_marker.get("head") or root_marker.get("head"),
            "latest_marker_created_at": thread_comments[latest_owned_index][
                "created_at"
            ],
            "disposition": latest_marker.get("disposition") or "open",
            "is_resolved": state.get("is_resolved"),
            "is_outdated": state.get("is_outdated"),
            "thread_node_id": state.get("node_id"),
            "latest_comment_id": thread_comments[-1]["id"],
            "external_replies": external_replies,
        }
    return owned


def next_transition_id(state, event_type, root_id):
    state["transition_sequence"] = int(state.get("transition_sequence") or 0) + 1
    return f"{event_type}:{root_id}:{state['transition_sequence']}"


def add_pending_event(state, event):
    event_id = event["event_id"]
    if event_id in state["acknowledged_events"]:
        return False
    if event_id in state["pending_events"]:
        return False
    state["pending_events"][event_id] = event
    return True


def add_head_event(state, pr, commits):
    reviewed = state.get("last_reviewed_head")
    if not reviewed or reviewed == pr["head_sha"]:
        return
    for event_id, event in list(state["pending_events"].items()):
        if event.get("event") == "head_changed":
            del state["pending_events"][event_id]
    event_id = f"head_changed:{reviewed}:{pr['head_sha']}"
    reviewed_index = next(
        (index for index, commit in enumerate(commits) if commit["sha"] == reviewed),
        None,
    )
    if reviewed_index is None:
        new_commits = commits
        history_status = "reviewed_head_not_in_current_pr_history"
    else:
        new_commits = commits[reviewed_index + 1 :]
        history_status = "linear_from_reviewed_head"
    add_pending_event(
        state,
        {
            "event": "head_changed",
            "event_id": event_id,
            "from_head": reviewed,
            "to_head": pr["head_sha"],
            "history_status": history_status,
            "commits": new_commits,
            "created_at": int(time.time()),
        },
    )


def add_reply_events(state, owned_threads):
    for thread in owned_threads.values():
        for reply in thread["external_replies"]:
            event_id = f"owned_thread_reply:{thread['root_id']}:{reply['id']}"
            add_pending_event(
                state,
                {
                    "event": "owned_thread_reply",
                    "event_id": event_id,
                    "issue_id": thread["issue_id"],
                    "thread_root_id": thread["root_id"],
                    "comment_id": reply["id"],
                    "author": reply["author"],
                    "body": reply["body"],
                    "path": reply["path"],
                    "line": reply["line"],
                    "url": reply["url"],
                    "created_at": reply["created_at"],
                },
            )


def add_external_review_events(
    state, review_activity, owned_threads, fresh_state, automation_login
):
    seen = state.get("seen_review_activity") or {}
    owned_root_ids = set(owned_threads)
    for item in review_activity:
        activity_id = item["activity_id"]
        was_seen = activity_id in seen
        seen[activity_id] = item["updated_at"] or item["created_at"]
        if fresh_state or was_seen:
            continue
        if item["kind"] == "inline_comment" and item["root_id"] in owned_root_ids:
            continue
        is_own_marked_activity = item[
            "author"
        ].casefold() == automation_login.casefold() and MARKER_RE.search(item["body"])
        if is_own_marked_activity:
            continue
        event_id = f"external_review_activity:{activity_id}"
        add_pending_event(
            state,
            {
                "event": "external_review_activity",
                "event_id": event_id,
                "activity_kind": item["kind"],
                "activity_id": activity_id,
                "author": item["author"],
                "body": item["body"],
                "review_state": item.get("state"),
                "thread_root_id": item["root_id"],
                "path": item["path"],
                "line": item["line"],
                "url": item["url"],
                "commit_id": item["commit_id"],
                "created_at": item["created_at"],
            },
        )
    state["seen_review_activity"] = seen


def add_thread_transition_events(state, owned_threads, fresh_state):
    previous_threads = state.get("owned_threads") or {}
    if fresh_state:
        return
    for root_id, current in owned_threads.items():
        previous = previous_threads.get(root_id)
        if not previous:
            continue
        transitions = (
            ("is_resolved", False, True, "thread_resolved"),
            ("is_resolved", True, False, "thread_reopened"),
            ("is_outdated", False, True, "finding_outdated"),
            ("is_outdated", True, False, "finding_current"),
        )
        for field, old_value, new_value, event_type in transitions:
            if previous.get(field) is old_value and current.get(field) is new_value:
                event_id = next_transition_id(state, event_type, root_id)
                add_pending_event(
                    state,
                    {
                        "event": event_type,
                        "event_id": event_id,
                        "issue_id": current["issue_id"],
                        "thread_root_id": root_id,
                        "path": current["path"],
                        "line": current["line"],
                        "created_at": int(time.time()),
                    },
                )


def add_terminal_event(state, pr):
    if not pr["merged"] and not pr["closed"]:
        return
    event_type = "pr_merged" if pr["merged"] else "pr_closed"
    event_id = f"{event_type}:{pr['head_sha']}"
    add_pending_event(
        state,
        {
            "event": event_type,
            "event_id": event_id,
            "head_sha": pr["head_sha"],
            "url": pr["url"],
            "created_at": int(time.time()),
        },
    )


def compact_thread(thread):
    return {
        key: value
        for key, value in thread.items()
        if key not in {"external_replies", "latest_marker_created_at"}
    }


def latest_marker_head(owned_threads):
    candidates = [
        thread for thread in owned_threads.values() if thread.get("review_head")
    ]
    if not candidates:
        return None
    latest = max(
        candidates,
        key=lambda thread: (
            thread.get("latest_marker_created_at") or "",
            thread["root_id"],
        ),
    )
    return latest["review_head"]


def collect_snapshot(args):
    pr = resolve_pr(args.pr, repo_override=args.repo)
    state_path = Path(args.state_file) if args.state_file else default_state_file(pr)
    state, fresh_state = load_state(state_path, pr)
    pending_event_ids_before = set(state["pending_events"])

    automation_login = state.get("automation_login")
    if not automation_login:
        automation_login = fetch_authenticated_login()
        state["automation_login"] = automation_login

    thread_states = fetch_thread_states(pr)
    reviews = fetch_reviews(pr)
    comments = normalize_comments(pr, reviews)
    review_activity = normalize_review_activity(pr, reviews, comments)
    owned_threads = build_owned_threads(comments, thread_states, automation_login)

    if fresh_state:
        if args.reviewed_head:
            state["last_reviewed_head"] = args.reviewed_head
            state["reviewed_head_source"] = "argument"
        else:
            marker_head = latest_marker_head(owned_threads)
            state["last_reviewed_head"] = marker_head or pr["head_sha"]
            state["reviewed_head_source"] = (
                "marker" if marker_head else "current_baseline"
            )
    elif args.reviewed_head and args.reviewed_head != state.get("last_reviewed_head"):
        raise WatchError(
            "--reviewed-head does not match existing state; use --mark-reviewed after verification"
        )

    commits = []
    if state.get("last_reviewed_head") != pr["head_sha"]:
        commits = fetch_pr_commits(pr)
    add_head_event(state, pr, commits)
    add_reply_events(state, owned_threads)
    add_external_review_events(
        state, review_activity, owned_threads, fresh_state, automation_login
    )
    add_thread_transition_events(state, owned_threads, fresh_state)
    add_terminal_event(state, pr)

    state["owned_threads"] = {
        root_id: compact_thread(thread) for root_id, thread in owned_threads.items()
    }
    state["last_seen_head"] = pr["head_sha"]
    state["last_snapshot_at"] = int(time.time())
    save_state(state_path, state)

    pending_events = sorted(
        state["pending_events"].values(),
        key=lambda event: (str(event.get("created_at") or ""), event["event_id"]),
    )
    return {
        "pr": pr,
        "last_reviewed_head": state.get("last_reviewed_head"),
        "reviewed_head_source": state.get("reviewed_head_source"),
        "automation_login": automation_login,
        "owned_issues": sorted(
            (compact_thread(thread) for thread in owned_threads.values()),
            key=lambda thread: (thread["issue_id"], thread["root_id"]),
        ),
        "pending_events": pending_events,
        "new_event_ids": sorted(
            set(state["pending_events"]) - pending_event_ids_before
        ),
        "state_file": str(state_path),
    }


def update_event_state(args, requeue=False):
    pr = resolve_pr(args.pr, repo_override=args.repo)
    state_path = Path(args.state_file) if args.state_file else default_state_file(pr)
    state, fresh_state = load_state(state_path, pr)
    if fresh_state:
        raise WatchError(f"No watcher state exists yet: {state_path}")
    event_ids = args.requeue_event if requeue else args.ack_event
    updated = []
    for event_id in event_ids:
        if requeue:
            event = state["acknowledged_events"].pop(event_id, None)
            if not event:
                raise WatchError(f"Acknowledged event not found: {event_id}")
            state["pending_events"][event_id] = event
        else:
            event = state["pending_events"].get(event_id)
            if not event:
                raise WatchError(f"Pending event not found: {event_id}")
            if event.get("event") == "head_changed":
                raise WatchError("Use --mark-reviewed for a head_changed event")
            state["acknowledged_events"][event_id] = state["pending_events"].pop(
                event_id
            )
        updated.append(event_id)
    save_state(state_path, state)
    return {
        "event": "events_requeued" if requeue else "events_acknowledged",
        "event_ids": updated,
        "state_file": str(state_path),
    }


def mark_reviewed(args):
    pr = resolve_pr(args.pr, repo_override=args.repo)
    if args.mark_reviewed != pr["head_sha"]:
        raise WatchError(
            f"Refusing stale reviewed head {args.mark_reviewed}; current PR HEAD is {pr['head_sha']}"
        )
    state_path = Path(args.state_file) if args.state_file else default_state_file(pr)
    state, fresh_state = load_state(state_path, pr)
    if fresh_state:
        raise WatchError(f"No watcher state exists yet: {state_path}")
    state["last_reviewed_head"] = args.mark_reviewed
    state["reviewed_head_source"] = "mark-reviewed"
    removed = []
    for event_id, event in list(state["pending_events"].items()):
        if event.get("event") == "head_changed":
            removed.append(event_id)
            del state["pending_events"][event_id]
    state["last_snapshot_at"] = int(time.time())
    save_state(state_path, state)
    return {
        "event": "reviewed_head_updated",
        "head_sha": args.mark_reviewed,
        "cleared_events": removed,
        "state_file": str(state_path),
    }


def print_json(value):
    print(json.dumps(value, sort_keys=True), flush=True)


def wait_result(status, snapshot, started_at, monotonic, **extra):
    result = {
        "event": "wait_result",
        "status": status,
        "waited_seconds": round(max(0, monotonic() - started_at), 3),
    }
    if snapshot:
        result.update(
            {
                "pr": snapshot["pr"],
                "last_reviewed_head": snapshot.get("last_reviewed_head"),
                "state_file": snapshot["state_file"],
            }
        )
        if status in {"events", "terminal"}:
            result["events"] = snapshot["pending_events"]
    result.update(extra)
    return result


def wait_for_event_batch(
    args,
    collect=collect_snapshot,
    monotonic=time.monotonic,
    sleep=time.sleep,
):
    started_at = monotonic()
    idle_deadline = started_at + args.max_wait_seconds
    settle_deadline = None
    hard_settle_deadline = None
    event_ids = set()
    consecutive_errors = 0
    recovered_errors = 0
    snapshot = None
    first_successful_snapshot = True

    while True:
        now = monotonic()
        if snapshot is not None and settle_deadline is None and now >= idle_deadline:
            return wait_result(
                "idle",
                snapshot,
                started_at,
                monotonic,
                recovered_poll_errors=recovered_errors,
            )

        try:
            snapshot = collect(args)
        except WatchError as err:
            consecutive_errors += 1
            now = monotonic()
            if event_ids and snapshot:
                return wait_result(
                    "events",
                    snapshot,
                    started_at,
                    monotonic,
                    batch_warning="settle_poll_failed",
                    error=str(err),
                    consecutive_errors=consecutive_errors,
                    recovered_poll_errors=recovered_errors,
                )
            if (
                consecutive_errors >= args.max_consecutive_errors
                or now >= idle_deadline
            ):
                return wait_result(
                    "blocked",
                    snapshot,
                    started_at,
                    monotonic,
                    reason="github_read_failures",
                    error=str(err),
                    consecutive_errors=consecutive_errors,
                )
            sleep(min(args.poll_seconds, max(0, idle_deadline - now)))
            continue

        if consecutive_errors:
            recovered_errors += consecutive_errors
            consecutive_errors = 0

        now = monotonic()
        pr = snapshot["pr"]
        current_event_ids = {event["event_id"] for event in snapshot["pending_events"]}
        newly_discovered_ids = set(snapshot.get("new_event_ids") or [])

        if pr["merged"] or pr["closed"]:
            reason = "pr_merged" if pr["merged"] else "pr_closed"
            return wait_result(
                "terminal",
                snapshot,
                started_at,
                monotonic,
                reason=reason,
                recovered_poll_errors=recovered_errors,
            )

        if current_event_ids:
            if first_successful_snapshot and not newly_discovered_ids:
                return wait_result(
                    "events",
                    snapshot,
                    started_at,
                    monotonic,
                    recovered_poll_errors=recovered_errors,
                )

            new_event_ids = current_event_ids - event_ids
            if settle_deadline is None:
                hard_settle_deadline = now + args.max_settle_seconds
                settle_deadline = min(
                    now + args.settle_seconds,
                    hard_settle_deadline,
                )
            elif new_event_ids:
                settle_deadline = min(
                    now + args.settle_seconds,
                    hard_settle_deadline,
                )
            event_ids = current_event_ids

            if now >= settle_deadline or now >= hard_settle_deadline:
                return wait_result(
                    "events",
                    snapshot,
                    started_at,
                    monotonic,
                    recovered_poll_errors=recovered_errors,
                )

            next_deadline = min(settle_deadline, hard_settle_deadline)
        else:
            if now >= idle_deadline:
                return wait_result(
                    "idle",
                    snapshot,
                    started_at,
                    monotonic,
                    recovered_poll_errors=recovered_errors,
                )
            next_deadline = idle_deadline

        first_successful_snapshot = False
        sleep(min(args.poll_seconds, max(0, next_deadline - now)))


def run_watch(args):
    emitted_event_ids = set()
    consecutive_errors = 0
    first_snapshot = True
    while True:
        try:
            snapshot = collect_snapshot(args)
        except WatchError as err:
            consecutive_errors += 1
            print_json(
                {
                    "event": "poll_error",
                    "error": str(err),
                    "consecutive_errors": consecutive_errors,
                    "max_consecutive_errors": args.max_consecutive_errors,
                }
            )
            if consecutive_errors >= args.max_consecutive_errors:
                print_json(
                    {
                        "event": "watcher_blocked",
                        "reason": "consecutive_github_read_failures",
                        "consecutive_errors": consecutive_errors,
                    }
                )
                return 1
            time.sleep(args.poll_seconds)
            continue

        if consecutive_errors:
            print_json(
                {
                    "event": "poll_recovered",
                    "previous_consecutive_errors": consecutive_errors,
                }
            )
            consecutive_errors = 0

        if first_snapshot:
            print_json({"event": "snapshot", "payload": snapshot})
            first_snapshot = False

        for event in snapshot["pending_events"]:
            if event["event_id"] in emitted_event_ids:
                continue
            print_json(event)
            emitted_event_ids.add(event["event_id"])

        pr = snapshot["pr"]
        if pr["merged"] or pr["closed"]:
            return 0
        time.sleep(args.poll_seconds)


def main():
    args = parse_args()
    try:
        if args.ack_event:
            print_json(update_event_state(args, requeue=False))
            return 0
        if args.requeue_event:
            print_json(update_event_state(args, requeue=True))
            return 0
        if args.mark_reviewed:
            print_json(mark_reviewed(args))
            return 0
        if args.wait_for_events:
            result = wait_for_event_batch(args)
            print_json(result)
            return 1 if result["status"] == "blocked" else 0
        if args.watch:
            return run_watch(args)
        print_json({"event": "snapshot", "payload": collect_snapshot(args)})
        return 0
    except WatchError as err:
        sys.stderr.write(f"self_driving_pr_watch.py error: {err}\n")
        return 1
    except KeyboardInterrupt:
        sys.stderr.write("self_driving_pr_watch.py interrupted\n")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
