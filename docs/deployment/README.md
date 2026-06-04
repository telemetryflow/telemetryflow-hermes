# Deployment Overview

Deploy TelemetryFlow Hermes in standard (cloud-connected) or air-gapped (fully offline) configurations.

## Deployment Models

```mermaid
graph TD
    CHOICE{"Deployment Model?"}

    STD["Standard Deployment<br/>External LLM providers<br/>Full feature set"]
    AIR["Air-Gapped Deployment<br/>Ollama local models<br/>No external network"]

    CHOICE -->|"Internet available"| STD
    CHOICE -->|"Zero egress required"| AIR

    STD --> STD_STEPS["1. Install Hermes Agent<br/>2. Configure API keys<br/>3. Deploy profiles<br/>4. Start Telegram gateways"]
    AIR --> AIR_STEPS["1. Install Hermes Agent<br/>2. Install Ollama + models<br/>3. Deploy profiles (ollama config)<br/>4. Start Telegram gateways"]

    style STD fill:#1a3a6b,stroke:#3b82f6,color:#fff
    style AIR fill:#1a6b4a,stroke:#00d4aa,color:#fff
```

## Prerequisites

### Common (both models)

| Requirement              | Purpose                          |
| ------------------------ | -------------------------------- |
| Python 3.8+              | Plugin tool runtime              |
| TelemetryFlow Platform   | Running instance with API access |
| ClickHouse               | Telemetry data storage           |
| Kubernetes cluster       | For remediation actions          |
| Telegram bot tokens (4x) | Agent communication              |
| `kubectl` configured     | K8s API access                   |

### Standard Only

| Requirement           | Purpose                                |
| --------------------- | -------------------------------------- |
| Anthropic API key     | Investigator agent (claude-sonnet-4-5) |
| Zhipu/OpenCode Go key | Triage/Reviewer/Remediator (glm-5.1)   |

### Air-Gapped Only

| Requirement          | Purpose                          |
| -------------------- | -------------------------------- |
| Ollama installed     | Local LLM inference              |
| Model weights pulled | `llama3.3`, `mistral-nemo`, etc. |
| No external network  | Full offline operation           |

## Quick Deploy

```bash
# Clone
git clone https://github.com/telemetryflow/telemetryflow-hermes.git
cd telemetryflow-hermes

# Configure
cp .env.example ~/.hermes/.env
# Edit ~/.hermes/.env with your keys

# Deploy
make setup
make telegram
make verify
make deploy
```

## Next Steps

- [Standard Deployment](./standard.md) — Full deployment with external LLM providers
- [Air-Gapped Deployment](./air-gapped.md) — Offline deployment with Ollama
