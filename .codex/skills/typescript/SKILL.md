---
name: typescript
description: TypeScript best practices and patterns
---

- Use `knip` to remove unused code if making large changes
- When adding comments to js, ts, or tsx files — remember to use JSDoc when writing multiline comments.
- Refrain from using `for (let i = 0; i < array.length; i++) {` statements. Use `for (const item of array) {` instead.
- Use early returns and continue statements whenever possible.
- Try to always have an empty line above return statements (unless it's a single line return statement).
- When adding interfaces, enums, or other types, always use PascalCase for the naming. The enum values should be in UPPER_CASE.
- ALWAYS use braces for if statements - no single-line `if (x) return` statements
- Don't unnecessarily add `try`/`catch`
- Don't case to `any` unless absolutely necessary