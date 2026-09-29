# Code Review Criteria

The baseline criteria for the review skill. A repo's own review guide (`REVIEW.md`, a review
section in AGENTS.md / CLAUDE.md, or docs they link) adds to these. Where the two conflict, the
repo's guide wins.

## Contents
- Top priorities
- Gates for every finding: Reachability, Efficacy, Provenance, Impact
- Already-flagged findings
- Writing up a bug
- Severity labels
- When to approve
- Always check: Correctness (incl. "Prose is a claim", "Refactor parity", "Chesterton's Fence", "Entitlement / visibility gates"), Data access, Architecture, UI state, Security, Audit logs, Dependencies, Patterns & conventions, Testing (incl. "Mutation check"), AI / LLM interface (evals)
- Style (incl. "Don't flood the review")
- Skip

## Top priorities

These are the most important things to check, in order:

1. **Simplicity** — is this the simplest approach? Flag over-engineering, premature abstractions, and unnecessary complexity. If there's a simpler way, say so. Don't stop at "this could be cleaner" — actively look for the reframing that makes whole branches, helpers, or layers *disappear*. Prefer deleting complexity over rearranging it; if there's a path to a dramatically simpler version, push for it.
2. **Readability** — favor clarity over cleverness. If code is hard to follow, it should be rewritten.
3. **Reuse** — does similar logic already exist in the codebase? Flag duplication and point to existing helpers, utilities, or patterns that should be used instead.
4. **Don't over-engineer** — no feature flags, config options, or abstractions for hypothetical future needs. Solve the problem at hand, nothing more.
5. **Impact analysis** — trace all callers and consumers of touched code. Investigate whether the change breaks behavior, alters return values, or affects downstream logic anywhere in the codebase. This is critical.

## Reachability gate

Before flagging any `bug` / `regression` / `concern`, name the **concrete trigger**: the real
caller or user action that makes it fire, and what the user or system **observably** experiences as
a result. Trace the actual callers (grep them) — don't reason from the function in isolation.

- If you can't construct a real trigger path, treat the finding as **theoretical** — prefer dropping
  it, or label it `theoretical` and keep it at `nit`. Avoid framing a theoretical issue as a concern.
- A finding that's only reachable by calling an internal function in a way no real caller does
  probably isn't a real bug. A test that fabricates such a call isn't a reproduction on its own.
- If every path that reaches the condition also changes its precondition, the condition is likely
  unreachable — lean towards dropping it.
- When unsure whether it's reachable, say so explicitly and rate confidence low, rather than
  asserting impact you haven't proven.

A finding can still be valid even if nothing triggers it *today* — a fragile invariant, a missing
guard that only holds by luck, or a foot-gun a plausible near-future change (a new caller, a
refactor) would walk straight into. Flag these as **latent / hardening**, calibrate severity to how
likely that future trigger is, and frame them as future risk — don't pass them off as a bug that's
broken today, and don't drop them just because the current code happens to avoid the path.

## Efficacy gate

On a bugfix PR the first question is not "is this code correct?" but **"does this actually fix the
problem?"** So establish the problem first, then hold the diff against it.

**Establishing the goal**, best source first:

1. The linked ticket's *problem statement* — not its scope line, and not its title.
2. The PR body, but only the part describing the **problem**. Descriptions usually narrate the
   *change*, and a diff held against a goal restated from that same diff always passes. Reach past
   it: what was broken, what was missing, who complained.
3. Commit messages, the linked issue or thread, and the diff itself, when the body only says *what*
   was done and never *why*. Say so when that's the case.

Often there is no ticket access. That's fine — work from 2 and 3, but **state the goal you derived
in one line in the summary** so the author can correct it. Reviewing against a goal you silently
invented is worse than admitting the goal is unclear.

**Then hold the diff against it:**

- A fix that addresses one plausible cause of an unreproduced bug can leave the real cause untouched.
  If that's the case, say what would still be broken. **That's a blocker**, not a nit.
- The same applies to a fix that works but treats a symptom while the root cause survives.
- **This overrides the provenance gate below.** Pre-existing behaviour that the problem exists to fix
  is not out of scope, it *is* the point. Never wave "that's pre-existing" at the defect being fixed.
