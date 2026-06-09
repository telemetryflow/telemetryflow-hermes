# Project Structure

## Root Layout

```
telemetryflow-platform-monolith/
├── backend/          # NestJS backend (@telemetryflow/backend)
├── frontend/         # Vue 3 frontend (@telemetryflow/viz)
├── config/           # Infrastructure configs (nginx, clickhouse, otel, postgres, certbot)
├── docs/             # Architecture docs, API docs, Postman collections, guides
├── scripts/          # Dev/CI shell scripts and utilities
├── _infra/           # Helm charts, Ansible playbooks, ingress configs
├── .kiro/            # Kiro specs and steering files
├── turbo.json        # Turborepo task pipeline
├── pnpm-workspace.yaml
└── Makefile          # Unified dev/CI commands
```

## Backend (`backend/src/`)

```
backend/src/
├── main.ts                  # App entry point (bootstraps NestJS + OTEL)
├── app.module.ts            # Root module
├── shared/
│   ├── domain/              # Base classes: Entity, ValueObject, AggregateRoot, DomainEvent
│   ├── dto/                 # Shared DTOs (pagination, etc.)
│   ├── errors/              # Shared error types
│   ├── filters/             # Global exception filters
│   ├── cache/               # Cache utilities
│   └── clickhouse/          # Shared ClickHouse client
├── database/
│   ├── postgres/            # TypeORM config, migrations, seeds, migration-runner
│   └── clickhouse/          # ClickHouse migrations, seeds, migration-runner
├── logger/                  # Winston logger module with OTEL transport
├── otel/                    # OpenTelemetry tracing setup
├── health/                  # Health check endpoint
└── modules/
    ├── auth/                # JWT auth (login, refresh, logout, me)
    ├── iam/                 # IAM module — full DDD/CQRS (see below)
    ├── audit/               # Audit logging (ClickHouse)
    ├── cache/               # Caching layer
    ├── telemetry/           # Telemetry ingestion/query
    ├── monitoring/          # Uptime monitoring
    ├── alerting/            # Alert rules and notifications
    ├── dashboard/           # Dashboard management
    ├── query/               # Query engine (TFQL)
    ├── reporting/           # Reports
    ├── notification/        # Notification channels
    ├── api-keys/            # API key management
    ├── sso/                 # SSO providers
    ├── subscription/        # Subscription management
    ├── retention/           # Data retention policies
    ├── tenancy/             # Tenancy management
    └── llm/                 # LLM/AI integration
```

### IAM Module DDD Structure (canonical pattern for all modules)

```
modules/iam/
├── domain/
│   ├── aggregates/          # User, Role, Permission, Tenant, Organization, Workspace, Group, Region
│   ├── entities/            # MFASettings, UserProfile
│   ├── value-objects/       # UserId, Email, RoleId, etc.
│   ├── events/              # Domain events (UserCreated, RoleAssigned, etc.)
│   ├── repositories/        # Repository interfaces (ports)
│   └── services/            # Domain services
├── application/
│   ├── commands/            # Write operation definitions
│   ├── queries/             # Read operation definitions
│   ├── handlers/            # Command + Query handlers
│   └── dto/                 # Application-layer DTOs
├── infrastructure/
│   ├── persistence/         # TypeORM entities + repository implementations
│   └── messaging/           # Event processors
└── presentation/
    ├── controllers/         # REST controllers
    ├── dto/                 # Request/Response DTOs (with Swagger decorators)
    ├── guards/              # Authorization guards
    └── decorators/          # Custom metadata decorators
```

Tests live in `modules/iam/__tests__/` — unit tests named `<Entity>.spec.ts`, controller tests `<Entity>.controller.spec.ts`.

## Frontend (`frontend/src/`)

```
frontend/src/
├── api/              # Axios API clients (one file per domain: auth.ts, iam.ts, users.ts, etc.)
├── components/       # Reusable Vue components (auth/, charts/, common/, dashboard/, etc.)
├── composables/      # Vue composables (useXxx.ts pattern)
├── config/           # App config (collector.ts, theme.ts, whitelabel.ts)
├── constants/        # Static registries (graph-registry, datatable-registry, stat-panel-registry)
├── directives/       # Custom Vue directives (v-permission)
├── layouts/          # App shell (MainLayout, SideNav, TopBar)
├── mocks/            # Mock data for development (TELEMETRYFLOW_USE_MOCK=true)
├── router/           # Vue Router (routes.ts + guards)
├── store/            # Pinia stores (auth.ts, metrics.ts, logs.ts, traces.ts, etc.)
├── streaming/        # WebSocket + SSE streaming handlers
├── styles/           # SCSS global styles and variables
├── types/            # TypeScript type definitions (one file per domain)
├── utils/            # Pure utility functions
└── views/            # Page-level Vue components organized by feature
    ├── auth/         # Login page
    ├── iam/          # IAM management (users, roles, permissions, tenants, etc.)
    ├── telemetry/    # Metrics, logs, traces views
    ├── dashboards/   # Dashboard views
    ├── alerts/       # Alerting views
    ├── monitoring/   # Uptime monitoring
    └── ...
```

## Key Conventions

- **Path alias**: `@/` maps to `frontend/src/`
- **API clients**: Each domain has its own file in `src/api/`. IAM calls use JWT bearer token via Axios interceptor in `src/api/iam.ts`.
- **Composables**: Named `useXxx.ts`. Mock variants named `useXxx.mock.ts`.
- **Stores**: One Pinia store per domain in `src/store/`.
- **Tests (backend)**: Jest, co-located in `__tests__/` within the module. Property-based tests use `fast-check`.
- **Tests (frontend)**: Vitest, files named `*.spec.ts` or `*.test.ts` inside `__tests__/` subdirectories.
- **Migrations**: Postgres migrations in `backend/src/database/postgres/`, ClickHouse in `backend/src/database/clickhouse/`.
- **Specs**: Kiro specs live in `.kiro/specs/{feature-name}/` with `requirements.md`, `design.md`, `tasks.md`.
