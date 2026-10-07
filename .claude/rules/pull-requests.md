# Pull requests

A pull request description tells a reviewer what changed and why before they read the diff. When a rule here conflicts with the repository's own conventions or PR template, follow the repository.

## Before you open

- Push, open, or update a pull request only when the user asks.
- Use the base branch that the user names. If the user names none, use the repository default branch. For a stacked pull request, use the parent branch as `--base`.
- Read the commits and the full `git diff <base>...HEAD`. Describe the code that changed, not only the commit messages.
- If the repository has a pull request template, fill it in instead of the structure below.

## Title

- Use the same Conventional Commits format as a commit title: `type(scope): description`.
- Add a ticket ID only when the repository uses ticket IDs in titles.

## Body

Use this structure as the minimum:

```markdown
## Summary

1-3 specific sentences that explain what this pull request does and why.

## Changes

### Area (for example API, Frontend, Database, Tests)

- One concrete change per bullet.
```

- Write in short, complete, active-voice sentences. Use ASD-STE100 Simplified Technical English principles.
- Group changes by logical area with `###` headers.
- Add sections such as design decisions, trade-offs, scope limits, or usage examples only when the change is complex enough to need them. Use GitHub alerts such as `> [!NOTE]` for context like "no runtime impact".
- Do not include test plans, checklists, "How to test" sections, or deployment notes, unless the template asks for them.
- Do not mention commit counts or how the work is split across commits.
- Do not write vague summaries such as "various improvements".
- Do not hard-wrap. Write each paragraph and each bullet as one line.
- Write the body to a file and pass it with `--body-file`. Do not use heredocs, and do not include ANSI codes.

## Metadata

- Assign the user with `--assignee @me`.
- Add reviewers and labels only when the user or the repository convention names them.
