use anyhow::{Context, Result, anyhow, bail};
use clap::{Args, Parser, Subcommand, ValueEnum};
use mysql::prelude::Queryable;
use mysql::{Opts, OptsBuilder, Pool, Row, Value};
use serde::{Deserialize, Serialize};
use serde_json::{Map, Number, json};
use std::env;
use std::fs::{self, OpenOptions};
use std::io::{self, Read, Write};
use std::path::PathBuf;
use std::time::Duration;

#[cfg(unix)]
use std::os::unix::fs::OpenOptionsExt;

const DEFAULT_PORT: u16 = 3306;
const ENV_URL: &str = "CODEX_SKILL_MYSQL_URL";
const ENV_HOST: &str = "CODEX_SKILL_MYSQL_HOST";
const ENV_PORT: &str = "CODEX_SKILL_MYSQL_PORT";
const ENV_USER: &str = "CODEX_SKILL_MYSQL_USER";
const ENV_PASSWORD: &str = "CODEX_SKILL_MYSQL_PASSWORD";
const ENV_PASSWORD_ENV: &str = "CODEX_SKILL_MYSQL_PASSWORD_ENV";
const ENV_DATABASE: &str = "CODEX_SKILL_MYSQL_DATABASE";
const ENV_CONFIG: &str = "CODEX_SKILL_MYSQL_CONFIG";
const DEFAULT_QUERY_TIMEOUT_SECONDS: u64 = 5;
const MAX_QUERY_TIMEOUT_SECONDS: u64 = 30;

#[derive(Parser)]
#[command(name = "query-mysql-database")]
#[command(about = "Query a MySQL database through read-only credentials.")]
struct Cli {
    #[arg(
        long,
        global = true,
        help = "Emit JSON for command results and errors."
    )]
    json: bool,

    #[command(flatten)]
    conn: ConnFlags,

    #[command(subcommand)]
    command: Command,
}

#[derive(Args, Clone, Default)]
struct ConnFlags {
    #[arg(long, global = true, env = ENV_URL, hide_env_values = true)]
    url: Option<String>,

    #[arg(long, global = true, env = ENV_HOST, hide_env_values = true)]
    host: Option<String>,

    #[arg(long, global = true, env = ENV_PORT, hide_env_values = true)]
    port: Option<u16>,

    #[arg(long, global = true, env = ENV_USER, hide_env_values = true)]
    user: Option<String>,

    #[arg(long, global = true, env = ENV_PASSWORD_ENV, hide_env_values = true)]
    password_env: Option<String>,

    #[arg(long, global = true, env = ENV_DATABASE, hide_env_values = true)]
    database: Option<String>,

    #[arg(long, global = true, env = ENV_CONFIG, hide_env_values = true)]
    config: Option<PathBuf>,
}

#[derive(Subcommand)]
enum Command {
    #[command(about = "Verify config, credentials, and database reachability.")]
    Doctor,

    #[command(about = "Write ~/.query-mysql-database/config.toml with connection settings.")]
    Init(InitArgs),

    #[command(subcommand, about = "Discover and inspect database tables.")]
    Tables(TablesCommand),

    #[command(subcommand, about = "Check credential safety.")]
    Security(SecurityCommand),

    #[command(about = "Run a read-only SQL query.")]
    Query(QueryArgs),

    #[command(about = "Raw SQL escape hatch, still read-only guarded.")]
    Raw(QueryArgs),
}

#[derive(Args)]
struct InitArgs {
    #[arg(long)]
    host: String,

    #[arg(long, default_value_t = DEFAULT_PORT)]
    port: u16,

    #[arg(long)]
    user: String,

    #[arg(long)]
    database: String,

    #[arg(
        long,
        help = "Store this environment variable name as the password source."
    )]
    password_env: Option<String>,

    #[arg(
        long,
        help = "Read the password from stdin and store it in the 0600 config file."
    )]
    password_stdin: bool,

    #[arg(long, help = "Overwrite an existing config file.")]
    force: bool,
}

