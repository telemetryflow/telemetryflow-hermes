# Hermes TelemetryFlow Plugin Tools — Requirements

## Overview

The Hermes TelemetryFlow plugin provides 40 CLI tools that enable the Hermes Agent to interact with the TelemetryFlow Observatory (TFO) Platform API. All tools are implemented in pure Python (stdlib only, no pip dependencies), follow a consistent execution pattern, and are registered via `plugin.yaml`. The plugin covers core telemetry querying, infrastructure monitoring, platform management, AI/LLM features, remediation actions, and RCA report generation.

---

## REQ-1: Shared Module (`_shared.py`)

### REQ-1.1: HTTP Client (`tfo_request`)

- **REQ-1.1.1**: The `tfo_request(path, method, data, params)` function shall construct HTTP requests to the TFO Platform API using `urllib.request`.
- **REQ-1.1.2**: The base URL shall be read from `TELEMETRYFLOW_API_URL` env var, defaulting to `http://localhost:3000/api/v2`.
- **REQ-1.1.3**: All requests shall include `Authorization: Bearer <key>`, `Content-Type: application/json`, and `Accept: application/json` headers.
- **REQ-1.1.4**: The API key shall be read from `TELEMETRYFLOW_API_KEY` env var. If missing or empty, the tool shall print an error to stderr and exit with code 1.
- **REQ-1.1.5**: Query parameters shall be appended as a query string, excluding entries with `None` values.
- **REQ-1.1.6**: Request bodies shall be JSON-encoded via `json.dumps` when `data` is not `None`.
- **REQ-1.1.7**: HTTP timeout shall be 30 seconds.
- **REQ-1.1.8**: On HTTP 204 response, the function shall return `None`.
- **REQ-1.1.9**: On `HTTPError`, the function shall print `HTTP {code}: {body}` to stderr and exit with code 1.
- **REQ-1.1.10**: On `URLError` (connection failure), the function shall print `Connection error: {reason}` to stderr and exit with code 1.
- **REQ-1.1.11**: Every URL shall be validated by `_validate_url()` before the request is sent.

### REQ-1.2: ClickHouse Query Routing (`clickhouse_query`)

- **REQ-1.2.1**: The `clickhouse_query(sql, fmt)` function shall route SQL queries through `POST /telemetry/query` — never directly to ClickHouse.
- **REQ-1.2.2**: The request body shall contain `{"sql": "<sql>", "format": "<fmt>"}`.
- **REQ-1.2.3**: The default format shall be `"JSON"`.
- **REQ-1.2.4**: All ClickHouse queries shall use `FORMAT JSON` in the SQL statement for direct-query tools.

### REQ-1.3: CLI Argument Parsing (`parse_args`)

- **REQ-1.3.1**: The `parse_args()` function shall parse `sys.argv` using the `--key value` pattern.
- **REQ-1.3.2**: Flags without values (e.g., `--verbose`) shall be stored as `{"verbose": "true"}`.
- **REQ-1.3.3**: Positional arguments (non-`--` prefixed) shall be ignored.
- **REQ-1.3.4**: The function shall return a `dict` of string key-value pairs.

### REQ-1.4: Output Helpers

- **REQ-1.4.1**: `output_json(data)` shall print `json.dumps(data, indent=2, default=str)` to stdout.
- **REQ-1.4.2**: `now_iso()` shall return the current UTC timestamp in ISO 8601 format.

### REQ-1.5: Validation Constants

- **REQ-1.5.1**: `CONTEXT_TYPES` shall be a list of 74 valid context type strings covering all TFO modules (metrics, logs, traces, kubernetes-_, infra-_, db-monitoring-_, iam-_, tenancy-\*, etc.).
- **REQ-1.5.2**: `INSIGHT_TYPES` shall be `["chronology", "prediction", "recommendation", "root-cause", "pattern"]`.
- **REQ-1.5.3**: `PROVIDER_TYPES` shall be a list of 15 valid LLM provider types: anthropic, claude, openai, google, gemini, deepseek, qwen, ollama, mistral, grok, kimi, zhipu, mimo, openrouter, custom.
- **REQ-1.5.4**: No duplicate entries shall exist in `CONTEXT_TYPES`, `INSIGHT_TYPES`, or `PROVIDER_TYPES`.

### REQ-1.6: SSRF Protection (`_validate_url`)

- **REQ-1.6.1**: The function shall extract the URL scheme and verify it is in `{"http", "https"}`.
- **REQ-1.6.2**: Scheme checking shall be case-insensitive.
- **REQ-1.6.3**: Blocked schemes (file, ftp, javascript, data, etc.) shall trigger an error message to stderr and `sys.exit(1)`.

---

## REQ-2: Core Telemetry Tools (7 tools)

### REQ-2.1: `query_metrics`

- **REQ-2.1.1**: Shall accept `--service` (required), `--metric`, `--duration`, `--resolution`, `--workspace_id`, `--limit`.
- **REQ-2.1.2**: Default duration: `1h`. Default resolution: `5m`. Default limit: `100`.
- **REQ-2.1.3**: Resolution shall map to ClickHouse tables: `1m` → `metrics_1m`, `5m`/`15m`/`30m` → `metrics_5m`, `1h` → `metrics_1h`.
- **REQ-2.1.4**: Duration shall map to SQL `INTERVAL` clauses: `15m` → `INTERVAL 15 MINUTE`, `1h` → `INTERVAL 1 HOUR`, etc.
- **REQ-2.1.5**: When `--metric` is provided, query shall return time-series: `minute, service_name, metric_name, avg_value, p95, p99, min_value, max_value, sample_count`.
- **REQ-2.1.6**: When `--metric` is omitted, query shall return metric summary: `service_name, metric_name, metric_type, avg_value, max_value, min_value, sample_count`.
- **REQ-2.1.7**: Shall route queries through `clickhouse_query()`, not directly to ClickHouse.

