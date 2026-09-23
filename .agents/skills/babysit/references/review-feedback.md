# Review Feedback

Read when the watcher surfaces review items. Before deciding on a code change or a response that depends on product intent, use [scope and safe fixes](safe-fixes.md).

## Select actionable feedback

Consider published feedback from humans and bots, including existing unaddressed feedback surfaced by a fresh state file. Ignore reviews in `PENDING` state and their inline comments; do not acknowledge unpublished feedback.

Ignore status-only messages, approvals, duplicates, self-authored follow-ups, and resolved threads without new unresolved feedback. Deliberately classify these before acknowledging them.

Apply the mandatory [comment-assessment checklist](../SKILL.md#assess-every-review-comment) to each substantive item before choosing a disposition below.

| Finding | Disposition |
| --- | --- |
| PR introduced or materially worsened a real in-scope issue | Make and validate the smallest fix, commit, push, and reply in the originating inline thread. |
| Rare but credible security, privacy, data-loss, or corruption issue | Do not dismiss it merely because it is uncommon. Apply the same scope and evidence checks. |
| Pre-existing behavior unchanged in reachability or impact | Do not expand the PR. Explain the base/head evidence in the inline thread; surface material risks to the user for separate handling. |
| Incorrect, already addressed, unreachable, or negligible concern | Make no code change and give an evidence-backed rationale in the inline thread. |
| Proposed scope change that the user has not decided, or new evidence that may change a deliberate trade-off | Ask the user before changing code or posting a disposition. Continue independent authorized work. |

A touched nearby file does not make a pre-existing issue part of the PR. When explicit user direction already settles the feedback and no new material evidence challenges it, explain that decision in the originating inline thread without asking again. Keep independent fixes separate; reply in every originating thread when several comments share a fix.

## Reply only in the originating inline thread

Use the inline review-comment reply endpoint with the watcher's `thread_root_id`. Verify that the created comment's `in_reply_to_id` equals that root before reporting success or acknowledging completion. See [API notes](github-api-notes.md#review-follow-up-endpoints) for the endpoint.

PR issue comments, review summaries, check annotations, and findings embedded in bot summaries have no inline thread target. Report that limitation to the user; do not create top-level comments as a substitute. A failed reply endpoint also does not authorize another posting destination.

Leave review threads open for reviewer follow-up unless the user explicitly asks for resolution. Keep replies limited to the disposition of surfaced feedback.

## Reply style

Use short, complete, active-voice sentences with ASD-STE100 Simplified Technical English principles. Keep terms consistent, use explicit nouns, and avoid contractions. Preserve exact identifiers, paths, SHAs, and quoted evidence.

Begin with `@<author-login>` using the originating item's author, except for Codex accounts. Never mention `@codex` or a Codex bot/service account in these replies because that can launch another task. Mention other human and automated reviewers.

Lead with `Addressed in <commit-sha>.` or `No change made.`, followed by the practical reason and supporting evidence. Explain unfamiliar terms and add an example only when it helps. Keep the reply understandable without the investigation history.

Do not append signatures, sign-offs, or automation attribution footers unless the user explicitly requests them.

## Acknowledge only completed dispositions

For a fix, verify the push and required inline reply first. For a no-change disposition, verify the inline reply. For ignorable feedback, finish its classification. Substantive feedback without an inline target needs a user handoff, not a fabricated reply or premature acknowledgement.

Stop the current watcher, acknowledge completed items, and restart `--watch`:

```bash
python3 "<babysit-skill-directory>/scripts/gh_pr_watch.py" \
  --pr <pr-url> \
  --ack-review-item <issue_comment|review_comment|review>:<id>
```

Resolve the skill directory as described in `SKILL.md`. The acknowledgement flag is repeatable. Use `--requeue-review-item <kind>:<id>` only to recover feedback that was incorrectly acknowledged or migrated as handled. Pending feedback otherwise repeats in snapshots; fetching it is not completion.
