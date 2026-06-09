# Development Patterns & LEGO Builder Guide

This document outlines the development patterns and modular architecture principles for TelemetryFlow Platform, based on the LEGO Builder methodology from the Platform.

## LEGO Builder Philosophy

TelemetryFlow Platform follows the **LEGO Builder** approach where each module is a self-contained "LEGO block" that can be discovered, loaded, and connected automatically.

### Core Principles

1. **Self-Contained**: Each module has everything it needs (domain, application, infrastructure, presentation)
2. **Discoverable**: System finds modules automatically via manifest
3. **Dependency-Aware**: Modules declare what they need, system loads in correct order
4. **Swappable**: Can enable/disable modules without breaking the system
5. **Isolated**: Modules don't directly import from other modules (use DI)

## Module Structure Pattern

### Complete LEGO Block Anatomy

```
src/modules/iam/                   # Example LEGO block
│
├── 🧩 iam.module.ts               # NestJS module definition
├── 🧩 module.manifest.ts          # LEGO instructions (future)
├── 📄 index.ts                    # Public API exports
├── 📄 README.md                   # Module documentation
│
├── 🎨 domain/                     # DOMAIN LAYER - Business Logic
│   ├── aggregates/                # Core business entities
│   │   ├── User.ts
│   │   ├── Role.ts
│   │   ├── Permission.ts
│   │   └── index.ts
│   ├── entities/                  # Domain entities
│   │   ├── MFASettings.ts
│   │   └── index.ts
│   ├── value-objects/             # Immutable concepts
│   │   ├── UserId.ts
│   │   ├── Email.ts
│   │   ├── RoleId.ts
│   │   └── index.ts
│   ├── events/                    # Domain events
│   │   ├── UserCreated.event.ts
│   │   ├── RoleAssigned.event.ts
│   │   └── index.ts
│   ├── repositories/              # Repository interfaces
│   │   ├── IUserRepository.ts
│   │   ├── IRoleRepository.ts
│   │   └── index.ts
│   ├── services/                  # Domain services
│   │   ├── PermissionService.ts
│   │   └── index.ts
│   └── index.ts
│
├── ⚙️ application/                # APPLICATION LAYER - Use Cases
│   ├── commands/                  # Write operations
│   │   ├── CreateUser.command.ts
│   │   ├── UpdateUser.command.ts
│   │   └── index.ts
│   ├── queries/                   # Read operations
│   │   ├── GetUser.query.ts
│   │   ├── ListUsers.query.ts
│   │   └── index.ts
│   ├── handlers/                  # CQRS handlers
│   │   ├── CreateUser.handler.ts
│   │   ├── GetUser.handler.ts
│   │   └── index.ts
│   ├── dto/                       # Application DTOs
│   │   ├── UserResponse.dto.ts
│   │   └── index.ts
│   └── index.ts
│
├── 🔌 infrastructure/             # INFRASTRUCTURE LAYER
│   ├── persistence/
│   │   ├── entities/              # TypeORM entities
│   │   │   ├── User.entity.ts
│   │   │   ├── Role.entity.ts
│   │   │   └── index.ts
│   │   ├── repositories/          # Repository implementations
│   │   │   ├── UserRepository.ts
│   │   │   ├── RoleRepository.ts
│   │   │   └── index.ts
│   │   ├── mappers/               # Domain ↔ Entity mappers
│   │   │   ├── UserMapper.ts
│   │   │   └── index.ts
│   │   ├── migrations/            # Database migrations
│   │   │   ├── 1704240000001-CreateUsersTable.ts
│   │   │   └── index.ts
│   │   ├── seeds/                 # Seed data
│   │   │   ├── 1704240000001-seed-iam-users.ts
│   │   │   └── index.ts
│   │   └── index.ts
│   ├── messaging/                 # Event processors
│   │   ├── IAMEventProcessor.ts
│   │   └── index.ts
│   └── index.ts
│
└── 🎛️ presentation/               # PRESENTATION LAYER - API
    ├── controllers/               # REST controllers
    │   ├── User.controller.ts
    │   ├── Role.controller.ts
    │   └── index.ts
    ├── dto/                       # Request/Response DTOs
    │   ├── CreateUserRequest.dto.ts
    │   ├── UserResponse.dto.ts
    │   └── index.ts
    ├── guards/                    # Route guards
    │   ├── PermissionGuard.ts
    │   └── index.ts
    ├── decorators/                # Custom decorators
    │   ├── RequirePermissions.ts
    │   └── index.ts
    └── index.ts
```

