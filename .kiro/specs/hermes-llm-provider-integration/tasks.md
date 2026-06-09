# Implementation Plan: Hermes LLM Provider Integration

## Overview

This plan covers the integration of multi-provider LLM support into Hermes across eight areas: core provider infrastructure, per-agent model configuration, API key management with encryption, health checking and fallback, air-gapped deployment with Ollama, cost tracking and analytics, integration testing, and documentation.

## Tasks

- [ ] 1. Validate PROVIDER_TYPES Completeness
  - Source: `plugins/telemetryflow/tools/_shared.py`
  - Verify `PROVIDER_TYPES` list contains all 15 types: anthropic, claude, openai, google, gemini, deepseek, qwen, ollama, mistral, grok, kimi, zhipu, mimo, openrouter, custom
  - Test: `test_manage_provider.py::TestManageProvider::test_create_invalid_type`
  - _Requirements: REQ-001_

- [ ] 2. Validate PROVIDER_MAP in Docker Entrypoint
  - Source: `docker-entrypoint.py`
  - Verify `PROVIDER_MAP` maps all provider key prefixes to canonical identifiers
  - Ensure aliases (gemini→google, claude→anthropic) are correct
  - Verify zhipu maps to opencode-go
  - _Requirements: REQ-001, REQ-008_

- [ ] 3. Verify ENV_FORWARD_PREFIXES Coverage
  - Source: `docker-entrypoint.py`
  - Confirm all 20 prefixes are present in `ENV_FORWARD_PREFIXES`
  - Verify Ollama-related vars are not needed (local inference)
  - Verify `LLM_` prefix covers `LLM_ENCRYPTION_KEY`
  - Test: Manual — `docker-entrypoint.py --check` should list all forwarded vars
  - _Requirements: REQ-003, REQ-010_

- [*] 4. Test manage_provider.py All Actions
  - Source: `plugins/telemetryflow/tools/manage_provider.py`, `tests/unit/test_manage_provider.py`
  - Verify all 7 actions (list, get, default, create, validate, test-key, set-default) call correct TFO API endpoints with correct HTTP methods
  - Test cases: `test_list` → `GET /llm/providers`, `test_get` → `GET /llm/providers/{id}`, `test_default` → `GET /llm/providers/default`, `test_create` → `POST /llm/providers` with full payload, `test_create_with_base_url` → includes `baseUrl` field, `test_validate` → `POST /llm/providers/{id}/validate`, `test_test_key` → `POST /llm/providers/test-key`, `test_set_default` → `POST /llm/providers/{id}/set-default`, `test_create_missing_fields` → exit code 1, `test_create_invalid_type` → exit code 1, `test_unknown_action` → exit code 1, `test_no_api_key_exits` → exit code 1, `test_api_error_exits` → exit code 1
  - _Requirements: REQ-009_

- [*] 5. Test parse_model_env() All Cases
  - Source: `docker-entrypoint.py`
  - Verify `parse_model_env()` handles all input formats
  - Test cases: `zhipu/glm-5.1` → `("glm-5.1", "opencode-go")`, `anthropic/claude-sonnet-4-5` → `("claude-sonnet-4-5", "anthropic")`, `ollama/llama3.3:70b` → `("llama3.3:70b", "ollama")`, `glm-5.1` → `("glm-5.1", "opencode-go")` (default), `unknown/model` → `("model", "unknown")` (pass-through)
  - _Requirements: REQ-002, REQ-008_

- [*] 6. Test write_profile_config() Substitution
  - Source: `docker-entrypoint.py`
  - Verify `write_profile_config()` correctly substitutes `default:` and `provider:` fields while preserving all other YAML content
  - Test with and without template files
  - _Requirements: REQ-002, REQ-008_

- [*] 7. Test Profile Model Assignment Flow
  - Source: `docker-entrypoint.py:configure()`
  - Verify the full configuration flow
  - Default model from `HERMES_MODEL` (default: `zhipu/glm-5.1`), Investigator model from `HERMES_INVESTIGATOR_MODEL` (default: `anthropic/claude-sonnet-4-5`)
  - Triage/Reviewer/Remediator use default model, Investigator uses its own model, all 4 profile config.yaml files are generated
  - _Requirements: REQ-002_

- [ ] 8. Verify Docker Compose Environment Variables
  - Source: `docker-compose.yaml`
  - Confirm `HERMES_MODEL` and `HERMES_INVESTIGATOR_MODEL` are passed to the Hermes container with correct defaults
  - _Requirements: REQ-011_

- [ ] 9. Verify API Key Forwarding
  - Source: `docker-entrypoint.py:write_hermes_env()`
  - Confirm all 11 API key environment variables are forwarded to `~/.hermes/.env`: ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY, DEEPSEEK_API_KEY, QWEN_API_KEY, MISTRAL_API_KEY, GROK_API_KEY, KIMI_API_KEY, ZHIPU_API_KEY, MIMO_API_KEY, OPENROUTER_API_KEY
  - _Requirements: REQ-003, REQ-010_

- [ ] 10. Test test-key Action
  - Source: `plugins/telemetryflow/tools/manage_provider.py`
  - Test cases: `test_test_key` — validates key, sends POST with providerType and apiKey, `test_test_key_with_base_url` — includes baseUrl for custom providers, `test_test_key_missing_api_key` — exit code 1
  - _Requirements: REQ-003, REQ-004_

- [ ] 11. Verify LLM_ENCRYPTION_KEY in Docker Compose
  - Source: `docker-compose.yaml`
  - Confirm `LLM_ENCRYPTION_KEY=${LLM_ENCRYPTION_KEY}` is set on the backend container
  - Verify `.env.example` documents the key and minimum length requirement
  - _Requirements: REQ-003_

