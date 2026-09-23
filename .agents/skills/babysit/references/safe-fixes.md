# Scope and Safe Fixes

Read before the first edit, then refresh facts that may have changed before later fixes or pushes.

## Establish the intended outcome

Use the conversation's user decisions, implementation reasoning, rejected alternatives, and non-goals. Fetch the live PR state, title, and full body yourself; the watcher snapshot is not a substitute for product context.

Read directly linked tickets and specifications that define the intended behavior through available authorized tools. Verify drift-prone facts and reconcile the sources with tests and code. Do not invent inaccessible private content. Missing or conflicting material blocks only decisions that depend on it; unrelated links do not block an otherwise well-supported fix.

Fix feedback automatically only when it fits the intended outcome or is necessary to make that outcome correct and safe. A PR-introduced issue is not automatically in scope. New supported scenarios, changed acceptance criteria, and unrelated product, design, or architecture decisions need user direction.

Explicit user decisions take precedence over ticket and PR text. If new evidence challenges a deliberate trade-off or rejected alternative, surface the decision instead of silently reversing or dismissing it. Continue independent authorized work while awaiting material clarification.

## Protect the selected checkout

- Fetch and confirm that local HEAD matches the latest PR head before editing. Align a clean checkout safely when needed; do not change the user's selected branch/worktree or use destructive commands.
- Leave unrelated uncommitted or staged changes untouched. Overlap that prevents a safe edit or atomic commit blocks the affected fix.
- Record the remote head SHA on which the fix is based. Immediately before pushing, fetch again and confirm that remote head still matches. If it advanced, integrate safely and revalidate; never overwrite it or force-push.

## Implement and deliver

Use the smallest clear fix at the existing ownership boundary. Keep names and control flow readable and preserve behavior outside the fix. Add an abstraction only when the direct solution would be incorrect, duplicate substantial logic, or be harder to read.

Validate the affected behavior and complete repository-required checks. Use the commit skill for explicit staging, dependency grouping, and Conventional Commit titles. Make independently actionable issues separate commits; comments about the same root cause can share a commit. Keep regression tests with the fix and avoid catch-all titles such as `chore: address PR review feedback`.

Push the current commit explicitly to the PR head branch:

```bash
git push origin HEAD:<head-branch>
```

For a fork PR, identify or add the writable head-repository remote and push `HEAD:<head-branch>` there. Verify the resulting remote SHA before reporting success.

For review-driven fixes, complete the originating feedback disposition using [review feedback](review-feedback.md), then resume the watcher immediately in the same turn. Do not stop after the push.
