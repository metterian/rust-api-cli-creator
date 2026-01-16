#!/usr/bin/env python3
"""
Rust API CLI Project Initializer

Creates a new Rust CLI project with proper structure for API wrappers,
including Claude Code skill integration.

Usage:
    init_rust_cli.py <cli-name> --api-name <ApiName> --path <output-dir>

Examples:
    init_rust_cli.py notion-cli --api-name Notion --path ~/projects
    init_rust_cli.py stripe-cli --api-name Stripe --path .
"""

import sys
from pathlib import Path

# Template: Cargo.toml
CARGO_TOML = '''[package]
name = "{cli_name}"
version = "0.1.0"
edition = "2021"
rust-version = "1.75.0"
license = "MIT"
description = "CLI for {api_name} API"

[dependencies]
# CLI parsing
clap = {{ version = "4.5", features = ["derive", "env"] }}

# Async runtime
tokio = {{ version = "1", features = ["full"] }}

# HTTP client
reqwest = {{ version = "0.12", features = ["json", "stream"] }}

# Serialization
serde = {{ version = "1", features = ["derive"] }}
serde_json = "1"

# Config management
toml = "0.8"
dirs = "5"
dotenvy = "0.15"

# Error handling
anyhow = "1"

# Logging
tracing = "0.1"
tracing-subscriber = {{ version = "0.3", features = ["env-filter"] }}

# Streaming
futures = "0.3"

[profile.release]
opt-level = 3
lto = true
codegen-units = 1
strip = true
'''

# Template: main.rs
MAIN_RS = '''mod cli;
mod config;
mod format;
mod {api_module};

use anyhow::{{Context, Result}};
use clap::Parser;
use cli::{{Cli, Command, ConfigAction}};
use std::io::{{self, Write}};

#[tokio::main]
async fn main() -> Result<()> {{
    let cli = Cli::parse();

    let level = if cli.verbose {{ "debug" }} else {{ "warn" }};
    tracing_subscriber::fmt()
        .with_env_filter(level)
        .with_writer(std::io::stderr)
        .compact()
        .with_target(false)
        .init();

    if let Command::Config {{ action }} = &cli.command {{
        return handle_config_action(action, cli.json);
    }}

    dotenvy::dotenv().ok();

    let config = config::Config::load(cli.config, cli.api_key)?;
    let client = {api_module}::Client::new(&config)?;

    match cli.command {{
        Command::Get {{ id, format }} => {{
            let result = client.get(&id).await?;
            format::print_result(&result, cli.json, format);
        }}
        Command::Search {{ query, limit, all }} => {{
            // TODO: Implement streaming with --all flag
            // See references/rust-cli-patterns.md for pagination patterns
            if cli.stream {{
                eprintln!("Streaming not yet implemented. Use --json for now.");
            }}
            if all {{
                // TODO: Implement paginated fetch with search_all()
                eprintln!("--all pagination not yet implemented.");
            }}
            let results = client.search(&query, limit).await?;
            format::print_results(&results, cli.json);
        }}
        Command::Config {{ .. }} => unreachable!(),
    }}

    Ok(())
}}

fn handle_config_action(action: &ConfigAction, as_json: bool) -> Result<()> {{
    match action {{
        ConfigAction::Init {{ api_key, force }} => init_config(api_key.clone(), *force),
        ConfigAction::Show => {{
            let config = config::Config::load(None, None)?;
            config.show_masked(as_json)
        }}
        ConfigAction::Path => {{
            let path = config::Config::default_config_path()
                .context("Cannot determine config path")?;
            println!("{{}}", path.display());
            Ok(())
        }}
        ConfigAction::Edit => config::Config::edit_config(),
    }}
}}

fn init_config(api_key: Option<String>, force: bool) -> Result<()> {{
    let path = config::Config::default_config_path()
        .context("Cannot determine config path")?;

    if path.exists() && !force {{
        anyhow::bail!("Config exists: {{}}\\nUse --force to overwrite", path.display());
    }}

    let api_key = match api_key {{
        Some(k) => k,
        None => {{
            print!("API key: ");
            io::stdout().flush()?;
            let mut input = String::new();
            io::stdin().read_line(&mut input)?;
            input.trim().to_string()
        }}
    }};

    if api_key.is_empty() {{
        anyhow::bail!("API key cannot be empty");
    }}

    let config = config::Config {{
        api_key: Some(api_key),
        ..Default::default()
    }};

    if let Some(parent) = path.parent() {{
        std::fs::create_dir_all(parent)?;
    }}
    let content = toml::to_string_pretty(&config)?;
    std::fs::write(&path, content)?;

    #[cfg(unix)]
    {{
        use std::os::unix::fs::PermissionsExt;
        let mut perms = std::fs::metadata(&path)?.permissions();
        perms.set_mode(0o600);
        std::fs::set_permissions(&path, perms)?;
    }}

    println!("Config saved: {{}}", path.display());
    Ok(())
}}
'''

