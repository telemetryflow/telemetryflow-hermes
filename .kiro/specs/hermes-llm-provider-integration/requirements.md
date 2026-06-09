# Requirements — Hermes LLM Provider Integration

## Overview

Hermes supports 15+ LLM providers, each configurable per agent profile. Providers are managed through the TelemetryFlow (TFO) API, with encryption at rest, health checking, fallback selection, cost tracking, and air-gapped deployment support.

---

## REQ-001: Multi-Provider Support

**Priority**: P0
**Status**: Required

Hermes shall support the following provider types, as defined in `_shared.py:PROVIDER_TYPES`:

| #   | Provider Type  | Integration Key | API Key Env Var      | Notes                                        |
| --- | -------------- | --------------- | -------------------- | -------------------------------------------- |
| 1   | Anthropic      | `anthropic`     | `ANTHROPIC_API_KEY`  | Claude Sonnet 4.5 — Investigator default     |
| 2   | Claude (alias) | `claude`        | `ANTHROPIC_API_KEY`  | Alias for anthropic                          |
| 3   | OpenAI         | `openai`        | `OPENAI_API_KEY`     | GPT-4, GPT-4o                                |
| 4   | Google         | `google`        | `GOOGLE_API_KEY`     | Gemini Pro                                   |
| 5   | Gemini (alias) | `gemini`        | `GOOGLE_API_KEY`     | Alias for google                             |
| 6   | DeepSeek       | `deepseek`      | `DEEPSEEK_API_KEY`   | Cost-efficient reasoning                     |
| 7   | Qwen           | `qwen`          | `QWEN_API_KEY`       | Alibaba Cloud                                |
| 8   | Mistral        | `mistral`       | `MISTRAL_API_KEY`    | European data residency                      |
| 9   | Grok           | `grok`          | `GROK_API_KEY`       | xAI                                          |
| 10  | Kimi           | `kimi`          | `KIMI_API_KEY`       | Moonshot                                     |
| 11  | Zhipu          | `zhipu`         | `ZHIPU_API_KEY`      | GLM-5.1 — Triage/Reviewer/Remediator default |
| 12  | MiMo           | `mimo`          | `MIMO_API_KEY`       | Xiaomi                                       |
| 13  | OpenRouter     | `openrouter`    | `OPENROUTER_API_KEY` | Unified endpoint for 200+ models             |
| 14  | Ollama         | `ollama`        | (none — local)       | Air-gapped / local inference                 |
| 15  | Custom         | `custom`        | (user-provided)      | User-defined base URL                        |

**Acceptance Criteria**:

- `PROVIDER_TYPES` in `_shared.py` contains all 15 provider type identifiers.
- `manage_provider.py --action create --type <type>` validates against `PROVIDER_TYPES` and rejects unknown types.
- `PROVIDER_MAP` in `docker-entrypoint.py` maps all provider key prefixes to canonical provider identifiers.
- Each cloud provider has a corresponding environment variable for its API key.
- Ollama requires no API key (local inference).

---

## REQ-002: Per-Agent Model Configuration

**Priority**: P0
**Status**: Required

Each agent profile shall be independently configurable with its own model and provider.

**Default Agent Model Assignments**:

| Agent Profile | Default Model       | Provider              | Env Var Override            |
| ------------- | ------------------- | --------------------- | --------------------------- |
| Triage        | `glm-5.1`           | `zhipu` (OpenCode Go) | `HERMES_MODEL`              |
| Investigator  | `claude-sonnet-4-5` | `anthropic`           | `HERMES_INVESTIGATOR_MODEL` |
| Reviewer      | `glm-5.1`           | `zhipu` (OpenCode Go) | `HERMES_MODEL`              |
| Remediator    | `glm-5.1`           | `zhipu` (OpenCode Go) | `HERMES_MODEL`              |

**Model Selection Format**: `provider/model-name` (e.g., `anthropic/claude-sonnet-4-5`, `zhipu/glm-5.1`). If no provider prefix, defaults to `zhipu`.

**Acceptance Criteria**:

