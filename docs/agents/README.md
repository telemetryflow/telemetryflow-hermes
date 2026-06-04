# Agent Overview

The TelemetryFlow Hermes multi-agent team uses Hermes profiles — each agent has its own SOUL.md, memory, skills, config, and Telegram bot. They share nothing.

## Team Architecture

```mermaid
graph TD
    ALERT["Alert Fired<br/>TFO Webhook / Telegram"]
    TRIAGE["<b>Triage</b><br/>Classify · Route"]
    INV["<b>Investigator</b><br/>Query · Correlate · Hypothesize"]
    REV["<b>Reviewer</b><br/>Verify · Challenge · Approve"]
    REM["<b>Remediator</b><br/>Propose · Gate · Execute"]
    HUMAN["<b>Human</b><br/>Approve / Reject"]

    ALERT --> TRIAGE
    TRIAGE -->|"genuine anomaly"| INV
    TRIAGE -->|"known pattern"| RESOLVED["Auto-resolve<br/>(from MEMORY.md)"]
    TRIAGE -->|"noise"| DISCARD["Discard"]
    INV --> REV
    REV -->|"approved"| REM
    REV -->|"rejected"| INV
    REM -->|"requires_approval"| HUMAN
    HUMAN -->|"approve"| EXECUTE["Execute Action"]
    HUMAN -->|"reject"| ESCALATE["Escalate"]

    style TRIAGE fill:#1a6b4a,stroke:#00d4aa,color:#fff
    style INV fill:#1a3a6b,stroke:#3b82f6,color:#fff
    style REV fill:#6b4a1a,stroke:#f0883e,color:#fff
    style REM fill:#6b1a2a,stroke:#ef4444,color:#fff
```

## Agent Profiles

| Agent            | Model                         | Max Turns | Role                     | Tools                             |
| ---------------- | ----------------------------- | --------- | ------------------------ | --------------------------------- |
| **Triage**       | glm-5.1 (OpenCode Go)         | 30        | Classify and route       | terminal, web, delegation         |
| **Investigator** | claude-sonnet-4-5 (Anthropic) | 45        | Evidence gathering       | terminal, web, delegation         |
| **Reviewer**     | glm-5.1 (OpenCode Go)         | 20        | Independent verification | terminal, web (read-only)         |
| **Remediator**   | glm-5.1 (OpenCode Go)         | 15        | Gated remediation        | terminal, web (approval required) |

## Delegation Model

```mermaid
sequenceDiagram
    participant T as Triage
    participant I as Investigator
    participant R as Reviewer
    participant M as Remediator
    participant H as Human

    Note over T: Alert received
    T->>T: Read MEMORY.md
    T->>T: Classify: critical/known/noise
    alt Known pattern
        T->>T: Auto-resolve
    else Genuine anomaly
        T->>I: delegate(task, context)
        Note over I: Fresh context, full tool access
        I->>I: query_metrics + search_logs + list_traces + get_exemplars
        I->>I: Form root cause hypothesis
        I->>R: delegate(evidence, hypothesis)
        Note over R: Separate context, read-only tools
        R->>R: Verify evidence independently
        R->>M: Approved hypothesis + recommended actions
        Note over M: Approval gate on all write ops
        M->>H: Telegram notification
        H->>M: Approve
        M->>M: Execute remediation
    end
```

## Profile Configuration

Each profile lives at `profiles/<agent-name>/` with:

| File                 | Purpose                                           |
| -------------------- | ------------------------------------------------- |
| `config.yaml`        | Model, turn cap, tool permissions, gateway config |
| `SOUL.md`            | Agent identity and behavioral constraints         |
| `memories/MEMORY.md` | Persistent agent facts (2,200 char max)           |
| `memories/USER.md`   | User profile and preferences (1,375 char max)     |

### Profile Isolation

- **Separate Telegram bots** — each agent has its own `TELEGRAM_BOT_TOKEN_*`
- **Separate memory** — agents don't share MEMORY.md or state.db
- **Separate skills** — each profile can have different skill sets
- **Separate config** — different models, turn caps, tool permissions

## Context Management

### Why Separate Contexts?

A single agent doing everything fills its context window fast. By step 4 it's operating on summaries of summaries, and quality degrades. Separate concerns: each agent has one job, one context, one set of tools.

### Reviewer Bias Prevention

The Reviewer runs in a **completely separate context** with:

- Zero visibility into the Investigator's thought process
- Read-only tools only (can't modify investigation)
- Fresh perspective on evidence and hypothesis

This prevents:

- **Confirmation bias** — defending the Investigator's conclusions
- **Anchoring bias** — overweighting initial findings
- **Sunk cost bias** — continuing a failed investigation approach

## Cost Model

| Agent        | Model             | Turns/Incident | Cost/Turn | Cost/Incident   |
| ------------ | ----------------- | -------------- | --------- | --------------- |
| Triage       | glm-5.1           | 3-5            | ~$0.002   | ~$0.01          |
| Investigator | claude-sonnet-4-5 | 10-20          | ~$0.008   | ~$0.05-0.15     |
| Reviewer     | glm-5.1           | 5-8            | ~$0.005   | ~$0.03-0.08     |
| Remediator   | glm-5.1           | 2-5            | ~$0.003   | ~$0.01-0.03     |
| **Total**    |                   | **20-38**      |           | **~$0.10-0.27** |

## Detailed Agent Docs

- [Triage Agent](./triage.md) — Alert classification and routing
- [Investigator Agent](./investigator.md) — Evidence gathering and root cause analysis
- [Reviewer Agent](./reviewer.md) — Independent verification
- [Remediator Agent](./remediator.md) — Gated remediation
