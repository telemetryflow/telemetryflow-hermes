#!/usr/bin/env bash
# Render slides.md to PPTX and PDF using Marp CLI
# Install once: npm install -g @marp-team/marp-cli

set -e

SLIDES="$(dirname "$0")/tfo-hermes-v1.2.0.md"
OUT="$(dirname "$0")/presentation"
mkdir -p "$OUT"

echo "→ Rendering PPTX..."
npx @marp-team/marp-cli "$SLIDES" --pptx --output "$OUT/tfo-hermes-presentation-2026.pptx" --allow-local-files

echo "→ Rendering PDF..."
npx @marp-team/marp-cli "$SLIDES" --pdf  --output "$OUT/tfo-hermes-presentation-2026.pdf"  --allow-local-files

echo "✓ Done — outputs in $OUT/"
