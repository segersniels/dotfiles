---
name: create-commit
description: "Create focused git commits without changing code. Use when Codex needs to review staged or unstaged changes, split work into small atomic commits, separate dependency updates from feature work, stage the right files, and write conventional commit titles in `type(scope): description` format."
---

Create commits only. Do not edit code, format files, or change generated output.

## Workflow

1. Inspect before staging
- Run `git status --short`, `git diff --stat`, `git diff --cached --stat`, and targeted diffs as needed.
- Identify unrelated user changes and leave them untouched.
- Do not start with `git add .`.

2. Plan commit buckets
- Define the smallest valid commit set before staging anything.
- Make each commit one reason to revert.
- Prefer extra small commits over one broad commit when either would work.
- If the diff mixes independent concerns, split them.

3. Split by change type
- Put added, removed, or updated runtime dependencies in `chore(deps): ...`.
- Put added, removed, or updated dev, test, or build dependencies in `chore(deps-dev): ...`.
- Keep manifest and lockfile changes with the dependency commit, not with `feat(...)` or `fix(...)`.
- Put pure tooling, config, or setup changes in `chore(scope): ...`.
- Put refactors with no behavior change in `refactor(scope): ...`.
- Put docs-only changes in `docs(scope): ...`.
- Keep tests with the behavior change they prove unless the test harness or test-only plumbing changed; then split `test(scope): ...`.

4. Stage one bucket at a time
- Use explicit paths or `git add -p`.
- Re-check the staged diff before each commit with `git diff --cached`.
- If one file contains multiple concerns, split hunks instead of bundling the whole file.

5. Commit
- Use `type(scope): description`.
- Prefer feature or domain scopes; fall back to package names only when no clearer scope exists.
- Use `deps` or `deps-dev` scopes for dependency updates.
- Keep the title under 100 characters and describe the outcome, not the implementation.

## Atomic Commit Heuristics

Split commits when any of these are true:

- A dependency or lockfile change appears beside app code.
- Two files support different user-visible changes.
- A mechanical rename or move sits beside logic changes.
- Config or CI changes only enable later feature work.
- Part of the diff could be reverted safely without the rest.

Keep changes together only when separating them would leave the repo broken or misleading.

## Examples

Use examples to reason about commit boundaries, not to justify bundling.

Example: mixed feature and dependency diff
- If `package.json` and lockfiles add a new package for password reset and app code adds the flow, split it:
- `chore(deps): add nodemailer`
- `feat(auth): add password reset flow`

Example: pure dependency update
- If the change is only upgrading a runtime package and its lockfile, use:
- `chore(deps): update react-native to 0.72.0`

Example: fix plus unrelated setup
- If Android NFC timeout logic changes and CI or Gradle config also changes, split it:
- `chore(ci): update Android build configuration`
- `fix(scanner): resolve NFC timeout on Android`

Example: behavior-preserving cleanup
- If the change only consolidates duplicate API error handling with no user-visible behavior change, use:
- `refactor(api): simplify error handling`

Prefer title-only commits by default. Add a commit body only when it adds important context such as why the change was necessary, a migration note, or a non-obvious constraint.

## Guardrails

- Never use `git add .` unless the whole worktree is already verified as one atomic change.
- Never commit unrelated staged changes just because they are present.
- Never rewrite code to make commits cleaner.
- Avoid `--no-verify`; reserve it for docs-only commits when hooks are clearly irrelevant.
- Never use heredoc or `cat` for commit messages.
- Avoid ANSI codes in commit messages.
- If the split is ambiguous, choose the smaller commits and state the assumption.

## Common Failure Modes

- Bundling dependency changes into `feat(...)` or `fix(...)`.
- Grouping setup, refactor, and behavior changes into one commit.
- Using package names as scopes when a clearer domain scope exists.
- Treating "same feature" as "same commit" even when the work has separable steps.