## Domain-Driven Design (DDD) Patterns

### 1. Aggregates

Aggregates are the main business entities that encapsulate business logic and maintain consistency.

```typescript
// domain/aggregates/User.ts
export class User extends AggregateRoot {
  private constructor(
    private readonly _id: UserId,
    private _email: Email,
    private _isActive: boolean,
    private _roles: Role[],
  ) {
    super();
  }

  // Factory method for creating new users
  static create(email: Email): User {
    const user = new User(UserId.generate(), email, true, []);

    // Emit domain event
    user.addDomainEvent(new UserCreatedEvent(user.id, user.email));
    return user;
  }

  // Factory method for reconstituting from persistence
  static reconstitute(
    id: UserId,
    email: Email,
    isActive: boolean,
    roles: Role[],
  ): User {
    return new User(id, email, isActive, roles);
  }

  // Business logic methods
  assignRole(role: Role): void {
    if (this._roles.some((r) => r.id.equals(role.id))) {
      throw new DomainError("User already has this role");
    }

    this._roles.push(role);
    this.addDomainEvent(new RoleAssignedEvent(this._id, role.id));
  }

  // Getters (no setters - encapsulation)
  get id(): UserId {
    return this._id;
  }
  get email(): Email {
    return this._email;
  }
  get isActive(): boolean {
    return this._isActive;
  }
  get roles(): readonly Role[] {
    return this._roles;
  }
}
```

### 2. Value Objects

Value objects are immutable concepts that have no identity.

```typescript
// domain/value-objects/Email.ts
export class Email extends ValueObject<string> {
  private constructor(value: string) {
    super(value);
  }

  static create(email: string): Email {
    if (!email || !this.isValidEmail(email)) {
      throw new DomainError("Invalid email format");
    }
    return new Email(email.toLowerCase());
  }

  private static isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  protected validate(value: string): void {
    // Validation is done in create method
  }
}
```

### 3. Domain Events

Domain events represent something important that happened in the domain.

```typescript
// domain/events/UserCreated.event.ts
export class UserCreatedEvent extends DomainEvent {
  constructor(
    public readonly userId: UserId,
    public readonly email: Email,
  ) {
    super();
  }
}
```

### 4. Repository Interfaces

