---
description: "Prepare a new branch ready to be pushed and ready to be used in a PR."
allowed-tools: ["Bash", "Read", "Edit", "MultiEdit", "TodoWrite"]
argument-hint: "[branch name]"
---

# Branch

Prepare a new branch ready to be pushed and ready to be used in a PR.

# Workflow:

1. **Create a new branch** - Create a new branch for the new feature
2. **Make atomic commits** - Look at the diff of the branch and make atomic commits

# Commits

## Process
1. Review current changes with `git status` and `git diff`
2. Stage changes if needed
3. Create focused, atomic commits with clear messages

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
