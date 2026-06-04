#!/usr/bin/env python3
"""Query signal correlations across metrics, logs, and traces.

Uses TFO's ClickHouse signal_correlations_1h materialized view.

Usage:
  python3 query_correlations.py --service payments-api --duration 1h
  python3 query_correlations.py --correlation-type metric-log --duration 6h
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
    correlation_type = args.get("correlation_type", "")
    duration = args.get("duration", "1h")
    workspace_id = args.get("workspace_id", os.environ.get("TELEMETRYFLOW_WORKSPACE_ID", ""))
    limit = int(args.get("limit", "50"))

    interval = DURATION_MAP.get(duration, "INTERVAL 1 HOUR")

    where_parts = [f"timestamp >= now() - {interval}"]
    if service:
        where_parts.append(f"service_name = '{service}'")
    if correlation_type:
        where_parts.append(f"correlation_type = '{correlation_type}'")
    if workspace_id:
        where_parts.append(f"workspace_id = '{workspace_id}'")

    where = " AND ".join(where_parts)

    sql = f"""
        SELECT
            service_name,
            correlation_type,
            count() AS correlation_count,
            avg(confidence_score) AS avg_confidence
        FROM signal_correlations_1h
        WHERE {where}
        GROUP BY service_name, correlation_type
        ORDER BY correlation_count DESC
        LIMIT {limit}
        FORMAT JSON
    """

    result = clickhouse_query(sql)
    output_json(result)


if __name__ == "__main__":
    main()
