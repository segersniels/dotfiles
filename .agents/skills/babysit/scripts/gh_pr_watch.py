#!/usr/bin/env python3
"""Watch GitHub PR CI and review activity for PR babysitting workflows."""

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

FAILED_RUN_CONCLUSIONS = {
    "failure",
    "timed_out",
    "cancelled",
    "action_required",
    "startup_failure",
    "stale",
}
PENDING_CHECK_STATES = {
    "QUEUED",
    "IN_PROGRESS",
    "PENDING",
    "WAITING",
    "REQUESTED",
}
MERGE_BLOCKING_REVIEW_DECISIONS = {
    "REVIEW_REQUIRED",
    "CHANGES_REQUESTED",
}
MERGE_CONFLICT_OR_BLOCKING_STATES = {
    "BLOCKED",
    "DIRTY",
    "DRAFT",
    "UNKNOWN",
}
REVIEW_STATE_VERSION = 2
REVIEW_ITEM_KINDS = ("issue_comment", "review_comment", "review")


class GhCommandError(RuntimeError):
    pass


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Normalize PR/CI/review state for PR babysitting and optionally "
            "trigger flaky reruns."
        )
    )
    parser.add_argument("--pr", default="auto", help="auto, PR number, or PR URL")
    parser.add_argument("--repo", help="Optional OWNER/REPO override")
    parser.add_argument("--poll-seconds", type=int, default=30, help="Watch poll interval")
    parser.add_argument(
        "--max-flaky-retries",
        type=int,
        default=3,
        help="Max rerun cycles per head SHA before stop recommendation",
    )
    parser.add_argument("--state-file", help="Path to state JSON file")
    parser.add_argument("--once", action="store_true", help="Emit one snapshot and exit")
    parser.add_argument("--watch", action="store_true", help="Continuously emit JSONL snapshots")
    parser.add_argument(
        "--retry-failed-now",
        action="store_true",
        help="Rerun failed jobs for current failed workflow runs when policy allows",
    )
    parser.add_argument(
        "--ack-review-item",
        action="append",
        default=[],
        metavar="KIND:ID",
        help="Mark a handled review item as acknowledged (repeatable)",
    )
    parser.add_argument(
        "--requeue-review-item",
        action="append",
        default=[],
        metavar="KIND:ID",
        help="Move a previously seen review item back to pending (repeatable)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable output (default behavior for --once and --retry-failed-now)",
    )
    args = parser.parse_args()

    if args.poll_seconds <= 0:
        parser.error("--poll-seconds must be > 0")
    if args.max_flaky_retries < 0:
        parser.error("--max-flaky-retries must be >= 0")
    if args.watch and args.retry_failed_now:
        parser.error("--watch cannot be combined with --retry-failed-now")
    if args.ack_review_item and args.requeue_review_item:
        parser.error("--ack-review-item cannot be combined with --requeue-review-item")
    if (args.ack_review_item or args.requeue_review_item) and (
        args.once or args.watch or args.retry_failed_now
    ):
        parser.error("review item state updates cannot be combined with watcher actions")
    if (
        not args.once
        and not args.watch
        and not args.retry_failed_now
        and not args.ack_review_item
        and not args.requeue_review_item
    ):
        args.once = True
    return args


def _format_gh_error(cmd, err):
    stdout = (err.stdout or "").strip()
    stderr = (err.stderr or "").strip()
    parts = [f"GitHub CLI command failed: {' '.join(cmd)}"]
    if stdout:
        parts.append(f"stdout: {stdout}")
    if stderr:
        parts.append(f"stderr: {stderr}")
    return "\n".join(parts)


def gh_text(args, repo=None):
    cmd = ["gh"]
    # `gh api` does not accept `-R/--repo` on all gh versions. The watcher's
    # API calls use explicit endpoints (e.g. repos/{owner}/{repo}/...), so the
    # repo flag is unnecessary there.
    if repo and (not args or args[0] != "api"):
        cmd.extend(["-R", repo])
    cmd.extend(args)
    try:
        proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
    except FileNotFoundError as err:
        raise GhCommandError("`gh` command not found") from err
    except subprocess.CalledProcessError as err:
        raise GhCommandError(_format_gh_error(cmd, err)) from err
    return proc.stdout


def gh_json(args, repo=None):
    raw = gh_text(args, repo=repo).strip()
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError as err:
        raise GhCommandError(f"Failed to parse JSON from gh output for {' '.join(args)}") from err


# ETag and parsed body for each REST GET endpoint. GitHub does not count a
# 304 Not Modified reply against the rate limit, so unchanged polls are free.
_ETAG_CACHE = {}
HTTP_HEADER_END_PATTERN = re.compile(r"\r?\n\r?\n")


