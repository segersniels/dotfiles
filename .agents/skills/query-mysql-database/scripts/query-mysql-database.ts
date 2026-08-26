#!/usr/bin/env bun

import { parseArgs } from "node:util";
import { SQL } from "bun";

const DEFAULT_TIMEOUT_SECONDS = 5;
const DEFAULT_ROW_LIMIT = 1_000;
const ALLOWED_PRIVILEGES = new Set([
  "SELECT",
  "SHOW ROUTINE",
  "SHOW VIEW",
  "SHOW_ROUTINE",
  "USAGE",
]);

const HELP = `Usage:
  bun run scripts/query-mysql-database.ts check
  bun run scripts/query-mysql-database.ts query --sql <SQL> [--limit <rows>] [--timeout-seconds <seconds>]
  bun run scripts/query-mysql-database.ts query --file <path> [--limit <rows>] [--timeout-seconds <seconds>]

Commands:
  check  Verify the selected database, account, and read-only grants.
  query  Run one read-only statement in a read-only transaction.

Environment:
  AGENT_MYSQL_HOST
  AGENT_MYSQL_PORT       Optional. Defaults to 3306.
  AGENT_MYSQL_USER
  AGENT_MYSQL_DATABASE
  AGENT_MYSQL_PASSWORD

Output is JSON. Errors exit with status 1.`;

type Row = Record<string, unknown>;

type Config = {
  hostname: string;
  port: number;
  username: string;
  database: string;
  password: string;
};

type Audit = {
  ok: boolean;
  current_user: string;
  database: string;
  server_version: string;
  grants: string[];
  allowed_privileges: string[];
  dangerous_privileges: string[];
  unverified_grants: string[];
};

function printJson(value: unknown): void {
  console.log(
    JSON.stringify(
      value,
      (_key, item) => (typeof item === "bigint" ? item.toString() : item),
      2,
    ),
  );
}

function fail(message: string): never {
  const password = process.env.AGENT_MYSQL_PASSWORD;
  const safeMessage = password ? message.replaceAll(password, "[REDACTED]") : message;
  printJson({ ok: false, error: { message: safeMessage } });
  process.exit(1);
}

function positiveInteger(value: string | undefined, fallback: number, name: string): number {
  if (value === undefined) return fallback;

  const parsed = Number(value);
  if (!Number.isSafeInteger(parsed) || parsed < 1) {
    fail(`${name} must be a positive integer`);
  }

  return parsed;
}

function loadConfig(): Config {
  const required = [
    "AGENT_MYSQL_HOST",
    "AGENT_MYSQL_USER",
    "AGENT_MYSQL_DATABASE",
    "AGENT_MYSQL_PASSWORD",
  ] as const;
  const missing = required.filter((name) => !process.env[name]);
  if (missing.length > 0) {
    fail(`missing environment variables: ${missing.join(", ")}`);
  }

  const port = positiveInteger(process.env.AGENT_MYSQL_PORT, 3306, "AGENT_MYSQL_PORT");
  if (port > 65_535) {
    fail("AGENT_MYSQL_PORT must be at most 65535");
  }

  return {
    hostname: process.env.AGENT_MYSQL_HOST!,
    port,
    username: process.env.AGENT_MYSQL_USER!,
    database: process.env.AGENT_MYSQL_DATABASE!,
    password: process.env.AGENT_MYSQL_PASSWORD!,
  };
}

function inspectGrants(grants: string[]): Pick<
  Audit,
  "allowed_privileges" | "dangerous_privileges" | "unverified_grants"
> {
  const allowed = new Set<string>();
  const dangerous = new Set<string>();
  const unverified: string[] = [];

  for (const grant of grants) {
    const normalized = grant.toUpperCase().replace(/\s+/g, " ").trim();
    const match = normalized.match(/^GRANT (.+) ON .+ TO /);
    if (!match) {
      unverified.push(grant);

      continue;
    }

    for (const privilege of match[1]!.split(",").map((value) => value.trim())) {
      (ALLOWED_PRIVILEGES.has(privilege) ? allowed : dangerous).add(privilege);
    }

    if (normalized.includes(" WITH GRANT OPTION")) {
      dangerous.add("GRANT OPTION");
    }
  }

  return {
    allowed_privileges: [...allowed].sort(),
    dangerous_privileges: [...dangerous].sort(),
    unverified_grants: unverified.sort(),
  };
}

