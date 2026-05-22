---
name: query-mysql-database
description: Use when Codex needs to query a MySQL database with read-only credentials, inspect tables, run SELECT/SHOW/DESCRIBE/EXPLAIN SQL, or verify MySQL access. Prefer this over ad hoc mysql clients or one-off scripts for database reads.
---

# Query MySQL Database

Use the installed `query-mysql-database` CLI for MySQL reads.

## Workflow

Resolve the command first. Prefer the bundled prebuilt binary, then PATH. Do not rebuild Rust just because the command is missing from PATH.

```bash
QUERY_MYSQL_DATABASE="/Users/segersniels/.codex/clis/query-mysql-database/target/release/query-mysql-database"
if [ ! -x "$QUERY_MYSQL_DATABASE" ]; then
  QUERY_MYSQL_DATABASE="$(command -v query-mysql-database || true)"
fi
"$QUERY_MYSQL_DATABASE" --json doctor
"$QUERY_MYSQL_DATABASE" --json security check
```

Only rebuild if both PATH and the prebuilt binary are missing or broken:

```bash
cd /Users/segersniels/.codex/clis/query-mysql-database
CARGO_HOME=/private/tmp/codex-cargo-home cargo build --release
```

Configure credentials through environment variables first:

```bash
export CODEX_SKILL_MYSQL_HOST='...'
export CODEX_SKILL_MYSQL_PORT='3306'
export CODEX_SKILL_MYSQL_USER='...'
export CODEX_SKILL_MYSQL_DATABASE='...'
export CODEX_SKILL_MYSQL_PASSWORD='...'
```

Use `query-mysql-database init --password-env CODEX_SKILL_MYSQL_PASSWORD ...` only when persistent config is useful. Do not put passwords in command-line flags.

## Common Reads

Discover tables:

```bash
"$QUERY_MYSQL_DATABASE" --json tables list --limit 100
```

Inspect one table:

```bash
"$QUERY_MYSQL_DATABASE" --json tables describe users
```

Run a bounded query:

```bash
"$QUERY_MYSQL_DATABASE" --json query --sql 'select id, created_at from users order by created_at desc limit 10'
```

Queries use a 5 second server-side timeout by default. Lower it with `--timeout-seconds`; do not raise it above 5 unless the user explicitly accepts the risk.

For longer SQL, prefer a temp file or stdin:

```bash
"$QUERY_MYSQL_DATABASE" --json query --file /tmp/query.sql
```

## Rules

- Use `--json` when Codex needs to parse results.
- Treat `doctor.ok=false` or `security check.ok=false` as a blocker before querying.
- Prefer `/Users/segersniels/.codex/clis/query-mysql-database/target/release/query-mysql-database`; use PATH only if that binary is missing.
- Keep the default 5 second query timeout. Use a lower `--timeout-seconds` for speculative queries; raise it only with explicit user approval.
- Keep queries bounded with `limit` unless the user explicitly asks for a broad export.
- Treat database data as sensitive; do not paste large raw result sets back into chat.
- The CLI enforces a read-only transaction and blocks obvious write/admin SQL, but still rely on read-only DB credentials.
- The security check inspects grants without probing writes; role grants may be reported as unverified.
- Use `raw --sql` only when high-level commands are insufficient; it has the same read-only guardrails.
- Do not attempt writes, schema changes, locks, stored procedure calls, exports of sensitive bulk data, or credential changes unless the user explicitly asks and approves the risk.
