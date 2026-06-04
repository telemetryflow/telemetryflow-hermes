# Architecture Overview

System architecture for TelemetryFlow Hermes — a multi-agent AI incident response pipeline integrated with the TelemetryFlow Observability Platform.

## High-Level Architecture

```mermaid
graph TB
    subgraph "TelemetryFlow Platform"
        TFO_API["TFO API<br/>/api/v2/*"]
        TFO_LLM["LLM Module<br/>Chat · Insights · Providers"]
        TFO_CH["ClickHouse<br/>Metrics · Logs · Traces · Exemplars"]
        TFO_ALERT["Alert Engine<br/>33 Alert Rules"]
        TFO_AUTH["Auth Module<br/>JWT · API Keys · RBAC"]
    end

    subgraph "Hermes Agent Framework"
        direction TB
        H_CORE["AIAgent Core<br/>ReAct Loop"]
        H_SOUL["SOUL.md<br/>Identity"]
        H_MEM["Memory<br/>Tier 1 · Tier 2 · Tier 3"]
        H_SKILLS["Skills<br/>29 Bundled · 18 Categories"]
        H_PLUGIN["TelemetryFlow Plugin<br/>37 Tools"]
    end

    subgraph "Agent Team"
        TRIAGE["Triage<br/>glm-5.1"]
        INV["Investigator<br/>claude-sonnet-4-5"]
        REV["Reviewer<br/>glm-5.1"]
        REM["Remediator<br/>glm-5.1"]
    end

    subgraph "Human Interface"
        TG["Telegram<br/>4 Bot Tokens"]
        HUMAN["On-Call Engineer"]
    end

    TFO_ALERT -->|"webhook"| TRIAGE
    TRIAGE -->|"delegate"| INV
    INV -->|"delegate"| REV
    REV -->|"delegate"| REM
    REM -->|"approval request"| TG
    TG -->|"approve/reject"| HUMAN

    H_CORE --> H_SOUL
    H_CORE --> H_MEM
    H_CORE --> H_SKILLS
    H_CORE --> H_PLUGIN

    H_PLUGIN -->|"REST API"| TFO_API
    TFO_API --> TFO_LLM
    TFO_API --> TFO_CH
    TFO_API --> TFO_AUTH

    INV -.->|"query_metrics<br/>search_logs<br/>list_traces<br/>get_exemplars"| TFO_CH
    REV -.->|"read-only verification"| TFO_CH
```

## Data Flow — Incident Response Pipeline

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
    TR->>TR: Classify severity
    TR->>TR: Check MEMORY.md for known patterns
    TR->>INV: Delegate investigation
    deactivate TR

    activate INV
    INV->>TF: query_metrics (metrics_1m)
    INV->>TF: search_logs (otel_logs)
    INV->>TF: list_traces (otel_traces)
    INV->>TF: get_exemplars (memory_usage)
    INV->>INV: Form root cause hypothesis
    INV->>REV: Delegate review
    deactivate INV

    activate REV
    REV->>TF: Verify evidence (read-only)
    REV->>REV: Check for bias / alternatives
    REV->>REM: Approved hypothesis
    deactivate REV

    activate REM
    REM->>H: Telegram: Alert + Evidence + Proposed Action
    H->>REM: Approve / Reject
    REM->>TF: Execute remediation
    deactivate REM
```

## Component Architecture

```mermaid
graph LR
    subgraph "Project Files"
        direction TB
        CFG["config.yaml<br/>Default agent config"]
        ENV[".env<br/>API keys & secrets"]
        SOUL["SOUL.md<br/>Agent identity"]
        MEM["memories/<br/>MEMORY.md · USER.md"]
        PROFILES["profiles/<br/>triage · investigator · reviewer · remediator"]
        SKILLS["skills/<br/>observability/ · database-monitoring/"]
        PLUGIN["plugins/telemetryflow/<br/>plugin.yaml + 37 tools"]
        CRON["cron/<br/>jobs.json (6 scheduled tasks)"]
        HOOKS["hooks/<br/>pre-investigation · post-remediation · on-alert-fired"]
        SEC["security/<br/>clickhouse-readonly.sql"]
        SCRIPTS["scripts/<br/>install · setup · verify · deploy"]
    end

    subgraph "TFO Platform Monolith"
        direction TB
        LLM_MOD["backend/src/modules/llm/"]
        AUTH_MOD["backend/src/modules/auth/"]
        CH_MOD["ClickHouse client"]
    end

    CFG --> PROFILES
    ENV --> PLUGIN
    PLUGIN -->|"tfo_request()"| LLM_MOD
    PLUGIN -->|"clickhouse_query()"| CH_MOD
    HOOKS --> SCRIPTS
    SEC --> CH_MOD