### REQ-2.2: `search_logs`

- **REQ-2.2.1**: Shall accept `--service`, `--severity` (default: `ERROR`), `--duration` (default: `1h`), `--search`, `--workspace_id`, `--limit` (default: `100`).
- **REQ-2.2.2**: Shall query `otel_logs` table with severity filtering (`severity_text >= '{severity}'`).
- **REQ-2.2.3**: Full-text search via `body LIKE '%{search}%'` when `--search` is provided.
- **REQ-2.2.4**: Results ordered by `timestamp DESC`.

### REQ-2.3: `list_traces`

- **REQ-2.3.1**: Shall accept `--service`, `--trace_id`, `--min_duration` (default: `500`), `--duration` (default: `1h`), `--workspace_id`, `--limit` (default: `50`).
- **REQ-2.3.2**: When `--trace_id` is provided, return full waterfall: `span_id, parent_span_id, name, service_name, duration_ms, status_code, timestamp` ordered by `timestamp`.
- **REQ-2.3.3**: When `--trace_id` is omitted, return slow spans ordered by `duration_ns DESC`.
- **REQ-2.3.4**: Duration filter uses `duration_ns > {min_duration} * 1000000`.

### REQ-2.4: `get_exemplars`

- **REQ-2.4.1**: Shall accept `--service`, `--metric`, `--trace_id`, `--duration` (default: `1h`), `--workspace_id`, `--limit` (default: `20`).
- **REQ-2.4.2**: Shall query `exemplars` table returning `timestamp, metric_name, service_name, trace_id, span_id, value`.
- **REQ-2.4.3**: Results ordered by `value DESC`.

### REQ-2.5: `query_correlations`

- **REQ-2.5.1**: Shall accept `--service`, `--correlation_type`, `--duration` (default: `1h`), `--workspace_id`, `--limit` (default: `50`).
- **REQ-2.5.2**: Shall query `signal_correlations_1h` materialized view.
- **REQ-2.5.3**: Return aggregated: `service_name, correlation_type, count() AS correlation_count, avg(confidence_score) AS avg_confidence`.
- **REQ-2.5.4**: Grouped by `service_name, correlation_type`, ordered by `correlation_count DESC`.

### REQ-2.6: `query_tfql`

- **REQ-2.6.1**: Unified query engine supporting three signals: `metrics`, `logs`, `traces` (via `--signal`).
- **REQ-2.6.2**: Signal `metrics`: supports actions `names` (list metric names), `labels` (get label values via `--label-name`), and default (query metrics via POST).
- **REQ-2.6.3**: Signal `logs`: supports actions `severity-distribution`, `count-by-severity`, and default (search logs via POST with `--query`, `--severity`, `--service-name`, `--trace-id`).
- **REQ-2.6.4**: Signal `traces`: supports actions `summaries`, `services`, `operations`, and default (query traces with `--trace-id`, `--service-name`, `--span-name`, `--status-code`, `--min-duration`, `--max-duration`).
- **REQ-2.6.5**: Uses TFO REST API endpoints (`/query/signals/*`), not ClickHouse directly.

### REQ-2.7: `query_ai_intelligence`

- **REQ-2.7.1**: Shall accept `--module` (one of: `anomaly-detection`, `corrective-maintenance`, `predictive-maintenance`, `cost-optimization`) and `--action` (list, get, analyze/predictions/recommendations/plans).
- **REQ-2.7.2**: Module `anomaly-detection`: actions `list`, `get`, `analyze`. Endpoints: `/ai-intelligence/anomaly-detection/anomalies`.
- **REQ-2.7.3**: Module `predictive-maintenance`: actions `list`/`predictions`, `get`. Endpoints: `/ai-intelligence/predictive-maintenance/predictions`.
- **REQ-2.7.4**: Module `cost-optimization`: actions `list`/`recommendations`, `get`. Endpoints: `/ai-intelligence/cost-optimization/recommendations`.
- **REQ-2.7.5**: Module `corrective-maintenance`: actions `list`/`plans`, `get`. Endpoints: `/ai-intelligence/corrective-maintenance/plans`.
- **REQ-2.7.6**: All list actions shall support `--page`, `--limit` (default: `20`) pagination params.

---

## REQ-3: Monitoring Tools (8 tools)

### REQ-3.1: `check_k8s`

- **REQ-3.1.1**: Shall accept `--resource` (default: `overview`), `--cluster`, `--namespace`.
- **REQ-3.1.2**: Valid resources: `overview`, `clusters`, `nodes`, `namespaces`, `pods`, `deployments`, `pv`.
- **REQ-3.1.3**: Resources `pods` and `deployments` shall support `--namespace` and `--cluster` filter params.
- **REQ-3.1.4**: Resources `nodes`, `namespaces`, `pv` shall support `--cluster` filter param.
- **REQ-3.1.5**: API paths: `/kubernetes/{resource}` with appropriate query params.

