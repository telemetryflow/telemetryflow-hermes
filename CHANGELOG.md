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

# Changelog

All notable changes to **TelemetryFlow Hermes** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-06-04

### Summary

**Initial public release** — Complete multi-agent AI incident response integration for TelemetryFlow Observability (TFO) Platform. Four specialised agents (Triage, Investigator, Reviewer, Remediator) form an autonomous pipeline with 23 plugin tools, 11 bundled skills, comprehensive documentation, and full CI/CD.

```mermaid
flowchart LR
    A["Alert Fired"] --> B["Triage<br/>glm-5.1"]
    B --> C["Investigator<br/>claude-sonnet-4-5"]
    C --> D["Reviewer<br/>glm-5.1"]
    D --> E["Remediator<br/>glm-5.1"]
    E --> F["Human Approval<br/>(Telegram)"]
    F --> G["Execute Action"]
```

### Added

#### Agents — Multi-Agent Team

- **Triage Agent** — Alert classification, severity assessment, known pattern auto-resolution, delegation to Investigator
- **Investigator Agent** — ClickHouse evidence gathering (metrics, logs, traces, exemplars), cross-signal correlation, root cause hypothesis formation
- **Reviewer Agent** — Independent verification in separate context, zero investigation bias, read-only tools only
- **Remediator Agent** — Gated remediation proposals (scale, restart, rollback, update_alert), 600s approval timeout with auto-escalation

#### Plugin Tools — 23 Tools (Python stdlib only)

- **Core Telemetry (5)**: `query_metrics`, `search_logs`, `list_traces`, `get_exemplars`, `query_correlations`
- **Infrastructure (3)**: `check_k8s`, `check_infra`, `check_db_monitoring` (16 database types)
- **Platform (5)**: `check_uptime`, `query_ai_intelligence`, `query_platform`, `query_account`, `manage_data_masking`
- **LLM Module (6)**: `chat_with_context`, `stream_chat`, `manage_conversation`, `generate_insight`, `query_llm_usage`, `manage_provider`
- **Remediation (4)**: `scale_deployment`, `restart_pod`, `rollback_deploy`, `update_alert` — all marked `requires_approval: true`

#### Skills — 11 Bundled

- **Observability (9)**: `k8s-pod-debug`, `payments-api-oom-rca`, `clickhouse-query-patterns`, `tfql-natural-language`, `alert-triage`, `remediation-gate`, `cross-signal-correlation`, `memory-pressure-investigation`, `tfo-llm-api`
- **Database Monitoring (2)**: `slow-query-detection`, `qan-analysis`

#### TFO LLM Module Integration

- Full ContextCollector support with 95+ ContextType values
- Chat endpoint (`/api/v2/llm/chat/message`) with automatic telemetry context injection
- Streaming chat (`/api/v2/llm/chat/stream`) via SSE
- Insight generation (`/api/v2/llm/insights/generate`) — 5 types: chronology, prediction, recommendation, root-cause, pattern
- Provider management (`/api/v2/llm/providers`) — 15 types with AES-256-GCM encryption
- Conversation management — list, get, archive, delete
- LLM usage analytics from ClickHouse — summary, by-provider, by-model, by-context, interval trends

#### Authentication

- **Method A: API Key** — `tfs_*` format, SHA-256 hashed at rest, recommended for agents
- **Method B: JWT Login** — Email/password → Bearer token, user-scoped
- **Method C: Ingestion Headers** — `tfk_*/tfs_*` key pair for OTEL Collector agents

#### Security

- ClickHouse read-only user (`hermes_readonly`) with table-level SELECT grants on 20 telemetry tables
- Mandatory `workspace_id` on all ClickHouse queries
- Organization-scoped LLM endpoint access
- 90-turn hard cap per agent task
- Separate reviewer context for bias prevention
- Python stdlib only — zero pip dependencies

#### Scheduled Tasks — 6 Cron Jobs

| Job                    | Schedule  | Agent        | Purpose                     |
| ---------------------- | --------- | ------------ | --------------------------- |
| `health-check-metrics` | Every 15m | Investigator | Anomaly spike detection     |
| `log-error-sweep`      | Every 30m | Investigator | New ERROR pattern detection |
| `k8s-health-check`     | Every 10m | Investigator | Pod health monitoring       |
| `db-slow-query-check`  | Every 1h  | Investigator | QAN slow query detection    |
| `alert-fatigue-review` | Every 6h  | Triage       | Noise alert suppression     |
| `skill-curator`        | Every 7d  | Default      | Skill garbage collection    |

#### Lifecycle Hooks — 3 Hooks

- `on-alert-fired.sh` — Alert enrichment and logging before triage
- `pre-investigation.sh` — Investigation context logging
- `post-remediation.sh` — Remediation outcome tracking and verification scheduling

#### Deployment

- **Standard deployment** — External LLM providers (Anthropic, Zhipu/OpenCode Go)
- **Air-gapped deployment** — Ollama local models, zero external network
- 5 deployment scripts (`install.sh`, `setup-profiles.sh`, `setup-telegram.sh`, `verify-pipeline.sh`, `deploy-air-gapped.sh`)

#### Documentation — 28 Pages

- Wiki index with table of contents
- Architecture with system diagrams and sequence diagrams
- Agent docs (triage, investigator, reviewer, remediator) with mermaid workflows
- Complete tool reference with all parameters
- API docs (authentication, LLM module, context types)
- Deployment guides (standard, air-gapped)
- Security documentation
- Environment variable reference
- Operations guide (cron, hooks, troubleshooting)
- Marp presentation (1,154 lines)

#### Testing — 105 Tests, 95%+ Coverage

- `tests/conftest.py` — Shared fixtures (mock_env, mock_urlopen, capture_stdout, mock_exit)
- `tests/mocks/tfo_api.py` — MockTFOApi, mock response factories
- `tests/unit/test_shared.py` — \_shared.py utilities (API helpers, parse_args, constants)
- `tests/unit/test_*.py` — 21 tool test files
- `tests/integration/test_pipeline.py` — End-to-end pipeline tests

#### CI/CD

- **GitHub Actions** — 5-job CI (lint, test, security, coverage, summary) + release workflow
- **GitLab CI/CD** — 5-stage pipeline matching GitHub Actions
- **Makefile** — 10 CI targets (ci-deps, ci-lint, ci-test-unit, ci-test-integration, ci-test, ci-security, ci-coverage, ci-validate, ci-pipeline, ci)

### Technical Details

- **Zero pip dependencies** — all tools use Python stdlib (`urllib`, `json`, `sys`, `os`)
- **All queries through TFO API** — ClickHouse accessed via `POST /api/v2/telemetry/query`, not directly
- **Cost model** — ~$0.10-0.27/incident (vs ~$0.39 Claude-only)
- **MTTR improvement** — ~23 seconds (vs ~40 minutes manual)

---

**Built with ❤️ by Telemetri Data Indonesia**
