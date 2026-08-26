---
name: orchestrate
description: "Implement an already-understood plan by coordinating focused, non-overlapping Sol Low workers while the current agent owns plan fidelity, KISS, Human Code, integration, and final verification. Use only when the user explicitly asks to orchestrate or delegate an implementation after investigation."
---

# Orchestrate

Continue from the current thread's investigation and chosen KISS implementation. The current agent is the orchestrator. It owns the plan, decomposition, worker guidance, integration, code quality, and final result.

Do not use the fleet to repeat the investigation or outsource architectural judgment. If the implementation direction is not yet clear, investigate first. If repository evidence invalidates the agreed direction or requires a materially larger scope, stop and explain the conflict to the user.

## Freeze the implementation brief

Before spawning workers, turn the current understanding into a compact brief:

- intended outcome and root cause;
- chosen smallest correct implementation;
- behavior allowed to change and invariants to preserve;
- explicit non-goals;
- acceptance and verification checks.

Workers use `fork_turns=none`, so every worker prompt must be self-contained. Do not assume a worker received the current conversation.

## Divide ownership

Split the plan into the smallest useful set of independent contracts or tightly coupled file groups. Spawn parallel workers only for slices that can be edited without overlap.

- Give each file, module, or contract one owner.
- Keep shared integration files and cross-cutting decisions with the orchestrator.
- Keep coupled work in one lane or sequence it instead of forcing parallel work.
- Do not fill every available slot unless the plan has that many independent slices.
- Do not assign the same implementation to multiple workers.

If the plan cannot be divided safely, use one worker for a coherent slice or implement it in the orchestrator. State why a larger fleet would create interference.

## Spawn workers

Spawn each implementation agent with:

- Agent type: `worker`.
- Model: `gpt-5.6-sol`.
- Reasoning effort: `low`.
- Context: `fork_turns=none`.
- Nested delegation: forbidden.

Always set the model and reasoning effort explicitly. Do not silently inherit the orchestrator's settings. If model overrides or delegation are unavailable, continue in the orchestrator and report the limitation.

Every worker prompt must include:

- the relevant implementation brief;
- exact ownership by files, module, or contract;
- the required behavior and acceptance criteria;
- relevant existing patterns and constraints;
- focused verification to run;
- explicit non-goals;
- instruction not to commit or push unless the user already authorized it;
- instruction not to edit outside ownership, revert concurrent work, or perform unrelated cleanup;
- instruction to report instead of expanding scope when another ownership area is required.

Tell every worker it is not alone in the worktree. It must preserve unrelated edits and adapt its slice to compatible concurrent changes.

## Oversee the fleet

Remain productive while workers run. Inspect integration seams and shared contracts, review emerging changes when useful, and process results as they arrive. Do not edit a worker's owned files while it is active.

Workers should message the orchestrator when:

- repository evidence conflicts with the brief;
- completion requires files outside their ownership;
- another lane changes a required contract;
- focused verification reveals a cross-lane problem;
- the smallest correct implementation is materially different from the assignment.

Steer an active worker with a concise message when it drifts. Interrupt it when the lane is clearly wrong or unsafe. Do not let one stalled worker block unrelated progress indefinitely.

## Review and correct

A worker's completion message is not acceptance. Inspect every owned diff and verify, in order:

1. It implements the agreed behavior and preserves the stated invariants.
2. It stays inside its ownership and non-goals.
3. It remains the smallest correct root-cause solution and follows existing patterns.
4. It reads like careful Human Code.
5. Its focused verification is relevant and passes.

For the Human Code review, read and apply [Human Code](../human-code/SKILL.md). Apply it to how the intended behavior is expressed; do not use it to justify unrelated refactors or semantic changes. Favor clear names, obvious control flow, useful guard clauses, limited nesting, and focused helpers only when they improve scan speed.

Send corrections back to the worker that owns the slice. State:

- the expected contract;
- the concrete mismatch;
- the smallest requested correction;
- why it is needed for behavior, KISS, or readability.

Keep ownership stable through correction rounds. Use another worker only when the original owner is unavailable or the work has become a genuinely separate contract. The orchestrator may make a tiny integration correction itself after the owner is finished, but it must still review and verify that change.

## Integrate and verify

Wait for every required lane to finish or explicitly resolve its failure. Then:

- review the complete diff for overlap, omissions, and accidental scope expansion;
- verify cross-lane contracts and the original acceptance criteria;
- run the repository's required lint, typecheck, and applicable tests;
- follow repository instructions about whether new tests require approval;
- confirm no active worker remains on the implementation;
- report the implemented slices, verification, and any remaining constraint.

Do not claim completion from worker reports alone. The orchestrator owns the final judgment that the integrated implementation matches the original plan, stays KISS, and is Human Code.
