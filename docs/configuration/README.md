# Configuration Overview

TelemetryFlow Hermes configuration is split across two mechanisms: `config.yaml` for agent behavior and `.env` for secrets.

## Configuration Architecture

```mermaid
graph TB
    subgraph "Agent Behavior (config.yaml)"
        CFG_MODEL["Model Selection<br/>default model + provider"]
        CFG_AGENT["Agent Settings<br/>max_turns, timeout"]
        CFG_TOOLS["Tool Permissions<br/>terminal, web, delegation"]
        CFG_MEM["Memory Limits<br/>tier1_max chars"]
        CFG_CUR["Curator Settings<br/>stale/age thresholds"]
    end

    subgraph "Secrets (.env)"
        ENV_API["TELEMETRYFLOW_API_KEY<br/>Platform authentication"]
        ENV_ORG["TELEMETRYFLOW_ORGANIZATION_ID<br/>Org scoping"]
        ENV_WS["TELEMETRYFLOW_WORKSPACE_ID<br/>Workspace scoping"]
        ENV_LLM["ANTHROPIC_API_KEY<br/>ZHIPU_API_KEY<br/>LLM provider keys"]
        ENV_TG["TELEGRAM_BOT_TOKEN_*<br/>Telegram gateway tokens"]
        ENV_CH["CLICKHOUSE_*<br/>Database connection"]
    end

    subgraph "Per-Profile Overrides"
        P_CFG["profiles/<name>/config.yaml"]
        P_SOUL["profiles/<name>/SOUL.md"]
        P_MEM["profiles/<name>/memories/"]
    end

    CFG_MODEL & CFG_AGENT & CFG_TOOLS & CFG_MEM & CFG_CUR --> DEFAULT["Default Profile"]
    DEFAULT --> P_CFG
    ENV_API & ENV_ORG & ENV_WS & ENV_LLM & ENV_TG & ENV_CH --> ENV_FILE["~/.hermes/.env"]
```

## File Locations

| File             | Location                                      | Purpose                            |
| ---------------- | --------------------------------------------- | ---------------------------------- |
| Default config   | `~/.hermes/config.yaml`                       | Agent behavior for default profile |
| Default identity | `~/.hermes/SOUL.md`                           | Agent personality                  |
| Default memory   | `~/.hermes/memories/`                         | MEMORY.md + USER.md                |
| Secrets          | `~/.hermes/.env`                              | All API keys and passwords         |
| Profile config   | `~/.hermes/profiles/<name>/config.yaml`       | Per-profile overrides              |
| Profile identity | `~/.hermes/profiles/<name>/SOUL.md`           | Per-profile personality            |
| Plugin config    | `~/.hermes/plugins/telemetryflow/plugin.yaml` | Tool definitions                   |
| Cron config      | `~/.hermes/cron/jobs.json`                    | Scheduled tasks                    |

## Sub-Pages

- [Environment Variables](./environment.md) — Complete `.env` reference

## Quick Configuration Commands

```bash
# View current config
hermes config get model.default
hermes config get model.provider

# Set model for default profile
hermes config set model.default "glm-5.1"
hermes config set model.provider "opencode-go"

# Set model for specific profile
hermes -p investigator config set model.default "claude-sonnet-4-5"
hermes -p investigator config set model.provider "anthropic"

# Check env path
hermes config env-path

# View tool status
hermes tools list
```
