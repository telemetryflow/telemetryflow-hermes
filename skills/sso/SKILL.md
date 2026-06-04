---
name: sso-management
description: >
  Activate for SSO authentication investigations. Covers OAuth2 provider
  management, user connections, JIT user provisioning, and authentication
  flow debugging.
version: 1.0.0
author: agent
platforms: [linux, macos]
---

## Procedure

1. List SSO providers
   ```
   python3 manage_sso.py --resource providers
   ```

2. Check user SSO connections
   ```
   python3 manage_sso.py --resource connections
   ```

3. Check public providers for an organization
   ```
   python3 manage_sso.py --resource public-providers --org-id <id>
   ```

## OAuth2 Flow

1. `POST /sso/initiate` — Start SSO (providerId, redirectUrl)
2. User authenticates with provider (Google, GitHub, etc.)
3. `GET /sso/callback/:provider` — Callback redirect
4. `POST /sso/callback` — Exchange code for tokens

## JIT User Provisioning

On first SSO login, TFO automatically:
- Creates user account from SSO profile
- Assigns default roles
- Creates SSO connection record

## TFO API Endpoints

- `GET /sso/providers` — List providers (admin)
- `GET /sso/providers/:organizationId/public` — Public providers
- `GET /sso/connections` — User's SSO connections
- `DELETE /sso/connections/:id` — Unlink connection

## Classification Rules

- SSO provider returning errors → WARNING
- Multiple failed SSO attempts → SECURITY ALERT
- Stale connection (provider user no longer exists) → WARNING
- No SSO provider configured for org with > 10 users → INFO

## Verification

- SSO providers are responding correctly
- User connections are valid
- JIT provisioning is working
- Token exchange is successful
