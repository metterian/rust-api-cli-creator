# rust-api-cli-creator

[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blue)](https://code.claude.com/docs/en/skills)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A Claude Code skill for creating production-ready Rust CLI tools that wrap APIs.

## Quick Start

```bash
# Clone and install
git clone https://github.com/metterian/rust-api-cli-creator.git
cd rust-api-cli-creator
./install.sh
```

The installer offers three options:
- **Global** (`~/.claude/skills/`) - Available in all projects
- **Local** (`./.claude/skills/`) - Current project only
- **Custom** - Your own path

## Usage

### Auto-trigger

The skill activates automatically when you ask:
- "make a CLI for the Notion API"
- "create a Rust CLI wrapper for Stripe"
- "build a CLI tool for GitHub API"

### Manual trigger

```
/rust-api-cli-creator
```

### Direct script

```bash
~/.claude/skills/rust-api-cli-creator/scripts/init_rust_cli.py \
  github-cli --api-name GitHub --path ~/projects
```

## Generated Project Structure

```
my-cli/
├── Cargo.toml
├── src/
│   ├── main.rs          # Entry point
│   ├── cli.rs           # Clap commands
│   ├── config.rs        # 4-tier config
│   └── api/             # API client
└── .claude/skills/      # Auto-generated skill
```

## Features

| Feature | Description |
|---------|-------------|
| **clap** | Type-safe CLI argument parsing |
| **tokio** | Async runtime |
| **reqwest** | HTTP client with JSON |
| **4-tier config** | CLI > ENV > Project > Global |
| **tracing** | Structured logging |

## Configuration Priority

```
1. CLI flags (--api-key)
2. Environment variables (MY_CLI_API_KEY)
3. Project config (./{cli-name}.toml)
4. Global config (~/.config/{cli-name}/config.toml)
```

## Uninstall

```bash
./uninstall.sh
```

## Requirements

- Python 3.10+
- Rust 1.75.0+
- Claude Code CLI

## License

MIT - see [LICENSE](LICENSE)

## Acknowledgments

Patterns extracted from:
- [perplexity-cli](https://github.com/metterian/perplexity-cli)
- [atlassian-cli](https://github.com/metterian/atlassian-cli)
- [slack-cli](https://github.com/metterian/slack-cli)
