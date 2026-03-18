---
name: create-pull-request
description: Create GitHub pull requests from the current branch with accurate titles and bodies derived from the real diff. Use when Codex needs to inspect commits and changed files, confirm the correct base branch and draft status, and open a PR with conventional-commit style titling and concise markdown sections.
---

## Process

1. Run `git fetch --all --prune` to ensure the latest changes are fetched
2. Check git status and current branch
3. Get commit history from [origin] to HEAD
4. Analyze `git diff [origin]...HEAD` to understand changes
5. Prompt the user for the [origin] (don't make assumptions)
5. Confirm with the user whether it needs to be a draft PR or not
7. Create a pull request with a descriptive title and body based on actual code changes (`gh`)
8. Assign the current git user to the created PR

## Analysis

- Examine modified files and functionality changes
- Understand technical implementation and business impact
- Focus on what changed, not just commit messages

## Rules

- **PR title MUST use Conventional Commits format**: `type(scope): description`
  - Lowercase, imperative mood (same as commit messages)
  - Optional Notion ticket ID in brackets at end: `[TL-1234]`
- Write meaningful descriptions based on diff analysis
- Never include checkboxes, test plans, or checklists
- Avoid ANSI codes in descriptions
- Pass markdown directly to gh, never use heredoc
- Use markdown and differentiate between sections using ###
- When writing PR titles or bodies, wrap every code identifier (variable names, params, functions, keys, enum values) in backticks.

## Common Failure Modes

- Assuming the base branch instead of asking the user
- Writing the PR body from commit messages instead of the actual diff
- Forgetting to confirm whether the PR should be draft or ready
- Including checklists or test-plan boilerplate that the repo does not want