### REQ-3.2: `check_vm`

- **REQ-3.2.1**: Shall accept `--resource` (default: `list`), `--vm-id`, `--provider`, `--status`, `--metric-name`, `--from`, `--to`.
- **REQ-3.2.2**: Valid resources: `list`, `get`, `metrics`.
- **REQ-3.2.3**: Resource `list` supports `--provider`, `--status`, `--page`, `--page-size` filters.
- **REQ-3.2.4**: Resources `get` and `metrics` require `--vm-id`.
- **REQ-3.2.5**: Resource `metrics` supports `--metric-name`, `--from`, `--to` params.
- **REQ-3.2.6**: API paths: `/monitoring/vms`, `/monitoring/vms/{id}`, `/monitoring/vms/{id}/metrics`.

### REQ-3.3: `check_agent`

- **REQ-3.3.1**: Shall accept `--resource` (default: `list`), `--agent-id`, `--status`, `--type`, `--name`, `--host`, `--last-seen-within-minutes`.
- **REQ-3.3.2**: Valid resources: `list`, `stats`, `get`, `health`.
- **REQ-3.3.3**: Resources `get` and `health` require `--agent-id`.
- **REQ-3.3.4**: Resource `health` supports `--from`, `--to`, `--limit` params.
- **REQ-3.3.5**: API paths: `/monitoring/agents`, `/monitoring/agents/stats`, `/monitoring/agents/{id}`, `/monitoring/agents/{id}/health`.

### REQ-3.4: `check_infra`

- **REQ-3.4.1**: Shall accept `--resource` (default: `overview`).
- **REQ-3.4.2**: Valid resources: `overview`, `cpu`, `memory`, `storage`, `network`.
- **REQ-3.4.3**: Maps to API path `/monitoring/vm/{resource}`.
- **REQ-3.4.4**: Invalid resource shall print error and exit with code 1.

### REQ-3.5: `check_uptime`

- **REQ-3.5.1**: Shall accept `--resource` (default: `monitors`), `--monitor-id`, `--status-page-id`, `--status`.
- **REQ-3.5.2**: Valid resources: `monitors`, `stats`, `checks`, `daily-stats`, `hourly-stats`, `ssl-summary`, `ssl-trend`, `status-pages`, `incidents`, `subscribers`.
- **REQ-3.5.3**: Resources `stats`, `checks`, `daily-stats`, `hourly-stats`, `ssl-trend` require `--monitor-id`.
- **REQ-3.5.4**: Resources `incidents`, `subscribers` require `--status-page-id`.
- **REQ-3.5.5**: Resource `incidents` supports `--status` filter param.
- **REQ-3.5.6**: Resource `monitors` supports optional `--monitor-id` (returns single monitor).
- **REQ-3.5.7**: Resource `status-pages` supports optional `--status-page-id` (returns single page).
- **REQ-3.5.8**: API paths: `/monitoring/uptime/monitors/*`, `/monitoring/status-pages/*`.

### REQ-3.6: `check_service_map`

- **REQ-3.6.1**: Shall accept `--resource` (default: `map`), `--service-id`, `--type`, `--status`, `--namespace`, `--depth`.
- **REQ-3.6.2**: Valid resources: `map`, `services`, `get`, `dependencies`, `health`, `metrics`, `topology`, `trace-dependencies`.
- **REQ-3.6.3**: Resources `get`, `dependencies`, `health`, `metrics` require `--service-id`.
- **REQ-3.6.4**: Resource `services` supports `--type`, `--status`, `--namespace` filters.
- **REQ-3.6.5**: Resource `topology` supports `--depth` param.
- **REQ-3.6.6**: API paths: `/monitoring/service-map/*`.

### REQ-3.7: `check_network_map`

- **REQ-3.7.1**: Shall accept `--resource` (default: `topology`), `--node-id`, `--type`, `--status`, `--cluster`, `--depth`.
- **REQ-3.7.2**: Valid resources: `topology`, `nodes`, `connections`, `traffic`, `flows`, `dns`, `k8s-flows`, `snmp-configs`, `paths`.
- **REQ-3.7.3**: Resources `connections` and `traffic` require `--node-id`.
- **REQ-3.7.4**: Resource `nodes` supports `--type`, `--status`, `--cluster` filters.
- **REQ-3.7.5**: Resource `topology` supports `--depth` param.
- **REQ-3.7.6**: API paths: `/monitoring/network-map/*`.

### REQ-3.8: `check_db_monitoring`

- **REQ-3.8.1**: Shall accept `--resource` (default: `inventory`), `--db-type`, `--min-duration` (default: `50`), `--instance-id`, `--limit` (default: `20`), `--workspace-id`.
- **REQ-3.8.2**: Valid resources: `inventory`, `qan`, `slow-queries`, `engine-metrics`, `wait-stats`, `top-queries`.
- **REQ-3.8.3**: Supported `--db-type` values (16): postgresql, mysql, mariadb, percona, clickhouse, mongodb-community, mongodb-atlas, mssql, sqlite3, timescaledb, aurora, aws-rds-mysql, aws-rds-aurora, aws-rds-postgresql, aws-dynamodb, cockroachdb.
- **REQ-3.8.4**: Resource `engine-metrics` maps each `--db-type` to a specific ClickHouse table (e.g., `postgresql` → `db_postgresql_metrics`).
- **REQ-3.8.5**: Resource `slow-queries` queries `qan_metrics` table via `clickhouse_query()`.
- **REQ-3.8.6**: Resource `wait-stats` is only available for `mssql`.
- **REQ-3.8.7**: Resource `top-queries` is available for: mysql, postgresql, mssql, aurora, clickhouse.
- **REQ-3.8.8**: Resource `inventory` and `qan` use `tfo_request()` to TFO API.

