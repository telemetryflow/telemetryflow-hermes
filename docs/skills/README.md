# Skills Overview

29 bundled skills across 18 categories covering all 20 TFO Platform modules. Skills are Hermes Agent's procedural memory — they define **how** the agent does things.

## Self-Evolving Skills

```mermaid
graph LR
    A["Encounter Problem"] --> B["Solve via Trial & Error"]
    B --> C["Save as SKILL.md"]
    C --> D["Next Similar Problem"]
    D --> E["Load Skill"]
    E --> A

    style C fill:#1a6b4a,stroke:#00d4aa,color:#fff
```

Skills are automatically created when the Investigator:

- Completes a complex task (5+ tool calls)
- Hits errors or dead ends and finds the working path
- Gets corrected by the Reviewer
- Discovers a non-trivial investigation workflow

## Bundled Skills

### Observability (9 skills)

| Skill                           | Category      | Trigger                                      |
| ------------------------------- | ------------- | -------------------------------------------- |
| `k8s-pod-debug`                 | Kubernetes    | CrashLoopBackOff, OOMKilled, pod failures    |
| `payments-api-oom-rca`          | RCA           | payments-api memory spike, OOM pattern       |
| `clickhouse-query-patterns`     | Query         | Common ClickHouse query templates for TFO    |
| `tfql-natural-language`         | Query         | Natural language to TFQL conversion          |
| `alert-triage`                  | Triage        | Alert classification and severity assessment |
| `remediation-gate`              | Remediation   | Approval gate workflow for write actions     |
| `cross-signal-correlation`      | Investigation | Correlating metrics ↔ logs ↔ traces          |
| `memory-pressure-investigation` | Investigation | Node/pod memory pressure debugging           |
| `tfo-llm-api`                   | API           | TFO LLM API v2.0 reference (74 ContextTypes) |

### Database Monitoring (2 skills)

| Skill                  | Category | Trigger                                |
| ---------------------- | -------- | -------------------------------------- |
| `slow-query-detection` | QAN      | Slow query identification and analysis |
| `qan-analysis`         | QAN      | Query Analytics deep-dive procedures   |

## Skill Format

Each skill is a Markdown file with YAML frontmatter:

```markdown
---
name: k8s-pod-debug
description: >
  Activate for crashing pods, CrashLoopBackOff,
  "why is my pod restarting", container failures.
version: 1.2.0
author: agent
platforms: [linux, macos]
---

## Procedure

1. Get pod status → check events → pull logs
2. Look for OOMKilled, ImagePullBackOff, config errors

## Pitfalls

- Forgetting --previous flag on restarted containers

## Verification

- Pod stays Running with 0 restarts for 5+ minutes
```

## Progressive Disclosure

```mermaid
graph TD
    L0["Level 0: Names + descriptions<br/>~3k tokens for full catalog"]
    L1["Level 1: Full skill content<br/>Loaded on demand"]
    L2["Level 2: Reference files<br/>Drilled into specifically"]

    L0 -->|"agent needs this skill"| L1
    L1 -->|"needs reference data"| L2

    style L0 fill:#1a3a6b,stroke:#3b82f6,color:#fff
    style L1 fill:#1a6b4a,stroke:#00d4aa,color:#fff
    style L2 fill:#6b4a1a,stroke:#f0883e,color:#fff
```

## Curator — Skill Garbage Collection

```mermaid
graph TD
    CHECK["7 days since last run?<br/>Agent idle 2+ hours?"]
    PHASE1["Phase 1: Automatic<br/>(deterministic, no LLM)"]
    PHASE2["Phase 2: LLM Review<br/>(up to 8 iterations)"]
    STALE["30 days unused → stale"]
    ARCHIVE["90 days unused → archived"]
    REVIEW["Forked agent reviews<br/>all agent-authored skills"]
    DECISION["Per-skill:<br/>keep · patch · consolidate · archive"]

    CHECK -->|"yes"| PHASE1
    CHECK -->|"no"| SKIP["Skip"]
    PHASE1 --> STALE
    PHASE1 --> ARCHIVE
    PHASE1 --> PHASE2
    PHASE2 --> REVIEW
    REVIEW --> DECISION

    style PHASE2 fill:#6b4a1a,stroke:#f0883e,color:#fff
    style DECISION fill:#1a6b4a,stroke:#00d4aa,color:#fff
```

### Safety Constraints

- **Never touches** bundled or hub-installed skills
- **Never auto-deletes** — worst case is archival (recoverable)
- **Snapshot before every pass** — `tar.gz` of entire skills directory
- **Pin protection** — `hermes curator pin <skill>` prevents archival

## Full Reference

See [Skill Reference](./reference.md) for detailed procedures.