#[derive(Subcommand)]
enum TablesCommand {
    #[command(about = "List tables in the configured database.")]
    List {
        #[arg(long, default_value_t = 100)]
        limit: usize,
    },

    #[command(about = "Describe columns for one table.")]
    Describe { table: String },
}

#[derive(Subcommand)]
enum SecurityCommand {
    #[command(about = "Inspect grants and verify credentials look read-only.")]
    Check,
}

#[derive(Args, Clone)]
struct QueryArgs {
    #[arg(long, help = "SQL statement to run.")]
    sql: Option<String>,

    #[arg(long, help = "Read SQL from this file.")]
    file: Option<PathBuf>,

    #[arg(long, value_enum, default_value_t = OutputFormat::Table)]
    format: OutputFormat,

    #[arg(
        long,
        default_value_t = 1000,
        help = "Maximum rows to print client-side."
    )]
    limit: usize,

    #[arg(
        long,
        default_value_t = DEFAULT_QUERY_TIMEOUT_SECONDS,
        value_parser = clap::value_parser!(u64).range(1..=MAX_QUERY_TIMEOUT_SECONDS),
        help = "Server-side statement timeout in seconds."
    )]
    timeout_seconds: u64,
}

#[derive(Copy, Clone, ValueEnum)]
enum OutputFormat {
    Table,
    Json,
    Csv,
    Tsv,
}

#[derive(Debug, Clone, Default, Deserialize, Serialize)]
struct ConfigFile {
    host: Option<String>,
    port: Option<u16>,
    user: Option<String>,
    password: Option<String>,
    password_env: Option<String>,
    database: Option<String>,
}

#[derive(Debug, Clone)]
struct ConnectionConfig {
    url: Option<String>,
    host: Option<String>,
    port: u16,
    user: Option<String>,
    password: Option<String>,
    database: Option<String>,
    source: ConfigSource,
}

#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "snake_case")]
enum ConfigSource {
    EnvUrl,
    EnvParts,
    ConfigFile,
    Flag,
    Missing,
}

#[derive(Debug, Serialize)]
struct Doctor {
    ok: bool,
    config_path: String,
    auth_source: ConfigSource,
    has_url: bool,
    has_host: bool,
    has_user: bool,
    has_password: bool,
    has_database: bool,
    reachable: bool,
    server_version: Option<String>,
    read_only_verified: Option<bool>,
    dangerous_privileges: Vec<String>,
    unverified_grants: Vec<String>,
    missing: Vec<String>,
    error: Option<String>,
}

#[derive(Debug, Serialize)]
struct SecurityReport {
    ok: bool,
    current_user: Option<String>,
    grant_count: usize,
    allowed_privileges: Vec<String>,
    dangerous_privileges: Vec<String>,
    unverified_grants: Vec<String>,
    grants: Vec<String>,
    error: Option<String>,
}

fn main() {
    let cli = Cli::parse();
    if let Err(error) = run(&cli) {
        if cli.json {
            let _ = writeln!(
                io::stdout(),
                "{}",
                json!({
                    "ok": false,
                    "error": {
                        "message": redact(&error.to_string()),
                    }
                })
            );
        } else {
            let _ = writeln!(io::stderr(), "error: {}", redact(&error.to_string()));
        }
        std::process::exit(1);
    }
}

fn run(cli: &Cli) -> Result<()> {
    match &cli.command {
        Command::Doctor => doctor(cli),
        Command::Init(args) => init(cli, args),
        Command::Tables(TablesCommand::List { limit }) => tables_list(cli, *limit),
        Command::Tables(TablesCommand::Describe { table }) => tables_describe(cli, table),
        Command::Security(SecurityCommand::Check) => security_check(cli),
        Command::Query(args) | Command::Raw(args) => query(cli, args),
    }
}

fn config_path(flags: &ConnFlags) -> PathBuf {
    flags.config.clone().unwrap_or_else(|| {
        if let Ok(path) = env::var(ENV_CONFIG) {
            return PathBuf::from(path);
        }
        let home = env::var("HOME").unwrap_or_else(|_| ".".to_string());
        PathBuf::from(home)
            .join(".query-mysql-database")
            .join("config.toml")
    })
}

