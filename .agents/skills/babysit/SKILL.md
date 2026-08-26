---
name: babysit
description: Babysit a GitHub pull request directly in the current session until it is merged, closed, or needs user help. Continuously monitor review comments, CI checks, workflow runs, and mergeability; diagnose failures, retry likely flakes, fix and push branch-related issues in atomic commits, and reply in originating inline review threads. Use when the user explicitly asks to monitor a PR, watch CI, handle review comments, or babysit an open PR.
---

# Babysit

## Objective
Babysit a PR persistently until one of these terminal outcomes occurs:

- The PR is merged or closed.
- A situation requires user help (for example CI infrastructure issues, repeated flaky failures after retry budget is exhausted, permission problems, or ambiguity that cannot be resolved safely).
- Optional readiness milestone: the PR is currently green + mergeable + review-clean. Treat this as a progress state, not a watcher stop, so late-arriving review comments are still surfaced promptly while the PR remains open.

Do not stop merely because a single snapshot returns `idle` while checks are still pending.

## Inputs
Accept any of the following:

- No PR argument: infer the PR from the current branch (`--pr auto`)
- PR number
- PR URL

## Session Ownership

An explicit `$babysit` invocation makes the current session the dedicated babysitter. Start the
watcher here and keep this session active until a strict stop condition occurs.

- Do not create another task, agent, session, branch, or worktree.
- The user chooses whether this session runs in the originating checkout, a new thread, or an
  isolated worktree. Do not attempt to enforce or replace that choice.
- Use the current conversation as the primary source of implementation context. If the user starts
  babysitting in a new thread, use the context they provide and do not invent missing decisions.
- Resolve the PR URL, title, full body, base repository, number, head repository, head branch, and
  current head SHA before monitoring.
- Prefer an explicit PR URL for every watcher command. Use `--pr auto` only when the current branch
  unambiguously identifies the intended PR.
- Confirm the current checkout is safe before any edit or push. Follow the Git Safety Rules below.
- Establish the Intent Boundary below before changing code.
- Run the Core Workflow below and keep this session active until a strict stop condition is reached.

## Intent Boundary

Before the first code change:

1. Read the current conversation. Treat its user decisions, solution rationale, rejected
   alternatives, evidence, and non-goals as first-class decision context. Do not assume factual
   state from earlier messages is still current.
2. Fetch the current PR title and full body from GitHub instead of relying only on conversation
   context.
3. Read every ticket or specification directly linked from the PR title or body, including linked
   Notion pages, using an available authorized connector. Do not infer inaccessible private content.
4. Reconcile the conversation with the live PR, linked sources, tests, and changed behavior. Verify
   drift-prone facts, but do not discard implementation reasoning merely because it is absent from
   the PR body. If no ticket is linked, use the conversation, PR title/body, tests, and changed
   behavior.
5. Derive a concise working scope: intended outcome, acceptance criteria, explicit non-goals, and
   deliberate trade-offs that affect review decisions.
6. Stop for user help before editing when required source material is inaccessible, sources conflict,
   the conversation is missing material context, or the intended behavior remains materially ambiguous.

Use this scope for every CI or review-driven code change. Automatically fix feedback only when it is
within the intended outcome or necessary to make that outcome correct and safe. Do not automatically
broaden supported scenarios, add new product behavior, change acceptance criteria, or make unrelated
product/design/architecture decisions merely because feedback is technically valid or PR-introduced.
Surface such feedback to the user as scope-expanding and wait for direction. Explicit user direction
takes precedence over the ticket and PR description. When review feedback revisits a deliberately
rejected alternative, trade-off, or non-goal from the implementation, assess whether the reviewer
provides new evidence. Do not silently reverse or dismiss the prior decision; ask the user when the
new evidence could materially change it.

## Core Workflow

