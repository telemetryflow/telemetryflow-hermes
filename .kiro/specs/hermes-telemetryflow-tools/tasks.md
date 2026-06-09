# Implementation Plan: Hermes TelemetryFlow Plugin Tools

## Overview

This implementation plan covers the development of 40 TelemetryFlow plugin tools for Hermes, organized into 10 phases. The tools provide observability capabilities spanning core telemetry (metrics, logs, traces), infrastructure monitoring, platform management, AI/LLM integration, remediation actions, and root cause analysis. All tools use only Python standard library, communicate via the TelemetryFlow API and ClickHouse SQL queries, and follow a consistent pattern with shared utilities.

## Phase 1: Foundation (Shared Infrastructure)

- [ ] 1. Implement `_shared.py` Core Utilities
  - [ ] 1.1 Implement HTTP client functions
    - Implement `get_api_url()` — read `TELEMETRYFLOW_API_URL` env var with default
    - Implement `get_api_key()` — read `TELEMETRYFLOW_API_KEY` env var, exit on missing
    - Implement `_validate_url()` — SSRF protection, allow only http/https schemes
    - Implement `tfo_request()` — HTTP client with Bearer auth, JSON body, error handling, timeout=30s
    - Implement `clickhouse_query()` — route SQL through `POST /telemetry/query`
  - [ ] 1.2 Implement CLI and output utilities
    - Implement `parse_args()` — custom `--key value` CLI parser
    - Implement `output_json()` — formatted JSON output to stdout
    - Implement `now_iso()` — UTC ISO 8601 timestamp
  - [ ] 1.3 Define constants and type lists
    - Define `CONTEXT_TYPES` list (74 entries)
    - Define `INSIGHT_TYPES` list (5 entries)
    - Define `PROVIDER_TYPES` list (15 entries)
    - Define `ALLOWED_URL_SCHEMES` constant
  - [*] 1.4 Write unit tests for `_shared.py`
    - Test all utility functions with various inputs
    - Test SSRF protection in `_validate_url`
    - Test error handling in `tfo_request` and `get_api_key`
    - Test `parse_args` with various argument patterns
    - Test `output_json` formatting
    - _Validation: pytest tests/unit/test_shared.py_

- [ ] 2. Implement `plugin.yaml` Tool Registry
  - [ ] 2.1 Define plugin metadata and tool entries
    - Define plugin metadata (name, version, description, author)
    - Declare all 40 tool entries with name, description, command, args
  - [ ] 2.2 Configure security and environment
    - Set `requires_approval: true` on 4 remediation tools
    - Declare environment variable requirements
  - [*] 2.3 Validate `plugin.yaml`
    - Verify YAML syntax is valid
    - Verify tool count = 40
    - Verify `requires_approval` on exactly 4 tools
    - _Validation: YAML linter, tool count check_

- [ ] 3. Implement Test Infrastructure
  - [ ] 3.1 Implement pytest fixtures
    - Implement `mock_env` fixture (API URL, key, workspace, ClickHouse creds)
    - Implement `mock_urlopen` fixture (mock HTTP 200 response)
    - Implement `mock_urlopen_error` fixture (HTTPError 404)
    - Implement `mock_urlopen_conn_error` fixture (URLError)
    - Implement `capture_stdout` fixture (capsys wrapper)
    - Implement `mock_exit` fixture (patches sys.exit)
  - [ ] 3.2 Implement test helpers and sample data
    - Implement `tfo_response_factory` helper
    - Define sample data constants (SAMPLE_METRICS, SAMPLE_LOGS, etc.)
    - Implement `autouse` fixture for sys.path and module cleanup
  - [*] 3.3 Validate test infrastructure
    - Verify all fixtures load without errors
    - Verify sample data is valid
    - _Validation: pytest tests/unit/test_shared.py passes_

---

## Phase 2: Core Telemetry Tools (7 tools)