- `docker-entrypoint.py` reads `HERMES_MODEL` (default: `zhipu/glm-5.1`) for Triage/Reviewer/Remediator profiles.
- `docker-entrypoint.py` reads `HERMES_INVESTIGATOR_MODEL` (default: `anthropic/claude-sonnet-4-5`) for the Investigator profile.
- `parse_model_env()` parses `provider/model` format, defaulting to `zhipu` if no prefix.
- `write_profile_config()` substitutes `default:` and `provider:` fields in each profile's `config.yaml`.
- Docker Compose passes `HERMES_MODEL` and `HERMES_INVESTIGATOR_MODEL` as environment variables.
- All 4 profiles (triage, investigator, reviewer, remediator) receive correct model assignments on container startup.

---

## REQ-003: API Key Management and Encryption

**Priority**: P0
**Status**: Required

LLM provider API keys shall be managed securely with encryption at rest.

**Environment Variables for Provider API Keys (11)**:

| Variable             | Provider           |
| -------------------- | ------------------ |
| `ANTHROPIC_API_KEY`  | Anthropic (Claude) |
| `OPENAI_API_KEY`     | OpenAI (GPT)       |
| `GOOGLE_API_KEY`     | Google (Gemini)    |
| `DEEPSEEK_API_KEY`   | DeepSeek           |
| `QWEN_API_KEY`       | Qwen (Alibaba)     |
| `MISTRAL_API_KEY`    | Mistral            |
| `GROK_API_KEY`       | Grok (xAI)         |
| `KIMI_API_KEY`       | Kimi (Moonshot)    |
| `ZHIPU_API_KEY`      | Zhipu (GLM)        |
| `MIMO_API_KEY`       | MiMo (Xiaomi)      |
| `OPENROUTER_API_KEY` | OpenRouter         |

**Encryption**:

- API keys stored in the TFO platform database are encrypted using AES-256-GCM via `EncryptionService`.
- `LLM_ENCRYPTION_KEY` environment variable configures the encryption key (minimum 32 characters).
- The backend NestJS service uses `LLM_ENCRYPTION_KEY` for encrypting/decrypting provider keys.
- Keys stored in `~/.hermes/.env` on the agent host are plaintext (file permission security).

**Acceptance Criteria**:

- `docker-entrypoint.py` forwards all 11 API key environment variables to `~/.hermes/.env` via `ENV_FORWARD_PREFIXES`.
- `ENV_FORWARD_PREFIXES` includes: `ANTHROPIC_`, `OPENAI_`, `GOOGLE_`, `GEMINI_`, `DEEPSEEK_`, `QWEN_`, `MISTRAL_`, `GROQ_`, `GROK_`, `KIMI_`, `ZHIPU_`, `MIMO_`, `OPENROUTER_`.
- `manage_provider.py --action create --api-key <key>` sends the API key to the TFO API for encrypted storage.
- `manage_provider.py --action test-key --type <type> --api-key <key>` validates an API key without storing it.
- `LLM_ENCRYPTION_KEY` is passed to the backend container via Docker Compose.
- API keys are never logged or printed in tool output.

---

## REQ-004: Provider Health Checking

**Priority**: P1
**Status**: Required

The system shall validate provider connectivity and API key validity.

**Health Check Operations**:

1. **Provider Validation** (`validate`): Validates an existing stored provider by ID. Calls `POST /llm/providers/{id}/validate`.
2. **Key Testing** (`test-key`): Tests a raw API key against a provider type without storing it. Calls `POST /llm/providers/test-key`.

**Acceptance Criteria**:

- `manage_provider.py --action validate --provider-id <uuid>` returns validation status.
- `manage_provider.py --action test-key --type anthropic --api-key sk-xxx` returns key validity.
- `test-key` supports optional `--base-url` for custom/self-hosted providers.
- Both operations return structured JSON with `{ "data": { "valid": true|false } }` on success.
- Invalid provider IDs cause an error exit (code 1).
- Missing API key for `test-key` causes an error exit (code 1).

---

## REQ-005: Fallback Provider Selection

**Priority**: P1
**Status**: Required

The system shall support a default provider mechanism with fallback selection.

**Default Provider Flow**:

1. If `TELEMETRYFLOW_DEFAULT_PROVIDER_ID` is set, Hermes uses that provider.
2. Otherwise, the TFO API returns the organization's default provider via `GET /llm/providers/default`.
3. If no default is configured, the first active provider is used.

**Acceptance Criteria**:

