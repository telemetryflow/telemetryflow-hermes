# Technology Stack & Build System

## Core Technologies

- **Framework**: NestJS 11.x (Node.js framework with decorators and dependency injection)
- **Language**: TypeScript 5.9 with strict configuration
- **Package Manager**: pnpm 10.24.0 (preferred over npm/yarn)
- **Runtime**: Node.js 22+ (Alpine Linux in Docker)

## Database Stack

- **Primary Database**: PostgreSQL 16 (IAM data, user management)
- **Analytics Database**: ClickHouse (audit logs, metrics, traces)
- **ORM**: TypeORM 0.3 with migrations (no synchronize in production)
- **Connection**: Environment-based configuration with health checks

## Architecture Patterns

- **Domain-Driven Design (DDD)**: Clean architecture with domain/application/infrastructure/presentation layers
- **CQRS**: Command Query Responsibility Segregation with @nestjs/cqrs
- **Event-Driven**: Domain events with event processors
- **Dependency Injection**: NestJS IoC container with interface-based repositories

## Security & Authentication

- **Authentication**: JWT with Passport.js
- **Password Hashing**: Argon2 (preferred over bcrypt)
- **Authorization**: Role-based access control with guards and decorators
- **Secrets**: Cryptographically secure generation via scripts/generate-secrets.js

## Observability Stack

- **Logging**: Winston with multiple transports (Console, File, OTEL, ClickHouse)
- **Tracing**: OpenTelemetry with OTLP export
- **Metrics**: Prometheus with custom metrics
- **API Docs**: Swagger/OpenAPI at `/api` endpoint
- **Health Checks**: Built-in `/health` endpoint

## Testing Framework

- **Test Runner**: Jest with ts-jest transformer
- **Coverage**: 90% threshold for branches, functions, lines, statements
- **API Testing**: Newman (Postman CLI) for BDD scenarios
- **Test Types**: Unit tests (_.spec.ts), E2E tests (_.e2e.spec.ts)

## Common Commands

### Development

```bash
# Start development server with hot reload
pnpm dev

# Start with debugger
pnpm start:debug

# Build for production
pnpm build

# Start production server
pnpm start
```

### Database Operations

```bash
# Full database setup (migrations + seeds)
pnpm db:migrate:seed

# Run migrations only
pnpm db:migrate
pnpm db:migrate:postgres    # PostgreSQL only
pnpm db:migrate:clickhouse  # ClickHouse only

# Seed data
pnpm db:seed
pnpm db:seed:iam            # IAM data only
pnpm db:seed:clickhouse     # ClickHouse only

# Clean databases
pnpm db:cleanup

# Generate sample data (50 records)
pnpm db:generate-sample
```

### Testing

```bash
# Unit tests
pnpm test
pnpm test:watch
pnpm test:cov

# BDD API tests (Newman)
pnpm test:bdd
pnpm test:bdd:verbose
pnpm test:bdd:users         # Users module only
pnpm test:bdd:roles         # Roles module only
```

### Docker Operations

```bash
# Start all services
pnpm docker:up
docker-compose --profile all up -d

# Core services only
docker-compose --profile core up -d

# With monitoring
docker-compose --profile core --profile monitoring up -d

# Stop services
pnpm docker:down

# View logs
pnpm docker:logs
```

### Security & Secrets

```bash
# Generate JWT and session secrets
pnpm generate:secrets

# Bootstrap entire environment
pnpm bootstrap
bash scripts/bootstrap.sh --dev
```

### Code Quality

```bash
# Lint and fix
pnpm lint

# Clean build artifacts
pnpm clean
```

## Environment Configuration

- **Development**: `.env` file with defaults from `.env.example`
- **Production**: Environment variables or secrets management
- **Docker**: Environment variables passed through docker-compose.yml
- **Required Secrets**: JWT_SECRET, SESSION_SECRET (32+ characters)

## Build Configuration

- **TypeScript**: ES2021 target, CommonJS modules, decorators enabled
- **NestJS CLI**: Automatic compilation with hot reload
- **Docker**: Multi-stage build (builder + production)
- **Exclusions**: Tests, scripts, and development files excluded from production build

## Performance Considerations

- **Database**: Connection pooling, query optimization, proper indexing
- **Logging**: Structured JSON logging with sampling for high-volume environments
- **Caching**: Built-in cache service for frequently accessed data
- **Monitoring**: OpenTelemetry instrumentation for performance tracking