fn init(cli: &Cli, args: &InitArgs) -> Result<()> {
    if args.password_env.is_some() && args.password_stdin {
        bail!("use either --password-env or --password-stdin, not both");
    }

    let path = config_path(&cli.conn);
    if path.exists() && !args.force {
        bail!(
            "config exists at {}; pass --force to overwrite",
            path.display()
        );
    }

    let password = if args.password_stdin {
        let mut buf = String::new();
        io::stdin()
            .read_to_string(&mut buf)
            .context("failed to read password from stdin")?;
        Some(buf.trim_end_matches(['\r', '\n']).to_string())
    } else {
        None
    };

    let config = ConfigFile {
        host: Some(args.host.clone()),
        port: Some(args.port),
        user: Some(args.user.clone()),
        password,
        password_env: args.password_env.clone(),
        database: Some(args.database.clone()),
    };

    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent)
            .with_context(|| format!("failed to create {}", parent.display()))?;
    }

    let body = toml::to_string_pretty(&config).context("failed to render config")?;
    let mut options = OpenOptions::new();
    options.create(true).write(true).truncate(true);
    #[cfg(unix)]
    options.mode(0o600);
    let mut file = options
        .open(&path)
        .with_context(|| format!("failed to open {}", path.display()))?;
    file.write_all(body.as_bytes())
        .with_context(|| format!("failed to write {}", path.display()))?;

    if cli.json {
        print_json(&json!({
            "ok": true,
            "config_path": path,
            "stored_password": args.password_stdin,
            "password_env": args.password_env,
        }))
    } else {
        println!("wrote {}", path.display());
        if args.password_env.is_some() {
            println!("password source: env");
        } else if args.password_stdin {
            println!("password source: config file");
        } else {
            println!("password source: missing");
        }
        Ok(())
    }
}

fn doctor(cli: &Cli) -> Result<()> {
    let path = config_path(&cli.conn);
    let resolved = resolve_config(&cli.conn)?;
    let missing = missing_fields(&resolved);
    let mut result = Doctor {
        ok: false,
        config_path: path.display().to_string(),
        auth_source: resolved.source.clone(),
        has_url: resolved.url.is_some(),
        has_host: resolved.host.is_some(),
        has_user: resolved.user.is_some(),
        has_password: resolved.password.is_some() || resolved.url.is_some(),
        has_database: resolved.database.is_some() || resolved.url.is_some(),
        reachable: false,
        server_version: None,
        read_only_verified: None,
        dangerous_privileges: Vec::new(),
        unverified_grants: Vec::new(),
        missing,
        error: None,
    };

    if result.missing.is_empty() {
        match connect(&resolved).and_then(|pool| {
            let mut conn = pool.get_conn().context("failed to open connection")?;
            let version: Option<String> = conn.query_first("SELECT VERSION()")?;
            Ok(version)
        }) {
            Ok(version) => {
                result.reachable = true;
                result.server_version = version;
            }
            Err(error) => result.error = Some(redact(&error.to_string())),
        }
        if result.reachable {
            match audit_read_only_grants(&resolved) {
                Ok(report) => {
                    result.read_only_verified = Some(report.ok);
                    result.dangerous_privileges = report.dangerous_privileges;
                    result.unverified_grants = report.unverified_grants;
                }
                Err(error) => {
                    result.read_only_verified = Some(false);
                    result.error = Some(redact(&error.to_string()));
                }
            }
        }
    }

    result.ok =
        result.missing.is_empty() && result.reachable && result.read_only_verified.unwrap_or(false);
    if cli.json {
        print_json(&result)
    } else {
        println!("config: {}", result.config_path);
        println!("auth source: {:?}", result.auth_source);
        println!("has host/url: {}", result.has_host || result.has_url);
        println!("has user: {}", result.has_user || result.has_url);
        println!("has password: {}", result.has_password);
        println!("has database: {}", result.has_database);
        println!("reachable: {}", result.reachable);
        if let Some(read_only_verified) = result.read_only_verified {
            println!("read-only verified: {read_only_verified}");
        }
        if !result.dangerous_privileges.is_empty() {
            println!(
                "dangerous privileges: {}",
                result.dangerous_privileges.join(", ")
            );
        }
        if !result.unverified_grants.is_empty() {
            println!(
                "unverified grants: {}",
                result.unverified_grants.join(" | ")
            );
        }
        if let Some(version) = result.server_version {
            println!("server: {version}");
        }
        if !result.missing.is_empty() {
            println!("missing: {}", result.missing.join(", "));
        }
        if let Some(error) = result.error {
            println!("error: {error}");
        }
        Ok(())
    }
}

