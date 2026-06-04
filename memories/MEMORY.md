# MEMORY.md

## Known Patterns
- payments-api always OOMs on deploy (4x in 30 days, versions v2.3.0, v2.3.4, v2.4.0, v2.4.1)
- workspace_id is mandatory on all ClickHouse queries
- node-pool-3 has recurring memory pressure
- alert fatigue rule: suppress < medium severity during deploys
- auth-service crashes correlate with cert rotation schedule (every 90 days)
- redis-cluster-01 latency spikes at 02:00 UTC (backup window)

## Platform Conventions
- All ClickHouse tables are OTLP-compliant: metrics_1m, metrics_5m, metrics_1h, otel_logs, otel_traces
- Tenant hierarchy: region → organization → workspace → tenant
- Always filter by workspace_id in WHERE clause
- Use materialized views for aggregation, not raw table scans

## Tool Quirks
- ClickHouse client needs --format JSON for script parsing
- kubectl logs --previous flag required for restarted containers
- Trace queries need both trace_id AND span_id for waterfall analysis
