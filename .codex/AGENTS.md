# AGENTS.MD

Work style: telegraph; noun-phrases ok; drop grammar; min tokens.

## Agent Protocol
- Contact: Niels Segers (@segersniels, github@niels.foo).
- PRs: use `gh pr view/diff` (no URLs).
- “Make a note” => edit AGENTS.md (shortcut; not a blocker). Ignore `CLAUDE.md`.
- Need upstream file: stage in `/tmp/`, then cherry-pick; never overwrite tracked.
- Bugs: add regression test when it fits.
- Keep files <~500 LOC; split/refactor as needed.
- Commits: Conventional Commits (`feat|fix|refactor|build|ci|chore|docs|style|perf|test`).
- CI: `gh run list/view` (rerun/fix til green).
- Prefer end-to-end verify; if blocked, say what’s missing.
- New deps: quick health check (recent releases/commits, adoption).
- Web: search early; quote exact errors; prefer 2024–2025 sources.
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

## TypeScript

- JSDoc for multiline comments.
- Prefer `for (const item of array)` loops.
- Early returns/continues.
- Empty line before return (except single-line).
- Types PascalCase; enum values UPPER_CASE.
- Always use braces for if statements so no `if (condition) return;` statements.
- Add blank newline between subsequent if statements.
- Avoid try/catch unless needed.
- Don’t cast to `any` unless required.

## React

- Avoid massive JSX; compose smaller components.
- Prefer compound components.
- Use flexbox for layout with gap for spacing.

## Next

- Above-the-fold `next/image`: `sync`/`eager`; use `priority` sparingly.
- Avoid `useEffect` unless needed.

## Build / Test Validation

- Before commit: run full gate (lint/typecheck/tests/docs) — evaluate warnings.
- Tests: run if present; ask before adding new tests. 
- Bugs: add regression test when it fits.
- Style enforcement: verify codebase follows AGENTS.md TypeScript/React conventions before finishing tasks (braces on if statements, no bare returns, etc.)

## PR Feedback
- Active PR: `gh pr view --json number,title,url --jq '"PR #\\(.number): \\(.title)\\n\\(.url)"'`.
- PR comments: `gh pr view …` + `gh api …/comments --paginate`.
- Replies: cite fix + file/line; resolve threads only after fix lands.

## Critical Thinking
- Fix root cause (not band-aid).
- Unsure: read more code; if still stuck, ask w/ short options.
- Conflicts: call out; pick safer path.
- Unrecognized changes: assume other agent; keep going; focus your changes. If it causes issues, stop + ask user.
- Leave breadcrumb notes in thread.

## Tools

### gh

- GitHub CLI for PRs/CI/releases. Given issue/PR URL (or `/pull/5`): use `gh`, not web search.
- Examples: `gh issue view <url> --comments -R owner/repo`, `gh pr view <url> --comments --files -R owner/repo`.
