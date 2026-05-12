---
name: "Keep it simple, stupid"
description: "KISS: keep the work simple and tightly scoped. Use when the user asks for a minimal fix, small diff, no feature creep, no extra refactors, or the simplest change that solves the task."
---

KISS: keep it simple. Stay on the task. Prefer the smallest change that fully solves the user's request.

## When to use

Use this skill when the user says or implies:
- keep it simple
- KISS
- minimal change
- small diff
- no scope creep
- no extra refactor
- just fix the issue
- focus on the task at hand

## Default stance

- Solve the stated problem first
- Prefer the fewest files and lines that can fix it cleanly
- Fix root cause, not symptoms
- Preserve existing patterns unless they block the fix
- Avoid speculative improvements

## Guardrails

Do:
- make the narrowest reasonable assumption
- reuse existing helpers and patterns
- keep interfaces stable unless a change is required
- stop once the requested outcome is achieved

Do not:
- add features the user did not ask for
- rename, reorganize, or refactor unrelated code
- introduce new abstractions unless duplication or complexity makes them necessary for this task
- expand into cleanup work just because you noticed it
- add tests, docs, or tooling changes unless they are clearly needed or the user asked for them

## Workflow

1. Restate the exact task in one sentence internally
2. Identify the smallest change that can solve it
3. Touch as little code as possible
4. Verify the targeted behavior
5. Report only the relevant change and any remaining constraint

## Decision rule

If two approaches both work, choose the one with:
- less code
- less surface area
- less behavioral risk
- less future maintenance cost

Only take the larger approach when the smaller one would be fragile, incorrect, or fail to fully solve the task.
