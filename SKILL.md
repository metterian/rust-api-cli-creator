---
name: rust-api-cli-creator
description: |
  Create production-ready Rust CLI tools that wrap APIs, with Claude Code skill integration.
  Use when: (1) "make a CLI for X API", (2) "create Rust CLI wrapper for Y",
  (3) "build CLI tool for REST/GraphQL API", (4) "create skill for my CLI",
  (5) "add Claude Code skill to existing CLI", (6) "write SKILL.md for CLI".
allowed-tools: Bash, Read, Write, Edit
---

# Rust API CLI Creator

Two workflows: **Create CLI** and **Create Skill** for the CLI.

## Workflow 1: Create Rust CLI

```bash
scripts/init_rust_cli.py my-cli --api-name MyAPI --path .
```

**Steps:**
1. Gather requirements (API docs, auth, key operations)
2. Run init script or create manually
3. Implement using `references/rust-cli-patterns.md`
4. Test and iterate

**Generated Structure:**
```
my-cli/
├── Cargo.toml
├── src/
│   ├── main.rs       # tokio::main
│   ├── cli.rs        # clap commands
│   ├── config.rs     # 4-tier config
│   └── api/          # HTTP client
└── CLAUDE.md
```

## Workflow 2: Create Skill for CLI

After CLI is working, create a skill at `.claude/skills/{cli-name}/SKILL.md`.

**Skill Structure:**
```yaml
---
name: {cli-name}
description: |
  {What it does}.
  Use when: (1) {trigger 1}, (2) {trigger 2}, (3) {trigger 3}.
  Commands: {cmd1}, {cmd2}, {cmd3}.
allowed-tools: Bash
---

# {cli-name}

## Commands
{Command examples with --json for parsing}

## Options
{Table of key options}

## Configuration
{Config init and env vars}
```

**Key Principles (from [skill-creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md)):**
- Description is the trigger - include ALL "when to use" scenarios
- Keep SKILL.md concise (<500 lines)
- Use tables over prose
- Include concrete examples

See `references/skill-template.md` for complete template with real examples.

## Config Priority (4-tier)

```
CLI flags > ENV vars > Project config > Global config
```

## References

- [Rust Patterns](references/rust-cli-patterns.md) - Code templates
- [Skill Template](references/skill-template.md) - SKILL.md guide with examples
