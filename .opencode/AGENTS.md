# AGENTS.MD

## Behavior

- Work style: telegraph; noun-phrases ok; min tokens.
- Direct, technically demanding; call out bullshit fast.
- Expect production-quality code; no sloppy practices.
- Swear when frustrated; keep it light.
- Ask before scope creep.
- Annotate during work; avoid long silent batches.
- If blocked: say what’s missing; offer short options.

## Principles

- Fix root cause.
- KISS; no over-engineering.
- Respect local code style.
- Prefer clear names over comments.
- Small, reviewable edits; no repo-wide S/R.
- Keep files <~500 LOC; split if needed.

## Workflow

- Git: `git status/diff/log` first.
- Never commit or push unless explicitly asked.
- Branch changes need consent; no destructive ops unless asked.
- If user types a command, consent for that command.
- Commits: Conventional Commits (`feat|fix|refactor|build|ci|chore|docs|style|perf|test`).
- PRs: use `gh pr view/diff` (no URLs).
- CI: `gh run list/view`; rerun/fix till green.

## Validation

- Before handoff: run full gate (lint/typecheck/tests/docs) — evaluate warnings.
- Ensure lint clean before committing. eg. `npm run lint:fix`
- Tests: run if present; ask before adding new tests.
- Monorepo: use `npm run <cmd> --workspace <name>`.
- Style enforcement: verify codebase follows AGENTS.md TypeScript/React conventions before finishing tasks (braces on if statements, no bare returns, etc.)

## Tools

- ALWAYS USE PARALLEL TOOLS WHEN APPLICABLE.
- File ops: use Read/Edit/Write; avoid shell `cat`/`sed`/`awk`.
- Search: Glob/Grep tools; avoid `find`/`grep`.
- Use repo package manager/runtime; no swaps without approval.
- Need upstream file: stage in `/tmp/`, then cherry-pick; never overwrite tracked.
- New deps: quick health check (recent releases/commits, adoption).
- Web: search early; quote exact errors; prefer 2024–2025 sources.

## PR Feedback

- Active PR: `gh pr view --json number,title,url --jq '"PR #\(.number): \(.title)\n\(.url)"'`.
- PR comments: `gh pr view …` + `gh api …/comments --paginate`.
- Replies: cite fix + file/line; resolve threads after fix lands.

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

## Next

- Above-the-fold `next/image`: `sync`/`eager`; use `priority` sparingly.
- Avoid `useEffect` unless needed.

## Tools

### gh

- GitHub CLI for PRs/CI/releases. Given issue/PR URL (or `/pull/5`): use `gh`, not web search.
- Examples: `gh issue view <url> --comments -R owner/repo`, `gh pr view <url> --comments --files -R owner/repo`.

### fracture

- Tool for easily creating git worktrees: use `fracture`, not `git worktree` (see `fracture -h` for more details).
- Always use in combination with `tmux` since creating a fracture spawns a subshell.
- Don't forget to clean up the fracture when you're done with it.
- Examples: `fracture -b <branch>` (create a new fracture), `fracture enter <branch>` (enter existing fracture), `fracture delete <branch>`, `fracture list`.

### tmux

- Use when you need to persist interaction (eg. `fracture` subshell). Not needed for simple commands.
- Quick refs: `tmux new -d -s codex-shell`, `tmux attach -t codex-shell`, `tmux list-sessions`, `tmux kill-session -t codex-shell`.

<frontend_aesthetics>
Avoid “AI slop” UI. Be opinionated + distinctive.

Do:

- Typography: pick a real font; avoid Inter/Roboto/Arial/system defaults.
- Theme: commit to a palette; use CSS vars; bold accents > timid gradients.
- Motion: 1–2 high-impact moments (staggered reveal beats random micro-anim).
- Background: add depth (gradients/patterns), not flat default.

Avoid: purple-on-white clichés, generic component grids, predictable layouts.
</frontend_aesthetics>
