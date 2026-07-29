# CI / Review Heuristics

## CI classification checklist

Treat as **branch-related** when logs clearly indicate a regression caused by the PR branch:

- Compile/typecheck/lint failures in files or modules touched by the branch
- Deterministic unit/integration test failures in changed areas
- Snapshot output changes caused by UI/text changes in the branch
- Static analysis violations introduced by the latest push
- Build script/config changes in the PR causing a deterministic failure

Treat as **likely flaky or unrelated** when evidence points to transient or external issues:

- DNS/network/registry timeout errors while fetching dependencies
- Runner image provisioning or startup failures
- GitHub Actions infrastructure/service outages
- Cloud/service rate limits or transient API outages
- Non-deterministic failures in unrelated integration tests with known flake patterns

Do not patch likely flaky/unrelated failures. Use the retry budget for rerunnable failures, wait for pending jobs, or stop and report the blocker when the failure is persistent or infrastructure-owned.

If uncertain, inspect failed logs once before choosing rerun.

## Decision tree (fix vs rerun vs stop)

1. If PR is merged/closed: stop.
2. If there are failed checks:
   - Diagnose first.
   - If checks are still pending but an individual job has already failed: fetch that job's logs and diagnose now.
   - If branch-related: fix locally, validate, create an atomic conventional commit with the create-commit skill, and push.
   - If likely flaky/unrelated and all checks for the current SHA are terminal: rerun failed jobs.
   - If likely flaky/unrelated and not safely rerunnable: stop and report the blocker; do not edit unrelated tests, build scripts, CI configuration, dependency pins, or infrastructure code.
   - If checks are still pending and no failed job is available yet: wait.
3. If flaky reruns for the same SHA reach the configured limit (default 3): stop and report persistent failure.
4. Independently, process any new human review comments.

## Review comment agreement criteria

Before deciding whether to change code for any reported issue:

1. Compare the relevant behavior at the PR merge base and PR head.
2. Determine whether the PR introduced it or materially increased its reachability, frequency, or impact.
3. Trace whether it is reachable through supported production behavior and whether its preconditions are plausible or deliberately controllable.
4. Check whether callers, validation, permissions, or lower layers already prevent the claimed impact.
5. Weigh likelihood and blast radius against the complexity and regression risk of the proposed fix.

Classify the issue as:

- **Practical PR regression:** introduced or materially worsened by the PR and plausibly affects real usage. Address it.
- **Rare but material PR regression:** low-frequency or unusual, but deliberately triggerable or credibly risks security, privacy, data loss, or corruption. Address it.
- **Pre-existing issue:** present at the merge base and not materially worsened by the PR. Do not auto-fix it. Reply with concrete base/head evidence when an inline thread exists. Surface a material risk to the user for separate handling.
- **Theoretical or negligible:** requires unrealistic preconditions or has no meaningful impact. Do not change code; give an evidence-backed no-change reply when an inline thread exists.

Touching nearby code does not make a pre-existing issue part of the PR.

Address the comment when:

- The comment is technically correct.
- The issue is a practical or rare-but-material regression caused or materially worsened by the current PR.
- The change is actionable in the current branch.
- The requested change does not conflict with the user’s intent or recent guidance.
- The change can be made safely without unrelated refactors.

Fix valid review feedback in code when possible. Handle independent issues in separate atomic commits. After pushing, reply in every originating inline review thread with the concrete change, rationale, and commit SHA.

Do not auto-fix when:

- The comment is ambiguous and needs clarification.
- The reported behavior was already present at the PR merge base and the PR did not materially worsen it.
- The issue is only theoretical or has negligible practical impact.
- The request conflicts with explicit user instructions.
- The proposed change requires product/design decisions the user has not made.
- The codebase is in a dirty/unrelated state that makes safe editing uncertain.
- The inline review comment only needs a written answer or disagreement response; post a concise, factual `No change made.` reply in that thread, ending with the required Codex signature, unless it requires an unresolved product decision, private context, or cross-team coordination.
- The feedback is a PR issue comment, review summary, check annotation, or embedded bot-summary section with no inline thread; report it to the user and do not create a top-level fallback comment.

## Stop-and-ask conditions

Stop and ask the user instead of continuing automatically when:

- The local worktree has unrelated uncommitted changes.
- `gh` auth/permissions fail.
- The PR branch cannot be pushed.
- CI failures persist after the flaky retry budget.
- Reviewer feedback requires a product decision or cross-team coordination.
- A review response requires an unresolved product decision, private context, or cross-team coordination.
