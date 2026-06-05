#!/usr/bin/env python3
"""Generate Root Cause Analysis (RCA) report and submit to Jira/Trello."""

import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(__file__))
from _shared import clickhouse_query, now_iso, output_json, parse_args, tfo_request

SEVERITY_MAP = {
    "critical": "P1 - Critical",
    "high": "P2 - High",
    "medium": "P3 - Medium",
    "low": "P4 - Low",
}


def _query_alert_instance(alert_id):
    return tfo_request("/alerts/instances", params={"alertId": alert_id, "limit": "1"})


def _query_metrics_baseline(service, duration_minutes=60):
    sql = (
        "SELECT "
        "  avg(toFloat64OrNull(metric_value)) as avg_val, "
        "  quantile(0.95)(toFloat64OrNull(metric_value)) as p95, "
        "  quantile(0.99)(toFloat64OrNull(metric_value)) as p99, "
        "  min(timestamp) as ts_min, "
        "  max(timestamp) as ts_max "
        "FROM metrics_1m "
        "WHERE service_name = '{service}' "
        "  AND timestamp >= now() - INTERVAL {dur} MINUTE "
        "LIMIT 1"
    ).format(service=service.replace("'", "''"), dur=duration_minutes)
    return clickhouse_query(sql)


def _query_error_logs(service, start_time, end_time, limit=50):
    sql = (
        "SELECT timestamp, severity_text, body, span_id, trace_id "
        "FROM otel_logs "
        "WHERE service_name = '{service}' "
        "  AND severity_text IN ('ERROR', 'FATAL', 'CRITICAL') "
        "  AND timestamp >= '{start}' "
        "  AND timestamp <= '{end}' "
        "ORDER BY timestamp ASC "
        "LIMIT {limit}"
    ).format(
        service=service.replace("'", "''"),
        start=start_time.replace("'", "''"),
        end=end_time.replace("'", "''"),
        limit=limit,
    )
    return clickhouse_query(sql)


def _query_trace_summary(service, start_time, end_time):
    sql = (
        "SELECT "
        "  count() as span_count, "
        "  avg(duration) as avg_duration_ms, "
        "  quantile(0.95)(duration) as p95_duration_ms, "
        "  countIf(status_code = 'ERROR') as error_spans "
        "FROM otel_traces "
        "WHERE service_name = '{service}' "
        "  AND timestamp >= '{start}' "
        "  AND timestamp <= '{end}' "
        "LIMIT 1"
    ).format(
        service=service.replace("'", "''"),
        start=start_time.replace("'", "''"),
        end=end_time.replace("'", "''"),
    )
    return clickhouse_query(sql)


def _query_audit_events(start_time, end_time, limit=100):
    sql = (
        "SELECT timestamp, action, resource, user_email, ip_address, details "
        "FROM audit_logs "
        "WHERE timestamp >= '{start}' "
        "  AND timestamp <= '{end}' "
        "ORDER BY timestamp DESC "
        "LIMIT {limit}"
    ).format(start=start_time.replace("'", "''"), end=end_time.replace("'", "''"), limit=limit)
    return clickhouse_query(sql)


def _build_timeline(alert_data, metrics_data, logs_data, traces_data, audit_data):
    events = []

    if alert_data:
        for item in alert_data if isinstance(alert_data, list) else [alert_data]:
            events.append(
                {
                    "timestamp": item.get("firedAt", item.get("createdAt", "")),
                    "event": "ALERT_FIRED",
                    "source": "telemetryflow",
                    "detail": item.get("alertName", item.get("name", "unknown alert")),
                    "severity": item.get("severity", "unknown"),
                }
            )

    if logs_data and isinstance(logs_data, list):
        for log in logs_data[:10]:
            events.append(
                {
                    "timestamp": log.get("timestamp", ""),
                    "event": "ERROR_LOG",
                    "source": log.get("service_name", "unknown"),
                    "detail": (log.get("body", "") or "")[:120],
                    "severity": log.get("severity_text", "ERROR"),
                }
            )

    if traces_data and isinstance(traces_data, list):
        for trace in traces_data[:5]:
            events.append(
                {
                    "timestamp": trace.get("timestamp", ""),
                    "event": "SLOW_SPAN",
                    "source": trace.get("service_name", "unknown"),
                    "detail": f"duration={trace.get('duration', '?')}ms op={trace.get('operation_name', '?')}",
                    "severity": "HIGH",
                }
            )

    if audit_data and isinstance(audit_data, list):
        for audit in audit_data[:10]:
            events.append(
                {
                    "timestamp": audit.get("timestamp", ""),
                    "event": f"AUDIT_{audit.get('action', 'UNKNOWN')}",
                    "source": audit.get("user_email", "system"),
                    "detail": f"{audit.get('resource', '')} from {audit.get('ip_address', '?')}",
                    "severity": "INFO",
                }
            )

    events.sort(key=lambda e: e.get("timestamp", ""))
    return events