# Template: cli.rs
CLI_RS = '''use clap::{{Parser, Subcommand, ValueEnum}};
use std::path::PathBuf;

#[derive(Parser)]
#[command(name = "{cli_name}", version, about = "CLI for {api_name} API", author)]
pub struct Cli {{
    #[command(subcommand)]
    pub command: Command,

    #[arg(long, env = "{env_var}", global = true, hide_env_values = true)]
    pub api_key: Option<String>,

    #[arg(long, short, global = true)]
    pub config: Option<PathBuf>,

    #[arg(long, short, global = true, help = "Output as JSON")]
    pub json: bool,

    #[arg(long, short, global = true, help = "Enable verbose output")]
    pub verbose: bool,

    #[arg(long, global = true, help = "Stream response in real-time")]
    pub stream: bool,
}}

#[derive(Subcommand)]
pub enum Command {{
    #[command(about = "Get an item by ID")]
    Get {{
        #[arg(help = "Item ID")]
        id: String,

        #[arg(long, value_enum, default_value = "json")]
        format: OutputFormat,
    }},

    #[command(about = "Search for items")]
    Search {{
        #[arg(help = "Search query")]
        query: String,

        #[arg(long, short, default_value = "20")]
        limit: u32,

        #[arg(long, help = "Fetch all results")]
        all: bool,
    }},

    #[command(about = "Configuration management")]
    Config {{
        #[command(subcommand)]
        action: ConfigAction,
    }},
}}

#[derive(Subcommand)]
pub enum ConfigAction {{
    #[command(about = "Initialize configuration")]
    Init {{
        #[arg(long)]
        api_key: Option<String>,
        #[arg(long)]
        force: bool,
    }},
    #[command(about = "Show current configuration")]
    Show,
    #[command(about = "Show configuration file path")]
    Path,
    #[command(about = "Edit configuration")]
    Edit,
}}

#[derive(ValueEnum, Clone, Copy, Debug, Default)]
pub enum OutputFormat {{
    #[default]
    Json,
    Table,
    Markdown,
}}
'''