1. Start with the watcher's continuous mode (`--watch`) and the explicit PR URL unless you are intentionally doing a one-shot diagnostic snapshot.
2. Run the watcher script to snapshot PR/review/CI state (or consume each streamed snapshot from `--watch`). Review items remain pending and repeat in snapshots until explicitly acknowledged.
3. Inspect the `actions` list in the JSON response.
4. If `diagnose_ci_failure` is present, inspect failed run logs and classify the failure.
5. If the failure is likely caused by the current branch and its fix fits the Intent Boundary, patch code locally, validate it, use the Atomic Commit Gate below, and push. Escalate a required scope-expanding fix instead of changing product intent to make CI pass. Do not patch random flaky tests, CI infrastructure, dependency outages, runner issues, or other failures that are unrelated to the branch.
6. If `process_review_comment` is present, inspect every surfaced published review item. Before deciding whether to address it, compare the reported behavior at the PR merge base and head, then assess whether it is reachable and materially relevant in real usage.
7. Treat an issue as branch-related only when the PR introduced it or materially worsened its reachability, frequency, or impact. A branch-related issue is not automatically in product scope: also apply the Intent Boundary before editing. Process independently actionable in-scope issues one at a time. For each issue: patch and validate the smallest fix, create one atomic commit, push it, then reply with the concrete change, rationale, and commit SHA only when the originating item is an inline review comment with an actual GitHub review thread.
8. If threaded feedback is incorrect, non-actionable, already addressed, theoretical with negligible practical impact, pre-existing and unchanged by the PR, or conflicts with explicit user direction, make no code change and reply in that actual review thread with a concise ELIJ-style rationale. A touched nearby file does not make a pre-existing issue part of the PR. Surface material pre-existing security, privacy, data-loss, or corruption risks to the user for separate handling instead of silently expanding the PR. Never create top-level PR comments as a substitute for thread replies. Do not reply to status-only bot messages, summaries without requested changes, approvals, or duplicate/self-authored follow-ups.
9. Acknowledge each review item only after its disposition is complete: the fix is pushed and its inline reply is verified; the no-change inline reply is verified; or status-only/duplicate/non-actionable feedback has been deliberately classified. Never acknowledge merely because an item was fetched or inspected.
10. If the failure is likely flaky/unrelated and `retry_failed_checks` is present, rerun failed jobs with `--retry-failed-now`.
11. If both actionable review feedback and `retry_failed_checks` are present, prioritize review feedback first; a new commit will retrigger CI, so avoid rerunning flaky checks on the old SHA unless you intentionally defer the review change.
12. On every loop, look for newly surfaced review feedback before acting on CI failures or mergeability state, then verify mergeability / merge-conflict status (for example via `gh pr view`) alongside CI.
13. After any push or rerun action, immediately return to step 1 and continue polling on the updated SHA/state.
14. If you had been using `--watch` before pausing to patch/commit/push, relaunch `--watch` yourself in the same turn immediately after the push (do not wait for the user to re-invoke the skill).
15. Repeat polling until `stop_pr_closed` appears or a user-help-required blocker is reached. A green + review-clean + mergeable PR is a progress milestone, not a reason to stop the watcher while the PR is still open.
16. Maintain terminal/session ownership: while babysitting is active, keep consuming watcher output in the same turn; do not leave a detached `--watch` process running and then end the turn as if monitoring were complete.

## Commands

### One-shot snapshot

Use the base directory containing this `SKILL.md` in place of `<babysit-skill-directory>`:

```bash
python3 "<babysit-skill-directory>/scripts/gh_pr_watch.py" --pr <pr-url> --once
```

### Continuous watch (JSONL)

```bash
python3 "<babysit-skill-directory>/scripts/gh_pr_watch.py" --pr <pr-url> --watch
```

### Trigger flaky retry cycle (only when watcher indicates)

```bash
python3 "<babysit-skill-directory>/scripts/gh_pr_watch.py" --pr <pr-url> --retry-failed-now
```

### Acknowledge handled review feedback

Stop the current watcher, acknowledge one or more completed dispositions, then restart `--watch`:

```bash
python3 "<babysit-skill-directory>/scripts/gh_pr_watch.py" \
  --pr <pr-url> \
  --ack-review-item <issue_comment|review_comment|review>:<id>
```

Use `--requeue-review-item <kind>:<id>` only to recover feedback that was incorrectly acknowledged
or migrated as handled. Both flags are repeatable.

### Explicit PR target

```bash
python3 "<babysit-skill-directory>/scripts/gh_pr_watch.py" --pr <number-or-url> --once
```

## CI Failure Classification
Use `gh` commands to inspect failed runs before deciding to rerun.

