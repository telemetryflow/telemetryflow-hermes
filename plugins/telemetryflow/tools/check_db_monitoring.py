#!/usr/bin/env python3
"""Check database monitoring via TFO API and ClickHouse.

Supports all 15+ database types with engine-specific metrics:
PostgreSQL, MySQL, MariaDB, Percona, ClickHouse, MongoDB Community/Atlas,
MSSQL, SQLite3, TimescaleDB, Aurora, AWS RDS MySQL/Aurora/PostgreSQL,
AWS DynamoDB, CockroachDB, and QAN (Query Analytics Network).

Usage:
  python3 check_db_monitoring.py --resource inventory
  python3 check_db_monitoring.py --resource qan --db-type postgresql
  python3 check_db_monitoring.py --resource slow-queries --db-type mysql --min-duration 100
  python3 check_db_monitoring.py --resource engine-metrics --db-type clickhouse
  python3 check_db_monitoring.py --resource engine-metrics --db-type aurora
  python3 check_db_monitoring.py --resource engine-metrics --db-type mssql
  python3 check_db_monitoring.py --resource engine-metrics --db-type timescaledb
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _shared import clickhouse_query, output_json, parse_args, tfo_request

DB_TYPES = [
    "postgresql",
    "mysql",
    "mariadb",
    "percona",
    "clickhouse",
    "mongodb-community",
    "mongodb-atlas",
    "mssql",
    "sqlite3",
    "timescaledb",
    "aurora",
    "aws-rds-mysql",
    "aws-rds-aurora",
    "aws-rds-postgresql",
    "aws-dynamodb",
    "cockroachdb",
]

ENGINE_METRIC_TABLES = {
    "postgresql": "db_postgresql_metrics",
    "mysql": "db_mysql_metrics",
    "mariadb": "db_mariadb_metrics",
    "percona": "db_percona_metrics",
    "clickhouse": "db_clickhouse_metrics",
    "mongodb-community": "db_mongodb_metrics",
    "mongodb-atlas": "db_mongodb_atlas_metrics",
    "mssql": "db_mssql_metrics",
    "sqlite3": "db_sqlite3_metrics",
    "timescaledb": "db_timescaledb_metrics",
    "aurora": "db_aurora_metrics_1m",
    "aws-rds-mysql": "db_aws_rds_mysql_metrics",
    "aws-rds-aurora": "db_aurora_metrics_1m",
    "aws-rds-postgresql": "db_postgresql_metrics",
    "aws-dynamodb": "db_aws_dynamodb_metrics",
    "cockroachdb": "db_cockroachdb_metrics",
}


def main():
    args = parse_args()
    resource = args.get("resource", "inventory")
    db_type = args.get("db_type", "")
    min_duration = args.get("min_duration", "50")
    instance_id = args.get("instance_id", "")
    limit = int(args.get("limit", "20"))
    workspace_id = args.get("workspace_id", os.environ.get("TELEMETRYFLOW_WORKSPACE_ID", ""))

    if resource == "inventory":
        params = {}
        if db_type:
            params["dbType"] = db_type
        result = tfo_request("/db-monitoring/inventory", params=params)
        output_json(result)

    elif resource == "qan":
        params = {"limit": str(limit)}
        if db_type:
            params["dbType"] = db_type
        if workspace_id:
            params["workspaceId"] = workspace_id
        result = tfo_request("/db-monitoring/query-analytics", params=params)
        output_json(result)

    elif resource == "slow-queries":
        if not db_type:
            print("ERROR: --db-type is required for slow-queries", file=sys.stderr)
            sys.exit(1)
        sql = f"""
            SELECT
                database,
                normalized_query,
                count() AS exec_count,
                avg(query_duration_ms) AS avg_duration_ms,
                quantile(0.95)(query_duration_ms) AS p95_duration_ms,
                sum(rows_read) AS total_rows_read
            FROM qan_metrics
            WHERE database_type = '{db_type}'
              {"AND workspace_id = '" + workspace_id + "'" if workspace_id else ""}
              AND timestamp >= now() - INTERVAL 1 HOUR
              AND query_duration_ms > {min_duration}
            GROUP BY database, normalized_query
            ORDER BY p95_duration_ms DESC
            LIMIT {limit}
            FORMAT JSON
        """
        result = clickhouse_query(sql)
        output_json(result)

    elif resource == "engine-metrics":
        if not db_type:
            print("ERROR: --db-type is required for engine-metrics", file=sys.stderr)
            print(f"Valid types: {', '.join(DB_TYPES)}")
            sys.exit(1)
        if db_type not in ENGINE_METRIC_TABLES:
            print(f"ERROR: unsupported db-type '{db_type}'")
            print(f"Valid: {', '.join(sorted(ENGINE_METRIC_TABLES.keys()))}")
            sys.exit(1)

        table = ENGINE_METRIC_TABLES[db_type]
        inst_filter = f"AND instance_id = '{instance_id}'" if instance_id else ""

        sql = f"""
            SELECT
                metric_name,
                avg(value) AS avg_value,
                max(value) AS max_value,
                min(value) AS min_value,
                count() AS sample_count
            FROM {table}
            WHERE timestamp >= now() - INTERVAL 1 HOUR
              {inst_filter}
            GROUP BY metric_name
            ORDER BY max_value DESC
            LIMIT {limit}
            FORMAT JSON
        """
        result = clickhouse_query(sql)
        output_json(result)

    elif resource == "wait-stats":
        if db_type not in ("mssql",):
            print("ERROR: wait-stats only available for mssql", file=sys.stderr)
            sys.exit(1)
        sql = f"""
            SELECT wait_category, sum(wait_time_ms) AS total_wait_ms,
                   sum(waiting_tasks_count) AS total_tasks
            FROM db_mssql_waits
            WHERE timestamp >= now() - INTERVAL 1 HOUR
              {"AND instance_id = '" + instance_id + "'" if instance_id else ""}
            GROUP BY wait_category
            ORDER BY total_wait_ms DESC
            LIMIT {limit}
            FORMAT JSON
        """
        result = clickhouse_query(sql)
        output_json(result)

    elif resource == "top-queries":
        if not db_type:
            print("ERROR: --db-type is required", file=sys.stderr)
            sys.exit(1)
        engine_tables = {
            "mysql": "db_mysql_queries",
            "postgresql": "db_postgresql_queries",
            "mssql": "db_mssql_queries",
            "aurora": "db_aurora_queries",
            "clickhouse": "db_clickhouse_queries",
        }
        table = engine_tables.get(db_type)
        if not table:
            print(f"ERROR: top-queries not available for '{db_type}'")
            sys.exit(1)
        sql = f"""
            SELECT
                query_hash,
                any(sql_text) AS sql_preview,
                sum(execution_count) AS exec_count,
                avg(avg_duration_ms) AS avg_duration_ms
            FROM {table}
            WHERE timestamp >= now() - INTERVAL 1 HOUR
              {"AND instance_id = '" + instance_id + "'" if instance_id else ""}
            GROUP BY query_hash
            ORDER BY avg_duration_ms DESC
            LIMIT {limit}
            FORMAT JSON
        """
        result = clickhouse_query(sql)
        output_json(result)

    else:
        print(f"ERROR: unknown resource '{resource}'")
        print("Valid: inventory, qan, slow-queries, engine-metrics, wait-stats, top-queries")
        sys.exit(1)


if __name__ == "__main__":
    main()