- [ ] 4. Implement Core Telemetry Tools
  - [ ] 4.1 Implement `query_metrics.py`
    - Implement RESOLUTION_MAP and DURATION_MAP dictionaries
    - Implement main() with --service (required), --metric, --duration, --resolution args
    - Implement per-metric time-series query (avg, p95, p99, min, max, count)
    - Implement metric summary query (all metrics for a service)
  - [*] 4.2 Write tests for `query_metrics.py`
    - Happy path with/without metric filter
    - Missing service error handling
    - ClickHouse query structure validation
    - _Validation: pytest tests/unit/test_query_metrics.py_

  - [ ] 4.3 Implement `search_logs.py`
    - Implement DURATION_MAP
    - Implement main() with --service, --severity, --duration, --search args
    - Build dynamic WHERE clause with severity, service, search filters
  - [*] 4.4 Write tests for `search_logs.py`
    - Various filter combinations
    - Severity ordering validation
    - _Validation: pytest tests/unit/test_search_logs.py_

  - [ ] 4.5 Implement `list_traces.py`
    - Implement main() with --service, --trace-id, --min-duration args
    - Implement trace waterfall query (by trace_id, ordered by timestamp)
    - Implement slow span query (by duration, ordered DESC)
  - [*] 4.6 Write tests for `list_traces.py`
    - Trace ID mode, service mode, duration filter
    - _Validation: pytest tests/unit/test_list_traces.py_

  - [ ] 4.7 Implement `get_exemplars.py`
    - Implement main() with --service, --metric, --trace-id args
    - Build dynamic WHERE clause
  - [*] 4.8 Write tests for `get_exemplars.py`
    - Various filter combinations
    - _Validation: pytest tests/unit/test_get_exemplars.py_

  - [ ] 4.9 Implement `query_correlations.py`
    - Implement main() with --service, --correlation-type, --duration args
    - Aggregate query on signal_correlations_1h
  - [*] 4.10 Write tests for `query_correlations.py`
    - Filter combinations, aggregation validation
    - _Validation: pytest tests/unit/test_query_correlations.py_

  - [ ] 4.11 Implement `query_tfql.py`
    - Implement metrics signal (names, labels, query)
    - Implement logs signal (severity-distribution, count-by-severity, search)
    - Implement traces signal (summaries, services, operations, search)
  - [*] 4.12 Write tests for `query_tfql.py`
    - All 3 signals × multiple actions
    - _Validation: pytest tests/unit/test_query_tfql.py_

  - [ ] 4.13 Implement `query_ai_intelligence.py`
    - Implement MODULES validation
    - Implement anomaly-detection (list, get, analyze)
    - Implement predictive-maintenance (list/predictions, get)
    - Implement cost-optimization (list/recommendations, get)
    - Implement corrective-maintenance (list/plans, get)
  - [*] 4.14 Write tests for `query_ai_intelligence.py`
    - All 4 modules × actions
    - _Validation: pytest tests/unit/test_query_ai_intelligence.py_

---

## Phase 3: Monitoring Tools (8 tools)

