---
name: iam-management
description: >
  Activate for identity and access management investigations. Covers
  users, roles, permissions, groups, MFA (TOTP), password policies,
  RBAC with direct permission assignment, and domain events.
  Full DDD/CQRS architecture with 8 aggregates, 28 domain events.
version: 1.0.0
author: agent
platforms: [linux, macos]
---

## Procedure

1. List users and their roles
   ```
   python3 manage_iam.py --resource users
   python3 manage_iam.py --resource user-roles --user-id <id>
   python3 manage_iam.py --resource user-permissions --user-id <id>
   ```

2. Check roles and permissions
   ```
   python3 manage_iam.py --resource roles
   python3 manage_iam.py --resource permissions
   python3 manage_iam.py --resource role-permissions --role-id <id>
   ```

3. Review groups
   ```
   python3 manage_iam.py --resource groups
   python3 manage_iam.py --resource group-users --group-id <id>
   ```

## IAM Domain Model

8 aggregates: User, Role, Permission, Tenant, Organization, Workspace, Group, Region
33 commands, 18 queries, 28 domain events

## Permission Format

`module:submodule:action`
- `monitoring:uptime:read`, `monitoring:uptime:write`
- `alert:read`, `alert:write`
- `ai-intelligence:read`
- `sso:delete`

## Security Features

- bcrypt password hashing
- TOTP MFA support
- Force password change on first login
- Hierarchical permission resolution
- Full audit trail via domain events

## TFO API Endpoints

- `GET /api/v2/users` — List users
- `GET /api/v2/roles` — List roles
- `GET /api/v2/permissions` — List permissions
- `GET /api/v2/groups` — List groups
- `GET /api/v2/audit-logs` — IAM audit logs

## Classification Rules

- User with admin role deactivated → WARNING
- Multiple failed login attempts → SECURITY ALERT
- Role without permissions → WARNING (misconfiguration)
- MFA not enabled for admin users → WARNING
- Stale user accounts (no login > 90 days) → INFO

## Verification

- All active users have appropriate roles
- Permissions follow least-privilege principle
- MFA is enabled for all admin users
- No orphaned roles or groups