---

## REQ-4: Platform Tools (8 tools)

### REQ-4.1: `manage_alerts`

- **REQ-4.1.1**: Shall accept `--resource` (default: `rules`), `--rule-id`, `--instance-id`, `--query`, plus filter params.
- **REQ-4.1.2**: Valid resources: `rules`, `rule-detail`, `instances`, `instance-detail`, `stats`, `channels`, `validate-tfql`.
- **REQ-4.1.3**: Resource `rules` supports `--enabled`, `--severity`, `--state`, `--search` filter params.
- **REQ-4.1.4**: Resource `instances` supports `--status`, `--severity`, `--rule`, `--from`, `--to` filter params.
- **REQ-4.1.5**: Resource `channels` supports `--enabled`, `--type` filter params.
- **REQ-4.1.6**: Resource `validate-tfql` requires `--query`, uses POST to `/alert-rules/validate-tfql`.
- **REQ-4.1.7**: Resources `rule-detail` and `instance-detail` require their respective ID args.

### REQ-4.2: `manage_dashboards`

- **REQ-4.2.1**: Shall accept `--resource` (default: `list`), `--dashboard-id`.
- **REQ-4.2.2**: Valid resources: `list`, `get`, `export`, `shared`, `public`, `templates`, `shared-graphs`.
- **REQ-4.2.3**: Resources `get` and `export` require `--dashboard-id`.
- **REQ-4.2.4**: Resource `list` supports `--tag`, `--tags`, `--isPublic`, `--isFavorite`, `--search` filters.
- **REQ-4.2.5**: API paths: `/dashboards/*`.

### REQ-4.3: `manage_reports`

- **REQ-4.3.1**: Shall accept `--resource` (default: `definitions`), `--definition-id`, `--execution-id`.
- **REQ-4.3.2**: Valid resources: `definitions`, `definition-detail`, `executions`, `execution-detail`, `stats`, `generate`.
- **REQ-4.3.3**: Resource `definitions` supports `--type`, `--schedule`, `--enabled`, `--search` filters.
- **REQ-4.3.4**: Resource `generate` requires `--definition-id`, uses POST.
- **REQ-4.3.5**: API paths: `/reports/*`.

### REQ-4.4: `manage_data_masking`

- **REQ-4.4.1**: Shall accept `--action` (default: `list`), `--policy-id`, `--name`, `--field`, `--pattern`, `--enabled`.
- **REQ-4.4.2**: Valid actions: `list`, `get`, `create`, `toggle`.
- **REQ-4.4.3**: Action `create` requires `--name`. Fields default: `field=body`, `pattern=email`, `enabled=true`.
- **REQ-4.4.4**: Action `toggle` requires `--policy-id`, uses PATCH.
- **REQ-4.4.5**: API paths: `/data-masking/policies/*`.

### REQ-4.5: `query_platform`

- **REQ-4.5.1**: Shall accept `--resource` (default: `iam-users`), `--page`, `--page-size`, `--duration`.
- **REQ-4.5.2**: Valid resources map directly to API paths: `iam-users` → `/iam/users`, `iam-roles` → `/iam/roles`, `iam-permissions` → `/iam/permissions`, `iam-assignments` → `/iam/assignments`, `tenancy-orgs` → `/tenancy/organizations`, `tenancy-workspaces` → `/tenancy/workspaces`, `tenancy-regions` → `/tenancy/regions`, `tenancy-tenants` → `/tenancy/tenants`, `audit-logs` → `/audit/logs`, `retention-policies` → `/retention/policies`, `subscriptions` → `/subscription/plans`, `api-keys` → `/api-keys`, `notification-channels` → `/notification/channels`.
- **REQ-4.5.3**: Resource `audit-logs` supports `--duration` param.
- **REQ-4.5.4**: All resources support `--page` and `--page-size` pagination.

### REQ-4.6: `query_account`

- **REQ-4.6.1**: Shall accept `--resource` (default: `profile`).
- **REQ-4.6.2**: Valid resources: `profile`, `security`, `sessions`, `preferences`.
- **REQ-4.6.3**: Maps to API paths: `/account/profile`, `/account/security`, `/account/sessions`, `/account/preferences`.

### REQ-4.7: `query_audit`

- **REQ-4.7.1**: Shall accept `--resource` (default: `logs`), `--duration`, `--event-type`, `--result`, `--user-email`, `--ip-address`, `--resource` (filter), `--page`, `--page-size`.
- **REQ-4.7.2**: Queries `/audit/logs` with filter params.

### REQ-4.8: `query_subscription`

- **REQ-4.8.1**: Shall accept `--resource` (default: `current`), `--plan-id`, `--metric-type`, `--invoice-id`.
- **REQ-4.8.2**: Valid resources: `current`, `plans`, `plan-detail`, `usage`, `usage-check`, `invoices`, `invoice-detail`.
- **REQ-4.8.3**: Resource `usage-check` requires `--metric-type`.
- **REQ-4.8.4**: Resources `plan-detail` and `invoice-detail` require their respective ID args.
- **REQ-4.8.5**: API paths: `/subscription/*`.