- Where there's no repro, say plainly that the fix can't be *proven* to close it, and name the signal
  that would confirm it after deploy.
- On a feature PR the same question is coverage of the ask. List what the ticket or body asked for
  that is missing or partial, and what the diff does that nobody asked for. Quote the line of the ask
  each finding hangs on, so the author can see which requirement you read it against.
- If you can't establish the goal at all, say that instead of quietly assuming one.

## Provenance gate

Classify where the finding came from and state it in the finding itself, unprompted. A finding that
can't fill this in hasn't been investigated enough to present.

The diff is the signal, and it's usually enough on its own: `+` lines are this PR's, context lines
are pre-existing. Don't infer provenance from how new the surrounding code looks.

- **pre-existing** — the behaviour is unchanged by this PR. **Never blocking** when it's unrelated
  to the task at hand, and never a reason to churn the diff. But don't bury it either: a genuinely
  valuable find is still worth surfacing. Report it in the summary, explicitly labelled pre-existing
  and out of scope, and let the author decide whether it earns a follow-up. The line is between
  *telling someone* and *holding up their PR over it* — do the first, never the second.
  **Exception:** pre-existing behaviour that is the ticket's actual defect. That's the Efficacy gate
  above, and it blocks.
- **introduced by this PR** — the author wrote it. Fair game.
- **introduced by review feedback on this PR** — a reviewer asked for X, the author added X, X is
  imperfect. Still in scope, but it is not a regression and rarely blocking. Saying so keeps the
  severity honest.

Ask **"is it a regression?"** separately. Something that worked before and is broken now is a
different animal from something new that merely works less well than it could.

## Impact gate

Proving the mechanism is not the same as proving it matters. Reading the code, or even the
dependency's source, tells you the thing is *real*. It does not tell you it's worth the author's
time. Before presenting anything that survived the gates above:

- Name what the user, or the on-call engineer, concretely loses.
- Check whether that's recoverable another way — a URL already on the event, a DB query, an existing
  log, a second code path. Recoverable in minutes means it's a nit at most, often not worth raising.
- Consider whether a different primitive fits the job better before proposing a fix.
- If you can't check whether it's recoverable — no way to run it, query it, or read the other path —
  say so and lower the confidence. Never assert an impact you haven't established.

Expect findings to die here, including ones you've already verified in source. That's the gate
working, not wasted effort.

## Already-flagged findings

A point another reviewer or bot already raised is **not** automatically out of scope, and not
automatically correct. It means exactly one thing: **don't raise it again as if it were new.**

- Never open a second thread where one already exists. If you have something to add, reply in that
  thread, framed as a follow-up rather than a fresh discovery.
- Keep it in the findings list, labelled with who flagged it, so the picture stays complete.
- **Verify validity and resolution separately.** They're independent questions, and both are claims:
  a confidently-worded finding — especially from a bot — is not proof of a defect, and a resolved
  thread is not proof of a fix. "Fixed in abc123" is worth holding against the diff.
- A valid finding that wasn't actually fixed **is a finding**. Raise it in the existing thread.
- A bogus finding that *was* "fixed" is also a finding: the author churned the diff for a non-issue.
  Say so.
- If the original flag was simply wrong and still open, say so and unblock the author.

Carry a status rather than a binary: `already flagged by <who>` plus `verified fixed` / `not fixed` /
`was never valid` / `disputed`.

## Writing up a bug

Explain every `bug`, `regression` or `concern` in **ASD-STE100 Simplified Technical English**. An
author reads a finding once, in a hurry, often in a second language. STE strips out the ambiguity
that makes them read it twice, or act on the wrong part of it.

This covers the explanation itself: the trigger, the mechanism, the consequence. Titles, code
snippets, quoted output and log lines stay as they are.

The rules that carry the weight here:

- One idea per sentence. Keep sentences under 20 words and paragraphs under 6 sentences.
- Active voice, with the actor named. "The handler drops the event", not "the event is dropped".
- Simple present, past or future tense. No `-ing` verb forms: "when the user submits", not "on
  submitting".
