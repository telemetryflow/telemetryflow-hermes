# Implementation Plan: Hermes RCA Generation

## Overview

Hermes RCA Generation provides automated Root Cause Analysis report creation, postmortem generation, and integration with Jira/Trello for incident management. The system queries telemetry data from ClickHouse and the TelemetryFlow API, builds structured Markdown reports with Mermaid diagrams, and optionally submits tickets to external tracking systems. A post-remediation shell hook automates the end-to-end workflow from incident resolution through report generation and ticket creation.

## Tasks

- [ ] 1. Telemetry Query Layer
  - [ ] 1.1 Implement five telemetry query functions for ClickHouse and TelemetryFlow API
    - `_query_alert_instance(alert_id)` — Fetch alert details from TelemetryFlow API
    - `_query_metrics_baseline(service, duration_minutes=60)` — Query avg/P95/P99 from `metrics_1m`
    - `_query_error_logs(service, start_time, end_time, limit=50)` — Query ERROR/FATAL/CRITICAL logs from `otel_logs`
    - `_query_trace_summary(service, start_time, end_time)` — Query span stats from `otel_traces`
    - `_query_audit_events(start_time, end_time, limit=100)` — Query audit trail from `audit_logs`
    - Each function must use `_shared.clickhouse_query()` or `_shared.tfo_request()` and handle failures independently via try/except SystemExit
    - _Source: generate_rca_report.py:23-91_

- [ ] 2. Timeline Builder
  - [ ] 2.1 Implement \_build_timeline() that merges events from all telemetry sources
    - Collect alert events (type: `ALERT_FIRED`)
    - Collect error log events (type: `ERROR_LOG`, limit 10)
    - Collect slow span events (type: `SLOW_SPAN`, limit 5)
    - Collect audit events (type: `AUDIT_{action}`, limit 10)
    - Sort all events by timestamp ascending
    - Return list of `{timestamp, event, source, detail, severity}` dicts
    - _Source: generate_rca_report.py:94-146_

- [ ] 3. Mermaid Diagram Generators
  - [ ] 3.1 Implement timeline and flowchart Mermaid diagram generators
    - `_generate_mermaid_timeline(events)` — Timeline diagram grouped by date sections, 60-char detail truncation, "No Events" fallback
    - `_generate_mermaid_flow(service, root_cause, remediation_action)` — Incident response flowchart with agent pipeline nodes and dotted evidence link
    - _Source: generate_rca_report.py:149-188_

- [ ] 4. Impact Metrics Generator
  - [ ] 4.1 Implement \_generate_impact_metrics() with robust data handling
    - Handle None/dict/list response shapes from ClickHouse
    - Extract avg_val, P95, P99 values
    - Format to 4 decimal places for numeric values
    - Fall back to "No metrics data available" for missing data
    - _Source: generate_rca_report.py:191-212_

- [ ] 5. RCA Report Builder
  - [ ] 5.1 Implement \_build_rca_report(params) that assembles the full Markdown report
    - Parse parameters (alert_id, service, root_cause, remediation, start_time, end_time, severity, author, workspace_id, title)
    - Execute all telemetry queries (with independent failure handling)
    - Build timeline from merged events
    - Generate Mermaid diagrams
    - Assemble report sections in order: metadata → executive summary → impact → 5W → timeline → flow → root cause → contributing factors → action items → lessons learned → footer
    - Return structured result dict with report string and metadata
    - _Source: generate_rca_report.py:215-381_

- [ ] 6. Action Router and CLI Entry Point
  - [ ] 6.1 Implement main() with action routing and CLI arg parsing
    - Parse CLI args via `_shared.parse_args()`
    - Determine submission flags (JIRA_ENABLED, TRELLO_ENABLED)
    - Build RCA report, Jira ticket, Trello card
    - Route by action: `rca` | `jira` | `jira-submit` | `trello` | `trello-submit` | `all` | `submit`
    - Output JSON via `_shared.output_json()`
    - _Source: generate_rca_report.py:668-715_