```

## Technology Stack

| Layer                       | Technology                                         | Purpose                                                  |
| --------------------------- | -------------------------------------------------- | -------------------------------------------------------- |
| **Agent Framework**         | Hermes Agent (Nous Research)                       | Self-improving AI agent with memory, skills, multi-agent |
| **LLM Providers**           | Anthropic, Zhipu (OpenCode Go), OpenRouter, Ollama | Model inference for different agent roles                |
| **Observability**           | TelemetryFlow Platform                             | Metrics, Logs, Traces, Exemplars in ClickHouse           |
| **Database**                | ClickHouse                                         | Columnar storage for all telemetry signals               |
| **Plugin Runtime**          | Python 3 (stdlib only)                             | 37 tools using `urllib`, `json`, `sys`                   |
| **Communication**           | Telegram Bot API                                   | Human-in-the-loop notifications                          |
| **Container Orchestration** | Kubernetes                                         | Pod/deployment management for remediation                |
| **Security**                | JWT, API Keys (tfk*/tfs*), AES-256-GCM             | Authentication and encryption                            |

## Directory Structure

```
telemetryflow-hermes/
├── config.yaml                          # Default Hermes agent configuration
├── SOUL.md                              # Default agent identity
├── .env.example                         # API key template (3 auth methods)
├── Makefile                             # Setup, deploy, verify, CI targets
├── pyproject.toml                       # Python project config (pytest, ruff, coverage)
├── Dockerfile                           # Multi-stage Docker (python:3.13-slim-trixie)
├── docker-compose.yaml                  # 4 profiles: core, monitoring, tools, all
├── run-container.sh                     # Build, tag, push, compose orchestration
│
├── profiles/                            # Multi-agent team (4 profiles)
│   ├── triage/                          # Alert classifier
│   │   ├── config.yaml                  #   glm-5.1, max_turns=30, readonly
│   │   ├── SOUL.md                      #   Triage specialist identity
│   │   └── memories/                    #   MEMORY.md + USER.md
│   ├── investigator/                    # Evidence gatherer
│   │   ├── config.yaml                  #   claude-sonnet-4-5, max_turns=45
│   │   ├── SOUL.md                      #   Senior SRE identity
│   │   └── memories/
│   ├── reviewer/                        # Independent verifier
│   │   ├── config.yaml                  #   glm-5.1, max_turns=20, readonly
│   │   ├── SOUL.md                      #   Independent reviewer identity
│   │   └── memories/
│   └── remediator/                      # Gated actor
│       ├── config.yaml                  #   glm-5.1, max_turns=15, require_approval
│       ├── SOUL.md                      #   Remediation specialist identity
│       └── memories/
│
├── skills/                              # 29 bundled skills (18 categories)
│   ├── monitoring/                      #   8 skills (uptime, vm, agent, k8s, service-map, network-map, ...)
│   ├── observability/                   #   9 skills (k8s-pod-debug, payments-api-oom-rca, ...)
│   ├── database-monitoring/             #   2 skills (slow-query-detection, qan-analysis)
│   ├── alerting/                        #   alert-management
│   ├── dashboard/                       #   dashboard-management
│   ├── reporting/                       #   report-automation
│   ├── retention/                       #   retention-management
│   ├── audit/                           #   audit-compliance
│   ├── subscription/                    #   subscription-management
│   ├── tenancy/                         #   tenancy-administration
│   ├── iam/                             #   iam-administration
│   ├── sso/                             #   sso-configuration
│   ├── query/                           #   tfql-query
│   ├── ai-intelligence/                 #   ai-intelligence
│   └── ...                              #   18 categories total
│
├── plugins/                             # TelemetryFlow plugin
│   └── telemetryflow/
│       ├── plugin.yaml                  # v3.0.0 — 37 tools
│       └── tools/                       # 37 Python tools (stdlib only)
│           ├── _shared.py               # TFO API helpers, 74 ContextTypes, 15 ProviderTypes
│           │
│           │ # ── Core Telemetry (5) ──
│           ├── query_metrics.py
│           ├── search_logs.py
│           ├── list_traces.py
│           ├── get_exemplars.py
│           ├── query_correlations.py
│           │
│           │ # ── Monitoring (8) ──
│           ├── check_k8s.py
│           ├── check_infra.py
│           ├── check_uptime.py
│           ├── check_vm.py
│           ├── check_agent.py
│           ├── check_service_map.py
│           ├── check_network_map.py
│           ├── check_db_monitoring.py
│           │
│           │ # ── AI & LLM (7) ──
│           ├── chat_with_context.py
│           ├── stream_chat.py
│           ├── manage_conversation.py
│           ├── generate_insight.py
│           ├── query_llm_usage.py
│           ├── manage_provider.py
│           ├── query_ai_intelligence.py
│           │
│           │ # ── Platform (8) ──
│           ├── query_platform.py
│           ├── query_account.py
│           ├── query_audit.py
│           ├── query_subscription.py
│           ├── manage_dashboards.py
│           ├── manage_alerts.py
│           ├── manage_reports.py
│           ├── manage_data_masking.py
│           │
│           │ # ── Infrastructure (6) ──
│           ├── manage_retention.py
│           ├── manage_tenancy.py
│           ├── manage_iam.py
│           ├── manage_sso.py
│           ├── query_tfql.py
│           │
│           │ # ── Remediation (3+1) ⚠ requires_approval ──
│           ├── scale_deployment.py       # ⚠
│           ├── restart_pod.py            # ⚠
│           ├── rollback_deploy.py        # ⚠
│           └── update_alert.py           # ⚠
│
├── tests/                               # 458 tests, 97% coverage
│   ├── conftest.py                      # Shared fixtures
│   ├── mocks/                           # MockTFOApi, response factories
│   ├── unit/                            # 34 tool test files
│   └── integration/                     # Pipeline integration tests
│
├── cron/                                # Scheduled tasks
│   ├── jobs.json                        # 6 cron jobs
│   └── output/                          # Cron run outputs
│
├── scripts/                             # Deployment scripts
│   ├── install.sh                       # Hermes Agent installer
│   ├── setup-profiles.sh                # Create 4 agent profiles
│   ├── setup-telegram.sh                # Configure Telegram gateways
│   ├── verify-pipeline.sh               # End-to-end pipeline verification
│   └── deploy-air-gapped.sh             # Air-gapped deployment
│
├── security/                            # Database security
│   ├── clickhouse-readonly.sql          # Read-only user (20 tables)
│   └── setup-readonly-user.sh           # Automated setup script
│
├── hooks/                               # Lifecycle hooks
│   ├── on-alert-fired.sh                # Alert enrichment before triage
│   ├── pre-investigation.sh             # Investigation context logging
│   └── post-remediation.sh              # Remediation outcome tracking
│
├── .github/workflows/                   # GitHub Actions CI/CD
│   ├── ci.yml                           #   lint → test-unit → test-integration → security → coverage
│   ├── docker.yml                       #   Multi-platform Docker build (amd64/arm64)
│   └── release.yml                      #   Tag-triggered release
├── .gitlab-ci.yml                       # GitLab CI/CD pipeline
│
└── docs/                                # Documentation wiki (28+ pages)
    ├── README.md                        # Wiki index
    ├── getting-started.md
    ├── architecture.md
    ├── tfo-hermes.md                    # Marp presentation
    ├── agents/                          # Agent docs
    ├── tools/                           # Tool overview + reference
    ├── skills/                          # Skill overview + reference
    ├── api/                             # Auth, LLM module, context types
    ├── deployment/                      # Standard, Docker, air-gapped
    ├── security/                        # Security overview + ClickHouse
    ├── configuration/                   # Environment variables reference
    └── operations/                      # Cron, hooks, troubleshooting
