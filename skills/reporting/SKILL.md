---
name: reporting
description: >
  Activate for report generation and management. Covers report definitions,
  scheduled execution, multi-section reports (utilization, reliability,
  alerting, user management, uptime), and email delivery.
version: 1.0.0
author: agent
platforms: [linux, macos]
---

## Procedure

1. List report definitions
   ```
   python3 manage_reports.py --resource definitions
   python3 manage_reports.py --resource definitions --type weekly
   ```

2. Check report executions
   ```
   python3 manage_reports.py --resource executions
   ```

3. Get report statistics
   ```
   python3 manage_reports.py --resource stats
   ```

4. Trigger manual report generation
   ```
   python3 manage_reports.py --resource generate --definition-id <id>
   ```

## Report Sections

- **Utilization**: Resource utilization across infrastructure
- **Reliability**: Uptime and error rate metrics
- **Alerting**: Alert frequency, severity distribution, MTTR
- **User Management**: IAM activity and access patterns
- **Uptime**: Endpoint availability and response times

## TFO API Endpoints

- `GET /reports/definitions` — List definitions
- `GET /reports/definitions/:id` — Get definition
- `POST /reports/definitions/:id/generate` — Generate report
- `GET /reports/executions` — List executions
- `GET /reports/executions/:id` — Get execution
- `GET /reports/stats` — Report statistics
- `POST /reports/definitions/:id/send-email` — Trigger email delivery

## Verification

- Scheduled reports are executing on time
- Report content reflects current data
- Email delivery is working
- No failed executions accumulating
