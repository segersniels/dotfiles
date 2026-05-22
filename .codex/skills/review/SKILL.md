---
name: review
description: "Review code changes with repo-aware context, architecture scrutiny, claim verification, and actionable findings. Use for uncommitted changes, commits, branches, or PRs when you want a thorough but low-noise review."
metadata:
  short-description: Repo-aware code review
---

You are a critical but fair technical lead reviewing a PR. Question everything. Be thorough. Approve when changes clearly improve overall code health; don't block only because it differs from your preferred style.

## Step 1: Context

1. Read @AGENTS.md, then read every file it references (e.g. `.agents/docs/*.md`) to understand project conventions
2. Read @REVIEW.md to understand what to focus on, prioritize, and skip during the review
3. Read @VOICE.md (if it exists) to match the reviewer's tone in suggested comments
4. Run `gh pr view --json number,title,body,headRefName,baseRefName` to get PR details
5. If the current local checkout is not already on `headRefName`, use the `create-worktree` skill to create an isolated local checkout of the PR head branch with `fracture --no-spawn --background-install`. Review changed files from that local worktree rather than reading file contents via `gh api`.
6. Only fall back to GitHub-hosted file contents when a local checkout is impossible (for example: no local repo, `fracture` unavailable, or the branch cannot be fetched locally). If you do fall back, say why.
7. Run `gh pr diff` to get the full diff
8. Read existing PR comments (including inline): `gh api repos/{owner}/{repo}/pulls/{number}/comments` and `gh api repos/{owner}/{repo}/issues/{number}/comments`. Build a structured list of already-flagged findings (file, line, topic, author/bot, and whether the author replied or it appears resolved). Pass this list to explorer agents explicitly so they skip duplicate feedback. The parent agent still owns final dedupe before reporting.

## Step 2: Review

Dispatch multiple explorer agents in parallel to review the PR:

Before dispatching, pass each explorer the already-flagged findings from Step 1.8 and instruct them to avoid re-raising those topics unless the current diff adds a new, distinct issue.

### Agent 1: High-Level Architecture Review
- Is the overall approach sound? Is there a simpler architectural alternative?
- Does the PR do one thing? Flag scope creep
- **Behavioral semantics**: does the PR claim to be a refactor but actually change behavior? Look for: new filters that exclude data, changed conditions (e.g. `||` added/removed), removed UI elements, different API call patterns, changed data-fetching semantics (e.g. `isLoading` vs `isValidating`)
- Are there missing edge cases or unhandled scenarios?
- Any security concerns?

### Agent 2+: File-by-File Deep Review
- Split the changed files across sub agents (group related files together)
- Review changed tests before implementation files when present, so intended behavior is clear before judging the code
- Prefer reading files from the local PR-head worktree. Do not default to `gh api repos/.../contents/...` for changed-file reads when a local checkout is available.
- Trace all code paths through each change
- **For moved/rewritten files**: read BOTH the old file (on base branch) and the new file. Compare every code path, every conditional branch, every state variable. Flag anything present in old but absent in new — this is where subtle regressions hide.
- Check for bugs, race conditions, N+1 queries, stale closures, ...
- Verify consistency with existing patterns in the codebase
- Flag dead code, misleading names, unnecessary complexity
- Check if tests cover the new/changed behavior

Each sub agent should return a list of findings with:
- File path and line number
- What's wrong
- Why it's wrong
- Severity (blocker / concern / nit)

## Step 3: Verify Claims

Do NOT blindly trust sub agent findings. For each claim from the sub agents:

1. **Read the actual code** — open the file, read the lines, trace the logic yourself
2. **Follow the data** — if a claim says "X calls Y with Z", verify it by reading the call chain
3. **Check assumptions** — if a claim assumes a value or behavior, grep/read the codebase to confirm
4. **Cross-reference** — if multiple agents flag the same thing differently, reconcile them
5. **Test the logic** — mentally trace edge cases against the actual code, not the agent's summary

Common sub agent mistakes to watch for:
- Assuming two things with similar names are different (e.g., sessionUuid vs submission.uuid)
- Missing that a function is called elsewhere with different behavior
- Claiming a filter is missing when the engine handles it (e.g., ENGINE_IS_DELETED + FINAL)
- Flagging "no error handling" when there's a try/catch at a higher level
- Overstating severity on things that are technically true but have zero functional impact

## Step 4: Build TODO List

After verification, create tasks for EACH finding (verified and debunked).
Then immediately call mark all debunked tasks as `completed`.

Before creating tasks, cross-check each surviving finding against the already-flagged list from Step 1.8. Same file + same line (±2) + same topic = already flagged. Drop these from the task list and interactive walkthrough; mention only the skipped count in the summary.

Order: blockers first, then concerns, then nits, then debunked.

## Step 5: Summary

After all tasks are created, present a concise report:

1. **Architecture assessment**: 2-4 sentences on whether the overall approach is sound, separation of concerns, and any fundamental design trade-offs
2. **Stats**: X agents ran, Y claims investigated, Z verified, W debunked, N already flagged on PR (skipped)
3. **Debunked**: One-liner per debunked claim with reason (e.g. `~~sessionUuid reuse~~ — sessionUuid IS submission.uuid`)
4. **Findings**: One-liner per verified finding with severity tag (e.g. `[concern] form-data.ts:165 — batch retention loop does sequential Tinybird FINAL calls`)
5. **Ask**: "Ready to go through the TODO list?"

## Step 6: Interactive Review

Go through each pending task one at a time.

For each pending task:

1. Mark current task as `in_progress`
2. Present the finding:
   - **What's wrong**: Clear explanation
   - **Why it matters**: What can go wrong
   - **How to fix**: Concrete code suggestion or approach
   - **Suggested PR comment**: To the point, no essay, include exact file and line
3. Wait for the user's response before advancing
4. When moving to next item: mark current task as `completed`, then present next

If the user disagrees or wants to skip, mark it `completed` and move on.