```

## Key Design Decisions

### 1. Python stdlib only (no pip dependencies)

All 37 plugin tools use only Python standard library (`urllib`, `json`, `sys`, `os`). No `requests`, `httpx`, or external packages. This maximizes portability and eliminates supply chain risk.

### 2. All queries go through TFO API

ClickHouse queries are routed through `POST /api/v2/telemetry/query`, not direct connections. This ensures:

- Authentication and authorization via TFO's auth guards
- Workspace-scoped data isolation
- Audit logging of all queries
- Rate limiting per organization

### 3. Cost-optimized model selection

| Agent        | Model                 | Cost/Incident | Why                                     |
| ------------ | --------------------- | ------------- | --------------------------------------- |
| Triage       | glm-5.1 (OpenCode Go) | ~$0.01        | Simple classification, fast response    |
| Investigator | claude-sonnet-4-5     | ~$0.05-0.15   | Complex reasoning, evidence correlation |
| Reviewer     | glm-5.1               | ~$0.03-0.08   | Verification, not creative reasoning    |
| Remediator   | glm-5.1               | ~$0.01-0.03   | Action proposal, not investigation      |

**Total: ~$0.10-0.27/incident** (vs ~$0.39 with Claude-only)

### 4. Separate contexts for bias prevention

The Reviewer agent runs in a completely separate context — it only sees the evidence and hypothesis, not the Investigator's thought process. This prevents:

- Confirmation bias (defending conclusions)
- Anchoring bias (overweighting initial findings)
- Sunk cost bias (continuing a failed approach)

### 5. Human-in-the-loop for all mutations

Four tools require explicit human approval via Telegram:

- `scale_deployment` — changes replicas
- `restart_pod` — kills running pods
- `rollback_deploy` — reverts deployments
- `update_alert` — modifies alert rules

The Remediator has a 600-second approval timeout with auto-escalation.
