---
name: subscription-management
description: >
  Activate for subscription and billing investigations. Covers plan management,
  usage tracking (13 metric types with real ClickHouse data volumes), billing
  cycles, invoices, and trial period support.
version: 1.0.0
author: agent
platforms: [linux, macos]
---

## Procedure

1. Check current subscription
   ```
   python3 query_subscription.py --resource current
   ```

2. Review usage against limits
   ```
   python3 query_subscription.py --resource usage
   python3 query_subscription.py --resource usage-check --metric-type LOG_INGESTION_GB
   ```

3. List invoices and billing history
   ```
   python3 query_subscription.py --resource invoices
   ```

4. Check available plans
   ```
   python3 query_subscription.py --resource plans
   ```

## Usage Metric Types (13 types)

- LOG_INGESTION_GB, METRIC_DATA_POINTS, TRACE_SPANS
- AI_CHAT_MESSAGES, AI_INSIGHT_GENERATIONS
- DASHBOARD_COUNT, ALERT_RULE_COUNT
- UPTIME_MONITORS, K8S_CLUSTERS
- DB_INSTANCES, VM_INSTANCES
- USERS, API_KEYS

## Subscription Lifecycle

trialing → active → (paused) → canceled
                 ↘ past_due → canceled

## TFO API Endpoints

- `GET /subscription/plans` — List plans
- `GET /subscription` — Current org subscription
- `GET /subscription/usage` — Current usage (ClickHouse-enriched)
- `GET /subscription/usage/check/:metricType` — Check specific limit
- `GET /subscription/invoices` — List invoices
- `POST /subscription/cancel` — Cancel subscription

## Classification Rules

- Usage > 90% of limit → WARNING
- Usage > 100% of limit → CRITICAL (overage)
- Subscription in PAST_DUE state → CRITICAL
- Trial expiring < 3 days → WARNING
- No active subscription → CRITICAL

## Verification

- Subscription is active and in good standing
- Usage metrics are within plan limits
- Invoices are paid and up-to-date
- Trial conversions are handled properly
