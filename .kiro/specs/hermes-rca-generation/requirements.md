# Hermes RCA Generation — Requirements

## Overview

Hermes must generate comprehensive Root Cause Analysis (RCA) reports, postmortem documents, and blank RCA templates from incident telemetry data. The system must produce structured Markdown reports with 5W analysis, Mermaid diagrams, impact metrics, and submit tracking tickets to Jira and/or Trello.

---

## REQ-1: RCA Report Generation

**Priority**: P1
**Source**: `plugins/telemetryflow/tools/generate_rca_report.py`

### REQ-1.1: 5W Analysis

The RCA report MUST include a complete 5W analysis section covering:

- **What happened**: Root cause description derived from incident parameters and evidence
- **Where it happened**: Affected service name, workspace ID, infrastructure context (Kubernetes cluster reference)
- **When it happened**: Incident start/end timestamps (ISO 8601), duration calculated from timeline
- **Why it happened**: Technical root cause explanation with evidence from telemetry queries
- **How it was resolved**: Remediation action taken, or "pending" status if unresolved

Each 5W dimension MUST be a distinct subsection under the `## 5W Analysis` heading.

### REQ-1.2: Incident Timeline

The report MUST include an incident timeline constructed from multiple telemetry sources:

- Alert events from TelemetryFlow API (`/alerts/instances`)
- Error logs from ClickHouse (`otel_logs` table, severity ERROR/FATAL/CRITICAL)
- Slow trace spans from ClickHouse (`otel_traces` table)
- Audit events from ClickHouse (`audit_logs` table)

Timeline events MUST be sorted chronologically and include: timestamp, event type, source, detail, severity.

### REQ-1.3: Mermaid Timeline Diagram

The report MUST include a Mermaid `timeline` diagram that:

- Groups events by date (`section YYYY-MM-DD`)
- Displays time and event description per entry
- Falls back to "No data available" when no events exist
- Truncates detail text to 60 characters for readability

### REQ-1.4: Mermaid Flow Diagram

The report MUST include a Mermaid `flowchart TD` diagram showing the incident response flow:

```
Alert Fired → Triage Agent → Investigator Agent → Reviewer Agent → Remediator Agent → Human Approval → Action Executed
```

With a dotted line from Investigator to Root Cause.

### REQ-1.5: Impact Assessment

The report MUST include an impact assessment section with:

- **Affected Service Metrics table**: Average, P95, P99 values from `metrics_1m` ClickHouse table
- **Blast Radius**: Primary service, incident duration window, user impact estimation based on error log availability

### REQ-1.6: Root Cause Details

The report MUST include:

- Root cause narrative section
- Contributing factors table (primary cause, environmental factors, process factors) with evidence references

### REQ-1.7: Action Items

The report MUST include an action items table with columns: #, Action, Owner, Priority, Status.

Default action items:

1. Remediation action (or "Define remediation") — SRE Team — incident severity — Done/Pending
2. Update alert thresholds if needed — SRE Team — MEDIUM — Pending
3. Update MEMORY.md with this pattern — Hermes Agent — LOW — Pending

### REQ-1.8: Lessons Learned

The report MUST include a lessons learned section with:

- What went well
- What could be improved
- Where we got lucky (placeholder for human reviewer)

### REQ-1.9: Report Metadata

Every RCA report MUST include header metadata:

- Incident title, date generated (ISO 8601), author, severity (mapped to P1-P4), service name, workspace ID, status (Resolved/Open)

Severity mapping:
| Input | Mapped |
|-------|--------|
| critical | P1 - Critical |
| high | P2 - High |
| medium | P3 - Medium |
| low | P4 - Low |

---

## REQ-2: Postmortem Report Generation

**Priority**: P1
**Source**: `plugins/telemetryflow/tools/generate_postmortem.py`

### REQ-2.1: Postmortem Document Structure

The postmortem MUST include all of the following sections:

