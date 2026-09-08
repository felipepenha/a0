---
name: cli-anything
description: "Agent-native CLI interface hub and harnesses for software applications (Notion, CLI-Hub catalog, and connected desktop apps). Use when any agent needs to interact with Notion (pages, databases, search, local app status), browse or launch CLI-Anything tools, or query application states using structured JSON output and CLI commands."
---

# CLI-Anything: Agent-Native Application Interface

Based on the [HKUDS CLI-Anything](https://github.com/HKUDS/CLI-Anything) specification. Provides AI agents with structured, composable command-line interfaces to software applications and cloud services.

## Prerequisites & Installation

CLI-Anything harnesses are installed as standard command-line tools on `PATH`:

```bash
# In Agent Zero Container:
# notion-cli, cli-anything-notion, and cli-hub are pre-installed in /usr/local/bin.

# On Host or External Machines:
pip install ./packages/cli-anything-notion
pip install cli-anything-hub
```

---

## Core Directives for Agents

1. **System Command Execution**: Execute `notion-cli` directly from any working directory or terminal session:
   ```bash
   notion-cli [command] [options]
   ```
2. **Machine-Readable Output (`--json`)**: Always include `--json` when parsing responses programmatically.
3. **Desktop Deep-Linking (`--open`)**: Use the `--open` flag on `page create`, `page get`, or use `page open <id>` to focus the local macOS `/Applications/Notion.app` desktop installation via native `notion://` URL schemes.
4. **Authentication**: Ensure `NOTION_TOKEN` is set in the environment / `.env` or pass `-t, --token <token>` in the command.

---

## Notion Harness (`notion-cli`)

### 1. Page Management (`notion-cli page`)

- **Create Page in Database or Parent Page**:
  ```bash
  notion-cli page create \
    --parent <DATABASE_ID_OR_PARENT_PAGE_ID> \
    --database \
    --title "Exercise Name" \
    --properties '{"Area": ["Upper Body"], "Tool": ["Bar"], "Target Muscles": ["Lats"]}' \
    --body "Detailed markdown text..." \
    --open \
    --json
  ```
- **Inspect Page**:
  ```bash
  notion-cli page get <PAGE_ID> --json
  ```
- **Append Blocks to Existing Page**:
  ```bash
  notion-cli page append <PAGE_ID> \
    --text "New section notes" \
    --type paragraph \
    --json
  ```
- **Open Page in macOS Notion App**:
  ```bash
  notion-cli page open <PAGE_ID>
  ```

### 2. Database Queries (`notion-cli db`)

- **Inspect Database Schema & Properties**:
  ```bash
  notion-cli db get <DATABASE_ID> --json
  ```
- **Query Database Rows**:
  ```bash
  notion-cli db query <DATABASE_ID> --limit 10 --json
  ```

### 3. Workspace Search (`notion-cli search`)

- **Search Pages and Databases**:
  ```bash
  notion-cli search "Pull Ups" --limit 5 --json
  ```

### 4. macOS Desktop Application Status (`notion-cli app`)

- **Inspect Local Notion Desktop State**:
  ```bash
  notion-cli app status --json
  ```

---

## CLI-Hub Package Manager (`cli-hub`)

Use the official `cli-anything-hub` package manager to discover, inspect, and install community harnesses for other desktop software:

```bash
# Browse registered software harnesses
cli-hub list

# Search for specific tools (e.g. 3d, image, notes, cad)
cli-hub search image

# Inspect software requirements
cli-hub info gimp

# Install and launch a harness
cli-hub install gimp
cli-hub launch gimp [args...]
```
