---
name: create-commit
description: Create focused git commits with conventional commit messages and sensible scopes. Use when Codex needs to review staged or unstaged changes, group them into atomic commits, stage the right files, and write commit titles in `type(scope): description` format without changing code.
---

## Process

- Look at the current staged and unstaged changes with `git status` and `git diff`
- Stage changes if needed using `git add .`
- Create focused, atomic commits with clear messages
- Refrain from adding one big commit, instead create multiple smaller atomic commits when it makes sense to do so

## Scope Guidelines

Prefer feature/change-focused scopes over package names:

- **First choice**: Feature or domain names that describe what's being changed
- **Fallback**: Package names if no clear feature scope exists
- **Always use**: `deps`/`deps-dev` for dependency updates
- **Infrastructure**: Generic scopes like `ci`, `docker`, `scripts` are fine

## Rules

- Use conventional commit format: `type(scope): description`
- Keep title under 100 characters
- Use `--no-verify` for .md files
- Never use heredoc or cat for commit messages
- Avoid ANSI codes in commit messages
- Never adjust code when running this, only create commits

## Common Failure Modes

- Staging unrelated files into the same commit
- Using package names as scopes when a clearer feature/domain scope exists
- Writing one large catch-all commit instead of a small set of atomic commits
- Editing code while trying to perform a commit-only task
