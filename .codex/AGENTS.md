# AGENTS.MD

## Agent protocol

- Prefer end-to-end verify; if blocked, say what’s missing.
- Web: search early; quote exact errors;
- Use repo’s package manager/runtime; no swaps w/o approval.
- Respect current repository AGENTS.md and references when applicable.
- Style: telegraph. Drop filler/grammar. Min tokens (global AGENTS + replies).

## Workflow

- Never commit or push unless explicitly asked.
- Branch changes need consent; no destructive ops unless asked.
- Commits: Conventional Commits (`feat|fix|refactor|build|ci|chore|docs|style|perf|test`).
- Shell paths: quote/escape any path with glob chars before first use, especially Next.js route segments like `[slug]`, `[...rest]`, `[[...rest]]`; never let zsh expand them first.
- Before commit: ALWAYS run full gate (lint, typecheck) - evaluate warnings!
- Tests: run if present; ask before adding new tests
- Bugs: add regression tests when it makes sense

## Critical thinking

- Fix root cause (not band-aid).
- Unsure: read more code; if still stuck, ask w/ short options.
- Conflicts: call out; pick safer path.
- Unrecognized changes: assume other agent; keep going; focus your changes. If it causes issues, stop + ask user.
- Leave breadcrumb notes in thread.

## Code style

- When writing, editing, or reviewing code, use the `human-code` skill for behavior-preserving readability: code flow, naming, comments, spacing, guard clauses, and reviewability.
