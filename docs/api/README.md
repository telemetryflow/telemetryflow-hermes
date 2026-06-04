# API Overview

TelemetryFlow Hermes integrates with the TFO Platform through its REST API and ClickHouse. All communication is authenticated and workspace-scoped.

## Integration Architecture

```mermaid
graph TB
    subgraph "Hermes Plugin Tools"
        TOOLS["37 Python Tools"]
        SHARED["_shared.py<br/>tfo_request() · clickhouse_query()"]
    end

    subgraph "TFO Platform API"
        direction TB
        AUTH["Auth Guards<br/>JWT · API Key · Ingestion"]
        PERM["Permissions Guard<br/>llm:chat · llm:read · llm:write"]
        CTRL["Controllers<br/>Chat · Insights · Providers · Telemetry"]
        SVC["Services<br/>ContextCollector · PromptBuilder · InsightGenerator"]
        CH["ClickHouse Client"]
    end

    subgraph "Data Stores"
        PG["PostgreSQL<br/>Conversations · Providers"]
        CLICK["ClickHouse<br/>Metrics · Logs · Traces · Exemplars"]
        REDIS["Redis<br/>Rate Limiting · Token Revocation"]
    end

    TOOLS --> SHARED
    SHARED -->|"HTTP Bearer/API Key"| AUTH
    AUTH --> PERM
    PERM --> CTRL
    CTRL --> SVC
    SVC --> CH
    CH --> PG
    CH --> CLICK
    CH --> REDIS
```

## API Modules

### Authentication

See [Authentication](./authentication.md) for detailed flows.

| Method     | Header                          | Use Case           |
| ---------- | ------------------------------- | ------------------ |
| JWT Bearer | `Authorization: Bearer <jwt>`   | User-scoped access |
| API Key    | `x-api-key: tfs_...`            | Agent M2M access   |
| Ingestion  | `X-TelemetryFlow-Key-ID/Secret` | OTEL Collector     |

### LLM Module

See [LLM Module](./llm-module.md) for endpoint details.

| Endpoint Group | Base Path                          | Description                              |
| -------------- | ---------------------------------- | ---------------------------------------- |
| Chat           | `/api/v2/llm/chat/*`               | Context-aware chat with ContextCollector |
| Insights       | `/api/v2/llm/insights/*`           | AI insight generation (5 types)          |
| Providers      | `/api/v2/llm/providers/*`          | LLM provider CRUD (15 types)             |
| Conversations  | `/api/v2/llm/chat/conversations/*` | Conversation management                  |

### Telemetry Queries

All telemetry queries go through `POST /api/v2/telemetry/query`:

```json
{
  "sql": "SELECT * FROM metrics_1m WHERE workspace_id = ? LIMIT 50",
  "format": "JSON"
}
```

### Context Types

See [Context Types](./context-types.md) for the complete list of 74 ContextType values used by the LLM module.

## Authentication Flow

```mermaid
sequenceDiagram
    participant H as Hermes Tool
    participant A as TFO Auth
    participant P as TFO API

    alt Method A: API Key
        H->>A: x-api-key: tfs_xxxxx
        A->>A: SHA-256 hash lookup
        A->>P: req.apiKey = {orgId, workspaceId, permissions}
    else Method B: JWT Login
        H->>A: POST /auth/login {email, password}
        A->>H: {accessToken, refreshToken}
        H->>P: Authorization: Bearer <accessToken>
        P->>P: req.user = {userId, orgId, roles, permissions}
    else Method C: Ingestion Headers
        H->>A: X-TelemetryFlow-Key-ID + Secret
        A->>A: Validate key pair + encryption key
        A->>P: req.apiKey + req.user
    end
```

## Rate Limiting

| Scope           | Limit       | Key                    |
| --------------- | ----------- | ---------------------- |
| LLM Chat        | 100 req/min | `llm:<organizationId>` |
| API General     | Varies      | Per API key            |
| Telemetry Query | Varies      | Per workspace          |

## Required Permissions

| Endpoint                  | Required Permission |
| ------------------------- | ------------------- |
| `/llm/chat/message`       | `llm:chat`          |
| `/llm/chat/conversations` | `llm:read`          |
| `/llm/insights/generate`  | `llm:insights`      |
| `/llm/providers` (read)   | `llm:read`          |
| `/llm/providers` (write)  | `llm:write`         |
| `/telemetry/query`        | `telemetry:read`    |
