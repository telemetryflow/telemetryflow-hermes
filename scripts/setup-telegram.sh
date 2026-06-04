#!/bin/bash
set -euo pipefail

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"

echo "========================================"
echo " TelemetryFlow Hermes — Telegram Setup"
echo "========================================"
echo ""
echo "Each agent profile needs its own Telegram bot."
echo "Create 4 bots with @BotFather, then configure each profile."
echo ""

PROFILES=("triage" "investigator" "reviewer" "remediator")

for profile in "${PROFILES[@]}"; do
  echo ""
  echo "--- Profile: $profile ---"
  echo "Setting up Telegram gateway for '$profile'..."
  hermes -p "$profile" gateway setup || {
    echo "[WARN] Gateway setup failed for '$profile'. Configure manually:"
    echo "  hermes -p $profile gateway setup"
  }
done

echo ""
echo "========================================"
echo " Telegram gateways configured!"
echo "========================================"
echo ""
echo "Start all gateways:"
echo "  hermes -p triage gateway start &"
echo "  hermes -p investigator gateway start &"
echo "  hermes -p reviewer gateway start &"
echo "  hermes -p remediator gateway start &"
echo ""
echo "Or use: make deploy"
