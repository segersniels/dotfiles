---
name: triage
description: "Investigate AI-created backlog bug tickets from Notion and judge whether the reported issue is confirmed, overstated, expected product behavior, false, or inconclusive. Use when the user passes a Notion ticket or backlog bug report for evidence-first validity assessment and, only for a valid issue, wants the smallest root-cause solution discussed with a Ponytail subagent."
---

# Triage

Assess the ticket; do not trust its framing. Stay read-only unless the user separately asks for implementation or a ticket update.

## Workflow

### 1. Read the complete ticket

- Open the supplied Notion ticket with the available Notion tools.
- Read its properties, description, reproduction steps, expected and actual behavior, attachments, comments, linked tickets, and source evidence.
- Treat AI-written claims, severity, scope, and proposed fixes as unverified assertions.
- If the ticket or relevant repository cannot be accessed, ask for the missing content or path. Do not guess.

### 2. Turn the report into testable claims

State separately:

- the behavior reportedly observed
- the behavior the ticket assumes is intended
- the affected path, users, and conditions
- the evidence that would prove or disprove each claim

Separate the core symptom from severity, frequency, scope, and impact. A real symptom does not validate an inflated impact claim.

### 3. Investigate the real behavior

- Read the repository's `AGENTS.md` and relevant local instructions.
- Trace the full reachable path: entrypoint, callers, owning component or service, shared helpers, configuration, feature flags, and tests.
- Look for explicit intent in tests, product copy, documentation, related tickets, commit history, and established adjacent behavior.
- Reproduce safely when practical. Prefer existing tests and read-only inspection; do not mutate production data or external systems.
- Search primary external documentation when the claim depends on a third-party contract.
- Quote exact code, logs, errors, or product language that materially supports the verdict. Distinguish direct evidence from inference.

Do not equate unusual behavior with a bug. A valid bug needs both:

1. a reachable, observable behavior; and
2. evidence that it violates an established requirement, invariant, contract, or clearly intended product behavior.

If intended behavior is genuinely unspecified, classify it as a product decision rather than inventing a requirement.

### 4. Assign one verdict

- **Confirmed bug** — the material claim is reproducible or directly proven and conflicts with established intent.
- **Valid but overstated** — a real defect exists, but the ticket exaggerates its reach, severity, frequency, or impact. State the narrower truth.
- **Product decision** — the behavior is real, but whether to change it is a UX/product choice with no established violated requirement.
- **False positive** — the claimed behavior is unreachable, contradicted by evidence, already handled, or based on a mistaken assumption.
- **Inconclusive** — decisive evidence is unavailable. Name exactly what is missing and the cheapest next check.

Use confidence `high`, `medium`, or `low`. Do not soften uncertainty into a confirmed verdict.

### 5. Consult Ponytail only for a valid issue

For **Confirmed bug** or **Valid but overstated**, spawn a `ponytail` subagent after completing the independent validity assessment.

Give Ponytail:

- the ticket's testable core claim, stripped of its proposed solution
- the verified evidence and actual scope
- relevant repository paths and constraints
- a read-only request to trace the same flow and recommend the smallest root-cause fix

Ask it explicitly whether no code change, deletion, reuse of an existing seam, configuration, or a one-place fix is sufficient. Do not ask it to implement. Reconcile its recommendation with the evidence; do not adopt it blindly.

Do not invoke Ponytail for **Product decision**, **False positive**, or **Inconclusive**. For a product decision, identify the smallest product question that needs an owner decision.

### 6. Report without mutating

Use this compact structure:

```markdown
## Verdict
[classification] — [confidence]

## What is actually true
[precise, bounded finding]

## Evidence
- [ticket or reproduction evidence]
- [code/product-intent evidence]

## Ticket accuracy
- Valid: [claims supported]
- Overstated or false: [claims not supported]

## KISS solution
[Ponytail-informed root-cause recommendation, only for a valid issue]

## Unknowns
[remaining uncertainty or "None material"]

## Recommended ticket action
[keep, narrow/rewrite, convert to product decision, close, or request evidence]
```

Omit `KISS solution` when the issue is not valid. Never edit the ticket, comment in Notion, change code, create a branch, or commit unless the user explicitly asks.
