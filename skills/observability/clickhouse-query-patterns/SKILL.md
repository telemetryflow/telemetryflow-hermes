---
name: clickhouse-query-patterns
description: >
  Activate when querying TelemetryFlow ClickHouse for observability data.
  Contains optimized query templates for metrics, logs, traces, and exemplars.
version: 1.1.0
author: agent
platforms: [linux, macos]
---

## Metrics Queries

### Time-series for a service metric
```sql
SELECT
  toStartOfMinute(timestamp) AS minute,
  avg(value) AS avg_value,
  quantile(0.95)(value) AS p95,
  quantile(0.99)(value) AS p99
FROM metrics_1m
WHERE workspace_id = '{workspace_id}'
  AND service_name = '{service}'
  AND metric_name = '{metric}'
  AND timestamp >= now() - INTERVAL {duration}
GROUP BY minute
ORDER BY minute
FORMAT JSON
```

### Top services by error rate
```sql
SELECT
  service_name,
  countIf(severity_text = 'ERROR') AS error_count,
  count(*) AS total_count,
  round(error_count / total_count * 100, 2) AS error_rate
FROM otel_logs
WHERE workspace_id = '{workspace_id}'
  AND timestamp >= now() - INTERVAL 1 HOUR
GROUP BY service_name
HAVING error_rate > 1
ORDER BY error_rate DESC
LIMIT 20
FORMAT JSON
```

## Log Queries

### Full-text search with severity filter
```sql
SELECT timestamp, severity_text, service_name, body
FROM otel_logs
WHERE workspace_id = '{workspace_id}'
  AND severity_text >= '{severity}'
  AND timestamp >= now() - INTERVAL {duration}
  AND body LIKE '%{search_term}%'
ORDER BY timestamp DESC
LIMIT {limit}
FORMAT JSON
```

## Trace Queries

### Waterfall for a specific trace
```sql
SELECT
  span_id,
  parent_span_id,
  name,
  service_name,
  duration_ns / 1e6 AS duration_ms,
  timestamp
FROM otel_traces
WHERE workspace_id = '{workspace_id}'
  AND trace_id = '{trace_id}'
ORDER BY timestamp
FORMAT JSON
```

### Slowest spans in time window
```sql
SELECT
  trace_id,
  span_id,
  name,
  service_name,
  duration_ns / 1e6 AS duration_ms
FROM otel_traces
WHERE workspace_id = '{workspace_id}'
  AND timestamp >= now() - INTERVAL {duration}
  AND duration_ns > {threshold_ms} * 1000000
ORDER BY duration_ns DESC
LIMIT 50
FORMAT JSON
```

## Exemplar Queries

### Link metric to traces
```sql
SELECT
  e.trace_id,
  m.value AS metric_value,
  m.metric_name,
  e.timestamp
FROM exemplars e
JOIN metrics_1m m ON m.timestamp = e.timestamp AND m.workspace_id = e.workspace_id
WHERE m.workspace_id = '{workspace_id}'
  AND m.metric_name = '{metric}'
  AND e.timestamp >= now() - INTERVAL {duration}
ORDER BY m.value DESC
LIMIT 20
FORMAT JSON
```

## Critical Rules

- workspace_id is MANDATORY in every WHERE clause
- Use FORMAT JSON for script parsing
- Prefer materialized views over raw table scans
- Use 1m resolution for acute, 5m for trends, 1h for patterns