def gh_api_get(endpoint):
    cached = _ETAG_CACHE.get(endpoint)
    cmd = ["gh", "api", "-i"]
    if cached:
        cmd.extend(["-H", f"If-None-Match: {cached[0]}"])
    cmd.append(endpoint)
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError as err:
        raise GhCommandError("`gh` command not found") from err

    parts = HTTP_HEADER_END_PATTERN.split(proc.stdout, maxsplit=1)
    head = parts[0]
    body = parts[1] if len(parts) > 1 else ""
    status_line = head.splitlines()[0] if head else ""
    # `gh api` exits with an error for a 304 reply, so read the status line.
    if cached and " 304" in status_line:
        return cached[1]
    if proc.returncode != 0:
        raise GhCommandError(
            _format_gh_error(cmd, subprocess.CalledProcessError(proc.returncode, cmd, proc.stdout, proc.stderr))
        )

    body = body.strip()
    if not body:
        return None
    try:
        data = json.loads(body)
    except json.JSONDecodeError as err:
        raise GhCommandError(f"Failed to parse JSON from gh api {endpoint}") from err
    etag = re.search(r"(?im)^etag:\s*(.+?)\s*$", head)
    if etag:
        _ETAG_CACHE[endpoint] = (etag.group(1), data)
    return data


def parse_pr_spec(pr_spec):
    if pr_spec == "auto":
        return {"mode": "auto", "value": None}
    if re.fullmatch(r"\d+", pr_spec):
        return {"mode": "number", "value": pr_spec}
    parsed = urlparse(pr_spec)
    if parsed.scheme and parsed.netloc and "/pull/" in parsed.path:
        return {"mode": "url", "value": pr_spec}
    raise ValueError("--pr must be 'auto', a PR number, or a PR URL")


_PR_TARGET_CACHE = {}


def resolve_pr_target(pr_spec, repo_override=None):
    # Return (OWNER/REPO, number). Only `auto` or a number without --repo needs
    # `gh pr view`, which uses GraphQL, so ask once per process.
    key = (pr_spec, repo_override)
    if key in _PR_TARGET_CACHE:
        return _PR_TARGET_CACHE[key]

    parsed = parse_pr_spec(pr_spec)
    if parsed["mode"] == "url":
        pr_url = parsed["value"]
    elif parsed["mode"] == "number" and repo_override:
        pr_url = None
        target = (repo_override, int(parsed["value"]))
    else:
        cmd = ["pr", "view"]
        if parsed["value"] is not None:
            cmd.append(parsed["value"])
        cmd.extend(["--json", "url"])
        data = gh_json(cmd, repo=repo_override)
        if not isinstance(data, dict):
            raise GhCommandError("Unexpected PR payload from `gh pr view`")
        pr_url = str(data.get("url") or "")

    if pr_url is not None:
        repo = repo_override or extract_repo_from_pr_url(pr_url)
        number = extract_number_from_pr_url(pr_url)
        if not repo or number is None:
            raise GhCommandError("Unable to determine OWNER/REPO and number for the PR")
        target = (repo, number)

    _PR_TARGET_CACHE[key] = target
    return target


def rest_mergeable(value):
    # Map the REST boolean to the GraphQL enum that the snapshot exposes.
    if value is True:
        return "MERGEABLE"
    if value is False:
        return "CONFLICTING"
    return "UNKNOWN"


def review_decision_from_reviews(reviews):
    # REST has no reviewDecision. Use the latest decisive review of each
    # reviewer. A missing required review shows as BLOCKED in merge_state_status.
    latest_by_reviewer = {}
    for review in reviews:
        if not isinstance(review, dict):
            continue
        state = str(review.get("state") or "").upper()
        if state not in {"APPROVED", "CHANGES_REQUESTED", "DISMISSED"}:
            continue
        latest_by_reviewer[extract_login(review.get("user"))] = state
    decisions = set(latest_by_reviewer.values())
    if "CHANGES_REQUESTED" in decisions:
        return "CHANGES_REQUESTED"
    if "APPROVED" in decisions:
        return "APPROVED"
    return ""


def resolve_pr(pr_spec, repo_override=None):
    repo, number = resolve_pr_target(pr_spec, repo_override)
    data = gh_api_get(f"repos/{repo}/pulls/{number}")
    if not isinstance(data, dict):
        raise GhCommandError("Unexpected payload from pulls API")
    reviews = gh_api_list_paginated(comment_endpoints(repo, number)["review"])

    merged = bool(data.get("merged") or data.get("merged_at"))
    closed = bool(data.get("closed_at")) or str(data.get("state") or "").lower() == "closed"
    head = data.get("head") or {}

    return {
        "number": int(data.get("number") or number),
        "url": str(data.get("html_url") or ""),
        "repo": repo,
        "head_sha": str(head.get("sha") or ""),
        "head_branch": str(head.get("ref") or ""),
        "state": "MERGED" if merged else str(data.get("state") or "").upper(),
        "merged": merged,
        "closed": closed,
        "mergeable": rest_mergeable(data.get("mergeable")),
        "merge_state_status": str(data.get("mergeable_state") or "").upper(),
        "review_decision": review_decision_from_reviews(reviews),
    }