- `manage_provider.py --action default` retrieves the current default provider via `GET /llm/providers/default`.
- `manage_provider.py --action set-default --provider-id <uuid>` sets a provider as default via `POST /llm/providers/{id}/set-default`.
- Provider creation supports `--is-default true` flag to set the new provider as default.
- The default provider is marked with `isDefault: true` in the provider list response.

---

## REQ-006: Air-Gapped Deployment (Ollama)

**Priority**: P1
**Status**: Required

Hermes shall operate fully offline using Ollama for local LLM inference.

**Deployment Chain**: `Ollama pod → Local model → Hermes Agent → ClickHouse → TelemetryFlow`

**Acceptance Criteria**:

- `scripts/deploy-air-gapped.sh` configures all 4 profiles to use `ollama/llama3.3:70b`.
- The script verifies Ollama is installed (`command -v ollama`).
- The script attempts `ollama pull llama3.3:70b` with a fallback warning if offline.
- Each profile is configured via `hermes config set model.default` and `model.provider`.
- No API keys are required for Ollama (local inference).
- Prompt, context, and response never leave the cluster.
- `docker-entrypoint.py` maps `ollama` provider correctly in `PROVIDER_MAP`.

**Model Selection Guide (Air-Gapped)**:

| Model        | Parameters | RAM   | Quality |
| ------------ | ---------- | ----- | ------- |
| llama3.3     | 70B        | 40GB+ | Best    |
| mistral-nemo | 12B        | 16GB+ | Good    |
| qwen2.5      | 7B         | 8GB+  | Decent  |
| phi3         | 3.8B       | 4GB+  | Basic   |

---

## REQ-007: Cost Tracking per Provider

**Priority**: P2
**Status**: Required

The system shall track LLM usage and costs per provider through the `llm_usage_analytics` ClickHouse table.

**Tracked Metrics**:

| Metric              | Description                           |
| ------------------- | ------------------------------------- |
| `total_requests`    | Total number of LLM calls             |
| `total_tokens`      | Sum of all tokens consumed            |
| `prompt_tokens`     | Tokens in prompts                     |
| `completion_tokens` | Tokens in completions                 |
| `latency_ms`        | Per-request latency                   |
| `provider_type`     | Provider used                         |
| `model_id`          | Model used                            |
| `context_type`      | Context (metrics, logs, traces, etc.) |
| `user_id`           | Requesting user                       |

**Query Actions** (via `query_llm_usage.py`):

| Action        | Description                                            |
| ------------- | ------------------------------------------------------ |
| `summary`     | Aggregate stats over time window                       |
| `by-provider` | Usage breakdown by provider type                       |
| `by-model`    | Usage breakdown by model                               |
| `by-context`  | Usage breakdown by context type                        |
| `top-users`   | Top users by token consumption                         |
| `interval`    | Time-series data from materialized views (5m, 15m, 6h) |

**Time Windows**: `1h`, `6h`, `24h`, `7d`, `30d`

**Acceptance Criteria**:

- `query_llm_usage.py --action by-provider --duration 7d` returns per-provider token counts, request counts, and average latency.
- `query_llm_usage.py --action by-model --duration 7d` returns per-model breakdown with provider association.
- `query_llm_usage.py --action summary --duration 24h` returns aggregate statistics including unique provider and model counts.
- Materialized interval views (`llm_usage_5m`, `llm_usage_15m`, `llm_usage_6h`) support time-series queries.
- All queries use parameterized intervals via `DURATION_MAP`.

---

## REQ-008: Dynamic Provider Substitution

**Priority**: P1
**Status**: Required

The Docker entrypoint shall dynamically substitute model and provider configuration per agent profile at container startup.

**Substitution Mechanism**:

1. `docker-entrypoint.py` reads `HERMES_MODEL` and `HERMES_INVESTIGATOR_MODEL` environment variables.
2. `parse_model_env()` extracts provider and model from `provider/model` format.
3. `write_profile_config()` rewrites each profile's `config.yaml`, replacing `default:` and `provider:` fields.
4. `write_default_config()` rewrites the global `~/.hermes/config.yaml`.

**Acceptance Criteria**:

- Container startup prints resolved model assignments: `[hermes] Default model: glm-5.1 via opencode-go`.
- Investigator profile uses `HERMES_INVESTIGATOR_MODEL` independently from other profiles.
- Profiles without explicit model overrides use `HERMES_MODEL`.
- If `HERMES_MODEL` is not set, defaults to `zhipu/glm-5.1`.
- If `HERMES_INVESTIGATOR_MODEL` is not set, defaults to `anthropic/claude-sonnet-4-5`.
- The `--check` flag validates environment variables without starting the agent.

