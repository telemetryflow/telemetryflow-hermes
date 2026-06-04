# Standard Deployment

Full deployment with external LLM providers (Anthropic, Zhipu/OpenCode Go, etc.).

## Architecture

```mermaid
graph TB
    subgraph "Agent Host"
        HERMES["Hermes Agent<br/>4 Profiles"]
        TG["Telegram Gateway<br/>4 Bot Tokens"]
    end

    subgraph "LLM Providers (External)"
        ANTH["Anthropic API<br/>claude-sonnet-4-5"]
        ZHIPU["OpenCode Go / Zhipu<br/>glm-5.1"]
    end

    subgraph "TelemetryFlow Platform"
        TFO_API["TFO API<br/>:3000"]
        TFO_CH["ClickHouse<br/>:9000"]
        TFO_PG["PostgreSQL<br/>:5432"]
        TFO_REDIS["Redis<br/>:6379"]
    end

    subgraph "Kubernetes Cluster"
        K8S["kubectl<br/>Remediation actions"]
    end

    subgraph "Telegram"
        TG_BOT["4 Telegram Bots"]
        HUMAN["On-Call Engineer"]
    end

    HERMES -->|"Investigator"| ANTH
    HERMES -->|"Triage/Reviewer/Remediator"| ZHIPU
    HERMES -->|"REST API<br/>TELEMETRYFLOW_API_KEY"| TFO_API
    TFO_API --> TFO_CH
    TFO_API --> TFO_PG
    TFO_API --> TFO_REDIS
    HERMES -->|"scale/restart/rollback"| K8S
    HERMES --> TG
    TG <-->|"bidirectional"| TG_BOT
    TG_BOT <--> HUMAN
```

## Step-by-Step

### Step 1 — Install Hermes Agent

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
source ~/.bashrc

# Verify
hermes doctor
hermes doctor --fix  # auto-repair issues
```

### Step 2 — Clone and Configure

```bash
git clone https://github.com/telemetryflow/telemetryflow-hermes.git
cd telemetryflow-hermes
cp .env.example ~/.hermes/.env
```

### Step 3 — Edit Environment Variables

Edit `~/.hermes/.env`:

```env
# Authentication (Method A recommended)
TELEMETRYFLOW_API_KEY=tfs_your_api_key_here

# Connection
TELEMETRYFLOW_API_URL=http://localhost:3000/api/v2
TELEMETRYFLOW_ORGANIZATION_ID=your-org-uuid
TELEMETRYFLOW_WORKSPACE_ID=your-workspace-uuid

# LLM Providers
ANTHROPIC_API_KEY=sk-ant-your-key    # Investigator
ZHIPU_API_KEY=your-zhipu-key         # Triage/Reviewer/Remediator
```

### Step 4 — Create TelemetryFlow API Key

In TelemetryFlow UI:

```mermaid
graph LR
    UI["TFO UI"] --> SETTINGS["Settings"]
    SETTINGS --> APIK["API Keys"]
    APIK --> GEN["Generate New Key"]
    GEN --> SCOPES["Set Scopes:<br/>llm:chat, llm:read, llm:write,<br/>llm:insights, telemetry:read"]
    SCOPES --> COPY["Copy key → .env"]
```

Required scopes:

- `llm:chat` — Send chat messages
- `llm:read` — Read providers and conversations
- `llm:write` — Manage providers
- `llm:insights` — Generate insights
- `telemetry:read` — Query ClickHouse

### Step 5 — Setup ClickHouse Read-Only User

```bash
# Run on ClickHouse server as admin
clickhouse-client < security/clickhouse-readonly.sql
```

This creates `hermes_readonly` with SELECT grants on 20 telemetry tables. See [ClickHouse Security](../security/clickhouse-readonly.md).

### Step 6 — Deploy Profiles and Tools

```bash
make setup
```

This runs:

1. `scripts/setup-profiles.sh` — Creates 4 agent profiles
2. Skills installation — Copies 29 skills to `~/.hermes/skills/`
3. Cron installation — Copies `jobs.json` to `~/.hermes/cron/`
4. Security setup — Runs ClickHouse readonly user setup
5. Hooks installation — Copies 3 lifecycle hooks
6. Plugin installation — Copies 37 tools to `~/.hermes/plugins/`

### Step 7 — Configure Telegram Gateways

```bash
# Create 4 bots via @BotFather on Telegram
# /newbot → triage_bot
# /newbot → investigator_bot
# /newbot → reviewer_bot
# /newbot → remediator_bot

