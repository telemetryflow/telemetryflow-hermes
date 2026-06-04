#!/usr/bin/env python3
"""Query TelemetryFlow metrics via ClickHouse or TFO API.

Usage:
  python3 query_metrics.py --service payments-api --metric process.memory.usage --duration 1h
  python3 query_metrics.py --service payments-api --metric http.server.duration --duration 30m --resolution 1m
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _shared import clickhouse_query, output_json, parse_args

RESOLUTION_MAP = {
    "1m": "metrics_1m",
    "5m": "metrics_5m",
    "1h": "metrics_1h",
    "15m": "metrics_5m",
    "30m": "metrics_5m",
}

DURATION_MAP = {
    "15m": "INTERVAL 15 MINUTE",
    "30m": "INTERVAL 30 MINUTE",
    "1h": "INTERVAL 1 HOUR",
    "2h": "INTERVAL 2 HOUR",
    "6h": "INTERVAL 6 HOUR",
    "12h": "INTERVAL 12 HOUR",
    "24h": "INTERVAL 24 HOUR",
    "1d": "INTERVAL 1 DAY",
    "7d": "INTERVAL 7 DAY",
}


def main():
    args = parse_args()
    service = args.get("service")
    metric = args.get("metric", "")
    duration = args.get("duration", "1h")
    resolution = args.get("resolution", "5m")
    workspace_id = args.get("workspace_id", os.environ.get("TELEMETRYFLOW_WORKSPACE_ID", ""))
    limit = int(args.get("limit", "100"))

    if not service:
        print("ERROR: --service is required", file=sys.stderr)
        sys.exit(1)

    table = RESOLUTION_MAP.get(resolution, "metrics_5m")
    interval = DURATION_MAP.get(duration, "INTERVAL 1 HOUR")

    if metric:
        sql = f"""
            SELECT
                toStartOfMinute(timestamp) AS minute,
                service_name,
                metric_name,
                avg(value) AS avg_value,
                quantile(0.95)(value) AS p95,
                quantile(0.99)(value) AS p99,
                min(value) AS min_value,
                max(value) AS max_value,
                count() AS sample_count
            FROM {table}
            WHERE service_name = '{service}'
              AND metric_name = '{metric}'
              {"AND workspace_id = '" + workspace_id + "'" if workspace_id else ""}
              AND timestamp >= now() - {interval}
            GROUP BY minute, service_name, metric_name
            ORDER BY minute DESC
            LIMIT {limit}
            FORMAT JSON
        """
    else:
        sql = f"""
            SELECT
                service_name,
                metric_name,
                metric_type,
                avg(value) AS avg_value,
                max(value) AS max_value,
                min(value) AS min_value,
                count() AS sample_count
            FROM {table}
            WHERE service_name = '{service}'
              {"AND workspace_id = '" + workspace_id + "'" if workspace_id else ""}
              AND timestamp >= now() - {interval}
            GROUP BY service_name, metric_name, metric_type
            ORDER BY max_value DESC
            LIMIT {limit}
            FORMAT JSON
        """

    result = clickhouse_query(sql)
    output_json(result)


if __name__ == "__main__":
    main()
