# Operations Overview

Day-to-day operations guide for TelemetryFlow Hermes — cron jobs, lifecycle hooks, and troubleshooting.

## Operations Dashboard

```mermaid
graph TB
    subgraph "Scheduled Tasks"
        C1["Metrics Check<br/>every 15m"]
        C2["Log Sweep<br/>every 30m"]
        C3["K8s Health<br/>every 10m"]
        C4["DB Slow Query<br/>every 1h"]
        C5["Alert Fatigue<br/>every 6h"]
        C6["Skill Curator<br/>every 7d"]
    end

    subgraph "Lifecycle Hooks"
        H1["on-alert-fired.sh<br/>Alert enrichment"]
        H2["pre-investigation.sh<br/>Context logging"]
        H3["post-remediation.sh<br/>Outcome tracking"]
    end

    subgraph "Monitoring"
        M1["make status<br/>Gateway health"]
        M2["~/.hermes/logs/<br/>Activity logs"]
        M3["hermes doctor<br/>Agent diagnostics"]
    end

    C1 & C2 & C3 & C4 & C5 & C6 --> OUT["cron/output/"]
    H1 --> LOGS["~/.hermes/logs/"]
    H2 --> LOGS
    H3 --> LOGS
```

## Common Operations

| Task                    | Command                                     | Description                        |
| ----------------------- | ------------------------------------------- | ---------------------------------- |
| Check status            | `make status`                               | Show all 4 gateway statuses        |
| View investigation logs | `tail -f ~/.hermes/logs/investigations.log` | Real-time investigations           |
| View remediation logs   | `tail -f ~/.hermes/logs/remediations.log`   | Real-time remediations             |
| Run diagnostics         | `make doctor`                               | Hermes agent health check          |
| Restart gateways        | `make deploy`                               | Restart all 4 gateways             |
| Clean installation      | `make clean`                                | Remove all profiles/skills/plugins |
| Run curator             | `hermes curator run`                        | Manual skill cleanup               |
| Verify pipeline         | `make verify`                               | Full pipeline verification         |

## Sub-Pages

- [Cron Jobs](./cron-jobs.md) — 6 scheduled investigation tasks
- [Lifecycle Hooks](./hooks.md) — 3 event-driven automation scripts
- [Troubleshooting](./troubleshooting.md) — Common issues and solutions
