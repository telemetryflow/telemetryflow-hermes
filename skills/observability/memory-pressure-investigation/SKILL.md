---
name: memory-pressure-investigation
description: >
  Activate when investigating node or pod memory pressure,
  Evicted pods, or memory-related alerts in Kubernetes.
version: 1.0.0
author: agent
platforms: [linux, macos]
---

## Procedure

1. Check node-level memory pressure
   ```bash
   kubectl describe node <node-name> | grep -A5 "MemoryPressure"
   kubectl top nodes
   ```

2. Identify memory-hungry pods
   ```bash
   kubectl top pods -A --sort-by=memory | head -20
   ```

3. Check for evicted pods
   ```bash
   kubectl get pods -A --field-selector=status.reason=Evicted
   ```

4. Query ClickHouse for memory metrics
   ```sql
   SELECT
     service_name,
     toStartOfMinute(timestamp) AS minute,
     avg(value) AS memory_mib,
     max(value) AS peak_mib
   FROM metrics_1m
   WHERE workspace_id = '{workspace_id}'
     AND metric_name = 'process.memory.usage'
     AND timestamp >= now() - INTERVAL 2 HOURS
   GROUP BY service_name, minute
   ORDER BY peak_mib DESC
   LIMIT 50
   FORMAT JSON
   ```

5. Check for OOM events in logs
   ```sql
   SELECT timestamp, service_name, body
   FROM otel_logs
   WHERE workspace_id = '{workspace_id}'
     AND (body LIKE '%OOM%' OR body LIKE '%evicted%' OR body LIKE '%memory pressure%')
     AND timestamp >= now() - INTERVAL 2 HOURS
   ORDER BY timestamp DESC
   LIMIT 50
   FORMAT JSON
   ```

6. Analyze memory trends over time
   - Compare current usage with 7-day average
   - Look for gradual increase (leak) vs sudden spike (load)
   - Check if memory returns to baseline after load subsides

## Root Cause Patterns

- Gradual increase + no baseline return = memory leak
- Sudden spike + specific deploy = bad release
- Spike + specific request pattern = load-related
- Spike + node pressure = insufficient node resources

## Verification

- Memory usage below 70% of limit after remediation
- No evicted pods for 30+ minutes
- Node MemoryPressure condition is False
