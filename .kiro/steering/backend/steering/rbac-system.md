# 5-Tier RBAC System Implementation Guide

This document provides comprehensive guidance for implementing and working with TelemetryFlow Platform's 5-tier Role-Based Access Control (RBAC) system.

## System Overview

TelemetryFlow Platform implements a **5-tier RBAC system** with hierarchical permissions and organizational scoping:

1. **Tier 1: Super Administrator** - Global platform management
2. **Tier 2: Administrator** - Organization-scoped management
3. **Tier 3: Developer** - Organization-scoped development access
4. **Tier 4: Viewer** - Read-only access
5. **Tier 5: Demo** - Isolated demo environment access

## Role Hierarchy & Permissions

### Permission Distribution

| Role                    | Permission Count | Scope            | Key Capabilities                       |
| ----------------------- | ---------------- | ---------------- | -------------------------------------- |
| **Super Administrator** | 60+ (100%)       | 🌍 Global        | Platform management, all organizations |
| **Administrator**       | 55+ (92%)        | 🏢 Organization  | Full CRUD within organization          |
| **Developer**           | 40+ (67%)        | 💻 Organization  | Create/Read/Update (no delete)         |
| **Viewer**              | 17 (28%)         | 👁️ Organization  | Read-only access                       |
| **Demo**                | 40+ (67%)        | 🔬 Demo Org Only | Developer access in demo environment   |

### Detailed Permission Matrix

| Permission Category      | Super Admin    | Administrator  | Developer             | Viewer       | Demo                  |
| ------------------------ | -------------- | -------------- | --------------------- | ------------ | --------------------- |
| **Platform Management**  | ✅ Full        | ❌ None        | ❌ None               | ❌ None      | ❌ None               |
| **Organization CRUD**    | ✅ Full        | 📖 Read/Update | 📖 Read               | 📖 Read      | 📖 Read (Demo only)   |
| **User Management**      | ✅ Full        | ✅ Full        | 📝 Create/Read/Update | 📖 Read      | 📝 Create/Read/Update |
| **Role Management**      | ✅ Full        | ✅ Full        | 📖 Read               | 📖 Read      | 📖 Read               |
| **Tenant Management**    | ✅ Full        | ✅ Full        | 📝 Create/Read/Update | 📖 Read      | 📝 Create/Read/Update |
| **Workspace Management** | ✅ Full        | ✅ Full        | 📝 Create/Read/Update | 📖 Read      | 📝 Create/Read/Update |
| **Audit Logs**           | ✅ Read/Export | ✅ Read/Export | 📖 Read               | 📖 Read      | 📖 Read               |
| **Delete Operations**    | ✅ Yes         | ✅ Yes         | ❌ No                 | ❌ No        | ❌ No                 |
| **Data Retention**       | ♾️ Permanent   | ♾️ Permanent   | ♾️ Permanent          | ♾️ Permanent | ⏰ 6 hours            |

**Legend**:

- ✅ Full = Full CRUD access
- 📝 Create/Read/Update = No delete permissions
- 📖 Read = Read-only access
- ❌ None = No access

## Implementation Architecture

### Database Schema

#### Core Tables

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    organization_id UUID REFERENCES organizations(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP NULL
);

