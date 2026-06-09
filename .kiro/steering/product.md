# TelemetryFlow Platform

TelemetryFlow Platform is a full-stack, production-ready observability platform (Community Enterprise Observability Platform — CEOP). It combines:

- A **NestJS backend** providing IAM (Identity & Access Management), authentication, telemetry ingestion, and API services
- A **Vue 3 frontend** (TelemetryFlow-Viz) for visualization dashboards, IAM management, and observability UIs

## Core Capabilities

- **5-Tier RBAC**: Super Admin → Administrator → Developer → Viewer → Demo
- **Multi-tenancy**: Tenant → Organization → Workspace hierarchy
- **Telemetry Ingestion**: OTLP-compliant collector supporting metrics, logs, and traces (v1 and v2 endpoints)
- **IAM Management**: Full CRUD for users, roles, permissions, groups, tenants, organizations, workspaces, regions
- **Observability Dashboards**: Metrics, logs, traces, Kubernetes, service maps, uptime, alerting
- **Audit Logging**: ClickHouse-backed audit trail
- **LLM Integration**: AI-assisted analysis across telemetry domains

## White-label Support

The platform supports full white-labeling via environment variables (`TELEMETRYFLOW_BRAND_*`, `TELEMETRYFLOW_LOGO_*`, `TELEMETRYFLOW_THEME_*`).

## API Base

- Backend REST API: `http://localhost:3000` — prefix `/api/v2/`
- OTEL Collector HTTP: `http://localhost:4318` — `/v1/` and `/v2/` endpoints
- Frontend dev server: `http://localhost:3100` (proxies `/api/v2` → backend, `/v1` → collector)
- Swagger UI: `http://localhost:3000/api`
