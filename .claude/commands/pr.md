---
description: "Create a pull request by analyzing code changes and commit history."
allowed-tools: ["Bash", "Read", "Edit", "MultiEdit", "TodoWrite"]
argument-hint: "[origin]"
---

# pr

Create a pull request by analyzing code changes and commit history.

## Process
1. Check git status and current branch
2. Get commit history from develop to HEAD
3. Analyze `git diff develop...HEAD` to understand changes
4. Create descriptive PR title and body based on actual code changes

## Analysis
- Examine modified files and functionality changes
- Understand technical implementation and business impact
- Focus on what changed, not just commit messages

## Rules
- Use develop as base branch
- Write meaningful descriptions based on diff analysis
- Never include checkboxes, test plans, or checklists
- Avoid ANSI codes in descriptions
- Pass markdown directly to gh, never use heredoc
