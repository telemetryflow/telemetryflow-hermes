# MEMORY.md — Investigator Agent

## Query Patterns
- Always start with metrics to establish timeline
- Use 1m resolution for acute incidents, 5m for trends, 1h for patterns
- Log search: start with severity='ERROR', expand if needed
- Trace analysis: filter by duration > p95 first, then narrow
- Exemplars: always link back to metric that triggered the alert

## Service-Specific Knowledge
- payments-api: memory-sensitive, check OOM patterns first
- auth-service: cert-related, check TLS expiry and rotation logs
- redis-cluster-01: check backup window impact (02:00 UTC)
- api-gateway: check upstream latency, not just gateway metrics

## ClickHouse Query Tips
- workspace_id is MANDATORY in every WHERE clause
- Use materialized views for aggregation over raw table scans
- otel_logs: use FTS5 syntax for full-text search
- otel_traces: JOIN on trace_id for waterfall analysis