fn security_check(cli: &Cli) -> Result<()> {
    let report = audit_read_only_grants(&resolve_config(&cli.conn)?)?;
    if cli.json {
        print_json(&report)
    } else {
        println!("current user: {}", report.current_user.unwrap_or_default());
        println!("read-only verified: {}", report.ok);
        println!("grant count: {}", report.grant_count);
        if !report.allowed_privileges.is_empty() {
            println!(
                "allowed privileges: {}",
                report.allowed_privileges.join(", ")
            );
        }
        if !report.dangerous_privileges.is_empty() {
            println!(
                "dangerous privileges: {}",
                report.dangerous_privileges.join(", ")
            );
        }
        if !report.unverified_grants.is_empty() {
            println!(
                "unverified grants: {}",
                report.unverified_grants.join(" | ")
            );
        }
        Ok(())
    }
}

fn tables_list(cli: &Cli, limit: usize) -> Result<()> {
    let sql = format!(
        "SELECT TABLE_NAME AS table_name FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE() ORDER BY TABLE_NAME LIMIT {}",
        limit
    );
    let rows = run_read_query(
        &resolve_config(&cli.conn)?,
        &sql,
        limit,
        DEFAULT_QUERY_TIMEOUT_SECONDS,
    )?;
    if cli.json {
        print_json(&json!({ "ok": true, "tables": rows }))
    } else {
        print_table(&rows)
    }
}

fn tables_describe(cli: &Cli, table: &str) -> Result<()> {
    validate_identifier(table)?;
    let sql = format!("DESCRIBE `{}`", table.replace('`', "``"));
    let rows = run_read_query(
        &resolve_config(&cli.conn)?,
        &sql,
        10_000,
        DEFAULT_QUERY_TIMEOUT_SECONDS,
    )?;
    if cli.json {
        print_json(&json!({ "ok": true, "table": table, "columns": rows }))
    } else {
        print_table(&rows)
    }
}

fn query(cli: &Cli, args: &QueryArgs) -> Result<()> {
    let sql = read_sql(args)?;
    ensure_read_only_sql(&sql)?;
    let rows = run_read_query(
        &resolve_config(&cli.conn)?,
        &sql,
        args.limit,
        args.timeout_seconds,
    )?;
    let format = if cli.json {
        OutputFormat::Json
    } else {
        args.format
    };
    match format {
        OutputFormat::Json => print_json(&json!({
            "ok": true,
            "row_count": rows.len(),
            "timeout_seconds": args.timeout_seconds,
            "rows": rows,
        })),
        OutputFormat::Csv => print_delimited(&rows, b','),
        OutputFormat::Tsv => print_delimited(&rows, b'\t'),
        OutputFormat::Table => print_table(&rows),
    }
}

fn read_sql(args: &QueryArgs) -> Result<String> {
    match (&args.sql, &args.file) {
        (Some(_), Some(_)) => bail!("use either --sql or --file, not both"),
        (Some(sql), None) => Ok(sql.clone()),
        (None, Some(path)) => fs::read_to_string(path)
            .with_context(|| format!("failed to read SQL from {}", path.display())),
        (None, None) => {
            let mut sql = String::new();
            io::stdin()
                .read_to_string(&mut sql)
                .context("failed to read SQL from stdin")?;
            if sql.trim().is_empty() {
                bail!("provide SQL with --sql, --file, or stdin");
            }
            Ok(sql)
        }
    }
}

