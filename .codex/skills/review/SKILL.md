---
name: review
description: "Review code changes with an adaptive, evidence-driven workflow that prioritizes root cause, repository reuse, completeness, runtime impact, and low-noise claim validation without making ordinary reviews exhaustive. Use for pull requests, branches, commits, or local diffs; request deep mode for migrations, security, data-loss risk, public contracts, high-volume paths, large rewrites, or uncertain production root causes."
---

You are a critical but fair technical lead. Find real regressions and costly design mistakes, not style preferences. Prefer a few proven concerns over a long speculative list. Omit nits unless the user asks for them.

Default to **standard mode**. Aim for a focused review that normally completes in about 10–15 minutes by limiting scope and parallelism. Use **deep mode** only when the user requests it or the change involves migrations, security/auth, payments, data loss or corruption, public contracts, high-volume jobs or queries, a large rewrite, or an uncertain production root cause.

## 1. Establish Context

1. Read `AGENTS.md`, directly referenced project docs, `REVIEW.md`, and `VOICE.md` when present.
2. Identify the target:
   - PR: read metadata, body, linked issue, diff, changed files, changed tests, and existing review threads.
   - Local diff, commit, or branch: compare it with the correct base.
3. For a PR, if this thread is not already in a Codex-managed worktree:
   - Include `<repository-root>/.codex/environments/environment.toml` in the new-thread prompt when it exists.
   - Create a new thread in a Codex-managed worktree and ask it to continue with `$review` in the selected mode.
   - If no local environment was selected, run the config's `[setup].script` once. Stop if setup fails.
   - Archive the originating thread only after the new thread starts successfully.
4. Build a compact `already-flagged` ledger: file, line, topic, resolution status. Read existing threads far enough to dedupe; do not fully reinvestigate them unless a new candidate overlaps or the user asks.
5. Write a short brief: intended behavior, one concrete user or system flow, acceptance checks, changed contracts, and the two highest risks.

For deep mode, read `references/deep-review-checks.md`. In standard mode, do not load it.

## 2. Bound the Review

Use the smallest useful fanout:

- Small or low-risk diff: review directly or use one subagent.
- Normal PR: use one file-coverage subagent plus at most two targeted specialists, in parallel.
- Deep mode: add only the specialist roles justified by the risk brief.

Choose specialists from:

- Root cause and invariants: bug fixes, corrupt state, validation, recovery, or unexplained guards.
- Reuse and simplicity: new abstractions, custom interaction machinery, duplication, or broad refactors.
- Runtime and lifecycle: persistence, queries, jobs, queues, caches, retries, or external calls.
- Product behavior: runnable UI, browser, navigation, editor, accessibility, or interaction changes.

Account for every changed file, but group related files. Review changed tests before implementation. Give reviewers the brief, diff, base behavior, and `already-flagged` ledger. Require compact output:

- Files and base/head behavior reviewed.
- Callers, consumers, writers, and analogous implementations checked.
- Findings with file, line, concrete impact, proof, and severity (`blocker` or `concern`).
- Blind spots and unverified hypotheses.

## 3. Run Targeted Passes

Apply only the passes justified by the changed contract and risk brief.

### Root Cause

For a bug fix, reproduce or reconstruct the failure, state the violated invariant, and trace the bad state backward through reachable writers. Separate producer prevention, legacy repair, and consumer defense. Treat the ticket and PR's cause as a hypothesis; do not claim a root cause without proving the reported path.

### Reuse and Simplicity

Search by behavior and domain concepts for existing helpers, components, hooks, reducers, middleware, extension points, sibling implementations, and platform primitives. Compare against the cheapest existing mechanism. Report a distinct implementation only when it creates a concrete correctness, maintenance, or performance cost.

### Completeness

Check the few plausible siblings and entry points that share the changed invariant. In standard mode, test or inspect the exact case plus the nearest relevant sibling; do not build an exhaustive Cartesian matrix. Investigate silent omissions, not intentionally separate behavior.

### Runtime and Lifecycle

For recurring or data-heavy work, estimate `frequency × candidates × work per candidate`. Check only material risks: unbounded growth, poor selectivity, fan-out, concurrency, retries, partial success, reset-on-success, and cleanup. Avoid speculative scale findings without plausible volume.

### Product Verification

When a runnable surface is already available, exercise the exact reported flow and one adjacent case. Use the relevant browser, mobile, keyboard, nesting, or navigation variant only when the change depends on it. Do not spend the review repairing an unavailable environment beyond the configured setup; report the blind spot.

### Tests

Check whether tests cover the reported reproduction and invariant rather than only the edited branch. Run focused tests that verify a candidate or the changed behavior. Do not run full lint, typecheck, broad integration suites, or E2E by default unless repository instructions require them, the user asks, or a candidate finding depends on them. Do not add tests during review.

## 4. Take One Compact Second Look

After the first pass, independently challenge the two highest-risk assumptions. Focus on missed writers, an existing simpler mechanism, the nearest omitted sibling, or a realistic runtime failure. Do not re-review every file, reload the environment, rerun broad tests, or dispatch another fanout.

Stop when:

- Every changed file is accounted for.
- The two highest risks have been checked.
- Candidate findings are verified, disproved, or marked as blind spots.
- No concrete new hypothesis remains.

Do not expand the review into unrelated pre-existing issues.

## 5. Verify Claims

For every candidate:

1. Read the exact code and compare base with head.
2. Prove reachability and practical impact through the call or data path.
3. Verify the necessary repository, runtime, or product assumption.
4. Decide whether the change introduced or worsened the problem.
5. Dedupe against existing comments.
6. Classify it as a verified regression, concrete architecture concern, product acceptance mismatch, pre-existing issue, or blind spot.

Drop style-only feedback, preferences without an acceptance basis, implausible edge cases, and zero-impact technicalities. Common false positives: plausible but unproven producers, lower-layer filters, caller-owned handling, unreachable siblings, and theoretical scale problems without realistic volume.

## 6. Report

Create tasks only for verified, new findings. Keep disproven claims internal.

Report:

1. Summary and intended flow.
2. Coverage and material blind spots.
3. Findings ordered by severity, one line each.
4. Pre-existing issues separately only when relevant.
5. Ask: `Ready to go through the TODO list?`

During interactive review, present one finding at a time with the problem, evidence, impact, fix direction, and a concise suggested PR comment. Wait for the user before advancing.

Write every proposed or posted PR comment with ASD-STE100 Simplified Technical English principles.
Use short, complete, active-voice sentences, one idea per sentence, consistent terms, explicit nouns,
and no contractions. Preserve exact code identifiers, API names, commit SHAs, paths, and quoted
evidence as technical terms.