- [ ] 5. Implement Monitoring Tools
  - [ ] 5.1 Implement `check_k8s.py`
    - Implement resource dispatch: overview, clusters, nodes, namespaces, pods, deployments, pv
    - Add cluster/namespace filter params
  - [*] 5.2 Write tests for `check_k8s.py`
    - All 7 resources, filter params, unknown resource
    - _Validation: pytest tests/unit/test_check_k8s.py_

  - [ ] 5.3 Implement `check_vm.py`
    - Implement resources: list (with provider/status filters), get, metrics
  - [*] 5.4 Write tests for `check_vm.py`
    - All resources, missing vm-id, filter params
    - _Validation: pytest tests/unit/test_check_vm.py_

  - [ ] 5.5 Implement `check_agent.py`
    - Implement resources: list (with status/type/name/host filters), stats, get, health
  - [*] 5.6 Write tests for `check_agent.py`
    - All resources, missing agent-id
    - _Validation: pytest tests/unit/test_check_agent.py_

  - [ ] 5.7 Implement `check_infra.py`
    - Implement 5 resources mapping to `/monitoring/vm/{resource}`
  - [*] 5.8 Write tests for `check_infra.py`
    - All resources, invalid resource
    - _Validation: pytest tests/unit/test_check_infra.py_

  - [ ] 5.9 Implement `check_uptime.py`
    - Implement 10 resources: monitors, stats, checks, daily-stats, hourly-stats, ssl-summary, ssl-trend, status-pages, incidents, subscribers
    - Handle required IDs per resource
  - [*] 5.10 Write tests for `check_uptime.py`
    - All resources, missing IDs, optional IDs, status filter
    - _Validation: pytest tests/unit/test_check_uptime.py_

  - [ ] 5.11 Implement `check_service_map.py`
    - Implement 8 resources: map, services, get, dependencies, health, metrics, topology, trace-dependencies
  - [*] 5.12 Write tests for `check_service_map.py`
    - All resources, missing service-id, filters
    - _Validation: pytest tests/unit/test_check_service_map.py_

  - [ ] 5.13 Implement `check_network_map.py`
    - Implement 9 resources: topology, nodes, connections, traffic, flows, dns, k8s-flows, snmp-configs, paths
  - [*] 5.14 Write tests for `check_network_map.py`
    - All resources, missing node-id, filters
    - _Validation: pytest tests/unit/test_check_network_map.py_

  - [ ] 5.15 Implement `check_db_monitoring.py`
    - Define DB_TYPES list (16 types) and ENGINE_METRIC_TABLES mapping
    - Implement resources: inventory (TFO API), qan (TFO API), slow-queries (ClickHouse), engine-metrics (ClickHouse), wait-stats (mssql only), top-queries (5 engines)
  - [*] 5.16 Write tests for `check_db_monitoring.py`
    - All resources, missing db-type, invalid db-type, engine table selection
    - _Validation: pytest tests/unit/test_check_db_monitoring.py_

---

## Phase 4: Platform Tools (8 tools)

- [ ] 6. Implement Platform Tools
  - [ ] 6.1 Implement `manage_alerts.py`
    - Implement 7 resources: rules, rule-detail, instances, instance-detail, stats, channels, validate-tfql
  - [*] 6.2 Write tests for `manage_alerts.py`
    - All resources, filter params, validate-tfql POST
    - _Validation: pytest tests/unit/test_manage_alerts.py_

  - [ ] 6.3 Implement `manage_dashboards.py`
    - Implement 7 resources: list, get, export, shared, public, templates, shared-graphs
  - [*] 6.4 Write tests for `manage_dashboards.py`
    - All resources, missing dashboard-id, filters
    - _Validation: pytest tests/unit/test_manage_dashboards.py_

  - [ ] 6.5 Implement `manage_reports.py`
    - Implement 6 resources: definitions, definition-detail, executions, execution-detail, stats, generate
  - [*] 6.6 Write tests for `manage_reports.py`
    - All resources, missing IDs, generate POST
    - _Validation: pytest tests/unit/test_manage_reports.py_

  - [ ] 6.7 Implement `manage_data_masking.py`
    - Implement 4 actions: list, get, create, toggle
  - [*] 6.8 Write tests for `manage_data_masking.py`
    - All actions, missing policy-id, create validation
    - _Validation: pytest tests/unit/test_manage_data_masking.py_

  - [ ] 6.9 Implement `query_platform.py`
    - Implement RESOURCES dict (13 resource → endpoint mappings)
  - [*] 6.10 Write tests for `query_platform.py`
    - All resources, pagination, audit-logs duration
    - _Validation: pytest tests/unit/test_query_platform.py_

  - [ ] 6.11 Implement `query_account.py`
    - Implement 4 resources: profile, security, sessions, preferences
  - [*] 6.12 Write tests for `query_account.py`
    - All resources, invalid resource
    - _Validation: pytest tests/unit/test_query_account.py_

  - [ ] 6.13 Implement `query_audit.py`
    - Implement logs resource with 6 filter params
  - [*] 6.14 Write tests for `query_audit.py`
    - Filters, pagination
    - _Validation: pytest tests/unit/test_query_audit.py_

  - [ ] 6.15 Implement `query_subscription.py`
    - Implement 7 resources: current, plans, plan-detail, usage, usage-check, invoices, invoice-detail
  - [*] 6.16 Write tests for `query_subscription.py`
    - All resources, missing IDs, missing metric-type
    - _Validation: pytest tests/unit/test_query_subscription.py_

