---
name: tenancy-management
description: >
  Activate for multi-tenancy investigations. Covers hierarchical
  tenant management: Regions > Tenants > Organizations > Workspaces.
  Auto-provisions default resources (retention policies, report definitions)
  when new organizations are created.
version: 1.0.0
author: agent
platforms: [linux, macos]
---

## Procedure

1. List tenants and their organizations
   ```
   python3 manage_tenancy.py --resource tenants
   python3 manage_tenancy.py --resource organizations --tenant-id <id>
   ```

2. Check regions for data residency
   ```
   python3 manage_tenancy.py --resource regions
   ```

3. List workspaces within an organization
   ```
   python3 manage_tenancy.py --resource workspaces --org-id <id>
   ```

## Hierarchy

```
Region (geographic data residency)
  └── Tenant (isolation boundary)
       └── Organization (name, code, domain, regionId)
            └── Workspace (project-level isolation)
```

## TFO API Endpoints

- `GET /tenancy/regions` — List regions
- `GET /tenancy/tenants` — List tenants
- `GET /tenancy/organizations` — List organizations (by region)
- `GET /tenancy/workspaces` — List workspaces (within org)

## Auto-Provisioning

When a new organization is created, TFO auto-provisions:
- Default retention policies (logs, metrics, traces, alerts, exemplars)
- Default report definitions (weekly utilization, reliability)

## Classification Rules

- Organization deactivated unexpectedly → WARNING
- Region unavailable → CRITICAL (data residency issue)
- Workspace count approaching limit → WARNING
- Tenant provisioning failure → CRITICAL

## Verification

- All organizations are active
- Regions are healthy and accessible
- Workspaces are properly isolated
- Auto-provisioning is working for new orgs