-- Roles table
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    tier INTEGER NOT NULL, -- 1-5 for the 5 tiers
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Permissions table
CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    resource VARCHAR(50) NOT NULL, -- e.g., 'users', 'roles'
    action VARCHAR(50) NOT NULL,   -- e.g., 'create', 'read', 'update', 'delete'
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Role-Permission mapping
CREATE TABLE role_permissions (
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

-- User-Role mapping
CREATE TABLE user_roles (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT NOW(),
    assigned_by UUID REFERENCES users(id),
    PRIMARY KEY (user_id, role_id)
);
```

#### Multi-Tenancy Tables

```sql
-- Organizations table
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tenants table
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    organization_id UUID REFERENCES organizations(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Workspaces table
CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    tenant_id UUID REFERENCES tenants(id),
    organization_id UUID REFERENCES organizations(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Domain Model Implementation

#### Role Aggregate

```typescript
// domain/aggregates/Role.ts
export class Role extends AggregateRoot {
  private constructor(
    private readonly _id: RoleId,
    private readonly _name: string,
    private readonly _tier: RoleTier,
    private _permissions: Permission[],
  ) {
    super();
  }

  static create(name: string, tier: RoleTier, permissions: Permission[]): Role {
    const role = new Role(RoleId.generate(), name, tier, permissions);

    role.addDomainEvent(new RoleCreatedEvent(role.id, role.name, role.tier));
    return role;
  }

  static reconstitute(
    id: RoleId,
    name: string,
    tier: RoleTier,
    permissions: Permission[],
  ): Role {
    return new Role(id, name, tier, permissions);
  }

  hasPermission(permission: Permission): boolean {
    return this._permissions.some((p) => p.equals(permission));
  }

  canPerformAction(resource: string, action: string): boolean {
    return this._permissions.some(
      (p) => p.resource === resource && p.action === action,
    );
  }

  // Getters
  get id(): RoleId {
    return this._id;
  }
  get name(): string {
    return this._name;
  }
  get tier(): RoleTier {
    return this._tier;
  }
  get permissions(): readonly Permission[] {
    return this._permissions;
  }
}
```

#### Permission Value Object

```typescript
// domain/value-objects/Permission.ts
export class Permission extends ValueObject<{
  resource: string;
  action: string;
}> {
  private constructor(resource: string, action: string) {
    super({ resource, action });
  }

  static create(resource: string, action: string): Permission {
    if (!resource || !action) {
      throw new DomainError("Resource and action are required");
    }
    return new Permission(resource, action);
  }

  get resource(): string {
    return this.value.resource;
  }

  get action(): string {
    return this.value.action;
  }

  get name(): string {
    return `${this.resource}:${this.action}`;
  }

  protected validate(value: { resource: string; action: string }): void {
    if (!value.resource || !value.action) {
      throw new DomainError("Invalid permission format");
    }
  }
}
```

#### Role Tier Enumeration

```typescript
// domain/value-objects/RoleTier.ts
export enum RoleTierEnum {
  SUPER_ADMINISTRATOR = 1,
  ADMINISTRATOR = 2,
  DEVELOPER = 3,
  VIEWER = 4,
  DEMO = 5,
}

export class RoleTier extends ValueObject<RoleTierEnum> {
  private constructor(tier: RoleTierEnum) {
    super(tier);
  }

  static create(tier: number): RoleTier {
    if (!Object.values(RoleTierEnum).includes(tier)) {
      throw new DomainError("Invalid role tier");
    }
    return new RoleTier(tier as RoleTierEnum);
  }

  static superAdministrator(): RoleTier {
    return new RoleTier(RoleTierEnum.SUPER_ADMINISTRATOR);
  }

  static administrator(): RoleTier {
    return new RoleTier(RoleTierEnum.ADMINISTRATOR);
  }

  static developer(): RoleTier {
    return new RoleTier(RoleTierEnum.DEVELOPER);
  }

  static viewer(): RoleTier {
    return new RoleTier(RoleTierEnum.VIEWER);
  }

  static demo(): RoleTier {
    return new RoleTier(RoleTierEnum.DEMO);
  }

  isHigherThan(other: RoleTier): boolean {
    return this.value < other.value; // Lower number = higher tier
  }

  canDelete(): boolean {
    return this.value <= RoleTierEnum.ADMINISTRATOR;
  }

  canManageUsers(): boolean {
    return this.value <= RoleTierEnum.ADMINISTRATOR;
  }

  isGlobalScope(): boolean {
    return this.value === RoleTierEnum.SUPER_ADMINISTRATOR;
  }

  isDemoRestricted(): boolean {
    return this.value === RoleTierEnum.DEMO;
  }

  protected validate(value: RoleTierEnum): void {
    if (!Object.values(RoleTierEnum).includes(value)) {
      throw new DomainError("Invalid role tier value");
    }
  }
}
```

### Permission System Implementation

#### Permission Guard

```typescript
// presentation/guards/PermissionGuard.ts
@Injectable()
export class PermissionGuard implements CanActivate {
  constructor(
    private readonly reflector: Reflector,
    @Inject("IUserRepository")
    private readonly userRepository: IUserRepository,
  ) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    // Get required permissions from decorator
    const requiredPermissions = this.reflector.get<string[]>(
      "permissions",
      context.getHandler(),
    );

    if (!requiredPermissions) {
      return true; // No permissions required
    }

    const request = context.switchToHttp().getRequest();
    const user = request.user;

    if (!user) {
      throw new UnauthorizedException("User not authenticated");
    }

    // Load user with roles and permissions
    const userWithRoles = await this.userRepository.findById(
      UserId.create(user.id),
    );

    if (!userWithRoles) {
      throw new UnauthorizedException("User not found");
    }

    // Check if user has required permissions
    const hasPermission = requiredPermissions.every((permission) =>
      this.userHasPermission(userWithRoles, permission),
    );

    if (!hasPermission) {
      throw new ForbiddenException("Insufficient permissions");
    }

    // Additional checks for demo users
    if (this.isDemoUser(userWithRoles)) {
      return this.validateDemoAccess(request, userWithRoles);
    }

    return true;
  }

  private userHasPermission(user: User, permissionName: string): boolean {
    const [resource, action] = permissionName.split(":");

    return user.roles.some((role) => role.canPerformAction(resource, action));
  }

  private isDemoUser(user: User): boolean {
    return user.roles.some((role) => role.tier.isDemoRestricted());
  }

  private validateDemoAccess(request: any, user: User): boolean {
    // Demo users can only access demo organization
    const organizationId = this.extractOrganizationId(request);

    if (organizationId && organizationId !== "org-demo") {
      throw new ForbiddenException(
        "Demo users can only access demo organization",
      );
    }

    return true;
  }

  private extractOrganizationId(request: any): string | null {
    // Extract organization ID from request params, body, or query
    return (
      request.params?.organizationId ||
      request.body?.organizationId ||
      request.query?.organizationId ||
      null
    );
  }
}
```

#### Permission Decorator

```typescript
// presentation/decorators/RequirePermissions.ts
export const RequirePermissions = (...permissions: string[]) => {
  return applyDecorators(
    SetMetadata("permissions", permissions),
    UseGuards(JwtAuthGuard, PermissionGuard),
    ApiBearerAuth(),
    ApiUnauthorizedResponse({ description: "Unauthorized" }),
    ApiForbiddenResponse({ description: "Insufficient permissions" }),
  );
};
```

### Usage Examples

#### Controller with Permission Checks

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
  @RequirePermissions("users:create")
  @ApiOperation({ summary: "Create a new user" })
  async createUser(@Body() request: CreateUserRequestDto): Promise<void> {
    const command = new CreateUserCommand(
      request.email,
      request.organizationId,
    );
    await this.commandBus.execute(command);
  }

  @Get()
  @RequirePermissions("users:read")
  @ApiOperation({ summary: "List all users" })
  async listUsers(
    @Query() query: ListUsersQueryDto,
  ): Promise<UserResponseDto[]> {
    const listQuery = new ListUsersQuery(
      query.organizationId,
      query.limit,
      query.offset,
    );
    return await this.queryBus.execute(listQuery);
  }

  @Put(":id")
  @RequirePermissions("users:update")
  @ApiOperation({ summary: "Update user" })
  async updateUser(
    @Param("id") id: string,
    @Body() request: UpdateUserRequestDto,
  ): Promise<void> {
    const command = new UpdateUserCommand(id, request.email, request.isActive);
    await this.commandBus.execute(command);
  }

  @Delete(":id")
  @RequirePermissions("users:delete")
  @ApiOperation({ summary: "Delete user" })
  async deleteUser(@Param("id") id: string): Promise<void> {
    const command = new DeleteUserCommand(id);
    await this.commandBus.execute(command);
  }
}
```

## Default Users & Seeding

### Seed Data Structure

```typescript
// infrastructure/persistence/seeds/1704240000001-seed-iam-roles-permissions.ts
export class SeedIAMRolesPermissions implements Seeder {
  async run(dataSource: DataSource): Promise<void> {
    const logger = new Logger("SeedIAMRolesPermissions");

    // 1. Create permissions
    const permissions = await this.createPermissions(dataSource);

    // 2. Create roles with permissions
    await this.createRoles(dataSource, permissions);

    logger.log("✅ IAM roles and permissions seeded successfully");
  }

  private async createPermissions(
    dataSource: DataSource,
  ): Promise<PermissionEntity[]> {
    const permissionRepository = dataSource.getRepository(PermissionEntity);

    const permissionData = [
      // User permissions
      { name: "users:create", resource: "users", action: "create" },
      { name: "users:read", resource: "users", action: "read" },
      { name: "users:update", resource: "users", action: "update" },
      { name: "users:delete", resource: "users", action: "delete" },

      // Role permissions
      { name: "roles:create", resource: "roles", action: "create" },
      { name: "roles:read", resource: "roles", action: "read" },
      { name: "roles:update", resource: "roles", action: "update" },
      { name: "roles:delete", resource: "roles", action: "delete" },

      // Organization permissions
      {
        name: "organizations:create",
        resource: "organizations",
        action: "create",
      },
      { name: "organizations:read", resource: "organizations", action: "read" },
      {
        name: "organizations:update",
        resource: "organizations",
        action: "update",
      },
      {
        name: "organizations:delete",
        resource: "organizations",
        action: "delete",
      },

      // Platform permissions (Super Admin only)
      { name: "platform:manage", resource: "platform", action: "manage" },
      { name: "system:admin", resource: "system", action: "admin" },

      // Audit permissions
      { name: "audit-logs:read", resource: "audit-logs", action: "read" },
      { name: "audit-logs:export", resource: "audit-logs", action: "export" },
    ];

    const permissions: PermissionEntity[] = [];

    for (const permData of permissionData) {
      const existing = await permissionRepository.findOne({
        where: { name: permData.name },
      });

      if (!existing) {
        const permission = permissionRepository.create(permData);
        await permissionRepository.save(permission);
        permissions.push(permission);
      } else {
        permissions.push(existing);
      }
    }

    return permissions;
  }

  private async createRoles(
    dataSource: DataSource,
    permissions: PermissionEntity[],
  ): Promise<void> {
    const roleRepository = dataSource.getRepository(RoleEntity);

    // Super Administrator (Tier 1) - All permissions
    await this.createRole(
      roleRepository,
      "super_administrator",
      "Super Administrator",
      1,
      permissions, // All permissions
    );

    // Administrator (Tier 2) - All except platform/system
    const adminPermissions = permissions.filter(
      (p) => !p.resource.includes("platform") && !p.resource.includes("system"),
    );
    await this.createRole(
      roleRepository,
      "administrator",
      "Administrator",
      2,
      adminPermissions,
    );

    // Developer (Tier 3) - No delete permissions
    const devPermissions = permissions.filter(
      (p) =>
        p.action !== "delete" &&
        !p.resource.includes("platform") &&
        !p.resource.includes("system"),
    );
    await this.createRole(
      roleRepository,
      "developer",
      "Developer",
      3,
      devPermissions,
    );

    // Viewer (Tier 4) - Only read permissions
    const viewerPermissions = permissions.filter((p) => p.action === "read");
    await this.createRole(
      roleRepository,
      "viewer",
      "Viewer",
      4,
      viewerPermissions,
    );

    // Demo (Tier 5) - Same as developer but demo-restricted
    await this.createRole(roleRepository, "demo", "Demo", 5, devPermissions);
  }

  private async createRole(
    roleRepository: Repository<RoleEntity>,
    name: string,
    displayName: string,
    tier: number,
    permissions: PermissionEntity[],
  ): Promise<void> {
    const existing = await roleRepository.findOne({ where: { name } });

    if (!existing) {
      const role = roleRepository.create({
        name,
        displayName,
        tier,
        permissions,
      });
      await roleRepository.save(role);
    }
  }
}
```

### Default Test Users

```typescript
// infrastructure/persistence/seeds/1704240000002-seed-auth-test-users.ts
export class SeedAuthTestUsers implements Seeder {
  async run(dataSource: DataSource): Promise<void> {
    const logger = new Logger("SeedAuthTestUsers");

    const userRepository = dataSource.getRepository(UserEntity);
    const roleRepository = dataSource.getRepository(RoleEntity);
    const organizationRepository = dataSource.getRepository(OrganizationEntity);

    // Create organizations
    const mainOrg = await this.createOrganization(
      organizationRepository,
      "TelemetryFlow",
      "telemetryflow",
    );

    const demoOrg = await this.createOrganization(
      organizationRepository,
      "Demo Organization",
      "org-demo",
    );

    // Get roles
    const roles = {
      superAdmin: await roleRepository.findOne({
        where: { name: "super_administrator" },
      }),
      admin: await roleRepository.findOne({ where: { name: "administrator" } }),
      developer: await roleRepository.findOne({ where: { name: "developer" } }),
      viewer: await roleRepository.findOne({ where: { name: "viewer" } }),
      demo: await roleRepository.findOne({ where: { name: "demo" } }),
    };

    // Create default users
    const users = [
      {
        email: "superadmin.telemetryflow@telemetryflow.id",
        password: "SuperAdmin@123456",
        role: roles.superAdmin,
        organization: mainOrg,
      },
      {
        email: "administrator.telemetryflow@telemetryflow.id",
        password: "Admin@123456",
        role: roles.admin,
        organization: mainOrg,
      },
      {
        email: "developer.telemetryflow@telemetryflow.id",
        password: "Developer@123456",
        role: roles.developer,
        organization: mainOrg,
      },
      {
        email: "viewer.telemetryflow@telemetryflow.id",
        password: "Viewer@123456",
        role: roles.viewer,
        organization: mainOrg,
      },
      {
        email: "demo.telemetryflow@telemetryflow.id",
        password: "Demo@123456",
        role: roles.demo,
        organization: demoOrg,
      },
    ];

    for (const userData of users) {
      await this.createUser(userRepository, userData);
    }

    logger.log("✅ Default test users created successfully");
  }

  private async createUser(
    userRepository: Repository<UserEntity>,
    userData: any,
  ): Promise<void> {
    const existing = await userRepository.findOne({
      where: { email: userData.email },
    });

    if (!existing) {
      const hashedPassword = await bcrypt.hash(userData.password, 10);

      const user = userRepository.create({
        email: userData.email,
        passwordHash: hashedPassword,
        isActive: true,
        organization: userData.organization,
        roles: [userData.role],
      });

      await userRepository.save(user);
    }
  }
}
```

## Demo Environment Protection

### Auto-Cleanup Implementation

```typescript
// infrastructure/processors/demo-cleanup.processor.ts
@Processor("demo-cleanup")
export class DemoCleanupProcessor {
  private readonly logger = new Logger(DemoCleanupProcessor.name);

  constructor(
    @InjectRepository(UserEntity)
    private readonly userRepository: Repository<UserEntity>,
    @InjectRepository(OrganizationEntity)
    private readonly organizationRepository: Repository<OrganizationEntity>,
  ) {}

  @Cron("0 */6 * * *") // Every 6 hours
  async handleDemoCleanup(): Promise<void> {
    this.logger.log("🧹 Starting demo environment cleanup...");

    try {
      // Find demo organization
      const demoOrg = await this.organizationRepository.findOne({
        where: { slug: "org-demo" },
      });

      if (!demoOrg) {
        this.logger.warn("Demo organization not found");
        return;
      }

      // Delete demo users (except default demo user)
      const deletedUsers = await this.userRepository.delete({
        organizationId: demoOrg.id,
        email: Not("demo.telemetryflow@telemetryflow.id"),
      });

      this.logger.log(`🗑️ Deleted ${deletedUsers.affected} demo users`);

      // TODO: Clean up demo data in other tables
      // - Demo dashboards
      // - Demo alerts
      // - Demo metrics (ClickHouse)
      // - Demo logs (ClickHouse)

      // Re-seed demo data
      await this.reseedDemoData(demoOrg);

      this.logger.log("✅ Demo cleanup completed successfully");
    } catch (error) {
      this.logger.error("❌ Demo cleanup failed", error);
    }
  }

  private async reseedDemoData(demoOrg: OrganizationEntity): Promise<void> {
    // Create fresh demo data
    // This would include sample dashboards, alerts, etc.
    this.logger.log("🌱 Re-seeding demo data...");
  }
}
```

## Testing the RBAC System

### Permission Testing

```typescript
// __tests__/rbac-system.e2e.spec.ts
describe("RBAC System E2E", () => {
  let app: INestApplication;
  let userTokens: Record<string, string>;

  beforeAll(async () => {
    // Setup test app and get tokens for each user type
    userTokens = {
      superAdmin: await getAuthToken(
        "superadmin.telemetryflow@telemetryflow.id",
      ),
      admin: await getAuthToken("administrator.telemetryflow@telemetryflow.id"),
      developer: await getAuthToken("developer.telemetryflow@telemetryflow.id"),
      viewer: await getAuthToken("viewer.telemetryflow@telemetryflow.id"),
      demo: await getAuthToken("demo.telemetryflow@telemetryflow.id"),
    };
  });

  describe("User Management Permissions", () => {
    it("should allow super admin to create users", async () => {
      const response = await request(app.getHttpServer())
        .post("/users")
        .set("Authorization", `Bearer ${userTokens.superAdmin}`)
        .send({
          email: "test@example.com",
          organizationId: "org-123",
        });

      expect(response.status).toBe(201);
    });

    it("should allow admin to create users in their org", async () => {
      const response = await request(app.getHttpServer())
        .post("/users")
        .set("Authorization", `Bearer ${userTokens.admin}`)
        .send({
          email: "test2@example.com",
          organizationId: "telemetryflow-org",
        });

      expect(response.status).toBe(201);
    });

    it("should deny viewer from creating users", async () => {
      const response = await request(app.getHttpServer())
        .post("/users")
        .set("Authorization", `Bearer ${userTokens.viewer}`)
        .send({
          email: "test3@example.com",
          organizationId: "telemetryflow-org",
        });

      expect(response.status).toBe(403);
    });
  });

  describe("Demo User Restrictions", () => {
    it("should allow demo user to access demo org", async () => {
      const response = await request(app.getHttpServer())
        .get("/organizations/org-demo")
        .set("Authorization", `Bearer ${userTokens.demo}`);

      expect(response.status).toBe(200);
    });

    it("should deny demo user access to production org", async () => {
      const response = await request(app.getHttpServer())
        .get("/organizations/telemetryflow-org")
        .set("Authorization", `Bearer ${userTokens.demo}`);

      expect(response.status).toBe(403);
    });
  });

  describe("Delete Permissions", () => {
    it("should allow admin to delete resources", async () => {
      const response = await request(app.getHttpServer())
        .delete("/users/test-user-id")
        .set("Authorization", `Bearer ${userTokens.admin}`);

      expect(response.status).toBe(200);
    });

    it("should deny developer from deleting resources", async () => {
      const response = await request(app.getHttpServer())
        .delete("/users/test-user-id")
        .set("Authorization", `Bearer ${userTokens.developer}`);

      expect(response.status).toBe(403);
    });
  });
});
```

## Best Practices

### 1. Permission Design

- Use resource:action format for permissions (e.g., `users:create`)
- Keep permissions granular but not overly complex
- Group related permissions logically

### 2. Role Assignment

- Follow principle of least privilege
- Start with lower-tier roles and upgrade as needed
- Regularly audit role assignments

### 3. Demo Environment

- Always isolate demo users to demo organization
- Implement automatic cleanup to prevent data accumulation
- Monitor demo usage patterns for security

### 4. Security Considerations

- Always validate organization/tenant context
- Log all permission checks for audit trails
- Implement rate limiting for demo users
- Use strong password requirements for all tiers

### 5. Testing

- Test each permission level thoroughly
- Verify cross-organization access restrictions
- Test demo environment isolation
- Include negative test cases (access denied scenarios)

This RBAC system provides a robust, scalable foundation for managing access control in TelemetryFlow Platform while maintaining security and organizational isolation.
