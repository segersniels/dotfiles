# Deep Review Protocol

Use this protocol for the initial review and every later commit delta. Its purpose is review closure, not quick feedback.

## 1. Establish the change box and evidence brief

Before judging the implementation, inspect every accessible source linked from the PR that can define the intended change. This includes Notion tickets, Slack threads, issue-tracker items, specifications, designs, incident reports, and linked parent or follow-up work. Read enough surrounding context to understand the decision, not only the quoted sentence. Also read the relevant base and HEAD code, tests, and end-to-end product flow to understand the existing contract. Do not follow unrelated links after the change boundary is clear.

Write a compact **change-box scope contract** with:

- The exact problem being fixed and the affected user or system flow.
- The intended observable outcome.
- Explicit acceptance criteria.
- Existing contracts and invariants that the change must preserve.
- Components and behaviors that are necessarily in scope.
- Explicit non-goals and adjacent work that is outside scope.
- Authoritative source links or identifiers for each material requirement.
- Missing, ambiguous, or conflicting product context.

Do not start finding publication decisions until this contract exists. If a required private link cannot be accessed, record what evidence is missing and how it limits the review. Do not infer that an inaccessible ticket or thread demands a broader change.

Record:

- The user or system problem and why it matters.
- Intended behavior and explicit non-goals.
- Acceptance criteria from authoritative sources.
- One concrete end-to-end flow.
- PR claims that still need proof.
- Base SHA and exact HEAD SHA.
- Missing or conflicting context.

Evidence priority is: explicit user direction, authoritative product or technical specification, current production contract and code, tests that prove that contract, PR description, ticket claims, and comments. A lower-priority source can reveal a conflict but cannot silently override a higher-priority decision. A linked Slack discussion or Notion ticket can define intent when it records the product decision; it does not make every adjacent observation in that discussion part of this PR.

Label inferred acceptance criteria. Do not report an inferred criterion as a confirmed product mismatch.

## 2. Build PR anatomy before judging hunks

Account for every changed file. Group files by changed contract, not by directory alone.

For each contract group, record:

`source or writer -> transformations -> persistence or transport -> final consumer`

State the invariant that must remain true across the chain. Associate tests, configuration, migrations, generated artifacts, and operational code with the group they protect.

Map the smallest useful blast radius:

- Callers and callees.
- Readers and writers of changed state.
- Imports, exports, public types, API consumers, queues, jobs, and webhooks.
- Sibling entry points that enforce the same invariant.
- Deployment ordering or compatibility boundaries.

Use dynamic context. Start with the changed hunk, then read its enclosing symbol, direct callers and consumers, shared invariant owners, and relevant siblings. Expand farther only when the current evidence creates a concrete question. Avoid both diff-only review and indiscriminate repository dumps.

## 3. Derive the review plan from this PR

Do not apply one fixed checklist. Generate review dimensions from the brief and anatomy. Common dimensions include:

- Functional correctness and boundary cases.
- State provenance, normalization, identity, ordering, and lifecycle.
- Authentication, authorization, privacy, and untrusted input.
- Persistence, schema, data integrity, migrations, and rollback.
- Concurrency, retries, idempotency, partial failure, cleanup, and recovery.
- Public API, compatibility, versioning, and deployment order.
- Runtime cost, fan-out, unbounded growth, cache behavior, and resource ownership.
- UI interaction, accessibility, navigation, device, and browser behavior.
- Observability, failure reporting, and operational diagnosis.
- Test adequacy and whether tests fail for the intended reason.

For each dimension, name the concrete risk, target files, context files, invariants, and proof needed. Merge overlapping dimensions. Add a dimension only when the PR gives it a real trigger.

## 4. Review changed tests before implementation

Tests reveal intended behavior and blind spots. Check:

- Whether the test recreates the reported producer and end-to-end path.
- Whether it asserts the invariant and observable result.
- Whether it covers the normal case and only the relevant adjacent cases.
- Whether mocks bypass the layer that failed in production.
- Whether the assertion can pass when the central behavior is removed or inverted.
- Whether test names or comments promise more than the assertions prove.