- [ ] 7. Jira Ticket Builder
  - [ ] 7.1 Implement \_build_jira_ticket(rca_result, params) constructing a Jira issue payload
    - Summary: `[RCA] {title}`
    - Description in Jira wiki markup (h2/h3 headers, bold fields, numbered lists)
    - Labels: `rca`, `hermes-agent`, `severity-{level}`, `{service-hyphenated}`
    - Components: service name
    - Priority mapping: CRITICAL→1, HIGH→2, MEDIUM→3, LOW→4
    - Project key: configurable (default: OPS)
    - _Source: generate_rca_report.py:384-425_

- [ ] 8. Jira Submission Client
  - [ ] 8.1 Implement \_submit_jira(ticket) with auth and error handling
    - Read credentials from env vars (JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN)
    - Encode Basic auth header
    - POST to `{JIRA_URL}/rest/api/2/issue` with JSON payload
    - Handle: missing credentials, HTTP errors (with body), URL errors
    - Return `{submitted, issue_key, issue_id, issue_url, transition}` on success
    - _Source: generate_rca_report.py:465-522_

- [ ] 9. Trello Card Builder
  - [ ] 9.1 Implement \_build_trello_card(rca_result, params) constructing a Trello card payload
    - Name: `[RCA] {title}`
    - Description in Markdown (severity, root cause, resolution, checklist)
    - Labels: severity level, `rca`, `hermes`
    - Color mapping: CRITICAL→red, HIGH→orange, MEDIUM→yellow, LOW→green
    - _Source: generate_rca_report.py:428-462_

- [ ] 10. Trello Submission Client
  - [ ] 10.1 Implement \_submit_trello(card) with credential handling and enrichment
    - Read credentials from env vars (TRELLO_API_KEY, TRELLO_API_TOKEN, TRELLO_LIST_ID_INCIDENTS)
    - POST to `https://api.trello.com/1/cards` with credentials in body
    - Extract card_id and card_url from response
    - Call `_trello_add_labels()` for label enrichment
    - Call `_trello_add_checklist()` for checklist creation
    - Handle: missing credentials, HTTP errors, URL errors
    - Return `{submitted, card_id, card_url, board_id, list, labels_added, checklist_added}`
    - _Source: generate_rca_report.py:525-577_

- [ ] 11. Trello Label and Checklist Enrichment
  - [ ] 11.1 Implement label and checklist enrichment for Trello cards
    - `_trello_add_labels(card_id, api_key, api_token, label_names)` — Add color-coded labels per severity/type, non-fatal on individual failures
    - `_trello_add_checklist(card_id, api_key, api_token)` — Create "Incident Response Checklist" with 7 items, non-fatal on individual item failures
    - _Source: generate_rca_report.py:580-657_

- [ ] 12. Postmortem Report Builder
  - [ ] 12.1 Implement \_build_postmortem(params) that assembles the full postmortem report
    - Parse parameters including 5W overrides, summary, and lessons learned lists
    - Fetch alert data from TelemetryFlow API (optional)
    - Build Mermaid timeline from custom events or default agent pipeline events
    - Assemble report sections: header → summary → timeline → RCA → 5W → resolution flow → lessons → action items → appendix → footer
    - Handle pipe-delimited list inputs for lessons learned
    - Conditionally include remediation events based on remediation status
    - _Source: generate_postmortem.py:193-381_

- [ ] 13. Postmortem Template
  - [ ] 13.1 Implement \_get_postmortem_template() returning a blank template
    - All sections as `{{PLACEHOLDER}}` variables
    - Mermaid diagram templates with `{{TIME}}` and `{{EVENT}}` placeholders
    - Instructional guidance in blockquote format
    - Standard postmortem structure matching the filled report
    - _Source: generate_postmortem.py:12-190_

- [ ] 14. Postmortem CLI Entry Point
  - [ ] 14.1 Implement main() with action routing
    - Route actions: `postmortem` (generate) or `template` (blank template)
    - _Source: generate_postmortem.py:384-401_

