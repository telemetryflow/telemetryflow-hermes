#!/bin/bash
set -euo pipefail

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "========================================"
echo " TelemetryFlow Hermes — Install"
echo "========================================"
echo ""

command -v hermes >/dev/null 2>&1 && {
  echo "[OK] Hermes already installed: $(hermes --version 2>/dev/null || echo 'unknown')"
  exit 0
}

echo "[1/3] Installing Hermes Agent..."
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

echo ""
echo "[2/3] Verifying installation..."
export PATH="$HOME/.local/bin:$PATH"
if command -v hermes >/dev/null 2>&1; then
  echo "[OK] Hermes installed successfully"
else
  echo "[FAIL] Hermes not found in PATH. Run: source ~/.bashrc"
  exit 1
fi

echo ""
echo "[3/3] Running health check..."
hermes doctor || {
  echo "[WARN] Health check failed. Run: hermes doctor --fix"
}

echo ""
echo "========================================"
echo " Installation complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Copy .env.example to ~/.hermes/.env and fill in your keys"
echo "  2. Run: make setup"
echo "  3. Run: make verify"
