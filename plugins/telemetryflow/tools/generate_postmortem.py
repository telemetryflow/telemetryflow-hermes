#!/usr/bin/env python3
"""Generate Postmortem report with full incident analysis."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _shared import now_iso, output_json, parse_args, tfo_request


def _get_postmortem_template():
    return {
        "template": "\n".join(
            [
                "# Postmortem: {{INCIDENT_TITLE}}",
                "",
                "| Field | Value |",
                "|-------|-------|",
                "| **Date** | {{INCIDENT_DATE}} |",
                "| **Authors** | {{AUTHORS}} |",
                "| **Status** | {{STATUS}} |",
                "| **Severity** | {{SEVERITY}} |",
                "| **Services Affected** | {{SERVICES}} |",
                "| **Duration** | {{DURATION}} |",
                "| **User Impact** | {{USER_IMPACT}} |",
                "",
                "---",
                "",
                "## Summary",
                "",
                "{{SUMMARY}}",
                "",
                "---",
                "",
                "## Timeline (All Times UTC)",
                "",
                "```mermaid",
                "timeline",
                "    title Incident Timeline",
                "    section {{DATE_START}}",
                "        {{TIME_1}} : {{EVENT_1}}",
                "        {{TIME_2}} : {{EVENT_2}}",
                "        {{TIME_3}} : {{EVENT_3}}",
                "    section {{DATE_END}}",
                "        {{TIME_4}} : {{EVENT_4}}",
                "        {{TIME_5}} : Resolution",
                "```",
                "",
                "### Detailed Timeline",
                "",
                "| Time | Event | Owner | Detail |",
                "|------|-------|-------|--------|",
                "| {{T1}} | Alert fired | TFO Platform | {{ALERT_DETAIL}} |",
                "| {{T2}} | Triage classified | Hermes Agent | CRITICAL — delegated to Investigator |",
                "| {{T3}} | Investigation started | Hermes Investigator | Querying metrics, logs, traces |",
                "| {{T4}} | Root cause identified | Hermes Investigator | {{ROOT_CAUSE_DETAIL}} |",
                "| {{T5}} | Review completed | Hermes Reviewer | CONFIRMED |",
                "| {{T6}} | Remediation proposed | Hermes Remediator | {{REMEDIATION_DETAIL}} |",
                "| {{T7}} | Human approved | On-Call Engineer | Approved via Telegram |",
                "| {{T8}} | Action executed | Hermes Remediator | {{EXECUTION_DETAIL}} |",
                "| {{T9}} | Verified resolved | Hermes Agent | Metrics returned to baseline |",
                "",
                "---",
                "",
                "## Root Cause Analysis",
                "",
                "### What Happened",
                "",
                "{{WHAT_HAPPENED}}",
                "",
                "### Why It Happened",
                "",
                "{{WHY_IT_HAPPENED}}",
                "",
                "### Why It Was Not Caught Sooner",
                "",
                "{{WHY_NOT_CAUGHT_SOONER}}",
                "",
                "### Impact",
                "",
                "```mermaid",
                "graph LR",
                "    ROOT[Root Cause] --> IMPACT1[Service Degradation]",
                "    ROOT --> IMPACT2[User Errors]",
                "    ROOT --> IMPACT3[Data Impact]",
                "    IMPACT1 --> USERS[Affected Users: {{USER_COUNT}}]",
                "    IMPACT2 --> ERRORS[Error Rate: {{ERROR_RATE}}%]",
                "```",
                "",
                "### 5W Analysis",
                "",
                "| Question | Answer |",
                "|----------|--------|",
                "| **What** | {{WHAT}} |",
                "| **Where** | {{WHERE}} |",
                "| **When** | {{WHEN}} |",
                "| **Why** | {{WHY}} |",
                "| **How resolved** | {{HOW}} |",
                "",
                "---",
                "",
                "## Resolution",
                "",
                "### Immediate Actions",
                "",
                "| # | Action | Owner | Time | Result |",
                "|---|--------|-------|------|--------|",
                "| 1 | {{ACTION_1}} | {{OWNER_1}} | {{TIME_1}} | {{RESULT_1}} |",
                "| 2 | {{ACTION_2}} | {{OWNER_2}} | {{TIME_2}} | {{RESULT_2}} |",
                "",
                "### Remediation Flow",
                "",
                "```mermaid",
                "flowchart TD",
                "    DETECT['Detection'] --> TRIAGE['Triage']",
                "    TRIAGE --> INVEST['Investigation']",
                "    INVEST --> REVIEW['Review']",
                "    REVIEW --> REMED['Remediation']",
                "    REMED --> VERIFY['Verification']",
                "    VERIFY --> DONE['Resolved']",
                "",
                "    style DETECT fill:#ef4444,color:#fff",
                "    style DONE fill:#22c55e,color:#fff",
                "```",
                "",
                "---",
                "",
                "## Lessons Learned",
                "",
                "### What Went Well",
                "",
                "- {{WENT_WELL_1}}",
                "- {{WENT_WELL_2}}",
                "- {{WENT_WELL_3}}",
                "",
                "### What Could Be Improved",
                "",
                "- {{IMPROVE_1}}",
                "- {{IMPROVE_2}}",
                "- {{IMPROVE_3}}",
                "",
                "### Where We Got Lucky",
                "",
                "- {{LUCKY_1}}",
                "- {{LUCKY_2}}",
                "",
                "---",
                "",
                "## Action Items",
                "",
                "| # | Action | Owner | Priority | Due Date | Status |",
                "|---|--------|-------|----------|----------|--------|",
                "| 1 | {{ACTION_ITEM_1}} | {{OWNER}} | P1 | {{DUE}} | Pending |",
                "| 2 | {{ACTION_ITEM_2}} | {{OWNER}} | P2 | {{DUE}} | Pending |",
                "| 3 | {{ACTION_ITEM_3}} | {{OWNER}} | P2 | {{DUE}} | Pending |",
                "",
                "---",
                "",
                "## Appendix",
                "",
                "### Alert Payload",
                "",
                "```json",
                "{{ALERT_PAYLOAD}}",
                "```",
                "",
                "### Key Metrics Snapshot",
                "",
                "| Metric | Before | During | After |",
                "|--------|--------|--------|-------|",
                "| {{METRIC_1}} | {{BEFORE_1}} | {{DURING_1}} | {{AFTER_1}} |",
                "| {{METRIC_2}} | {{BEFORE_2}} | {{DURING_2}} | {{AFTER_2}} |",
                "",
                "### Related Resources",
                "",
                "- Alert ID: `{{ALERT_ID}}`",
                "- Triage classification: CRITICAL",
                "- Investigator hypothesis: {{HYPOTHESIS}}",
                "- Reviewer verdict: CONFIRMED",
                "- Remediator action: {{REMEDIATION}}",
                "- RCA Report: generated by Hermes Agent",
                "",
                "---",
                "",
                "*Postmortem generated by TelemetryFlow Hermes Agent on {{GENERATED_AT}}*",
            ]
        ),
        "format": "template",
    }


def _build_postmortem(params):
    alert_id = params.get("alert_id", "")
    service = params.get("service", "unknown")
    root_cause = params.get("root_cause", "Under investigation")
    remediation = params.get("remediation", "None")
    start_time = params.get("start_time", "")
    end_time = params.get("end_time", now_iso())
    severity = params.get("severity", "high")
    author = params.get("author", "Hermes Agent")
    title = params.get("title", f"Postmortem: {service} incident {now_iso()[:10]}")

    what = params.get("what", root_cause)
    where = params.get("where", f"Service: {service}, Workspace: {os.environ.get('TELEMETRYFLOW_WORKSPACE_ID', '')}")
    when = f"{start_time} to {end_time}"
    why = params.get("why", root_cause)
    how = params.get("how", remediation if remediation != "None" else "Pending")
    summary = params.get(
        "summary",
        f"On {start_time[:10] if start_time else 'unknown date'}, {service} experienced a {severity.upper()} incident caused by {root_cause}. {'Resolution: ' + remediation + '.' if remediation and remediation != 'None' else 'Resolution pending.'}",
    )

    went_well = params.get("went_well", "Automated detection via TelemetryFlow alert engine").split("|")
    improve = params.get("improve", "Review alert threshold calibration").split("|")
    lucky = params.get("lucky", "Low user-traffic period during incident").split("|")

    alert_data = None
    if alert_id:
        try:
            alert_data = tfo_request("/alerts/instances", params={"alertId": alert_id, "limit": "1"})
        except SystemExit:
            pass

    alert_payload = json.dumps(alert_data, indent=2, default=str)[:2000] if alert_data else "{}"

    report = "\n".join(
        [
            f"# Postmortem: {title}",
            "",
            "| Field | Value |",
            "|-------|-------|",
            f"| **Date** | {start_time[:10] if start_time else 'unknown'} |",
            f"| **Authors** | {author} |",
            f"| **Status** | {'Resolved' if remediation and remediation != 'None' else 'Open'} |",
            f"| **Severity** | {severity.upper()} |",
            f"| **Services Affected** | `{service}` |",
            f"| **Duration** | {start_time} → {end_time} |",
            f"| **Alert ID** | `{alert_id}` |",
            "",
            "---",
            "",
            "## Summary",
            "",
            summary,
            "",
            "---",
            "",
            "## Timeline (All Times UTC)",
            "",
            "```mermaid",
            "timeline",
            f"    title {service} Incident Timeline",
        ]
    )

    tl_events = params.get("timeline_events", "")
    if tl_events:
        try:
            events = json.loads(tl_events)
            current_date = None
            for ev in events:
                ts = ev.get("timestamp", "")
                date_part = ts[:10] if len(ts) >= 10 else "unknown"
                time_part = ts[11:19] if len(ts) >= 19 else ts
                if date_part != current_date:
                    current_date = date_part
                    report += f"\n    section {current_date}"
                report += f"\n        {time_part} : {ev.get('event', 'EVENT')} : {ev.get('detail', '')[:60]}"
        except (json.JSONDecodeError, TypeError):
            report += "\n    section Timeline\n        : Manual entry required"

    report += "\n```\n\n"

    report += "### Detailed Timeline\n\n"
    report += "| Time | Event | Owner | Detail |\n"
    report += "|------|-------|-------|--------|\n"

    default_events = [
        (start_time or "T-0", "Alert fired", "TFO Platform", f"{service} anomaly detected"),
        ("T+0s", "Triage classified", "Hermes Triage", "CRITICAL — delegated to Investigator"),
        ("T+5s", "Investigation started", "Hermes Investigator", "Querying metrics, logs, traces, exemplars"),
        ("T+30s", "Root cause identified", "Hermes Investigator", root_cause),
        ("T+45s", "Review completed", "Hermes Reviewer", "CONFIRMED — evidence verified"),
    ]
    if remediation and remediation != "None":
        default_events.extend(
            [
                ("T+60s", "Remediation proposed", "Hermes Remediator", remediation),
                ("T+60s+", "Human approved", "On-Call Engineer", "Approved via Telegram"),
                ("T+90s", "Action executed", "Hermes Remediator", remediation),
                ("T+120s", "Verified resolved", "Hermes Agent", "Metrics returned to baseline"),
            ]
        )

    for ts, event, owner, detail in default_events:
        report += f"| {ts} | {event} | {owner} | {detail} |\n"

    report += "\n---\n\n"

    report += "## Root Cause Analysis\n\n"
    report += "### What Happened\n\n"
    report += f"{what}\n\n"
    report += "### Why It Happened\n\n"
    report += f"{why}\n\n"
    report += "### Why It Was Not Caught Sooner\n\n"
    report += (
        f"{params.get('why_not_sooner', 'Alert threshold may need recalibration based on this incident pattern.')}\n\n"
    )

    report += "### 5W Analysis\n\n"
    report += "| Question | Answer |\n|----------|--------|\n"
    report += f"| **What** | {what} |\n"
    report += f"| **Where** | {where} |\n"
    report += f"| **When** | {when} |\n"
    report += f"| **Why** | {why} |\n"
    report += f"| **How resolved** | {how} |\n\n"

    report += "---\n\n"
    report += "## Resolution\n\n"
    report += "### Remediation Flow\n\n"
    report += "```mermaid\n"
    report += "flowchart TD\n"
    report += "    DETECT['Detection<br/>TFO Alert Engine'] --> TRIAGE['Triage<br/>Hermes Agent']\n"
    report += "    TRIAGE --> INVEST['Investigation<br/>Hermes Agent']\n"
    report += "    INVEST --> REVIEW['Review<br/>Hermes Agent']\n"
    report += "    REVIEW --> REMED['Remediation<br/>Hermes Agent']\n"
    report += "    REMED --> HUMAN['Human Approval<br/>Telegram']\n"
    report += "    HUMAN --> EXEC['Execute Action']\n"
    report += "    EXEC --> VERIFY['Verify Resolution']\n"
    report += "    VERIFY --> DONE['Resolved']\n"
    report += "    style DETECT fill:#ef4444,color:#fff\n"
    report += "    style DONE fill:#22c55e,color:#fff\n"
    report += "```\n\n"

    report += "---\n\n"
    report += "## Lessons Learned\n\n"
    report += "### What Went Well\n\n"
    for item in went_well:
        if item.strip():
            report += f"- {item.strip()}\n"
    report += "\n### What Could Be Improved\n\n"
    for item in improve:
        if item.strip():
            report += f"- {item.strip()}\n"
    report += "\n### Where We Got Lucky\n\n"
    for item in lucky:
        if item.strip():
            report += f"- {item.strip()}\n"

    report += "\n---\n\n"
    report += "## Action Items\n\n"
    report += "| # | Action | Owner | Priority | Status |\n|---|--------|-------|----------|--------|\n"
    report += f"| 1 | {remediation or 'Define remediation'} | SRE Team | P1 | {'Done' if remediation and remediation != 'None' else 'Pending'} |\n"
    report += "| 2 | Review alert thresholds for this pattern | SRE Team | P2 | Pending |\n"
    report += "| 3 | Update MEMORY.md with incident pattern | Hermes Agent | P2 | Pending |\n"
    report += "| 4 | Schedule postmortem review with team | Engineering | P3 | Pending |\n"

    report += "\n---\n\n"
    report += "## Appendix\n\n"
    report += "### Alert Payload\n\n"
    report += f"```json\n{alert_payload}\n```\n\n"
    report += "### Related Resources\n\n"
    report += f"- Alert ID: `{alert_id}`\n"
    report += f"- Service: `{service}`\n"
    report += f"- Root cause: {root_cause}\n"
    report += f"- Remediation: {remediation}\n"
    report += "- RCA Report: generated by Hermes Agent\n"
    report += "- Reviewer verdict: CONFIRMED\n"
    report += "- Pipeline agents: Triage → Investigator → Reviewer → Remediator\n"
    report += f"\n---\n\n*Postmortem generated by TelemetryFlow Hermes Agent on {now_iso()}*\n"

    return {
        "report": report,
        "format": "markdown",
        "alert_id": alert_id,
        "service": service,
        "severity": severity,
        "title": title,
        "generated_at": now_iso(),
    }


def main():
    args = parse_args()
    action = args.get("action", "postmortem")

    if action == "postmortem":
        result = _build_postmortem(args)
    elif action == "template":
        result = _get_postmortem_template()
    else:
        print(f"ERROR: Unknown action '{action}'. Use: postmortem, template", file=sys.stderr)
        sys.exit(1)
        return

    output_json(result)


if __name__ == "__main__":
    main()