- [ ] 12. Test .env.example Completeness
  - Source: `.env.example`
  - Verify `.env.example` contains all 11 provider API key placeholders, `LLM_ENCRYPTION_KEY`, model assignment documentation, and generation command for secrets
  - _Requirements: REQ-003, REQ-011_

- [ ] 13. Test Provider Validation
  - Source: `plugins/telemetryflow/tools/manage_provider.py`
  - Test cases: `test_validate` — calls `POST /llm/providers/{id}/validate`, `test_validate_missing_provider_id` — exit code 1
  - _Requirements: REQ-004_

- [ ] 14. Test Default Provider Selection
  - Source: `plugins/telemetryflow/tools/manage_provider.py`
  - Test cases: `test_default` — calls `GET /llm/providers/default`, `test_set_default` — calls `POST /llm/providers/{id}/set-default`, `test_set_default_missing_provider_id` — exit code 1, `test_create` with `--is-default true` flag
  - _Requirements: REQ-005_

- [ ] 15. Test docker-entrypoint.py --check
  - Source: `docker-entrypoint.py:check()`
  - Verify `--check` flag validates auth method, API URL, and environment configuration
  - Returns exit code 0 on success, 1 on validation failure
  - _Requirements: REQ-008_

- [ ] 16. Verify deploy-air-gapped.sh Script
  - Source: `scripts/deploy-air-gapped.sh`
  - Verify the script checks Ollama installation, sets global model to `llama3.3:70b` with provider `ollama`, attempts `ollama pull llama3.3:70b` with graceful fallback, configures all 4 profiles (triage, investigator, reviewer, remediator), prints deployment chain and completion message
  - _Requirements: REQ-006_

- [ ] 17. Verify Air-Gapped Documentation
  - Source: `docs/deployment/air-gapped.md`
  - Confirm documentation covers architecture diagram (Mermaid), data flow diagram (zero egress), step-by-step deployment (6 steps), model selection guide with RAM requirements, model transfer procedure for air-gapped hosts, profile configuration table, limitations comparison (standard vs air-gapped), Telegram alternatives for offline environments
  - _Requirements: REQ-006_

- [ ] 18. Test Ollama Provider Mapping
  - Source: `docker-entrypoint.py`
  - Verify `PROVIDER_MAP["ollama"]` == `"ollama"`
  - Verify `parse_model_env("ollama/llama3.3:70b")` returns `("llama3.3:70b", "ollama")`
  - _Requirements: REQ-006_

- [ ] 19. Verify query_llm_usage.py Actions
  - Source: `plugins/telemetryflow/tools/query_llm_usage.py`
  - Verify all 6 actions produce correct ClickHouse SQL
  - `summary` — aggregate stats with count, sum, avg, quantile, uniqExact
  - `by-provider` — GROUP BY provider_type
  - `by-model` — GROUP BY model_id, provider_type
  - `by-context` — GROUP BY context_type
  - `top-users` — GROUP BY user_id
  - `interval` — queries materialized views (llm_usage_5m, llm_usage_15m, llm_usage_6h)
  - _Requirements: REQ-007_

- [ ] 20. Test Duration Mapping
  - Source: `plugins/telemetryflow/tools/query_llm_usage.py`
  - Verify `DURATION_MAP` maps all supported windows: 1h, 6h, 24h, 7d, 30d
  - Unknown durations default to `INTERVAL 24 HOUR`
  - _Requirements: REQ-007_

- [ ] 21. Test Interval View Selection
  - Source: `plugins/telemetryflow/tools/query_llm_usage.py`
  - Verify `interval` action maps view parameter (5m, 15m, 6h) to correct ClickHouse materialized view tables
  - _Requirements: REQ-007_

- [*] 22. End-to-End Docker Configuration
  - Run `docker-entrypoint.py` with test environment variables
  - Verify all profile config.yaml files generated with correct model/provider
  - Verify `~/.hermes/.env` contains all forwarded variables
  - Verify `~/.hermes/config.yaml` has global default model/provider
  - Verify all profiles, skills, tools, hooks, cron are copied
  - _Requirements: REQ-002, REQ-008, REQ-010, REQ-011_

- [*] 23. End-to-End Provider Management
  - Using `manage_provider.py`, verify complete lifecycle
  - `--action create` — create a provider with encrypted API key
  - `--action list` — verify provider appears
  - `--action validate` — validate the provider
  - `--action set-default` — set as default
  - `--action default` — confirm it's the default
  - `--action test-key` — test a new key without storing
  - _Requirements: REQ-009_

- [*] 24. Air-Gapped End-to-End
  - In a test environment with Ollama running: run `scripts/deploy-air-gapped.sh`
  - Verify all 4 profiles configured for Ollama
  - Verify no API keys required
  - Verify model is available locally
  - _Requirements: REQ-006_

- [ ] 25. Verify .env.example Documentation
  - Confirm `.env.example` contains sections for all provider keys, model assignment documentation, encryption key guidance, and secret generation command
  - _Requirements: REQ-003_

- [ ] 26. Verify manage_provider.py Docstring
  - Confirm the module docstring contains usage examples for all 7 actions
  - _Requirements: REQ-009_

- [ ] 27. Verify docker-entrypoint.py Docstring
  - Confirm the module docstring documents `--check` flag and configuration behavior
  - _Requirements: REQ-008_

- [ ] 28. Checkpoint - LLM Provider Integration Complete