- [ ] 15. Blank RCA Template
  - [ ] 15.1 Implement \_build_blank_template(params) generating a comprehensive RCA template
    - Accept optional pre-fill parameters (title, service, severity, author)
    - Generate comprehensive 10-section template
    - Use `{{VARIABLE_NAME}}` syntax for all unfilled fields
    - Include instructional blockquotes for each section
    - Include Mermaid diagram templates (blast radius, causal chain, timeline)
    - Include Jira/Trello ticket summary placeholders
    - Include approval sign-off table
    - Return `{report, format: "markdown", type: "blank_rca_template", generated_at}`
    - _Source: generate_rca_template.py:11-279_

- [ ] 16. Post-Remediation Shell Hook
  - [ ] 16.1 Implement post-remediation automation hook in shell
    - Parse 8 positional parameters (ALERT_ID, ACTION, OUTCOME, APPROVED_BY, SERVICE, ROOT_CAUSE, START_TIME, SEVERITY)
    - Set HERMES_HOME and create report/log directories
    - Log remediation completion event
    - Conditionally trigger RCA generation on success/resolved outcome
    - Invoke `generate_rca_report.py --action all` with all parameters
    - Extract Markdown report from JSON output
    - Log Jira/Trello ticket references
    - Handle failures with graceful degradation (exit 0)
    - _Source: hooks/post-remediation.sh_

- [*] 17. RCA Report Generation Tests
  - [*] 17.1 Write unit tests for generate_rca_report.py
    - Test `_build_rca_report()` with minimal params (no alert_id, unknown service)
    - Test `_build_rca_report()` with full params and all telemetry data
    - Test `_build_timeline()` with empty data, partial data, full data
    - Test `_generate_mermaid_timeline()` with empty events, single event, multi-date events
    - Test `_generate_mermaid_flow()` output format
    - Test `_generate_impact_metrics()` with None, dict, list, and numeric data
    - Test severity mapping in SEVERITY_MAP

- [*] 18. Postmortem Generation Tests
  - [*] 18.1 Write unit tests for generate_postmortem.py
    - Test `_build_postmortem()` with default parameters
    - Test `_build_postmortem()` with custom timeline events (JSON string)
    - Test `_build_postmortem()` with pipe-delimited lessons learned
    - Test `_get_postmortem_template()` placeholder coverage
    - Test conditional remediation events inclusion

- [*] 19. RCA Template Tests
  - [*] 19.1 Write unit tests for generate_rca_template.py
    - Test `_build_blank_template()` with no params (all placeholders)
    - Test `_build_blank_template()` with pre-fill params
    - Test that all `{{PLACEHOLDER}}` variables are present
    - Test Mermaid diagram template validity

- [*] 20. Jira Integration Tests
  - [*] 20.1 Write integration tests for Jira submission
    - Test `_build_jira_ticket()` payload structure and field mapping
    - Test `_submit_jira()` with missing credentials (graceful failure)
    - Test `_submit_jira()` with HTTP error responses
    - Test priority mapping (CRITICAL→1, HIGH→2, MEDIUM→3, LOW→4)

- [*] 21. Trello Integration Tests
  - [*] 21.1 Write integration tests for Trello submission
    - Test `_build_trello_card()` payload structure and label colors
    - Test `_submit_trello()` with missing credentials (graceful failure)
    - Test `_trello_add_labels()` color mapping
    - Test `_trello_add_checklist()` item creation
    - Test partial enrichment failures (labels fail, checklist succeeds)

- [*] 22. Post-Remediation Hook Tests
  - [*] 22.1 Write shell script tests for post-remediation.sh
    - Test execution with OUTCOME=success triggers RCA generation
    - Test execution with OUTCOME=failure skips RCA generation
    - Test graceful degradation when generate_rca_report.py fails
    - Test log file creation and format
    - Test report file creation (JSON + Markdown)

- [ ] 23. API Documentation
  - [ ] 23.1 Document CLI parameters, environment variables, and output formats for all three tools

- [ ] 24. Configuration Guide
  - [ ] 24.1 Create setup guide for Jira and Trello integration
    - Required environment variables
    - Feature flag configuration
    - Credential setup instructions
    - Testing connectivity

- [ ] 25. Error Message Audit
  - [ ] 25.1 Review all error messages for clarity and actionability
    - Ensure every error includes: what failed, why it likely failed, how to fix it

- [ ] 26. Checkpoint - RCA Generation Complete