- One word, one meaning. Pick the noun for a thing and repeat it. Don't drift between "order",
  "record" and "entry" for the same object.
- No more than three nouns in a row. Break up "order submission validation error path".
- Never drop articles or helper words to make a sentence shorter.
- State what happens. No hedged clauses stacked on each other, no "it is possible that".

Avoid:

> Due to the fact that the validation error path is being invoked prior to the null check being
> performed, it is possible that a crash could potentially occur for some submissions.

Prefer:

> The handler calls `validate()` before the null check. If `payload` is null, `validate()` throws.
> The API returns a 500 error and the user sees "Something went wrong".

## Severity labels

- **blocker** — must fix before merge (security vulnerability, data loss, broken functionality)
- **concern** — should fix before merge (wrong abstraction, missing edge case, subtle regression risk)
- **nit** — optional, author's call (naming, minor style, alternative approach)

## When to approve

Be a critical but fair technical lead. Question everything, be thorough — then **approve when the
changes definitely improve overall code health. Don't block because it isn't exactly how you'd write
it.** Request changes only for a blocker, or a concern that genuinely hurts code health.

"I'd have done this differently" is not a review finding. Neither is a preference dressed as a
concern. The bar for holding up someone's work is that the codebase is measurably worse if it lands.

## Always check

### Correctness

- **Prose is a claim, not context.** The PR body, commit message, code comments and linked ticket all
  assert things about the code. Check each against the code and say so when it doesn't hold. The
  recurring shapes are a fix described as broader than it is, a "not retroactive" note that isn't,
  and a comment that outlived the behavior it describes. A claim that survives checking is worth
  reporting too. The author's framing is exactly what a sycophantic review rubber-stamps, so when the
  body says a behavior was a bug, verify the old behavior was actually wrong before blessing its
  removal.
- Trace all references to changed functions, types, and exports — flag any caller where behavior may have shifted
- **Refactor parity**: when a PR moves or rewrites a component, diff the old and new implementations. Check that every code path, state transition, and UI element is either intentionally removed or preserved. This is where subtle regressions hide.
- **Chesterton's Fence**: before removing or simplifying code that seems unnecessary, check git blame and understand why it exists — the reason may still apply
- **Behavioral changes in refactors**: if a PR claims to be a refactor but adds filters, changes conditions, removes UI elements, or alters API call patterns, flag it — that's a behavior change, not a refactor
- **Entitlement / visibility gates**: when a change tightens who sees a UI element (adds a plan/role check, hides a button), trace what the now-excluded user's click previously did before approving — a free-tier user seeing a paid feature's entry point is often a deliberate upsell, and hiding it strands that path. Don't treat the PR's own "fixes a mismatch" / "users shouldn't see this" framing as proof the old behavior was a bug — that's a claim to verify, not a fact
- **Data-fetching semantics**: loading flags differ between the first load and a background refetch (e.g. `isLoading` vs `isValidating` / `isFetching`) — mixing them up causes skeleton flashes or missing loading states
- No nested ternaries (`? : ? : ? :`) — use if/else for complex branches
- Defensive handling of optional values where the data can actually be missing
- No race conditions or stale closures in async code and UI hooks
- Error handling wraps risky operations (external APIs, file I/O) and reports failures to the repo's error tracking, so they are visible
- No dead code left behind — after refactoring, actively identify orphaned functions, unused imports, and unreachable branches
- Flag unnecessary work — redundant computations, missing short-circuits, or obvious performance issues

### Data access

Every query the diff adds is paid on every request that reaches it, and new code is where the pattern
gets locked in. Read the queries, don't skim them. Check scale against real data when the repo gives
you a way to, before you assert impact.

- **Count the round trips on the path.** A query inside a loop is an N+1 until proven otherwise:
  batch it into one query over a list of ids, or hoist it out of the loop. Say how many queries one
  request runs now versus before.
- **A fetch that runs before anything needs it is waste.** Check what each query is actually used for.
  If only one branch reads it, or a cheap guard could skip it, it belongs behind that condition.