---

## REQ-5: Infrastructure Tools (4 tools)

### REQ-5.1: `manage_retention`

- **REQ-5.1.1**: Shall accept `--resource` (default: `policies`), `--policy-id`, `--data-type`, `--include-defaults`, `--dry-run`.
- **REQ-5.1.2**: Valid resources: `policies`, `policy-detail`, `statistics`, `enforce`.
- **REQ-5.1.3**: Resource `policies` supports `--data-type` and `--include-defaults` filters.
- **REQ-5.1.4**: Resource `policy-detail` requires `--policy-id`.
- **REQ-5.1.5**: Resource `enforce` uses POST, supports `--dry-run true` to set `dryRun: True` in request body.
- **REQ-5.1.6**: API paths: `/retention/policies/*`.

### REQ-5.2: `manage_tenancy`

- **REQ-5.2.1**: Shall accept `--resource` (default: `regions`), `--region-id`, `--tenant-id`, `--org-id`.
- **REQ-5.2.2**: Valid resources: `regions`, `region-detail`, `tenants`, `tenant-detail`, `organizations`, `org-detail`, `workspaces`.
- **REQ-5.2.3**: Resource `organizations` supports `--region-id` filter.
- **REQ-5.2.4**: Resource `workspaces` requires `--org-id`.
- **REQ-5.2.5**: Detail resources require their respective ID args.
- **REQ-5.2.6**: API paths: `/tenancy/*`.

### REQ-5.3: `manage_iam`

- **REQ-5.3.1**: Shall accept `--resource` (default: `users`), `--user-id`, `--role-id`, `--group-id`, `--page`, `--page-size`.
- **REQ-5.3.2**: Valid resources: `users`, `user-detail`, `user-roles`, `user-permissions`, `roles`, `role-detail`, `role-permissions`, `permissions`, `groups`, `group-detail`, `group-users`, `audit-logs`.
- **REQ-5.3.3**: Resources requiring IDs: `user-detail`, `user-roles`, `user-permissions` require `--user-id`; `role-detail`, `role-permissions` require `--role-id`; `group-detail`, `group-users` require `--group-id`.
- **REQ-5.3.4**: Resource `audit-logs` supports `--page`, `--page-size` pagination.
- **REQ-5.3.5**: API paths: `/iam/*`.

### REQ-5.4: `manage_sso`

- **REQ-5.4.1**: Shall accept `--resource` (default: `providers`), `--provider-id`, `--org-id`.
- **REQ-5.4.2**: Valid resources: `providers`, `provider-detail`, `public-providers`, `connections`.
- **REQ-5.4.3**: Resource `provider-detail` requires `--provider-id`.
- **REQ-5.4.4**: Resource `public-providers` requires `--org-id`.
- **REQ-5.4.5**: API paths: `/sso/*`.

---

## REQ-6: AI & LLM Tools (7 tools)

### REQ-6.1: `chat_with_context`

- **REQ-6.1.1**: Shall accept `--message` (required), `--context-type` (default: `metrics`), `--context-id`, `--provider-id`, `--conversation-id`, `--time-from`, `--time-to`.
- **REQ-6.1.2**: `--context-type` must be validated against `CONTEXT_TYPES`. Invalid values shall exit with code 1.
- **REQ-6.1.3**: If `--time-from` is not provided, default to 1 hour ago from current UTC time.
- **REQ-6.1.4**: If `--time-to` is not provided, default to `now_iso()`.
- **REQ-6.1.5**: Uses POST to `/llm/chat/message`.
- **REQ-6.1.6**: Request body: `{"message": "...", "contextType": "...", "contextId": "...", "providerId": "...", "conversationId": "...", "timeFrom": "...", "timeTo": "..."}`.

### REQ-6.2: `stream_chat`

- **REQ-6.2.1**: Shall accept `--message` (required), `--context-type` (default: `metrics`), `--provider-id`, `--conversation-id`.
- **REQ-6.2.2**: `--context-type` must be validated against `CONTEXT_TYPES`.
- **REQ-6.2.3**: Uses SSE (Server-Sent Events) via POST to `/llm/chat/stream`.
- **REQ-6.2.4**: Timeout shall be 120 seconds for streaming connections.
- **REQ-6.2.5**: Accept header shall be `text/event-stream`.
- **REQ-6.2.6**: Shall parse SSE events: `start` (capture `conversationId`), `chunk` (print content), `end` (print messageId and latencyMs to stderr), `error` (exit with code 1).
- **REQ-6.2.7**: Time defaults: `timeFrom` = 1 hour ago, `timeTo` = `now_iso()`.
- **REQ-6.2.8**: On `HTTPError`, print error to stderr and exit with code 1.

### REQ-6.3: `manage_conversation`

- **REQ-6.3.1**: Shall accept `--action` (default: `list`), `--conversation-id`, `--context-type`, `--search`, `--is-archived`, `--page`, `--page-size`.
- **REQ-6.3.2**: Valid actions: `list`, `get`, `archive`, `delete`.
- **REQ-6.3.3**: Actions `get`, `archive`, `delete` require `--conversation-id`.
- **REQ-6.3.4**: Action `delete` uses DELETE method, prints confirmation message.
- **REQ-6.3.5**: Action `archive` uses POST to `/llm/chat/conversations/{id}/archive`.
- **REQ-6.3.6**: API paths: `/llm/chat/conversations/*`.