- `gh run view <run-id> --json jobs,name,workflowName,conclusion,status,url,headSha`
- `gh api repos/<owner>/<repo>/actions/runs/<run-id>/jobs -X GET -f per_page=100`
- `gh api repos/<owner>/<repo>/actions/jobs/<job-id>/logs > /tmp/codex-gh-job-<job-id>-logs.zip`
- `gh run view <run-id> --log-failed` as a fallback after the overall workflow run is complete

`gh run view --log-failed` is workflow-run scoped and may not expose failed-job logs until the overall run finishes. For faster diagnosis, poll the run's jobs first and, as soon as a specific job has failed, fetch that job's logs directly from the Actions job logs endpoint. The watcher includes a `failed_jobs` list with each failed job's `job_id` and `logs_endpoint` when GitHub exposes one.

Prefer treating failures as branch-related when failed-job logs point to changed code (compile/test/lint/typecheck/snapshots/static analysis in touched areas).

Prefer treating failures as flaky/unrelated when logs show transient infra/external issues (timeouts, runner provisioning failures, registry/network outages, GitHub Actions infra errors).

Do not attempt to fix flaky/unrelated failures by changing tests, build scripts, CI configuration, dependency pins, or infrastructure-adjacent code unless the logs clearly connect the failure to the PR branch. For flaky/unrelated failures, rerun only when the watcher recommends `retry_failed_checks`; otherwise wait or stop for user help.

If classification is ambiguous, perform one manual diagnosis attempt before choosing rerun.

Read `references/heuristics.md` relative to this `SKILL.md` for a concise checklist.

## Edit Quality Gate

Apply this gate separately to every actionable CI or review issue before editing:

1. Load and apply the `Keep it simple, stupid` skill.
2. State internally, in one sentence, the exact defect and the smallest direct fix that fully addresses it.
3. Confirm the fix fits the Intent Boundary. Start at the existing ownership seam and prefer a local change over a new helper, abstraction, type, interface, or generalized solution.
4. Introduce an abstraction only when the direct fix would be incorrect, duplicate substantial logic, or make the code clearly harder to read. Possible future reuse is not sufficient.
5. Load and apply the `human-code` skill within that minimal shape. Keep names clear, control flow obvious, and local structure natural without expanding the change.
6. Inspect the completed diff through KISS again. If a smaller solution fully fixes the issue, simplify the implementation before validation.
7. Follow the repository's `AGENTS.md`, style, test, lint, and typecheck requirements. Preserve existing behavior outside the requested fix.

## Atomic Commit Gate

After an issue's code change is complete and validated, but before staging:

1. Load and apply the `create-commit` skill.
2. Inspect the unstaged and staged state. Leave unrelated user changes untouched and never start with `git add .`.
3. Stage only the paths or hunks for that one issue and review the staged diff before committing.
4. Make the commit one reason to revert. Do not accumulate independent review issues into one commit.
5. Use a concrete conventional title in `type(scope): description` format that states the outcome. Never use a catch-all title such as `address PR review feedback`.
6. Keep tests with the behavior change they prove. Split dependencies, tooling, mechanical changes, or other independently revertible concerns as required by the create-commit skill.

Multiple comments may share one commit only when they describe the same root cause and splitting them would leave the repository broken or misleading. Reply in each originating inline review thread with that commit.

## Inline Reply Style (ELIJ)

Write every automated inline reply so an outside reader can understand it without the babysitter's
investigation context. Apply the "Explain it like I'm a junior" style:

- Write all reply prose with ASD-STE100 Simplified Technical English principles. Use short,
  complete, active-voice sentences, one idea per sentence, consistent terms, explicit nouns, and no
  contractions. Preserve exact code identifiers, API names, commit SHAs, paths, and quoted evidence
  as technical terms.
- Begin every automated inline reply with `@<author-login>`, using the exact `author` from the
  originating watcher item, except when the author is Codex or a Codex bot/service account. Codex
  mentions can launch an unwanted Codex Cloud task. For Codex-authored feedback, omit the author
  mention entirely and start with the outcome. Mention all other human and automated reviewers so
  connected notification channels can alert the original author. Never include `@codex` or another
  GitHub mention of a Codex account in a reply to Codex-authored feedback.
- Start with the outcome in one or two sentences: what changed, or why no change was needed.
- Explain the practical reason before implementation details or edge cases.
- Use plain language before jargon. Briefly explain unavoidable terms instead of assuming the reader
  knows internal labels such as "merge base," "reachability," or "intent boundary."
