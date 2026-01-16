# rust-api-cli-creator

A Claude Code skill for creating production-ready Rust CLI tools that wrap APIs, with automatic skill integration.

## Features

- **Project Scaffolding**: Generate complete Rust CLI projects with one command
- **Proven Patterns**: Templates extracted from real-world CLIs (perplexity-cli, atlassian-cli, slack-cli)
- **4-Tier Config**: CLI flags > Environment > Project config > Global config
- **Skill Integration**: Auto-generates `.claude/skills/` for Claude Code compatibility
- **Best Practices**: Async/await, proper error handling, streaming support patterns

## Installation

### Quick Install

```bash
# Clone the repository
git clone https://github.com/metterian/rust-api-cli-creator.git
cd rust-api-cli-creator

# Run installer
./install.sh
```

The installer will ask:
- **Global** (`~/.claude/skills/`) - Available in all projects
- **Local** (`./.claude/skills/`) - Only current project
- **Custom** - Specify your own path

### Manual Install

```bash
# Global installation
cp -r rust-api-cli-creator ~/.claude/skills/

# Or local installation
mkdir -p .claude/skills
cp -r rust-api-cli-creator .claude/skills/
```

## Usage

### Auto-trigger

The skill automatically activates when you ask Claude Code things like:
- "make a CLI for the Notion API"
- "create a Rust CLI wrapper for Stripe"
- "add a Claude Code skill to my CLI"

### Manual trigger

```
/rust-api-cli-creator
```

### Quick Start Script

```bash
# Create a new CLI project
~/.claude/skills/rust-api-cli-creator/scripts/init_rust_cli.py \
  github-cli --api-name GitHub --path ~/projects
```

This generates:

```
github-cli/
├── Cargo.toml
├── src/
│   ├── main.rs
│   ├── lib.rs
│   ├── cli.rs
│   ├── config.rs
│   ├── format.rs
│   └── github/
│       ├── mod.rs
│       ├── client.rs
│       └── types.rs
├── .claude/
│   └── skills/
│       └── github-cli/
│           └── SKILL.md
└── CLAUDE.md
```

## Project Structure

```
rust-api-cli-creator/
├── SKILL.md                    # Main skill definition
├── install.sh                  # Interactive installer
├── uninstall.sh               # Uninstaller
├── README.md                  # This file
├── references/
│   ├── rust-cli-patterns.md   # Complete Rust code templates
│   └── skill-template.md      # SKILL.md writing guide
└── scripts/
    └── init_rust_cli.py       # Project scaffolding script
```

## Generated CLI Features

Every generated CLI includes:

| Feature | Description |
|---------|-------------|
| **clap** derive macros | Type-safe CLI argument parsing |
| **tokio** async runtime | Non-blocking HTTP operations |
| **reqwest** HTTP client | Modern HTTP with JSON support |
| **4-tier config** | Flexible configuration management |
| **Error handling** | `anyhow` for ergonomic errors |
| **Logging** | `tracing` with env filter |
| **Output formats** | JSON, table, or custom |
| **Claude Code skill** | Auto-generated SKILL.md |

## Configuration Priority

Generated CLIs follow this config priority:

```
1. CLI flags (--token, --domain)     ← Highest priority
2. Environment variables (API_TOKEN)
3. Project config (./{cli-name}.toml)
4. Global config (~/.config/{cli-name}/config.toml)
```

## References

The skill includes detailed reference documentation:

### `references/rust-cli-patterns.md`

Complete code templates for:
- Cargo.toml with optimal dependencies
- main.rs with command dispatch
- cli.rs with clap derive macros
- config.rs with 4-tier loading
- API client with auth patterns
- Streaming and pagination patterns

### `references/skill-template.md`

Guide for writing effective SKILL.md files:
- YAML frontmatter format
- Description trigger patterns
- Command documentation examples
- Real examples from production CLIs

## Uninstallation

```bash
./uninstall.sh
```

Or manually:

```bash
# Global
rm -rf ~/.claude/skills/rust-api-cli-creator

# Local
rm -rf .claude/skills/rust-api-cli-creator
```

## Requirements

- Python 3.10+ (for init script)
- Rust 1.75.0+ (for generated projects)
- Claude Code CLI

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

Patterns extracted from real-world production CLIs.