# Template: config.rs
CONFIG_RS = '''use anyhow::{{Context, Result}};
use serde::{{Deserialize, Serialize}};
use std::path::PathBuf;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Config {{
    #[serde(skip_serializing_if = "Option::is_none")]
    pub api_key: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub domain: Option<String>,

    #[serde(default)]
    pub defaults: Defaults,
}}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Defaults {{
    #[serde(default = "default_limit")]
    pub limit: u32,
}}

fn default_limit() -> u32 {{
    20
}}

impl Config {{
    /// Load config with 4-tier priority:
    /// 1. CLI flags (passed as parameters)
    /// 2. Environment variables
    /// 3. Project config (./{cli_name}.toml in current directory)
    /// 4. Global config (~/.config/{cli_name}/config.toml)
    pub fn load(
        config_path: Option<PathBuf>,
        api_key_override: Option<String>,
    ) -> Result<Self> {{
        // Determine config path with priority: explicit > project > global
        let path = config_path.unwrap_or_else(|| {{
            let project_config = PathBuf::from("./{cli_name}.toml");
            if project_config.exists() {{
                project_config
            }} else {{
                Self::default_config_path().unwrap_or_else(|| PathBuf::from("config.toml"))
            }}
        }});

        let mut config = if path.exists() {{
            let content = std::fs::read_to_string(&path)
                .with_context(|| format!("Failed to read config: {{}}", path.display()))?;
            toml::from_str(&content)
                .with_context(|| format!("Failed to parse config: {{}}", path.display()))?
        }} else {{
            Config::default()
        }};

        // CLI flag override (highest priority)
        if let Some(key) = api_key_override {{
            config.api_key = Some(key);
        }}

        // Environment variable fallback
        if config.api_key.is_none() {{
            config.api_key = std::env::var("{env_var}").ok();
        }}

        Ok(config)
    }}

    pub fn default_config_path() -> Option<PathBuf> {{
        dirs::config_dir().map(|p| p.join("{cli_name}").join("config.toml"))
    }}

    pub fn show_masked(&self, as_json: bool) -> Result<()> {{
        let masked = Config {{
            api_key: self.api_key.as_ref().map(|k| mask_key(k)),
            domain: self.domain.clone(),
            defaults: self.defaults.clone(),
        }};

        if as_json {{
            println!("{{}}", serde_json::to_string_pretty(&masked)?);
        }} else {{
            println!("{{}}", toml::to_string_pretty(&masked)?);
        }}
        Ok(())
    }}

    pub fn edit_config() -> Result<()> {{
        let path = Self::default_config_path().context("Cannot determine config path")?;

        if !path.exists() {{
            anyhow::bail!("Config not found: {{}}\\nRun '{cli_name} config init' first", path.display());
        }}

        let editor = std::env::var("EDITOR").unwrap_or_else(|_| "vim".to_string());
        std::process::Command::new(&editor)
            .arg(&path)
            .status()
            .with_context(|| format!("Failed to open editor: {{}}", editor))?;

        Ok(())
    }}

    pub fn get_api_key(&self) -> Result<&str> {{
        self.api_key
            .as_deref()
            .context("API key not configured. Run '{cli_name} config init' or set {env_var}")
    }}
}}

fn mask_key(key: &str) -> String {{
    if key.len() <= 8 {{
        "*".repeat(key.len())
    }} else {{
        format!("{{}}...{{}}", &key[..4], &key[key.len() - 4..])
    }}
}}
'''

# Template: format.rs
FORMAT_RS = '''use crate::cli::OutputFormat;
use serde::Serialize;
use serde_json::Value;

pub fn print_result<T: Serialize>(result: &T, as_json: bool, _format: OutputFormat) {{
    if as_json {{
        match serde_json::to_string_pretty(result) {{
            Ok(json) => println!("{{}}", json),
            Err(e) => eprintln!("Error serializing result: {{}}", e),
        }}
    }} else {{
        match serde_json::to_value(result) {{
            Ok(value) => print_value(&value, 0),
            Err(e) => eprintln!("Error converting result: {{}}", e),
        }}
    }}
}}

pub fn print_results<T: Serialize>(results: &[T], as_json: bool) {{
    if as_json {{
        match serde_json::to_string_pretty(results) {{
            Ok(json) => println!("{{}}", json),
            Err(e) => eprintln!("Error serializing results: {{}}", e),
        }}
    }} else {{
        for result in results {{
            if let Ok(value) = serde_json::to_value(result) {{
                print_value(&value, 0);
                println!();
            }}
        }}
    }}
}}

fn print_value(value: &Value, indent: usize) {{
    let prefix = "  ".repeat(indent);
    match value {{
        Value::Object(map) => {{
            for (key, val) in map {{
                print!("{{}}{{}}: ", prefix, key);
                match val {{
                    Value::Object(_) | Value::Array(_) => {{
                        println!();
                        print_value(val, indent + 1);
                    }}
                    _ => println!("{{}}", format_scalar(val)),
                }}
            }}
        }}
        Value::Array(arr) => {{
            for item in arr {{
                println!("{{}}- ", prefix);
                print_value(item, indent + 1);
            }}
        }}
        _ => println!("{{}}{{}}", prefix, format_scalar(value)),
    }}
}}

fn format_scalar(value: &Value) -> String {{
    match value {{
        Value::String(s) => s.clone(),
        Value::Number(n) => n.to_string(),
        Value::Bool(b) => b.to_string(),
        Value::Null => "null".to_string(),
        _ => value.to_string(),
    }}
}}
'''

