# Claude Code Skill Template

Complete template for creating `.claude/skills/{cli-name}/SKILL.md` files.

## Directory Structure

```
.claude/
└── skills/
    └── {cli-name}/
        └── SKILL.md
```

## SKILL.md Template

```markdown
---
name: {cli-name}
description: |
  {One-line summary of what the CLI does}.
  Use when: (1) {trigger scenario 1}, (2) {trigger scenario 2}, (3) {trigger scenario 3}.
  Commands: {cmd1}, {cmd2}, {cmd3}, {cmd4}.
allowed-tools: Bash
---

# {cli-name}

{Brief description of CLI purpose and key capability.}

## Command Selection Guide

| Need | Command | Notes |
|------|---------|-------|
| {Use case 1} | `{cmd1}` | {Brief note} |
| {Use case 2} | `{cmd2}` | {Brief note} |
| {Use case 3} | `{cmd3}` | {Brief note} |

## Commands

### {Command 1}
```bash
{cli-name} {cmd1} <required_arg> [--option value]
{cli-name} {cmd1} "example query" --format json
```

### {Command 2}
```bash
{cli-name} {cmd2} <arg1> <arg2>
```

## Key Options

| Option | Description |
|--------|-------------|
| `--json` | Output as JSON (for parsing) |
| `--format` | Output format: json, table, markdown |
| `--limit N` | Maximum results |
| `--all` | Fetch all results (paginated) |
| `--stream` | Real-time streaming output |

## Configuration

```bash
# Initialize config
{cli-name} config init

# Show config (secrets masked)
{cli-name} config show

# Config location
{cli-name} config path
```

Environment variables:
- `{ENV_VAR}` - API key/token
- `{ENV_VAR}_DOMAIN` - API domain (optional)
```

---

## Real Examples

### Example 1: perplexity-cli

```yaml
---
name: perplexity-cli
description: |
  Perplexity AI CLI for web search, Q&A, reasoning, and deep research.
  Use when: (1) Need real-time web information or recent news, (2) Research topics requiring citations,
  (3) Complex reasoning with web grounding, (4) Academic or SEC filings search.
  Commands: ask (general Q&A), search (web search with sources), reason (step-by-step analysis), research (deep investigation).
---
```

**Key Features:**
- Command selection table with model recommendations
- Each command has 2-3 concrete examples
- Options table with clear descriptions
- Search mode documentation

### Example 2: jira-confluence (atlassian-cli)

```yaml
---
name: jira-confluence
description: Execute Jira/Confluence queries via atlassian-cli. All commands use flat structure (e.g., `jira comments`, `jira comment-add`). Support JQL/CQL searches with ADF-to-Markdown conversion, create/update tickets and pages, manage comments and attachments, handle issue transitions.
allowed-tools: Bash
---
```

**Key Features:**
- URL handling section (extract IDs from URLs)
- Separate sections for Jira and Confluence
- Format documentation (ADF, HTML, Markdown)
- Auto-injection filter config example
- Pagination options (`--all`, `--stream`)

### Example 3: slack-workspace (slack-cli)

```yaml
---
name: slack-workspace
version: 0.1.0
description: |
  Execute Slack workspace queries via slack-cli. Search users/channels, send/update/delete messages,
  add reactions, pin messages, manage bookmarks, list emoji. Use when working with Slack data,
  team communication, or automating Slack workflows.
allowed-tools: Bash
---
```

**Key Features:**
- JSON + jq pattern for ID extraction
- Compact command reference
- `--expand` fields table
- Channel format documentation
- mrkdwn syntax warning (NOT Markdown)

---

## Description Writing Guidelines

The description is the primary trigger mechanism. Include:

1. **What it does** (one sentence)
2. **Use when** (3-5 numbered scenarios)
3. **Commands** (list key commands)

### Good Description Pattern

```
{Brief purpose statement}.
Use when: (1) {scenario 1}, (2) {scenario 2}, (3) {scenario 3}.
Commands: {cmd1} ({purpose}), {cmd2} ({purpose}), {cmd3} ({purpose}).
```

### Examples

**API CLI:**
```
CLI for GitHub API operations including repositories, issues, and pull requests.
Use when: (1) Managing GitHub repos programmatically, (2) Creating/updating issues,
(3) Reviewing PRs, (4) Automating GitHub workflows.
Commands: repo (manage repos), issue (manage issues), pr (pull requests), workflow (actions).
```

**Data Processing CLI:**
```
CLI for transforming and analyzing JSON/CSV data files.
Use when: (1) Converting between data formats, (2) Filtering/transforming datasets,
(3) Aggregating or summarizing data, (4) Validating data schemas.
Commands: convert (format conversion), filter (data filtering), aggregate (summarization).
```

---

## Skill Body Best Practices

### 1. Start with Quick Reference

```markdown
**Use `--json` for parsing.** Combine with `jq` for extraction.

```bash
# Common pattern
{cli} {cmd} "query" --json | jq -r '.[0].id'
```
```

### 2. Command Tables Over Prose

```markdown
| Need | Command | Notes |
|------|---------|-------|
| Quick lookup | `get` | Single item |
| Search | `search` | Supports JQL/CQL |
| Bulk export | `search --all` | Paginated |
```

### 3. Concrete Examples

```markdown
### Search Examples
```bash
# Find open bugs assigned to me
{cli} search "assignee = currentUser() AND status = Open"

# Export all items to JSONL
{cli} search "project = PROJ" --all --stream > items.jsonl
```
```

### 4. Options Tables

```markdown
| Option | Description | Applies To |
|--------|-------------|------------|
| `--format markdown` | Convert to Markdown | get, search |
| `--limit N` | Results per page | search |
| `--all` | Fetch all results | search |
```

### 5. Format/Syntax Warnings

If the API has unique syntax, document it clearly:

```markdown
## Important: Slack mrkdwn (NOT Markdown)

| Element | Correct | Wrong |
|---------|---------|-------|
| Bold | `*text*` | `**text**` |
| Link | `<url\|label>` | `[label](url)` |
```

---

## Skill File Checklist

- [ ] YAML frontmatter with `name` and `description`
- [ ] Description includes "Use when" triggers
- [ ] Description lists key commands
- [ ] Command selection guide/table
- [ ] Concrete command examples
- [ ] Options reference table
- [ ] Configuration section
- [ ] Environment variable list
- [ ] Format/syntax warnings (if applicable)
