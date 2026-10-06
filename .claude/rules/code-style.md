# Code style

The user reads and reviews every diff by hand. Optimize for a small change that a reviewer understands on first read. When a rule here conflicts with the repository's own conventions, follow the repository.

## Scope

- Make the smallest complete change that fixes the root cause of the request.
- Do not add features, configuration, refactors, or cleanup that the task does not need. Mention a worthwhile follow-up in one line instead.
- Before you write a new helper, search the codebase for one that already does the job: utilities, hooks, types, constants, and installed dependencies. Use it when it fits the task. Do not copy its logic into a second version.
- When an existing utility almost fits, prefer a small change to it only if that change stays within the task. If not, mention the gap and use the closest existing option.
- Do not add error handling, fallbacks, or validation for cases that cannot happen. Validate only at system boundaries.
- Do not create a helper, abstraction, or file for one-time use. Do not design for future requirements that nobody asked for.
- Choose a larger change only when the smaller one is fragile, obscure, or incorrect.

## Readability

- Use names that state the domain meaning, not the type or mechanics.
- Keep the happy path at the lowest indent. Use guard clauses and early returns to reduce nesting.
- Replace nested ternaries with plain control flow.
- Keep simple logic inline. Extract a function only when it makes the caller easier to read.
