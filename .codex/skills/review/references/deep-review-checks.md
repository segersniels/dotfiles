# Deep Review Checks

Use this for PR-wide reviews, risky diffs, rewrites, broad refactors, or when subtle regressions matter.

## Required Passes

- Intent: turn PR claims, linked issues, tests, and visible copy into acceptance checks.
- Coverage: account for every changed file; list skipped files with reasons.
- Regression: compare base/head behavior for conditions, defaults, deleted branches, side effects, loading/error states, data shape, and whole-state replacement paths.
- Call graph: trace direct callers, consumers, background jobs, API boundaries, UI entrypoints, hooks, and tests.
- Data: check persistence, migrations, serialization, nullability, pagination, ordering, retries, idempotency, and rollback/restore paths.
- Runtime: check env/config, cache invalidation, rate limits, async queues, platform limits, streaming/buffering, and dependency assumptions.
- User surface: check authz, permissions, i18n runtime loading, a11y, empty states, error copy, and feature flags.
- Tests: verify changed behavior has meaningful tests or clearly report the gap.
- Evidence: report only verified findings; keep non-issues internal, but surface blind spots.

## Subagent Prompt Add-on

Return this shape:

- Files reviewed
- Base/head behavior compared
- Callers/consumers traced
- Tests/config/docs read
- Regression passes checked
- Findings
- Blind spots

If you cannot prove a claim from code, mark it as a blind spot instead of a finding.