1. **Header table**: Date, Authors, Status, Severity, Services Affected, Duration, Alert ID
2. **Summary**: Narrative incident summary
3. **Timeline (All Times UTC)**: Mermaid timeline diagram + detailed event table (Time, Event, Owner, Detail)
4. **Root Cause Analysis**: What happened, Why it happened, Why not caught sooner
5. **5W Analysis**: Table with What, Where, When, Why, How resolved
6. **Resolution**: Remediation flow Mermaid diagram (Detection → Triage → Investigation → Review → Remediation → Human Approval → Execute → Verify → Resolved)
7. **Lessons Learned**: What went well, What could be improved, Where we got lucky
8. **Action Items**: Table with #, Action, Owner, Priority, Status
9. **Appendix**: Alert payload JSON, related resources

### REQ-2.2: Timeline Event Sources

Postmortem timeline MUST support:

- Default agent pipeline events (Alert fired → Triage → Investigation → Root cause → Review → Remediation → Human approval → Execution → Verified)
- Custom timeline events via `timeline_events` JSON parameter
- Conditional remediation events (only shown when remediation is provided and not "None")

### REQ-2.3: Parameterized Content

The postmortem MUST accept these override parameters:

- `went_well`: Pipe-delimited string of positive observations
- `improve`: Pipe-delimited string of improvement areas
- `lucky`: Pipe-delimited string of lucky factors
- `why_not_sooner`: Explanation of why detection was delayed

### REQ-2.4: Blank Template Mode

The postmortem tool MUST support a `template` action that returns a blank template with `{{PLACEHOLDER}}` variables for manual filling.

---

## REQ-3: RCA Template Generation

**Priority**: P2
**Source**: `plugins/telemetryflow/tools/generate_rca_template.py`

### REQ-3.1: Blank RCA Template

The system MUST generate a blank RCA template document with the following sections:

1. **Document Control**: Title, incident date, report date, author, reviewers, severity, service, workspace ID, alert ID, status
2. **Executive Summary**: Instructional placeholder for 3-5 sentence non-technical summary
3. **Impact Assessment**: User impact table, service impact before/during/after comparison, blast radius Mermaid diagram
4. **5W Analysis**: Each W as a section with instructional guidance and structured tables
5. **Timeline**: Mermaid timeline diagram with detection/investigation/verification/resolution sections, detailed event log table
6. **Root Cause Deep Dive**: Contributing factors table, why defenses didn't catch it, causal chain Mermaid flowchart
7. **Lessons Learned**: What went well / What could be improved / Where we got lucky with checkboxes
8. **Action Items**: Table with Jira/Trello ticket reference column
9. **Jira/Trello Ticket Summary**: Pre-formatted ticket fields for both platforms
10. **Approval**: Incident Commander, Technical Lead, Engineering Manager sign-off table

### REQ-3.2: Template Parameterization

The template MUST accept optional parameters for pre-filling: `title`, `service`, `severity`, `author`.

All unfilled fields MUST use `{{VARIABLE_NAME}}` placeholder syntax.

---

## REQ-4: Mermaid Diagram Generation

**Priority**: P1
**Spans**: REQ-1, REQ-2, REQ-3

### REQ-4.1: Timeline Diagrams

All Mermaid timeline diagrams MUST:

- Use ````mermaid\ntimeline\n    title <title>` header format
- Group events by date using `section YYYY-MM-DD`
- Format entries as `HH:MM:SS : EVENT_TYPE : detail_text`
- Truncate detail text to 60 characters maximum

### REQ-4.2: Flow Diagrams

All Mermaid flow diagrams MUST:

- Use `flowchart TD` direction
- Include agent pipeline nodes: Alert → Triage → Investigator → Reviewer → Remediator → Human → Execute
- Show dotted evidence link from Investigator to Root Cause
- Use node syntax with labels: `NODE_ID['Label<br/>Detail']`

### REQ-4.3: Impact Diagrams

Blast radius and causal chain diagrams MUST:

- Use color-coded styling (`fill:#ef4444` for root cause/red, `fill:#22c55e` for healthy/green, etc.)
- Show propagation from root cause through primary service to downstream services
- Support custom downstream service names

