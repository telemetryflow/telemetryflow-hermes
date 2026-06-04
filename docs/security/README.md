# Security Overview

Layered security model for TelemetryFlow Hermes — from authentication to database access to remediation gates.

## Security Layers

```mermaid
graph TB
    subgraph "Layer 1: Authentication"
        L1_APIK["API Key (tfs_xxxx)<br/>SHA-256 hashed"]
        L1_JWT["JWT Bearer Token<br/>HS256 signed"]
        L1_ING["Ingestion Headers<br/>Key ID + Secret"]
    end

    subgraph "Layer 2: Authorization"
        L2_PERM["Permissions Guard<br/>llm:chat · llm:read · llm:write<br/>llm:insights · llm:delete · telemetry:read"]
        L2_ORG["Organization Scoping<br/>All queries scoped to org"]
        L2_WS["Workspace Isolation<br/>Mandatory workspace_id"]
    end

    subgraph "Layer 3: Database Access"
        L3_RO["Read-Only User<br/>hermes_readonly"]
        L3_TBL["Table-Level Grants<br/>20 tables only"]
        L3_NET["Network Policy<br/>No direct ClickHouse access"]
    end

    subgraph "Layer 4: Agent Constraints"
        L4_TURN["90-Turn Hard Cap<br/>Prevents runaway loops"]
        L4_READONLY["Read-Only Tools<br/>3 of 4 agents can't write"]
        L4_GATE["Approval Gates<br/>All mutations require human"]
        L4_TIMEOUT["Approval Timeout<br/>600s → auto-escalate"]
    end

    subgraph "Layer 5: Data Protection"
        L5_ENV["Secrets in .env only<br/>Never in config.yaml"]
        L5_ENC["AES-256-GCM<br/>API key encryption"]
        L5_AUDIT["Audit Logging<br/>All queries logged"]
    end

    L1_APIK & L1_JWT & L1_ING --> L2_PERM & L2_ORG & L2_WS
    L2_PERM & L2_ORG & L2_WS --> L3_RO & L3_TBL & L3_NET
    L3_RO & L3_TBL & L3_NET --> L4_TURN & L4_READONLY & L4_GATE & L4_TIMEOUT
    L4_TURN & L4_READONLY & L4_GATE & L4_TIMEOUT --> L5_ENV & L5_ENC & L5_AUDIT
```

## Threat Model

```mermaid
graph TD
    subgraph "Threats Mitigated"
        T1["Credential Leak"]
        T2["Unauthorized Data Access"]
        T3["Cross-Tenant Data Leakage"]
        T4["Runaway API Cost"]
        T5["Unauthorized Mutation"]
        T6["Investigation Bias"]
        T7["Skill Loss"]
        T8["Supply Chain (Python deps)"]
    end

    subgraph "Mitigations"
        M1[".env only, not config.yaml<br/>API keys SHA-256 hashed at rest"]
        M2["Permissions Guard + org scoping"]
        M3["Mandatory workspace_id"]
        M4["90-turn cap + org rate limiting"]
        M5["Human approval gates (600s timeout)"]
        M6["Separate Reviewer context + read-only"]
        M7["Curator snapshots + pin protection"]
        M8["Python stdlib only (0 pip deps)"]
    end

    T1 -.-> M1
    T2 -.-> M2
    T3 -.-> M3
    T4 -.-> M4
    T5 -.-> M5
    T6 -.-> M6
    T7 -.-> M7
    T8 -.-> M8
```

## Agent Permission Matrix

```mermaid
graph TD
    subgraph "Triage Agent"
        TA_R["✓ Read metrics, logs, alert rules"]
        TA_D["✓ Delegate to Investigator"]
        TA_W["✗ No write operations"]
    end

    subgraph "Investigator Agent"
        IA_R["✓ Read all telemetry signals"]
        IA_D["✓ Delegate to Reviewer"]
        IA_W["✗ No write operations"]
    end

    subgraph "Reviewer Agent"
        RA_R["✓ Read-only verification"]
        RA_W["✗ No write operations"]
        RA_D["✗ No delegation"]
    end

    subgraph "Remediator Agent"
        RM_R["✓ Read metrics, logs"]
        RM_W["⚠ Write with approval gate"]
        RM_ES["✓ Escalate (no approval)"]
    end

    style TA_W fill:#6b1a2a,stroke:#ef4444,color:#fff
    style IA_W fill:#6b1a2a,stroke:#ef4444,color:#fff
    style RA_W fill:#6b1a2a,stroke:#ef4444,color:#fff
    style RM_W fill:#6b4a1a,stroke:#f0883e,color:#fff
```

| Capability        | Triage | Investigator | Reviewer | Remediator   |
| ----------------- | ------ | ------------ | -------- | ------------ |
| Read metrics      | ✓      | ✓            | ✓        | ✓            |
| Read logs         | ✓      | ✓            | ✓        | ✓            |
| Read traces       | ✗      | ✓            | ✓        | ✗            |
| Read exemplars    | ✗      | ✓            | ✓        | ✗            |
| Read correlations | ✗      | ✓            | ✓        | ✗            |
| Scale deployment  | ✗      | ✗            | ✗        | ⚠ (approval) |
| Restart pod       | ✗      | ✗            | ✗        | ⚠ (approval) |
| Rollback deploy   | ✗      | ✗            | ✗        | ⚠ (approval) |
| Update alert      | ✗      | ✗            | ✗        | ⚠ (approval) |
| Delegate          | ✓      | ✓            | ✗        | ✗            |
| Escalate to human | ✓      | ✓            | ✓        | ✓            |

## Encryption

```mermaid
graph LR
    subgraph "At Rest"
        APIK["API Keys<br/>AES-256-GCM<br/>(EncryptionService)"]
        JWT_S["JWT Secret<br/>JWT_SECRET env var"]
        LLM_K["LLM Keys<br/>LLM_ENCRYPTION_KEY<br/>(min 32 chars)"]
    end

    subgraph "In Transit"
        TLS["TLS 1.3<br/>(TFO API)"]
        WS["Workspace isolation<br/>(query-level)"]
    end
```

## Secrets Management

| Secret                  | Location         | Format                    |
| ----------------------- | ---------------- | ------------------------- |
| `TELEMETRYFLOW_API_KEY` | `~/.hermes/.env` | `tfs_<64 chars>`          |
| `ANTHROPIC_API_KEY`     | `~/.hermes/.env` | `sk-ant-...`              |
| `ZHIPU_API_KEY`         | `~/.hermes/.env` | Provider-specific         |
| `LLM_ENCRYPTION_KEY`    | `~/.hermes/.env` | Base64, 32+ chars         |
| `CLICKHOUSE_PASSWORD`   | `~/.hermes/.env` | Plain text                |
| `TELEGRAM_BOT_TOKEN_*`  | `~/.hermes/.env` | Bot token from @BotFather |

**Rules:**

- Secrets go in `~/.hermes/.env`, **never** in `config.yaml`
- `config.yaml` is for agent behavior settings only
- `.env` file should be `chmod 600`

## Sub-Pages

- [ClickHouse Read-Only Access](./clickhouse-readonly.md) — Database user and table grants
