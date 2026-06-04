---
name: tfql-natural-language
description: >
  Activate when user asks a question in natural language about
  observability data. Converts natural language to ClickHouse SQL
  via TelemetryFlow TFQL query engine.
version: 1.0.0
author: agent
platforms: [linux, macos]
---

## Procedure

1. Parse the natural language question for:
   - Time range (e.g., "last hour", "past 24 hours")
   - Service name (e.g., "payments-api", "auth-service")
   - Signal type (metrics, logs, traces, exemplars)
   - Aggregation (average, p95, count, rate)

2. Construct TFQL request
   ```bash
   curl -X POST "${TELEMETRYFLOW_API_URL}/api/v1/tfql/query" \
     -H "Authorization: Bearer ${TELEMETRYFLOW_API_KEY}" \
     -H "Content-Type: application/json" \
     -d '{
       "workspace_id": "<workspace_id>",
       "query": "<natural language question>",
       "format": "json"
     }'
   ```

3. If TFQL is unavailable, fall back to clickhouse-query-patterns skill
   and construct the SQL query manually using templates.

4. Parse response and present findings with:
   - Direct answer to the question
   - Supporting data points
   - Relevant time range and filters applied

## Example Queries

- "What is the p95 latency of payments-api in the last hour?"
- "How many errors did auth-service log today?"
- "Which service has the highest memory usage right now?"
- "Show me all traces slower than 500ms in the last 30 minutes"

## Pitfalls

- TFQL may not support all ClickHouse functions — fall back to raw SQL
- Always verify workspace_id is included in the request
- Natural language ambiguity: if unclear, ask for clarification
