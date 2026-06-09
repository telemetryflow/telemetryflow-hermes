# TelemetryFlow Platform Product Overview

TelemetryFlow Platform is a monolith, production-ready Identity and Access Management (IAM) service extracted from the larger TelemetryFlow Platform. It provides complete identity and access management with enterprise-grade security features.

## Core Features

- **5-Tier RBAC System**: Super Admin, Administrator, Developer, Viewer, Demo roles with hierarchical permissions
- **Multi-tenant Architecture**: Tenant → Organization → Workspace hierarchy for data isolation
- **Domain-Driven Design**: Clean architecture with DDD patterns and CQRS implementation
- **Enterprise Security**: JWT authentication, Argon2 password hashing, role-based access control
- **Observability**: OpenTelemetry tracing, Winston logging, Swagger API documentation
- **Audit Logging**: Complete audit trail stored in ClickHouse for compliance

## Architecture

The system follows Domain-Driven Design (DDD) with Clean Architecture principles:
- **Domain Layer**: 8 aggregates, 10 value objects, domain services
- **Application Layer**: CQRS with 33 commands and 18 queries
- **Infrastructure Layer**: TypeORM repositories, event processors
- **Presentation Layer**: 9 REST controllers with comprehensive API

## Technology Stack

- **Backend**: NestJS 11.x with TypeScript 5.9
- **Database**: PostgreSQL 16 (IAM data) + ClickHouse (audit logs)
- **Authentication**: JWT with Passport
- **Observability**: OpenTelemetry, Winston, Prometheus, Grafana
- **Testing**: Jest with 90%+ coverage requirements

## Default Users

The system comes with pre-configured users for each RBAC tier:
- Super Administrator: `superadmin.telemetryflow@telemetryflow.id`
- Administrator: `administrator.telemetryflow@telemetryflow.id`
- Developer: `developer.telemetryflow@telemetryflow.id`
- Viewer: `viewer.telemetryflow@telemetryflow.id`
- Demo: `demo.telemetryflow@telemetryflow.id`

All default passwords follow the pattern: `{Role}@123456` (change in production).