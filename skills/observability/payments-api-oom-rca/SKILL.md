---
name: payments-api-oom-rca
description: >
  Activate when payments-api shows OOM kill pattern,
  memory spike, or pod restart cascade. Covers investigation
  from metrics through logs to traces.
version: 1.3.0
author: agent
platforms: [linux, macos]
---

## Procedure

1. Query metrics to detect memory spike
   ```sql
   SELECT
     toStartOfMinute(timestamp) AS minute,
     avg(value) AS memory_usage_mib
   FROM metrics_1m
   WHERE workspace_id = '<workspace_id>'
     AND service_name = 'payments-api'
     AND metric_name = 'process.memory.usage'
     AND timestamp >= now() - INTERVAL 1 HOUR
   GROUP BY minute
   ORDER BY minute
   ```

2. Search logs for OOM kill messages
   ```sql
   SELECT timestamp, severity_text, body
   FROM otel_logs
   WHERE workspace_id = '<workspace_id>'
     AND service_name = 'payments-api'
     AND severity_text IN ('ERROR', 'FATAL')
     AND (body LIKE '%OOM%' OR body LIKE '%killed%' OR body LIKE '%memory%')
     AND timestamp >= now() - INTERVAL 1 HOUR
   ORDER BY timestamp DESC
   LIMIT 100
   ```

3. List slow traces related to the service
   ```sql
   SELECT trace_id, span_id, name, duration_ns / 1e6 AS duration_ms
   FROM otel_traces
   WHERE workspace_id = '<workspace_id>'
     AND service_name = 'payments-api'
     AND duration_ns > 500000000
     AND timestamp >= now() - INTERVAL 1 HOUR
   ORDER BY duration_ns DESC
   LIMIT 50
   ```

4. Get exemplars linking memory metric to traces
   ```sql
   SELECT e.trace_id, m.value AS memory_value, e.timestamp
   FROM exemplars e
   JOIN metrics_1m m ON m.timestamp = e.timestamp
   WHERE m.workspace_id = '<workspace_id>'
     AND m.metric_name = 'process.memory.usage'
     AND m.service_name = 'payments-api'
     AND e.timestamp >= now() - INTERVAL 1 HOUR
   ORDER BY m.value DESC
   LIMIT 20
   ```

5. Cross-reference with MEMORY.md for previous OOM incidents

## Root Cause Pattern

- 512 MiB memory request insufficient after v2.4.1 deploy
- Memory spike correlates with increased request rate
- Previous occurrences: v2.3.0, v2.3.4, v2.4.0, v2.4.1
- Likely cause: memory leak introduced in connection pool refactor

## Verification

- Pod stays Running with 0 restarts for 5+ minutes after fix
- Memory usage stabilizes below 70% of new limit
- No new OOM kill messages in logs
