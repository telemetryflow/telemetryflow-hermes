# Reviewer Agent

Independent verifier running in a completely separate context. Only sees evidence and hypothesis — never the Investigator's thought process.

## Role

```mermaid
graph TD
    INPUT["Evidence + Hypothesis<br/>from Investigator"] --> VERIFY["Verify Each<br/>Evidence Point"]
    VERIFY --> M["Re-query Metrics<br/>(independent check)"]
    VERIFY --> L["Re-query Logs<br/>(independent check)"]
    VERIFY --> T["Re-query Traces<br/>(independent check)"]
    M --> ASSESS["Assess Hypothesis"]
    L --> ASSESS
    T --> ASSESS
    ASSESS --> ALT["Check Alternatives<br/>Not Considered"]
    ALT --> VERDICT["Verdict"]
    VERDICT -->|"approved"| REM["Delegate to Remediator"]
    VERDICT -->|"rejected"| INV["Return to Investigator<br/>with notes"]

    style VERIFY fill:#6b4a1a,stroke:#f0883e,color:#fff
    style VERDICT fill:#6b4a1a,stroke:#f0883e,color:#fff
```

## Configuration

| Setting        | Value                 |
| -------------- | --------------------- |
| **Model**      | glm-5.1 (OpenCode Go) |
| **Max Turns**  | 20                    |
| **Timeout**    | 180s                  |
| **Read-only**  | Yes                   |
| **Delegation** | No                    |

## SOUL.md Identity

```
You are an independent incident reviewer. You only see the evidence
and the hypothesis — not the Investigator's thought process. You
check for confirmation bias, missed alternatives, and unsupported
conclusions. You never modify the investigation.
```

## Allowed ClickHouse Tables

Same as Investigator (read-only verification):

| Table         | Purpose                    |
| ------------- | -------------------------- |
| `metrics_1m`  | Verify metric claims       |
| `metrics_5m`  | Verify metric trends       |
| `metrics_1h`  | Verify historical patterns |
| `otel_logs`   | Verify log evidence        |
| `otel_traces` | Verify trace evidence      |
| `exemplars`   | Verify metric-trace links  |

## Review Checklist

The Reviewer follows a structured checklist for every investigation:

```mermaid
graph TD
    E1["1. Evidence Completeness<br/>All signals checked?"]
    E2["2. Metric Accuracy<br/>Do numbers match claims?"]
    E3["3. Log Correlation<br/>Do logs support hypothesis?"]
    E4["4. Trace Evidence<br/>Are spans correctly interpreted?"]
    E5["5. Alternative Causes<br/>Other explanations possible?"]
    E6["6. Historical Consistency<br/>Matches MEMORY.md patterns?"]
    E7["7. Remediation Proportionality<br/>Is proposed action proportional?"]

    E1 --> E2 --> E3 --> E4 --> E5 --> E6 --> E7
    E7 --> VERDICT["Verdict: Approved / Approved with Caveats / Rejected"]
```

### Verdict Outcomes

| Verdict                   | Meaning                             | Next Step                            |
| ------------------------- | ----------------------------------- | ------------------------------------ |
| **Approved**              | Evidence supports hypothesis fully  | Delegate to Remediator               |
| **Approved with caveats** | Mostly correct, minor gaps          | Delegate to Remediator with notes    |
| **Rejected**              | Evidence doesn't support hypothesis | Return to Investigator with feedback |

## Bias Prevention

### Why Separate Context?

```mermaid
graph LR
    subgraph "Investigator Context"
        I_THOUGHTS["Investigator thoughts<br/>(hidden from Reviewer)"]
        I_EVIDENCE["Evidence gathered"]
        I_HYPOTHESIS["Root cause hypothesis"]
    end

    subgraph "Reviewer Context"
        R_EVIDENCE["Evidence only"]
        R_HYPOTHESIS["Hypothesis only"]
        R_INDEPENDENT["Independent verification"]
    end

    I_EVIDENCE -->|"passed"| R_EVIDENCE
    I_HYPOTHESIS -->|"passed"| R_HYPOTHESIS
    I_THOUGHTS -.-x|"NOT passed"| R_INDEPENDENT

    style I_THOUGHTS fill:#333,stroke:#666,color:#999,stroke-dasharray: 5 5
    style R_INDEPENDENT fill:#1a6b4a,stroke:#00d4aa,color:#fff
```

The Reviewer never sees:

- The Investigator's reasoning process
- Which tools were used and in what order
- Dead ends the Investigator explored
- Confidence scores from intermediate steps

This prevents:

- **Confirmation bias** — defending conclusions
- **Anchoring bias** — overweighting first findings
- **Sunk cost bias** — continuing failed approaches

## Telegram Bot

- Token: `TELEGRAM_BOT_TOKEN_REVIEWER`
- Chat: `TELEGRAM_CHAT_ID_REVIEWER`
- Receives: Evidence + hypothesis packages from Investigator
- Sends: Review verdicts with detailed reasoning

## Memory Usage

MEMORY.md tracks:

- Review patterns (what tends to be wrong with hypotheses)
- Common alternative causes for specific services
- Reviewer calibration (confidence vs accuracy)