Repository interfaces define how aggregates are persisted (domain layer doesn't know about databases).

```typescript
// domain/repositories/IUserRepository.ts
export interface IUserRepository {
  save(user: User): Promise<void>;
  findById(id: UserId): Promise<User | null>;
  findByEmail(email: Email): Promise<User | null>;
  findAll(): Promise<User[]>;
  delete(id: UserId): Promise<void>;
}
```

## CQRS Pattern Implementation

### Commands (Write Operations)

```typescript
// application/commands/CreateUser.command.ts
export class CreateUserCommand {
  constructor(
    public readonly email: string,
    public readonly organizationId: string,
  ) {}
}
```

### Queries (Read Operations)

```typescript
// application/queries/GetUser.query.ts
export class GetUserQuery {
  constructor(public readonly userId: string) {}
}
```

### Command Handlers

```typescript
// application/handlers/CreateUser.handler.ts
@CommandHandler(CreateUserCommand)
export class CreateUserHandler implements ICommandHandler<CreateUserCommand> {
  constructor(
    @Inject("IUserRepository")
    private readonly userRepository: IUserRepository,
    private readonly eventBus: EventBus,
  ) {}

  async execute(command: CreateUserCommand): Promise<void> {
    // 1. Create value objects
    const email = Email.create(command.email);

    // 2. Check business rules
    const existingUser = await this.userRepository.findByEmail(email);
    if (existingUser) {
      throw new DomainError("User with this email already exists");
    }

    // 3. Create aggregate
    const user = User.create(email);

    // 4. Save aggregate
    await this.userRepository.save(user);

    // 5. Publish domain events
    user.getUncommittedEvents().forEach((event) => {
      this.eventBus.publish(event);
    });
    user.markEventsAsCommitted();
  }
}
```

### Query Handlers

```typescript
// application/handlers/GetUser.handler.ts
@QueryHandler(GetUserQuery)
export class GetUserHandler implements IQueryHandler<GetUserQuery> {
  constructor(
    @Inject("IUserRepository")
    private readonly userRepository: IUserRepository,
  ) {}

  async execute(query: GetUserQuery): Promise<UserResponseDto> {
    const userId = UserId.create(query.userId);
    const user = await this.userRepository.findById(userId);

    if (!user) {
      throw new NotFoundException("User not found");
    }

    return UserResponseDto.fromDomain(user);
  }
}
```

## Infrastructure Layer Patterns

### Repository Implementation

```typescript
// infrastructure/persistence/repositories/UserRepository.ts
@Injectable()
export class UserRepository implements IUserRepository {
  constructor(
    @InjectRepository(UserEntity)
    private readonly userEntityRepository: Repository<UserEntity>,
    private readonly userMapper: UserMapper,
  ) {}

  async save(user: User): Promise<void> {
    const userEntity = this.userMapper.toEntity(user);
    await this.userEntityRepository.save(userEntity);
  }

  async findById(id: UserId): Promise<User | null> {
    const userEntity = await this.userEntityRepository.findOne({
      where: { id: id.value },
      relations: ["roles"],
    });

    return userEntity ? this.userMapper.toDomain(userEntity) : null;
  }

  async findByEmail(email: Email): Promise<User | null> {
    const userEntity = await this.userEntityRepository.findOne({
      where: { email: email.value },
      relations: ["roles"],
    });

    return userEntity ? this.userMapper.toDomain(userEntity) : null;
  }
}
```

### Domain-Entity Mapping

```typescript
// infrastructure/persistence/mappers/UserMapper.ts
@Injectable()
export class UserMapper {
  toDomain(entity: UserEntity): User {
    const roles =
      entity.roles?.map((roleEntity) =>
        Role.reconstitute(
          RoleId.create(roleEntity.id),
          roleEntity.name,
          roleEntity.permissions || [],
        ),
      ) || [];

    return User.reconstitute(
      UserId.create(entity.id),
      Email.create(entity.email),
      entity.isActive,
      roles,
    );
  }

  toEntity(domain: User): UserEntity {
    const entity = new UserEntity();
    entity.id = domain.id.value;
    entity.email = domain.email.value;
    entity.isActive = domain.isActive;
    // Note: roles are handled separately in the repository
    return entity;
  }
}
```

## Presentation Layer Patterns

### Controllers

```typescript
// presentation/controllers/User.controller.ts
@Controller("users")
@ApiTags("Users")
export class UserController {
  constructor(
    private readonly commandBus: CommandBus,
    private readonly queryBus: QueryBus,
  ) {}

  @Post()
  @ApiOperation({ summary: "Create a new user" })
  @ApiResponse({ status: 201, description: "User created successfully" })
  @RequirePermissions("users:create")
  async createUser(@Body() request: CreateUserRequestDto): Promise<void> {
    const command = new CreateUserCommand(
      request.email,
      request.organizationId,
    );
    await this.commandBus.execute(command);
  }

  @Get(":id")
  @ApiOperation({ summary: "Get user by ID" })
  @ApiResponse({ status: 200, type: UserResponseDto })
  @RequirePermissions("users:read")
  async getUser(@Param("id") id: string): Promise<UserResponseDto> {
    const query = new GetUserQuery(id);
    return await this.queryBus.execute(query);
  }
}
```

### DTOs with Validation

```typescript
// presentation/dto/CreateUserRequest.dto.ts
export class CreateUserRequestDto {
  @ApiProperty({ example: "user@example.com" })
  @IsEmail()
  @IsNotEmpty()
  email: string;

  @ApiProperty({ example: "org-123" })
  @IsString()
  @IsNotEmpty()
  organizationId: string;
}

// application/dto/UserResponse.dto.ts
export class UserResponseDto {
  @ApiProperty()
  id: string;

  @ApiProperty()
  email: string;

  @ApiProperty()
  isActive: boolean;

  @ApiProperty({ type: [RoleResponseDto] })
  roles: RoleResponseDto[];

  static fromDomain(user: User): UserResponseDto {
    return {
      id: user.id.value,
      email: user.email.value,
      isActive: user.isActive,
      roles: user.roles.map((role) => RoleResponseDto.fromDomain(role)),
    };
  }
}
```

## Module Configuration Pattern

### NestJS Module Setup

```typescript
// iam.module.ts
@Module({
  imports: [
    CqrsModule,
    TypeOrmModule.forFeature([
      UserEntity,
      RoleEntity,
      PermissionEntity,
      // ... other entities
    ]),
  ],
  controllers: [
    UserController,
    RoleController,
    PermissionController,
    // ... other controllers
  ],
  providers: [
    // Command Handlers
    CreateUserHandler,
    UpdateUserHandler,
    DeleteUserHandler,

    // Query Handlers
    GetUserHandler,
    ListUsersHandler,

    // Repositories (with DI tokens)
    { provide: "IUserRepository", useClass: UserRepository },
    { provide: "IRoleRepository", useClass: RoleRepository },

    // Mappers
    UserMapper,
    RoleMapper,

    // Services
    PermissionService,

    // Event Processors
    IAMEventProcessor,
  ],
  exports: [
    // Export repository tokens for other modules
    "IUserRepository",
    "IRoleRepository",
  ],
})
export class IAMModule {}
```

## Testing Patterns

### Unit Tests for Aggregates

```typescript
// domain/aggregates/__tests__/User.spec.ts
describe("User Aggregate", () => {
  describe("create", () => {
    it("should create a user with valid email", () => {
      // Arrange
      const email = Email.create("test@example.com");

      // Act
      const user = User.create(email);

      // Assert
      expect(user.email).toEqual(email);
      expect(user.isActive).toBe(true);
      expect(user.getUncommittedEvents()).toHaveLength(1);
      expect(user.getUncommittedEvents()[0]).toBeInstanceOf(UserCreatedEvent);
    });

    it("should throw error for invalid email", () => {
      // Act & Assert
      expect(() => Email.create("invalid-email")).toThrow(DomainError);
    });
  });

  describe("assignRole", () => {
    it("should assign role to user", () => {
      // Arrange
      const user = User.create(Email.create("test@example.com"));
      const role = Role.create("admin", []);

      // Act
      user.assignRole(role);

      // Assert
      expect(user.roles).toContain(role);
      expect(user.getUncommittedEvents()).toHaveLength(2); // UserCreated + RoleAssigned
    });
  });
});
```

### Integration Tests for Repositories

```typescript
// infrastructure/persistence/repositories/__tests__/UserRepository.integration.spec.ts
describe("UserRepository Integration", () => {
  let repository: UserRepository;
  let testingModule: TestingModule;

  beforeEach(async () => {
    testingModule = await Test.createTestingModule({
      imports: [
        TypeOrmModule.forRoot(testDatabaseConfig),
        TypeOrmModule.forFeature([UserEntity, RoleEntity]),
      ],
      providers: [UserRepository, UserMapper],
    }).compile();

    repository = testingModule.get<UserRepository>(UserRepository);
  });

  it("should save and retrieve user", async () => {
    // Arrange
    const user = User.create(Email.create("test@example.com"));

    // Act
    await repository.save(user);
    const retrievedUser = await repository.findById(user.id);

    // Assert
    expect(retrievedUser).toBeDefined();
    expect(retrievedUser!.email.value).toBe("test@example.com");
  });
});
```

## Error Handling Patterns

### Domain Errors

```typescript
// shared/domain/DomainError.ts
export class DomainError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "DomainError";
  }
}
```

### Application Errors

```typescript
// application/errors/UserNotFoundError.ts
export class UserNotFoundError extends Error {
  constructor(userId: string) {
    super(`User with ID ${userId} not found`);
    this.name = "UserNotFoundError";
  }
}
```

### Global Exception Filter

```typescript
// presentation/filters/GlobalExceptionFilter.ts
@Catch()
export class GlobalExceptionFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();

    if (exception instanceof DomainError) {
      response.status(400).json({
        statusCode: 400,
        message: exception.message,
        error: "Bad Request",
      });
    } else if (exception instanceof UserNotFoundError) {
      response.status(404).json({
        statusCode: 404,
        message: exception.message,
        error: "Not Found",
      });
    } else {
      // Handle other exceptions
      response.status(500).json({
        statusCode: 500,
        message: "Internal server error",
        error: "Internal Server Error",
      });
    }
  }
}
```

## Best Practices

### 1. Dependency Injection

- Use interface tokens for repositories: `'IUserRepository'`
- Inject interfaces, not implementations
- Use constructor injection consistently

### 2. Event Handling

- Always publish domain events after successful persistence
- Use event handlers for side effects (email notifications, etc.)
- Keep event handlers idempotent

### 3. Validation

- Domain validation in value objects and aggregates
- Input validation in DTOs using class-validator
- Business rule validation in command handlers

### 4. Error Handling

- Use domain-specific errors for business rule violations
- Use application-specific errors for use case failures
- Use HTTP-specific errors in controllers

### 5. Testing

- Unit test aggregates and value objects in isolation
- Integration test repositories with real database
- E2E test controllers with full application context

This development pattern guide ensures consistency with TelemetryFlow Platform's existing architecture while providing clear guidelines for implementing new features using DDD and CQRS patterns.
