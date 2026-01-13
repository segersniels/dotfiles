---
description: Review and refine uncommitted code changes
argument-hint: [INSTRUCTIONS=<instructions>]
---

Review this code like a senior engineer. Identify issues, bad patterns, and areas for improvement. Simplify aggressively — favor clarity, readability, and maintainability over cleverness. Optimize for performance and simplicity. Keep behavior identical unless fixing a bug. 

Prioritize $INSTRUCTIONS when provided.

# Step 1: Analyze Changes

If $INSTRUCTIONS is provided and contains:
1. A base branch:
  - Run `git diff <base_branch>...HEAD` to see the changes.
2. A PR URL:
  - Run `gh pr view <pr_url>` to see the changes.
3. A commit hash or PR URL:
  - Run `git show <commit_hash>` to see the changes.

Additionally also check:
- Check **staged changes** (`git diff --staged`)
- Check **unstaged changes** (`git diff`)
- List all modified files

# Step 2: Understand the Context

For each modified file:

- Read the **full file** (not just the diff) to understand context
- Note the existing patterns and conventions
- Understand the purpose of the changes

# Step 3: Review the Code

Look for:

- **Complexity** — can this be simplified? Is cleverness hiding clarity?
- **Bad patterns** — anti-patterns, code smells, inconsistencies
- **Duplication** — should this be extracted into a helper?
- **Performance** — obvious issues, unnecessary work, missing optimizations
- **Naming** — are variables/functions clearly named?
- **Edge cases** — missing error handling or null checks?

# Step 4: Apply Refinements

For each issue:

1. Explain the problem briefly
2. Fix it directly in the code
3. Keep behavior identical (unless it's a bug)

**Do NOT:**

- Over-engineer or add unnecessary abstractions
- Refactor code that wasn't part of the changes
- Add features or improvements beyond what's needed
- Change working code just because you'd write it differently

# Priorities

1. Simplify complex code
2. Improve readability
3. Optimize performance (only where impactful)
