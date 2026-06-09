# Naming Conventions

Based on TelemetryFlow Platform standards, this document defines consistent naming patterns across the TelemetryFlow Platform codebase.

## Core Principles

1. **Consistency**: Same pattern across all modules
2. **Clarity**: Name reveals purpose and layer
3. **TypeScript**: Follow TypeScript/NestJS conventions
4. **Searchability**: Easy to grep/find files
5. **No Mixing**: One convention per file type

## File Naming Conventions

### Domain Layer

| Type                     | Pattern                     | Example                 | ❌ Wrong                           |
| ------------------------ | --------------------------- | ----------------------- | ---------------------------------- |
| **Aggregate**            | `{entity}.aggregate.ts`     | `User.ts`, `Role.ts`    | ~~`user.aggregate.ts`~~            |
| **Value Object**         | `{Name}.ts`                 | `UserId.ts`, `Email.ts` | ~~`user-id.value-object.ts`~~      |
| **Domain Event**         | `{Entity}{Action}.event.ts` | `UserCreated.event.ts`  | ~~`user-created.event.ts`~~        |
| **Repository Interface** | `I{Entity}Repository.ts`    | `IUserRepository.ts`    | ~~`user.repository.interface.ts`~~ |

**Rules for TelemetryFlow Platform**:

- ✅ **PascalCase** for domain files (matches existing codebase)
- ✅ Use descriptive suffixes: `.event.ts` for events
- ✅ `I` prefix for repository interfaces
- ❌ NO kebab-case in domain layer (conflicts with existing code)

### Application Layer

| Type                | Pattern                       | Example                 | ❌ Wrong                     |
| ------------------- | ----------------------------- | ----------------------- | ---------------------------- |
| **Command**         | `{Action}{Entity}.command.ts` | `CreateUser.command.ts` | ~~`create-user.command.ts`~~ |
| **Query**           | `{Action}{Entity}.query.ts`   | `GetUser.query.ts`      | ~~`get-user.query.ts`~~      |
| **Command Handler** | `{Action}{Entity}.handler.ts` | `CreateUser.handler.ts` | ~~`CreateUserHandler.ts`~~   |
| **Query Handler**   | `{Action}{Entity}.handler.ts` | `GetUser.handler.ts`    | ~~`GetUserHandler.ts`~~      |
| **DTO**             | `{Entity}{Type}.dto.ts`       | `UserResponse.dto.ts`   | ~~`user-response.dto.ts`~~   |

**Rules**:

- ✅ **PascalCase** for file names (matches existing handlers)
- ✅ Action verbs: `Create`, `Update`, `Delete`, `Get`, `List`
- ✅ Suffixes: `.command`, `.query`, `.handler`, `.dto`

### Infrastructure Layer

| Type                | Pattern                        | Example                             | Current Example     |
| ------------------- | ------------------------------ | ----------------------------------- | ------------------- |
| **Entity**          | `{Entity}.entity.ts`           | `User.entity.ts`                    | ✅ Matches existing |
| **Repository Impl** | `{Entity}Repository.ts`        | `UserRepository.ts`                 | ✅ Matches existing |
| **Mapper**          | `{Entity}Mapper.ts`            | `UserMapper.ts`                     | ✅ Matches existing |
| **Migration**       | `{timestamp}-{Description}.ts` | `1704240000001-CreateUsersTable.ts` | ✅ Matches existing |

**Rules**:

- ✅ **PascalCase** for Entity/Repository/Mapper file names (TypeORM convention)
- ✅ Suffix `.entity.ts` for entities
- ✅ NO suffix for Repository/Mapper files
- ✅ Timestamp prefix for migrations

### Presentation Layer

| Type             | Pattern                          | Example                    | Current Example     |
| ---------------- | -------------------------------- | -------------------------- | ------------------- |
| **Controller**   | `{Entity}.controller.ts`         | `User.controller.ts`       | ✅ Matches existing |
| **Request DTO**  | `{Action}{Entity}Request.dto.ts` | `CreateUserRequest.dto.ts` | ✅ Matches existing |
| **Response DTO** | `{Entity}Response.dto.ts`        | `UserResponse.dto.ts`      | ✅ Matches existing |

**Rules**:

