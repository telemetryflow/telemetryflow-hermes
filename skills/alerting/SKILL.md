---
name: alerting-management
description: >
  Activate for alert rule management and alert instance investigation.
  Covers TFQL-based alert conditions, alert lifecycle (firing → acknowledged
  → resolved/silenced), notification channel management, and alert evaluation.
version: 1.0.0
author: agent
platforms: [linux, macos]
---

## Procedure

1. List alert rules and their states
   ```
   python3 manage_alerts.py --resource rules
   python3 manage_alerts.py --resource rules --severity critical
   ```

2. Check firing alert instances
   ```
   python3 manage_alerts.py --resource instances --status firing
   python3 manage_alerts.py --resource instances --severity critical
   ```

3. Get alert statistics
   ```
   python3 manage_alerts.py --resource stats
   ```

4. Review notification channels
   ```
   python3 manage_alerts.py --resource channels
   ```

5. Validate TFQL query for a rule
   ```
   python3 manage_alerts.py --resource validate-tfql --query "SELECT avg(value) FROM metrics WHERE ..."
   ```

## Alert Rule Structure

```json
{
  "name": "High Error Rate",
  "severity": "critical",
  "conditions": [{
    "aggregation": "AVG|MAX|MIN|SUM|COUNT",
    "operator": "GT|LT|GTE|LTE|EQ|NEQ",
    "threshold": 5.0,
    "forDuration": "5m"
  }],
  "notificationChannels": ["channel-uuid"],
  "tfqlQuery": "SELECT ...",
  "evaluationInterval": "1m",
  "sourceType": "metrics"
}
```

## Alert Lifecycle

1. **firing** — Condition met, alert active
2. **acknowledged** — Human confirmed awareness
3. **resolved** — Condition no longer met
4. **silenced** — Muted for a period (with reason)

## TFO API Endpoints

- `GET /alert-rules` — List rules (filter by enabled, severity, state)
- `GET /alert-rules/:id` — Get rule detail
- `POST /alert-rules/validate-tfql` — Validate TFQL query
- `GET /alert-instances` — List instances (filter by status, severity)
- `GET /alert-instances/stats` — Alert statistics
- `POST /alert-instances/:id/acknowledge` — Acknowledge
- `POST /alert-instances/:id/resolve` — Resolve
- `POST /alert-instances/:id/silence` — Silence
- `GET /notification-channels` — List channels
- `POST /notification-channels/:id/test` — Test channel

## Classification Rules

- Firing CRITICAL alert unacknowledged > 15 min → ESCALATE
- Firing WARNING alert > 1 hour → ESCALATE
- Silenced alert where condition persists → INVESTIGATE
- Alert rule evaluation failing → CRITICAL (monitoring gap)
- Multiple alerts firing on same service → CORRELATE

## Verification

- All alert rules are evaluating correctly
- No stale firing alerts (firing > 24h without change)
- Notification channels are functional
- TFQL queries are valid and performant
