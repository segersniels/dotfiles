---
name: add-comments
description: "Add, remove, or move code comments in requested code. Use when the user asks for comments, better comments, comment placement, why-comments, JSDoc, or comments that make code easier to review."
---

# Comment

Add, remove, or move comments using the original Human Code comment guidance.

## Comments

- Comments should help a reviewer scan the code and understand the product-level flow without fully diving into the implementation.
- Prefer high-level product intent over low-level mechanics.
- Comment why a guard exits or why a branch exists.
- Put comments that explain an `if` branch directly above the `if`; for `if`/`else`, put branch-specific comments inside the relevant block.
- Use `//` for single-line comments.
- Use JSDoc for multi-line comments or function explanations.