---

## Phase 5: Infrastructure Tools (4 tools)

- [ ] 7. Implement Infrastructure Tools
  - [ ] 7.1 Implement `manage_retention.py`
    - Implement 4 resources: policies, policy-detail, statistics, enforce
    - Implement dry-run support for enforce
  - [*] 7.2 Write tests for `manage_retention.py`
    - All resources, dry-run toggle
    - _Validation: pytest tests/unit/test_manage_retention.py_

  - [ ] 7.3 Implement `manage_tenancy.py`
    - Implement 7 resources: regions, region-detail, tenants, tenant-detail, organizations, org-detail, workspaces
  - [*] 7.4 Write tests for `manage_tenancy.py`
    - All resources, missing IDs, org-id for workspaces
    - _Validation: pytest tests/unit/test_manage_tenancy.py_

  - [ ] 7.5 Implement `manage_iam.py`
    - Implement 12 resources: users, user-detail, user-roles, user-permissions, roles, role-detail, role-permissions, permissions, groups, group-detail, group-users, audit-logs
  - [*] 7.6 Write tests for `manage_iam.py`
    - All resources, missing IDs, audit-logs pagination
    - _Validation: pytest tests/unit/test_manage_iam.py_

  - [ ] 7.7 Implement `manage_sso.py`
    - Implement 4 resources: providers, provider-detail, public-providers, connections
  - [*] 7.8 Write tests for `manage_sso.py`
    - All resources, missing IDs
    - _Validation: pytest tests/unit/test_manage_sso.py_

---

## Phase 6: AI & LLM Tools (6 tools)

- [ ] 8. Implement AI & LLM Tools
  - [ ] 8.1 Implement `chat_with_context.py`
    - Implement context_type validation against CONTEXT_TYPES
    - Implement time defaults (1h ago → now)
    - Implement POST to /llm/chat/message
  - [*] 8.2 Write tests for `chat_with_context.py`
    - Valid context types, invalid context type, missing message, time defaults
    - _Validation: pytest tests/unit/test_chat_with_context.py_

  - [ ] 8.3 Implement `stream_chat.py`
    - Implement SSE event loop with 120s timeout
    - Handle event types: start, chunk, end, error
    - Implement Accept: text/event-stream header
  - [*] 8.4 Write tests for `stream_chat.py`
    - SSE parsing, error events, HTTP error
    - _Validation: pytest tests/unit/test_stream_chat.py_

  - [ ] 8.5 Implement `manage_conversation.py`
    - Implement 4 actions: list, get, archive, delete
  - [*] 8.6 Write tests for `manage_conversation.py`
    - All actions, missing conversation-id, DELETE confirmation
    - _Validation: pytest tests/unit/test_manage_conversation.py_

  - [ ] 8.7 Implement `generate_insight.py`
    - Implement insight_type and context_type validation
    - Implement additional_context JSON parsing with fallback
  - [*] 8.8 Write tests for `generate_insight.py`
    - Valid/invalid types, JSON parsing
    - _Validation: pytest tests/unit/test_generate_insight.py_

  - [ ] 8.9 Implement `query_llm_usage.py`
    - Implement 6 actions: summary, by-provider, by-model, by-context, top-users, interval
    - Implement interval view mapping (5m, 15m, 6h)
  - [*] 8.10 Write tests for `query_llm_usage.py`
    - All actions, SQL validation, interval views
    - _Validation: pytest tests/unit/test_query_llm_usage.py_

  - [ ] 8.11 Implement `manage_provider.py`
    - Implement 7 actions: list, get, default, create, validate, test-key, set-default
    - Implement provider type validation against PROVIDER_TYPES
  - [*] 8.12 Write tests for `manage_provider.py`
    - All actions, create validation, invalid type, missing IDs/keys
    - _Validation: pytest tests/unit/test_manage_provider.py_

