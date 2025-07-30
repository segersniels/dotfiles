---
description: "Analyze PR comments for value and fix high-impact issues individually"
allowed-tools: ["Bash", "Read", "Edit", "TodoWrite"]
argument-hint: "[optional: specific patterns to focus on]"
---

# Review PR Comments Workflow

Analyze CodeRabbit/review comments to identify genuinely valuable feedback vs. noise, then fix high-impact issues individually with separate commits.

## Process:

1. **Fetch PR comments** - Get all comments from the current PR
2. **Analyze for value** - Categorize comments by actual impact:
   - ✅ **High Value**: Runtime safety, null checks, debug code, security issues
   - ❌ **Low Value**: Style preferences, subjective organization, minor type complaints
3. **Create action plan** - Todo list for worthwhile fixes only
4. **Fix individually** - Address each high-value issue separately  
5. **Commit atomically** - Individual commits with descriptive messages
6. **Push changes** - Push all commits to remote before replying
7. **Reply to comments** - Respond to each fixed comment with confirmation and commit reference

## Focus Areas:

**Always Fix:**
- Null pointer/undefined access issues
- Debug console.log statements
- Runtime safety problems
- Security vulnerabilities
- Resource leaks

**Usually Skip:**
- Style/formatting preferences  
- Subjective code organization
- Type assertions (unless clearly unsafe)
- Minor performance micro-optimizations
- Opinionated architectural suggestions

## Push Before Reply:

**Critical**: Always push commits to remote before replying to comments to ensure:
- ✅ **Reviewers can see the fixes** immediately when they click commit links
- ✅ **CI/CD can run** on the updated code
- ✅ **No broken links** in comment replies
- ✅ **Professional workflow** - fixes are available before acknowledgment

```bash
git push origin [branch-name]
```

## Comment Replies:

After pushing all fixes, reply to the original comments with:
- ✅ **Confirmation** that the issue was addressed
- 🔗 **Commit reference** linking to the specific fix
- 📝 **Brief explanation** of what was changed (if needed)

**Reply Template:**
```
✅ Fixed in commit [commit-hash]. 

[Brief description of the change made]

Thanks for catching this!
```

For skipped comments, optionally reply explaining why:
```
Thanks for the suggestion! This appears to be a style preference rather than a functional issue, so I'm leaving it as-is for now to focus on runtime safety fixes.
```

## Usage:
```
/review-pr-comments
```

This workflow ensures we address genuine bugs while avoiding time-wasting style bikeshedding.

$ARGUMENTS