fn resolve_config(flags: &ConnFlags) -> Result<ConnectionConfig> {
    let file_config = read_config_file(flags)?;

    let env_url = env::var(ENV_URL).ok();
    let flag_url = flags.url.clone();
    if let Some(url) = flag_url.or(env_url) {
        return Ok(ConnectionConfig {
            url: Some(url),
            host: None,
            port: DEFAULT_PORT,
            user: None,
            password: None,
            database: None,
            source: if flags.url.is_some() {
                if cli_conn_arg_present() {
                    ConfigSource::Flag
                } else {
                    ConfigSource::EnvUrl
                }
            } else {
                ConfigSource::EnvUrl
            },
        });
    }

    let env_has_parts = env::var(ENV_HOST).is_ok()
        || env::var(ENV_USER).is_ok()
        || env::var(ENV_DATABASE).is_ok()
        || env::var(ENV_PASSWORD).is_ok()
        || env::var(ENV_PASSWORD_ENV).is_ok();

    let host = flags
        .host
        .clone()
        .or_else(|| env::var(ENV_HOST).ok())
        .or(file_config.host);
    let port = flags
        .port
        .or_else(|| env::var(ENV_PORT).ok().and_then(|v| v.parse().ok()))
        .or(file_config.port)
        .unwrap_or(DEFAULT_PORT);
    let user = flags
        .user
        .clone()
        .or_else(|| env::var(ENV_USER).ok())
        .or(file_config.user);
    let password_env = flags
        .password_env
        .clone()
        .or_else(|| env::var(ENV_PASSWORD_ENV).ok())
        .or(file_config.password_env);
    let password = env::var(ENV_PASSWORD)
        .ok()
        .or_else(|| password_env.as_ref().and_then(|name| env::var(name).ok()))
        .or(file_config.password);
    let database = flags
        .database
        .clone()
        .or_else(|| env::var(ENV_DATABASE).ok())
        .or(file_config.database);

    let source = if cli_conn_arg_present() {
        ConfigSource::Flag
    } else if env_has_parts {
        ConfigSource::EnvParts
    } else if host.is_some() || user.is_some() || database.is_some() {
        ConfigSource::ConfigFile
    } else {
        ConfigSource::Missing
    };

    Ok(ConnectionConfig {
        url: None,
        host,
        port,
        user,
        password,
        database,
        source,
    })
}

fn cli_conn_arg_present() -> bool {
    let names = [
        "--url",
        "--host",
        "--port",
        "--user",
        "--password-env",
        "--database",
        "--config",
    ];
    env::args().any(|arg| {
        names
            .iter()
            .any(|name| arg == *name || arg.starts_with(&format!("{name}=")))
    })
}

fn read_config_file(flags: &ConnFlags) -> Result<ConfigFile> {
    let path = config_path(flags);
    if !path.exists() {
        return Ok(ConfigFile::default());
    }
    let raw =
        fs::read_to_string(&path).with_context(|| format!("failed to read {}", path.display()))?;
    toml::from_str(&raw).with_context(|| format!("failed to parse {}", path.display()))
}

fn missing_fields(config: &ConnectionConfig) -> Vec<String> {
    if config.url.is_some() {
        return Vec::new();
    }
    let mut missing = Vec::new();
    if config.host.is_none() {
        missing.push("host".to_string());
    }
    if config.user.is_none() {
        missing.push("user".to_string());
    }
    if config.password.is_none() {
        missing.push("password".to_string());
    }
    if config.database.is_none() {
        missing.push("database".to_string());
    }
    missing
}

fn connect(config: &ConnectionConfig) -> Result<Pool> {
    let opts = if let Some(url) = &config.url {
        Opts::from_url(url).context("invalid MySQL URL")?
    } else {
        if !missing_fields(config).is_empty() {
            bail!("missing config: {}", missing_fields(config).join(", "));
        }
        let builder = OptsBuilder::new()
            .ip_or_hostname(config.host.clone())
            .tcp_port(config.port)
            .user(config.user.clone())
            .pass(config.password.clone())
            .db_name(config.database.clone())
            .tcp_connect_timeout(Some(Duration::from_secs(10)));
        Opts::from(builder)
    };
    Pool::new(opts).context("failed to create MySQL pool")
}