def extract_repo_from_pr_url(pr_url):
    parsed = urlparse(pr_url)
    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) >= 4 and parts[2] == "pull":
        return f"{parts[0]}/{parts[1]}"
    return None


def extract_number_from_pr_url(pr_url):
    parts = [p for p in urlparse(pr_url).path.split("/") if p]
    if len(parts) >= 4 and parts[2] == "pull" and parts[3].isdigit():
        return int(parts[3])
    return None


def load_state(path):
    if path.exists():
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError as err:
            raise RuntimeError(f"State file is not valid JSON: {path}") from err
        if not isinstance(data, dict):
            raise RuntimeError(f"State file must contain an object: {path}")
        return data, False
    return {
        "pr": {},
        "started_at": None,
        "last_seen_head_sha": None,
        "retries_by_sha": {},
        "seen_issue_comment_ids": [],
        "seen_review_comment_ids": [],
        "seen_review_ids": [],
        "review_state_version": REVIEW_STATE_VERSION,
        "pending_issue_comment_ids": [],
        "pending_review_comment_ids": [],
        "pending_review_ids": [],
        "acknowledged_issue_comment_ids": [],
        "acknowledged_review_comment_ids": [],
        "acknowledged_review_ids": [],
        "last_snapshot_at": None,
    }, True


