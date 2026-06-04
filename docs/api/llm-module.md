# LLM Module Integration

Complete reference for the TelemetryFlow Platform LLM module API — the AI Assistant backend that powers context-aware chat, insights, and provider management.

## Architecture

```mermaid
graph TB
    subgraph "Hermes Plugin Tools"
        CHAT["chat_with_context"]
        STREAM["stream_chat"]
        CONV["manage_conversation"]
        INSIGHT["generate_insight"]
        USAGE["query_llm_usage"]
        PROV["manage_provider"]
    end

    subgraph "TelemetryFlow LLM Module"
        direction TB
        GUARD["Guards<br/>JwtAuth · Permissions · LLMRateLimiter"]

        CC["ChatController<br/>/api/v2/llm/chat/*"]
        IC["InsightsController<br/>/api/v2/llm/insights/*"]
        PC["LLMProvidersController<br/>/api/v2/llm/providers/*"]

        CCTX["ContextCollector<br/>4440 lines · 74 ContextTypes"]
        PB["PromptBuilder<br/>865 lines · 65+ System Prompts"]
        IG["InsightGenerator<br/>415 lines · 5 Insight Types"]
        ES["EncryptionService<br/>AES-256-GCM"]
        AF["LLMAdapterFactory<br/>7 Adapter Classes"]
    end

    subgraph "LLM Providers"
        A1["ClaudeAdapter<br/>anthropic · claude"]
        A2["OpenAIAdapter<br/>openai · mistral · grok<br/>kimi · zhipu · mimo · openrouter"]
        A3["GeminiAdapter<br/>google · gemini"]
        A4["DeepSeekAdapter"]
        A5["QwenAdapter"]
        A6["OllamaAdapter"]
        A7["CustomAdapter"]
    end

    CHAT --> CC
    STREAM --> CC
    CONV --> CC
    INSIGHT --> IC
    PROV --> PC
    USAGE --> CC

    GUARD --> CC & IC & PC
    CC --> CCTX --> PB --> AF
    IC --> IG --> AF
    PC --> ES
    AF --> A1 & A2 & A3 & A4 & A5 & A6 & A7
```

## Data Flow — Chat with Context

```mermaid
sequenceDiagram
    participant Tool as Hermes Tool
    participant Ctrl as ChatController
    participant CC as ContextCollector
    participant PB as PromptBuilder
    participant AF as LLMAdapterFactory
    participant LLM as LLM Provider

    Tool->>Ctrl: POST /llm/chat/message<br/>{message, contextType, contextId}
    Ctrl->>Ctrl: Validate SendMessageDto
    Ctrl->>CC: collectContext(contextType, contextId, timeFrom, timeTo)
    CC->>CC: Query ClickHouse for relevant telemetry
    CC-->>Ctrl: contextData (metrics, logs, traces, etc.)
    Ctrl->>PB: buildSystemPrompt(contextType, contextData)
    PB->>PB: Select from 65+ specialized prompts
    PB-->>Ctrl: systemPrompt + contextMessages
    Ctrl->>AF: createAdapter(providerType)
    AF->>LLM: chat(systemPrompt + userMessage)
    LLM-->>Ctrl: response
    Ctrl-->>Tool: {content, conversationId, usage}
```

## Endpoints

### Chat — `/api/v2/llm/chat`

| Method   | Endpoint                          | Permission   | Description                         |
| -------- | --------------------------------- | ------------ | ----------------------------------- |
| `POST`   | `/chat/message`                   | `llm:chat`   | Send message with context injection |
| `POST`   | `/chat/stream`                    | `llm:chat`   | Streaming chat (SSE)                |
| `GET`    | `/chat/conversations`             | `llm:read`   | List conversations                  |
| `GET`    | `/chat/conversations/:id`         | `llm:read`   | Get conversation                    |
| `POST`   | `/chat/conversations/:id/archive` | `llm:write`  | Archive conversation                |
| `DELETE` | `/chat/conversations/:id`         | `llm:delete` | Delete conversation                 |

#### SendMessage DTO (`POST /chat/message`)

```json
{
  "message": "Analyze the memory spike pattern",
  "contextType": "metrics",
  "contextId": "payments-api",
  "conversationId": "uuid-optional",
  "providerId": "uuid-optional",
  "timeFrom": "2026-06-04T00:00:00Z",
  "timeTo": "2026-06-04T03:47:00Z",
  "metadata": {},
  "attachments": [
    {
      "mediaType": "image/png",
      "data": "base64...",
      "name": "screenshot.png"
    }
  ]
}
```

