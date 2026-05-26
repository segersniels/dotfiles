---
name: ask-claude
description: Ask Anthropic Claude Opus/Claude Code for a read-only second opinion through the local `claude` CLI. Use when the user asks to run a solution, implementation, plan, diff, frontend change, design choice, or Codex-written code past Claude/Opus; asks whether Claude agrees; asks how Claude would approach it; or wants confirmation, critique, or inspiration from Claude before continuing.
---

# Ask Claude

## Overview

Ask Claude for an external opinion by giving it explicit context and a bounded question. Use it to check whether Claude agrees with Codex's implementation, to surface simpler or more idiomatic approaches, or to get inspiration before committing to a direction.

## Workflow

1. Confirm `claude` exists with `command -v claude` if it has not been checked in the current turn.
2. Run Claude through Codex's macOS sandbox wrapper with `:danger-full-access`. Direct `claude` calls from Codex can fail to see macOS Keychain-backed auth even when the same command works in the user's terminal.
3. Check authentication through the wrapper:
   `codex sandbox macos --permissions-profile :danger-full-access --cd "$PWD" claude auth status`
   Continue only when it reports `"loggedIn": true`; otherwise quote the exact output and ask the user to authenticate.
4. Gather the smallest useful context:
   - user question, proposed approach, or decision to review
   - relevant file paths and snippets
   - `git diff` or focused diff when reviewing recent edits
   - screenshots or UI notes summarized in text when reviewing frontend work
   - constraints such as "KISS", "read-only", "do not suggest broad refactors"
5. Do not send secrets, credentials, private customer data, or large unrelated files.
6. Run Claude through the wrapper in print mode with the prompt as the command argument.
7. Wait for the command to complete and use stdout as Claude's answer in the current context.
8. Summarize Claude's agreement, disagreement, and alternative approach ideas. Do not blindly adopt Claude's conclusion.

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

Prefer the user's requested model when provided. Otherwise default to `opus`.

```bash
codex sandbox macos --permissions-profile :danger-full-access --cd "$PWD" claude --print --model opus 'You are giving a second opinion only.
Do not edit files. Do not run commands unless explicitly asked.

Question:
...

Current solution or approach:
...

Context:
...'
```

Keep paths with glob characters quoted before first use. If the prompt would be huge, trim to the relevant snippets or diff before calling Claude. Do not write prompt temp files unless the direct command fails because of shell length or quoting limits.

## Reporting Back

Return a concise synthesis:

- Claude verdict
- Where Claude agrees or disagrees with Codex's direction
- Any concrete issue worth acting on
- Any smaller or more idiomatic alternative worth considering
- Where Claude's answer seems speculative or conflicts with local evidence
- Your recommendation as Codex

If the CLI fails, quote the exact error and continue with the local analysis.