### REQ-6.4: `generate_insight`

- **REQ-6.4.1**: Shall accept `--insight-type` (default: `root-cause`), `--context-type` (default: `metrics`), `--context-id`, `--provider-id`, `--time-from`, `--time-to`, `--additional-context`.
- **REQ-6.4.2**: `--insight-type` must be validated against `INSIGHT_TYPES`.
- **REQ-6.4.3**: `--context-type` must be validated against `CONTEXT_TYPES`.
- **REQ-6.4.4**: `--additional-context` shall be parsed as JSON if valid, otherwise wrapped as `{"note": "<value>"}`.
- **REQ-6.4.5**: Uses POST to `/llm/insights/{insight-type}`.

### REQ-6.5: `query_llm_usage`

- **REQ-6.5.1**: Shall accept `--action` (default: `summary`), `--duration` (default: `24h`), `--limit` (default: `20`), `--view`.
- **REQ-6.5.2**: Valid actions: `summary`, `by-provider`, `by-model`, `by-context`, `top-users`, `interval`.
- **REQ-6.5.3**: Queries `llm_usage_analytics` table (and interval views: `llm_usage_5m`, `llm_usage_15m`, `llm_usage_6h`) via `clickhouse_query()`.
- **REQ-6.5.4**: Action `interval` supports `--view` (default: `5m`): `5m` → `llm_usage_5m`, `15m` → `llm_usage_15m`, `6h` → `llm_usage_6h`.
- **REQ-6.5.5**: Duration mapping: `1h`, `6h`, `24h`, `7d`, `30d`.

### REQ-6.6: `manage_provider`

- **REQ-6.6.1**: Shall accept `--action` (default: `list`), `--provider-id`, `--name`, `--type`, `--api-key`, `--model`, `--base-url`, `--temperature` (default: `0.7`), `--max-tokens` (default: `4096`), `--top-p` (default: `1.0`), `--is-default`, `--page`, `--page-size`.
- **REQ-6.6.2**: Valid actions: `list`, `get`, `default`, `create`, `validate`, `test-key`, `set-default`.
- **REQ-6.6.3**: Action `create` requires `--name`, `--api-key`, `--model`. Validates `--type` against `PROVIDER_TYPES`.
- **REQ-6.6.4**: Action `validate` and `set-default` require `--provider-id`.
- **REQ-6.6.5**: Action `test-key` requires `--api-key`.
- **REQ-6.6.6**: API paths: `/llm/providers/*`.

### REQ-6.7: AI Intelligence (`query_ai_intelligence`)

(Covered in REQ-2.7 above — part of core telemetry but semantically AI)

---

## REQ-7: Remediation Tools (4 tools, gated)

### REQ-7.1: Approval Gate Requirements

- **REQ-7.1.1**: All four remediation tools shall have `requires_approval: true` in `plugin.yaml`.
- **REQ-7.1.2**: Each tool shall print a PROPOSAL message to stdout describing the action before execution.
- **REQ-7.1.3**: Each tool shall print a Risk assessment: `LOW`, `MEDIUM`, or `HIGH`.
- **REQ-7.1.4**: Each tool shall print `Awaiting human approval...` before making the API call.

### REQ-7.2: `scale_deployment`

- **REQ-7.2.1**: Shall accept `--name` (required), `--namespace` (default: `default`), `--replicas` (default: `1`).
- **REQ-7.2.2**: Risk: `MEDIUM` — cost impact, may not solve root cause.
- **REQ-7.2.3**: Uses POST to `/kubernetes/deployments/scale`.
- **REQ-7.2.4**: Request body: `{"name": "...", "namespace": "...", "replicas": N}`.

### REQ-7.3: `restart_pod`

- **REQ-7.3.1**: Shall accept `--deployment`, `--pod`, `--namespace` (default: `default`). At least one of `--deployment` or `--pod` is required.
- **REQ-7.3.2**: Risk: `HIGH` — may lose in-flight requests, temporary disruption.
- **REQ-7.3.3**: If `--deployment`: uses POST to `/kubernetes/deployments/restart` with `{"name": "...", "namespace": "..."}`.
- **REQ-7.3.4**: If `--pod`: uses POST to `/kubernetes/pods/restart` with `{"name": "...", "namespace": "..."}`.

### REQ-7.4: `rollback_deploy`

- **REQ-7.4.1**: Shall accept `--name` (required), `--namespace` (default: `default`), `--revision` (optional).
- **REQ-7.4.2**: Risk: `LOW` — rollback to known-good version.
- **REQ-7.4.3**: Uses POST to `/kubernetes/deployments/rollback`.
- **REQ-7.4.4**: Request body includes `revision` only when provided.

### REQ-7.5: `update_alert`

- **REQ-7.5.1**: Shall accept `--rule-id` (required), `--threshold`, `--enabled`, `--severity`. At least one update field is required.
- **REQ-7.5.2**: Risk: `LOW` — alert configuration change only.
- **REQ-7.5.3**: Uses PATCH to `/alerts/rules/{rule-id}`.
- **REQ-7.5.4**: `--threshold` shall be cast to `float`. `--enabled` shall be cast to `bool`.

---

## REQ-8: RCA Tools (3 tools)

### REQ-8.1: `generate_rca_report`