fn run_read_query(
    config: &ConnectionConfig,
    sql: &str,
    limit: usize,
    timeout_seconds: u64,
) -> Result<Vec<Map<String, serde_json::Value>>> {
    ensure_read_only_sql(sql)?;
    let pool = connect(config)?;
    let mut conn = pool.get_conn().context("failed to open connection")?;
    apply_query_timeout(&mut conn, timeout_seconds)?;
    conn.query_drop("START TRANSACTION READ ONLY")
        .context("failed to start read-only transaction")?;
    let result = (|| -> Result<Vec<Map<String, serde_json::Value>>> {
        let rows: Vec<Row> = conn.query(sql).with_context(|| {
            format!("query failed or exceeded {timeout_seconds}s statement timeout")
        })?;
        Ok(rows.into_iter().take(limit).map(row_to_json).collect())
    })();
    let rollback = conn.query_drop("ROLLBACK");
    if let Err(error) = rollback {
        return Err(anyhow!("failed to rollback read-only transaction: {error}"));
    }
    result
}

fn apply_query_timeout(conn: &mut mysql::PooledConn, timeout_seconds: u64) -> Result<()> {
    let timeout_ms = timeout_seconds
        .checked_mul(1000)
        .ok_or_else(|| anyhow!("query timeout is too large"))?;
    conn.query_drop(format!("SET SESSION max_execution_time = {timeout_ms}"))
        .with_context(|| format!("failed to set {timeout_seconds}s statement timeout"))
}

fn audit_read_only_grants(config: &ConnectionConfig) -> Result<SecurityReport> {
    let pool = connect(config)?;
    let mut conn = pool.get_conn().context("failed to open connection")?;
    let current_user: Option<String> = conn
        .query_first("SELECT CURRENT_USER()")
        .context("failed to read current user")?;
    let grants: Vec<String> = conn
        .query_map("SHOW GRANTS FOR CURRENT_USER()", |grant: String| grant)
        .context("failed to read grants for current user")?;
    let grant_count = grants.len();
    let (allowed_privileges, dangerous_privileges, unverified_grants) = inspect_grants(&grants);
    let ok = dangerous_privileges.is_empty() && unverified_grants.is_empty() && !grants.is_empty();

    Ok(SecurityReport {
        ok,
        current_user,
        grant_count,
        allowed_privileges,
        dangerous_privileges,
        unverified_grants,
        grants,
        error: None,
    })
}

fn inspect_grants(grants: &[String]) -> (Vec<String>, Vec<String>, Vec<String>) {
    let mut allowed = Vec::new();
    let mut dangerous = Vec::new();
    let mut unverified = Vec::new();

    for grant in grants {
        let upper = grant.to_ascii_uppercase();
        if upper.starts_with("GRANT PROXY ") {
            add_unique(&mut dangerous, "PROXY".to_string());
            continue;
        }
        let Some(rest) = upper.strip_prefix("GRANT ") else {
            unverified.push(grant.clone());
            continue;
        };
        let Some((privileges, _target)) = rest.split_once(" ON ") else {
            unverified.push(grant.clone());
            continue;
        };

        for privilege in privileges.split(',') {
            let privilege = normalize_privilege(privilege);
            if privilege.is_empty() {
                continue;
            }
            if is_allowed_privilege(&privilege) {
                add_unique(&mut allowed, privilege);
            } else {
                add_unique(&mut dangerous, privilege);
            }
        }
    }

    allowed.sort();
    dangerous.sort();
    unverified.sort();
    (allowed, dangerous, unverified)
}

fn normalize_privilege(value: &str) -> String {
    let mut privilege = value.trim().to_string();
    if let Some((name, _columns)) = privilege.split_once('(') {
        privilege = name.trim().to_string();
    }
    privilege
}

fn is_allowed_privilege(privilege: &str) -> bool {
    matches!(privilege, "USAGE" | "SELECT" | "SHOW VIEW" | "SHOW_ROUTINE")
}