- ✅ **PascalCase** for file names (matches existing controllers)
- ✅ **Singular** for controller file names (e.g., `User.controller.ts`)
- ✅ Suffixes: `.controller`, `.dto`

### Tests

| Type                 | Pattern                         | Example                              | ❌ Wrong                  |
| -------------------- | ------------------------------- | ------------------------------------ | ------------------------- |
| **Unit Test**        | `{Subject}.spec.ts`             | `User.spec.ts`                       | ~~`UserTest.ts`~~         |
| **Integration Test** | `{Subject}.integration.spec.ts` | `UserRepository.integration.spec.ts` | ~~`user-integration.ts`~~ |
| **E2E Test**         | `{Controller}.e2e.spec.ts`      | `User.controller.e2e.spec.ts`        | ~~`user.e2e.ts`~~         |

## Class/Interface Naming

### TypeScript Classes

| Type             | Pattern                   | Example                      |
| ---------------- | ------------------------- | ---------------------------- |
| **Aggregate**    | `{Entity}`                | `User`, `Role`, `Permission` |
| **Value Object** | `{Name}`                  | `UserId`, `Email`, `RoleId`  |
| **Domain Event** | `{Entity}{Action}Event`   | `UserCreatedEvent`           |
| **Command**      | `{Action}{Entity}Command` | `CreateUserCommand`          |
| **Query**        | `{Action}{Entity}Query`   | `GetUserQuery`               |
| **Handler**      | `{Action}{Entity}Handler` | `CreateUserHandler`          |
| **DTO**          | `{Entity}{Type}Dto`       | `UserResponseDto`            |
| **Entity**       | `{Entity}Entity`          | `UserEntity`                 |
| **Repository**   | `{Entity}Repository`      | `UserRepository`             |
| **Controller**   | `{Entity}Controller`      | `UserController`             |

### Interfaces

| Type                     | Pattern               | Example                |
| ------------------------ | --------------------- | ---------------------- |
| **Repository Interface** | `I{Entity}Repository` | `IUserRepository`      |
| **Service Interface**    | `I{Name}Service`      | `INotificationService` |

## Database Naming

### Table Names

- ✅ **snake_case** for table names: `users`, `user_roles`, `role_permissions`
- ✅ **Plural** for entity tables: `users`, `roles`, `permissions`
- ✅ **Singular_singular** for junction tables: `user_role`, `role_permission`

### Column Names

- ✅ **snake_case** for column names: `user_id`, `created_at`, `updated_at`
- ✅ **Consistent** timestamps: `created_at`, `updated_at`, `deleted_at`
- ✅ **Foreign keys**: `{entity}_id` (e.g., `user_id`, `organization_id`)

### Migration Names

- ✅ **Timestamp-Description**: `1704240000001-CreateUsersTable.ts`
- ✅ **PascalCase** description: `CreateUsersTable`, `AddIndexToUsers`
- ✅ **Descriptive** actions: `Create`, `Add`, `Drop`, `Alter`

### Seed Names

- ✅ **Timestamp-seed-module-entity**: `1704240000001-seed-iam-roles-permissions.ts`
- ✅ **kebab-case** for module/entity: `iam-roles`, `auth-users`

## Module Structure Naming

### Module Files

- ✅ **Module**: `iam.module.ts` (matches existing)
- ✅ **Manifest**: `module.manifest.ts` (for future plugin system)
- ✅ **Index**: `index.ts` (barrel exports)

### Folder Structure

```
src/modules/iam/
├── domain/                 # Business logic
│   ├── aggregates/         # User.ts, Role.ts
│   ├── entities/           # MFASettings.ts
│   ├── value-objects/      # UserId.ts, Email.ts
│   ├── events/             # UserCreated.event.ts
│   ├── repositories/       # IUserRepository.ts
│   └── services/           # PermissionService.ts
├── application/            # Use cases
│   ├── commands/           # CreateUser.command.ts
│   ├── queries/            # GetUser.query.ts
│   ├── handlers/           # CreateUser.handler.ts
│   └── dto/                # UserResponse.dto.ts
├── infrastructure/         # Technical implementation
│   ├── persistence/
│   │   ├── entities/       # User.entity.ts
│   │   ├── repositories/   # UserRepository.ts
│   │   ├── mappers/        # UserMapper.ts
│   │   ├── migrations/     # 001-CreateUsersTable.ts
│   │   └── seeds/          # 001-seed-iam-users.ts
│   ├── messaging/          # IAMEventProcessor.ts
│   └── processors/         # iam-event.processor.ts
└── presentation/           # API layer
    ├── controllers/        # User.controller.ts
    ├── dto/                # CreateUserRequest.dto.ts
    ├── guards/             # PermissionGuard.ts
    └── decorators/         # RequirePermissions.ts
```

