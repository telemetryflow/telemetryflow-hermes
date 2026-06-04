#!/bin/bash
# Pre-investigation hook
# Runs before the Investigator agent starts a new investigation
# Logs the investigation start and validates alert context

set -euo pipefail

ALERT_ID="${1:-}"
SERVICE="${2:-}"
SEVERITY="${3:-}"

LOG_DIR="${HERMES_HOME:-$HOME/.hermes}/logs"
mkdir -p "$LOG_DIR"

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] INVESTIGATION_START alert=$ALERT_ID service=$SERVICE severity=$SEVERITY" >> "$LOG_DIR/investigations.log"

if [ -z "$ALERT_ID" ]; then
  echo "[WARN] No alert_id provided — investigation may lack context"
fi
