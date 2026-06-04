---
name: audit-trails
description: >
  Activate for security and compliance investigations. Query audit events
  across 4 categories (AUTH, AUTHZ, DATA, SYSTEM) with structured logging
  including user context, IP addresses, resource access, and results.
version: 1.0.0
author: agent
platforms: [linux, macos]
---

## Procedure

1. Query recent audit events
   ```
   python3 query_audit.py --resource logs --duration 24h
   python3 query_audit.py --resource logs --event-type AUTH --result FAILURE
   ```

2. Search for specific user activity
   ```
   python3 query_audit.py --resource logs --user-email admin@example.com
   ```

3. Check for security anomalies
   - Multiple AUTH FAILURE events from same IP
   - DATA access outside normal patterns
   - AUTHZ DENIED events (permission escalation attempts)
   - SYSTEM configuration changes

## Event Categories

- **AUTH**: Login, logout, token refresh, MFA events
- **AUTHZ**: Permission checks, role assignments, access denied
- **DATA**: CRUD operations on sensitive resources
- **SYSTEM**: Configuration changes, module enable/disable

## Event Structure

```json
{
  "eventType": "AUTH",
  "eventResult": "SUCCESS|FAILURE|DENIED",
  "userId": "uuid",
  "userEmail": "user@example.com",
  "ipAddress": "192.168.1.100",
  "resource": "/api/v2/users",
  "action": "CREATE",
  "metadata": {},
  "timestamp": "2026-06-04T12:00:00Z"
}
```

## Classification Rules

- > 10 AUTH FAILURE from same IP in 5 min → CRITICAL (brute force)
- AUTHZ DENIED for admin resources → WARNING
- DATA events for PII outside business hours → INVESTIGATE
- SYSTEM config changes by non-admin → CRITICAL
- Concurrent sessions from different countries → WARNING

## Verification

- Audit logging is active and capturing events
- No suspicious authentication patterns
- All data access is within policy
- System changes are properly authorized