| Field            | Type     | Required | Validation        | Default          |
| ---------------- | -------- | -------- | ----------------- | ---------------- |
| `message`        | string   | **Yes**  | max 32,000 chars  | —                |
| `contextType`    | enum     | **Yes**  | One of 56+ values | —                |
| `contextId`      | string   | No       | —                 | —                |
| `conversationId` | UUID     | No       | `@IsUUID()`       | New conversation |
| `providerId`     | UUID     | No       | `@IsUUID()`       | Org default      |
| `timeFrom`       | ISO 8601 | No       | `@IsDateString()` | 1 hour ago       |
| `timeTo`         | ISO 8601 | No       | `@IsDateString()` | Now              |
| `metadata`       | object   | No       | `@IsObject()`     | —                |
| `attachments`    | array    | No       | `AttachmentDto[]` | —                |

#### ListConversations Query DTO

| Field         | Type    | Default | Validation                |
| ------------- | ------- | ------- | ------------------------- |
| `page`        | number  | `1`     | `@Min(1)`                 |
| `pageSize`    | number  | `20`    | `@Min(1)`, `@Max(100000)` |
| `contextType` | enum    | —       | Filter by context         |
| `isArchived`  | boolean | —       | Filter archived           |
| `search`      | string  | —       | max 255 chars             |

---

### Insights — `/api/v2/llm/insights`

Rate limited to **50 requests** (lower than default 100, insights are more expensive).

| Method | Endpoint               | Permission     | Insight Type            |
| ------ | ---------------------- | -------------- | ----------------------- |
| `POST` | `/insights/generate`   | `llm:insights` | Any (specified in body) |
| `POST` | `/insights/chronology` | `llm:insights` | `chronology`            |
| `POST` | `/insights/root-cause` | `llm:insights` | `root-cause`            |
| `POST` | `/insights/predict`    | `llm:insights` | `prediction`            |
| `POST` | `/insights/recommend`  | `llm:insights` | `recommendation`        |
| `POST` | `/insights/patterns`   | `llm:insights` | `pattern`               |

#### GenerateInsight DTO (`POST /insights/generate`)

```json
{
  "insightType": "root-cause",
  "contextType": "metrics",
  "contextId": "payments-api",
  "providerId": "uuid-optional",
  "timeFrom": "2026-06-03T00:00:00Z",
  "timeTo": "2026-06-04T00:00:00Z",
  "additionalContext": {
    "alert_id": "alert_abc123",
    "severity": "high"
  }
}
```

| Field               | Type     | Required | Default      |
| ------------------- | -------- | -------- | ------------ |
| `insightType`       | enum     | **Yes**  | —            |
| `contextType`       | enum     | **Yes**  | —            |
| `contextId`         | string   | No       | —            |
| `providerId`        | UUID     | No       | Org default  |
| `timeFrom`          | ISO 8601 | No       | 24 hours ago |
| `timeTo`            | ISO 8601 | No       | Now          |
| `additionalContext` | object   | No       | —            |

#### Insight Types

```mermaid
graph TD
    INSIGHT["InsightGenerator"]
    CHR["chronology<br/>Timeline of events"]
    RC["root-cause<br/>Causal chain analysis"]
    PRED["prediction<br/>Forecast based on trends"]
    REC["recommendation<br/>Actionable suggestions"]
    PAT["pattern<br/>Recurring patterns"]

    INSIGHT --> CHR & RC & PRED & REC & PAT

    style CHR fill:#1a3a6b,stroke:#3b82f6,color:#fff
    style RC fill:#6b1a2a,stroke:#ef4444,color:#fff
    style PRED fill:#6b4a1a,stroke:#f0883e,color:#fff
    style REC fill:#1a6b4a,stroke:#00d4aa,color:#fff
    style PAT fill:#4a1a6b,stroke:#a855f7,color:#fff
```

---

### Providers — `/api/v2/llm/providers`

| Method   | Endpoint                     | Permission   | Description          |
| -------- | ---------------------------- | ------------ | -------------------- |
| `POST`   | `/providers`                 | `llm:write`  | Create provider      |
| `GET`    | `/providers`                 | `llm:read`   | List providers       |
| `GET`    | `/providers/default`         | `llm:read`   | Get default provider |
| `POST`   | `/providers/test-key`        | `llm:write`  | Test API key         |
| `GET`    | `/providers/:id`             | `llm:read`   | Get provider         |
| `PATCH`  | `/providers/:id`             | `llm:write`  | Update provider      |
| `POST`   | `/providers/:id/set-default` | `llm:write`  | Set as default       |
| `POST`   | `/providers/:id/validate`    | `llm:write`  | Validate provider    |
| `DELETE` | `/providers/:id`             | `llm:delete` | Delete provider      |

#### CreateLLMProvider DTO (`POST /providers`)

```json
{
  "name": "Production Claude",
  "providerType": "anthropic",
  "apiKey": "sk-ant-...",
  "modelId": "claude-sonnet-4-20250514",
  "temperature": 0.7,
  "maxTokens": 4096,
  "topP": 1.0,
  "samplingMode": "auto",
  "isDefault": true
}
```

