---
name: status-page-management
description: >
  Activate for status page incidents, scheduled maintenance, and subscriber
  management. Covers public/private status pages with custom branding,
  incident lifecycle (investigating → identified → monitoring → resolved),
  and email/webhook subscriber notifications.
version: 1.0.0
author: agent
platforms: [linux, macos]
---

## Procedure

1. List status pages and their overall health
   ```
   python3 check_uptime.py --resource status-pages
   ```

2. Check active incidents on a status page
   ```
   python3 check_uptime.py --resource incidents --status-page-id <id>
   ```

3. Review incident details and updates
   - Impact levels: NONE, MINOR, MAJOR, CRITICAL
   - Statuses: INVESTIGATING, IDENTIFIED, MONITORING, RESOLVED, SCHEDULED
   - Each incident has a timeline of updates

4. Check for scheduled maintenance windows
   - `isScheduledMaintenance: true` incidents
   - Verify start/end times against current time

5. Assess subscriber notification status
   - Email subscribers with confirmation tokens
   - Webhook subscribers (ALL, INCIDENTS_ONLY, MAINTENANCE_ONLY)

## TFO API Endpoints

- `GET /status-pages` — List status pages
- `GET /status-pages/:id` — Get status page detail
- `GET /status-pages/:id/incidents` — List incidents (filter by status)
- `GET /status-pages/:id/subscribers` — List subscribers
- `GET /public/status/:slug` — Public status page

## Incident Classification

- CRITICAL impact with INVESTIGATING status → CRITICAL
- MAJOR impact with IDENTIFIED status → HIGH
- SCHEDULED maintenance starting within 1 hour → INFO
- RESOLVED within last hour → INFO (verify resolution)
- Multiple active incidents on same page → ESCALATE

## Pitfalls

- Not checking scheduled maintenance before escalating
- Ignoring subscriber notification failures
- Missing custom domain verification issues

## Verification

- All incidents have proper impact classification
- No stale incidents (INVESTIGATING > 2 hours without update)
- Subscriber notifications are functional
- Custom domains are verified and serving
