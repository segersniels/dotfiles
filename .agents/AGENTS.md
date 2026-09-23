# AGENTS.MD

## Agent protocol

- Prefer end-to-end verify; if blocked, say what’s missing.
- Web: search early; quote exact errors;
- Use repo’s package manager/runtime; no swaps w/o approval.
- Respect current repository AGENTS.md and references when applicable.
- Style: short, complete, active-voice sentences. Remove filler. Use ASD-STE100 Simplified Technical English principles.

## Workflow

- Prefer harness tools over manual scripts when they can perform the required task.
- Never commit or push unless explicitly asked.
- Branch changes need consent; no destructive ops unless asked.
- Commits: Conventional Commits (`feat|fix|refactor|build|ci|chore|docs|style|perf|test`).
- Shell paths: quote/escape any path with glob chars before first use, especially Next.js route segments like `[slug]`, `[...rest]`, `[[...rest]]`; never let zsh expand them first.
- Before commit, complete the repository-required gate, including applicable lint and typecheck, and evaluate warnings. For documentation or configuration work, use the required checks for those files.
- Run tests relevant to the change and all required repository checks. Reuse successful checks while the relevant source, configuration, dependencies, and environment are unchanged, unless the repository requires a fresh run. Repeat or broaden checks after new changes, failures, or unresolved concerns.
- Add focused regression tests when they materially verify a bug fix. A request for TDD or tests authorizes adding them. Ask before adding new test infrastructure or expanding test scope.

## Critical thinking

- Fix root cause (not band-aid).
- Unsure: read more code; if still stuck, ask w/ short options.
- Explicit user instructions take precedence over skill guidelines. A skill governs its part of the task and does not cancel other authorized work. Use established authorization; ask only when a material decision remains unresolved.
- Conflicts: call out material unresolved conflicts; continue independent authorized work.
- Unrecognized changes: assume other agent; keep going; focus your changes. If it causes issues, stop + ask user.
- Leave breadcrumb notes in thread.
