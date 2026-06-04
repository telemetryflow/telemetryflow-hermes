# TelemetryFlow Hermes — Documentation Wiki

Self-improving AI agent integration for TelemetryFlow Observability Platform using Hermes Agent by Nous Research.

## Table of Contents

### Getting Started

| Document                                        | Description                                  |
| ----------------------------------------------- | -------------------------------------------- |
| [Getting Started](./getting-started.md)         | Installation, setup, first investigation     |
| [Configuration](./configuration/environment.md) | Environment variables, config.yaml reference |

### Architecture

| Document                                   | Description                                 |
| ------------------------------------------ | ------------------------------------------- |
| [Architecture Overview](./architecture.md) | System design, data flow, component diagram |

### Agents

| Document                                       | Description                                  |
| ---------------------------------------------- | -------------------------------------------- |
| [Agent Overview](./agents/README.md)           | Multi-agent team design and delegation model |
| [Triage Agent](./agents/triage.md)             | Alert classification and routing             |
| [Investigator Agent](./agents/investigator.md) | Evidence gathering and root cause analysis   |
| [Reviewer Agent](./agents/reviewer.md)         | Independent verification and bias detection  |
| [Remediator Agent](./agents/remediator.md)     | Gated remediation with human approval        |

### Tools

| Document                               | Description                                |
| -------------------------------------- | ------------------------------------------ |
| [Tools Overview](./tools/README.md)    | 23 plugin tools and their categories       |
| [Tool Reference](./tools/reference.md) | Complete parameter reference for all tools |

### Skills

| Document                                 | Description                           |
| ---------------------------------------- | ------------------------------------- |
| [Skills Overview](./skills/README.md)    | 11 bundled skills and self-evolution  |
| [Skill Reference](./skills/reference.md) | All skill descriptions and procedures |

### API Integration

| Document                                  | Description                                 |
| ----------------------------------------- | ------------------------------------------- |
| [API Overview](./api/README.md)           | TFO Platform API integration patterns       |
| [Authentication](./api/authentication.md) | JWT, API Key, and Ingestion auth flows      |
| [LLM Module](./api/llm-module.md)         | TFO LLM chat, insights, provider management |
| [Context Types](./api/context-types.md)   | All 95+ ContextType values and usage        |

### Deployment

| Document                                            | Description                                 |
| --------------------------------------------------- | ------------------------------------------- |
| [Deployment Overview](./deployment/README.md)       | Standard and air-gapped deployment          |
| [Standard Deployment](./deployment/standard.md)     | Full deployment with external LLM providers |
| [Air-Gapped Deployment](./deployment/air-gapped.md) | Offline deployment with Ollama              |

### Security

| Document                                                  | Description             |
| --------------------------------------------------------- | ----------------------- |
| [Security Overview](./security/README.md)                 | Layered security model  |
| [ClickHouse Read-Only](./security/clickhouse-readonly.md) | Database access control |

### Operations

| Document                                           | Description                   |
| -------------------------------------------------- | ----------------------------- |
| [Operations Overview](./operations/README.md)      | Day-to-day operations guide   |
| [Cron Jobs](./operations/cron-jobs.md)             | Scheduled investigation tasks |
| [Lifecycle Hooks](./operations/hooks.md)           | Event-driven automation       |
| [Troubleshooting](./operations/troubleshooting.md) | Common issues and solutions   |

## Presentations

| Document                                     | Description                  |
| -------------------------------------------- | ---------------------------- |
| [TFO + Hermes Presentation](./tfo-hermes.md) | Marp slide deck (1154 lines) |

## Quick Links

- **Repository**: [telemetryflow-hermes](https://github.com/telemetryflow/telemetryflow-hermes)
- **TFO Platform**: [telemetryflow-platform-monolith](https://github.com/telemetryflow/telemetryflow-platform-monolith)
- **Hermes Agent**: [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
- **Website**: [telemetryflow.id](https://telemetryflow.id)
