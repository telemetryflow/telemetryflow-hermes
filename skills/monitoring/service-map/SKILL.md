---
name: service-map
description: >
  Activate for service dependency investigations. Auto-discovered from
  OpenTelemetry traces, Kubernetes service sync, and manual definition.
  Provides topology visualization, health scores, and trace-based metrics.
version: 1.0.0
author: agent
platforms: [linux, macos]
---

## Procedure

1. Get complete service map
   ```
   python3 check_service_map.py --resource map
   ```

2. List services with health scores
   ```
   python3 check_service_map.py --resource services
   python3 check_service_map.py --resource services --type MICROSERVICE
   ```

3. Get service dependencies
   ```
   python3 check_service_map.py --resource dependencies --service-id <id>
   ```

4. Check service health and metrics
   ```
   python3 check_service_map.py --resource health --service-id <id>
   python3 check_service_map.py --resource metrics --service-id <id>
   ```

5. View topology graph
   ```
   python3 check_service_map.py --resource topology --depth 3
   ```

## Service Types

- API, GATEWAY, DATABASE, MICROSERVICE, WORKER, EXTERNAL

## Service Health

- **score**: 0-100 composite health score
- **uptime**: percentage over time window
- **latency**: P50/P95/P99 response times
- **errorRate**: percentage of failed requests
- **requestRate**: requests per second

## Dependency Types

- HTTP, GRPC, TCP, HTTP_CLIENT, DATABASE, DATABASE_CONNECTION

## TFO API Endpoints

- `GET /monitoring/service-map` — Complete map (services + dependencies)
- `GET /monitoring/service-map/services` — List services
- `GET /monitoring/service-map/services/:id` — Service detail
- `GET /monitoring/service-map/services/:id/dependencies` — Dependencies
- `GET /monitoring/service-map/services/:id/health` — Health metrics
- `GET /monitoring/service-map/services/:id/metrics` — Trace-based metrics
- `GET /monitoring/service-map/topology` — Topology graph

## Classification Rules

- Service UNHEALTHY → CRITICAL
- Service DEGRADED with error rate > 10% → CRITICAL
- Dependency with latency > 2x baseline → WARNING
- External service DOWN → WARNING (external dependency)
- Health score < 50 → CRITICAL

## Auto-Discovery

Services are auto-discovered from:
1. **OTEL traces** — every 5 minutes, extracts service names and HTTP/gRPC dependencies
2. **K8s service sync** — every 2 minutes, syncs K8s services
3. **Infrastructure health probe** — every 30 seconds, checks infrastructure health

## Verification

- All services show HEALTHY status
- Dependency graph is complete (no orphan services)
- Health scores > 80 for all critical services
- No stale services (no traces for > 1 hour)
