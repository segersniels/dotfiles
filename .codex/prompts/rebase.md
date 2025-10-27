---
description: "Look at the current rebase state and help the user finish it."
allowed-tools: ["Bash", "Read", "Edit", "MultiEdit", "TodoWrite"]
argument-hint: "[instructions]"
---

# rebase

Look at the current rebase state and help the user finish it.

## Process
1. Check git status 
2. Look at the affected files
3. Figure out what needs to be done to finish the rebase
4. After resolving all conflicts run `git add . && git rebase --continue ; git status`
5. Continue until rebase is done

## Analysis
- Examine modified files and functionality changes
- Understand technical implementation and business impact
- Focus on what changed
- Ask the user for any missing information if you're unsure