| Field          | Type    | Required | Default  | Validation                      |
| -------------- | ------- | -------- | -------- | ------------------------------- |
| `name`         | string  | **Yes**  | —        | max 255                         |
| `providerType` | enum    | **Yes**  | —        | 15 values                       |
| `apiKey`       | string  | **Yes**  | —        | Encrypted at rest (AES-256-GCM) |
| `modelId`      | string  | **Yes**  | —        | max 100                         |
| `baseUrl`      | URL     | No\*     | —        | Required for `custom`, `ollama` |
| `temperature`  | number  | No       | `0.7`    | 0–2                             |
| `maxTokens`    | number  | No       | `4096`   | 1–128,000                       |
| `topP`         | number  | No       | `1.0`    | 0–1                             |
| `samplingMode` | enum    | No       | `"auto"` | `temperature`, `top_p`, `auto`  |
| `isDefault`    | boolean | No       | `false`  | —                               |

#### Provider Types and Adapter Routing

```mermaid
graph TD
    AF["LLMAdapterFactory"]
    CL["ClaudeAdapter<br/>anthropic, claude"]
    OA["OpenAIAdapter<br/>openai, mistral, grok<br/>kimi, zhipu, mimo, openrouter"]
    GA["GeminiAdapter<br/>google, gemini"]
    DS["DeepSeekAdapter<br/>deepseek"]
    QA["QwenAdapter<br/>qwen"]
    OL["OllamaAdapter<br/>ollama"]
    CU["CustomAdapter<br/>custom"]

    AF -->|"anthropic, claude"| CL
    AF -->|"openai, mistral, grok, kimi, zhipu, mimo, openrouter"| OA
    AF -->|"google, gemini"| GA
    AF -->|"deepseek"| DS
    AF -->|"qwen"| QA
    AF -->|"ollama"| OL
    AF -->|"custom"| CU
```

| Provider Type         | Adapter         | Default Base URL                            |
| --------------------- | --------------- | ------------------------------------------- |
| `anthropic`, `claude` | ClaudeAdapter   | `https://api.anthropic.com`                 |
| `openai`              | OpenAIAdapter   | `https://api.openai.com`                    |
| `mistral`             | OpenAIAdapter   | `https://api.mistral.ai`                    |
| `grok`                | OpenAIAdapter   | `https://api.x.ai`                          |
| `kimi`                | OpenAIAdapter   | `https://api.moonshot.cn`                   |
| `zhipu`               | OpenAIAdapter   | `https://open.bigmodel.cn/api/paas`         |
| `mimo`                | OpenAIAdapter   | `https://api.mimo.ai`                       |
| `openrouter`          | OpenAIAdapter   | `https://openrouter.ai/api`                 |
| `google`, `gemini`    | GeminiAdapter   | `https://generativelanguage.googleapis.com` |
| `deepseek`            | DeepSeekAdapter | `https://api.deepseek.com`                  |
| `qwen`                | QwenAdapter     | `https://dashscope.aliyuncs.com`            |
| `ollama`              | OllamaAdapter   | `http://localhost:11434`                    |
| `custom`              | CustomAdapter   | User-provided                               |

## Encryption

API keys are encrypted at rest using `EncryptionService` with AES-256-GCM:

```mermaid
graph LR
    PLAIN["Plain API Key"] --> ES["EncryptionService<br/>AES-256-GCM"]
    KEY["LLM_ENCRYPTION_KEY<br/>(32+ chars)"] --> ES
    ES --> ENC["Encrypted → PostgreSQL"]
    ENC -->|"on read"| ES
    ES -->|"decrypt"| PLAIN
```

The `LLM_ENCRYPTION_KEY` env var is **required** — the app crashes on startup if missing or < 32 chars.

## Rate Limiting

```mermaid
graph TD
    REQ["Incoming Request"] --> GUARD["LLMRateLimiterGuard"]
    GUARD --> KEY["Rate limit key:<br/>llm:{organizationId}"]
    KEY --> CHECK{"Requests < limit?"}
    CHECK -->|"yes"| PASS["Allow"]
    CHECK -->|"no"| REJECT["429 Too Many Requests"]

    CHAT["Chat endpoints<br/>100 req/min"] --> GUARD
    INS["Insight endpoints<br/>50 req/min"] --> GUARD
```

| Endpoint               | Limit         | Key           |
| ---------------------- | ------------- | ------------- |
| Chat (message, stream) | 100 req/min   | `llm:{orgId}` |
| Insights (all)         | 50 req/min    | `llm:{orgId}` |
| Providers              | No rate limit | —             |

## Usage Analytics (ClickHouse)

LLM usage is tracked in `llm_usage_analytics` with materialized rollups:

```mermaid
graph TD
    RAW["llm_usage_analytics<br/>Raw events"]
    MV5["llm_usage_5m<br/>5-minute rollup"]
    MV15["llm_usage_15m<br/>15-minute rollup"]
    MV6H["llm_usage_6h<br/>6-hour rollup"]

    RAW --> MV5
    RAW --> MV15
    RAW --> MV6H
```

Query via `query_llm_usage` tool with actions: `summary`, `by-provider`, `by-model`, `by-context`, `top-users`, `interval`.
