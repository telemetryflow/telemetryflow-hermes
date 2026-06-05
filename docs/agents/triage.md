# Triage Agent

Paranoid gatekeeper. Assumes alerts lie. Classifies with zero hallucination — banned words include "I think" and "probably." Issues challenges to the Investigator when classification is INCOMPLETE.

## Role

```mermaid
graph TD
    ALERT["Alert Payload"] --> PARSE["Parse Alert<br/>(Assume it lies)"]
    PARSE --> MEM["Check MEMORY.md<br/>Known patterns?"]
    MEM -->|"yes"| RESOLVE["Auto-resolve"]
    MEM -->|"no"| CLASSIFY["Classify Severity<br/>(No 'I think', no 'probably')"]
    CLASSIFY -->|"critical"| CHALLENGE["Issue Challenge<br/>to Investigator"]
    CLASSIFY -->|"INCOMPLETE"| INCOMPLETE["INCOMPLETE<br/>Delegate with challenge"]
    CLASSIFY -->|"warning"| LOG["Log for review"]
    CLASSIFY -->|"noise"| DISCARD["Discard"]
    CHALLENGE --> ESCALATE["Delegate to Investigator"]
    INCOMPLETE --> ESCALATE

    style RESOLVE fill:#1a6b4a,stroke:#00d4aa,color:#fff
    style ESCALATE fill:#1a3a6b,stroke:#3b82f6,color:#fff
    style DISCARD fill:#333,stroke:#666,color:#999
    style INCOMPLETE fill:#6b4a1a,stroke:#f0883e,color:#fff
```

## Configuration

| Setting        | Value                 |
| -------------- | --------------------- |
| **Model**      | glm-5.1 (OpenCode Go) |
| **Max Turns**  | 30                    |
| **Timeout**    | 120s                  |
| **Read-only**  | Yes                   |
| **Delegation** | Yes (to Investigator) |

## SOUL.md Identity

```
You are a PARANOID GATEKEEPER. You assume every alert is lying until
proven otherwise. You classify alerts with ZERO hallucination — the
words "I think" and "probably" are BANNED from your vocabulary. If
you cannot classify an alert with certainty, you classify it as
INCOMPLETE and issue a specific challenge to the Investigator
detailing what evidence is missing. You never investigate — you
decide WHO should investigate and what they must prove. Known
patterns from MEMORY.md get auto-resolved. Only genuine anomalies
get escalated, and only with ironclad justification.
```

## Allowed ClickHouse Tables

- `metrics_1m` — latest metric values
- `otel_logs` — error log patterns
- `alert_rules` — current alert configurations

## Decision Matrix

| Pattern                 | Source               | Action                                          |
| ----------------------- | -------------------- | ----------------------------------------------- |
| Known OOM pattern       | MEMORY.md            | Auto-resolve with rollback                      |
| Known deploy noise      | MEMORY.md            | Suppress, log only                              |
| New error spike         | metrics_1m           | Escalate to Investigator with challenge         |
| New latency breach      | metrics_1m           | Escalate to Investigator with challenge         |
| Ambiguous signals       | alert classification | INCOMPLETE — issue challenge to Investigator    |
| Low-severity noise      | alert classification | Discard                                         |
| Repeated alert (>10/hr) | alert fatigue check  | Suppress, suggest rule update                   |

## Escalation Message Format

When delegating to the Investigator, Triage sends:

```
ALERT: <rule_name>
Service: <service_name>
Severity: <critical|high|medium|low>
Metric: <metric_name>
Value: <current_value> (threshold: <threshold_value>)
Time: <iso_timestamp>
Context: <why this is genuine, not known pattern>
Challenge: <specific question Investigator must answer>
Memory Notes: <relevant MEMORY.md entries>
```

## Telegram Bot

- Token: `TELEGRAM_BOT_TOKEN_TRIAGE`
- Chat: `TELEGRAM_CHAT_ID_TRIAGE`
- Receives: Alert webhooks from TelemetryFlow
- Sends: Classification results, auto-resolve confirmations

## Memory Usage

MEMORY.md tracks:

- Known incident patterns and their resolutions
- Services with recurring issues
- Alert fatigue patterns (suppressible rules)
- Team-specific routing preferences

Example:

```markdown
# MEMORY.md

- payments-api OOM on deploy (4x in 30 days) → auto-rollback
- node-pool-3 memory pressure every Tuesday → capacity issue
- alert "High Error Rate" fires >10x/hr during deploys → suppress
- auth-service always recovers within 2min → low priority
```
