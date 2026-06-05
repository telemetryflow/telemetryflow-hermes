#!/bin/bash
set -euo pipefail

CLICKHOUSE_HOST="${CLICKHOUSE_HOST:-localhost}"
CLICKHOUSE_PORT="${CLICKHOUSE_PORT:-9000}"
CLICKHOUSE_USER="${CLICKHOUSE_USER:-default}"
CLICKHOUSE_PASSWORD="${CLICKHOUSE_PASSWORD:-}"
TELEMETRYFLOW_DB_NAME="${TELEMETRYFLOW_DB_NAME:-telemetryflow_db}"
HERMES_PASSWORD="${1:-}"

if [ -z "$HERMES_PASSWORD" ]; then
  echo "Usage: $0 <hermes_readonly_password>"
  echo ""
  echo "Creates a read-only ClickHouse user for Hermes agents."
  echo "The user will have SELECT-only access to telemetry tables."
  echo ""
  echo "Database name is read from TELEMETRYFLOW_DB_NAME env var"
  echo "(default: telemetryflow_db)"
  exit 1
fi

echo "Creating hermes_readonly user on ClickHouse (database: ${TELEMETRYFLOW_DB_NAME})..."

SQL_TEMPLATE="$(dirname "$0")/clickhouse-readonly.sql"
SQL_EXPANDED=$(sed "s/\${TELEMETRYFLOW_DB_NAME}/${TELEMETRYFLOW_DB_NAME}/g" "$SQL_TEMPLATE")

clickhouse-client \
  --host="$CLICKHOUSE_HOST" \
  --port="$CLICKHOUSE_PORT" \
  --user="$CLICKHOUSE_USER" \
  ${CLICKHOUSE_PASSWORD:+--password="$CLICKHOUSE_PASSWORD"} \
  --database="$TELEMETRYFLOW_DB_NAME" \
  --query="$SQL_EXPANDED" \
  -q "ALTER USER hermes_readonly IDENTIFIED BY '$HERMES_PASSWORD'"

echo ""
echo "User created. Update ~/.hermes/.env:"
echo "  CLICKHOUSE_USER=hermes_readonly"
echo "  CLICKHOUSE_PASSWORD=$HERMES_PASSWORD"
echo "  TELEMETRYFLOW_DB_NAME=$TELEMETRYFLOW_DB_NAME"
