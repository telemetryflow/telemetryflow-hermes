#!/usr/bin/env bash
# ===========================================================================
# run-container.sh
# Build, tag, and/or push TelemetryFlow Hermes Docker images.
#
# TelemetryFlow Hermes - Community Enterprise Observability Platform (CEOP)
# Copyright (c) 2024-2026 Telemetri Data Indonesia. All rights reserved.
#
# Usage:
#   ./run-container.sh [options]
#
# Options:
#   -b, --build           Build the Hermes image
#   -t, --tag <version>   Override version tag (default: 2.0.0)
#   -p, --push            Push tags to registry
#   -c, --complete        Complete: build, tag, and push
#   --profile <name>      Start with docker-compose profile (core, monitoring, all, tools)
#   --up                  Start containers (docker-compose up)
#   --down                Stop containers (docker-compose down)
#   -h, --help            Show help
#
# Examples:
#   ./run-container.sh                        # Build Hermes, tag only
#   ./run-container.sh -b -t 2.1.0            # Build with custom tag
#   ./run-container.sh -c                     # Build, tag, push
#   ./run-container.sh -c -t 2.1.0            # Complete with custom tag
#   ./run-container.sh --up                   # Start Hermes only
#   ./run-container.sh --up --profile core    # Start with core profile
#   ./run-container.sh --up --profile all     # Start full stack
#   ./run-container.sh --down                 # Stop all containers
#
# Images:
#   hermes → telemetryflow/telemetryflow-hermes
#
# Tags generated per image:
#   :latest, :<version>, :<version>-<commit>, :demo-<YYYYMMDD>
# ===========================================================================
set -euo pipefail

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
IMAGE_HERMES="telemetryflow/telemetryflow-hermes"
VERSION="1.0.0"
COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
YYYYMMDD=$(date +"%Y%m%d")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
header() { echo -e "\n$1\n----------------------------------------------------------"; }

usage() {
  cat <<EOF
Usage: $0 [options]

Options:
  -b, --build            Build the Hermes image
  -t, --tag <version>    Override version tag (default: ${VERSION})
  -p, --push             Push tags to registry
  -c, --complete         Complete: build, tag, and push
  --profile <name>       Docker Compose profile (core, monitoring, all, tools)
  --up                   Start containers (docker-compose up)
  --down                 Stop containers (docker-compose down)
  -h, --help             Show this help

Examples:
  $0                        # Build Hermes, tag only
  $0 -b -t 2.1.0            # Build with custom tag
  $0 -c                     # Build, tag, push
  $0 --up                   # Start Hermes only
  $0 --up --profile core    # Start with core profile
  $0 --up --profile all     # Start full stack
  $0 --down                 # Stop all containers

Profiles:
  core        Backend + Frontend + Postgres + ClickHouse + Redis + NATS
  monitoring  TFO Collector + TFO Agent + Jaeger
  tools       Portainer
  all         Everything combined
EOF
  exit 0
}

# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
build_hermes() {
  header "Building TelemetryFlow Hermes..."
  docker build \
    --build-arg VERSION="${VERSION}" \
    --build-arg GIT_COMMIT="${COMMIT}" \
    --build-arg GIT_BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo main)" \
    --build-arg BUILD_TIME="$(date -u '+%Y-%m-%dT%H:%M:%SZ')" \
    -t "${IMAGE_HERMES}:latest" \
    -t "${IMAGE_HERMES}:${VERSION}" \
    -t "${IMAGE_HERMES}:${VERSION}-${COMMIT}" \
    -t "${IMAGE_HERMES}:demo-${YYYYMMDD}" \
    .
}

# ---------------------------------------------------------------------------
# Tag
# ---------------------------------------------------------------------------
tag_image() {
  header "Tagging Hermes..."
  docker tag "${IMAGE_HERMES}:latest" "${IMAGE_HERMES}:${VERSION}" 2>/dev/null || true
  docker tag "${IMAGE_HERMES}:latest" "${IMAGE_HERMES}:${VERSION}-${COMMIT}" 2>/dev/null || true
  docker tag "${IMAGE_HERMES}:latest" "${IMAGE_HERMES}:demo-${YYYYMMDD}" 2>/dev/null || true
}

# ---------------------------------------------------------------------------
# Push
# ---------------------------------------------------------------------------
push_image() {
  header "Pushing Hermes..."
  docker push "${IMAGE_HERMES}:latest"
  docker push "${IMAGE_HERMES}:${VERSION}"
  docker push "${IMAGE_HERMES}:${VERSION}-${COMMIT}"
  docker push "${IMAGE_HERMES}:demo-${YYYYMMDD}"
}

# ---------------------------------------------------------------------------
# Compose
# ---------------------------------------------------------------------------
compose_up() {
  header "Starting containers..."
  local profile_args=()
  for p in "${PROFILES[@]}"; do
    profile_args+=(--profile "$p")
  done

  echo "Profiles: ${profile_args[*]:-<none - hermes only>}"
  docker compose "${profile_args[@]}" up -d

  echo ""
  echo "Running containers:"
  docker compose "${profile_args[@]}" ps
}

compose_down() {
  header "Stopping containers..."
  docker compose --profile core --profile monitoring --profile tools --profile all down
  echo "All containers stopped."
}

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print_summary() {
  local action=$1
  echo "  [Hermes] ${action}"
  echo "  ${IMAGE_HERMES}:latest"
  echo "  ${IMAGE_HERMES}:${VERSION}"
  echo "  ${IMAGE_HERMES}:${VERSION}-${COMMIT}"
  echo "  ${IMAGE_HERMES}:demo-${YYYYMMDD}"
}

# ---------------------------------------------------------------------------
# Parse args
# ---------------------------------------------------------------------------
DO_BUILD=false
DO_PUSH=false
DO_COMPLETE=false
DO_UP=false
DO_DOWN=false
PROFILES=()

while [[ $# -gt 0 ]]; do
  case $1 in
    -b|--build)    DO_BUILD=true;    shift   ;;
    -t|--tag)      VERSION="$2";     shift 2 ;;
    -p|--push)     DO_PUSH=true;     shift   ;;
    -c|--complete) DO_COMPLETE=true;  shift   ;;
    --profile)     PROFILES+=("$2");  shift 2 ;;
    --up)          DO_UP=true;        shift   ;;
    --down)        DO_DOWN=true;      shift   ;;
    -h|--help)     usage ;;
    *) echo "Unknown option: $1"; usage ;;
  esac
done

# --complete overrides: build + push
if $DO_COMPLETE; then
  DO_BUILD=true
  DO_PUSH=true
fi

# Default: build if no action flags given
if ! $DO_BUILD && ! $DO_PUSH && ! $DO_UP && ! $DO_DOWN; then
  DO_BUILD=true
fi

# ---------------------------------------------------------------------------
# Execute — Build & Tag
# ---------------------------------------------------------------------------
if $DO_BUILD; then
  build_hermes
  tag_image
fi

# ---------------------------------------------------------------------------
# Execute — Push
# ---------------------------------------------------------------------------
if $DO_PUSH; then
  push_image
fi

# ---------------------------------------------------------------------------
# Execute — Compose
# ---------------------------------------------------------------------------
if $DO_DOWN; then
  compose_down
fi

if $DO_UP; then
  compose_up
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
header "Done."
if $DO_BUILD; then
  print_summary "built+tagged"
fi
if $DO_PUSH; then
  print_summary "pushed"
fi