fn add_unique(values: &mut Vec<String>, value: String) {
    if !values.contains(&value) {
        values.push(value);
    }
}

fn ensure_read_only_sql(sql: &str) -> Result<()> {
    let trimmed = sql.trim().trim_end_matches(';').trim();
    if trimmed.is_empty() {
        bail!("SQL is empty");
    }
    if trimmed.matches(';').count() > 0 {
        bail!("multiple SQL statements are not allowed");
    }

    let lower = strip_sql_comments(trimmed).to_ascii_lowercase();
    let first = lower.split_whitespace().next().unwrap_or("");
    let allowed = matches!(
        first,
        "select" | "show" | "describe" | "desc" | "explain" | "with"
    );
    if !allowed {
        bail!("only read-only SQL is allowed");
    }

    let blocked = [
        "alter", "analyze", "call", "create", "delete", "drop", "grant", "insert", "kill", "load",
        "lock", "optimize", "replace", "revoke", "set", "truncate", "unlock", "update",
    ];
    for word in blocked {
        if contains_word(&lower, word) {
            bail!("blocked non-read SQL token: {word}");
        }
    }
    Ok(())
}

fn strip_sql_comments(sql: &str) -> String {
    sql.lines()
        .filter(|line| {
            let trimmed = line.trim_start();
            !trimmed.starts_with("--") && !trimmed.starts_with('#')
        })
        .collect::<Vec<_>>()
        .join("\n")
}

fn contains_word(haystack: &str, needle: &str) -> bool {
    haystack
        .split(|c: char| !c.is_ascii_alphanumeric() && c != '_')
        .any(|part| part == needle)
}

fn validate_identifier(value: &str) -> Result<()> {
    let valid = !value.is_empty()
        && value
            .chars()
            .all(|ch| ch.is_ascii_alphanumeric() || ch == '_' || ch == '$');
    if valid {
        Ok(())
    } else {
        bail!("invalid table identifier")
    }
}

fn row_to_json(row: Row) -> Map<String, serde_json::Value> {
    let names: Vec<String> = row
        .columns_ref()
        .iter()
        .map(|column| column.name_str().to_string())
        .collect();
    let values = row.unwrap();
    names
        .into_iter()
        .zip(values)
        .map(|(name, value)| (name, mysql_value_to_json(value)))
        .collect()
}

fn mysql_value_to_json(value: Value) -> serde_json::Value {
    match value {
        Value::NULL => serde_json::Value::Null,
        Value::Bytes(bytes) => {
            serde_json::Value::String(String::from_utf8_lossy(&bytes).into_owned())
        }
        Value::Int(value) => serde_json::Value::Number(Number::from(value)),
        Value::UInt(value) => serde_json::Value::Number(Number::from(value)),
        Value::Float(value) => Number::from_f64(value as f64)
            .map(serde_json::Value::Number)
            .unwrap_or(serde_json::Value::Null),
        Value::Double(value) => Number::from_f64(value)
            .map(serde_json::Value::Number)
            .unwrap_or(serde_json::Value::Null),
        Value::Date(year, month, day, hour, minute, second, micros) => {
            serde_json::Value::String(format!(
                "{year:04}-{month:02}-{day:02} {hour:02}:{minute:02}:{second:02}.{:06}",
                micros
            ))
        }
        Value::Time(negative, days, hours, minutes, seconds, micros) => {
            let sign = if negative { "-" } else { "" };
            serde_json::Value::String(format!(
                "{sign}{days} {hours:02}:{minutes:02}:{seconds:02}.{:06}",
                micros
            ))
        }
    }
}

fn print_json<T: Serialize>(value: &T) -> Result<()> {
    println!("{}", serde_json::to_string_pretty(value)?);
    Ok(())
}

fn print_delimited(rows: &[Map<String, serde_json::Value>], delimiter: u8) -> Result<()> {
    let mut writer = csv::WriterBuilder::new()
        .delimiter(delimiter)
        .from_writer(io::stdout());
    if let Some(first) = rows.first() {
        let headers: Vec<&str> = first.keys().map(String::as_str).collect();
        writer.write_record(&headers)?;
        for row in rows {
            let values: Vec<String> = headers
                .iter()
                .map(|header| cell_to_string(row.get(*header).unwrap_or(&serde_json::Value::Null)))
                .collect();
            writer.write_record(values)?;
        }
    }
    writer.flush()?;
    Ok(())
}

