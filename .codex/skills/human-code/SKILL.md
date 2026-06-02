---
name: human-code
description: "Use for readability and reviewability improvements to existing logic: code flow, naming, comments, spacing, guard clauses, and making code read naturally. Use when the user asks for human code, readable code, proper code, reviewable code, or making code flow nicely. Keep the existing behavior intact."
---

# Human Code

Make code read like a careful human wrote it. Focus on how the logic is expressed, not what the logic does.

## Default stance

- Prefer edits that improve scan speed: naming, comments, spacing, and local control-flow layout.
- Keep the existing behavior intact.
- Avoid broad rewrites and speculative cleanup.
- If you notice a behavior issue, call it out separately instead of folding it into readability work.
- Always lint and typecheck after each change.
- Stop once the code flows clearly.

## Good edits

- Rename variables, helpers, and local concepts for clarity.
- Reorder local setup so the flow reads top-to-bottom without changing execution.
- Extract one focused helper when it makes the existing flow easier to read.
- Add, remove, or move comments so they explain the natural flow of higher-level logic and non-obvious branches.
- Apply spacing rules that make control flow visually clear.

## Implementation shape

- Keep control flow visually separated from business logic.
- Use one focused helper when inline logic is hard to read.
- Prefer guard clauses and early returns for rejected cases.
- Keep the happy path obvious.
- Rewrite complicated nested ternaries as clear, flowing `if` statements.
- Use optional chaining for simple nullable property access when it preserves behavior and removes boilerplate.
- Use temporary names when they make existing logic easier to read; avoid adding names that obscure the flow.
- Prefer names that make the rule readable at scan speed.

## Spacing

- Add an empty line before early exits and control-transfer statements when preceded by other logic in the same block: `return`, `throw`, `break`, `continue`.
- Do not separate a control-transfer statement from its own opening control statement.
- Add an empty line after logical block statements when more code follows: `if`, `else`, `for`, `while`, `do`, `switch`, `try`, `catch`, `finally`.
- Add an empty line between `switch` cases, including before `default`.
- Keep one-line setup attached to the following control flow.
- Add a blank line between any multi-line statement and the next logical block.

## Comments

- Comments should help a reviewer follow the higher-level flow and intent of the code.
- Comment why a guard exits or why a branch exists.
- Do not comment obvious happy-path returns.
- Use `//` for single-line comments.
- Use JSDoc for multi-line comments or function explanations.
- Keep broad rationale in the PR, commit message, or final explanation instead of inline code.

## Mechanical lint

For JavaScript and TypeScript codebases, run the bundled oxlint style check after human-code edits when `oxlint` is available. Skip it for non-JS/TS codebases such as Go, Rust, and C#.

```sh
files=()
while IFS= read -r -d '' file; do [[ "$file" =~ \.(c|m)?(j|t)sx?$ ]] && files+=("$file"); done < <(git diff --name-only -z --diff-filter=ACMR)
(( ${#files[@]} )) && oxlint -c "$HOME/.codex/skills/human-code/assets/oxlint.config.json" --no-error-on-unmatched-pattern "${files[@]}"
```

This is additive to project linting, formatting, typechecking, and tests. Do not install `oxlint` or use autofix flags unless asked. When cleaning current edits only, act only on diagnostics that overlap changed hunks.
