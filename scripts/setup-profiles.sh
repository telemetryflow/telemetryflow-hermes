#!/bin/bash
set -euo pipefail

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "========================================"
echo " TelemetryFlow Hermes — Setup Profiles"
echo "========================================"
echo ""

command -v hermes >/dev/null 2>&1 || {
  echo "[FAIL] Hermes not installed. Run: make install"
  exit 1
}

PROFILES=("triage" "investigator" "reviewer" "remediator")

for profile in "${PROFILES[@]}"; do
  echo ""
  echo "--- Profile: $profile ---"

  if [ -d "$HERMES_HOME/profiles/$profile" ]; then
    echo "[SKIP] Profile '$profile' already exists"
    continue
  fi

  hermes profile create "$profile" --clone 2>/dev/null || {
    echo "[WARN] Could not create profile via hermes CLI. Creating manually..."
    mkdir -p "$HERMES_HOME/profiles/$profile"/{memories,skills}
  }

  if [ -d "$HERMES_HOME/profiles/$profile" ]; then
    if [ -f "$PROJECT_DIR/profiles/$profile/SOUL.md" ]; then
      cp "$PROJECT_DIR/profiles/$profile/SOUL.md" "$HERMES_HOME/profiles/$profile/SOUL.md"
      echo "[OK] SOUL.md installed"
    fi

    if [ -f "$PROJECT_DIR/profiles/$profile/config.yaml" ]; then
      cp "$PROJECT_DIR/profiles/$profile/config.yaml" "$HERMES_HOME/profiles/$profile/config.yaml"
      echo "[OK] config.yaml installed"
    fi

    if [ -f "$PROJECT_DIR/profiles/$profile/memories/MEMORY.md" ]; then
      cp "$PROJECT_DIR/profiles/$profile/memories/MEMORY.md" "$HERMES_HOME/profiles/$profile/memories/MEMORY.md"
      echo "[OK] MEMORY.md installed"
    fi

    if [ -f "$PROJECT_DIR/profiles/$profile/memories/USER.md" ]; then
      cp "$PROJECT_DIR/profiles/$profile/memories/USER.md" "$HERMES_HOME/profiles/$profile/memories/USER.md"
      echo "[OK] USER.md installed"
    fi
  fi

  echo "[OK] Profile '$profile' configured"
done

echo ""
echo "========================================"
echo " Profiles created!"
echo "========================================"
echo ""
echo "Verify with: hermes profile list"
