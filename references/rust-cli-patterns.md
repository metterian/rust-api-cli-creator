# Rust CLI Patterns Reference

Complete code templates extracted from perplexity-cli, atlassian-cli, and slack-cli.

## Table of Contents

1. [Cargo.toml Template](#cargotoml-template)
2. [main.rs Template](#mainrs-template)
3. [cli.rs Template](#clirs-template)
4. [config.rs Template](#configrs-template)
5. [API Client Template](#api-client-template)
6. [format.rs Template](#formatrs-template)
7. [HTTP Client Pattern](#http-client-pattern)
8. [Streaming Pattern](#streaming-pattern)
9. [Pagination Pattern](#pagination-pattern)

---

## Cargo.toml Template

```toml
[package]
name = "{cli-name}"
version = "0.1.0"
edition = "2021"
rust-version = "1.75.0"
license = "MIT"
description = "CLI for {API Name}"

[dependencies]
# CLI parsing
clap = { version = "4.5", features = ["derive", "env"] }

# Async runtime
tokio = { version = "1", features = ["full"] }

# HTTP client
reqwest = { version = "0.12", features = ["json", "stream"] }

# Serialization
serde = { version = "1", features = ["derive"] }
serde_json = "1"

# Config management
toml = "0.8"
dirs = "5"
dotenvy = "0.15"

# Error handling
anyhow = "1"
thiserror = "2"

# Logging
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter"] }

# Streaming (optional)
futures = "0.3"

# Rate limiting (optional, for API safety)
governor = "0.8"

# Base64 encoding (for Basic auth)
base64 = "0.22"

[profile.release]
opt-level = 3
lto = true
codegen-units = 1
strip = true
```

---

## main.rs Template

```rust
mod cli;
mod config;
mod format;
mod {api_module};

use anyhow::{Context, Result};
use clap::Parser;
use cli::{Cli, Command, ConfigAction};
use std::io::{self, Write};

#[tokio::main]
async fn main() -> Result<()> {
    let cli = Cli::parse();

    // Initialize logging
    let level = if cli.verbose { "debug" } else { "warn" };
    tracing_subscriber::fmt()
        .with_env_filter(level)
        .with_writer(std::io::stderr)
        .compact()
        .with_target(false)
        .init();

    // Handle config commands first (no API key needed)
    if let Command::Config { action } = &cli.command {
        return handle_config_action(action, cli.json);
    }

    // Load .env file
    dotenvy::dotenv().ok();

    // Load config with CLI overrides
    let config = config::Config::load(cli.config, cli.api_key)?;
    let client = {api_module}::Client::new(&config)?;

    // Dispatch commands
    match cli.command {
        Command::Get { id } => {
            let result = client.get(&id).await?;
            format::print_result(&result, cli.json);
        }
        Command::Search { query, limit } => {
            let results = client.search(&query, limit).await?;
            format::print_results(&results, cli.json);
        }
        Command::Config { .. } => unreachable!(),
    }

    Ok(())
}

fn handle_config_action(action: &ConfigAction, as_json: bool) -> Result<()> {
    match action {
        ConfigAction::Init { api_key, force } => init_config(api_key.clone(), *force),
        ConfigAction::Show => {
            let config = config::Config::load(None, None)?;
            config.show_masked(as_json)
        }
        ConfigAction::Path => {
            let path = config::Config::default_config_path()
                .context("Cannot determine config path")?;
            println!("{}", path.display());
            Ok(())
        }
        ConfigAction::Edit => config::Config::edit_config(),
    }
}

fn init_config(api_key: Option<String>, force: bool) -> Result<()> {
    let path = config::Config::default_config_path()
        .context("Cannot determine config path")?;

    if path.exists() && !force {
        anyhow::bail!("Config exists: {}\nUse --force to overwrite", path.display());
    }

    let api_key = match api_key {
        Some(k) => k,
        None => {
            print!("API key: ");
            io::stdout().flush()?;
            let mut input = String::new();
            io::stdin().read_line(&mut input)?;
            input.trim().to_string()
        }
    };

    if api_key.is_empty() {
        anyhow::bail!("API key cannot be empty");
    }

    let config = config::Config {
        api_key: Some(api_key),
        ..Default::default()
    };

    if let Some(parent) = path.parent() {
        std::fs::create_dir_all(parent)?;
    }
    let content = toml::to_string_pretty(&config)?;
    std::fs::write(&path, content)?;

    // Set restrictive permissions on Unix
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let mut perms = std::fs::metadata(&path)?.permissions();
        perms.set_mode(0o600);
        std::fs::set_permissions(&path, perms)?;
    }

    println!("Config saved: {}", path.display());
    Ok(())
}
```

---

## cli.rs Template

```rust
use clap::{Parser, Subcommand, ValueEnum};
use std::path::PathBuf;

#[derive(Parser)]
#[command(name = "{cli-name}", version, about = "CLI for {API Name}", author)]
pub struct Cli {
    #[command(subcommand)]
    pub command: Command,

    /// API key (or set {ENV_VAR})
    #[arg(long, env = "{ENV_VAR}", global = true, hide_env_values = true)]
    pub api_key: Option<String>,

    /// Config file path
    #[arg(long, short, global = true)]
    pub config: Option<PathBuf>,

    /// Output as JSON
    #[arg(long, short, global = true)]
    pub json: bool,

    /// Enable verbose output
    #[arg(long, short, global = true)]
    pub verbose: bool,

    /// Stream response in real-time
    #[arg(long, global = true)]
    pub stream: bool,
}

#[derive(Subcommand)]
pub enum Command {
    /// Get a single item by ID
    Get {
        /// Item ID
        id: String,

        /// Output format
        #[arg(long, value_enum, default_value = "json")]
        format: OutputFormat,
    },

    /// Search for items
    Search {
        /// Search query
        query: String,

        /// Maximum results
        #[arg(long, short, default_value = "20")]
        limit: u32,

        /// Fetch all results (paginated)
        #[arg(long)]
        all: bool,
    },

    /// Create a new item
    Create {
        /// Item name/title
        name: String,

        /// Item content
        content: Option<String>,
    },

    /// Configuration management
    Config {
        #[command(subcommand)]
        action: ConfigAction,
    },
}

#[derive(Subcommand)]
pub enum ConfigAction {
    /// Initialize configuration
    Init {
        #[arg(long)]
        api_key: Option<String>,
        #[arg(long)]
        force: bool,
    },
    /// Show current configuration (secrets masked)
    Show,
    /// Show configuration file path
    Path,
    /// Edit configuration with default editor
    Edit,
}

#[derive(ValueEnum, Clone, Copy, Debug, Default)]
pub enum OutputFormat {
    #[default]
    Json,
    Table,
    Markdown,
}

impl OutputFormat {
    pub fn as_str(&self) -> &'static str {
        match self {
            OutputFormat::Json => "json",
            OutputFormat::Table => "table",
            OutputFormat::Markdown => "markdown",
        }
    }
}
```

---

## config.rs Template

```rust
use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use std::path::PathBuf;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Config {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub api_key: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub domain: Option<String>,

    #[serde(default)]
    pub defaults: Defaults,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Defaults {
    #[serde(default = "default_limit")]
    pub limit: u32,

    #[serde(default)]
    pub stream: bool,
}

impl Default for Defaults {
    fn default() -> Self {
        Self {
            limit: default_limit(),
            stream: false,
        }
    }
}

fn default_limit() -> u32 {
    20
}

impl Config {
    /// Load config with 4-tier priority:
    /// 1. CLI flags (passed as parameters)
    /// 2. Environment variables
    /// 3. Project config (./{cli-name}.toml in current directory)
    /// 4. Global config (~/.config/{cli-name}/config.toml)
    pub fn load(
        config_path: Option<PathBuf>,
        api_key_override: Option<String>,
    ) -> Result<Self> {
        // Determine config path with priority: explicit > project > global
        let path = config_path.unwrap_or_else(|| {
            let project_config = PathBuf::from("./{cli-name}.toml");
            if project_config.exists() {
                project_config
            } else {
                Self::default_config_path().unwrap_or_else(|| PathBuf::from("config.toml"))
            }
        });

        let mut config = if path.exists() {
            let content = std::fs::read_to_string(&path)
                .with_context(|| format!("Failed to read config: {}", path.display()))?;
            toml::from_str(&content)
                .with_context(|| format!("Failed to parse config: {}", path.display()))?
        } else {
            Config::default()
        };

        // CLI flag override (highest priority)
        if let Some(key) = api_key_override {
            config.api_key = Some(key);
        }

        // Environment variable fallback
        if config.api_key.is_none() {
            config.api_key = std::env::var("{ENV_VAR}").ok();
        }

        if config.domain.is_none() {
            config.domain = std::env::var("{ENV_VAR}_DOMAIN").ok();
        }

        Ok(config)
    }

    pub fn default_config_path() -> Option<PathBuf> {
        dirs::config_dir().map(|p| p.join("{cli-name}").join("config.toml"))
    }

    pub fn show_masked(&self, as_json: bool) -> Result<()> {
        let masked = Config {
            api_key: self.api_key.as_ref().map(|k| mask_key(k)),
            domain: self.domain.clone(),
            defaults: self.defaults.clone(),
        };

        if as_json {
            println!("{}", serde_json::to_string_pretty(&masked)?);
        } else {
            println!("{}", toml::to_string_pretty(&masked)?);
        }
        Ok(())
    }

    pub fn edit_config() -> Result<()> {
        let path = Self::default_config_path().context("Cannot determine config path")?;

        if !path.exists() {
            anyhow::bail!("Config not found: {}\nRun '{cli-name} config init' first", path.display());
        }

        let editor = std::env::var("EDITOR").unwrap_or_else(|_| "vim".to_string());
        std::process::Command::new(&editor)
            .arg(&path)
            .status()
            .with_context(|| format!("Failed to open editor: {}", editor))?;

        Ok(())
    }

    pub fn get_api_key(&self) -> Result<&str> {
        self.api_key
            .as_deref()
            .context("API key not configured. Run '{cli-name} config init' or set {ENV_VAR}")
    }
}

fn mask_key(key: &str) -> String {
    if key.len() <= 8 {
        "*".repeat(key.len())
    } else {
        format!("{}...{}", &key[..4], &key[key.len() - 4..])
    }
}
```

---

## API Client Template

```rust
// src/{api}/mod.rs
mod client;
mod types;

pub use client::Client;
pub use types::*;

// src/{api}/client.rs
use anyhow::{Context, Result};
use reqwest::header::{HeaderMap, HeaderValue, AUTHORIZATION, CONTENT_TYPE};
use serde_json::Value;
use crate::config::Config;

pub struct Client {
    http: reqwest::Client,
    base_url: String,
}

impl Client {
    pub fn new(config: &Config) -> Result<Self> {
        let api_key = config.get_api_key()?;

        let mut headers = HeaderMap::new();
        headers.insert(
            AUTHORIZATION,
            HeaderValue::from_str(&format!("Bearer {}", api_key))
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

        Ok(Self { http, base_url })
    }

    pub async fn get(&self, id: &str) -> Result<Value> {
        let url = format!("{}/items/{}", self.base_url, id);
        let response = self.http.get(&url).send().await?;
        self.handle_response(response).await
    }

    pub async fn search(&self, query: &str, limit: u32) -> Result<Vec<Value>> {
        let url = format!("{}/search", self.base_url);
        let response = self.http
            .get(&url)
            .query(&[("q", query), ("limit", &limit.to_string())])
            .send()
            .await?;

        let data = self.handle_response(response).await?;
        Ok(data["results"].as_array().cloned().unwrap_or_default())
    }

    async fn handle_response(&self, response: reqwest::Response) -> Result<Value> {
        let status = response.status();
        let text = response.text().await?;

        if !status.is_success() {
            anyhow::bail!("API error ({}): {}", status, text);
        }

        serde_json::from_str(&text).context("Failed to parse response")
    }
}

// src/{api}/types.rs
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Item {
    pub id: String,
    pub name: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub description: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SearchResult {
    pub items: Vec<Item>,
    pub total: u32,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub next_cursor: Option<String>,
}
```

---

## format.rs Template

```rust
use serde::Serialize;
use serde_json::Value;

pub fn print_result<T: Serialize>(result: &T, as_json: bool) {
    if as_json {
        println!("{}", serde_json::to_string_pretty(result).unwrap());
    } else {
        print_formatted(result);
    }
}

pub fn print_results<T: Serialize>(results: &[T], as_json: bool) {
    if as_json {
        println!("{}", serde_json::to_string_pretty(results).unwrap());
    } else {
        for result in results {
            print_formatted(result);
            println!();
        }
    }
}

fn print_formatted<T: Serialize>(item: &T) {
    let value = serde_json::to_value(item).unwrap();
    print_value(&value, 0);
}

fn print_value(value: &Value, indent: usize) {
    let prefix = "  ".repeat(indent);
    match value {
        Value::Object(map) => {
            for (key, val) in map {
                print!("{}{}: ", prefix, key);
                match val {
                    Value::Object(_) | Value::Array(_) => {
                        println!();
                        print_value(val, indent + 1);
                    }
                    _ => println!("{}", format_scalar(val)),
                }
            }
        }
        Value::Array(arr) => {
            for item in arr {
                println!("{}- ", prefix);
                print_value(item, indent + 1);
            }
        }
        _ => println!("{}{}", prefix, format_scalar(value)),
    }
}

fn format_scalar(value: &Value) -> String {
    match value {
        Value::String(s) => s.clone(),
        Value::Number(n) => n.to_string(),
        Value::Bool(b) => b.to_string(),
        Value::Null => "null".to_string(),
        _ => value.to_string(),
    }
}

// For streaming output
pub fn print_stream_footer(metadata: &Value) {
    if let Some(sources) = metadata.get("sources").and_then(|s| s.as_array()) {
        if !sources.is_empty() {
            println!("\n\n---\nSources:");
            for source in sources {
                if let Some(url) = source.as_str() {
                    println!("- {}", url);
                }
            }
        }
    }
}
```

---

## HTTP Client Pattern

### Basic Auth (Atlassian style)

```rust
use base64::{engine::general_purpose::STANDARD, Engine};

fn create_auth_header(email: &str, token: &str) -> String {
    let credentials = format!("{}:{}", email, token);
    format!("Basic {}", STANDARD.encode(credentials))
}
```

### Bearer Token (Perplexity/Slack style)

```rust
fn create_auth_header(token: &str) -> String {
    format!("Bearer {}", token)
}
```

### Rate Limiting

```rust
use governor::{Quota, RateLimiter};
use std::num::NonZeroU32;

let rate_limiter = RateLimiter::direct(
    Quota::per_minute(NonZeroU32::new(60).unwrap())
);

// Before each request
rate_limiter.until_ready().await;
```

---

## Streaming Pattern

```rust
use futures::StreamExt;

pub async fn chat_stream<F>(
    &self,
    request: Value,
    on_chunk: F,
) -> Result<Value>
where
    F: Fn(&str),
{
    let response = self.http
        .post(&format!("{}/chat", self.base_url))
        .json(&request)
        .send()
        .await?;

    let mut stream = response.bytes_stream();
    let mut buffer = String::new();
    let mut result = Value::Null;

    while let Some(chunk) = stream.next().await {
        let bytes = chunk?;
        let text = String::from_utf8_lossy(&bytes);

        for line in text.lines() {
            if line.starts_with("data: ") {
                let data = &line[6..];
                if data == "[DONE]" {
                    break;
                }

                if let Ok(json) = serde_json::from_str::<Value>(data) {
                    if let Some(content) = json["choices"][0]["delta"]["content"].as_str() {
                        on_chunk(content);
                        buffer.push_str(content);
                    }
                    result = json;
                }
            }
        }
    }

    Ok(result)
}
```

---

## Pagination Pattern

### Offset-based (Jira style)

```rust
pub async fn search_all(&self, query: &str) -> Result<Vec<Value>> {
    let mut all_results = Vec::new();
    let mut start_at = 0;
    let max_results = 100;

    loop {
        let response = self.http
            .get(&format!("{}/search", self.base_url))
            .query(&[
                ("jql", query),
                ("startAt", &start_at.to_string()),
                ("maxResults", &max_results.to_string()),
            ])
            .send()
            .await?;

        let data: Value = response.json().await?;
        let issues = data["issues"].as_array().cloned().unwrap_or_default();
        let total = data["total"].as_u64().unwrap_or(0);

        all_results.extend(issues.clone());
        start_at += issues.len();

        if start_at as u64 >= total {
            break;
        }

        // Rate limit delay
        tokio::time::sleep(std::time::Duration::from_millis(200)).await;
    }

    Ok(all_results)
}
```

### Cursor-based (Confluence/Slack style)

```rust
pub async fn search_all(&self, query: &str) -> Result<Vec<Value>> {
    let mut all_results = Vec::new();
    let mut cursor: Option<String> = None;

    loop {
        let mut request = self.http.get(&format!("{}/search", self.base_url));
        request = request.query(&[("q", query)]);

        if let Some(ref c) = cursor {
            request = request.query(&[("cursor", c)]);
        }

        let response = request.send().await?;
        let data: Value = response.json().await?;

        let results = data["results"].as_array().cloned().unwrap_or_default();
        all_results.extend(results);

        // Check for next page
        cursor = data["_links"]["next"]
            .as_str()
            .and_then(|url| extract_cursor(url));

        if cursor.is_none() {
            break;
        }

        // Rate limit delay
        tokio::time::sleep(std::time::Duration::from_millis(200)).await;
    }

    Ok(all_results)
}

fn extract_cursor(url: &str) -> Option<String> {
    url.split("cursor=")
        .nth(1)
        .map(|s| s.split('&').next().unwrap_or(s).to_string())
}
```
