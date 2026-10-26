# Comments

Comments help a reviewer scan the code and understand the product-level flow without reading every line. When a rule here conflicts with the repository's own conventions, follow the repository.

- Comment only what the code cannot say: why a guard exits, why a branch exists, or a non-obvious constraint. Describe product intent, not mechanics.
- Do not restate what the code does. Do not add comments to code you did not change.
- Put a comment that explains an `if` directly above it. For `if`/`else`, put branch-specific comments inside each block.
- Put one blank line above a comment, unless the comment is the first line of its block. A comment starts a new section, so do not attach it to the code above it.
- In JS/TS, always use JSDoc above a function, method, class, type, or module-level constant (such as `MAX_RETRIES`, exported or not), even for one line, so editors show it on hover wherever it is used. Use `//` only for one-line comments inside a function body. Use JSDoc for any multi-line comment. Start a function's JSDoc with a verb that states what the function does, such as "Checks whether…" or "Builds…". Do not describe only the return value, such as "True for…" or "Returns true when…".
- Write comments as short, complete, active-voice sentences in plain American English. Do not use contractions.
