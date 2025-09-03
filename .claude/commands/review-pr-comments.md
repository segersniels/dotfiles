---
description: "Comprehensively review PR comments, fix valid issues, and reply to commenters"
allowed-tools: ["Bash", "Read", "Edit", "MultiEdit", "TodoWrite"]
argument-hint: "[PR number or URL]"
---

# PR Comment Review & Resolution

Fetch ALL PR comments (regular + inline), analyze their validity, fix high-value issues with separate commits, and reply to commenters with proper @mentions.

## Workflow:

1. **Fetch All Comments** - Get complete comment data using GitHub API
2. **Analyze PR Context** - Review the actual changes to understand scope  
3. **Categorize Comments** - Separate high-value fixes from low-value style preferences
4. **Create Action Plan** - Todo list of valid issues to address
5. **Fix Issues Individually** - Make changes, then lint/typecheck before committing
6. **Commit & Push** - Create atomic commits and push to remote
7. **Reply to Comments** - Reply to commenters with commit references (only after push)

## Comment Categories:

**HIGH VALUE (Always Fix):**
- Null pointer/undefined access issues  
- Debug console.log statements
- Runtime safety problems
- Security vulnerabilities  
- Resource leaks
- Breaking changes

**LOW VALUE (Usually Skip):**
- Style/formatting preferences
- Subjective code organization
- Type assertions (unless clearly unsafe)
- Minor performance micro-optimizations  
- Opinionated architectural suggestions

## Critical Workflow Rules:

- **Always fetch both regular AND inline code comments**
- **ALWAYS run linting and typechecking BEFORE committing each fix**:
  - `npm run lint:fix` (or equivalent for the project)
  - `npm run typecheck` (or equivalent for the project) 
  - Fix any linting/type errors before proceeding to commit
- **ALWAYS commit and push to remote BEFORE replying to comments**
- **Use proper @mentions in all replies**
- **Create separate commits for each distinct issue**

## Reply Templates:

**For fixes:**
```
✅ Fixed in commit {commit-hash}. 

{Brief explanation of what was changed}

Thanks for catching this @{username}.
```

**For declined suggestions:**
```
Thanks for the suggestion @{username}. This appears to be a style preference rather than a functional issue, so I'm leaving it as-is to focus on runtime safety fixes.
```

## Commands Used:
```bash
gh pr view {PR} --comments --json comments
gh api repos/{owner}/{repo}/pulls/{PR}/comments  
gh pr diff {PR}
# For each fix:
npm run lint:fix && npm run typecheck
git add {files} && git commit -m "fix: {description}"
git push origin {branch}
gh pr comment {PR} --body "{reply}"
```

This workflow ensures we address genuine bugs while maintaining positive team collaboration and avoiding style bikeshedding.

$ARGUMENTS