# Deep Review Checks

Read this file only in deep mode. Use only the sections justified by the review brief; do not run every checklist mechanically.

## Root Cause and State Provenance

- Reproduce the reported case or preserve the exact production evidence.
- State the invariant before judging the fix.
- Find all writers, converters, importers, duplicators, deserializers, migrations, and public inputs.
- Trace the reported bad state through a reachable producer; do not substitute a manufactured equivalent state.
- Distinguish prevention, normalization, migration, self-healing, and defensive consumption.
- Check whether a validation function mutates, rejects, or merely observes data.
- Challenge unexplained allowlists, sanitizers, guards, and special cases with history when useful.

## Reuse and Complexity

- Search for domain terms, behavior, UI copy, data fields, event names, and analogous tests.
- Inspect sibling packages and surfaces, not only the changed directory.
- Check shared components, primitives, extension points, middleware, reducers, hooks, and utilities.
- Check whether the browser, framework, database, standard library, or platform already supplies the behavior.
- Compare lines, states, and compatibility obligations introduced by the custom design.
- Ask whether work can happen once at the source instead of through polling or reconciliation.
- Prefer a local proven mechanism over a new shared abstraction unless multiple real consumers justify it.

## Completeness Matrix

Build the smallest relevant matrix:

| Dimension | Examples |
| --- | --- |
| Family | types, providers, integrations, block/input kinds |
| Entry point | UI, API, worker, job, webhook, import/export, public client |
| State | create, update, delete, retry, recover, clean up |
| Shape | empty, partial, nested, stale, legacy, malformed |
| Platform | browser, mobile, keyboard, pointer, locale, assistive tech |
| Permission | owner, member, anonymous, expired, revoked |

Mark each cell checked, intentionally excluded, unreachable, or untested.

## Runtime Cost Model

- Record schedule or request frequency and possible concurrency.
- Estimate candidate rows or objects now and after sustained growth.
- Inspect query plans or index structure when practical; otherwise state the blind spot.
- Check predicate selectivity, expressions over columns, ordering, pagination, and full-scan risk.
- Count downstream queries, renders, network calls, or queue jobs per candidate.
- Check locks, leases, timeouts, renewal, retries, partial success, and idempotency.
- Check whether failure markers reset on recovery and whether retained state has a bound.
- Check cache invalidation, cleanup, deletion, archival, rollback, and replay.
- Avoid reporting hypothetical scale concerns without plausible volume and frequency.

## Product and Interaction Verification

- Start with the exact ticket URL, data, sequence, and role when available.
- Test the expected path, nearest sibling, and one adversarial path.
- For interaction changes, check focus, selection, keyboard navigation, Escape, outside click, loading, cancellation, and repeated use.
- For navigation changes, check nested routes, deleted resources, stale URLs, back/forward, and refresh.
- For responsive UI, check at least one desktop and mobile viewport when feasible.
- For browser-specific fixes, verify the reported browser and a control browser.
- Compare visible copy, timing, layout, and affordances with an existing analogous surface.
- Separate acceptance mismatches from subjective preferences.

## Regression Test Quality

- Recreate the reported failure, not only an equivalent object assembled after the producer.
- Assert the invariant and user-visible or system-visible result.
- Retain a normal case proving supported behavior still works.
- Add adjacent negative, sibling, and entry-point cases when they share the changed invariant.
- For lifecycle logic, cover failure, partial success, retry, recovery, and cleanup.
- Assert that the original error, telemetry signal, duplicate side effect, or invalid persistence no longer occurs.

## Evidence Standard

A reportable finding needs:

- Exact file and line in the reviewed head.
- Reachable trigger or realistic runtime scenario.
- Concrete impact.
- Evidence that the change introduced or worsened it.
- Novelty relative to existing review threads.

If any element is missing, investigate further or report a blind spot instead.
