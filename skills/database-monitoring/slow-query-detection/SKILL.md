---
name: slow-query-detection
description: >
  Activate when investigating database performance issues.
  Queries TelemetryFlow QAN (Query Analytics) data in ClickHouse
  to identify slow queries and performance bottlenecks.
version: 1.0.0
author: agent
platforms: [linux, macos]
---

## Procedure

1. Query QAN data for slow queries
   ```sql
   SELECT
     database,
     query_hash,
     normalized_query,
     count() AS exec_count,
     avg(query_duration_ms) AS avg_duration_ms,
     quantile(0.95)(query_duration_ms) AS p95_duration_ms,
     sum(rows_read) AS total_rows_read
   FROM qan_metrics
   WHERE workspace_id = '{workspace_id}'
     AND timestamp >= now() - INTERVAL 1 HOUR
     AND query_duration_ms > {threshold_ms}
   GROUP BY database, query_hash, normalized_query
   ORDER BY p95_duration_ms DESC
   LIMIT 20
   FORMAT JSON
   ```

2. Identify top resource consumers
   ```sql
   SELECT
     database,
     normalized_query,
     sum(rows_read) AS total_rows,
     sum(bytes_read) AS total_bytes,
     count() AS exec_count
   FROM qan_metrics
   WHERE workspace_id = '{workspace_id}'
     AND timestamp >= now() - INTERVAL 1 HOUR
   GROUP BY database, normalized_query
   ORDER BY total_rows DESC
   LIMIT 20
   FORMAT JSON
   ```

3. Check for lock contention
   ```sql
   SELECT timestamp, database, query, lock_wait_time_ms
   FROM qan_metrics
   WHERE workspace_id = '{workspace_id}'
     AND lock_wait_time_ms > 100
     AND timestamp >= now() - INTERVAL 1 HOUR
   ORDER BY lock_wait_time_ms DESC
   LIMIT 20
   FORMAT JSON
   ```

4. Correlate with application metrics
   - Check if slow queries correlate with latency spikes
   - Check if slow queries correlate with error rate increase
   - Use exemplars to link application traces to specific queries

## Common Findings

- Missing index: high rows_read for simple lookups
- Full table scan: normalized_query shows SELECT * without WHERE
- Lock contention: high lock_wait_time_ms during peak hours
- Connection pool exhaustion: many short-duration queries queued

## Verification

- Query duration returns to baseline after fix
- No new slow query alerts for 15+ minutes
- Application latency metrics normalize
