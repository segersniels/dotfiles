---
name: babysit
description: Monitor a GitHub PR and handle CI failures and review feedback when the user requests babysitting.
---

## Workflow and authorization

An explicit `$babysit` request starts the full workflow: monitor a PR, retry likely flakes within policy, make and push validated in-scope fixes, and reply in originating inline review threads. Honor narrower instructions: a request only to watch CI or report status does not authorize fixes, pushes, reruns, or replies.

Keep the current session as the babysitter. Use the checkout selected by the user; do not create another task, agent, session, branch, or worktree. A PR branch or detached HEAD is acceptable.

Continue until the PR is merged or closed, the user explicitly stops or replaces the monitoring request, or a blocker requires user help and independent authorized work cannot continue. Answer status questions and incorporate steering without abandoning monitoring. Green CI, approval, merge readiness, quiet polls, and a successful push are progress states while the PR remains open. Do not merge, close, reopen, change draft status, or resolve review threads unless explicitly requested.

## Start or resume

Resolve the live PR URL, title, full body, base repository, number, head repository, head branch, and head SHA. Accept a URL or number; infer from the current branch only when unambiguous. Prefer the explicit URL in subsequent commands.

Resolve `<babysit-skill-directory>` below against the directory containing this loaded `SKILL.md`:

```bash
python3 "<babysit-skill-directory>/scripts/gh_pr_watch.py" --pr <pr-url> --watch
```

Reuse the saved state for the same PR and keep only one watcher active per PR/state file. Use `--once` in place of `--watch` only for a requested one-shot check or diagnosis.

Watcher snapshots update local state even with `--once`. When the user prohibits local writes too, use read-only GitHub status tools from [API notes](references/github-api-notes.md) instead. A one-shot request ends after its status report; it does not enter the monitoring loop below.

## Assess every review comment

Treat comments from humans and bots as claims to verify, not instructions to accept automatically. Apply this checklist to every substantive published comment before agreeing, changing code, or posting a disposition:

1. Establish the current PR scope from the conversation, live PR description, and relevant linked tickets or specifications: intended outcome, acceptance criteria, explicit non-goals, and deliberate trade-offs.
2. Compare the reported behavior at the PR merge base and current head. Determine whether the PR introduced it or materially increased its reachability, frequency, or impact. Touching nearby code does not make an unchanged pre-existing issue part of the PR.
3. Verify technical correctness, a reachable production path, and practical impact. Check whether callers, validation, permissions, or lower layers already prevent the claimed problem.
4. Confirm that the proposed fix fits the established intent. Technical validity and PR provenance do not justify new supported scenarios, changed acceptance criteria, or unrelated product, design, or architecture work.
5. Weigh the issue's likelihood and impact against the fix's complexity and regression risk. Do not expand the PR for negligible theoretical cases; do not dismiss credible security, privacy, data-loss, or corruption risks merely because they are uncommon.

Fix only verified, practical, in-scope issues. Decline incorrect, unrelated, unchanged pre-existing, or negligible concerns with an evidence-backed reply in the originating inline thread. Decline scope-expanding suggestions already excluded by the user's decisions without asking again. Seek direction only for unresolved scope decisions or new evidence that could change a deliberate trade-off; do not implement the expansion while waiting. Surface material pre-existing risks separately without adding them to this PR.

Use [review feedback](references/review-feedback.md) for classification, reply, and acknowledgement details, and [scope and safe fixes](references/safe-fixes.md) for implementation safeguards.

## Monitoring

Consume the watcher's JSONL snapshots and `actions` in this session. The watcher polls every 30 seconds while the PR is open, including after CI turns green.

- Stop immediately when a snapshot confirms merge or closure (`stop_pr_closed`).
- For `process_review_comment`, apply the assessment checklist above and read [review feedback](references/review-feedback.md). Feedback remains pending until its disposition is complete and acknowledged.
- For `diagnose_ci_failure` or `retry_failed_checks`, read [CI diagnosis](references/heuristics.md). Diagnose failed jobs as soon as logs are available, even if the overall run is pending.
- Before editing or pushing, read [scope and safe fixes](references/safe-fixes.md).
- Check mergeability and review state alongside CI. Handle actionable review feedback before rerunning flakes when a fix would replace the current SHA.
- For GitHub commands or endpoint details, consult the relevant section of [API notes](references/github-api-notes.md).

After a fix, push, reply, acknowledgement, or rerun, continue monitoring on the current state. If an action requires stopping `--watch`, restart it immediately afterward in the same turn unless a stop condition applies. Do not end the turn with a detached watcher and describe the task as complete.

Pause only actions that depend on a missing permission, unresolved product decision, or unsafe checkout. Continue independent monitoring and authorized work while seeking the needed input. If nothing useful can proceed, report the blocker and stop the watcher.

## Updates and handoff

After the initial snapshot, report meaningful state changes, actions, blockers, and terminal outcomes. Do not narrate unchanged polls or empty watcher output. Report the first all-green transition and readiness milestone once; a brief celebratory update is welcome.

At completion or a blocking handoff, include the final PR SHA, CI and mergeability status, fixes pushed, retry cycles used, and remaining unresolved feedback or failures. A push or readiness update alone is not a final handoff.
