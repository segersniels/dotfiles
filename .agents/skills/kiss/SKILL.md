---
name: kiss
description: Keep implementation or review tightly scoped when the user asks for KISS, a minimal fix, or no extra refactoring.
---

Prefer the smallest clear, complete solution to the user's request.

- Fix the root cause and reuse existing helpers, ownership boundaries, and conventions.
- Keep unrelated behavior and interfaces stable. Avoid speculative features, cleanup, and abstractions.
- Judge simplicity by clarity, behavioral risk, and maintenance cost. Fewer lines or files are useful only when they improve those qualities.
- Choose a larger change when the smaller one would be fragile, obscure, incorrect, or incomplete.
- Add tests, docs, or tooling only when they materially support the requested outcome or satisfy project requirements.

Apply this as an assessment criterion during review and as an implementation constraint during authorized edits. Verify the affected behavior and complete the full request, including any authorized delivery steps. Stop when that outcome is achieved.
