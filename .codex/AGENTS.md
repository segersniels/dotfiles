# AGENTS.MD

## Agent Protocol

- PRs: use `gh pr view/diff` (no URLs).
- Need upstream file: stage in `/tmp/`, then cherry-pick; never overwrite tracked.
- Keep files <~500 LOC; split/refactor as needed.
- Commits: Conventional Commits (`feat|fix|refactor|build|ci|chore|docs|style|perf|test`).
- CI: `gh run list/view` (rerun/fix til green).
- Prefer end-to-end verify; if blocked, say what’s missing.
- Web: search early; quote exact errors;
- Use repo’s package manager/runtime; no swaps w/o approval.
- Style: telegraph. Drop filler/grammar. Min tokens (global AGENTS + replies).

## Workflow

- Git: `git status/diff/log` first.
- Never commit or push unless explicitly asked.
- Branch changes need consent; no destructive ops unless asked.
- If user types a command, consent for that command.
- Commits: Conventional Commits (`feat|fix|refactor|build|ci|chore|docs|style|perf|test`).
- PRs: use `gh pr view/diff` (no URLs).
- CI: `gh run list/view`; rerun/fix till green.
- Monorepo: use `npm run <cmd> --workspace <name>`.
- Shell paths: quote/escape any path with glob chars before first use, especially Next.js route segments like `[slug]`, `[...rest]`, `[[...rest]]`; never let zsh expand them first.
- Before commit: run full gate (lint, typecheck) - evaluate warnings
- Tests: run if present; ask before adding new tests
- Bugs: add regression tests when it makes sense

## Critical Thinking

- Fix root cause (not band-aid).
- Unsure: read more code; if still stuck, ask w/ short options.
- Conflicts: call out; pick safer path.
- Unrecognized changes: assume other agent; keep going; focus your changes. If it causes issues, stop + ask user.
- Leave breadcrumb notes in thread.

## Agents

### explorer

- Read-only codebase explorer for targeted file reads.

## Tools

### git

- Do not use in parallel to prevent getting stuck on `index.lock` during commit

### gh

- GitHub CLI for PRs/CI/releases. Given issue/PR URL (or `/pull/5`): use `gh`, not web search.
- Examples: `gh issue view <url> --comments -R owner/repo`, `gh pr view <url> --comments --files -R owner/repo`.