def save_state(path, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(state, indent=2, sort_keys=True) + "\n"
    fd, tmp_name = tempfile.mkstemp(prefix=f"{path.name}.", suffix=".tmp", dir=path.parent)
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as tmp_file:
            tmp_file.write(payload)
        os.replace(tmp_path, path)
    except Exception:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise


def default_state_file_for(pr):
    repo_slug = pr["repo"].replace("/", "-")
    return Path(f"/tmp/codex-babysit-pr-{repo_slug}-pr{pr['number']}.json")


def check_bucket(conclusion):
    # Same buckets as `gh pr checks`.
    if conclusion in {"SUCCESS", "NEUTRAL"}:
        return "pass"
    if conclusion == "SKIPPED":
        return "skipping"
    if conclusion == "CANCELLED":
        return "cancel"
    return "fail"


def normalize_check_run(run):
    status = str(run.get("status") or "").upper()
    if status != "COMPLETED":
        state, bucket = status, "pending"
    else:
        state = str(run.get("conclusion") or "").upper()
        bucket = check_bucket(state)
    return {
        "name": str(run.get("name") or ""),
        "state": state,
        "bucket": bucket,
        "link": str(run.get("details_url") or run.get("html_url") or ""),
    }


def normalize_commit_status(status):
    state = str(status.get("state") or "").upper()
    if state == "PENDING":
        bucket = "pending"
    elif state == "SUCCESS":
        bucket = "pass"
    else:
        bucket = "fail"
    return {
        "name": str(status.get("context") or ""),
        "state": state,
        "bucket": bucket,
        "link": str(status.get("target_url") or ""),
    }


def get_pr_checks(repo, head_sha):
    # REST replacement for `gh pr checks`, which uses GraphQL. The check-runs
    # endpoint returns only the latest run for each check name.
    check_runs = gh_api_list_paginated(
        f"repos/{repo}/commits/{head_sha}/check-runs", list_key="check_runs"
    )
    statuses = gh_api_list_paginated(f"repos/{repo}/commits/{head_sha}/status", list_key="statuses")
    return [normalize_check_run(run) for run in check_runs if isinstance(run, dict)] + [
        normalize_commit_status(status) for status in statuses if isinstance(status, dict)
    ]


def is_pending_check(check):
    bucket = str(check.get("bucket") or "").lower()
    state = str(check.get("state") or "").upper()
    return bucket == "pending" or state in PENDING_CHECK_STATES


def summarize_checks(checks):
    pending_count = 0
    failed_count = 0
    passed_count = 0
    for check in checks:
        bucket = str(check.get("bucket") or "").lower()
        if is_pending_check(check):
            pending_count += 1
        if bucket == "fail":
            failed_count += 1
        if bucket == "pass":
            passed_count += 1
    return {
        "pending_count": pending_count,
        "failed_count": failed_count,
        "passed_count": passed_count,
        "all_terminal": pending_count == 0,
    }


def get_workflow_runs_for_sha(repo, head_sha):
    data = gh_api_get(f"repos/{repo}/actions/runs?head_sha={head_sha}&per_page=100")
    if not isinstance(data, dict):
        raise GhCommandError("Unexpected payload from actions runs API")
    runs = data.get("workflow_runs") or []
    if not isinstance(runs, list):
        raise GhCommandError("Expected `workflow_runs` to be a list")
    return runs


def failed_runs_from_workflow_runs(runs, head_sha):
    failed_runs = []
    for run in runs:
        if not isinstance(run, dict):
            continue
        if str(run.get("head_sha") or "") != head_sha:
            continue
        conclusion = str(run.get("conclusion") or "")
        if conclusion not in FAILED_RUN_CONCLUSIONS:
            continue
        failed_runs.append(
            {
                "run_id": run.get("id"),
                "workflow_name": run.get("name") or run.get("display_title") or "",
                "status": str(run.get("status") or ""),
                "conclusion": conclusion,
                "html_url": str(run.get("html_url") or ""),
            }
        )
    failed_runs.sort(key=lambda item: (str(item.get("workflow_name") or ""), str(item.get("run_id") or "")))
    return failed_runs


def get_jobs_for_run(repo, run_id):
    data = gh_api_get(f"repos/{repo}/actions/runs/{run_id}/jobs?per_page=100")
    if not isinstance(data, dict):
        raise GhCommandError("Unexpected payload from actions run jobs API")
    jobs = data.get("jobs") or []
    if not isinstance(jobs, list):
        raise GhCommandError("Expected `jobs` to be a list")
    return jobs


ACTIONS_RUN_ID_PATTERN = re.compile(r"/actions/runs/(\d+)")


def run_ids_with_failed_checks(checks):
    # Each check links to its Actions job. The run ID in that link lets the
    # watcher fetch jobs only for runs that already have a failed job.
    run_ids = set()
    for check in checks:
        if str(check.get("bucket") or "").lower() != "fail":
            continue
        match = ACTIONS_RUN_ID_PATTERN.search(str(check.get("link") or ""))
        if match:
            run_ids.add(int(match.group(1)))
    return run_ids


def failed_jobs_from_workflow_runs(repo, runs, head_sha, failed_check_run_ids=frozenset()):
    failed_jobs = []
    for run in runs:
        if not isinstance(run, dict):
            continue
        if str(run.get("head_sha") or "") != head_sha:
            continue
        run_id = run.get("id")
        if run_id in (None, ""):
            continue
        run_status = str(run.get("status") or "")
        run_conclusion = str(run.get("conclusion") or "")
        if run_status.lower() == "completed":
            if run_conclusion not in FAILED_RUN_CONCLUSIONS:
                continue
        elif int(run_id) not in failed_check_run_ids:
            # Skip the jobs API for running workflows without a failed job.
            # One call per active run per poll exhausts the rate limit fast.
            continue
        jobs = get_jobs_for_run(repo, run_id)
        for job in jobs:
            if not isinstance(job, dict):
                continue
            conclusion = str(job.get("conclusion") or "")
            if conclusion not in FAILED_RUN_CONCLUSIONS:
                continue
            job_id = job.get("id")
            logs_endpoint = None
            if job_id not in (None, ""):
                logs_endpoint = f"repos/{repo}/actions/jobs/{job_id}/logs"
            failed_jobs.append(
                {
                    "run_id": run_id,
                    "workflow_name": run.get("name") or run.get("display_title") or "",
                    "run_status": run_status,
                    "run_conclusion": run_conclusion,
                    "job_id": job_id,
                    "job_name": str(job.get("name") or ""),
                    "status": str(job.get("status") or ""),
                    "conclusion": conclusion,
                    "html_url": str(job.get("html_url") or ""),
                    "logs_endpoint": logs_endpoint,
                }
            )
    failed_jobs.sort(
        key=lambda item: (
            str(item.get("workflow_name") or ""),
            str(item.get("job_name") or ""),
            str(item.get("job_id") or ""),
        )
    )
    return failed_jobs


def comment_endpoints(repo, pr_number):
    return {
        "issue_comment": f"repos/{repo}/issues/{pr_number}/comments",
        "review_comment": f"repos/{repo}/pulls/{pr_number}/comments",
        "review": f"repos/{repo}/pulls/{pr_number}/reviews",
    }


def gh_api_list_paginated(endpoint, repo=None, per_page=100, list_key=None):
    # `list_key` names the list inside an object payload, such as `check_runs`.
    items = []
    page = 1
    while True:
        sep = "&" if "?" in endpoint else "?"
        page_endpoint = f"{endpoint}{sep}per_page={per_page}&page={page}"
        payload = gh_api_get(page_endpoint)
        if payload is None:
            break
        if list_key is not None and isinstance(payload, dict):
            payload = payload.get(list_key) or []
        if not isinstance(payload, list):
            raise GhCommandError(f"Unexpected paginated payload from gh api {endpoint}")
        items.extend(payload)
        if len(payload) < per_page:
            break
        page += 1
    return items


def normalize_issue_comments(items):
    out = []
    for item in items:
        if not isinstance(item, dict):
            continue
        out.append(
            {
                "kind": "issue_comment",
                "id": str(item.get("id") or ""),
                "author": extract_login(item.get("user")),
                "author_association": str(item.get("author_association") or ""),
                "created_at": str(item.get("created_at") or ""),
                "body": str(item.get("body") or ""),
                "path": None,
                "line": None,
                "url": str(item.get("html_url") or ""),
            }
        )
    return out


def normalize_review_comments(items, review_states):
    out = []
    for item in items:
        if not isinstance(item, dict):
            continue
        review_id = str(item.get("pull_request_review_id") or "")
        if review_states.get(review_id) == "PENDING":
            continue
        line = item.get("line")
        if line is None:
            line = item.get("original_line")
        out.append(
            {
                "kind": "review_comment",
                "id": str(item.get("id") or ""),
                "thread_root_id": str(item.get("in_reply_to_id") or item.get("id") or ""),
                "author": extract_login(item.get("user")),
                "author_association": str(item.get("author_association") or ""),
                "created_at": str(item.get("created_at") or ""),
                "body": str(item.get("body") or ""),
                "path": item.get("path"),
                "line": line,
                "url": str(item.get("html_url") or ""),
            }
        )
    return out


def normalize_reviews(items):
    out = []
    for item in items:
        if not isinstance(item, dict):
            continue
        if str(item.get("state") or "").upper() == "PENDING":
            continue
        out.append(
            {
                "kind": "review",
                "id": str(item.get("id") or ""),
                "author": extract_login(item.get("user")),
                "author_association": str(item.get("author_association") or ""),
                "created_at": str(item.get("submitted_at") or item.get("created_at") or ""),
                "body": str(item.get("body") or ""),
                "path": None,
                "line": None,
                "url": str(item.get("html_url") or ""),
            }
        )
    return out


def extract_login(user_obj):
    if isinstance(user_obj, dict):
        return str(user_obj.get("login") or "")
    return ""


def review_state_key(status, kind):
    return f"{status}_{kind}_ids"


def ensure_review_tracking_state(
    state,
    pending_review_comment_ids=None,
    pending_review_ids=None,
):
    if state.get("review_state_version") != REVIEW_STATE_VERSION:
        pending_review_comment_ids = set(pending_review_comment_ids or [])
        pending_review_ids = set(pending_review_ids or [])
        legacy_seen = {
            "issue_comment": {
                str(item_id)
                for item_id in state.get("seen_issue_comment_ids") or []
            },
            "review_comment": {
                str(item_id)
                for item_id in state.get("seen_review_comment_ids") or []
            }
            - pending_review_comment_ids,
            "review": {
                str(item_id)
                for item_id in state.get("seen_review_ids") or []
            }
            - pending_review_ids,
        }
        for kind in REVIEW_ITEM_KINDS:
            state[review_state_key("pending", kind)] = []
            state[review_state_key("acknowledged", kind)] = sorted(
                legacy_seen[kind]
            )
        state["review_state_version"] = REVIEW_STATE_VERSION

    for kind in REVIEW_ITEM_KINDS:
        for status in ("pending", "acknowledged"):
            key = review_state_key(status, kind)
            if not isinstance(state.get(key), list):
                state[key] = []


def validate_review_items(review_items):
    validated = []
    for kind, item_id in review_items:
        if kind not in REVIEW_ITEM_KINDS:
            raise ValueError(
                f"Unknown review item kind {kind!r}; expected one of "
                f"{', '.join(REVIEW_ITEM_KINDS)}"
            )
        item_id = str(item_id)
        if not item_id:
            raise ValueError("Review item ID cannot be empty")
        validated.append((kind, item_id))
    return validated


def acknowledge_review_items(state, review_items):
    ensure_review_tracking_state(state)
    acknowledged = []
    for kind, item_id in validate_review_items(review_items):
        pending_key = review_state_key("pending", kind)
        acknowledged_key = review_state_key("acknowledged", kind)
        pending_ids = {str(value) for value in state[pending_key]}
        acknowledged_ids = {str(value) for value in state[acknowledged_key]}
        pending_ids.discard(item_id)
        acknowledged_ids.add(item_id)
        state[pending_key] = sorted(pending_ids)
        state[acknowledged_key] = sorted(acknowledged_ids)
        acknowledged.append({"kind": kind, "id": item_id})
    return acknowledged


def requeue_review_items(state, review_items):
    ensure_review_tracking_state(state)
    requeued = []
    for kind, item_id in validate_review_items(review_items):
        pending_key = review_state_key("pending", kind)
        acknowledged_key = review_state_key("acknowledged", kind)
        pending_ids = {str(value) for value in state[pending_key]}
        acknowledged_ids = {str(value) for value in state[acknowledged_key]}
        acknowledged_ids.discard(item_id)
        pending_ids.add(item_id)
        state[pending_key] = sorted(pending_ids)
        state[acknowledged_key] = sorted(acknowledged_ids)
        requeued.append({"kind": kind, "id": item_id})
    return requeued


def parse_review_item_refs(values):
    parsed = []
    for value in values:
        kind, separator, item_id = value.partition(":")
        if not separator:
            raise ValueError(
                f"Invalid review item {value!r}; expected KIND:ID"
            )
        parsed.append((kind, item_id))
    return validate_review_items(parsed)


def fetch_new_review_items(pr, state, fresh_state):
    repo = pr["repo"]
    pr_number = pr["number"]
    endpoints = comment_endpoints(repo, pr_number)

    issue_payload = gh_api_list_paginated(endpoints["issue_comment"], repo=repo)
    review_comment_payload = gh_api_list_paginated(endpoints["review_comment"], repo=repo)
    review_payload = gh_api_list_paginated(endpoints["review"], repo=repo)

    issue_items = normalize_issue_comments(issue_payload)
    review_states = {
        str(item.get("id")): str(item.get("state") or "").upper()
        for item in review_payload
        if isinstance(item, dict) and item.get("id") not in (None, "")
    }
    pending_review_ids = {
        review_id for review_id, review_state in review_states.items() if review_state == "PENDING"
    }
    pending_review_comment_ids = {
        str(item.get("id"))
        for item in review_comment_payload
        if isinstance(item, dict)
        and item.get("id") not in (None, "")
        and str(item.get("pull_request_review_id") or "") in pending_review_ids
    }
    review_comment_items = normalize_review_comments(review_comment_payload, review_states)
    review_items = normalize_reviews(review_payload)
    all_items = issue_items + review_comment_items + review_items

    seen_issue = {str(x) for x in state.get("seen_issue_comment_ids") or []}
    seen_review_comment = {str(x) for x in state.get("seen_review_comment_ids") or []}
    seen_review = {str(x) for x in state.get("seen_review_ids") or []}
    seen_review_comment.difference_update(pending_review_comment_ids)
    seen_review.difference_update(pending_review_ids)
    ensure_review_tracking_state(
        state,
        pending_review_comment_ids=pending_review_comment_ids,
        pending_review_ids=pending_review_ids,
    )

    pending_by_kind = {
        kind: {
            str(item_id)
            for item_id in state.get(review_state_key("pending", kind)) or []
        }
        for kind in REVIEW_ITEM_KINDS
    }
    acknowledged_by_kind = {
        kind: {
            str(item_id)
            for item_id in state.get(review_state_key("acknowledged", kind)) or []
        }
        for kind in REVIEW_ITEM_KINDS
    }
    published_ids_by_kind = {
        kind: {
            str(item.get("id"))
            for item in all_items
            if item.get("kind") == kind and item.get("id")
        }
        for kind in REVIEW_ITEM_KINDS
    }
    for kind in REVIEW_ITEM_KINDS:
        pending_by_kind[kind].intersection_update(published_ids_by_kind[kind])

    new_items = []
    for item in all_items:
        item_id = item.get("id")
        if not item_id:
            continue
        author = item.get("author") or ""
        if not author:
            continue

        kind = item["kind"]
        if item_id in acknowledged_by_kind[kind]:
            continue

        pending_by_kind[kind].add(item_id)
        new_items.append(item)
        if kind == "issue_comment":
            seen_issue.add(item_id)
        elif kind == "review_comment":
            seen_review_comment.add(item_id)
        elif kind == "review":
            seen_review.add(item_id)

    new_items.sort(key=lambda item: (item.get("created_at") or "", item.get("kind") or "", item.get("id") or ""))
    state["seen_issue_comment_ids"] = sorted(seen_issue)
    state["seen_review_comment_ids"] = sorted(seen_review_comment)
    state["seen_review_ids"] = sorted(seen_review)
    for kind in REVIEW_ITEM_KINDS:
        state[review_state_key("pending", kind)] = sorted(pending_by_kind[kind])
        state[review_state_key("acknowledged", kind)] = sorted(
            acknowledged_by_kind[kind]
        )
    return new_items


def current_retry_count(state, head_sha):
    retries = state.get("retries_by_sha") or {}
    value = retries.get(head_sha, 0)
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def set_retry_count(state, head_sha, count):
    retries = state.get("retries_by_sha")
    if not isinstance(retries, dict):
        retries = {}
    retries[head_sha] = int(count)
    state["retries_by_sha"] = retries


def unique_actions(actions):
    out = []
    seen = set()
    for action in actions:
        if action not in seen:
            out.append(action)
            seen.add(action)
    return out


def is_pr_ready_to_merge(pr, checks_summary, new_review_items):
    if pr["closed"] or pr["merged"]:
        return False
    if not checks_summary["all_terminal"]:
        return False
    if checks_summary["failed_count"] > 0 or checks_summary["pending_count"] > 0:
        return False
    if new_review_items:
        return False
    if str(pr.get("mergeable") or "") != "MERGEABLE":
        return False
    if str(pr.get("merge_state_status") or "") in MERGE_CONFLICT_OR_BLOCKING_STATES:
        return False
    if str(pr.get("review_decision") or "") in MERGE_BLOCKING_REVIEW_DECISIONS:
        return False
    return True


def recommend_actions(pr, checks_summary, failed_runs, failed_jobs, new_review_items, retries_used, max_retries):
    actions = []
    if pr["closed"] or pr["merged"]:
        if new_review_items:
            actions.append("process_review_comment")
        actions.append("stop_pr_closed")
        return unique_actions(actions)

    if is_pr_ready_to_merge(pr, checks_summary, new_review_items):
        actions.append("ready_to_merge")
        return unique_actions(actions)

    if new_review_items:
        actions.append("process_review_comment")

    has_failed_pr_checks = checks_summary["failed_count"] > 0 or bool(failed_jobs)
    if has_failed_pr_checks:
        if checks_summary["all_terminal"] and retries_used >= max_retries:
            actions.append("stop_exhausted_retries")
        else:
            actions.append("diagnose_ci_failure")
            if checks_summary["all_terminal"] and failed_runs and retries_used < max_retries:
                actions.append("retry_failed_checks")

    if not actions:
        actions.append("idle")
    return unique_actions(actions)


def collect_snapshot(args):
    pr = resolve_pr(args.pr, repo_override=args.repo)
    state_path = Path(args.state_file) if args.state_file else default_state_file_for(pr)
    state, fresh_state = load_state(state_path)

    if not state.get("started_at"):
        state["started_at"] = int(time.time())

    new_review_items = fetch_new_review_items(
        pr,
        state,
        fresh_state=fresh_state,
    )
    # Surface review feedback before drilling into CI and mergeability details.
    # That keeps the babysitter responsive to new comments even when other
    # actions are also available.
    checks = get_pr_checks(pr["repo"], pr["head_sha"])
    checks_summary = summarize_checks(checks)
    workflow_runs = get_workflow_runs_for_sha(pr["repo"], pr["head_sha"])
    failed_runs = failed_runs_from_workflow_runs(workflow_runs, pr["head_sha"])
    failed_jobs = failed_jobs_from_workflow_runs(
        pr["repo"],
        workflow_runs,
        pr["head_sha"],
        failed_check_run_ids=run_ids_with_failed_checks(checks),
    )

    retries_used = current_retry_count(state, pr["head_sha"])
    actions = recommend_actions(
        pr,
        checks_summary,
        failed_runs,
        failed_jobs,
        new_review_items,
        retries_used,
        args.max_flaky_retries,
    )

    state["pr"] = {"repo": pr["repo"], "number": pr["number"]}
    state["last_seen_head_sha"] = pr["head_sha"]
    state["last_snapshot_at"] = int(time.time())
    save_state(state_path, state)

    snapshot = {
        "pr": pr,
        "checks": checks_summary,
        "failed_runs": failed_runs,
        "failed_jobs": failed_jobs,
        "new_review_items": new_review_items,
        "actions": actions,
        "retry_state": {
            "current_sha_retries_used": retries_used,
            "max_flaky_retries": args.max_flaky_retries,
        },
    }
    return snapshot, state_path


def retry_failed_now(args):
    snapshot, state_path = collect_snapshot(args)
    pr = snapshot["pr"]
    checks_summary = snapshot["checks"]
    failed_runs = snapshot["failed_runs"]
    retries_used = snapshot["retry_state"]["current_sha_retries_used"]
    max_retries = snapshot["retry_state"]["max_flaky_retries"]

    result = {
        "snapshot": snapshot,
        "state_file": str(state_path),
        "rerun_attempted": False,
        "rerun_count": 0,
        "rerun_run_ids": [],
        "reason": None,
    }

    if pr["closed"] or pr["merged"]:
        result["reason"] = "pr_closed"
        return result
    if checks_summary["failed_count"] <= 0:
        result["reason"] = "no_failed_pr_checks"
        return result
    if not failed_runs:
        result["reason"] = "no_failed_runs"
        return result
    if not checks_summary["all_terminal"]:
        result["reason"] = "checks_still_pending"
        return result
    if retries_used >= max_retries:
        result["reason"] = "retry_budget_exhausted"
        return result

    for run in failed_runs:
        run_id = run.get("run_id")
        if run_id in (None, ""):
            continue
        gh_text(["run", "rerun", str(run_id), "--failed"], repo=pr["repo"])
        result["rerun_run_ids"].append(run_id)

    if result["rerun_run_ids"]:
        state, _ = load_state(state_path)
        new_count = current_retry_count(state, pr["head_sha"]) + 1
        set_retry_count(state, pr["head_sha"], new_count)
        state["last_snapshot_at"] = int(time.time())
        save_state(state_path, state)
        result["rerun_attempted"] = True
        result["rerun_count"] = len(result["rerun_run_ids"])
        result["reason"] = "rerun_triggered"
    else:
        result["reason"] = "failed_runs_missing_ids"

    return result


def update_review_item_state(args, acknowledge):
    pr = resolve_pr(args.pr, repo_override=args.repo)
    state_path = Path(args.state_file) if args.state_file else default_state_file_for(pr)
    state, _ = load_state(state_path)
    values = args.ack_review_item if acknowledge else args.requeue_review_item
    review_items = parse_review_item_refs(values)
    if acknowledge:
        updated = acknowledge_review_items(state, review_items)
        status = "acknowledged"
    else:
        updated = requeue_review_items(state, review_items)
        status = "requeued"
    state["pr"] = {"repo": pr["repo"], "number": pr["number"]}
    state["last_snapshot_at"] = int(time.time())
    save_state(state_path, state)
    return {
        "status": status,
        "review_items": updated,
        "state_file": str(state_path),
    }


def print_json(obj):
    sys.stdout.write(json.dumps(obj, sort_keys=True) + "\n")
    sys.stdout.flush()


def print_event(event, payload):
    print_json({"event": event, "payload": payload})


def is_ci_green(snapshot):
    checks = snapshot.get("checks") or {}
    return (
        bool(checks.get("all_terminal"))
        and int(checks.get("failed_count") or 0) == 0
        and int(checks.get("pending_count") or 0) == 0
    )


def snapshot_change_key(snapshot):
    pr = snapshot.get("pr") or {}
    checks = snapshot.get("checks") or {}
    review_items = snapshot.get("new_review_items") or []
    return (
        str(pr.get("head_sha") or ""),
        str(pr.get("state") or ""),
        str(pr.get("mergeable") or ""),
        str(pr.get("merge_state_status") or ""),
        str(pr.get("review_decision") or ""),
        int(checks.get("passed_count") or 0),
        int(checks.get("failed_count") or 0),
        int(checks.get("pending_count") or 0),
        tuple(
            (str(item.get("kind") or ""), str(item.get("id") or ""))
            for item in review_items
            if isinstance(item, dict)
        ),
        tuple(snapshot.get("actions") or []),
    )


def run_watch(args):
    poll_seconds = args.poll_seconds
    last_change_key = None
    while True:
        snapshot, state_path = collect_snapshot(args)
        current_change_key = snapshot_change_key(snapshot)
        changed = current_change_key != last_change_key
        if changed:
            print_event(
                "snapshot",
                {
                    "snapshot": snapshot,
                    "state_file": str(state_path),
                    "next_poll_seconds": poll_seconds,
                },
            )
        actions = set(snapshot.get("actions") or [])
        if (
            "stop_pr_closed" in actions
            or "stop_exhausted_retries" in actions
        ):
            print_event("stop", {"actions": snapshot.get("actions"), "pr": snapshot.get("pr")})
            return 0

        green = is_ci_green(snapshot)
        pr = snapshot.get("pr") or {}
        pr_open = not bool(pr.get("closed")) and not bool(pr.get("merged"))

        if not green or pr_open:
            poll_seconds = args.poll_seconds
        elif changed or last_change_key is None:
            poll_seconds = args.poll_seconds

        last_change_key = current_change_key
        time.sleep(poll_seconds)


def main():
    args = parse_args()
    try:
        if args.ack_review_item:
            print_json(update_review_item_state(args, acknowledge=True))
            return 0
        if args.requeue_review_item:
            print_json(update_review_item_state(args, acknowledge=False))
            return 0
        if args.retry_failed_now:
            print_json(retry_failed_now(args))
            return 0
        if args.watch:
            return run_watch(args)
        snapshot, state_path = collect_snapshot(args)
        snapshot["state_file"] = str(state_path)
        print_json(snapshot)
        return 0
    except (GhCommandError, RuntimeError, ValueError) as err:
        sys.stderr.write(f"gh_pr_watch.py error: {err}\n")
        return 1
    except KeyboardInterrupt:
        sys.stderr.write("gh_pr_watch.py interrupted\n")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
