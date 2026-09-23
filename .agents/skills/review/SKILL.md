---
name: review
description: Review pull requests, branches, commits, or local diffs and prepare useful PR comments about proven concerns.
---

Find actionable problems supported by evidence. Omit style preferences and nits unless requested. Perform the review directly; do not delegate coverage or candidate generation to subagents.

## Scope and target

A review-only request is read-only. Its deliverables are findings and proposed review comments. Do not edit product code, add tests, commit, push, approve, post comments, or create external tasks without authorization for that action. Temporary mutation checks are limited to a permitted isolated disposable checkout.

Review TODOs are candidates for PR comments, not implementation assignments. Stay in the reviewer role during the walkthrough: a fix direction is advice for the PR author. Switch to implementation only when the user explicitly requests it; a review request or agreement to go through TODOs does not imply that request.

Read applicable `AGENTS.md` and review instructions. Read linked project docs for the behavior under review, and voice guidance when preparing comments; do not load every referenced document by default.

Establish the exact diff and its intended behavior:

- For a PR, record the immutable base and current head SHAs, read its description and relevant linked issue, and inspect changed files, commits, tests, and existing review threads. Label inferred acceptance criteria.
- For a branch, commit, or local diff, identify the correct base and include the requested staged and unstaged changes.
- Use a dedicated isolated worktree for PR reviews. Reuse a suitable existing one, or create it with a supported harness or Git mechanism and configured environment setup. Carry the PR URL and recorded SHAs into that context, using the head ref or a detached recorded head. Do not recursively create review tasks. Try another safe mechanism if one is unavailable; if isolation cannot be established, report the coverage limitation.
- Use the current checkout for local reviews when suitable. Preserve unrelated user changes.

## Coverage and verification

Account for every changed file and trace meaningful behavior changes through the relevant callers, transformations, and consumers. Keep ordinary reviews focused. Use a brief, flow map, or coverage ledger when complexity makes it useful, rather than producing each artifact for every review.

For a bug fix, reconstruct the reported failure and verify the proposed cause. Treat the ticket's explanation as a hypothesis. Compare base and head behavior, and check whether existing callers or lower layers prevent the suspected problem.

Load only the applicable sections of [risk-triggered checks](references/risk-triggered-checks.md) when changes involve state provenance, normalization or resolution, reuse costs, interacting cases, recurring or high-volume work, product interactions, test quality, or review-fix deltas.

A reportable finding needs:

- An exact file and line in the reviewed version.
- A reachable trigger and concrete correctness, maintenance, performance, or acceptance impact.
- Evidence that the change introduced or materially worsened the issue.
- Verified runtime, repository, or product assumptions.
- A distinct concern not already covered by another finding or existing review thread.

Check counterevidence before retaining a candidate. Drop disproved, duplicate, unreachable, or negligible claims; they are not coverage gaps. Record plausible material concerns that cannot be verified as uncertainty, not proven findings.

Read changed tests and run focused checks for central behavior or suspected regressions. Follow repository-required checks; do not run broad suites merely to accumulate verification. Do not repair an unavailable environment beyond configured setup during review.

For central stateful, multi-stage, resolver-heavy, or similarly high-risk changes, assess whether tests would catch a broken implementation. Use the conditional mutation guidance in the reference when practical and permitted. Restore temporary mutations and report material test-quality gaps.

## Completion

Finish when the requested diff has been covered, retained concerns are verified or explicitly uncertain, relevant existing findings are reconciled, and the target is still current:

- PR: refresh the remote head and compare it with the reviewed SHA.
- Committed local changes: confirm HEAD is unchanged.
- Uncommitted changes: confirm the working-tree and index diffs still match what was reviewed.

If the target changed, review the new delta before giving a current verdict. Do not reuse an earlier clean verdict for a later head. Elapsed time alone never justifies a clean verdict; report incomplete coverage when needed. Do not expand into unrelated pre-existing issues.

## Report

Always deliver the complete initial review with these sections in this order:

1. **What the PR aims to fix:** Explain the original problem, why it matters, and the expected behavior in junior-friendly language. State when no linked ticket is available and label inferred intent. For a feature or local diff, explain its intended outcome instead of inventing a bug or PR.
2. **How the PR addresses it:** Explain the main changes and the resulting flow in plain language. Connect the implementation to the intended outcome, define unfamiliar terms, and use a small example when helpful. Distinguish verified behavior from the PR's claims.
3. **Findings and verification:** List verified findings by severity with file/line, evidence, practical impact, and fix direction. State coverage and material uncertainty; do not give a confident clean verdict when material coverage remains unresolved. Keep disproved hypotheses internal and mention relevant pre-existing issues separately.
4. **TODO list:** Propose a numbered, prioritized list of concerns worth turning into PR review comments. Each item names the concern and the comment to prepare, rather than assigning a code or test change to Codex. Include practical, evidence-backed findings and demonstrated test gaps with a clear reason they matter to this PR. Keep general verification limitations in the findings section; missing coverage alone does not justify a comment. Include the TODO section even when empty; say `No comment-worthy TODOs identified` instead of inventing work.

End by asking: `Ready to go through the TODO list one by one?`

## TODO walkthrough and PR comments

When the user accepts, take the first TODO and present: **Problem**, **Evidence**, **Impact**, **Fix direction**, **Suggested PR comment**, **Severity**, and **Status**. Keep the explanation junior-friendly and provide the actual proposed comment text, with its target file and line or existing thread. Lead the comment with the issue and practical impact, then explain the proposed fix. It must make sense to the PR author without this conversation.

End with `Post this comment on the PR?` and wait for the user's decision before advancing. The user can revise or skip the draft. A `yes` to the walkthrough means explain and draft the next comment; a `yes` to this posting question authorizes posting that comment. Do not respond to a review TODO by offering to implement the fix or add the test.

When posting is authorized, recheck the current PR head and existing threads, verify the concern still applies, and post to the appropriate file/line or existing thread without duplicating feedback. Verify the posted comment and mark the TODO as posted before continuing. Otherwise keep it drafted or mark it skipped. Respect any explicit batch-posting authorization without asking again for each comment.

For a local review without a PR, prepare the same actionable feedback without inventing a posting destination. Keep implementation requests separate from comment review and posting; carry out an explicit implementation request within its authorized scope.

Write proposed or authorized PR comments with ASD-STE100 Simplified Technical English principles: short, complete, active-voice sentences, consistent terms, explicit nouns, and no contractions. Preserve technical identifiers and quoted evidence.
