---
name: human-code
description: "Use for readability and reviewability improvements to existing logic: code flow, naming, guard clauses, local structure, and making code read naturally. Use when the user asks for human code, readable code, proper code, reviewable code, or making code flow nicely. Keep the existing behavior intact. Do not use for comment-only work; use the comment skill for requested code comments."
---

# Human Code

Make code read like a careful human wrote it. Focus on how the logic is expressed, not what the logic does.

## Default stance

- Prefer edits that improve scan speed: naming, spacing, and local control-flow layout.
- Keep the existing behavior intact.
- Avoid broad rewrites and speculative cleanup.
- If you notice a behavior issue, call it out separately instead of folding it into readability work.
- Always lint and typecheck after each change.
- Stop once the code flows clearly.

## Good edits

- Rename variables, helpers, and local concepts for clarity.
- Reorder local setup so the flow reads top-to-bottom without changing execution.
- Extract one focused helper when it makes the existing flow easier to read.
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
