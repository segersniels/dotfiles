---
name: investigate
description: Investigate code, bugs, logs, or diffs and report evidence before implementation.
---

Build enough understanding to answer the question, verify the likely cause, and explain material uncertainty.

## Scope

An investigation-only request ends with findings and next steps. If the user also authorized a fix, complete the investigation and continue with that fix without another approval pause. This skill governs discovery; it does not cancel other authorized work.

Keep investigation-only work free of source edits, formatting, dependency installs, and changes to Git or external services. Local checks may create disposable test output or caches when they do not change source files or shared services. Respect stricter user instructions and inspect unfamiliar test setup before running it.

## Evidence and completion

- Start with the narrowest scope that answers the request. Follow relevant callers, transformations, consumers, and tests until the behavior is supported by evidence.
- Read project instructions and supporting docs when they apply. Use primary documentation when a conclusion depends on external behavior.
- Distinguish observed behavior from hypotheses. Verify the conditions that make the reported failure reachable.
- Stop expanding the investigation once the question is answered and material alternatives are resolved or clearly identified as unknown.

Lead the report with the finding and its supporting file, line, log, or reproduction. Include the likely cause, material uncertainty, and the next step when useful. Ask only when missing information would change the scope or result; continue independent authorized work.
