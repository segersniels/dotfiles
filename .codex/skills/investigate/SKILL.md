---
name: investigate
description: "Investigate without making code changes. Use when the user wants read-only discovery first: catch up on a codebase, understand current behavior, trace a bug, inspect diffs or logs, gather context, or report findings and next steps before any edits."
---

Stay in investigation mode. Build understanding, verify claims, and report findings. Do not edit files, generate code, or make repo changes unless the user explicitly asks to leave investigation mode.

## When to use

Use this skill when the user says or implies:
- investigate first
- no code changes yet
- catch me up on this codebase
- understand how this works
- look into this bug and report findings
- inspect current diffs, logs, or behavior before proposing a fix

## Workflow

### 1. Set scope

Pick the narrowest scope that answers the request:
- specific file, package, feature, bug, commit, branch, or PR
- if unclear, make the safest reasonable assumption and state it

### 2. Gather context with read-only actions

Prefer read-only inspection:
- `git status`, `git diff`, `git log`, `git show`
- `rg`, `find`, `sed`, `cat`, `ls`
- read `AGENTS.md` and nearby convention files when relevant
- inspect logs, stack traces, configs, tests, and call sites

If the question depends on external behavior, browse primary docs and quote exact errors or messages when useful.

### 3. Trace the real behavior

Do not stop at the first likely answer. Follow the path:
- entrypoints
- callers and consumers
- shared helpers
- config and environment assumptions
- tests covering the same flow

Verify claims against the actual code and usage sites.

### 4. Keep the session non-mutating

Do not:
- edit files
- run formatters or code generators
- install dependencies
- create commits, branches, or PRs
- use destructive commands

Avoid commands with side effects. If a build, test, or dev server may write files, change state, or be expensive, call that out before running it.

### 5. Report findings

Respond with concise sections:
1. Understanding
2. Findings
3. Evidence
4. Unknowns or risks
5. Recommended next step

When helpful, include:
- likely root cause
- competing hypotheses
- impacted files or modules
- what should be checked next

### 6. Stop before implementation

If the user also wants a fix, stop after the investigation report and wait for explicit approval before making changes.
