# query-mysql-database

Read-only CLI for MySQL database investigations.

## Install

```bash
make install-local
```

This installs `query-mysql-database` into `~/.local/bin`.

## Configure

Prefer environment variables:

```bash
export CODEX_SKILL_MYSQL_HOST='example.mysql.host'
export CODEX_SKILL_MYSQL_PORT='3306'
export CODEX_SKILL_MYSQL_USER='readonly_user'
export CODEX_SKILL_MYSQL_DATABASE='production'
export CODEX_SKILL_MYSQL_PASSWORD='...'
```

Or use a URL:

```bash
export CODEX_SKILL_MYSQL_URL='mysql://readonly_user:password@example.mysql.host:3306/production'
```

Or write a private config file:

```bash
query-mysql-database init --host example.mysql.host --user readonly_user --database production --password-env CODEX_SKILL_MYSQL_PASSWORD
```

Config path: `~/.query-mysql-database/config.toml`.

## Commands

```bash
query-mysql-database --json doctor
query-mysql-database --json security check
query-mysql-database --json tables list --limit 50
query-mysql-database --json tables describe users
query-mysql-database query --sql 'select id, email from users limit 10' --format table
query-mysql-database --json query --sql 'select count(*) as count from users'
query-mysql-database --json query --timeout-seconds 3 --sql 'select 1 as ok'
cat query.sql | query-mysql-database query --format csv
```

## JSON Policy

`--json` writes JSON to stdout only.

Success shape:

```json
{
  "ok": true,
  "row_count": 1,
  "timeout_seconds": 5,
  "rows": [{ "count": 123 }]
}
```

Error shape:

```json
{
  "ok": false,
  "error": { "message": "blocked non-read SQL token: update" }
}
```

Credentials are not intentionally printed. Do not pass passwords as command-line flags.

## Guardrails

The CLI is meant for read-only credentials. It also:

- Starts every live query with `START TRANSACTION READ ONLY`.
- Sets `SESSION max_execution_time` before each read query. Default: 5 seconds. Max override: 30 seconds.
- Checks grants with `SHOW GRANTS FOR CURRENT_USER()` in `doctor` and `security check`.
- Rejects multiple statements.
- Allows `select`, `show`, `describe`, `desc`, `explain`, and `with`.
- Blocks obvious write/admin tokens before sending SQL.
- Treats role grants as unverified unless their concrete privileges are visible.

These guardrails do not replace database-level read-only permissions.
