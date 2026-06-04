---
name: cross-signal-correlation
description: >
  Activate when investigating an incident that spans multiple telemetry
  signals. Provides methodology for correlating metrics, logs, traces,
  and exemplars to find root cause.
version: 1.1.0
author: agent
platforms: [linux, macos]
---

## Procedure

1. Start with the triggering signal (usually a metric alert)
   - Record the exact timestamp and value
   - Note the service, namespace, and workspace

2. Establish the timeline
   - Query metrics for 30 min before and after the alert
   - Look for correlated metric changes in other services

3. Correlate with logs
   - Search for ERROR/CRITICAL logs in the same time window
   - Check for patterns: OOM, timeout, connection refused, cert errors
   - Note: log timestamps may lag — check ±2 minutes

4. Correlate with traces
   - Find slow spans in the affected time window
   - Build waterfall: identify which span is the bottleneck
   - Check downstream services in the same trace

5. Link via exemplars
   - Use exemplar links from the triggering metric to specific traces
   - This provides direct evidence: "this metric spike was caused by this trace"

6. Cross-reference with MEMORY.md
   - Check for similar patterns in past incidents
   - Note any recurring root causes

7. Produce correlation report:
   ```
   Correlation: {metric spike} → {log errors} → {slow spans} → {exemplar traces}
   Timeline: T+0 alert → T+30s log errors → T+45s trace slowdown
   Root cause hypothesis: {hypothesis}
   Evidence: {citations from each signal}
   ```

## Correlation Patterns

| Metric Pattern           | Log Pattern              | Trace Pattern              | Likely Cause         |
|--------------------------|--------------------------|----------------------------|----------------------|
| Memory spike             | OOM killed               | Allocation-heavy spans     | Memory leak / limit  |
| Latency spike            | Timeout errors           | Long-duration spans        | Downstream slowdown  |
| Error rate increase      | 5xx responses            | Error-marked spans         | Bad deploy / config  |
| CPU spike                | High CPU in logs         | Compute-heavy spans        | Infinite loop / load |
| Connection pool exhaust  | Connection refused       | Queue wait spans           | Pool size too small  |

## Pitfalls

- Correlation ≠ causation — always verify the causal chain
- Clock skew between services — use trace_id for ordering, not timestamps
- Sampling: traces may be sampled — absence of evidence is not evidence of absence
