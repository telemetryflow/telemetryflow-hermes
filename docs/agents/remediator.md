# Remediator Agent

Cautious pragmatist. Three gates before any action: confirmed root cause, proportional response, human approval. Performs blast radius analysis on every proposed action. Post-action verification is mandatory. Never auto-executes.

## Role

```mermaid
graph TD
    INPUT["CONFIRMED Hypothesis<br/>from Reviewer"] --> GATE1["Gate 1: Confirmed<br/>Root Cause?"]
    GATE1 -->|"no"| REJECT1["Reject: Insufficient<br/>root cause evidence"]
    GATE1 -->|"yes"| GATE2["Gate 2: Proportional<br/>Response?"]
    GATE2 -->|"no"| REJECT2["Reject: Action<br/>disproportionate"]
    GATE2 -->|"yes"| BLAST["Blast Radius<br/>Analysis"]
    BLAST --> OPTIONS["Generate Options<br/>with Risk Assessment"]
    OPTIONS --> GATE3["Gate 3: Human<br/>Approval"]
    GATE3 -->|"scale"| SCALE["scale_deployment<br/>⚠ requires_approval"]
    GATE3 -->|"restart"| RESTART["restart_pod<br/>⚠ requires_approval"]
    GATE3 -->|"rollback"| ROLLBACK["rollback_deploy<br/>⚠ requires_approval"]
    GATE3 -->|"update_alert"| ALERT["update_alert<br/>⚠ requires_approval"]
    GATE3 -->|"escalate"| ESCALATE["Escalate to Human<br/>(no approval needed)"]

    SCALE --> NOTIFY["Telegram Notification"]
    RESTART --> NOTIFY
    ROLLBACK --> NOTIFY
    ALERT --> NOTIFY
    NOTIFY --> HUMAN["Human Decision"]
    HUMAN -->|"approve"| EXECUTE["Execute Action"]
    HUMAN -->|"reject"| CANCEL["Cancel + Log"]
    HUMAN -->|"timeout 10m"| AUTO_ESC["Auto-Escalate"]
    EXECUTE --> VERIFY["Post-Action<br/>Verification<br/>(Mandatory)"]

    style GATE1 fill:#6b1a2a,stroke:#ef4444,color:#fff
    style GATE2 fill:#6b1a2a,stroke:#ef4444,color:#fff
    style GATE3 fill:#6b1a2a,stroke:#ef4444,color:#fff
    style NOTIFY fill:#1a3a6b,stroke:#3b82f6,color:#fff
    style EXECUTE fill:#1a6b4a,stroke:#00d4aa,color:#fff
    style VERIFY fill:#1a6b4a,stroke:#00d4aa,color:#fff
```

## Configuration

| Setting                      | Value                        |
| ---------------------------- | ---------------------------- |
| **Model**                    | glm-5.1 (OpenCode Go)        |
| **Max Turns**                | 15                           |
| **Timeout**                  | 180s                         |
| **Read-only**                | **No** (unique among agents) |
| **Require Approval**         | Yes (600s timeout)           |
| **Auto-Escalate on Timeout** | Yes                          |

## SOUL.md Identity

```
You are a CAUTIOUS PRAGMATIST. You never auto-execute any action. Three
gates stand between you and remediation: (1) Is the root cause CONFIRMED
by the Reviewer? (2) Is the proposed response proportional to the
incident? (3) Has a human explicitly approved? You perform blast radius
analysis on every proposed action — who and what else is affected? After
any action, post-action verification is MANDATORY, not optional. You
present clear risk assessments and never execute without explicit consent.
When uncertain, escalate to human. You would rather be slow and safe than
fast and sorry.
```

## Approval-Gated Tools

These 4 tools are marked `requires_approval: true` in `plugin.yaml`:

| Tool               | Action                     | Risk                                 | Approval Required |
| ------------------ | -------------------------- | ------------------------------------ | ----------------- |
| `scale_deployment` | Change replica count       | Medium — affects resource allocation | Yes               |
| `restart_pod`      | Kill and restart pods      | Medium — brief downtime              | Yes               |
| `rollback_deploy`  | Revert to previous version | High — version change                | Yes               |
| `update_alert`     | Modify alert rules         | Medium — monitoring gap risk         | Yes               |

## Telegram Notification Format

```
🔧 REMEDIATION REQUEST

Alert: payments-api p95 latency 640ms
Root Cause: OOM after v2.4.1 deploy (memory spike 512→890MiB)
Evidence:
  📊 metrics: memory spike confirmed
  📋 logs: 512 OOM kill messages
  🔗 traces: 89 slow spans correlated
Reviewer: ✅ CONFIRMED

Proposed Action: Rollback to v2.4.0
Blast Radius: payments-api deployment only (3 pods)
Risk: LOW — v2.4.0 was stable for 14 days
Impact: ~30s downtime during rollout
Post-Action Verification: Monitor memory + error rate for 5 minutes

[Approve] [Reject] [Manual Review]
```

## Approval Flow

```mermaid
sequenceDiagram
    participant R as Remediator
    participant T as Telegram
    participant H as Human
    participant TF as TelemetryFlow

    R->>R: Assess remediation options
    R->>R: Blast radius analysis
    R->>T: Send approval request
    T->>H: Push notification

    alt Human approves
        H->>T: Tap [Approve]
        T->>R: Approval received
        R->>TF: Execute action (e.g., rollback_deploy)
        TF->>R: Action confirmed
        R->>R: Post-action verification (mandatory)
        R->>T: Remediation complete + verification results
    else Human rejects
        H->>T: Tap [Reject]
        T->>R: Rejection received
        R->>R: Log rejection, suggest alternatives
    else Timeout (10 minutes)
        R->>R: Auto-escalate
        R->>T: Escalation notification
    end
```

## Risk Assessment Matrix

| Action            | Downtime | Reversible         | Blast Radius        | Default Risk |
| ----------------- | -------- | ------------------ | ------------------- | ------------ |
| Scale up          | None     | Yes (scale down)   | Single deployment   | Low          |
| Scale down        | None     | Yes (scale up)     | Single deployment   | Medium       |
| Restart pod       | 5-30s    | Yes (automatic)    | Single pod          | Low          |
| Rollback deploy   | 30-120s  | Yes (roll forward) | Entire deployment   | Medium       |
| Update alert rule | None     | Yes (revert)       | Monitoring coverage | Low-Medium   |

## Escalation Criteria

The Remediator auto-escalates (no approval needed) when:

1. **Approval timeout** — 600 seconds with no response
2. **Root cause unconfirmed** — Reviewer verdict was not CONFIRMED
3. **Disproportionate response** — no proportional action available
4. **Multiple services affected** — blast radius too large
5. **Production database** — any action touching data stores
6. **Multiple simultaneous incidents** — potential cascade

## Post-Remediation

After executing an approved action, the `post-remediation.sh` hook performs **mandatory** verification:

1. Logs outcome to `~/.hermes/logs/remediations.log`
2. Schedules a verification check (30 seconds later)
3. Checks: metrics return to baseline, no new error spikes, pod status healthy
4. **Post-action verification is not optional** — if metrics haven't normalized, escalates
5. Updates MEMORY.md with remediation result

## Memory Usage

MEMORY.md tracks:

- Successful remediation patterns per service
- Approval rates (which actions get approved vs rejected)
- Mean time to approve (team responsiveness)
- Recurring remediation needs (indicates deeper issues)
