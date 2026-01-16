---
name: rust-api-cli-creator
description: |
  Create production-ready Rust CLI tools that wrap APIs.
  Use when: (1) "make a CLI for X API", (2) "create Rust CLI wrapper",
  (3) "build CLI tool for REST/GraphQL API", (4) Adding skill to existing CLI.
allowed-tools: Bash, Read, Write, Edit
---

# Rust API CLI Creator

Generate Rust CLI projects with async HTTP client, 4-tier config, and Claude Code skill integration.

## Quick Start

```bash
scripts/init_rust_cli.py my-cli --api-name MyAPI --path .
```

## Workflow

1. **Requirements** - API docs, auth method, key operations
2. **Initialize** - Run script or manually create project
3. **Implement** - Follow patterns in `references/rust-cli-patterns.md`
4. **Add Skill** - Create `.claude/skills/{cli-name}/SKILL.md`

## Generated Structure

```
my-cli/
├── Cargo.toml
├── src/
│   ├── main.rs       # tokio::main entry
│   ├── cli.rs        # clap commands
│   ├── config.rs     # 4-tier config
│   └── api/          # HTTP client
└── .claude/skills/   # Auto-generated skill
```

## Config Priority

```
CLI flags > ENV vars > Project config > Global config
```

## References

- [Code Templates](references/rust-cli-patterns.md) - Rust patterns
- [Skill Template](references/skill-template.md) - SKILL.md guide
