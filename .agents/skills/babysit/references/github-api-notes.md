# GitHub CLI / API Notes For `babysit`

## Primary commands used

### PR metadata

- `gh pr view --json number,url,state,mergedAt,closedAt,headRefName,headRefOid,headRepository,headRepositoryOwner`

Used to resolve PR number, URL, branch, head SHA, and closed/merged state.

### PR checks summary

- `gh pr checks --json name,state,bucket,link,workflow,event,startedAt,completedAt`

Used to compute pending/failed/passed counts and whether the current CI round is terminal.

### Workflow runs for head SHA

- `gh api repos/{owner}/{repo}/actions/runs -X GET -f head_sha=<sha> -f per_page=100`

Used to discover failed workflow runs and rerunnable run IDs.

### Failed log inspection

- `gh run view <run-id> --json jobs,name,workflowName,conclusion,status,url,headSha`
- `gh api repos/{owner}/{repo}/actions/runs/{run_id}/jobs -X GET -f per_page=100`
- `gh api repos/{owner}/{repo}/actions/jobs/{job_id}/logs > /tmp/codex-gh-job-{job_id}-logs.zip`
- `gh run view <run-id> --log-failed`

Used by the babysitter to classify branch-related vs flaky/unrelated failures. Prefer the direct job log endpoint as soon as a job has failed because `gh run view --log-failed` may not produce failed-job logs until the overall workflow run completes.

### Retry failed jobs only

- `gh run rerun <run-id> --failed`

Reruns only failed jobs (and dependencies) for a workflow run.

## Review-related endpoints

- Issue comments on PR:
  - `gh api repos/{owner}/{repo}/issues/<pr_number>/comments?per_page=100`
- Inline PR review comments:
  - `gh api repos/{owner}/{repo}/pulls/<pr_number>/comments?per_page=100`
- Review submissions:
  - `gh api repos/{owner}/{repo}/pulls/<pr_number>/reviews?per_page=100`

Use each inline comment's `pull_request_review_id` to find its parent review. Ignore parent reviews
whose `state` is `PENDING`, along with their inline comments, until the review is submitted.

## Review follow-up endpoints

- Reply to an inline review comment:
  - `gh api -X POST repos/{owner}/{repo}/pulls/<pr_number>/comments/<comment_id>/replies -f body='<reply>'`

Use the watcher's `thread_root_id` as `<comment_id>`. After posting, verify that the returned
`in_reply_to_id` equals `thread_root_id`; only then report that the reply was posted in the thread.

After a pushed fix, include the commit SHA, what changed, and why. When no change is made, state the
technical reason. Do not reply to status-only bot messages, summaries without requested changes,
approvals, or self-authored follow-ups. Leave review threads open for reviewer follow-up unless the
user explicitly asks to resolve them.

GitHub PR issue comments, review summaries, check annotations, and sections embedded inside a bot
summary do not have inline review-thread reply targets. Never use
`repos/{owner}/{repo}/issues/<pr_number>/comments` as a fallback and never split embedded findings
into synthetic top-level PR comments. If the inline reply endpoint is unavailable or fails, report
the blocker instead of posting elsewhere.

## JSON fields consumed by the watcher

### `gh pr view`

- `number`
- `url`
- `state`
- `mergedAt`
- `closedAt`
- `headRefName`
- `headRefOid`

### `gh pr checks`

- `bucket` (`pass`, `fail`, `pending`, `skipping`)
- `state`
- `name`
- `workflow`
- `link`

### Actions runs API (`workflow_runs[]`)

- `id`
- `name`
- `status`
- `conclusion`
- `html_url`
- `head_sha`

### Actions run jobs API (`jobs[]`)

- `id`
- `name`
- `status`
- `conclusion`
- `html_url`
