<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/telemetryflow/.github/raw/main/docs/assets/tfo-logo-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/telemetryflow/.github/raw/main/docs/assets/tfo-logo-light.svg">
    <img src="https://github.com/telemetryflow/.github/raw/main/docs/assets/tfo-logo-light.svg" alt="TelemetryFlow Logo" width="80%">
  </picture>

  <h3>TelemetryFlow Hermes — Self-Improving AI Agent for Observability Incident Response</h3>

[![Version](https://img.shields.io/badge/Version-1.0.0-orange.svg)](CHANGELOG.md)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python)](https://www.python.org/)
[![Hermes](https://img.shields.io/badge/Hermes-Agent-00d4aa)](https://github.com/NousResearch/hermes-agent)
[![Tests](https://img.shields.io/badge/Tests-105%20passing-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/Coverage-95%25+-brightgreen.svg)](tests/)
[![Tools](https://img.shields.io/badge/Tools-23%20Plugin-blueviolet)](plugins/telemetryflow/plugin.yaml)
[![ContextTypes](https://img.shields.io/badge/ContextTypes-95+-9cf)](docs/api/context-types.md)
[![ClickHouse](https://img.shields.io/badge/ClickHouse-Readonly-FFCC00?logo=clickhouse)](security/clickhouse-readonly.sql)
[![Docs](https://img.shields.io/badge/Docs-28%20Pages-informational)](docs/)

</div>

---

## Overview

**TelemetryFlow Hermes** deploys a self-improving, multi-agent AI team for autonomous incident response against the TelemetryFlow Observability Platform. Four specialised agents — Triage, Investigator, Reviewer, and Remediator — form an autonomous pipeline that classifies alerts, gathers evidence from all four telemetry signals (metrics, logs, traces, exemplars), independently verifies root cause hypotheses, and proposes gated remediation with human approval.

Steps 1–4 are fully autonomous. You only touch step 5.

```
Alert Fired → Triage → Investigator → Reviewer → Remediator → Human Approval
```

## Features

### Multi-Agent Team

- **Triage Agent** — Classifies alerts by severity, auto-resolves known patterns, routes genuine anomalies
- **Investigator Agent** — Queries ClickHouse for metrics, logs, traces, exemplars; cross-correlates evidence; forms root cause hypotheses
- **Reviewer Agent** — Independent verification in a separate context with zero investigation bias (read-only tools)
- **Remediator Agent** — Proposes gated remediation actions (scale, restart, rollback, update_alert) with human-in-the-loop approval

### TelemetryFlow Integration (23 Tools)

- **Core Telemetry** (5) — query_metrics, search_logs, list_traces, get_exemplars, query_correlations
- **Infrastructure** (3) — check_k8s, check_infra, check_db_monitoring (16 DB types)
- **Platform** (5) — check_uptime, query_ai_intelligence, query_platform, query_account, manage_data_masking
- **LLM Module** (6) — chat_with_context, stream_chat, manage_conversation, generate_insight, query_llm_usage, manage_provider
- **Remediation** (4) — scale_deployment, restart_pod, rollback_deploy, update_alert (all gated)

### TFO LLM Module Support

- **95+ ContextType values** — all context types from TFO's ContextCollector (4,440 lines)
- **15 LLM Provider types** — anthropic, openai, google, gemini, deepseek, qwen, ollama, mistral, grok, kimi, zhipu, mimo, openrouter, custom
- **5 Insight types** — chronology, prediction, recommendation, root-cause, pattern
- **7 Adapter classes** — Claude, OpenAI, Gemini, DeepSeek, Qwen, Ollama, Custom

### Self-Improving Skills (11 Bundled)

- **Observability** (9) — k8s-pod-debug, payments-api-oom-rca, clickhouse-query-patterns, tfql-natural-language, alert-triage, remediation-gate, cross-signal-correlation, memory-pressure-investigation, tfo-llm-api
- **Database Monitoring** (2) — slow-query-detection, qan-analysis
- Skills auto-evolve through investigation experience (GEPA optimization available offline)

### Cost Optimization

| Agent        | Model                         | Cost/Incident            |
| ------------ | ----------------------------- | ------------------------ |
| Triage       | glm-5.1 (OpenCode Go)         | ~$0.01                   |
| Investigator | claude-sonnet-4-5 (Anthropic) | ~$0.05-0.15              |
| Reviewer     | glm-5.1 (OpenCode Go)         | ~$0.03-0.08              |
| Remediator   | glm-5.1 (OpenCode Go)         | ~$0.01-0.03              |
| **Total**    |                               | **~$0.10-0.27/incident** |

## Architecture

### System Architecture

```mermaid
graph TB
    subgraph Alert["Alert Sources"]
        TF["TelemetryFlow Alert Engine<br/>33 Alert Rules"]
        PD["PagerDuty / Slack / K8s Events"]
    end

    subgraph Agents["Hermes Agent Team"]
        direction LR
        T["Triage<br/>glm-5.1"]
        I["Investigator<br/>claude-sonnet-4-5"]
        R["Reviewer<br/>glm-5.1"]
        M["Remediator<br/>glm-5.1"]
    end

    subgraph Tools["Plugin Tools (23)"]
        direction LR
        MT["Metrics · Logs · Traces · Exemplars"]
        K8["K8s · Infra · DB Monitoring"]
        LM["LLM Chat · Insights · Providers"]
        RM["Scale · Restart · Rollback ⚠"]
    end

    subgraph TFO["TelemetryFlow Platform"]
        API["TFO API<br/>/api/v2/*"]
        CH[("ClickHouse<br/>Metrics · Logs · Traces<br/>Exemplars")]
        LLM["LLM Module<br/>ContextCollector · PromptBuilder<br/>InsightGenerator"]
        AUTH["Auth Module<br/>JWT · API Keys · RBAC"]
    end

    subgraph Human["Human Interface"]
        TG["Telegram<br/>4 Bot Tokens"]
        ENG["On-Call Engineer"]
    end

    TF --> T
    T -->|"genuine anomaly"| I
    I --> R
    R --> M
    M -->|"approval request"| TG
    TG <--> ENG

    Agents --> Tools
    Tools --> API
    API --> CH
    API --> LLM
    API --> AUTH

    style Agents fill:#e0f2fe
    style Tools fill:#ddd6fe
    style TFO fill:#d1fae5
    style Human fill:#fef3c7
```

### Incident Response Pipeline

```mermaid
sequenceDiagram
    participant TF as TelemetryFlow
    participant TR as Triage Agent
    participant INV as Investigator Agent
    participant REV as Reviewer Agent
    participant REM as Remediator Agent
    participant H as Human (Telegram)

    TF->>TR: Alert webhook fires
    activate TR
    TR->>TR: Classify severity + check MEMORY.md
    TR->>INV: Delegate investigation
    deactivate TR

    activate INV
    INV->>TF: query_metrics + search_logs + list_traces + get_exemplars
    INV->>INV: Cross-correlate evidence → root cause hypothesis
    INV->>REV: Delegate review
    deactivate INV

    activate REV
    REV->>TF: Verify evidence independently (read-only)
    REV->>REM: Approved hypothesis
    deactivate REV

    activate REM
    REM->>H: Telegram: Alert + Evidence + Proposed Action
    H->>REM: Approve
    REM->>TF: Execute remediation
    deactivate REM
```

### Directory Structure

```
telemetryflow-hermes/
├── config.yaml                          # Default Hermes agent configuration
├── SOUL.md                              # Default agent identity
├── .env.example                         # API key template (3 auth methods)
├── Makefile                             # Setup, deploy, verify, CI targets
├── pyproject.toml                       # Python project config (pytest, ruff, coverage)
│
├── profiles/                            # Multi-agent team (4 profiles)
│   ├── triage/                          #   glm-5.1 · max_turns=30 · readonly
│   ├── investigator/                    #   claude-sonnet-4-5 · max_turns=45
│   ├── reviewer/                        #   glm-5.1 · max_turns=20 · readonly
│   └── remediator/                      #   glm-5.1 · max_turns=15 · require_approval
│
├── skills/                              # 11 bundled skills
│   ├── observability/                   #   9 observability skills
│   └── database-monitoring/             #   2 DB monitoring skills
│
├── plugins/                             # TelemetryFlow plugin
│   └── telemetryflow/
│       ├── plugin.yaml                  #   v2.0.0 — 23 tools
│       └── tools/                       #   23 Python tools (stdlib only)
│           ├── _shared.py               #     API helpers, type constants
│           ├── query_metrics.py
│           ├── search_logs.py
│           ├── list_traces.py
│           ├── get_exemplars.py
│           ├── query_correlations.py
│           ├── check_k8s.py
│           ├── check_infra.py
│           ├── check_db_monitoring.py
│           ├── check_uptime.py
│           ├── query_ai_intelligence.py
│           ├── query_platform.py
│           ├── query_account.py
│           ├── manage_data_masking.py
│           ├── chat_with_context.py
│           ├── stream_chat.py
│           ├── manage_conversation.py
│           ├── generate_insight.py
│           ├── query_llm_usage.py
│           ├── manage_provider.py
│           ├── scale_deployment.py       #   ⚠ requires_approval
│           ├── restart_pod.py            #   ⚠ requires_approval
│           ├── rollback_deploy.py        #   ⚠ requires_approval
│           └── update_alert.py           #   ⚠ requires_approval
│
├── cron/                                # 6 scheduled investigation jobs
├── scripts/                             # 5 deployment scripts
├── security/                            # ClickHouse read-only user (20 tables)
├── hooks/                               # 3 lifecycle hooks
├── tests/                               # 105 tests, 95%+ coverage
│   ├── conftest.py
│   ├── mocks/
│   ├── unit/                            # 21 tool test files
│   └── integration/                     # Pipeline integration tests
├── docs/                                # 28-page documentation wiki
│   ├── agents/                          # 5 agent docs
│   ├── tools/                           # Tool overview + reference
│   ├── skills/                          # Skill overview + reference
│   ├── api/                             # Auth, LLM module, context types
│   ├── deployment/                      # Standard + air-gapped
│   ├── security/                        # Security overview + ClickHouse
│   ├── configuration/                   # Environment variables reference
│   └── operations/                      # Cron, hooks, troubleshooting
│
├── .github/workflows/                   # GitHub Actions CI/CD
│   ├── ci.yml                           #   lint → test → security → coverage
│   └── release.yml                      #   Tag-triggered release
└── .gitlab-ci.yml                       # GitLab CI/CD pipeline
```

## Quick Start

### Prerequisites

| Requirement            | Version  | Check                                |
| ---------------------- | -------- | ------------------------------------ |
| Python 3               | 3.8+     | `python3 --version`                  |
| Hermes Agent           | Latest   | `hermes --version`                   |
| TelemetryFlow Platform | Running  | `curl $TELEMETRYFLOW_API_URL/health` |
| Telegram Bot Tokens    | 4 tokens | [@BotFather](https://t.me/BotFather) |

### One-Command Setup

```bash
# Install Hermes Agent
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
source ~/.bashrc
hermes doctor

# Clone and deploy
git clone https://github.com/telemetryflow/telemetryflow-hermes.git
cd telemetryflow-hermes

# Configure API keys
cp .env.example ~/.hermes/.env
# Edit ~/.hermes/.env — minimum: TELEMETRYFLOW_API_KEY, TELEMETRYFLOW_ORGANIZATION_ID,
#                       TELEMETRYFLOW_WORKSPACE_ID, ANTHROPIC_API_KEY, ZHIPU_API_KEY

# Deploy everything
make setup        # profiles + skills + cron + security + hooks + plugins
make telegram     # configure 4 Telegram gateways
make verify       # end-to-end pipeline verification
make deploy       # start all 4 gateways
```

## Configuration

### Environment Variables

See [.env.example](./.env.example) for the complete template. **Minimum required:**

```env
TELEMETRYFLOW_API_KEY=tfs_xxxxx                          # API Key (recommended)
TELEMETRYFLOW_API_URL=http://localhost:3000/api/v2        # Platform URL
TELEMETRYFLOW_ORGANIZATION_ID=your-org-uuid               # Required for all LLM endpoints
TELEMETRYFLOW_WORKSPACE_ID=your-workspace-uuid            # Required for telemetry queries
ANTHROPIC_API_KEY=sk-ant-xxxxx                            # Investigator (claude-sonnet-4-5)
ZHIPU_API_KEY=your-zhipu-key                              # Triage/Reviewer/Remediator (glm-5.1)
```

Three authentication methods supported: API Key (`tfs_*`), JWT Login, Ingestion Headers (`tfk_*/tfs_*`).

### Agent Models

| Agent        | Model             | Provider    | Max Turns | Access        |
| ------------ | ----------------- | ----------- | --------- | ------------- |
| Triage       | glm-5.1           | OpenCode Go | 30        | Read-only     |
| Investigator | claude-sonnet-4-5 | Anthropic   | 45        | Read-only     |
| Reviewer     | glm-5.1           | OpenCode Go | 20        | Read-only     |
| Remediator   | glm-5.1           | OpenCode Go | 15        | Write (gated) |

## Security

- **Read-only ClickHouse user** — `hermes_readonly` with table-level SELECT grants on 20 tables
- **Human-in-the-loop** — all 4 remediation tools require approval (600s timeout → auto-escalate)
- **90-turn hard cap** — prevents runaway loops and credit burn
- **Mandatory `workspace_id`** — all queries scoped to prevent cross-tenant data leakage
- **Separate reviewer context** — prevents investigation bias (confirmation, anchoring, sunk cost)
- **Python stdlib only** — zero pip dependencies, no supply chain risk
- **Secrets in `.env` only** — never in `config.yaml`

See [SECURITY.md](./SECURITY.md) for the complete security policy.

## Testing

```bash
# Run all tests
make test

# Run with coverage (95%+ required)
make test-cov

# Run CI pipeline locally
make ci-pipeline
```

## Makefile Commands

| Target             | Description                                             |
| ------------------ | ------------------------------------------------------- |
| `make setup`       | Deploy profiles, skills, cron, security, hooks, plugins |
| `make deploy`      | Setup + start all 4 Telegram gateways                   |
| `make verify`      | End-to-end pipeline verification                        |
| `make test`        | Run pytest test suite                                   |
| `make test-cov`    | Run tests with coverage report                          |
| `make lint`        | Run ruff linter                                         |
| `make ci-pipeline` | Full CI pipeline (lint → test → security)               |
| `make doctor`      | Run `hermes doctor --fix`                               |
| `make clean`       | Remove all installed profiles/skills/plugins            |

## Documentation

| Document                                                     | Description                                         |
| ------------------------------------------------------------ | --------------------------------------------------- |
| [Architecture](./docs/architecture.md)                       | System design, data flow, component diagrams        |
| [Getting Started](./docs/getting-started.md)                 | Installation and first investigation                |
| [Agents](./docs/agents/README.md)                            | Multi-agent team design                             |
| [Tool Reference](./docs/tools/reference.md)                  | All 23 tools with parameters                        |
| [LLM Module](./docs/api/llm-module.md)                       | TFO LLM API integration (chat, insights, providers) |
| [Context Types](./docs/api/context-types.md)                 | All 95+ ContextType values                          |
| [Authentication](./docs/api/authentication.md)               | JWT, API Key, Ingestion auth flows                  |
| [Environment Variables](./docs/configuration/environment.md) | Complete `.env` reference                           |
| [Deployment](./docs/deployment/standard.md)                  | Standard and air-gapped deployment                  |
| [Security](./docs/security/README.md)                        | Layered security model                              |
| [Troubleshooting](./docs/operations/troubleshooting.md)      | Common issues and solutions                         |

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed guidelines.

## Project Statistics

| Metric              | Count               |
| ------------------- | ------------------- |
| Agent Profiles      | 4                   |
| Plugin Tools        | 23                  |
| Bundled Skills      | 11                  |
| Context Types       | 95+                 |
| Provider Types      | 15                  |
| Cron Jobs           | 6                   |
| Lifecycle Hooks     | 3                   |
| ClickHouse Tables   | 20 (read-only)      |
| Documentation Pages | 28                  |
| Test Methods        | 105                 |
| Test Coverage       | 95%+                |
| CI/CD Pipelines     | 2 (GitHub + GitLab) |

## License

Apache-2.0 License — see [LICENSE](./LICENSE) file for details.

## Acknowledgments

Built for the [TelemetryFlow Platform](https://github.com/telemetryflow/telemetryflow-platform-monolith) — Enterprise Telemetry & Observability Platform. Powered by [Hermes Agent](https://github.com/NousResearch/hermes-agent) by Nous Research.

---

**Built with ❤️ by Telemetri Data Indonesia**
