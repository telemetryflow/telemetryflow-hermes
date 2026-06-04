# Tool Reference

Complete parameter reference for all 23 TelemetryFlow Hermes plugin tools.

## Common Parameters

All tools accept these CLI arguments:

| Parameter        | Type   | Description                                                               |
| ---------------- | ------ | ------------------------------------------------------------------------- |
| `--workspace_id` | string | TelemetryFlow workspace ID (defaults to `TELEMETRYFLOW_WORKSPACE_ID` env) |
| `--output`       | string | Output format: `json` (default), `table`                                  |

All tools exit with code 1 on error and print error details to stderr.

---

## Core Telemetry

### query_metrics

Query TelemetryFlow metrics via ClickHouse materialized views.

```bash
python3 query_metrics.py \
  --table metrics_1m \
  --service payments-api \
  --metric memory_usage \
  --from "2026-06-04T00:00:00Z" \
  --to "2026-06-04T03:47:00Z" \
  --workspace_id ws_abc123
```

| Parameter       | Required | Description                                 |
| --------------- | -------- | ------------------------------------------- |
| `--table`       | Yes      | `metrics_1m`, `metrics_5m`, or `metrics_1h` |
| `--service`     | No       | Filter by service name                      |
| `--metric`      | No       | Filter by metric name                       |
| `--from`        | No       | Start time (ISO 8601, default: 1 hour ago)  |
| `--to`          | No       | End time (ISO 8601, default: now)           |
| `--aggregation` | No       | `avg`, `max`, `min`, `sum` (default: `avg`) |
| `--group_by`    | No       | Group by dimension (e.g., `host`, `pod`)    |

### search_logs

Search TelemetryFlow otel_logs with severity filtering and full-text search.

```bash
python3 search_logs.py \
  --service payments-api \
  --severity ERROR \
  --query "OOMKilled" \
  --from "2026-06-04T03:00:00Z" \
  --limit 100
```

| Parameter    | Required | Description                                        |
| ------------ | -------- | -------------------------------------------------- |
| `--service`  | No       | Filter by service name                             |
| `--severity` | No       | `TRACE`, `DEBUG`, `INFO`, `WARN`, `ERROR`, `FATAL` |
| `--query`    | No       | Full-text search term                              |
| `--from`     | No       | Start time (default: 30 minutes ago)               |
| `--to`       | No       | End time (default: now)                            |
| `--limit`    | No       | Max results (default: 50)                          |

### list_traces

List and analyze distributed traces from TelemetryFlow.

```bash
python3 list_traces.py \
  --service payments-api \
  --min_duration_ms 500 \
  --operation "POST /api/payments" \
  --limit 20
```

| Parameter           | Required | Description                      |
| ------------------- | -------- | -------------------------------- |
| `--service`         | No       | Filter by service name           |
| `--operation`       | No       | Filter by operation name         |
| `--min_duration_ms` | No       | Minimum duration in milliseconds |
| `--max_duration_ms` | No       | Maximum duration in milliseconds |
| `--status`          | No       | `ok` or `error`                  |
| `--from`            | No       | Start time (default: 1 hour ago) |
| `--to`              | No       | End time (default: now)          |
| `--limit`           | No       | Max results (default: 20)        |

### get_exemplars

Get exemplars linking metrics to specific traces.

```bash
python3 get_exemplars.py \
  --metric memory_usage \
  --service payments-api \
  --from "2026-06-04T03:00:00Z"
```

| Parameter   | Required | Description                      |
| ----------- | -------- | -------------------------------- |
| `--metric`  | No       | Filter by metric name            |
| `--service` | No       | Filter by service name           |
| `--from`    | No       | Start time (default: 1 hour ago) |
| `--to`      | No       | End time (default: now)          |
| `--limit`   | No       | Max results (default: 20)        |

### query_correlations

Query signal_correlations_1h for cross-signal correlation analysis.

```bash
python3 query_correlations.py \
  --signal_types "metrics,logs,traces" \
  --service payments-api \
  --from "2026-06-04T03:00:00Z"
```

| Parameter        | Required | Description                                      |
| ---------------- | -------- | ------------------------------------------------ |
| `--signal_types` | No       | Comma-separated: `metrics,logs,traces,exemplars` |
| `--service`      | No       | Filter by service name                           |
| `--from`         | No       | Start time (default: 1 hour ago)                 |
| `--to`           | No       | End time (default: now)                          |
| `--limit`        | No       | Max results (default: 20)                        |

---

## Infrastructure Monitoring

### check_k8s

Check Kubernetes cluster health.

```bash
python3 check_k8s.py --scope pods --namespace production
python3 check_k8s.py --scope overview
```

| Parameter          | Required | Description                                                                |
| ------------------ | -------- | -------------------------------------------------------------------------- |
| `--scope`          | Yes      | `overview`, `clusters`, `nodes`, `namespaces`, `pods`, `deployments`, `pv` |
| `--cluster`        | No       | Filter by cluster name                                                     |
| `--namespace`      | No       | Filter by namespace                                                        |
| `--label_selector` | No       | Kubernetes label selector                                                  |

