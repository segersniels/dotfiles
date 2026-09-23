---
name: human-code
description: Assess or improve code readability when the user asks for human-code, clearer naming, or easier-to-follow logic.
---

Make the intended behavior easy to understand from the code.

## Scope

For a readability-only request, preserve behavior and report unrelated bugs separately. When the user also requests a fix or feature, apply these principles to that implementation and preserve behavior outside the requested change. For an assessment, report findings without editing.

This skill governs how code is expressed; it does not cancel other authorized work. Use the comment skill for comment-only requests.

## Readability

- Use names that state the domain rule and make the flow easy to scan.
- Keep the happy path clear. Prefer guard clauses and early returns when they reduce nesting.
- Replace complicated nested ternaries with straightforward control flow.
- Extract a focused helper only when it makes the flow easier to understand. Keep simple logic local.
- Use spacing, temporary names, and optional chaining when they clarify the code without hiding execution order or changing semantics.
- Follow existing conventions and avoid unrelated rewrites.

After a coherent set of edits, run applicable project checks and verify the affected behavior. Complete the user's full request once the code reads clearly.