fn print_table(rows: &[Map<String, serde_json::Value>]) -> Result<()> {
    if rows.is_empty() {
        println!("(no rows)");
        return Ok(());
    }
    let headers: Vec<String> = rows[0].keys().cloned().collect();
    let mut widths: Vec<usize> = headers.iter().map(String::len).collect();
    let rendered: Vec<Vec<String>> = rows
        .iter()
        .map(|row| {
            headers
                .iter()
                .enumerate()
                .map(|(index, header)| {
                    let value = cell_to_string(row.get(header).unwrap_or(&serde_json::Value::Null));
                    widths[index] = widths[index].max(value.len());
                    value
                })
                .collect()
        })
        .collect();

    print_row(&headers, &widths);
    println!(
        "{}",
        widths
            .iter()
            .map(|width| "-".repeat(*width))
            .collect::<Vec<_>>()
            .join("-+-")
    );
    for row in rendered {
        print_row(&row, &widths);
    }
    Ok(())
}

fn print_row(cells: &[String], widths: &[usize]) {
    println!(
        "{}",
        cells
            .iter()
            .zip(widths)
            .map(|(cell, width)| format!("{cell:width$}"))
            .collect::<Vec<_>>()
            .join(" | ")
    );
}

fn cell_to_string(value: &serde_json::Value) -> String {
    match value {
        serde_json::Value::Null => "NULL".to_string(),
        serde_json::Value::String(value) => value.clone(),
        other => other.to_string(),
    }
}

fn redact(value: &str) -> String {
    let mut redacted = value.to_string();
    for key in [ENV_PASSWORD, "password"] {
        if let Ok(secret) = env::var(key) {
            if !secret.is_empty() {
                redacted = redacted.replace(&secret, "[redacted]");
            }
        }
    }
    redacted
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn allows_read_statements() {
        ensure_read_only_sql("select 1").unwrap();
        ensure_read_only_sql("SHOW TABLES").unwrap();
        ensure_read_only_sql("describe users").unwrap();
        ensure_read_only_sql("-- comment\nselect * from users").unwrap();
    }

    #[test]
    fn blocks_write_statements() {
        assert!(ensure_read_only_sql("delete from users").is_err());
        assert!(ensure_read_only_sql("select * from users; drop table users").is_err());
        assert!(ensure_read_only_sql("with x as (select 1) update users set name = 'x'").is_err());
    }

    #[test]
    fn validates_table_identifiers() {
        validate_identifier("users_2026").unwrap();
        assert!(validate_identifier("users;drop").is_err());
    }

    #[test]
    fn accepts_select_only_grants() {
        let grants = vec![
            "GRANT USAGE ON *.* TO `reader`@`%`".to_string(),
            "GRANT SELECT, SHOW VIEW, SHOW_ROUTINE ON `production`.* TO `reader`@`%`".to_string(),
        ];

        let (_allowed, dangerous, unverified) = inspect_grants(&grants);

        assert!(dangerous.is_empty());
        assert!(unverified.is_empty());
    }

    #[test]
    fn flags_write_grants() {
        let grants =
            vec!["GRANT SELECT, INSERT, UPDATE ON `production`.* TO `reader`@`%`".to_string()];

        let (_allowed, dangerous, unverified) = inspect_grants(&grants);

        assert_eq!(dangerous, vec!["INSERT".to_string(), "UPDATE".to_string()]);
        assert!(unverified.is_empty());
    }

    #[test]
    fn flags_role_grants_as_unverified() {
        let grants = vec!["GRANT `app_readonly`@`%` TO `reader`@`%`".to_string()];

        let (_allowed, dangerous, unverified) = inspect_grants(&grants);

        assert!(dangerous.is_empty());
        assert_eq!(unverified, grants);
    }
}
