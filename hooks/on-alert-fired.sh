#!/bin/bash
# On-alert-fired hook
# Runs when a TelemetryFlow alert triggers the Triage agent
# Logs the alert and enriches context before triage classification

set -euo pipefail

ALERT_PAYLOAD="${1:-}"

LOG_DIR="${HERMES_HOME:-$HOME/.hermes}/logs"
mkdir -p "$LOG_DIR"

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ALERT_FIRED payload_size=${#ALERT_PAYLOAD}" >> "$LOG_DIR/alerts.log"

if [ -n "$ALERT_PAYLOAD" ]; then
  ALERT_ID=$(echo "$ALERT_PAYLOAD" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('alert_id','unknown'))" 2>/dev/null || echo "parse-error")
  RULE_NAME=$(echo "$ALERT_PAYLOAD" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('rule_name','unknown'))" 2>/dev/null || echo "parse-error")
  SEVERITY=$(echo "$ALERT_PAYLOAD" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('severity','unknown'))" 2>/dev/null || echo "parse-error")

  echo "  Alert ID: $ALERT_ID"
  echo "  Rule: $RULE_NAME"
  echo "  Severity: $SEVERITY"
  echo "  Triage classification starting..."
fi
