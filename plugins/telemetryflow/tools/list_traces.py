#!/usr/bin/env python3
"""List and analyze distributed traces from TelemetryFlow.

Usage:
  python3 list_traces.py --service payments-api --min-duration 500 --duration 1h
  python3 list_traces.py --trace-id abc123def456
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
}


def main():
    args = parse_args()
    service = args.get("service", "")
    trace_id = args.get("trace_id", "")
    min_duration = int(args.get("min_duration", "500"))
    duration = args.get("duration", "1h")
    workspace_id = args.get("workspace_id", os.environ.get("TELEMETRYFLOW_WORKSPACE_ID", ""))
    limit = int(args.get("limit", "50"))

    if trace_id:
        sql = f"""
            SELECT
                span_id,
                parent_span_id,
                name,
                service_name,
                duration_ns / 1e6 AS duration_ms,
                status_code,
                timestamp
            FROM otel_traces
            WHERE trace_id = '{trace_id}'
              {"AND workspace_id = '" + workspace_id + "'" if workspace_id else ""}
            ORDER BY timestamp
            FORMAT JSON
        """
    else:
        interval = DURATION_MAP.get(duration, "INTERVAL 1 HOUR")
        where_parts = [
            f"duration_ns > {min_duration} * 1000000",
            f"timestamp >= now() - {interval}",
        ]
        if service:
            where_parts.append(f"service_name = '{service}'")
        if workspace_id:
            where_parts.append(f"workspace_id = '{workspace_id}'")

        where = " AND ".join(where_parts)

        sql = f"""
            SELECT
                trace_id,
                span_id,
                name,
                service_name,
                duration_ns / 1e6 AS duration_ms,
                status_code,
                timestamp
            FROM otel_traces
            WHERE {where}
            ORDER BY duration_ns DESC
            LIMIT {limit}
            FORMAT JSON
        """

    result = clickhouse_query(sql)
    output_json(result)


if __name__ == "__main__":
    main()
