# Tech Stack

## Monorepo

- **Build orchestration**: Turborepo (`turbo.json`) with pnpm workspaces
- **Package manager**: pnpm (root uses pnpm@10, frontend uses pnpm@9)
- **Workspaces**: `@telemetryflow/backend`, `@telemetryflow/viz`

## Backend (`backend/`)

- **Runtime**: Node.js 18+
- **Framework**: NestJS 11.x
- **Language**: TypeScript 5.9
- **ORM**: TypeORM 0.3 (PostgreSQL via `pg`)
- **Databases**: PostgreSQL 16 (IAM/relational data), ClickHouse (audit logs, telemetry)
- **Auth**: Passport.js + JWT (`@nestjs/passport`, `@nestjs/jwt`), Argon2 password hashing
- **Architecture**: DDD + CQRS (`@nestjs/cqrs`) — Domain / Application / Infrastructure / Presentation layers
- **Queue**: BullMQ + Redis
- **Observability**: OpenTelemetry SDK (traces, metrics, logs), Winston logger
- **Validation**: `class-validator` + `class-transformer`
- **API Docs**: Swagger/OpenAPI (`@nestjs/swagger`)
- **Testing**: Jest + `ts-jest`, `fast-check` (property-based), Supertest (e2e)

## Frontend (`frontend/`)

- **Framework**: Vue 3.5+ (Composition API, `<script setup>`)
- **Language**: TypeScript 5.7
- **Build tool**: Vite 6
- **State management**: Pinia
- **UI library**: Naive UI
- **Charts**: ECharts + vue-echarts
- **HTTP client**: Axios (with JWT interceptor)
- **Router**: Vue Router 4
- **CSS**: SCSS + UnoCSS (utility-first)
- **Icons**: Iconify + @vicons/ionicons5
- **Testing**: Vitest + `@vue/test-utils` + `fast-check` (property-based), happy-dom environment
- **Auto-imports**: `unplugin-auto-import` (vue, vue-router, pinia, naive-ui composables), `unplugin-vue-components`

## Common Commands

```bash
# Install all dependencies
pnpm install

# Development (both backend + frontend via Turborepo)
pnpm dev
pnpm dev:backend
pnpm dev:frontend

# Build
pnpm build
pnpm build:backend
pnpm build:frontend

# Tests
pnpm test                        # Jest (backend unit tests)
pnpm test:cov                    # Jest with coverage
pnpm test:bdd                    # BDD API tests via Newman/Postman
cd frontend && pnpm test         # Vitest (frontend, single run)
cd frontend && pnpm test:watch   # Vitest watch mode

# Linting
pnpm lint
pnpm lint:fix

# Database
pnpm db:migrate                  # Run all migrations (Postgres + ClickHouse)
pnpm db:seed                     # Seed all data
pnpm db:fresh                    # Full reset (drop + migrate + seed)
pnpm db:migrate:postgres
pnpm db:migrate:clickhouse

# Docker
pnpm docker:up                   # docker-compose up -d
pnpm docker:down
docker-compose --profile all up -d   # All services including frontend

# Secrets
pnpm generate:secrets

# Makefile shortcuts (recommended for CI)
make dev
make test
make build
make ci-pipeline
```

## Environment Variables

All frontend env vars are prefixed `TELEMETRYFLOW_`. Key ones:

| Variable                    | Purpose                                                    |
| --------------------------- | ---------------------------------------------------------- |
| `TELEMETRYFLOW_IAM_API_URL` | NestJS backend URL (default: `http://localhost:3000`)      |
| `TELEMETRYFLOW_API_URL`     | OTEL Collector HTTP URL (default: `http://localhost:4318`) |
| `TELEMETRYFLOW_USE_MOCK`    | Enable mock API server in dev                              |
| `TELEMETRYFLOW_WS_URL`      | WebSocket URL                                              |

Backend env vars follow standard NestJS conventions (see `.env.example`).
