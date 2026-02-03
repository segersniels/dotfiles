---
name: Simplify Code
description: Simplify and refine uncommitted changes - remove slop, fix patterns, improve clarity
---

Review changes like a senior engineer. Simplify aggressively — clarity over cleverness. Keep behavior identical unless fixing a bug.

## Step 1: Determine scope

Check what the user wants reviewed:
- If they mention "staged": `git diff --staged`
- If they mention "unstaged": `git diff`
- If they mention a branch: `git diff <branch>...HEAD`
- If they mention specific file(s): read those files directly
- If unspecified: run `git status` to see what's available, then ask or pick the most sensible option

## Step 2: Read full context

For each modified file, read the **full file** to understand existing patterns.

## Step 3: Look for issues

**Structural simplification:**
- Functions taking derived values → accept discriminators, derive internally
- Multiple "paired" params → single type discriminator
- Unnecessary interfaces for obvious params
- Utility wrappers around single values (`fn({ x })` → `fn(x)`)

**AI slop removal:**
- Comments a human wouldn't add or inconsistent with file style
- Excessive defensive checks / try-catch in trusted codepaths
- Casts to `any` to bypass type issues
- Unnecessary emoji usage
- Style inconsistent with the file

**General cleanup:**
- Complexity that can be simplified
- Duplication that should be extracted
- Anti-patterns / code smells
- Poor naming
- Missing null checks / edge cases
- Performance issues (unnecessary work, missing optimizations)

## Step 4: Apply fixes

For each issue:
1. Explain briefly
2. Fix directly
3. Keep behavior identical

**Do NOT:**
- Refactor code outside the changes
- Over-engineer or add abstractions
- Add features beyond what's needed
- Change working code just because you'd write it differently

## Step 5: Summarize

End with 1-3 sentences of what changed.
