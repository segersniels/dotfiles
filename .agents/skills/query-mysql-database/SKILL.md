---
name: query-mysql-database
description: Run read-only MySQL queries, inspect schemas, or verify database access with the bundled Bun script.
---

Use the bundled `scripts/query-mysql-database.ts` for MySQL reads. It requires Bun and has no package dependencies.

## Setup and target verification

Keep the user's project as the command working directory so its environment remains available. Resolve the script against the directory containing this loaded `SKILL.md`; do not switch into the skill directory or substitute another database client.

In the examples below, replace `<absolute-skill-directory>` with that resolved directory:

```bash
bun run "<absolute-skill-directory>/scripts/query-mysql-database.ts" --help
bun run "<absolute-skill-directory>/scripts/query-mysql-database.ts" check
```

Use the project's existing `AGENT_MYSQL_HOST`, `AGENT_MYSQL_PORT`, `AGENT_MYSQL_USER`, `AGENT_MYSQL_DATABASE`, and `AGENT_MYSQL_PASSWORD` environment variables. If required credentials are unavailable, report what is missing without exposing secrets.

Before querying a target, verify that `check.ok` is true and that the reported database and account match the intended target. A failed check or unexpected target blocks queries. Repeat verification when the connection target or credentials change.

## Reads

```bash
bun run "<absolute-skill-directory>/scripts/query-mysql-database.ts" query --sql 'show tables'
bun run "<absolute-skill-directory>/scripts/query-mysql-database.ts" query --sql 'describe users'
bun run "<absolute-skill-directory>/scripts/query-mysql-database.ts" query --sql 'select id, created_at from users order by created_at desc limit 10'
```

For longer SQL, use a temporary file:

```bash
bun run "<absolute-skill-directory>/scripts/query-mysql-database.ts" query --file /tmp/query.sql
```

## Query boundaries

- Keep the default 5 second server-side timeout. Lower it with `--timeout-seconds` for speculative queries; raise it only with explicit user approval.
- Bound row-returning queries with SQL `LIMIT` unless the user explicitly requests a broad export. The script's output row cap does not limit database work.
- Use read-only credentials even though the script enforces a read-only transaction and rejects obvious write/admin SQL. Its grant check does not probe writes; role grants may remain unverified.
- Treat results as sensitive. Return the evidence needed for the question, not large raw result sets.
- This workflow does not perform writes, schema changes, locks, stored procedure calls, sensitive bulk exports, or credential changes. Those operations require a separately authorized workflow.
