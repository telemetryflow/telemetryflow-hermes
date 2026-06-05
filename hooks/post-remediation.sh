#!/bin/bash
set -euo pipefail

ALERT_ID="${1:-}"
ACTION="${2:-}"
OUTCOME="${3:-unknown}"
APPROVED_BY="${4:-human}"
SERVICE="${5:-unknown}"
ROOT_CAUSE="${6:-unknown}"
START_TIME="${7:-unknown}"
SEVERITY="${8:-high}"

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
LOG_DIR="$HERMES_HOME/logs"
REPORT_DIR="$HERMES_HOME/reports"
mkdir -p "$LOG_DIR" "$REPORT_DIR"

TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
DATE_STAMP=$(date -u +%Y%m%d)
REPORT_FILE="$REPORT_DIR/RCA-${ALERT_ID:-manual}-$DATE_STAMP.md"
POSTMORTEM_FILE="$REPORT_DIR/POSTMORTEM-${ALERT_ID:-manual}-$DATE_STAMP.md"

echo "[$TIMESTAMP] REMEDIATION_COMPLETE alert=$ALERT_ID action=$ACTION outcome=$OUTCOME approved_by=$APPROVED_BY" >> "$LOG_DIR/remediations.log"

if [ "$OUTCOME" = "success" ] || [ "$OUTCOME" = "resolved" ]; then
    echo "[$TIMESTAMP] Generating RCA report for alert=$ALERT_ID service=$SERVICE"

    python3 "$HERMES_HOME/plugins/telemetryflow/tools/generate_rca_report.py" \
        --action all \
        --alert_id "$ALERT_ID" \
        --service "$SERVICE" \
        --root_cause "$ROOT_CAUSE" \
        --remediation "$ACTION" \
        --start_time "$START_TIME" \
        --end_time "$TIMESTAMP" \
        --severity "$SEVERITY" \
        > "$REPORT_FILE.json" 2>/dev/null || {
        echo "[$TIMESTAMP] WARN: RCA auto-generation failed. Use: make rca-report" >> "$LOG_DIR/remediations.log"
        exit 0
    }

    python3 -c "
import json, sys
data = json.load(open('$REPORT_FILE.json'))
report = data.get('rca_report', '')
if report:
    open('$REPORT_FILE', 'w').write(report)
    print(f'RCA report written to $REPORT_FILE')
jira = data.get('jira_ticket', {})
if jira:
    print(f'Jira: [{jira.get(\"project_key\", \"OPS\")}] {jira.get(\"summary\", \"\")}')
trello = data.get('trello_card', {})
if trello:
    print(f'Trello: {trello.get(\"name\", \"\")}')
" 2>/dev/null || true

    echo "[$TIMESTAMP] RCA report generated: $REPORT_FILE" >> "$LOG_DIR/remediations.log"
fi

echo ""
echo "Post-remediation verification should run in 30 seconds."
echo "RCA report: $REPORT_FILE"
echo "Generate postmortem: python3 plugins/telemetryflow/tools/generate_postmortem.py --alert_id $ALERT_ID --service $SERVICE"