- **REQ-8.1.1**: Shall accept `--action` (default: `rca`), `--alert-id`, `--service`, `--root-cause`, `--remediation`, `--start-time`, `--end-time`, `--severity` (default: `high`), `--author` (default: `Hermes Agent`), `--title`, `--workspace-id`, `--submit` (default: `false`), `--project-key`, `--issue-type`, `--trello-list`.
- **REQ-8.1.2**: Valid actions: `rca`, `jira`, `jira-submit`, `trello`, `trello-submit`, `all`, `submit`.
- **REQ-8.1.3**: Shall generate a markdown RCA report with: Executive Summary, Impact Assessment, 5W Analysis, Incident Timeline (mermaid), Incident Response Flow (mermaid), Root Cause Details, Contributing Factors, Action Items, Lessons Learned.
- **REQ-8.1.4**: Shall query real telemetry data (alert instances, metrics baseline, error logs, trace summary, audit events) from ClickHouse and TFO API.
- **REQ-8.1.5**: Data query failures shall be caught (`except SystemExit`) and not abort the report.
- **REQ-8.1.6**: Jira submission: requires `JIRA_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN` env vars. Creates an Issue via Jira REST API v2.
- **REQ-8.1.7**: Trello submission: requires `TRELLO_API_KEY`, `TRELLO_API_TOKEN`, `TRELLO_LIST_ID_INCIDENTS` env vars. Creates a card with labels and checklist.
- **REQ-8.1.8**: Jira/Trello toggle env vars: `JIRA_ENABLED`, `TRELLO_ENABLED`.
- **REQ-8.1.9**: All external URLs (Jira, Trello) shall pass through `_validate_url()`.

### REQ-8.2: `generate_postmortem`

- **REQ-8.2.1**: Shall accept `--action` (default: `postmortem`), `--alert-id`, `--service`, `--root-cause`, `--remediation`, `--start-time`, `--end-time`, `--severity`, `--author`, `--title`, `--what`, `--where`, `--why`, `--how`, `--summary`, `--went-well` (pipe-separated), `--improve` (pipe-separated), `--lucky` (pipe-separated), `--timeline-events` (JSON), `--why-not-sooner`.
- **REQ-8.2.2**: Valid actions: `postmortem`, `template`.
- **REQ-8.2.3**: Action `postmortem`: generates full postmortem report with Summary, Timeline, Root Cause Analysis (5W), Resolution, Remediation Flow (mermaid), Lessons Learned, Action Items, Appendix.
- **REQ-8.2.4**: Action `template`: returns a blank template with `{{PLACEHOLDER}}` fields.
- **REQ-8.2.5**: Default timeline events include the full agent pipeline: Alert → Triage → Investigator → Reviewer → Remediator → Human Approval → Execute → Verify.

### REQ-8.3: `generate_rca_template`

- **REQ-8.3.1**: Shall accept `--title`, `--service`, `--severity`, `--author`.
- **REQ-8.3.2**: Shall generate a blank RCA report template with all sections: Document Control, Executive Summary, Impact Assessment (with mermaid blast radius), 5W Analysis, Timeline (mermaid), Root Cause Deep Dive (with causal chain mermaid), Lessons Learned, Action Items, Jira/Trello Ticket Summary, Approval signatures.
- **REQ-8.3.3**: All fill-in fields shall use `{{PLACEHOLDER}}` format.

---

## REQ-9: Tool Registration (`plugin.yaml`)

### REQ-9.1: Plugin Metadata

- **REQ-9.1.1**: Plugin name: `telemetryflow`.
- **REQ-9.1.2**: Plugin version: `1.2.0`.
- **REQ-9.1.3**: Author: `TelemetryFlow`.
- **REQ-9.1.4**: Description shall reference all 20 TFO Platform modules.

### REQ-9.2: Tool Declarations

- **REQ-9.2.1**: All 40 tools shall be declared in the `tools:` list.
- **REQ-9.2.2**: Each tool shall have: `name`, `description`, `command: python3`, `args: ["${PLUGIN_DIR}/tools/<name>.py"]`.
- **REQ-9.2.3**: Remediation tools (`scale_deployment`, `restart_pod`, `rollback_deploy`, `update_alert`) shall have `requires_approval: true`.
- **REQ-9.2.4**: Non-remediation tools shall not have `requires_approval`.

### REQ-9.3: Environment Variables

- **REQ-9.3.1**: `TELEMETRYFLOW_API_URL`: TFO API base URL (required, default `http://localhost:3000/api/v2`).
- **REQ-9.3.2**: `TELEMETRYFLOW_API_KEY`: API key for JWT Bearer authentication (required).
- **REQ-9.3.3**: `TELEMETRYFLOW_WORKSPACE_ID`: Default workspace ID for ClickHouse queries (optional).

---

## REQ-10: Security

### REQ-10.1: ClickHouse Read-Only User

