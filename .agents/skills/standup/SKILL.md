---
name: standup
description: List the GitHub pull requests the user opened or merged since a given time as a short bullet TLDR for a standup. Use when the user asks for a standup summary, what they worked on, or their PR activity since a timestamp.
---

Give the user a quick standup overview of their own pull request activity. This is read-only: do not comment on, edit, or change any pull request.

## Resolve the start time

- Accept any time format: ISO timestamp, date, weekday, or a phrase such as "yesterday 9am".
- Read times without a timezone as local time. Get the local offset with `date +%z`.
- If the user gives no time, use 00:00 local time on the previous workday. On Monday, use Friday.
- Convert the start time to ISO 8601 with an offset, for example `2026-10-16T09:00:00+02:00`.

## Fetch pull requests

Run both searches in parallel. Replace `<since>` with the resolved start time.

```bash
gh search prs --author=@me --merged-at=">=<since>" --limit 200 \
  --json number,title,url,repository,closedAt
```

```bash
gh search prs --author=@me --created=">=<since>" --limit 200 \
  --json number,title,url,repository,state,isDraft,createdAt
```

- The searches cover every repository the user can access, not only the current one.
- A pull request that was opened and merged in the window belongs only under **Merged**.
- Under **Opened**, mark drafts with `(draft)` and pull requests closed without merge with `(closed)`.
- If a search returns 200 results, tell the user the list can be incomplete.

## Output

Start with one line that states the window, for example `Since Fri 16 Oct 09:00:`. Then show the sections below. Leave out an empty section.

```markdown
**Merged**
- Plain-language summary of the change ([repo#123](url))

**Opened**
- Plain-language summary of the change ([repo#124](url)) (draft)
```

- Write each bullet as a short phrase that the user can say aloud in a standup.
- Remove the Conventional Commit prefix, such as `fix(blocks):`, from the title. Keep ticket IDs such as `[TL-123]`.
- Use only the repository name in the link text. Use `owner/repo` only when two repositories share a name.
- Sort each section from newest to oldest.
- If both searches return nothing, say that no pull requests were opened or merged since the start time.

Do not add commentary, suggestions, or a closing summary after the list.
