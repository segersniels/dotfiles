---
name: commit
description: Stage and create focused Conventional Commits when the user requests commits or splitting changes into commits.
---

Create small commits that each have one reason to revert.

## Scope

For a commit-only request, do not edit code, format files, or change generated output. If implementation is also authorized, finish and validate it before entering the commit phase. Do not rewrite code merely to make commit boundaries easier.

Loading this skill does not authorize a commit or push. Use the user's existing authorization, including an explicitly requested workflow that includes committing. Continue any authorized push or delivery steps after committing.

## Inspect and stage

- Inspect the worktree, index, and relevant diffs before staging. Leave unrelated user changes untouched, including unrelated staged changes.
- Choose the smallest coherent commit set. Split independently revertible concerns; keep changes together when separation would leave the repository broken or misleading.
- Use explicit paths or selected hunks and inspect `git diff --cached` before each commit. Use `git add .` only when the whole worktree is verified as one atomic change.
- Complete required project checks and evaluate warnings before committing. Reuse successful checks when the relevant source, configuration, dependencies, and environment are unchanged, unless the repository requires a fresh run.

## Commit boundaries

| Change | Commit type and grouping |
| --- | --- |
| Runtime dependencies | `chore(deps)`; keep the relevant manifest and lockfile changes together, separate from app code. |
| Development, test, or build dependencies | `chore(deps-dev)`; keep the relevant manifest and lockfile changes together. |
| Tooling, config, or setup | `chore(scope)`; separate when independently revertible. |
| Behavior-preserving refactor or mechanical move | `refactor(scope)`; separate from behavior changes when viable. |
| Documentation only | `docs(scope)`. |
| Feature or fix | `feat(scope)` or `fix(scope)`; keep tests with the behavior they prove. Split independent test infrastructure into `test(scope)`. |

For example, adding a mail package and a password-reset flow normally produces `chore(deps): add nodemailer` followed by `feat(auth): add password reset flow`. Prefer small commits when boundaries remain ambiguous, and state the assumption.

## Messages and completion

Use `type(scope): description`, with a feature or domain scope when available. Keep the title under 100 characters and describe the outcome. Prefer title-only commits; add a body for a useful rationale, migration note, or non-obvious constraint.

Do not use heredoc or `cat` for commit messages, or include ANSI codes. Avoid `--no-verify`; reserve it for docs-only commits when hooks are clearly irrelevant and repository instructions permit it.

Verify the resulting commits and remaining worktree/index state. Report what was committed and any uncommitted changes relevant to the request.
