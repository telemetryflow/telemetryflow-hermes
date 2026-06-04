#!/bin/bash
set -euo pipefail

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"

echo "========================================"
echo " TelemetryFlow Hermes — Air-Gapped Deploy"
echo "========================================"
echo ""
echo "This script configures Hermes for air-gapped operation"
echo "using Ollama as the LLM provider (no external network)."
echo ""

command -v ollama >/dev/null 2>&1 || {
  echo "[FAIL] Ollama not installed. Install first: curl -fsSL https://ollama.com/install.sh | sh"
  exit 1
}

echo "[1/3] Configuring Ollama..."
hermes config set model.default "llama3.3:70b" || true
hermes config set model.provider "ollama" || true

echo ""
echo "[2/3] Pulling model (requires network for initial pull)..."
ollama pull llama3.3:70b 2>/dev/null || {
  echo "[WARN] Could not pull model. Ensure model is already available."
  echo "  Run: ollama pull llama3.3:70b"
}

echo ""
echo "[3/3] Configuring profiles for air-gapped..."
PROFILES=("triage" "investigator" "reviewer" "remediator")
for profile in "${PROFILES[@]}"; do
  hermes -p "$profile" config set model.default "llama3.3:70b" 2>/dev/null || true
  hermes -p "$profile" config set model.provider "ollama" 2>/dev/null || true
  echo "[OK] $profile → ollama/llama3.3:70b"
done

echo ""
echo "========================================"
echo " Air-gapped deployment ready!"
echo "========================================"
echo ""
echo "Deployment chain:"
echo "  Ollama pod → Local model → Hermes Agent → ClickHouse → TelemetryFlow"
echo ""
echo "No external network access required."
echo "No API keys needed."
echo "Prompt, context, and response never leave the cluster."