---

## REQ-009: Provider Management Tool

**Priority**: P0
**Status**: Required

The `manage_provider.py` tool shall support full CRUD operations for LLM providers through the TFO API.

**Supported Actions**:

| Action        | Method | Endpoint                          | Required Args                    |
| ------------- | ------ | --------------------------------- | -------------------------------- |
| `list`        | GET    | `/llm/providers`                  | —                                |
| `get`         | GET    | `/llm/providers/{id}`             | `--provider-id`                  |
| `default`     | GET    | `/llm/providers/default`          | —                                |
| `create`      | POST   | `/llm/providers`                  | `--name`, `--api-key`, `--model` |
| `validate`    | POST   | `/llm/providers/{id}/validate`    | `--provider-id`                  |
| `test-key`    | POST   | `/llm/providers/test-key`         | `--api-key`                      |
| `set-default` | POST   | `/llm/providers/{id}/set-default` | `--provider-id`                  |

**Create Parameters**:

| Parameter   | Flag            | Default     | Required |
| ----------- | --------------- | ----------- | -------- |
| Name        | `--name`        | —           | Yes      |
| Type        | `--type`        | `anthropic` | No       |
| API Key     | `--api-key`     | —           | Yes      |
| Model       | `--model`       | —           | Yes      |
| Base URL    | `--base-url`    | —           | No       |
| Temperature | `--temperature` | `0.7`       | No       |
| Max Tokens  | `--max-tokens`  | `4096`      | No       |
| Top P       | `--top-p`       | `1.0`       | No       |
| Is Default  | `--is-default`  | `false`     | No       |

**Acceptance Criteria**:

- All 7 actions are supported with correct HTTP methods and endpoints.
- `create` validates provider type against `PROVIDER_TYPES` whitelist.
- `create` requires `--name`, `--api-key`, and `--model` (exits with code 1 if missing).
- `get`, `validate`, and `set-default` require `--provider-id` (exits with code 1 if missing).
- `test-key` requires `--api-key` (exits with code 1 if missing).
- Unknown actions print valid action list and exit with code 1.
- All API errors are printed to stderr with HTTP status code.
- Missing `TELEMETRYFLOW_API_KEY` causes immediate exit.
- All output is structured JSON via `output_json()`.

---

## REQ-010: Environment Variable Forwarding

**Priority**: P0
**Status**: Required

The Docker entrypoint shall forward all provider-relevant environment variables to the Hermes runtime environment.

**Forwarded Prefixes**:

`TELEMETRYFLOW_`, `ANTHROPIC_`, `OPENAI_`, `GOOGLE_`, `GEMINI_`, `DEEPSEEK_`, `QWEN_`, `ZHIPU_`, `MISTRAL_`, `GROQ_`, `GROK_`, `KIMI_`, `MIMO_`, `OPENROUTER_`, `JIRA_`, `TRELLO_`, `TELEGRAM_`, `CLICKHOUSE_`, `LLM_`, `KUBECONFIG`

**Acceptance Criteria**:

- `write_hermes_env()` iterates all environment variables and writes matching ones to `~/.hermes/.env`.
- The function returns a count of forwarded variables.
- The entrypoint logs: `[hermes] .env: N variables`.
- Docker Compose passes all provider API keys as environment variables to the container.

---

## REQ-011: Docker Compose Integration

**Priority**: P0
**Status**: Required

The Docker Compose configuration shall support multi-provider deployment with all required environment variables.

**Acceptance Criteria**:

- `docker-compose.yaml` passes `HERMES_MODEL` (default: `zhipu/glm-5.1`) and `HERMES_INVESTIGATOR_MODEL` (default: `anthropic/claude-sonnet-4-5`).
- All 11 provider API key environment variables are passed with defaults to empty strings.
- `LLM_ENCRYPTION_KEY` is passed to the backend service.
- `TELEMETRYFLOW_DEFAULT_PROVIDER_ID` is supported via `.env` file.
- The Hermes container uses `docker-entrypoint.py` as its entrypoint.
- The backend container health check confirms API availability before the frontend starts.
