# GitHub CLI / API Notes For `babysit`

## Rate limits

The watcher polls only REST endpoints. `gh pr view` and `gh pr checks` use GraphQL, which has a
small shared hourly budget; do not poll them in a loop. The watcher sends `If-None-Match` with the
last ETag of each endpoint. GitHub does not count a `304 Not Modified` reply against the rate limit.
Only `--pr auto` or a bare number without `--repo` calls `gh pr view --json url` once per run.

`gh api rate_limit` can report a wrong GraphQL budget. To see the real budget, read the
`X-RateLimit-*` headers of `gh api -i graphql -f query='{viewer{login}}'`.

## Endpoints the watcher reads

- `repos/{owner}/{repo}/pulls/<pr_number>`: head SHA, base branch, merged and closed state, `mergeable`, and `mergeable_state`.
- `repos/{owner}/{repo}/commits/<sha>`: the author of the head commit, to tell other people's pushes from yours.
- `repos/{owner}/{repo}/commits/<sha>/check-runs` and `repos/{owner}/{repo}/commits/<sha>/status`: checks on the head commit.
- `repos/{owner}/{repo}/issues/<pr_number>/comments`, `repos/{owner}/{repo}/pulls/<pr_number>/comments`, and `repos/{owner}/{repo}/pulls/<pr_number>/reviews`: published comments and reviews.

## Start-up sweep

The watcher reports only changes after it starts, so run this sweep before the first watch and each
time you resume. It is one GraphQL call, not a loop.

List unresolved inline threads whose latest comment is not yours:

```bash
gh api graphql -f owner=<owner> -f repo=<repo> -F number=<pr_number> -f query='
query($owner: String!, $repo: String!, $number: Int!) {
  viewer { login }
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $number) {
      reviewThreads(first: 100) {
        nodes {
          isResolved
          root: comments(first: 1) { nodes { databaseId path line } }
          latest: comments(last: 1) { nodes { author { login } body url } }
        }
      }
    }
  }
}' --jq '.data.viewer.login as $me | .data.repository.pullRequest.reviewThreads.nodes[]
  | select((.isResolved | not) and .latest.nodes[0].author.login != $me)
  | {thread: .root.nodes[0].databaseId, path: .root.nodes[0].path, line: .root.nodes[0].line,
     author: .latest.nodes[0].author.login, body: .latest.nodes[0].body[:300], url: .latest.nodes[0].url}'
```

`thread` is the ID to reply to. Then list failed checks on the current head:

```bash
gh pr checks <pr-url> --json name,bucket,link --jq '.[] | select(.bucket == "fail")'
```

Review summaries and PR issue comments have no thread state. Read the latest ones with
`gh pr view <pr-url> --comments` when the user asks, or when a thread points to them.

## Failed log inspection

- `gh run view <run-id> --json jobs,name,workflowName,conclusion,status,url,headSha`
- `gh api repos/{owner}/{repo}/actions/runs/{run_id}/jobs -X GET -f per_page=100`
- `gh api repos/{owner}/{repo}/actions/jobs/{job_id}/logs`
- `gh run view <run-id> --log-failed`

Used to classify branch-related vs flaky/unrelated failures. Prefer the direct job log endpoint as
soon as a job has failed, because `gh run view --log-failed` may not produce failed-job logs until
the overall workflow run completes.

## Retry failed jobs only

- `gh run view <run-id> --json attempt --jq .attempt`
- `gh run rerun <run-id> --failed`

Reruns only failed jobs (and dependencies) for a workflow run. See [CI diagnosis](heuristics.md)
for the retry limit.

## Review follow-up endpoints

- Reply to an inline review comment:
  - `gh api -X POST repos/{owner}/{repo}/pulls/<pr_number>/comments/<thread_id>/replies -f body='<reply>'`

Use the thread ID from the watcher update or the start-up sweep. After posting, verify that the
returned `in_reply_to_id` equals that thread ID; only then report that the reply was posted in the
thread.

After a pushed fix, include the commit SHA, what changed, and why. When no change is made, state the
technical reason. Do not reply to status-only bot messages, summaries without requested changes,
approvals, or self-authored follow-ups. Leave review threads open for reviewer follow-up unless the
user explicitly asks to resolve them.

GitHub PR issue comments, review summaries, check annotations, and sections embedded inside a bot
summary do not have inline review-thread reply targets. Never use
`repos/{owner}/{repo}/issues/<pr_number>/comments` as a fallback and never split embedded findings
into synthetic top-level PR comments. If the inline reply endpoint is unavailable or fails, report
the blocker instead of posting elsewhere.