### check_infra

Check infrastructure health via vm_metrics_1h.

```bash
python3 check_infra.py --scope cpu --host node-3
```

| Parameter | Required | Description                                       |
| --------- | -------- | ------------------------------------------------- |
| `--scope` | Yes      | `overview`, `cpu`, `memory`, `storage`, `network` |
| `--host`  | No       | Filter by hostname                                |
| `--from`  | No       | Start time (default: 1 hour ago)                  |

### check_db_monitoring

Check database monitoring for 16+ database types.

```bash
python3 check_db_monitoring.py --db-type postgresql --action qan
python3 check_db_monitoring.py --db-type mysql --action overview
```

| Parameter    | Required | Description                                                                                                                                                                                                                          |
| ------------ | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `--db_type`  | Yes      | `postgresql`, `mysql`, `mariadb`, `percona`, `clickhouse`, `mongodb-community`, `mongodb-atlas`, `mssql`, `sqlite3`, `timescaledb`, `aurora`, `aws-rds-mysql`, `aws-rds-aurora`, `aws-rds-postgresql`, `aws-dynamodb`, `cockroachdb` |
| `--action`   | Yes      | `overview`, `qan`, `performance`, `connections`, `replication`, `storage`                                                                                                                                                            |
| `--instance` | No       | Database instance identifier                                                                                                                                                                                                         |

---

## Platform Management

### check_uptime

Check uptime monitors and status pages.

```bash
python3 check_uptime.py --scope monitors
python3 check_uptime.py --scope incidents --monitor api-health
```

| Parameter   | Required | Description                                               |
| ----------- | -------- | --------------------------------------------------------- |
| `--scope`   | Yes      | `monitors`, `response-times`, `status-pages`, `incidents` |
| `--monitor` | No       | Filter by monitor name                                    |
| `--from`    | No       | Start time (default: 24 hours ago)                        |

### query_ai_intelligence

Query AI Intelligence modules.

```bash
python3 query_ai_intelligence.py --module anomaly-detection --action summary
```

| Parameter   | Required | Description                                                                                  |
| ----------- | -------- | -------------------------------------------------------------------------------------------- |
| `--module`  | Yes      | `anomaly-detection`, `corrective-maintenance`, `predictive-maintenance`, `cost-optimization` |
| `--action`  | Yes      | `summary`, `details`, `predictions`, `recommendations`                                       |
| `--service` | No       | Filter by service name                                                                       |

### query_platform

Query platform management: IAM, Tenancy, Audit, etc.

```bash
python3 query_platform.py --module iam --action list-users
python3 query_platform.py --module tenancy --action list-workspaces
```

| Parameter  | Required | Description                                                                         |
| ---------- | -------- | ----------------------------------------------------------------------------------- |
| `--module` | Yes      | `iam`, `tenancy`, `audit`, `retention`, `subscription`, `api-keys`, `notifications` |
| `--action` | Yes      | Varies per module                                                                   |
| `--id`     | No       | Specific resource ID                                                                |

### query_account

Query account-scoped data.

```bash
python3 query_account.py --scope profile
```

| Parameter | Required | Description                                                                       |
| --------- | -------- | --------------------------------------------------------------------------------- |
| `--scope` | Yes      | `profile`, `security`, `sessions`, `notifications`, `preferences`, `organization` |

### manage_data_masking

Manage PII data masking policies.

```bash
python3 manage_data_masking.py --action list
python3 manage_data_masking.py --action create --rule '{"field":"email","pattern":"email","replacement":"***"}'
```

| Parameter   | Required | Description                         |
| ----------- | -------- | ----------------------------------- |
| `--action`  | Yes      | `list`, `get`, `create`, `toggle`   |
| `--rule`    | No       | JSON rule definition (for `create`) |
| `--rule_id` | No       | Rule ID (for `get`, `toggle`)       |

---

## LLM Module

### chat_with_context

Send a chat message to TFO LLM with automatic telemetry context injection via ContextCollector.

```bash
python3 chat_with_context.py \
  --message "Analyze the memory spike pattern" \
  --context-type metrics \
  --context-id payments-api
```

| Parameter           | Required | Description                                     |
| ------------------- | -------- | ----------------------------------------------- |
| `--message`         | Yes      | Chat message (max 32,000 chars)                 |
| `--context_type`    | Yes      | One of 74 ContextType values                    |
| `--context_id`      | No       | Specific context (e.g., service name, alert ID) |
| `--conversation_id` | No       | Continue existing conversation                  |
| `--provider_id`     | No       | LLM provider ID (defaults to org default)       |
| `--time_from`       | No       | Context time range start                        |
| `--time_to`         | No       | Context time range end                          |

### stream_chat