def _generate_mermaid_timeline(events):
    if not events:
        return (
            "```mermaid\ntimeline\n    title Incident Timeline\n    section No Events\n        No data available\n```"
        )

    lines = ["```mermaid", "timeline", "    title Incident Timeline"]
    current_date = None
    for ev in events:
        ts = ev.get("timestamp", "")
        date_part = ts[:10] if len(ts) >= 10 else "unknown"
        time_part = ts[11:19] if len(ts) >= 19 else ts
        if date_part != current_date:
            current_date = date_part
            lines.append(f"    section {current_date}")
        event_type = ev.get("event", "EVENT")
        detail = ev.get("detail", "")[:60]
        lines.append(f"        {time_part} : {event_type} : {detail}")
    lines.append("```")
    return "\n".join(lines)


def _generate_mermaid_flow(service, root_cause, remediation_action):
    return "\n".join(
        [
            "```mermaid",
            "flowchart TD",
            f"    ALERT['Alert Fired<br/>{service}']",
            "    TRIAGE['Triage Agent<br/>Classified: CRITICAL']",
            "    INV['Investigator Agent<br/>Evidence Gathered']",
            "    REV['Reviewer Agent<br/>Verdict: CONFIRMED']",
            "    REM['Remediator Agent<br/>Action Proposed']",
            "    HUMAN['Human Approval<br/>Approved']",
            f"    EXEC['Action Executed<br/>{remediation_action}']",
            f"    ROOT['Root Cause<br/>{root_cause}']",
            "    ALERT --> TRIAGE --> INV --> REV --> REM --> HUMAN --> EXEC",
            "    INV -.->|evidence| ROOT",
            "```",
        ]
    )


def _generate_impact_metrics(metrics_data, service):
    if not metrics_data:
        return ["| Metric | Value |", "|--------|-------|", f"| {service} | No metrics data available |"]

    data = metrics_data
    if isinstance(data, dict):
        data = data.get("data", data)
    if isinstance(data, list):
        data = data[0] if data else {}
    if not isinstance(data, dict):
        return ["| Metric | Value |", "|--------|-------|", f"| {service} | No metrics data available |"]

    rows = []
    for key, label in [("avg_val", "Average"), ("p95", "P95"), ("p99", "P99")]:
        val = data.get(key, "N/A")
        if isinstance(val, (int, float)):
            rows.append(f"| {label} | {val:.4f} |")
        else:
            rows.append(f"| {label} | {val} |")

    header = "| Metric | Value |\n|--------|-------|"
    return [header] + rows


