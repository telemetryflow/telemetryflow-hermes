---
name: dashboard-management
description: >
  Activate for dashboard-related tasks. Covers dashboard CRUD, widget
  management, variable templating, import/export, sharing, public dashboards,
  and graph short URLs.
version: 1.0.0
author: agent
platforms: [linux, macos]
---

## Procedure

1. List dashboards
   ```
   python3 manage_dashboards.py --resource list
   python3 manage_dashboards.py --resource list --tag production
   ```

2. Get dashboard detail with widgets
   ```
   python3 manage_dashboards.py --resource get --dashboard-id <id>
   ```

3. Export/import dashboards
   ```
   python3 manage_dashboards.py --resource export --dashboard-id <id>
   python3 manage_dashboards.py --resource import --file dashboard.json
   ```

4. Check shared and public dashboards
   ```
   python3 manage_dashboards.py --resource shared
   python3 manage_dashboards.py --resource public
   ```

## Dashboard Features

- **Widgets**: Metric charts, log panels, trace tables, status indicators
- **Variables**: Template variables for dynamic filtering (namespace, service, etc.)
- **Time Range**: Global time range with refresh intervals
- **Tags**: For organizing and filtering dashboards
- **Sharing**: Token-based sharing with expiry
- **Public**: Public dashboards accessible without auth

## TFO API Endpoints

- `GET /dashboards` — List (filter by tags, isPublic, isFavorite, search)
- `GET /dashboards/:id` — Get with widgets and variables
- `POST /dashboards` — Create dashboard
- `PUT /dashboards/:id` — Update dashboard
- `DELETE /dashboards/:id` — Delete
- `POST /dashboards/:id/clone` — Clone
- `POST /dashboards/:id/export-token` — Generate export token
- `GET /dashboards/export/:token` — Download by token
- `POST /dashboards/import` — Import from JSON

## Verification

- All production dashboards are accessible
- Widgets render correctly with current data
- Shared dashboards have valid export tokens
- No orphaned dashboards (no widgets/variables)
