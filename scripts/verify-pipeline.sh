#!/bin/bash
set -euo pipefail

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

ERRORS=0

echo "========================================"
echo " TelemetryFlow Hermes — Pipeline Verify"
echo "========================================"
echo ""

command -v hermes >/dev/null 2>&1 || {
  echo "[FAIL] Hermes not installed"
  ERRORS=$((ERRORS + 1))
}
echo "[OK] Hermes CLI found"

echo ""
echo "--- Checking profiles ---"
PROFILES=("triage" "investigator" "reviewer" "remediator")
for profile in "${PROFILES[@]}"; do
  if [ -d "$HERMES_HOME/profiles/$profile" ]; then
    if [ -f "$HERMES_HOME/profiles/$profile/SOUL.md" ]; then
      echo "[OK] $profile: SOUL.md present"
    else
      echo "[FAIL] $profile: SOUL.md missing"
      ERRORS=$((ERRORS + 1))
    fi
    if [ -f "$HERMES_HOME/profiles/$profile/config.yaml" ]; then
      echo "[OK] $profile: config.yaml present"
    else
      echo "[FAIL] $profile: config.yaml missing"
      ERRORS=$((ERRORS + 1))
    fi
  else
    echo "[FAIL] $profile: directory not found"
    ERRORS=$((ERRORS + 1))
  fi
done

echo ""
echo "--- Checking skills ---"
SKILLS=(
  "observability/k8s-pod-debug"
  "observability/payments-api-oom-rca"
  "observability/clickhouse-query-patterns"
  "observability/alert-triage"
  "observability/remediation-gate"
  "observability/cross-signal-correlation"
)
for skill in "${SKILLS[@]}"; do
  if [ -f "$PROJECT_DIR/skills/$skill/SKILL.md" ]; then
    echo "[OK] $skill"
  else
    echo "[FAIL] $skill: SKILL.md missing"
    ERRORS=$((ERRORS + 1))
  fi
done

echo ""
echo "--- Checking plugin ---"
if [ -f "$PROJECT_DIR/plugins/telemetryflow/plugin.yaml" ]; then
  echo "[OK] plugin.yaml present"
  TOOLS=$(ls "$PROJECT_DIR/plugins/telemetryflow/tools/"*.py 2>/dev/null | wc -l | tr -d ' ')
  echo "[OK] $TOOLS tool scripts found"
else
  echo "[FAIL] plugin.yaml missing"
  ERRORS=$((ERRORS + 1))
fi

echo ""
echo "--- Checking environment ---"
if [ -f "$HERMES_HOME/.env" ]; then
  echo "[OK] ~/.hermes/.env present"
else
  echo "[WARN] ~/.hermes/.env not found — copy from .env.example"
fi

echo ""
echo "--- Checking API connectivity ---"
  TELEMETRYFLOW_URL="${TELEMETRYFLOW_API_URL:-http://localhost:3000/api/v2}"
  if curl -sf -o /dev/null --max-time 5 "${TELEMETRYFLOW_URL%%/api/v2*}/health" 2>/dev/null; then
    echo "[OK] TelemetryFlow API reachable"
  else
    echo "[WARN] TelemetryFlow API not reachable at ${TELEMETRYFLOW_URL%%/api/v2*}"
fi

echo ""
echo "========================================"
if [ "$ERRORS" -eq 0 ]; then
  echo " ALL CHECKS PASSED"
else
  echo " $ERRORS ISSUE(S) FOUND"
fi
echo "========================================"