- **Reuse what the caller already holds.** When the handler already loaded the rows, pass them in
  rather than looking them up again on the same key. A re-query is also a second version of the same
  truth, which is how the two drift.
- **Check the projection.** No full row load on a wide or large table when two columns would do —
  one row of a wide table can be hundreds of KB, and a wide select inside a loop is both problems at
  once.
- **Check what the filter can use.** A `WHERE` or `ORDER BY` on an unindexed column scans. Confirm
  against the schema or the database instead of guessing, and prefer an index that already exists
  over asking for a new one; a new index costs writes and a schema change.
- **Bound anything unbounded.** A query with no limit over a table that grows with usage is a future
  timeout, not a style nit. Same for an update or delete sweep with no batching.
- **Calibrate, don't inflate.** "One extra indexed lookup per item, and there is normally one item" is
  a nit that often isn't worth raising. "Fetches every row of the parent on every request" is a
  concern. Say which of the two you have, and don't dress an indexed lookup up as a blocker.

### Architecture

- Review the entire architecture of the changes — was this the simplest, most pragmatic approach? Especially important for bigger PRs
- New loops don't duplicate iteration over data already looped elsewhere — extend or re-use existing loops instead
- No unnecessary complexity — flag over-engineering and premature abstractions
- A PR pushing a file from under ~1,000 lines to over it is a presumptive smell — ask whether it should be decomposed first, unless there's a strong reason
- No spaghetti growth — new ad-hoc conditionals or one-off branches bolted onto unrelated flows are a design problem, not a style nit; push them behind a dedicated abstraction
- Flag thin wrappers and identity abstractions that add indirection without buying clarity
- A refactor that only moves complexity around without deleting it hasn't simplified anything — say so
- "Temporary" branching tends to become permanent debt — flag it
- Refactors update all consumers directly — no lazy re-exports from old locations
- Changes stay within the stated PR scope — flag unrelated modifications, but expand scope if a reviewer identifies a real user-facing bug
- Scope binds the reviewer too — findings in files the PR doesn't touch are out of scope by construction. Note them under "pre-existing, out of scope" rather than raising them against the diff, unless it's a real user-facing bug worth expanding scope for

### UI state (React and similar)

- If a value can be computed from existing state or props, derive it during render — don't store it in separate state
- No state + effect pair to "sync" state from other state or props — that's redundant state with an extra render cycle
- Store minimal canonical data (e.g. an ID), derive the rest (e.g. look up the object)
- Use functional state updates (`setState(prev => ...)`) inside memoized callbacks to avoid stale closures and keep callback refs stable
- Flag optimistic state patterns that duplicate what the data-fetching layer (SWR, React Query) already handles

### Security

- User input validated at API boundaries — no raw input passed to queries, shell commands, or HTML rendering
- Database queries use parameterized inputs (ORM or prepared statements), never string concatenation
- No secrets (API keys, tokens, passwords) in code, logs, or commit history
- Authorization checked on protected endpoints — verify users can only access their own resources (IDOR)
- Error responses don't expose stack traces or internal details to users

Flag security only where the change creates a concrete, exploitable risk, removes a safety check, or
skips validation at a trust boundary. **Don't flag legitimate functionality merely because it touches
shell, filesystem, network, or auth** — proximity to a sensitive API is not a vulnerability, and
treating it as one buries the findings that are.

### Audit logs

Apply when the repo keeps an audit log or a staff-access log. Its docs have the how.

- **A new staff or admin surface that reads or changes customer data must log the access.** Check it
  names every customer it touches, not just the first.
- **Check where the log call sits.** An access log belongs before the work: a handler that returns
  early has still read the data. An action log belongs after the work: a log before the write records
  an action that a later throw can still cancel.
- **A lookup added only to name the customer must not be able to break the action.** It must swallow
  its own failure.
- **A new writing route must be classified** when the repo keeps an audited / unaudited route list.
  Check the classification is right, not only that it is there.
- **A create logs the created id**, or the row names the parent object and reads as an edit of it.
- **No payloads in the row.** Ids, a route or command name, a status and short enum values. Never
  bodies, names, emails or tokens.

