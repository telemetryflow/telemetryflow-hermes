#!/usr/bin/env python3
"""Get exemplars linking metrics to traces.

Usage:
  python3 get_exemplars.py --service payments-api --metric process.memory.usage --duration 1h
  python3 get_exemplars.py --trace-id abc123
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
}


def main():
    args = parse_args()
    service = args.get("service", "")
    metric = args.get("metric", "")
    trace_id = args.get("trace_id", "")
    duration = args.get("duration", "1h")
    workspace_id = args.get("workspace_id", os.environ.get("TELEMETRYFLOW_WORKSPACE_ID", ""))
    limit = int(args.get("limit", "20"))

    interval = DURATION_MAP.get(duration, "INTERVAL 1 HOUR")

    where_parts = [f"timestamp >= now() - {interval}"]
    if service:
        where_parts.append(f"service_name = '{service}'")
    if metric:
        where_parts.append(f"metric_name = '{metric}'")
    if trace_id:
        where_parts.append(f"trace_id = '{trace_id}'")
    if workspace_id:
        where_parts.append(f"workspace_id = '{workspace_id}'")

    where = " AND ".join(where_parts)

    sql = f"""
        SELECT
            timestamp,
            metric_name,
            service_name,
            trace_id,
            span_id,
            value
        FROM exemplars
        WHERE {where}
        ORDER BY value DESC
        LIMIT {limit}
        FORMAT JSON
    """

    result = clickhouse_query(sql)
    output_json(result)


if __name__ == "__main__":
    main()