make telegram
```

For each bot, get the chat ID:

1. Message the bot
2. Visit `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Copy the `chat.id` value

### Step 8 — Verify Pipeline

```bash
make verify
```

Verification checks:

```mermaid
graph TD
    V1["Hermes installation"]
    V2["Config files present"]
    V3["API keys set"]
    V4["TelemetryFlow API reachable"]
    V5["ClickHouse accessible"]
    V6["Telegram gateways"]
    V7["Tools available"]

    V1 --> V2 --> V3 --> V4 --> V5 --> V6 --> V7
    V7 --> OK["ALL CHECKS PASSED"]
```

### Step 9 — Start Gateways

```bash
make deploy
```

Starts 4 background processes:

- `hermes -p triage gateway start`
- `hermes -p investigator gateway start`
- `hermes -p reviewer gateway start`
- `hermes -p remediator gateway start`

### Step 10 — Test with Sample Alert

Send a test alert to the Triage bot on Telegram:

```
ALERT: payments-api p95 latency breach
Service: payments-api
Metric: http_server_duration_p95
Value: 640ms (threshold: 200ms)
Severity: HIGH
Time: 2026-06-04T03:47:00Z
```

Expected flow: Triage → Investigator → Reviewer → Remediator → Human approval (~23 seconds).

## Make Targets Reference

| Target            | Description                                             |
| ----------------- | ------------------------------------------------------- |
| `make install`    | Install Hermes Agent only                               |
| `make setup`      | Deploy profiles, skills, cron, security, hooks, plugins |
| `make profiles`   | Create 4 agent profiles                                 |
| `make skills`     | Install 29 observability skills                         |
| `make cron`       | Install 6 cron jobs                                     |
| `make security`   | Setup ClickHouse read-only user                         |
| `make hooks`      | Install 3 lifecycle hooks                               |
| `make plugins`    | Install TelemetryFlow plugin (37 tools)                 |
| `make telegram`   | Configure 4 Telegram gateways                           |
| `make verify`     | Run pipeline verification                               |
| `make deploy`     | Setup + start all gateways                              |
| `make status`     | Check gateway status                                    |
| `make doctor`     | Run `hermes doctor --fix`                               |
| `make clean`      | Remove all installed profiles/skills/plugins            |
| `make air-gapped` | Deploy with Ollama (offline)                            |

## Production Considerations

### Process Management

Use `systemd` or `screen` to keep gateways running:

```bash
# Using screen
screen -dmS hermes-triage hermes -p triage gateway start
screen -dmS hermes-investigator hermes -p investigator gateway start
screen -dmS hermes-reviewer hermes -p reviewer gateway start
screen -dmS hermes-remediator hermes -p remediator gateway start

# Or for SSH disconnects
sudo loginctl enable-linger $USER
```

### Logging

All agent activity is logged to `~/.hermes/logs/`:

| Log File             | Contents                             |
| -------------------- | ------------------------------------ |
| `agent.log`          | Agent activity and decisions         |
| `gateway.log`        | Telegram gateway events              |
| `errors.log`         | Error traces                         |
| `investigations.log` | Investigation start/end (from hooks) |
| `remediations.log`   | Remediation outcomes (from hooks)    |
| `alerts.log`         | Alert received events (from hooks)   |

### Monitoring

```bash
# Check all gateway status
make status

# Watch recent investigation logs
tail -f ~/.hermes/logs/investigations.log

# Check errors
grep -i error ~/.hermes/logs/gateway.log | tail -20
```