- Include a small concrete example when it makes the behavior easier to understand.
- Keep the reply compact. Include the evidence that supports the decision, but omit the investigation
  diary, internal classification, and unrelated technical detail.
- Be direct and respectful, never patronizing.

For example, prefer `I checked the code from before this PR, and it already behaves this way. This PR
does not make the behavior more likely or more harmful, so changing it here would expand the scope.`
over an unexplained statement that the issue is "pre-existing at the merge base and not materially
more reachable."

## Review Comment Handling
The watcher surfaces review items from:

- PR issue comments
- Inline review comments
- Review submissions (COMMENT / APPROVED / CHANGES_REQUESTED)

Only act on published feedback. Ignore review submissions in GitHub's `PENDING` state and inline
comments attached to those pending reviews. Do not mark pending review feedback as seen; it should
be eligible to surface after the reviewer submits the review.

The watcher surfaces all published feedback regardless of author association or bot identity. This includes collaborators, external contributors, and automated reviewers such as Codex, Copilot, Cursor, and CodeRabbit. Collection is intentionally inclusive; assess whether each surfaced item is relevant and actionable before changing code.
On a fresh watcher state file, existing unaddressed published review feedback may be surfaced immediately (not only comments that arrive after monitoring starts). This is intentional so already-open review comments are not missed.

For every reported issue, read `references/heuristics.md` and verify both scope and practical impact before changing code. Compare the PR head with its merge base to determine whether the behavior is an actual PR regression. Do not auto-fix behavior that was already present and is unchanged in reachability or impact; when an inline thread exists, reply with the concrete base/head evidence and explain that it is outside this PR's scope. Low-frequency issues may still warrant a fix when inputs are deliberately controllable or the credible impact includes security, privacy, data loss, or corruption.

When you agree with a comment and it is actionable:

1. Patch code locally.
2. Validate the focused change.
3. Use the Atomic Commit Gate to create a small, issue-specific conventional commit.
4. Push to the PR head branch.
5. If the originating item is an inline `review_comment`, reply in its actual GitHub review thread with `@<author-login> Addressed in <commit-sha>.` followed by an ELIJ-style explanation of what changed and why it matters. If the author is Codex or a Codex bot/service account, omit `@<author-login>` and begin with `Addressed in <commit-sha>.`.
6. Leave the review thread open so the reviewer can follow up or re-review.
7. Acknowledge the originating watcher item only after the push and verified thread reply.
8. Resume watching on the new SHA immediately (do not stop after reporting the push).
9. If monitoring was running in `--watch` mode, restart `--watch` immediately after the push in the same turn; do not wait for the user to ask again.

When threaded feedback does not warrant a code change, reply in the actual inline review thread with `@<author-login> No change made.` followed by the concrete reason in the ELIJ style above. If the author is Codex or a Codex bot/service account, omit `@<author-login>` and begin with `No change made.`. Be respectful and factual. Ask the user before replying only when the response requires an unresolved product decision, private context, or cross-team coordination.
For unchanged pre-existing behavior, use the substance of: `No change made. I checked the code from before this PR (<sha/path evidence>), and it already behaves this way. This PR does not make the behavior more likely or more harmful, so changing it here would expand the scope.` Adapt the evidence to the actual report rather than posting a generic dismissal.
After the reply is verified, acknowledge the originating watcher item. For status-only noise, approvals,
duplicates, and self-authored follow-ups, acknowledge only after deliberately classifying them as ignorable.
If a code review comment/thread is already marked as resolved in GitHub, treat it as non-actionable and safely ignore it unless new unresolved follow-up feedback appears.

PR issue comments, review summaries, check annotations, and sections embedded inside a bot's summary comment are not inline review threads. They have no thread-reply target. Do not synthesize separate PR comments for them. If substantive feedback has no inline thread, report that limitation to the user instead of posting on GitHub.

## GitHub State Mutation Policy

You can read any PR state you need for monitoring. Writes must comply with this policy.

You can push PRs to update the code under review or to force CI re-runs as described above.

The user authorizes automatic replies to inline review threads from human and automated reviewers.
Reply only to communicate the disposition of that threaded feedback: the pushed fix and commit, or
the reason no change was made.