- **REQ-10.1.1**: A `hermes_readonly` user shall be created in ClickHouse with `readonly = 1` setting.
- **REQ-10.1.2**: The user shall have SELECT grants on exactly 20 telemetry tables (no system/config table access).
- **REQ-10.1.3**: Tables: `metrics_1m`, `metrics_5m`, `metrics_1h`, `otel_logs`, `otel_traces`, `exemplars`, `exemplars_1h`, `signal_correlations_1h`, `service_latency_percentiles_1h`, `service_error_rates_1h`, `logs_1h`, `qan_metrics`, `audit_logs`, `audit_logs_1h`, `uptime_checks`, `kubernetes_metrics_1h`, `vm_metrics_1h`, `service_map_metrics_1h`, `network_map_traffic_1h`, `network_map_connection_metrics_1h`.
- **REQ-10.1.4**: Setup script (`security/setup-readonly-user.sh`) shall accept password as CLI arg, read `CLICKHOUSE_HOST`, `CLICKHOUSE_PORT`, `CLICKHOUSE_USER`, `CLICKHOUSE_PASSWORD`, `TELEMETRYFLOW_DB_NAME` from env vars.
- **REQ-10.1.5**: The SQL template (`security/clickhouse-readonly.sql`) shall use `${TELEMETRYFLOW_DB_NAME}` placeholder.

### REQ-10.2: SSRF Protection

- **REQ-10.2.1**: All outbound HTTP requests (both TFO API and external Jira/Trello) shall pass through `_validate_url()`.
- **REQ-10.2.2**: Only `http://` and `https://` schemes are allowed.
- **REQ-10.2.3**: Blocked schemes shall trigger `sys.exit(1)`.

### REQ-10.3: API Key Management

- **REQ-10.3.1**: API keys shall be read from environment variables only, never hardcoded.
- **REQ-10.3.2**: Missing `TELEMETRYFLOW_API_KEY` shall produce a clear error and exit.
- **REQ-10.3.3**: Bearer tokens shall be sent in the `Authorization` header, not in query strings.

### REQ-10.4: SQL Injection Considerations

- **REQ-10.4.1**: ClickHouse queries use string interpolation from CLI args. This is acceptable because: (a) tools are invoked by the Hermes agent, not end users; (b) queries are routed through the TFO API which has its own validation; (c) the `hermes_readonly` user can only SELECT.
- **REQ-10.4.2**: User-supplied values in SQL shall have single quotes escaped via `replace("'", "''")` in RCA report queries.

---

## REQ-11: Testing

### REQ-11.1: Test Infrastructure

- **REQ-11.1.1**: 41 test files in `tests/unit/` — one per tool (`test_shared.py` for `_shared.py`).
- **REQ-11.1.2**: `conftest.py` shall provide fixtures: `mock_env`, `mock_urlopen`, `mock_urlopen_error`, `mock_urlopen_conn_error`, `capture_stdout`, `mock_exit`, `tfo_response_factory`, plus sample data constants.
- **REQ-11.1.3**: `mock_env` shall set: `TELEMETRYFLOW_API_URL`, `TELEMETRYFLOW_API_KEY`, `TELEMETRYFLOW_WORKSPACE_ID`, `TELEMETRYFLOW_ORGANIZATION_ID`, `CLICKHOUSE_HOST`, `CLICKHOUSE_PORT`, `CLICKHOUSE_USER`, `CLICKHOUSE_PASSWORD`, `CLICKHOUSE_DATABASE`.
- **REQ-11.1.4**: `mock_urlopen` shall return a mock response with `status=200` and configurable `read()` return value.
- **REQ-11.1.5**: `mock_urlopen_error` shall raise `HTTPError(404)`.
- **REQ-11.1.6**: `mock_urlopen_conn_error` shall raise `URLError("Connection refused")`.
- **REQ-11.1.7**: `capture_stdout` wraps `capsys` for compatibility.
- **REQ-11.1.8**: `mock_exit` patches `sys.exit` to prevent test termination.
- **REQ-11.1.9**: `autouse` fixture shall add `TOOLS_DIR` to `sys.path` and clean up imported modules after each test.

### REQ-11.2: Test Coverage Requirements

- **REQ-11.2.1**: Every tool shall test: (a) happy path for each resource/action, (b) missing required args exit with code 1, (c) unknown resource/action exits with code 1, (d) missing API key exits, (e) HTTP error exits, (f) connection error exits.
- **REQ-11.2.2**: `_shared.py` tests shall cover: `get_api_url`, `get_api_key`, `tfo_request` (GET, POST, params, 204, HTTP error, connection error), `clickhouse_query`, `parse_args` (key-value, flag, empty, edge cases), `output_json`, `now_iso`, `CONTEXT_TYPES`/`INSIGHT_TYPES`/`PROVIDER_TYPES` validation, `_validate_url` (http, https, blocked schemes, case-insensitive).
- **REQ-11.2.3**: Each test shall use `importlib.reload()` to ensure fresh module state.

---

## REQ-12: Implementation Constraints

- **REQ-12.1**: All tools shall use Python stdlib only (`json`, `os`, `sys`, `urllib.request`, `urllib.error`, `datetime`, `base64`). No pip dependencies.
- **REQ-12.2**: Every tool shall follow the execution pattern: `import → parse_args() → process → tfo_request() or clickhouse_query() → output_json()`.
- **REQ-12.3**: Every tool file shall be executable (`#!/usr/bin/env python3`) and have a `if __name__ == "__main__": main()` guard.
- **REQ-12.4**: Each tool file shall include docstring with usage examples.
- **REQ-12.5**: `sys.path.insert(0, os.path.dirname(__file__))` shall be used for `_shared` import.
- **REQ-12.6**: Error messages shall be printed to stderr. Normal output to stdout.
- **REQ-12.7**: Exit code 0 on success, 1 on any error.
