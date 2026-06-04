---
name: qan-analysis
description: >
  Activate when analyzing Query Analytics data from TelemetryFlow's
  database monitoring. Provides patterns for understanding query
  performance across 9 supported databases.
version: 1.0.0
author: agent
platforms: [linux, macos]
---

## Supported Databases

TelemetryFlow monitors 9 databases with native collectors:
PostgreSQL, MySQL, MongoDB, Redis, ClickHouse, Elasticsearch, Cassandra, SQLite, SQL Server

## Procedure

1. Identify the target database type
2. Query QAN overview for the database
   ```sql
   SELECT
     database_type,
     count(DISTINCT query_hash) AS unique_queries,
     count() AS total_executions,
     avg(query_duration_ms) AS avg_duration,
     quantile(0.95)(query_duration_ms) AS p95_duration
   FROM qan_metrics
   WHERE workspace_id = '{workspace_id}'
     AND timestamp >= now() - INTERVAL 1 HOUR
   GROUP BY database_type
   ORDER BY p95_duration DESC
   FORMAT JSON
   ```

3. Drill into specific database queries
   ```sql
   SELECT
     normalized_query,
     count() AS exec_count,
     avg(query_duration_ms) AS avg_ms,
     quantile(0.99)(query_duration_ms) AS p99_ms,
     avg(rows_examined) AS avg_rows,
     avg(rows_sent) AS avg_result_rows,
     avg(rows_examined) / nullIf(avg(rows_sent), 0) AS selectivity_ratio
   FROM qan_metrics
   WHERE workspace_id = '{workspace_id}'
     AND database_type = '{db_type}'
     AND timestamp >= now() - INTERVAL 1 HOUR
   GROUP BY normalized_query
   HAVING avg_ms > 50
   ORDER BY avg_ms DESC
   LIMIT 20
   FORMAT JSON
   ```

4. Analyze selectivity (rows examined vs rows returned)
   - High ratio (> 100) → missing index or inefficient query
   - Low ratio (< 10) → query is well-optimized

5. Check temporal patterns
   - Are slow queries concentrated at specific times?
   - Do they correlate with backup windows?
   - Do they correlate with deployment events?

## Reporting Format

```
Database: {database_type}
Total Queries: {count}
Top Slow Query: {normalized_query}
  Executions: {count}
  Avg Duration: {avg_ms}ms
  P95 Duration: {p95_ms}ms
  Selectivity: {ratio}
  Recommendation: {index_hint / query_rewrite / config_change}
```

## Verification

- QAN shows no new slow queries after remediation
- Average query duration within acceptable range
- No lock contention in subsequent analysis window
