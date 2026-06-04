---
name: tfql-query
description: >
  Activate for unified telemetry querying via TFQL. Covers all three
  signal types — metrics, logs, and traces — through a centralized
  query engine with specialized query builders per domain.
version: 1.0.0
author: agent
platforms: [linux, macos]
---

## Procedure

1. Query metrics
   ```
   python3 query_tfql.py --signal metrics --metric-name http_requests_total
   python3 query_tfql.py --signal metrics --metric-name cpu_usage --aggregation avg --interval 5m
   ```

2. Query logs
   ```
   python3 query_tfql.py --signal logs --query "ERROR AND timeout"
   python3 query_tfql.py --signal logs --severity ERROR --service payments-api
   ```

3. Query traces
   ```
   python3 query_tfql.py --signal traces --service-name payments-api
   python3 query_tfql.py --signal traces --trace-id <trace-id>
   ```

4. Discover available metrics and labels
   ```
   python3 query_tfql.py --signal metrics --action names
   python3 query_tfql.py --signal metrics --action labels --label-name service
   ```

5. Get trace summaries and services
   ```
   python3 query_tfql.py --signal traces --action summaries
   python3 query_tfql.py --signal traces --action services
   python3 query_tfql.py --signal traces --action operations
   ```

## Query Features

- **Metrics**: aggregation (AVG, SUM, MAX, MIN), interval, percentiles, label filtering
- **Logs**: full-text search, severity filtering, attribute filtering, severity distribution
- **Traces**: trace ID lookup, span filtering, duration filtering, service/operation discovery

## Specialized Query Builders

TFO routes queries through domain-specific builders:
- AgentsQueryBuilder, UptimeQueryBuilder, StatusPageQueryBuilder
- ServiceMapQueryBuilder, NetworkMapQueryBuilder
- KubernetesQueryBuilder, VMQueryBuilder

## TFO API Endpoints

- `POST /query/signals/metrics` — Query metrics
- `GET /query/signals/metrics/names` — Available metric names
- `GET /query/signals/metrics/labels/:labelName` — Label values
- `POST /query/signals/logs` — Query logs
- `POST /query/signals/logs/count-by-severity` — Severity distribution
- `POST /query/signals/traces` — Query traces
- `GET /query/signals/traces/:traceId` — Get trace by ID
- `POST /query/signals/traces/summaries` — Trace summaries
- `GET /query/signals/traces/services` — Service names
- `GET /query/signals/traces/operations` — Operation names

## Classification Rules

- Query returning no results for active services → WARNING
- High cardinality query timing out → OPTIMIZE
- Log query with too many results → NARROW FILTER

## Verification

- Query responses are well-formed
- Response normalizer handles all signal types
- Time-series data is continuous (no gaps)