async function audit(connection: Awaited<ReturnType<SQL["reserve"]>>): Promise<Audit> {
  const [identity] = (await connection`
    SELECT
      CURRENT_USER() AS authenticated_user,
      DATABASE() AS database_name,
      VERSION() AS server_version
  `) as Row[];

  if (!identity) {
    throw new Error("database returned no identity information");
  }

  const grantRows = (await connection`SHOW GRANTS FOR CURRENT_USER()`) as Row[];
  const grants = grantRows.map((row) => String(Object.values(row)[0] ?? ""));
  const inspected = inspectGrants(grants);

  return {
    ok:
      grants.length > 0 &&
      inspected.dangerous_privileges.length === 0 &&
      inspected.unverified_grants.length === 0,
    current_user: String(identity.authenticated_user ?? ""),
    database: String(identity.database_name ?? ""),
    server_version: String(identity.server_version ?? ""),
    grants,
    ...inspected,
  };
}

function ensureReadOnly(sql: string): string {
  const statement = sql.trim().replace(/;\s*$/, "").trim();
  if (!statement) {
    fail("SQL is empty");
  }

  if (statement.includes(";") || /--|#|\/\*/.test(statement)) {
    fail("SQL must be one statement without comments");
  }

  const words = statement.toLowerCase().match(/[a-z_]+/g) ?? [];
  if (!["select", "show", "describe", "desc", "explain", "with"].includes(words[0] ?? "")) {
    fail("only read-only SQL is allowed");
  }

  const blocked = new Set([
    "alter",
    "analyze",
    "call",
    "create",
    "delete",
    "drop",
    "dumpfile",
    "grant",
    "insert",
    "kill",
    "load",
    "lock",
    "optimize",
    "outfile",
    "replace",
    "revoke",
    "set",
    "truncate",
    "unlock",
    "update",
  ]);
  const blockedWord = words.find((word) => blocked.has(word));
  if (blockedWord) {
    fail(`blocked non-read SQL token: ${blockedWord}`);
  }

  return statement;
}

async function main(): Promise<void> {
  let parsed: ReturnType<typeof parseArgs>;
  try {
    parsed = parseArgs({
      args: Bun.argv.slice(2),
      allowPositionals: true,
      strict: true,
      options: {
        help: { type: "boolean", short: "h" },
        sql: { type: "string" },
        file: { type: "string" },
        limit: { type: "string" },
        "timeout-seconds": { type: "string" },
      },
    });
  } catch (error) {
    fail(error instanceof Error ? error.message : String(error));
  }

  if (parsed.values.help) {
    console.log(HELP);

    return;
  }

  const command = parsed.positionals[0];
  if (!command || !["check", "query"].includes(command)) {
    fail("command must be check or query; use --help for usage");
  }

  if (parsed.positionals.length > 1) {
    fail("unexpected positional arguments");
  }

  const config = loadConfig();
  const database = new SQL({
    adapter: "mysql",
    ...config,
    max: 1,
    connectionTimeout: 10,
  });
  const connection = await database.reserve({ signal: AbortSignal.timeout(10_000) });

  try {
    const report = await audit(connection);
    if (command === "check") {
      printJson(report);

      if (!report.ok) {
        process.exitCode = 1;
      }

      return;
    }

    if (!report.ok) {
      printJson({ ...report, error: { message: "credentials are not verified read-only" } });
      process.exitCode = 1;

      return;
    }

    if (Boolean(parsed.values.sql) === Boolean(parsed.values.file)) {
      fail("query requires exactly one of --sql or --file");
    }

    const input = parsed.values.sql ?? (await Bun.file(parsed.values.file!).text());
    const statement = ensureReadOnly(input);
    const limit = positiveInteger(parsed.values.limit, DEFAULT_ROW_LIMIT, "--limit");
    const timeoutSeconds = positiveInteger(
      parsed.values["timeout-seconds"],
      DEFAULT_TIMEOUT_SECONDS,
      "--timeout-seconds",
    );

    if (timeoutSeconds > 30) {
      fail("--timeout-seconds must be at most 30");
    }

    await connection.unsafe(`SET SESSION max_execution_time = ${timeoutSeconds * 1_000}`);
    await connection.unsafe("START TRANSACTION READ ONLY");
    try {
      const rows = (await connection.unsafe(statement)) as Row[];
      printJson({
        ok: true,
        database: report.database,
        current_user: report.current_user,
        row_count: Math.min(rows.length, limit),
        truncated: rows.length > limit,
        rows: rows.slice(0, limit),
      });
    } finally {
      await connection.unsafe("ROLLBACK");
    }
  } finally {
    connection.release();
    await database.close();
  }
}

main().catch((error) => {
  fail(error instanceof Error ? error.message : String(error));
});