def _build_rca_report(params):
    alert_id = params.get("alert_id", "")
    service = params.get("service", "unknown")
    root_cause = params.get("root_cause", "Under investigation")
    remediation = params.get("remediation", "None")
    start_time = params.get("start_time", "")
    end_time = params.get("end_time", now_iso())
    severity = params.get("severity", "high")
    author = params.get("author", "Hermes Agent")
    workspace_id = params.get("workspace_id", os.environ.get("TELEMETRYFLOW_WORKSPACE_ID", ""))
    incident_title = params.get("title", f"RCA: {service} incident {now_iso()[:10]}")

    alert_data = None
    metrics_data = None
    logs_data = None
    traces_data = None
    audit_data = None

    if alert_id:
        try:
            alert_data = _query_alert_instance(alert_id)
        except SystemExit:
            pass

    if service and service != "unknown" and start_time:
        try:
            metrics_data = _query_metrics_baseline(service)
        except SystemExit:
            pass
        try:
            logs_data = _query_error_logs(service, start_time, end_time)
        except SystemExit:
            pass
        try:
            traces_data = _query_trace_summary(service, start_time, end_time)
        except SystemExit:
            pass

    if start_time:
        try:
            audit_data = _query_audit_events(start_time, end_time)
        except SystemExit:
            pass

    timeline = _build_timeline(alert_data, metrics_data, logs_data, traces_data, audit_data)
    mermaid_timeline = _generate_mermaid_timeline(timeline)
    mermaid_flow = _generate_mermaid_flow(service, root_cause, remediation)
    impact_table = "\n".join(_generate_impact_metrics(metrics_data, service))

    report = "\n".join(
        [
            "# Root Cause Analysis Report",
            "",
            f"**Incident**: {incident_title}",
            f"**Date Generated**: {now_iso()}",
            f"**Author**: {author}",
            f"**Severity**: {SEVERITY_MAP.get(severity.lower(), severity)}",
            f"**Service**: `{service}`",
            f"**Workspace**: `{workspace_id}`",
            f"**Status**: {'Resolved' if remediation and remediation != 'None' else 'Open'}",
            "",
            "---",
            "",
            "## Executive Summary",
            "",
            f"On **{start_time[:10] if start_time else 'unknown date'}**, the `{service}` service "
            f"experienced a **{severity.upper()}** incident. Root cause: **{root_cause}**. "
            f"{'Resolution: ' + remediation + '.' if remediation and remediation != 'None' else 'Resolution pending.'}",
            "",
            "---",
            "",
            "## Impact Assessment",
            "",
            "### Affected Service Metrics",
            "",
            impact_table,
            "",
            "### Blast Radius",
            "",
            f"- **Primary**: `{service}`",
            f"- **Duration**: {start_time} → {end_time}",
            f"- **User Impact**: {'Estimated from error rates in timeline below' if logs_data else 'Unknown — no log data available'}",
            "",
            "---",
            "",
            "## 5W Analysis",
            "",
            "### What Happened?",
            "",
            f"{root_cause}",
            "",
            "### Where Did It Happen?",
            "",
            f"- **Service**: `{service}`",
            f"- **Workspace**: `{workspace_id}`",
            "- **Infrastructure**: Kubernetes cluster (see service map for topology)",
            "",
            "### When Did It Happen?",
            "",
            f"- **Start**: `{start_time}`",
            f"- **End**: `{end_time}`",
            "- **Duration**: Calculated from timeline below",
            "",
            "### Why Did It Happen?",
            "",
            f"{root_cause}",
            "",
            "### How Was It Resolved?",
            "",
            f"{'Action taken: ' + remediation if remediation and remediation != 'None' else 'Not yet resolved — pending investigation or approval'}",
            "",
            "---",
            "",
            "## Incident Timeline",
            "",
            mermaid_timeline,
            "",
            "### Timeline Details",
            "",
            "| Timestamp | Event | Source | Detail | Severity |",
            "|-----------|-------|--------|--------|----------|",
        ]
    )

    for ev in timeline:
        ts = ev.get("timestamp", "")[:19]
        report += f"\n| {ts} | {ev.get('event', '')} | {ev.get('source', '')} | {ev.get('detail', '')[:80]} | {ev.get('severity', '')} |"

    report += "\n\n---\n\n"
    report += "## Incident Response Flow\n\n"
    report += mermaid_flow
    report += "\n\n---\n\n"

    report += "## Root Cause Details\n\n"
    report += f"{root_cause}\n\n"

    report += "## Contributing Factors\n\n"
    report += "| Factor | Contribution | Evidence |\n"
    report += "|--------|-------------|----------|\n"
    report += f"| Primary cause | {root_cause} | Alert data, metrics |\n"
    report += "| Environmental | Service load, resource constraints | Metrics baseline |\n"
    report += "| Process | Detection and response time | Timeline above |\n"

    report += "\n---\n\n"
    report += "## Action Items\n\n"
    report += "| # | Action | Owner | Priority | Status |\n"
    report += "|---|--------|-------|----------|--------|\n"
    report += f"| 1 | {remediation or 'Define remediation'} | SRE Team | {severity.upper()} | {'Done' if remediation and remediation != 'None' else 'Pending'} |\n"
    report += "| 2 | Update alert thresholds if needed | SRE Team | MEDIUM | Pending |\n"
    report += "| 3 | Update MEMORY.md with this pattern | Hermes Agent | LOW | Pending |\n"

    report += "\n---\n\n"
    report += "## Lessons Learned\n\n"
    report += "- **What went well**: Automated detection and agent pipeline response\n"
    report += "- **What could be improved**: Review response time and evidence completeness\n"
    report += "- **Where we got lucky**: [To be filled by human reviewer]\n\n"
    report += f"---\n\n*Generated by TelemetryFlow Hermes Agent on {now_iso()}*\n"

    return {
        "report": report,
        "format": "markdown",
        "alert_id": alert_id,
        "service": service,
        "severity": severity,
        "title": incident_title,
        "generated_at": now_iso(),
    }