---

## Phase 7: Remediation Tools (4 tools, gated)

- [ ] 9. Implement Remediation Tools
  - [ ] 9.1 Implement `scale_deployment.py`
    - Implement PROPOSAL/Risk/Awaiting output pattern
    - Implement POST to /kubernetes/deployments/scale
    - Verify `requires_approval: true` in plugin.yaml
  - [*] 9.2 Write tests for `scale_deployment.py`
    - Happy path, missing name, proposal output validation
    - _Validation: pytest tests/unit/test_scale_deployment.py_

  - [ ] 9.3 Implement `restart_pod.py`
    - Implement dual mode: deployment restart vs. pod restart
    - Require at least one of --deployment or --pod
  - [*] 9.4 Write tests for `restart_pod.py`
    - Both modes, missing both args, proposal output
    - _Validation: pytest tests/unit/test_restart_pod.py_

  - [ ] 9.5 Implement `rollback_deploy.py`
    - Implement optional --revision support
  - [*] 9.6 Write tests for `rollback_deploy.py`
    - With/without revision, missing name
    - _Validation: pytest tests/unit/test_rollback_deploy.py_

  - [ ] 9.7 Implement `update_alert.py`
    - Implement dynamic data dict from optional fields
    - Type casting: threshold→float, enabled→bool
    - Require at least one update field
  - [*] 9.8 Write tests for `update_alert.py`
    - Individual fields, combined fields, missing rule-id, no fields
    - _Validation: pytest tests/unit/test_update_alert.py_

---

## Phase 8: RCA Tools (3 tools)

- [ ] 10. Implement RCA Tools
  - [ ] 10.1 Implement `generate_rca_report.py`
    - Implement data query functions (\_query_alert_instance, \_query_metrics_baseline, \_query_error_logs, \_query_trace_summary, \_query_audit_events)
    - Implement timeline builder (\_build_timeline)
    - Implement mermaid generators (\_generate_mermaid_timeline, \_generate_mermaid_flow)
    - Implement impact metrics table (\_generate_impact_metrics)
    - Implement report builder (\_build_rca_report) with all sections
    - Implement Jira ticket builder + submitter (\_build_jira_ticket, \_submit_jira)
    - Implement Trello card builder + submitter (\_build_trello_card, \_submit_trello, \_trello_add_labels, \_trello_add_checklist)
    - Implement action dispatch (rca, jira, trello, all)
  - [*] 10.2 Write tests for `generate_rca_report.py`
    - Report generation, Jira/Trello ticket building
    - Env var toggles, graceful degradation
    - _Validation: pytest tests/unit/test_generate_rca_report.py_

  - [ ] 10.3 Implement `generate_postmortem.py`
    - Implement blank template generator (\_get_postmortem_template)
    - Implement postmortem builder (\_build_postmortem) with all sections
    - Implement pipe-separated list parsing for lessons learned
  - [*] 10.4 Write tests for `generate_postmortem.py`
    - Postmortem action, template action, custom timeline events, lessons parsing
    - _Validation: pytest tests/unit/test_generate_postmortem.py_

  - [ ] 10.5 Implement `generate_rca_template.py`
    - Implement blank template builder with all sections (9 sections)
  - [*] 10.6 Write tests for `generate_rca_template.py`
    - Template generation, placeholder presence, mermaid diagrams
    - _Validation: pytest tests/unit/test_generate_rca_template.py_

---

