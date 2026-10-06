# Comments

Comments help a reviewer scan the code and understand the product-level flow without reading every line. When a rule here conflicts with the repository's own conventions, follow the repository.

- Comment only what the code cannot say: why a guard exits, why a branch exists, or a non-obvious constraint. Describe product intent, not mechanics.
- Do not restate what the code does. Do not add comments to code you did not change.
- Put a comment that explains an `if` directly above it. For `if`/`else`, put branch-specific comments inside each block.
- In JS/TS, use `//` for one line and JSDoc for multi-line or function-level explanations.
- Write comments as short, complete, active-voice sentences in plain American English. Do not use contractions.
