# Agent Overview

The TelemetryFlow Hermes multi-agent team uses Hermes profiles — each agent has its own SOUL.md, memory, skills, config, and Telegram bot. They share nothing.

## Team Architecture

```mermaid
graph TD
    ALERT["Alert Fired<br/>TFO Webhook / Telegram"]
    TRIAGE["<b>Triage</b><br/>Paranoid Gatekeeper"]
    INV["<b>Investigator</b><br/>Hostile Scientist"]
    REV["<b>Reviewer</b><br/>Professional Skeptic"]
    REM["<b>Remediator</b><br/>Cautious Pragmatist"]
    HUMAN["<b>Human</b><br/>Approve / Reject"]

    ALERT --> TRIAGE
    TRIAGE -->|"genuine anomaly"| INV
    TRIAGE -->|"INCOMPLETE"| CHALLENGE["Issue challenge<br/>to Investigator"]
    TRIAGE -->|"known pattern"| RESOLVED["Auto-resolve<br/>(from MEMORY.md)"]
    TRIAGE -->|"noise"| DISCARD["Discard"]
    CHALLENGE --> INV
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

All agents operate as adversarial scientists — they assume inputs are wrong, actively falsify hypotheses, and never trust without proof.

| Agent            | Model                         | Max Turns | Role                     | Tools                             |
| ---------------- | ----------------------------- | --------- | ------------------------ | --------------------------------- |
| **Triage**       | glm-5.1 (OpenCode Go)         | 30        | Paranoid gatekeeper      | terminal, web, delegation         |
| **Investigator** | claude-sonnet-4-5 (Anthropic) | 45        | Hostile scientist        | terminal, web, delegation         |
| **Reviewer**     | glm-5.1 (OpenCode Go)         | 20        | Professional skeptic     | terminal, web (read-only)         |
| **Remediator**   | glm-5.1 (OpenCode Go)         | 15        | Cautious pragmatist      | terminal, web (approval required) |

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
    T->>T: Classify: critical/known/noise/INCOMPLETE
    alt Known pattern
        T->>T: Auto-resolve
    else INCOMPLETE classification
        T->>I: delegate(task, context, challenge)
    else Genuine anomaly
        T->>I: delegate(task, context)
        Note over I: Fresh context, full tool access
        I->>I: query_metrics + search_logs + list_traces + get_exemplars
        I->>I: Falsify hypotheses — guilty until proven innocent
        I->>I: Document dead hypotheses
        I->>R: delegate(evidence, surviving hypothesis)
        Note over R: Separate context, read-only tools
        R->>R: Hunt for disconfirming evidence
        R->>R: Verdict: CONFIRMED / NEEDS_MORE_EVIDENCE / REJECTED
        R->>M: CONFIRMED hypothesis + recommended actions
        Note over M: Three gates: root cause, proportional, approval
        M->>M: Blast radius analysis
        M->>H: Telegram notification
        H->>M: Approve
        M->>M: Execute remediation
        M->>M: Post-action verification
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

- [Triage Agent](./triage.md) — Paranoid gatekeeper: assumes alerts lie, zero hallucination
- [Investigator Agent](./investigator.md) — Hostile scientist: falsification-first root cause analysis
- [Reviewer Agent](./reviewer.md) — Professional skeptic: hunts disconfirming evidence
- [Remediator Agent](./remediator.md) — Cautious pragmatist: three-gate remediation