def _build_jira_ticket(rca_result, params):
    summary = f"[RCA] {rca_result['title']}"
    severity = params.get("severity", "high").upper()

    description = "\n".join(
        [
            f"h2. Root Cause Analysis — {rca_result['service']}",
            "",
            f"*Severity*: {severity}",
            f"*Service*: {rca_result['service']}",
            f"*Generated*: {rca_result['generated_at']}",
            "",
            "h3. Root Cause",
            f"{params.get('root_cause', 'See full RCA report')}",
            "",
            "h3. Resolution",
            f"{params.get('remediation', 'Pending')}",
            "",
            "h3. Action Items",
            "# Execute approved remediation",
            "# Update alert thresholds",
            "# Update MEMORY.md with incident pattern",
            "# Schedule postmortem review",
            "",
            "---",
            f"Full RCA report available in Hermes logs for alert {rca_result.get('alert_id', 'N/A')}",
        ]
    )

    labels = ["rca", "hermes-agent", f"severity-{severity.lower()}", rca_result["service"].replace(" ", "-")]
    components = [rca_result["service"]]

    return {
        "project_key": params.get("project_key", "OPS"),
        "issue_type": params.get("issue_type", "Incident"),
        "summary": summary,
        "description": description,
        "labels": labels,
        "components": components,
        "priority": severity,
        "format": "jira",
    }


def _build_trello_card(rca_result, params):
    severity = params.get("severity", "high").upper()
    service = rca_result["service"]

    desc = "\n".join(
        [
            f"## {service} — {severity}",
            "",
            f"**Root Cause**: {params.get('root_cause', 'See full RCA')}",
            f"**Resolution**: {params.get('remediation', 'Pending')}",
            f"**Alert ID**: {rca_result.get('alert_id', 'N/A')}",
            "",
            "### Checklist",
            "- [ ] Remediation executed",
            "- [ ] Alert thresholds reviewed",
            "- [ ] MEMORY.md updated",
            "- [ ] Postmortem scheduled",
        ]
    )

    labels_map = {
        "CRITICAL": "red",
        "HIGH": "orange",
        "MEDIUM": "yellow",
        "LOW": "green",
    }

    return {
        "name": f"[RCA] {rca_result['title']}",
        "description": desc,
        "labels": [severity.lower(), "rca", "hermes"],
        "label_colors": [labels_map.get(severity, "blue")],
        "list": params.get("trello_list", "Incident Review"),
        "format": "trello",
    }


def _submit_jira(ticket):
    jira_url = os.environ.get("JIRA_URL", "").rstrip("/")
    jira_email = os.environ.get("JIRA_EMAIL", "")
    jira_token = os.environ.get("JIRA_API_TOKEN", "")

    if not all([jira_url, jira_email, jira_token]):
        return {
            "submitted": False,
            "error": "Jira credentials not configured. Set JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN.",
            "ticket": ticket,
        }

    url = f"{jira_url}/rest/api/2/issue"
    cred = base64.b64encode(f"{jira_email}:{jira_token}".encode()).decode()

    priority_map = {"CRITICAL": "1", "HIGH": "2", "MEDIUM": "3", "LOW": "4"}
    priority_id = priority_map.get(ticket.get("priority", "HIGH"), "3")

    payload = {
        "fields": {
            "project": {"key": ticket["project_key"]},
            "summary": ticket["summary"],
            "description": ticket["description"],
            "issuetype": {"name": ticket.get("issue_type", "Incident")},
            "priority": {"id": priority_id},
            "labels": ticket.get("labels", []),
        }
    }
    if ticket.get("components"):
        payload["fields"]["components"] = [{"name": c} for c in ticket["components"]]

    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Basic {cred}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return {
                "submitted": True,
                "issue_key": result.get("key", ""),
                "issue_id": result.get("id", ""),
                "issue_url": f"{jira_url}/browse/{result.get('key', '')}",
                "transition": "To Do",
            }
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        return {"submitted": False, "error": f"Jira HTTP {e.code}: {err}", "ticket": ticket}
    except urllib.error.URLError as e:
        return {"submitted": False, "error": f"Jira connection error: {e.reason}", "ticket": ticket}


def _submit_trello(card):
    api_key = os.environ.get("TRELLO_API_KEY", "")
    api_token = os.environ.get("TRELLO_API_TOKEN", "")
    board_id = os.environ.get("TRELLO_BOARD_ID", "")
    list_id = os.environ.get("TRELLO_LIST_ID_INCIDENTS", "")

    if not all([api_key, api_token, list_id]):
        return {
            "submitted": False,
            "error": "Trello credentials not configured. Set TRELLO_API_KEY, TRELLO_API_TOKEN, TRELLO_LIST_ID_INCIDENTS.",
            "card": card,
        }

    url = "https://api.trello.com/1/cards"
    params = {
        "key": api_key,
        "token": api_token,
        "idList": list_id,
        "name": card["name"],
        "desc": card["description"],
    }

    body = json.dumps(params).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            card_id = result.get("id", "")
            card_url = result.get("shortUrl", "")

            labels_result = _trello_add_labels(card_id, api_key, api_token, card.get("labels", []))
            checklist_result = _trello_add_checklist(card_id, api_key, api_token)

            return {
                "submitted": True,
                "card_id": card_id,
                "card_url": card_url,
                "board_id": board_id,
                "list": card.get("list", "Incident Review"),
                "labels_added": labels_result.get("added", 0),
                "checklist_added": checklist_result.get("added", 0),
            }
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        return {"submitted": False, "error": f"Trello HTTP {e.code}: {err}", "card": card}
    except urllib.error.URLError as e:
        return {"submitted": False, "error": f"Trello connection error: {e.reason}", "card": card}


