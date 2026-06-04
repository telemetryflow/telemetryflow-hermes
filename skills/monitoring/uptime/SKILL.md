---
name: uptime-monitoring
description: >
  Activate for uptime-related investigations. Covers HTTP/HTTPS/TCP endpoint
  monitoring, SSL certificate tracking, response time percentiles (P50-P99),
  uptime percentage calculations, and scheduled check analysis.
version: 1.0.0
author: agent
platforms: [linux, macos]
---

## Procedure

1. Query uptime monitors and their current status
   ```
   python3 check_uptime.py --resource monitors
   python3 check_uptime.py --resource monitors --monitor-id <id>
   ```

2. Check individual monitor health details
   ```
   python3 check_uptime.py --resource stats --monitor-id <id>
   python3 check_uptime.py --resource checks --monitor-id <id>
   ```

3. Analyze SSL certificate status
   ```
   python3 check_uptime.py --resource ssl-summary
   python3 check_uptime.py --resource ssl-trend --monitor-id <id>
   ```

4. Review historical performance
   ```
   python3 check_uptime.py --resource daily-stats --monitor-id <id>
   python3 check_uptime.py --resource hourly-stats --monitor-id <id>
   ```

## Key Metrics

- **Uptime %**: Calculated over 24h/7d/30d/90d windows from ClickHouse MVs
- **Response Time**: P50, P90, P95, P99 percentiles
- **SSL Days Remaining**: Expiry tracking with trend analysis
- **Monitor Status**: PENDING, UP, DOWN, DEGRADED, MAINTENANCE

## TFO API Endpoints

- `GET /monitoring/uptime/monitors` — List all monitors
- `GET /monitoring/uptime/monitors/:id` — Get monitor detail
- `GET /monitoring/uptime/monitors/:id/stats` — Uptime % + response time
- `GET /monitoring/uptime/monitors/:id/checks` — Check history
- `GET /monitoring/uptime/monitors/:id/daily-stats` — Daily MV stats
- `GET /monitoring/uptime/monitors/:id/hourly-stats` — Hourly MV stats
- `GET /monitoring/uptime/monitors/:id/ssl-trend` — SSL trend
- `GET /monitoring/uptime/monitors/ssl-summary` — Org-wide SSL summary

## Classification Rules

- Monitor DOWN > 5 minutes → CRITICAL
- SSL expiry < 7 days → CRITICAL
- SSL expiry < 30 days → WARNING
- Uptime < 99.9% over 24h → WARNING
- Response time P99 > 5s → WARNING
- Response time P99 > 10s → CRITICAL
- Monitor in MAINTENANCE state → INFO

## Verification

- All monitors show UP status
- SSL certificates have > 30 days remaining
- Uptime percentage >= 99.9% over 7 days
- Response time P95 within acceptable thresholds
