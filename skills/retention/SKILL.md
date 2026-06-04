---
name: retention-management
description: >
  Activate for data retention policy management. Covers policy CRUD,
  automatic enforcement, archive support, real data volume statistics
  from ClickHouse, and dry-run enforcement testing.
version: 1.0.0
author: agent
platforms: [linux, macos]
---

## Procedure

1. List retention policies
   ```
   python3 manage_retention.py --resource policies
   python3 manage_retention.py --resource policies --data-type logs
   ```

2. Check retention statistics (real data volumes)
   ```
   python3 manage_retention.py --resource statistics
   ```

3. Test enforcement (dry run)
   ```
   python3 manage_retention.py --resource enforce --dry-run true
   ```

## Data Types

- **logs** — Application and system logs
- **metrics** — Time-series metric data points
- **traces** — Distributed trace spans
- **alerts** — Alert instances and history
- **exemplars** — Metric-to-trace exemplars

## TFO API Endpoints

- `GET /retention/policies` — List policies (filter by dataType)
- `GET /retention/policies/statistics` — Real data volumes
- `POST /retention/policies` — Create policy
- `PUT /retention/policies/:id` — Update policy
- `POST /retention/policies/enforce` — Enforce (dry run supported)
- `POST /retention/policies/:id/activate` — Activate
- `POST /retention/policies/:id/deactivate` — Deactivate

## Classification Rules

- Data volume approaching storage limit > 80% → WARNING
- Data volume > 95% → CRITICAL
- Retention policy disabled → WARNING
- No policy for a data type → WARNING
- Enforcement job failing → CRITICAL

## Verification

- All data types have active retention policies
- Enforcement is running on schedule
- Archive destinations are accessible
- Data volumes within expected ranges