---

## REQ-5: Jira Integration

**Priority**: P1
**Source**: `generate_rca_report.py` — `_submit_jira()`

### REQ-5.1: Ticket Creation

When Jira submission is enabled (`JIRA_ENABLED=true`), the system MUST create a Jira issue via REST API (`POST /rest/api/2/issue`) with:

- **Summary**: `[RCA] {incident_title}`
- **Description**: Jira wiki markup with Root Cause, Resolution, and Action Items sections
- **Issue Type**: "Incident" (configurable via `issue_type` parameter)
- **Priority**: Mapped from severity (CRITICAL→1, HIGH→2, MEDIUM→3, LOW→4)
- **Labels**: `rca`, `hermes-agent`, `severity-{level}`, `{service-name}`
- **Components**: Service name
- **Project Key**: Configurable via `project_key` parameter (default: "OPS")

### REQ-5.2: Authentication

Jira integration MUST use Basic authentication:

- `JIRA_URL`: Base Jira instance URL
- `JIRA_EMAIL`: User email
- `JIRA_API_TOKEN`: API token
- Credentials encoded as Base64 in `Authorization: Basic {cred}` header

### REQ-5.3: Error Handling

Jira submission MUST handle:

- Missing credentials: Return `submitted: false` with descriptive error message
- HTTP errors: Return status code and response body
- Connection errors: Return `URLError` reason
- Timeout: 30-second request timeout

### REQ-5.4: Response

Successful submission MUST return: `issue_key`, `issue_id`, `issue_url` (`{JIRA_URL}/browse/{key}`), `transition: "To Do"`.

---

## REQ-6: Trello Integration

**Priority**: P1
**Source**: `generate_rca_report.py` — `_submit_trello()`

### REQ-6.1: Card Creation

When Trello submission is enabled (`TRELLO_ENABLED=true`), the system MUST create a Trello card via REST API (`POST https://api.trello.com/1/cards`) with:

- **Name**: `[RCA] {incident_title}`
- **Description**: Markdown with severity, root cause, resolution, alert ID, and checklist
- **List**: Target list ID from `TRELLO_LIST_ID_INCIDENTS`

### REQ-6.2: Card Enrichment

After card creation, the system MUST:

1. **Add labels** (`POST /1/cards/{id}/labels`): Severity label (color-mapped), `rca` (blue), `hermes` (purple)
2. **Add checklist** (`POST /1/cards/{id}/checklists`): "Incident Response Checklist" with items:
   - Execute approved remediation
   - Verify service restored
   - Review alert thresholds
   - Update MEMORY.md with incident pattern
   - Schedule postmortem review
   - Send stakeholder notification
   - Update runbook if applicable

### REQ-6.3: Authentication

Trello integration MUST use query parameter authentication:

- `TRELLO_API_KEY`: API key
- `TRELLO_API_TOKEN`: API token
- `TRELLO_BOARD_ID`: Board ID (reference only)
- `TRELLO_LIST_ID_INCIDENTS`: Target list ID for card creation

### REQ-6.4: Error Handling

Trello submission MUST handle:

- Missing credentials: Return `submitted: false` with descriptive error message
- HTTP errors: Return status code and response body
- Connection errors: Return `URLError` reason
- Label/checklist addition failures: Non-fatal, continue without failing card creation
- Timeout: 30-second main request, 10-second label/checklist requests

### REQ-6.5: Response

Successful submission MUST return: `card_id`, `card_url`, `board_id`, `list`, `labels_added` (count), `checklist_added` (count).

---

## REQ-7: Report Formatting

**Priority**: P1

### REQ-7.1: Markdown Output

All reports MUST be valid Markdown with:

- ATX headings (`#`, `##`, `###`)
- Tables with pipe syntax and alignment row
- Code blocks for Mermaid diagrams (triple backtick + `mermaid`)
- Bold text for emphasis (`**text**`)
- Inline code for identifiers (`` `backtick` ``)
- Horizontal rules (`---`) between major sections

### REQ-7.2: JSON Output Wrapper

Each tool MUST output a JSON envelope via `output_json()` containing:

- `report`: Full Markdown report string
- `format`: Report format identifier (`markdown`, `jira`, `trello`, `rca`, `all`)
- `alert_id`: Source alert identifier
- `service`: Affected service name
- `severity`: Incident severity
- `title`: Report title
- `generated_at`: ISO 8601 generation timestamp

### REQ-7.3: Footers

Every report MUST end with a timestamped generation footer:

```
*Generated by TelemetryFlow Hermes Agent on {ISO8601_TIMESTAMP}*
```

---

## REQ-8: Automated RCA Triggering

**Priority**: P1
**Source**: `hooks/post-remediation.sh`

### REQ-8.1: Post-Remediation Hook

The `hooks/post-remediation.sh` script MUST automatically trigger RCA generation after successful remediation.

### REQ-8.2: Hook Parameters

The hook MUST accept positional parameters:

1. `ALERT_ID` — Alert identifier
2. `ACTION` — Remediation action taken
3. `OUTCOME` — Result status (`success` or `resolved` triggers RCA)
4. `APPROVED_BY` — Approver identity (default: `human`)
5. `SERVICE` — Affected service name
6. `ROOT_CAUSE` — Root cause description
7. `START_TIME` — Incident start timestamp
8. `SEVERITY` — Incident severity

### REQ-8.3: Conditional Generation

RCA generation MUST only occur when `OUTCOME` is `success` or `resolved`. Other outcomes MUST skip report generation gracefully.

### REQ-8.4: Output Files

The hook MUST produce:

- `$HERMES_HOME/reports/RCA-{ALERT_ID}-{DATE}.json` — Raw JSON output from the RCA tool
- `$HERMES_HOME/reports/RCA-{ALERT_ID}-{DATE}.md` — Extracted Markdown report
- `$HERMES_HOME/logs/remediations.log` — Timestamped log entries for all hook actions

### REQ-8.5: Graceful Degradation

If RCA auto-generation fails, the hook MUST:

- Log a warning with manual fallback instructions
- Exit with code 0 (non-blocking)
- NOT prevent the remediation from completing

### REQ-8.6: Action Routing

The hook MUST invoke `generate_rca_report.py` with `--action all` to generate the RCA report, Jira ticket, and Trello card in a single invocation.

---

## Non-Functional Requirements

### NFR-1: Security

- All URLs MUST be validated against allowed schemes (`http`, `https`) via `_validate_url()`
- API keys and tokens MUST be read from environment variables only, never hardcoded
- Jira credentials MUST use Base64-encoded Basic auth
- No secrets in log output

### NFR-2: Reliability

- Each telemetry query (metrics, logs, traces, audit) MUST fail independently — one query failure MUST NOT prevent report generation
- External service failures (Jira, Trello) MUST NOT prevent local report generation
- Report generation MUST succeed even with zero telemetry data (graceful degradation with placeholder content)

### NFR-3: Performance

- ClickHouse queries SHOULD use appropriate `LIMIT` clauses (metrics: 1, logs: 50, traces: 5, audit: 100)
- Timeline events SHOULD be limited to prevent oversized reports (logs: 10, traces: 5, audit: 10)
- External API calls MUST have timeouts (30s for Jira/Trello main calls, 10s for Trello label/checklist)

### NFR-4: Extensibility

- Tools MUST use `_shared.py` utilities for common operations (HTTP, CLI parsing, timestamps)
- Report sections SHOULD be composed from independent builder functions
- New telemetry sources SHOULD be addable without modifying the report template structure
