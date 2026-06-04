#!/usr/bin/env python3
"""Search TelemetryFlow logs with severity filtering.

Usage:
  python3 search_logs.py --service payments-api --severity ERROR --duration 1h
  python3 search_logs.py --service auth-service --search "OOM killed" --duration 2h
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _shared import clickhouse_query, output_json, parse_args

DURATION_MAP = {
    "15m": "INTERVAL 15 MINUTE",
    "30m": "INTERVAL 30 MINUTE",
    "1h": "INTERVAL 1 HOUR",
    "2h": "INTERVAL 2 HOUR",
    "6h": "INTERVAL 6 HOUR",
    "24h": "INTERVAL 24 HOUR",
    "1d": "INTERVAL 1 DAY",
    "7d": "INTERVAL 7 DAY",
}


def main():
    args = parse_args()
    service = args.get("service")
    severity = args.get("severity", "ERROR")
    duration = args.get("duration", "1h")
    search = args.get("search", "")
    workspace_id = args.get("workspace_id", os.environ.get("TELEMETRYFLOW_WORKSPACE_ID", ""))
    limit = int(args.get("limit", "100"))

    interval = DURATION_MAP.get(duration, "INTERVAL 1 HOUR")

    where_parts = [
        f"severity_text >= '{severity}'",
        f"timestamp >= now() - {interval}",
    ]
    if service:
        where_parts.append(f"service_name = '{service}'")
    if workspace_id:
        where_parts.append(f"workspace_id = '{workspace_id}'")
    if search:
        where_parts.append(f"body LIKE '%{search}%'")

    where = " AND ".join(where_parts)

    sql = f"""
        SELECT timestamp, severity_text, service_name, trace_id, span_id, body
        FROM otel_logs
        WHERE {where}
        ORDER BY timestamp DESC
        LIMIT {limit}
        FORMAT JSON
    """

    result = clickhouse_query(sql)
    output_json(result)


if __name__ == "__main__":
    main()
