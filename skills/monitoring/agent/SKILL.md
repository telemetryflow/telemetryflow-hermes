---
name: agent-monitoring
description: >
  Activate for TFO Agent investigations. Covers agent registration,
  health checks, system metrics (CPU, memory, disk, network), version
  tracking, and agent lifecycle management. Agents use API key auth
  (M2M) for heartbeat and registration.
version: 1.0.0
author: agent
platforms: [linux, macos]
---

## Procedure

1. List all agents and their status
   ```
   python3 check_agent.py --resource list
   python3 check_agent.py --resource list --status offline
   ```

2. Get agent statistics
   ```
   python3 check_agent.py --resource stats
   ```

3. Check individual agent health
   ```
   python3 check_agent.py --resource get --agent-id <id>
   python3 check_agent.py --resource health --agent-id <id>
   ```

4. Analyze agent metrics
   - System info: hostname, OS, CPU cores, memory
   - Response time: heartbeat round-trip latency
   - Raw metrics: detailed telemetry data

## Agent Properties

- **Type**: Infrastructure, Kubernetes, DB, Custom
- **Auth**: API Key (TfoApiKeyGuard) for M2M operations
- **Health**: tracked via heartbeat with metrics payload
- **Labels/Config**: agent-specific configuration

## TFO API Endpoints

- `GET /monitoring/agents` — List agents (filter by org, type, status)
- `GET /monitoring/agents/stats` — Aggregated statistics
- `GET /monitoring/agents/:id` — Get agent detail
- `GET /monitoring/agents/:id/health` — Health history
- `POST /monitoring/agents` — Register (API key auth)
- `POST /monitoring/agents/:id/heartbeat` — Heartbeat (API key auth)

## Classification Rules

- Agent offline > 10 min → CRITICAL
- Agent version mismatch across fleet → WARNING
- Heartbeat response time > 5s → WARNING
- Agent with repeated health failures → CRITICAL
- All agents in one region offline → CRITICAL

## Pitfalls

- Agents use API key auth (not JWT) — don't confuse auth models
- Health history is time-series in ClickHouse — use time ranges
- Agent type determines what sub-modules are active

## Verification

- All agents reporting healthy
- No version drift across agent fleet
- Response times within normal range
- Last heartbeat within expected interval