For central or high-risk logic, assess whether the focused test would fail when the essential behavior is absent. Do not edit tracked files in the exact-SHA review worktree to perform a mutation check. Use existing mutation tooling only when it operates in a separate disposable copy with no push path and leaves the review worktree byte-for-byte unchanged.

## 5. Investigate each contract end to end

Compare base and HEAD. Trace the producer to the final consumer. Check history only when it answers intent, compatibility, or provenance.

For bug fixes:

1. Reproduce or reconstruct the exact reported failure.
2. State the violated invariant.
3. Trace the bad state backward through reachable writers.
4. Distinguish prevention, migration, normalization, self-healing, and consumer defense.
5. Prove that the chosen layer owns the fix.
6. Check the nearest sibling cases that share the invariant.

For new behavior:

1. Trace a normal path.
2. Trace a relevant boundary or adversarial path.
3. Trace failure, cancellation, retry, or cleanup when the lifecycle supports it.
4. Verify compatibility with existing consumers and deployment order.

For matching or resolution logic, check zero, one, and multiple matches. Check lossy transformations, exact and fallback intersections, collisions, stale identifiers, ordering changes, and decisions made before later normalization.

For recurring or data-heavy work, estimate:

`frequency x candidates x work per candidate x retry or concurrency factor`

Use realistic present and near-future volume. Do not report theoretical scale risks without a plausible workload.

## 6. Reproduce proportionately

Require the worktree-bootstrap parity gate before executing project code. The dependency install must finish before tests, builds, type checks, application launches, or reproductions. If parity or installation failed, do not use the incomplete environment as evidence of a product defect; record the exact setup error and the resulting blind spot.

Use the strongest safe evidence available:

1. Existing focused tests that exercise the actual path.
2. A focused repository command or existing integration harness.
3. A minimal disposable reproduction in the isolated worktree.
4. A browser, simulator, service, or manual product flow when already available.
5. Static proof through exhaustive control or data-flow tracing when runtime execution is unavailable.

Inspect changes to dependency manifests, lockfiles, install hooks, package scripts, build files, test configuration, and CI automation before executing them. Use a sandbox or container when the PR or author is not trusted. Do not run changed or untrusted code on the host merely because it is in an isolated worktree.

Use the repository's configured package manager and runtime. Do not repair an unavailable environment beyond normal documented setup. Record exact errors and convert material missing runtime evidence into a blind spot.

Never implement a proposed fix during reproduction. A patch suggestion stays textual. If a test, formatter, generator, or setup command changes a tracked file, stop, record the explicit local side effect, restore only that tool-created path to the reviewed SHA, and reverify a clean worktree before continuing.

Run broad gates only when project instructions require them, the changed contract spans them, or focused evidence cannot answer the question.

## 7. Candidate ledger

Record every plausible candidate before disposition:

- Stable internal ID.
- Path and line or symbol.
- Contract and invariant.
- Base behavior.
- HEAD behavior.
- Reachable trigger.
- Concrete impact.
- Introduction or worsening evidence.
- Reproduction or static proof.
- Counterevidence and uncertainty.
- Existing-thread overlap.

Candidate states are `open`, `verified`, `disproved`, `duplicate`, `pre-existing`, or `blind-spot`.

Do not publish an `open` candidate.

## 8. Falsification gate

Try to disprove every material candidate. Ask:

- Is the path reachable with supported inputs and current configuration?
- Does a caller, lower layer, transaction, framework, or platform already enforce safety?
- Is the behavior intentional under the authoritative product contract?
- Did the same practical behavior exist at the base SHA?
- Does the PR materially increase reachability, frequency, or impact?
- Is the claimed impact observable, or does a later transformation remove it?
- Does a focused reproduction fail before the change and succeed because of the change?
- Is another existing thread already reporting the same root cause and trigger?

Drop candidates that fail this gate. Do not move disproved ideas into blind spots.

A blind spot is a material question that remained plausible but could not be verified because required evidence was unavailable. State what evidence is missing and why it matters.

## 9. Mandatory scope gate

Run this gate after technical verification and before severity or publication. Technical validity and PR actionability are separate decisions.

