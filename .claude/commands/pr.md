---
description: "Create a pull request by analyzing code changes and commit history."
allowed-tools: ["Bash", "Read", "Edit", "MultiEdit", "TodoWrite"]
argument-hint: "[origin] [draft]"
---

# pr

Create a pull request by analyzing code changes and commit history.

## Process

1. Run `git fetch --all --prune` to ensure the latest changes are fetched
2. Check git status and current branch
3. Get commit history from [origin] to HEAD
4. Analyze `git diff [origin]...HEAD` to understand changes
5. Create a pull request with a descriptive title and body based on actual code changes
6. Use `gh` to create the PR
7. Assign the current git user to the created PR

## Analysis

- Examine modified files and functionality changes
- Understand technical implementation and business impact
- Focus on what changed, not just commit messages

## Rules

- If [origin] was not provided by the user, prompt the user for the base branch (don't make assumptions)
- Respect [origin] as the base branch and preferably prefix it with origin/[origin] if not already present so we check against the latest changes (local might be stale)
- Write meaningful descriptions based on diff analysis
- Never include checkboxes, test plans, or checklists
- Avoid ANSI codes in descriptions
- Pass markdown directly to gh, never use heredoc
- When writing PR titles or bodies, wrap every code identifier (variable names, params, functions, keys, enum values) in backticks.
- The title of the PR should follow conventional commit standards
- Use markdown and differentiate between sections using ###