## Phase 9: Security Setup

- [ ] 11. Implement ClickHouse Read-Only User
  - [ ] 11.1 Create SQL template and setup script
    - Create SQL template with CREATE USER, GRANT SELECT on 20 tables
    - Create shell script with env var reading, sed expansion, clickhouse-client execution
    - Add password validation, usage message
    - Verify script produces correct SQL with TELEMETRYFLOW_DB_NAME substitution
    - _Files: security/clickhouse-readonly.sql, security/setup-readonly-user.sh_

---

## Phase 10: Integration & Validation

- [*] 12. Full Test Suite Execution
  - [*] 12.1 Run all unit tests
    - Run `pytest tests/unit/ -v` — verify all 41 test files pass
    - Check test coverage for each tool file
  - [*] 12.2 Lint and type-check
    - Verify no tool imports external (non-stdlib) packages
    - Lint all Python files (ruff check)
    - Type-check if mypy configuration exists
    - _Validation: pytest tests/unit/ -v, ruff check_

- [*] 13. Plugin Registration Validation
  - [*] 13.1 Verify tool declarations
    - Verify plugin.yaml declares exactly 40 tools
    - Verify each tool name matches its filename
    - Verify requires_approval is set on exactly 4 tools
  - [*] 13.2 Verify environment and syntax
    - Verify all environment variables are declared
    - Verify YAML syntax is valid
    - _Validation: YAML linter, tool count = 40_

- [*] 14. Security Review
  - [*] 14.1 Validate URL and input handling
    - Verify all tfo_request calls pass through \_validate_url
    - Verify all external API calls (Jira, Trello) use \_validate_url
    - Verify no hardcoded API keys or secrets
  - [*] 14.2 Validate database permissions
    - Verify clickhouse-readonly.sql grants SELECT only on 20 specified tables
    - Run bandit security linter
    - _Validation: bandit security linter, SQL grants review_

---

## Checkpoint

- [ ] 15. Checkpoint - All Tools Complete
  - All 40 tools implemented and tested
  - All unit tests passing
  - Plugin registration validated
  - Security review complete
  - No external dependencies (stdlib only)

---

## Maintenance Tasks

### M.1 Add New Tool

When adding a tool to the plugin:

1. Create `plugins/telemetryflow/tools/<name>.py` following the standard pattern
2. Add test file `tests/unit/test_<name>.py`
3. Add tool entry in `plugin.yaml` (with `requires_approval` if needed)
4. Add module name to `conftest.py` cleanup list
5. If ClickHouse table is new, add GRANT SELECT in `security/clickhouse-readonly.sql`
6. Run full test suite

### M.2 Add New Resource to Existing Tool

When adding a new `--resource` or `--action`:

1. Add `elif` branch in tool's `main()` function
2. Update valid resource/action list in error message
3. Add test case(s) for new resource/action
4. Run tool-specific tests

### M.3 Add New Database Type

When adding support for a new database engine:

1. Add type to `DB_TYPES` list in `check_db_monitoring.py`
2. Add engine-to-table mapping in `ENGINE_METRIC_TABLES` dict
3. Add context type string to `CONTEXT_TYPES` in `_shared.py`
4. Add GRANT SELECT for new ClickHouse table in `security/clickhouse-readonly.sql`
5. Add test cases for new DB type
6. Update `plugin.yaml` description

### M.4 Add New LLM Provider Type

When adding a new LLM provider:

1. Add provider string to `PROVIDER_TYPES` in `_shared.py`
2. Verify no duplicates
3. Add test case for new provider
4. Update `plugin.yaml` description

### M.5 Update ClickHouse Tables

When adding a new ClickHouse table that tools query:

1. Add `GRANT SELECT ON ${TELEMETRYFLOW_DB_NAME}.<table> TO hermes_readonly;` in `security/clickhouse-readonly.sql`
2. Update the table count in security documentation
3. Re-run `security/setup-readonly-user.sh` to apply changes
