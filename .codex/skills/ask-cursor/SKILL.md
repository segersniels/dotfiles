---
name: ask-cursor
description: Ask Cursor Agent/Composer for a read-only second opinion through the local `agent prompt` CLI. Use when the user asks to run a solution, implementation, plan, diff, frontend change, design choice, or Codex-written code past Cursor/Composer; asks whether Composer agrees; asks how Cursor would approach it; or wants confirmation, critique, or inspiration from Cursor before continuing.
---

# Ask Cursor

## Overview

Ask Cursor for an external opinion by giving it explicit context and a bounded question. Use it to check whether Composer agrees with Codex's implementation, to surface simpler or more idiomatic approaches, or to get inspiration before committing to a direction.

## Workflow

1. Confirm `agent` exists with `command -v agent` if it has not been checked in the current turn.
2. Run Cursor through Codex's macOS sandbox wrapper with `:danger-full-access`. Direct `agent` calls from Codex can fail to see macOS Keychain-backed auth even when the same command works in the user's terminal.
3. Check authentication through the wrapper:
   `codex sandbox macos --permissions-profile :danger-full-access --cd "$PWD" agent status`
   Continue only when it reports a logged-in user; otherwise quote the exact output and ask the user to authenticate.
4. Gather the smallest useful context:
   - user question, proposed approach, or decision to review
   - relevant file paths and snippets
   - `git diff` or focused diff when reviewing recent edits
   - screenshots or UI notes summarized in text when reviewing frontend work
   - constraints such as "KISS", "read-only", "do not suggest broad refactors"
5. Do not send secrets, credentials, private customer data, or large unrelated files.
6. Run Cursor through the wrapper in print mode with the prompt as the command argument.
7. Wait for the command to complete and use stdout as Cursor's answer in the current context.
8. Summarize Cursor's agreement, disagreement, and alternative approach ideas. Do not blindly adopt Cursor's conclusion.

## Prompt Shape

Use this structure:

```text
You are giving a second opinion only.
Do not edit files. Do not run commands unless explicitly asked.
Review the supplied solution/implementation and answer the question.

Question:
...

Current solution or approach:
...

Constraints:
- Be direct.
- Say whether you agree with the direction.
- Focus on correctness, hidden risks, simpler alternatives, UX/frontend quality when relevant, and missing tests.
- If you would approach it differently, describe the smallest useful alternative.
- Ignore unrelated style preferences unless they affect maintainability.

Context:
...

Return:
- Verdict
- Agreement/disagreement
- Concerns
- Alternative approach or inspiration
- Concrete next steps
- Confidence
```

## Command

Prefer the user's requested model when provided. Otherwise default to `composer-2.5`.

```bash
codex sandbox macos --permissions-profile :danger-full-access --cd "$PWD" agent prompt --print --yolo --model composer-2.5 --mode ask --output-format text 'You are giving a second opinion only.
Do not edit files. Do not run commands unless explicitly asked.

Question:
...

Current solution or approach:
...

Context:
...'
```

Keep paths with glob characters quoted before first use. If the prompt would be huge, trim to the relevant snippets or diff before calling Cursor. Do not write prompt temp files unless the direct command fails because of shell length or quoting limits.

Do not use `--force` or `--sandbox disabled` for ask requests. Cursor's print mode can access write and shell tools unless constrained; keep `--mode ask` unless the user explicitly asks for a different mode. Use `--yolo` only to bypass Cursor's workspace-trust prompt for this read-only ask flow.

## Reporting Back

Return a concise synthesis:

- Cursor verdict
- Where Cursor agrees or disagrees with Codex's direction
- Any concrete issue worth acting on
- Any smaller or more idiomatic alternative worth considering
- Where Cursor's answer seems speculative or conflicts with local evidence
- Your recommendation as Codex

If the CLI fails, quote the exact error and continue with the local analysis.
