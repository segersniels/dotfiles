---
name: query-mysql-database
description: Use when Codex needs to query a MySQL database with read-only credentials, inspect tables, run SELECT/SHOW/DESCRIBE/EXPLAIN SQL, or verify MySQL access. Prefer this over ad hoc mysql clients or one-off scripts for database reads.
---

# Query MySQL Database

Use the bundled script for MySQL reads. Keep the user's current project as the command working directory so its environment remains available. In tool calls, resolve `scripts/query-mysql-database.ts` against the directory containing this loaded `SKILL.md`, then pass that absolute path to Bun. Do not change into the skill directory or assume a fixed home or installation path.

## Available Script

- **`scripts/query-mysql-database.ts`** — Checks read-only access and runs bounded MySQL queries with Bun's built-in SQL client.

Requires Bun. It has no package dependencies.

## Workflow

Inspect the concise command interface when needed:

```bash
bun run scripts/query-mysql-database.ts --help
```

Configure credentials with only these environment variables:

```bash
export AGENT_MYSQL_HOST='...'
export AGENT_MYSQL_PORT='3306'
export AGENT_MYSQL_USER='...'
export AGENT_MYSQL_DATABASE='...'
export AGENT_MYSQL_PASSWORD='...'
```

Before querying, verify that the reported database and account match the intended target and that `ok` is `true`:

```bash
bun run scripts/query-mysql-database.ts check
```

## Common Reads

Discover tables:

```bash
bun run scripts/query-mysql-database.ts query --sql 'show tables'
```

Inspect one table:

```bash
bun run scripts/query-mysql-database.ts query --sql 'describe users'
```

Run a bounded query:

```bash
bun run scripts/query-mysql-database.ts query --sql 'select id, created_at from users order by created_at desc limit 10'
```

Queries use a 5 second server-side timeout by default. Lower it with `--timeout-seconds`; do not raise it above 5 unless the user explicitly accepts the risk.

For longer SQL, prefer a temp file:

```bash
bun run scripts/query-mysql-database.ts query --file /tmp/query.sql
```

## Rules

- Treat `check.ok=false` or an unexpected database/account as a blocker before querying.
- Resolve and use the bundled `scripts/query-mysql-database.ts`; do not substitute another database client or hardcode its installation path.
- Keep the default 5 second query timeout. Use a lower `--timeout-seconds` for speculative queries; raise it only with explicit user approval.
- Keep queries bounded with `limit` unless the user explicitly asks for a broad export.
- Treat database data as sensitive; do not paste large raw result sets back into chat.
- The script enforces a read-only transaction and blocks obvious write/admin SQL, but still rely on read-only DB credentials.
- The security check inspects grants without probing writes; role grants may be reported as unverified.
- Do not attempt writes, schema changes, locks, stored procedure calls, exports of sensitive bulk data, or credential changes unless the user explicitly asks and approves the risk.
