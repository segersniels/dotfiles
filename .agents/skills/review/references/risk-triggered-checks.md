# Risk-Triggered Review Checks

Use only the sections justified by the review brief and changed contracts. Do not run every checklist mechanically.

## Root Cause and State Provenance

- Reproduce the reported case or preserve the exact production evidence.
- State the invariant before judging the fix.
- Find relevant writers, converters, importers, duplicators, deserializers, migrations, and public inputs.
- Trace the reported bad state through a reachable producer; do not substitute a manufactured equivalent state.
- Distinguish prevention, normalization, migration, self-healing, and defensive consumption.
- Check whether validation mutates, rejects, resolves, or only observes data.
- Challenge unexplained allowlists, sanitizers, guards, and special cases with history when useful.

## Normalization and Resolution

- Record which state each validation or resolution decision observes.
- Trace later changes to position, identity, scope, ownership, ordering, or shape.
- Re-evaluate earlier eligibility and resolution decisions against the final normalized state.
- For names, prefixes, truncation, translation, coercion, or fallback matching, check zero, one, and multiple candidates.
- Check exact matches that also intersect a fallback set.
- Check two distinct source values that become identical after a lossy transformation.
- Prefer ambiguity or no match over silently binding to the wrong object when the contract permits it.

## Reuse and Complexity

- Search for domain terms, behavior, UI copy, data fields, event names, and analogous tests.
- Inspect relevant sibling packages and surfaces, not only the changed directory.
- Check shared components, primitives, extension points, middleware, reducers, hooks, and utilities.
- Check whether the browser, framework, database, standard library, or platform already supplies the behavior.
- Compare the states and compatibility obligations introduced by a custom design.
- Ask whether work can happen once at the source instead of through polling or reconciliation.
- Prefer a local proven mechanism over a new shared abstraction unless multiple real consumers justify it.

## Completeness Matrix

Build the smallest relevant matrix only when two or more dimensions can interact with the changed invariant:

| Dimension | Examples |
| --- | --- |
| Family | types, providers, integrations, block/input kinds |
| Entry point | UI, API, worker, job, webhook, import/export, public client |
| State | create, update, delete, retry, recover, clean up |
| Shape | empty, partial, nested, stale, legacy, malformed |
| Platform | browser, mobile, keyboard, pointer, locale, assistive tech |
| Permission | owner, member, anonymous, expired, revoked |

Mark each relevant cell checked, intentionally excluded, unreachable, or untested. Do not build a full Cartesian matrix when dimensions do not interact with the changed invariant.

## Runtime Cost Model

- Record schedule or request frequency and possible concurrency.
- Estimate candidate rows or objects now and after sustained growth.
- Inspect query plans or index structure when practical; otherwise state the blind spot.
- Check predicate selectivity, expressions over columns, ordering, pagination, and full-scan risk.
- Count downstream queries, renders, network calls, or queue jobs per candidate.
- Check locks, leases, timeouts, renewal, retries, partial success, and idempotency.
- Check whether failure markers reset on recovery and whether retained state has a bound.
- Check cache invalidation, cleanup, deletion, archival, rollback, and replay.
- Avoid hypothetical scale concerns without plausible volume and frequency.

## Product and Interaction Verification

- Start with the exact ticket URL, data, sequence, and role when available.
- Test the expected path, nearest sibling, and one adversarial path justified by the contract.
- For interaction changes, check relevant focus, selection, keyboard navigation, Escape, outside click, loading, cancellation, and repeated use.
- For navigation changes, check relevant nested routes, deleted resources, stale URLs, back/forward, and refresh.
- For responsive UI, check desktop and mobile only when layout behavior changed.
- For browser-specific fixes, verify the reported browser and a control browser.
- Compare visible copy, timing, layout, and affordances with an existing analogous surface.
- Separate acceptance mismatches from subjective preferences.

## Regression Test Quality

- Recreate the reported failure, not only an equivalent object assembled after the producer.
- Assert the invariant and user-visible or system-visible result.
- Retain a normal case proving supported behavior still works.
- Cover adjacent negative, sibling, and entry-point cases only when they share the invariant.
- For lifecycle logic, cover the relevant failure, partial success, retry, recovery, and cleanup states.
- Assert that the original error, telemetry signal, duplicate side effect, or invalid persistence no longer occurs.
- For central high-risk behavior, remove or invert one essential implementation step in an isolated disposable worktree and require the focused test to fail.
- Mutate independent responsibilities separately when one test suite claims to protect each responsibility.

## Review-Fix Deltas

- Record the last reviewed SHA and the current HEAD.
- Review the intervening diff as new code, even when every commit claims to address feedback.
- Re-run the exact prior finding at the current HEAD.
- Check whether the fix moved behavior across layers or changed ordering, identity, scope, or normalization.
- Do not reuse a clean verdict from the prior SHA.

## Evidence Standard

A reportable finding needs:

- Exact file and line in the reviewed HEAD.
- Reachable trigger or realistic runtime scenario.
- Concrete impact.
- Evidence that the change introduced or materially worsened it.
- Novelty relative to existing review threads.

If any element is missing, investigate further or report a blind spot instead.
