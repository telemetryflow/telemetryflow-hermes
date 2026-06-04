# MEMORY.md — Triage Agent

## Known Auto-Resolve Patterns
- payments-api OOM on deploy → auto-resolve, notify on-call
- cert rotation auth-service crash → auto-resolve if within rotation window
- redis-cluster-01 latency 02:00 UTC → auto-resolve, backup window

## Escalation Rules
- Any latency breach > 2x baseline → CRITICAL
- Any error rate > 5% → CRITICAL
- Any pod CrashLoopBackOff > 3 restarts → CRITICAL
- Known patterns with changed behavior → CRITICAL (re-evaluate)

## Noise Suppression Rules
- Suppress < medium severity during active deploy windows
- Suppress duplicate alerts within 5 minutes
- Suppress health check failures during scheduled maintenance