def _trello_add_labels(card_id, api_key, api_token, label_names):
    if not label_names:
        return {"added": 0}

    color_map = {
        "critical": "red",
        "high": "orange",
        "medium": "yellow",
        "low": "green",
        "rca": "blue",
        "hermes": "purple",
    }

    added = 0
    for name in label_names:
        color = color_map.get(name.lower(), "blue")
        url = f"https://api.trello.com/1/cards/{card_id}/labels"
        body = json.dumps({"key": api_key, "token": api_token, "name": name, "color": color}).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
        try:
            urllib.request.urlopen(req, timeout=10)
            added += 1
        except (urllib.error.HTTPError, urllib.error.URLError):
            pass

    return {"added": added}


def _trello_add_checklist(card_id, api_key, api_token):
    url = f"https://api.trello.com/1/cards/{card_id}/checklists"
    items = [
        "Execute approved remediation",
        "Verify service restored",
        "Review alert thresholds",
        "Update MEMORY.md with incident pattern",
        "Schedule postmortem review",
        "Send stakeholder notification",
        "Update runbook if applicable",
    ]

    body = json.dumps(
        {
            "key": api_key,
            "token": api_token,
            "name": "Incident Response Checklist",
            "pos": "top",
        }
    ).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            cl = json.loads(resp.read().decode("utf-8"))
            checklist_id = cl.get("id", "")
            added = 0
            for item_text in items:
                item_url = f"https://api.trello.com/1/checklists/{checklist_id}/checkItems"
                item_body = json.dumps(
                    {
                        "key": api_key,
                        "token": api_token,
                        "name": item_text,
                        "checked": False,
                    }
                ).encode("utf-8")
                item_req = urllib.request.Request(
                    item_url, data=item_body, headers={"Content-Type": "application/json"}, method="POST"
                )
                try:
                    urllib.request.urlopen(item_req, timeout=10)
                    added += 1
                except (urllib.error.HTTPError, urllib.error.URLError):
                    pass
            return {"added": added}
    except (urllib.error.HTTPError, urllib.error.URLError):
        return {"added": 0}


def _should_submit_jira():
    return os.environ.get("JIRA_ENABLED", "false").lower() in ("true", "1", "yes")


def _should_submit_trello():
    return os.environ.get("TRELLO_ENABLED", "false").lower() in ("true", "1", "yes")


def main():
    args = parse_args()
    action = args.get("action", "rca")
    submit_flag = args.get("submit", "false").lower() in ("true", "1", "yes")
    do_jira = submit_flag and _should_submit_jira()
    do_trello = submit_flag and _should_submit_trello()

    rca = _build_rca_report(args)
    jira_ticket = _build_jira_ticket(rca, args)
    trello_card = _build_trello_card(rca, args)

    result = {
        "rca_report": rca["report"],
        "jira_ticket": jira_ticket,
        "trello_card": trello_card,
        "format": "rca",
        "submit_requested": submit_flag,
        "jira_enabled": _should_submit_jira(),
        "trello_enabled": _should_submit_trello(),
    }

    if action in ("jira", "jira-submit"):
        result["format"] = "jira"
        if do_jira or action == "jira-submit":
            result["jira_submission"] = _submit_jira(jira_ticket)
    elif action in ("trello", "trello-submit"):
        result["format"] = "trello"
        if do_trello or action == "trello-submit":
            result["trello_submission"] = _submit_trello(trello_card)
    elif action in ("all", "submit"):
        result["format"] = "all"
        if do_jira or action == "submit":
            result["jira_submission"] = _submit_jira(jira_ticket)
        if do_trello or action == "submit":
            result["trello_submission"] = _submit_trello(trello_card)
    elif action != "rca":
        print(
            f"ERROR: Unknown action '{action}'. Use: rca, jira, trello, all",
            file=sys.stderr,
        )
        sys.exit(1)
        return

    output_json(result)


if __name__ == "__main__":
    main()
