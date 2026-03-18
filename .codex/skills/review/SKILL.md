---
name: review
description: "Review code changes with repo-aware context, architecture scrutiny, claim verification, and actionable findings. Use for uncommitted changes, commits, branches, or PRs when you want a thorough but low-noise review."
metadata:
  short-description: Repo-aware code review
---

## Goal

Review changes thoroughly; prioritize real bugs, regressions, unnecessary complexity, and missing coverage; keep false positives low.

## Determine Review Target

Pick the narrowest source of truth that matches the input:

1. No arguments:
   - Run `git status --short`
   - Run `git diff`
   - Run `git diff --cached`
   - Include untracked files

2. Commit hash:
   - Run `git show $ARGUMENTS`

3. Branch name:
   - Run `git diff $ARGUMENTS...HEAD`

4. PR URL or number:
   - Run `gh pr view $ARGUMENTS --json title,number,body,headRefName,baseRefName,files`
   - If inside the repo and current branch matches `headRefName`, treat local checkout as source of truth
   - Otherwise use `gh pr diff $ARGUMENTS`

Use best judgment if input is ambiguous.

## Bootstrap Repo Context

Before reviewing, load the repo's own standards if present:

- `AGENTS.md`
- Files referenced from `AGENTS.md` that materially affect conventions or workflow
- `REVIEW.md`
- `VOICE.md`
- Other obvious convention files when relevant: `CONVENTIONS.md`, `.editorconfig`, package-level docs

Do not bulk-read reference docs blindly. Load the files most likely to affect the changed code.

## Gather Context

Diffs are not enough.

- Read full changed files, not only hunks
- Read nearby helpers, callers, exports, and tests when behavior changed
- Trace impacted call sites if return shape, control flow, types, or side effects changed
- For PR reviews, read existing review comments first so you do not re-flag resolved or already-raised points:
  - `gh api repos/{owner}/{repo}/pulls/{number}/comments`
  - `gh api repos/{owner}/{repo}/issues/{number}/comments`

If the branch is checked out locally, prefer local files over remote file contents.

If the relevant code is available locally and the current environment allows sub-agents, prefer using the explorer subagent early to gather:

- changed-file context
- surrounding code and prior art
- local conventions and patterns
- nearby helpers, tests, and callers

Use it to gather evidence faster, not to replace your own verification.

## Review Passes

Run these passes in order.

### 1. Architecture Pass

Assess the overall approach before drilling into line comments:

- Simplest viable solution?
- Scope creep or unrelated changes?
- Clear separation of concerns?
- Missing edge cases or lifecycle coverage?
- Security or data-integrity concerns?
- Existing abstraction/pattern available but ignored?

### 2. File and Flow Pass

For each changed area:

- Trace control flow and data flow end to end
- Check callers and consumers for behavior drift
- Check error handling, async behavior, race conditions, stale closures
- Check performance only when it is obviously meaningful
- Check tests for changed behavior
- Check consistency with surrounding package patterns

### 3. Convention Pass

Use repo conventions to filter findings:

- Flag real convention violations that matter for maintainability or correctness
- Do not nitpick style preferences unless the repo clearly requires them
- Prefer project-specific guidance over generic best-practice dogma

## What to Look For

Prioritize:

- Logic bugs
- Regressions in callers/consumers
- Missing guards or broken edge cases
- Security/privacy issues
- Broken or invisible error handling
- Unnecessary complexity / over-engineering
- Duplication where a clear existing helper should be reused
- Missing or weak tests for changed logic

Only flag performance when the cost is realistic and material.

## Claim Verification

Before reporting a finding, verify it.

1. Read the actual code around the claim
2. Follow the call chain or data path yourself
3. Check assumptions with grep/search
4. Reconcile duplicate or conflicting observations
5. Mentally test realistic edge cases against the real code

If unsure after investigation, say so and do not present it as a definite bug.

Common mistakes to avoid:

- Confusing similar identifiers or types
- Missing higher-level error handling
- Missing hidden framework behavior already covering the case
- Reporting style discomfort as correctness issues
- Escalating theoretical edge cases with no realistic failure path

## Optional Parallelization

For large PRs, you may split review work across sub-agents only when the current environment allows it or the user explicitly asks for delegation.

Suggested split:

- One architecture reviewer
- One or more file/area reviewers

You must still verify every claim yourself before reporting it.

## Severity

Use this taxonomy:

- `blocker`: likely bug, regression, security issue, or merge-stopping risk
- `concern`: meaningful issue worth fixing before merge
- `nit`: small clarity or maintainability issue; non-blocking

Do not inflate severity.

## Output

Start with the review target title when available.

Then provide:

1. High-level assessment
   - 2-4 sentences
   - Overall soundness, scope, architecture tradeoffs

2. Findings
   - Verified findings only
   - Ordered: `blocker`, `concern`, `nit`
   - Include file + line
   - Explain what is wrong and why it matters

3. Debunked / checked items
   - Briefly list claims you investigated and rejected when that context is useful

4. Actionable review comments
   - Provide GitHub-ready comment text for non-trivial findings

When the environment supports inline review directives, emit one `::code-comment` per finding in addition to the written summary.

## Output Rules

- Findings first; summary brief
- Review only the changes and their impact surface
- Do not pad with praise
- Do not invent issues to "balance" the review
- If there are no findings, say so explicitly and mention residual risk or test gaps
- Prefer concise, concrete language over long essays

## Helpful Commands

- `git status --short`
- `git diff`
- `git diff --cached`
- `git show <sha>`
- `gh pr view <pr> --json title,number,body,headRefName,baseRefName,files`
- `gh pr diff <pr>`
- `gh api repos/{owner}/{repo}/pulls/{number}/comments`
- `gh api repos/{owner}/{repo}/issues/{number}/comments`
- `rg`

## Notes

- Use local source of truth when the relevant branch is checked out
- Prefer repo-specific review guidance over generic style instincts
- Thorough and low-noise beats exhaustive and speculative