Classify each verified candidate as exactly one of:

- **In-scope regression:** The PR introduced or materially worsened the behavior, and correcting it is necessary to preserve an existing contract or make the stated outcome correct and safe.
- **Acceptance mismatch:** The PR does not meet an explicit authoritative requirement within its stated outcome.
- **Pre-existing unchanged:** The behavior is reachable at the base SHA, is not the condition this PR explicitly promises to correct, and the PR does not materially increase its reachability, frequency, or impact.
- **Scope-expanding opportunity:** The observation asks for adjacent cleanup, redesign, extra product behavior, broader compatibility, or a stronger contract than the PR needs.
- **Scope ambiguous:** The evidence does not establish whether the requested behavior belongs to this PR.

Compare the candidate to the written change-box scope contract, not to a vague sense of code quality. Cite the acceptance criterion, preserved invariant, or PR-introduced regression that makes the requested change necessary. If none applies, the candidate cannot be an inline finding.

Only an in-scope regression or acceptance mismatch can become an inline blocker, concern, or nit.

Do not label the target bug as pre-existing merely because it also reproduces at the base SHA. If the change box says the PR must correct that behavior and the reviewed HEAD does not, classify it as an acceptance mismatch.

For pre-existing unchanged behavior and scope-expanding opportunities:

- Do not request a change in the current PR.
- Do not open an inline finding.
- Record concise base-SHA or contract evidence in the review ledger.
- Put a material item in a separate **Follow-up candidates** summary section with `No change requested in this PR.`
- Do not create a ticket or external task unless the user separately asks.

Surface serious pre-existing security, privacy, data-loss, corruption, or availability risks prominently to the user, but keep the attribution and follow-up boundary explicit.

For scope ambiguity, ask the user only when the answer can materially change the current review. Do not guess a broader contract.

A regression caused by the PR remains in scope even when the smallest correct fix is difficult. Scope discipline must not hide breakage introduced by the implementation.

## 10. Compound and completeness pass

After individual verification, cluster findings by shared state, identity, lifecycle, permission boundary, caller, or consumer. Check whether two locally safe changes combine into one system failure.

Then look for omissions:

- A claimed requirement with no implementation.
- A changed producer with an unchanged consumer assumption.
- One entry point fixed while another shared entry point remains exposed.
- Missing migration, rollback, cleanup, telemetry, or recovery behavior.
- A test that covers the edit but not the product invariant.
- A review-fix commit that resolves one finding and introduces another.

## 11. Severity and reportability

Classify only after verification:

- **Blocker:** credible security, privacy, data-loss, corruption, availability, or core-functional failure that should prevent merge.
- **Concern:** reachable correctness, reliability, compatibility, performance, or maintainability defect with concrete impact.
- **Nit:** small, concrete improvement with low impact and no speculative redesign.
- **Blind spot:** material unverified coverage gap, not a proven defect.
- **Pre-existing:** relevant risk present at the base and not materially worsened by the PR.

Severity is based on impact and reachability, not reviewer confidence. State uncertainty separately.

A publishable blocker, concern, or nit requires:

- Exact reviewed-HEAD location.
- Reachable trigger.
- Concrete impact.
- Evidence that the PR introduced or materially worsened it.
- Verification against repository and product assumptions.
- Novelty relative to existing threads.
- An `in-scope regression` or `acceptance mismatch` result from the mandatory scope gate.

## 12. Review closure gate

Do not declare the review complete until:

- Every changed file has a recorded coverage result.
- The change-box scope contract is complete enough to judge publication, or the missing context is an explicit blind spot.
- Every meaningful changed contract has a source-to-consumer trace and invariant.
- Every triggered review dimension is complete or named as a blind spot.
- Every candidate has a final disposition.
- Every verified candidate has a recorded scope-gate classification.
- Cross-contract and omission passes are complete.
- Existing findings are reconciled with the exact HEAD.
- Focused verification is recorded with results.
- The live remote HEAD still equals the reviewed HEAD.

If the HEAD changes during closure, review the delta, revisit affected coverage, and repeat the gate. Elapsed time is never a substitute for this evidence.