Use only the inline review-comment reply endpoint with the watcher's `thread_root_id`. Verify the
created comment has `in_reply_to_id` equal to that thread root before reporting success. Never use
the PR issue-comments endpoint as a fallback, and never claim a reply was threaded based only on
successful comment creation. If no thread root exists or the reply endpoint fails, report the
limitation or blocker to the user. Do not resolve review threads automatically; leave them open for
reviewer follow-up unless the user explicitly asks for resolution.

Before making any changes, fetch the PR state, title, and full body yourself instead of relying on the
PR watcher script's output, and confirm that the Intent Boundary still supports the proposed change.

Unless explicitly asked, do not:

* post top-level PR comments as a substitute for inline review-thread replies
* post unrelated or proactive comments that are not a disposition of surfaced review feedback
* mark PRs as drafts or ready for review
* close or reopen PRs

Never impersonate the user. Keep automated follow-ups scoped, factual, and visibly attributed.

## Git Safety Rules

- Work only in the checkout selected by the user for this babysitting session. Do not create or
  switch branches or worktrees solely because the skill was invoked.
- The checkout may use the PR branch or detached HEAD. Do not require one form over the other.
- Avoid destructive git commands.
- Before each edit, fetch the PR and confirm `HEAD` matches the latest PR head SHA. If GitHub
  advanced, update the clean checkout safely without force or destructive commands. Stop for user
  help if the checkout cannot be aligned safely.
- Before editing, check for unrelated uncommitted changes. Leave them untouched. Stop and ask the
  user if they overlap the intended fix or make an atomic commit unsafe.
- Record the PR head SHA used as the base for each fix. Immediately before pushing, fetch again and
  verify the remote PR head still equals that base. If it advanced, integrate safely and revalidate;
  never overwrite it.
- For a same-repository PR, push the current commit explicitly with `git push origin
  HEAD:<head-branch>`. For a fork PR, identify or add a remote for the writable head
  repository and push `HEAD:<head-branch>` there.
- Never force-push from the babysitter.
- After each successful issue-specific fix, use the create-commit skill, commit, push the current
  HEAD explicitly to the PR head branch, reply in each originating inline review thread when one
  exists, then re-run the watcher.
- If you interrupted a live `--watch` session to make the fix, restart `--watch` immediately after the push in the same turn.
- Do not run multiple concurrent `--watch` processes for the same PR/state file; keep one watcher session active and reuse it until it stops or you intentionally restart it.
- A push is not a terminal outcome; continue the monitoring loop unless a strict stop condition is met.

Commit titles must be concrete conventional commits, for example:

- `fix(search): fail resync when cache is unavailable`
- `fix(auth): preserve session during token refresh`

Never use `chore: address PR review feedback` or another catch-all title.

## Monitoring Loop Pattern
Use this loop in the current session:

1. Run `--once`.
2. Read `actions`.
3. First check whether the PR is now merged or otherwise closed; if so, report that terminal state and stop polling immediately.
4. Check CI summary, new review items, and mergeability/conflict status.
5. Diagnose CI failures and classify branch-related vs flaky/unrelated. If the overall run is still pending but `failed_jobs` already includes a failed job, fetch that job's logs and diagnose immediately instead of waiting for the whole workflow run to finish. Patch only when the failure is branch-related.
6. For each surfaced review issue from another author, handle it independently. Compare merge-base behavior with PR-head behavior, assess real-world reachability, likelihood, and impact, and apply the Intent Boundary. If the PR introduced or materially worsened a practical in-scope issue, patch and validate it, create an atomic conventional commit with the create-commit skill, push, and reply in every originating inline review thread with the commit and rationale. If technically valid feedback would expand product scope, stop and ask the user instead of editing or posting a disposition. If feedback is incorrect, non-actionable, already addressed, theoretical with negligible impact, or pre-existing and unchanged by the PR, reply in that thread with a concise evidence-backed rationale using the Inline Reply Style. Never substitute top-level PR comments for thread replies. Leave threads unresolved for follow-up. Ignore status-only noise and do not respond to your own attributed replies.
7. Process actionable review comments before flaky reruns when both are present; if a review fix requires a commit, push it and skip rerunning failed checks on the old SHA.
8. Retry failed checks only when `retry_failed_checks` is present and you are not about to replace the current SHA with a review/CI fix commit. Do not make code changes for unrelated flakes or infrastructure failures just to get CI green.
9. If you pushed a commit, posted a feedback disposition, or triggered a rerun, report the action briefly and continue polling (do not stop). Stop for user input only when a reply requires a product decision, private context, or cross-team coordination.
10. After a review-fix push, proactively restart continuous monitoring (`--watch`) in the same turn unless a strict stop condition has already been reached.
11. When everything first becomes passing, mergeable, not blocked on required review approval, and free of unaddressed review items, report once that the PR is ready to merge. Keep the watcher running, but do not repeat the update while that state remains unchanged.
12. If blocked on a user-help-required issue (infra outage, exhausted flaky retries, unclear reviewer request, permissions), report the blocker and stop.
13. Otherwise sleep according to the polling cadence below and repeat.

