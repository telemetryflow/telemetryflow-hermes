# Project Structure & Organization

## Root Directory Structure

```
telemetryflow-backend/
├── src/                    # Source code (TypeScript)
├── config/                 # Service configurations (ClickHouse, PostgreSQL, OTEL, etc.)
├── docs/                   # Documentation and guides
├── scripts/                # Utility scripts (bootstrap, database, secrets)
├── coverage/               # Test coverage reports
├── logs/                   # Application logs (development)
├── dist/                   # Compiled JavaScript (production build)
└── node_modules/           # Dependencies (managed by pnpm)
```

## Source Code Architecture (src/)

The codebase follows Domain-Driven Design (DDD) with Clean Architecture:

```
src/
├── main.ts                 # Application entry point with OpenTelemetry bootstrap
├── app.module.ts           # Root NestJS module with global configuration
├── app.controller.ts       # Root controller (basic endpoints)
│
├── shared/                 # Shared domain primitives
│   ├── domain/             # Base classes for DDD
│   │   ├── Entity.ts       # Base entity class
│   │   ├── ValueObject.ts  # Base value object class
│   │   ├── AggregateRoot.ts # Base aggregate root
│   │   └── DomainEvent.ts  # Base domain event
│   └── clickhouse/         # Shared ClickHouse service
│
├── logger/                 # Winston logging module
│   ├── config/             # Logger configuration
│   ├── transports/         # Custom transports (ClickHouse, etc.)
│   ├── middleware/         # Request context middleware
│   ├── decorators/         # @Log() decorator
│   └── logger.service.ts   # Main logger service
│
├── health/                 # Health check module
├── otel/                   # OpenTelemetry configuration
├── database/               # Database configuration and migrations
│   ├── config/             # Database connection config
│   ├── postgres/           # PostgreSQL migrations and seeds
│   ├── clickhouse/         # ClickHouse migrations and seeds
│   └── typeorm.config.ts   # TypeORM configuration
│
└── modules/                # Business modules
    ├── audit/              # Audit logging module
    ├── auth/               # Authentication guards and decorators
    ├── cache/              # Caching service
    └── iam/                # Identity and Access Management (main module)
```

## IAM Module Structure (DDD Implementation)

The IAM module follows strict DDD layering:

```
src/modules/iam/
├── domain/                 # Business logic layer
│   ├── aggregates/         # Domain aggregates (User, Role, Permission, etc.)
│   ├── entities/           # Domain entities (MFASettings, UserProfile)
│   ├── value-objects/      # Value objects (UserId, Email, RoleId)
│   ├── events/             # Domain events (UserCreated, RoleAssigned)
│   ├── repositories/       # Repository interfaces
│   └── services/           # Domain services
│
├── application/            # Use cases layer (CQRS)
│   ├── commands/           # Write operations (33 commands)
│   ├── queries/            # Read operations (18 queries)
│   ├── handlers/           # Command/Query handlers (51 total)
│   └── dto/                # Application DTOs
│
├── infrastructure/         # Technical implementation
│   ├── persistence/        # TypeORM entities and repositories
│   │   ├── entities/       # Database entities (*.entity.ts)
│   │   └── repositories/   # Repository implementations
│   ├── messaging/          # Event processors
│   └── processors/         # Background job processors
│
├── presentation/           # API layer
│   ├── controllers/        # REST controllers (9 controllers)
│   ├── dto/                # Request/Response DTOs
│   ├── guards/             # Authorization guards
│   └── decorators/         # Custom decorators
│
├── __tests__/              # Module-specific tests
├── docs/                   # Module documentation
└── iam.module.ts           # NestJS module configuration
```

## Configuration Structure (config/)

Service configurations are organized by technology:

```
config/
├── clickhouse/             # ClickHouse configuration
│   ├── config.xml          # Server settings
│   ├── users.xml           # User accounts
│   └── migrations/         # Schema migrations
├── postgresql/             # PostgreSQL configuration
│   └── postgresql.conf     # Server settings
├── otel/                   # OpenTelemetry Collector
│   ├── otel-collector-config.yaml
│   └── examples/           # Configuration examples
├── prometheus/             # Metrics collection
│   └── prometheus.yml
└── grafana/                # Dashboards and datasources
    ├── dashboards/
    └── provisioning/
```

## Naming Conventions

### Files and Directories

- **Modules**: PascalCase (e.g., `IAMModule`, `LoggerModule`)
- **Controllers**: `{Entity}.controller.ts` (e.g., `User.controller.ts`)
- **Services**: `{Entity}.service.ts` (e.g., `logger.service.ts`)
- **Entities**: `{Entity}.entity.ts` or `{Entity}Entity.ts`
- **Repositories**: `{Entity}Repository.ts`
- **Handlers**: `{Action}{Entity}.handler.ts` (e.g., `CreateUser.handler.ts`)
- **DTOs**: `{Action}{Entity}.dto.ts` or descriptive names
- **Tests**: `{Entity}.spec.ts` or `{Entity}.e2e.spec.ts`

### Code Conventions

- **Interfaces**: Prefix with `I` (e.g., `IUserRepository`)
- **Domain Events**: Suffix with `Event` (e.g., `UserCreatedEvent`)
- **Value Objects**: Descriptive names (e.g., `UserId`, `Email`)
- **Commands**: Action-based (e.g., `CreateUserCommand`)
- **Queries**: Query-based (e.g., `GetUserQuery`)

## Database Structure

### PostgreSQL (IAM Data)

- **Migrations**: `src/database/postgres/migrations/`
- **Seeds**: `src/database/postgres/seeds/`
- **Naming**: Timestamp prefix (e.g., `1704240000001-CreateUsersTable.ts`)

### ClickHouse (Analytics)

- **Migrations**: `src/database/clickhouse/migrations/`
- **Seeds**: `src/database/clickhouse/seeds/`
- **Tables**: `audit_logs`, `logs`, `metrics`, `traces`

## Testing Structure

### Unit Tests

- **Location**: Alongside source files (`*.spec.ts`)
- **Coverage**: 90% threshold for all metrics
- **Mocking**: Jest mocks for external dependencies

### Integration Tests

- **Location**: `__tests__/` directories within modules
- **Naming**: `{Entity}.e2e.spec.ts`
- **Database**: Test database with cleanup

### API Tests (BDD)

- **Location**: `docs/postman/`
- **Format**: Postman collections with Newman runner
- **Scenarios**: 33 BDD test scenarios with Given-When-Then

## Documentation Structure

```
docs/
├── references/             # Technical references and guides
├── postman/                # API testing collections
├── winston-logger/         # Logger documentation
├── dependabot/             # Dependency management
└── assets/                 # Images and diagrams
```

## Import Path Conventions

- **Relative imports**: For files within the same module
- **Absolute imports**: From `src/` root for cross-module dependencies
- **Barrel exports**: Use `index.ts` files for clean imports
- **Interface imports**: Always import interfaces, not implementations

## Module Dependencies

- **Shared modules**: Can be imported by any module
- **Domain layer**: No dependencies on other layers
- **Application layer**: Depends only on domain
- **Infrastructure layer**: Implements domain interfaces
- **Presentation layer**: Depends on application layer

## Environment-Specific Files

- **Development**: `.env` (local configuration)
- **Production**: Environment variables or secrets management
- **Docker**: `docker-compose.yml` with profiles
- **CI/CD**: GitHub Actions workflows in `.github/`