## Environment Variables

### Naming Pattern

- ✅ **SCREAMING_SNAKE_CASE**: `DATABASE_HOST`, `JWT_SECRET`
- ✅ **Descriptive prefixes**: `POSTGRES_`, `CLICKHOUSE_`, `OTEL_`
- ✅ **Consistent suffixes**: `_HOST`, `_PORT`, `_DB`, `_USERNAME`, `_PASSWORD`

### Examples

```bash
# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=telemetryflow_db
POSTGRES_USERNAME=postgres
POSTGRES_PASSWORD=telemetryflow123

# ClickHouse
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=8123
CLICKHOUSE_DB=telemetryflow_db

# Authentication
JWT_SECRET=your-jwt-secret-min-32-chars
JWT_EXPIRES_IN=24h
SESSION_SECRET=your-session-secret-min-32-chars

# OpenTelemetry
OTEL_ENABLED=true
OTEL_SERVICE_NAME=telemetryflow-platform
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
```

## API Naming

### Endpoint Patterns

- ✅ **REST conventions**: `/api/users`, `/api/roles`, `/api/permissions`
- ✅ **Plural resources**: `/users` not `/user`
- ✅ **kebab-case** for multi-word resources: `/user-roles`, `/role-permissions`
- ✅ **Versioning**: `/api/v1/users` (future consideration)

### HTTP Methods

- ✅ **GET** `/users` - List users
- ✅ **GET** `/users/:id` - Get specific user
- ✅ **POST** `/users` - Create user
- ✅ **PUT** `/users/:id` - Update user (full)
- ✅ **PATCH** `/users/:id` - Update user (partial)
- ✅ **DELETE** `/users/:id` - Delete user

## Validation Checklist

Before committing code, verify:

### File Names

- [ ] All files follow established patterns in existing codebase
- [ ] Entity files end with `.entity.ts`
- [ ] Handler files end with `.handler.ts`
- [ ] Controller files end with `.controller.ts`
- [ ] No duplicate files with different naming conventions

### Class Names

- [ ] All classes use **PascalCase**
- [ ] Repository interfaces use `I` prefix
- [ ] Commands end with `Command`
- [ ] Queries end with `Query`
- [ ] Handlers end with `Handler`
- [ ] DTOs end with `Dto`
- [ ] Events end with `Event`

### Database Names

- [ ] Table names use **snake_case** and are **plural**
- [ ] Column names use **snake_case**
- [ ] Foreign keys follow `{entity}_id` pattern
- [ ] Migration files have timestamp prefix

### Import Statements

- [ ] Relative imports use correct casing
- [ ] No circular dependencies
- [ ] Consistent import ordering

## Quick Reference

### Current TelemetryFlow Platform Patterns

```
Domain Layer:
  ✅ User.ts (aggregate)
  ✅ UserId.ts (value object)
  ✅ UserCreated.event.ts (domain event)
  ✅ IUserRepository.ts (repository interface)

Application Layer:
  ✅ CreateUser.command.ts
  ✅ GetUser.query.ts
  ✅ CreateUser.handler.ts
  ✅ UserResponse.dto.ts

Infrastructure Layer:
  ✅ User.entity.ts
  ✅ UserRepository.ts
  ✅ UserMapper.ts
  ✅ 1704240000001-CreateUsersTable.ts

Presentation Layer:
  ✅ User.controller.ts
  ✅ CreateUserRequest.dto.ts

Tests:
  ✅ User.spec.ts
  ✅ UserRepository.integration.spec.ts
  ✅ User.controller.e2e.spec.ts
```

This naming convention document ensures consistency with the existing TelemetryFlow Platform codebase while providing clear guidelines for future development.