When the user explicitly asks to monitor/watch/babysit a PR, prefer `--watch` so polling continues autonomously in one command. Use repeated `--once` snapshots only for debugging, local testing, or when the user explicitly asks for a one-shot check.
Do not stop to ask the user whether to continue polling; continue autonomously until a strict stop condition is met or the user explicitly interrupts.
Do not hand control back to the user after a review-fix push just because a new SHA was created; restarting the watcher and re-entering the poll loop is part of the same babysitting task.
If a `--watch` process is still running and no strict stop condition has been reached, the babysitting task is still in progress; keep streaming/consuming watcher output instead of ending the turn.

## Polling Cadence
Keep review polling aggressive and continue monitoring even after CI turns green:

- Poll every 30 seconds while the PR remains open, including while CI is pending, failing, or green.
- After CI turns green: keep polling at the base cadence while the PR remains open so newly posted review comments are surfaced promptly instead of waiting on a long green-state backoff.
- Reset the cadence immediately whenever anything changes (new commit/SHA, check status changes, new review comments, mergeability changes, review decision changes).
- If CI stops being green again (new commit, rerun, or regression): stay on the base polling cadence.
- If any poll shows the PR is merged or otherwise closed: stop polling immediately and report the terminal state.

## Stop Conditions (Strict)
Stop only when one of the following is true:

- PR merged or closed (stop as soon as a poll/snapshot confirms this).
- User intervention is required and the babysitter cannot safely proceed alone.

Keep polling when:

- `actions` contains only `idle` but checks are still pending.
- CI is still running/queued.
- Review state is quiet but CI is not terminal.
- CI is green but mergeability is unknown/pending.
- CI is green and mergeable, but the PR is still open and you are waiting for possible new review comments or merge-conflict changes.
- The PR is green but blocked on review approval (`REVIEW_REQUIRED` / similar); continue polling at the base cadence and surface any new review comments without asking for confirmation to keep watching.

## Output Expectations
Provide concise progress updates while monitoring and a final summary that includes:

- After the initial watcher snapshot, emit progress only for a meaningful state change, an action taken, a user-help blocker, or a terminal outcome. Do not emit heartbeat, liveness, "still watching," or unchanged-status updates. Silence means monitoring is healthy and unchanged.
- Treat push confirmations, intermediate CI snapshots, ready-to-merge snapshots, and review-action updates as progress updates only; do not emit the final summary or end the babysitting session unless a strict stop condition is met.
- A user request to "monitor" is not satisfied by a couple of sample polls; remain in the loop until a strict stop condition or an explicit user interruption.
- A review-fix commit + push is not a completion event; immediately resume live monitoring (`--watch`) in the same turn and continue reporting progress updates.
- When CI first transitions to all green for the current SHA, emit a one-time celebratory progress update (do not repeat it on every green poll). Preferred style: `🚀 CI is all green! 33/33 passed. Still on watch for review approval.`
- The watcher deliberately suppresses identical snapshots. When a live watcher wait returns no new output, do not narrate the empty poll; continue waiting. Align nested terminal and orchestration yield timeouts so one wait interval does not cause multiple unnecessary model resumptions.
- Do not send the final summary while a watcher terminal is still running unless the watcher has emitted/confirmed a strict stop condition; otherwise continue with progress updates.

- Final PR SHA
- CI status summary
- Mergeability / conflict status
- Fixes pushed
- Flaky retry cycles used
- Remaining unresolved failures or review comments

## References

- Heuristics and decision tree: `references/heuristics.md`
- GitHub CLI/API details used by the watcher: `references/github-api-notes.md`
