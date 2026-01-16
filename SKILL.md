---
name: rust-api-cli-creator
description: |
  Create production-ready Rust CLI tools that wrap APIs, with Claude Code skill integration.
  Use when: (1) Building a new CLI tool for an API (REST, GraphQL), (2) Creating MCP-compatible
  CLI wrappers, (3) Adding Claude Code skill to existing CLI, (4) "make a CLI for X API",
  (5) "create skill for Y CLI". Generates complete Cargo project with async HTTP client,
  config management, and .claude/skills/ integration.
---

# Rust API CLI Creator

Create Rust CLI tools with Claude Code skill integration following proven patterns from perplexity-cli, atlassian-cli, and slack-cli.

## Workflow Overview

1. **Gather Requirements** - API docs, auth method, key operations
2. **Initialize Project** - Run init script or create Cargo project
3. **Implement CLI** - Follow the modular architecture pattern
4. **Create Skill** - Add .claude/skills/{cli-name}/SKILL.md
5. **Test & Iterate** - Verify commands work, refine skill triggers

## Step 1: Gather Requirements

Before creating a CLI, clarify:

| Question | Example Answer |
|----------|----------------|
| What API? | Notion API, GitHub API, Stripe API |
| Auth method? | API key header, Bearer token, Basic auth |
| Key operations? | CRUD, search, list, export |
| Output formats? | JSON, table, markdown |
| Config needs? | Domain, token, defaults |

## Step 2: Project Architecture

Standard directory structure:

```
{cli-name}/
├── Cargo.toml
├── src/
│   ├── main.rs          # Entry point (tokio::main)
│   ├── lib.rs           # Module exports
│   ├── cli.rs           # Clap command definitions
│   ├── config.rs        # TOML config + env vars
│   ├── format.rs        # Output formatting (JSON/table/text)
│   └── {api}/           # API client module
│       ├── mod.rs
│       ├── client.rs    # HTTP client, request builders
│       └── types.rs     # Data structures
├── .claude/
│   └── skills/
│       └── {cli-name}/
│           └── SKILL.md # Claude Code skill
└── CLAUDE.md            # Project instructions for Claude
```

## Step 3: Core Implementation Patterns

### Cargo.toml Dependencies

```toml
[package]
name = "{cli-name}"
version = "0.1.0"
edition = "2021"
rust-version = "1.75.0"

[dependencies]
# CLI
clap = { version = "4.5", features = ["derive", "env"] }

# Async runtime
tokio = { version = "1", features = ["full"] }

# HTTP client
reqwest = { version = "0.12", features = ["json", "stream"] }

# Serialization
serde = { version = "1", features = ["derive"] }
serde_json = "1"

# Config
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

[profile.release]
opt-level = 3
lto = true
codegen-units = 1
strip = true
```

### Config Priority Chain (4-tier)

```
1. CLI flags (--token, --domain)     ← Highest priority
2. Environment variables (API_TOKEN)
3. Project config (./{cli}.toml)
4. Global config (~/.config/{cli}/config.toml)
```

See `references/rust-cli-patterns.md` for complete code templates.

## Step 4: Create Claude Code Skill

Every CLI should include a skill at `.claude/skills/{cli-name}/SKILL.md`:

```yaml
---
name: {cli-name}
description: |
  {Brief description of CLI purpose}.
  Use when: (1) {trigger 1}, (2) {trigger 2}, (3) {trigger 3}.
  Commands: {cmd1}, {cmd2}, {cmd3}.
---
```

Skill body should include:
- **Command reference** - All available commands with examples
- **Output formats** - JSON, table, markdown options
- **Common workflows** - Step-by-step for complex operations

See `references/skill-template.md` for complete skill template.

## Step 5: Implementation Checklist

- [ ] Cargo.toml with all dependencies
- [ ] CLI commands with clap derive macros
- [ ] Config loading with 4-tier priority
- [ ] HTTP client with auth headers
- [ ] Error handling with anyhow
- [ ] Output formatting (--json flag)
- [ ] Streaming support for large results (--stream)
- [ ] Rate limiting for API safety
- [ ] .claude/skills/{name}/SKILL.md
- [ ] CLAUDE.md with project instructions

## Quick Start Script

Initialize a new CLI project:

```bash
scripts/init_rust_cli.py {cli-name} --api-name {ApiName} --path {output-dir}
```

## Resources

- **Code Templates**: `references/rust-cli-patterns.md` - Complete Rust code patterns
- **Skill Template**: `references/skill-template.md` - SKILL.md template with examples
- **Init Script**: `scripts/init_rust_cli.py` - Project scaffolding