### Dependencies

- Does the existing stack already solve this? Prefer existing utilities over new dependencies
- Check bundle impact, maintenance status, and known vulnerabilities
- License must be compatible with the project

### Patterns & conventions

- Follow the conventions the repo documents; a convention finding must cite the doc line it rests on
- User-facing text uses the repo's i18n system when it has one, never hardcoded strings
- Theme-aware colors — no hardcoded color values that only work in one theme
- Prefer CSS media queries (`@media (hover: hover) and (pointer: fine)`) over JavaScript-based touch/hover detection

### Testing

- **Review tests first** — tests reveal intent and expected behavior before you read the implementation
- New or changed logic has corresponding test coverage — but never ask for a spec that cannot fail.
  Missing tests and slop tests are both findings:
  - **Smoke tests** — "it renders", "it does not throw", "the service is defined" — pass against
    almost any implementation, so a green run reports nothing.
  - **Deletion tests** — when a feature is removed, the deleted code is the proof. A spec that
    asserts the feature is gone pins the absence forever.
  - If you cannot name the defect a test catches, it should not exist.
- Tests verify behavior, not implementation details — would they catch a regression if the code changed?
- **Mutation check**: for any test in the diff, name a concrete edit to the source that leaves it
  green. If you can't construct one, the test pins its behavior. If you can, that edit *is* the
  finding: quote the mutation and the surviving count rather than writing "coverage looks thin".
  The usual survivors are an off-by-one in a boundary constant, a call site reverted to its old
  form, and a guard deleted outright.
- **Fixture realism**: check the fixture against the shape the real dependency actually returns, not
  a convenient one. A test that is green against input production never produces certifies a path
  that nothing reaches.
- **Boundaries need both sides.** Covering only the side that passes leaves an off-by-one free.

### AI / LLM interface (evals)

When a PR changes anything the model sees or acts on — tool arguments/schemas, tool descriptions,
system prompts, the context format fed to the model, tool-error feedback strings, or which tools are
exposed — unit tests won't catch a behavioral regression. The change can typecheck and pass every
spec while the model quietly starts picking the wrong tool, misreading the context, or regressing on
a task.

- Flag these PRs and recommend running the repo's evals for that surface before merge — the diff
  alone can't prove the model still behaves.
- If eval results are already posted on the PR, treat that as the evidence and just confirm the
  touched surface is covered — don't ask for a re-run. If no eval ran and the interface changed,
  that's a coverage gap worth calling out, not a blocker.
- Evals are generative, a bit flaky (a lone failing case is usually noise), and cost tokens —
  recommend, don't auto-run them mid-review unless asked.

## Style

- Prefer `||` or `??` over ternaries when condition and truthy branch are the same value
- Prefer early returns over deeply nested conditionals
- Extract helpers when duplicating 10+ lines of logic
- Match existing code patterns in the surrounding file and package
- Comments should add value — flag essay/docstring blocks added by default and any comment that just restates the code or the function/variable name. A concise usage note above a function or class is welcome; line-by-line narration is not
- Favor clarity over cleverness — if code is hard to read, it should be simplified
- Don't flood the review — prefer a few high-conviction findings over a long list of nits; when there's a structural issue, suppress cosmetic notes, they're noise next to the real problem
- Variables and functions should be clearly named — flag vague names like `data`, `temp`, `result` when a more descriptive name is obvious
- Quantify impact where possible — "this N+1 adds ~50ms per item" beats "this could be slow"

## Skip

- Formatting and whitespace — handled by the repo's formatter
- Import ordering — handled by linters
- Missing comments or docstrings on code that wasn't changed in the PR
- Generated files and lock files
- Working code that you'd write differently but isn't broken or unclear — don't nitpick style preferences on unchanged code
- Review metadata — a stale or outdated PR title, body or description is the author's to keep current, not a review finding. Mention it in the summary at most
- Commit history — how the branch is sliced, the order of commits, and whether an intermediate commit
  builds or passes its tests on its own. That is the author's call, never a review finding
