#!/bin/bash
# Post-remediation hook
# Runs after the Remediator agent executes an approved action
# Logs the outcome and triggers verification

set -euo pipefail

ALERT_ID="${1:-}"
ACTION="${2:-}"
OUTCOME="${3:-unknown}"
APPROVED_BY="${4:-human}"

LOG_DIR="${HERMES_HOME:-$HOME/.hermes}/logs"
mkdir -p "$LOG_DIR"

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] REMEDIATION_COMPLETE alert=$ALERT_ID action=$ACTION outcome=$OUTCOME approved_by=$APPROVED_BY" >> "$LOG_DIR/remediations.log"

echo "Post-remediation verification should run in 30 seconds."
echo "Check: metrics return to baseline, no new error spikes, pod status healthy."