Send a streaming chat message (SSE) to TFO LLM.

```bash
python3 stream_chat.py \
  --message "What caused the latency spike?" \
  --context-type logs \
  --context-id payments-api
```

Same parameters as `chat_with_context`. Returns Server-Sent Events stream.

### manage_conversation

Manage TFO LLM conversations.

```bash
python3 manage_conversation.py --action list
python3 manage_conversation.py --action get --id conv_abc123
```

| Parameter  | Required | Description                        |
| ---------- | -------- | ---------------------------------- |
| `--action` | Yes      | `list`, `get`, `archive`, `delete` |
| `--id`     | No       | Conversation ID                    |

### generate_insight

Generate AI insight via TFO LLM.

```bash
python3 generate_insight.py \
  --insight-type root-cause \
  --context-type metrics \
  --context-id payments-api \
  --time-from "2026-06-04T03:00:00Z"
```

| Parameter        | Required | Description                                                           |
| ---------------- | -------- | --------------------------------------------------------------------- |
| `--insight_type` | Yes      | `chronology`, `prediction`, `recommendation`, `root-cause`, `pattern` |
| `--context_type` | Yes      | One of 74 ContextType values                                          |
| `--context_id`   | No       | Specific context ID                                                   |
| `--provider_id`  | No       | LLM provider to use                                                   |
| `--time_from`    | No       | Start time (default: 24 hours ago)                                    |
| `--time_to`      | No       | End time (default: now)                                               |

### query_llm_usage

Query LLM usage analytics from ClickHouse.

```bash
python3 query_llm_usage.py --action summary
python3 query_llm_usage.py --action by-provider --from "2026-06-01T00:00:00Z"
```

| Parameter    | Required | Description                                                                 |
| ------------ | -------- | --------------------------------------------------------------------------- |
| `--action`   | Yes      | `summary`, `by-provider`, `by-model`, `by-context`, `top-users`, `interval` |
| `--from`     | No       | Start time (default: 7 days ago)                                            |
| `--to`       | No       | End time (default: now)                                                     |
| `--interval` | No       | Interval for trends: `5m`, `15m`, `6h`                                      |

### manage_provider

Manage TFO LLM providers (15 types).

```bash
python3 manage_provider.py --action list
python3 manage_provider.py --action create --name "My Claude" --provider-type anthropic --api-key "sk-..." --model-id "claude-sonnet-4-5"
```

| Parameter         | Required | Description                                                    |
| ----------------- | -------- | -------------------------------------------------------------- |
| `--action`        | Yes      | `list`, `get`, `create`, `validate`, `test-key`, `set-default` |
| `--id`            | No       | Provider ID                                                    |
| `--name`          | No       | Display name (for `create`)                                    |
| `--provider_type` | No       | Provider type (for `create`)                                   |
| `--api_key`       | No       | API key (for `create`)                                         |
| `--model_id`      | No       | Model ID (for `create`)                                        |
| `--base_url`      | No       | Custom base URL (for `ollama`, `custom`)                       |

---

## Remediation (Requires Approval)

### scale_deployment

Scale a Kubernetes deployment. **Requires human approval.**

```bash
python3 scale_deployment.py \
  --deployment payments-api \
  --namespace production \
  --replicas 3
```

| Parameter      | Required | Description          |
| -------------- | -------- | -------------------- |
| `--deployment` | Yes      | Deployment name      |
| `--namespace`  | Yes      | Kubernetes namespace |
| `--replicas`   | Yes      | Target replica count |

### restart_pod

Restart Kubernetes pods. **Requires human approval.**

```bash
python3 restart_pod.py \
  --deployment payments-api \
  --namespace production
```

| Parameter      | Required | Description                                 |
| -------------- | -------- | ------------------------------------------- |
| `--deployment` | Yes      | Deployment name                             |
| `--namespace`  | Yes      | Kubernetes namespace                        |
| `--pod`        | No       | Specific pod name (restarts all if omitted) |

### rollback_deploy

Rollback a Kubernetes deployment. **Requires human approval.**

```bash
python3 rollback_deploy.py \
  --deployment payments-api \
  --namespace production \
  --revision 2
```

| Parameter      | Required | Description                            |
| -------------- | -------- | -------------------------------------- |
| `--deployment` | Yes      | Deployment name                        |
| `--namespace`  | Yes      | Kubernetes namespace                   |
| `--revision`   | No       | Target revision (defaults to previous) |

### update_alert

Update a TelemetryFlow alert rule. **Requires human approval.**

```bash
python3 update_alert.py \
  --alert-id alert_abc123 \
  --action update-threshold \
  --value 500
```

| Parameter    | Required | Description                                                |
| ------------ | -------- | ---------------------------------------------------------- |
| `--alert_id` | Yes      | Alert rule ID                                              |
| `--action`   | Yes      | `update-threshold`, `enable`, `disable`, `update-severity` |
| `--value`    | No       | New threshold value                                        |