# Template: lib.rs
LIB_RS = '''pub mod cli;
pub mod config;
pub mod format;
pub mod {api_module};
'''

# Template: API module mod.rs
API_MOD_RS = '''mod client;
mod types;

pub use client::Client;
pub use types::*;
'''

# Template: API client.rs
API_CLIENT_RS = '''use anyhow::{{Context, Result}};
use reqwest::header::{{HeaderMap, HeaderValue, AUTHORIZATION, CONTENT_TYPE}};
use serde_json::Value;
use crate::config::Config;

pub struct Client {{
    http: reqwest::Client,
    base_url: String,
}}

impl Client {{
    pub fn new(config: &Config) -> Result<Self> {{
        let api_key = config.get_api_key()?;

        let mut headers = HeaderMap::new();
        headers.insert(
            AUTHORIZATION,
            HeaderValue::from_str(&format!("Bearer {{}}", api_key))
                .context("Invalid API key format")?,
        );
        headers.insert(CONTENT_TYPE, HeaderValue::from_static("application/json"));

        let http = reqwest::Client::builder()
            .default_headers(headers)
            .timeout(std::time::Duration::from_secs(30))
            .build()?;

        let base_url = config.domain
            .as_deref()
            .unwrap_or("https://api.example.com")
            .to_string();

        Ok(Self {{ http, base_url }})
    }}

    pub async fn get(&self, id: &str) -> Result<Value> {{
        let url = format!("{{}}/items/{{}}", self.base_url, id);
        let response = self.http.get(&url).send().await?;
        self.handle_response(response).await
    }}

    pub async fn search(&self, query: &str, limit: u32) -> Result<Vec<Value>> {{
        let url = format!("{{}}/search", self.base_url);
        let response = self.http
            .get(&url)
            .query(&[("q", query), ("limit", &limit.to_string())])
            .send()
            .await?;

        let data = self.handle_response(response).await?;
        Ok(data["results"].as_array().cloned().unwrap_or_default())
    }}

    async fn handle_response(&self, response: reqwest::Response) -> Result<Value> {{
        let status = response.status();
        let text = response.text().await?;

        if !status.is_success() {{
            anyhow::bail!("API error ({{}}): {{}}", status, text);
        }}

        serde_json::from_str(&text).context("Failed to parse response")
    }}
}}
'''

# Template: API types.rs
API_TYPES_RS = '''use serde::{{Deserialize, Serialize}};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Item {{
    pub id: String,
    pub name: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub description: Option<String>,
}}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SearchResult {{
    pub items: Vec<Item>,
    pub total: u32,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub next_cursor: Option<String>,
}}
'''

# Template: SKILL.md
SKILL_MD = '''---
name: {cli_name}
description: |
  CLI for {api_name} API operations.
  Use when: (1) {api_name} API queries, (2) {api_name} data retrieval, (3) {api_name} automation.
  Commands: get (fetch item), search (query items), config (manage settings).
allowed-tools: Bash
---

# {cli_name}

CLI for {api_name} API.

## Commands

```bash
# Get item by ID
{cli_name} get <id> --format json

# Search
{cli_name} search "query" --limit 20

# Search with JSON output (for parsing)
{cli_name} search "query" --json | jq '.[0].id'
```

## Options

| Option | Description |
|--------|-------------|
| `--json` | Output as JSON |
| `--format` | Output format: json, table, markdown |
| `--limit N` | Maximum results |
| `--stream` | Real-time streaming |

## Configuration

```bash
# Initialize config
{cli_name} config init

# Show config (API key masked)
{cli_name} config show
```

Environment variable: `{env_var}`
'''

# Template: CLAUDE.md
CLAUDE_MD = '''# {api_name} CLI - AI Agent Guide

## Project Structure

```
src/
├── main.rs          # CLI entry, command dispatch
├── cli.rs           # Clap command definitions
├── config.rs        # 4-tier config: CLI > ENV > project > global
├── format.rs        # Output formatting (JSON/table)
└── {api_module}/
    ├── mod.rs       # Module exports
    ├── client.rs    # HTTP client, API methods
    └── types.rs     # Data structures
```

## Key Patterns

### Config Priority Chain
```rust
// CLI flag > ENV var > config file
let api_key = cli_api_key
    .or_else(|| env::var("{env_var}").ok())
    .or_else(|| file_config.api_key);
```

### Adding Commands

1. `cli.rs`: Add variant to `Command` enum
2. `main.rs`: Add match arm
3. `{api_module}/client.rs`: Implement async method

## Testing

```bash
cargo test
cargo clippy && cargo fmt
```
'''


def to_snake_case(name: str) -> str:
    """Convert hyphenated name to snake_case for Rust modules."""
    return name.replace('-', '_')


def to_env_var(name: str) -> str:
    """Convert CLI name to environment variable format."""
    return name.upper().replace('-', '_') + '_API_KEY'


def extract_api_module_name(cli_name: str) -> str:
    """Extract API module name from CLI name.

    Examples:
        github-cli -> github
        notion-api-cli -> notion_api
        stripe-cli -> stripe
        my-awesome-tool -> my_awesome_tool
    """
    # Remove -cli suffix if present (only at the end)
    if cli_name.endswith('-cli'):
        base_name = cli_name[:-4]  # Remove last 4 chars '-cli'
    else:
        base_name = cli_name
    return to_snake_case(base_name)


def init_rust_cli(cli_name: str, api_name: str, path: str) -> Path | None:
    """
    Initialize a new Rust CLI project.

    Args:
        cli_name: Name of the CLI (hyphen-case)
        api_name: Name of the API (PascalCase)
        path: Output directory path

    Returns:
        Path to created project, or None if error
    """
    project_dir = Path(path).resolve() / cli_name
    api_module = extract_api_module_name(cli_name)
    env_var = to_env_var(cli_name)

    if project_dir.exists():
        print(f"Error: Directory already exists: {project_dir}")
        return None

    try:
        # Create directory structure
        (project_dir / 'src' / api_module).mkdir(parents=True)
        (project_dir / '.claude' / 'skills' / cli_name).mkdir(parents=True)

        # Template variables
        vars = {
            'cli_name': cli_name,
            'api_name': api_name,
            'api_module': api_module,
            'env_var': env_var,
        }

        # Write files
        files = {
            'Cargo.toml': CARGO_TOML,
            'src/main.rs': MAIN_RS,
            'src/lib.rs': LIB_RS,
            'src/cli.rs': CLI_RS,
            'src/config.rs': CONFIG_RS,
            'src/format.rs': FORMAT_RS,
            f'src/{api_module}/mod.rs': API_MOD_RS,
            f'src/{api_module}/client.rs': API_CLIENT_RS,
            f'src/{api_module}/types.rs': API_TYPES_RS,
            f'.claude/skills/{cli_name}/SKILL.md': SKILL_MD,
            'CLAUDE.md': CLAUDE_MD,
        }

        for file_path, template in files.items():
            full_path = project_dir / file_path
            content = template.format(**vars)
            full_path.write_text(content)
            print(f"  Created {file_path}")

        print(f"\nProject initialized: {project_dir}")
        print("\nNext steps:")
        print(f"  1. cd {project_dir}")
        print("  2. Update src/{api_module}/client.rs with actual API endpoints")
        print("  3. Update .claude/skills/{cli_name}/SKILL.md with command examples")
        print("  4. cargo build")

        return project_dir

    except Exception as e:
        print(f"Error: {e}")
        return None


def main():
    if len(sys.argv) < 6 or '--api-name' not in sys.argv or '--path' not in sys.argv:
        print("Usage: init_rust_cli.py <cli-name> --api-name <ApiName> --path <output-dir>")
        print("\nExamples:")
        print("  init_rust_cli.py notion-cli --api-name Notion --path ~/projects")
        print("  init_rust_cli.py github-cli --api-name GitHub --path .")
        sys.exit(1)

    cli_name = sys.argv[1]
    api_name_idx = sys.argv.index('--api-name') + 1
    path_idx = sys.argv.index('--path') + 1

    api_name = sys.argv[api_name_idx]
    path = sys.argv[path_idx]

    print(f"Initializing {cli_name} for {api_name} API...")
    print(f"Location: {path}\n")

    result = init_rust_cli(cli_name, api_name, path)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
