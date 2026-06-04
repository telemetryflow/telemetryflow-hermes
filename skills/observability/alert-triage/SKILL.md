---
name: alert-triage
description: >
  Activate when a new alert fires from TelemetryFlow. Classifies
  severity, cross-references known patterns, and routes to the
  appropriate agent.
version: 1.0.0
author: agent
platforms: [linux, macos]
---

## Procedure

1. Parse alert payload from TelemetryFlow webhook
   ```json
   {
     "alert_id": "<uuid>",
     "rule_name": "<string>",
     "severity": "<critical|warning|info>",
     "labels": {"service": "...", "namespace": "..."},
     "annotations": {"summary": "...", "description": "..."},
     "fired_at": "<timestamp>",
     "values": {"current": "...", "threshold": "..."}
   }
   ```

2. Extract key fields:
   - alert_id, rule_name, severity
   - service name from labels
   - current value vs threshold
   - timestamp

3. Cross-reference MEMORY.md known patterns:
   - Exact match → auto-resolve with note
   - Partial match → flag similarity but still investigate
   - No match → genuine anomaly

4. Classify:
   - CRITICAL: Genuine anomaly, delegate to Investigator
   - KNOWN: Auto-resolve, log to session
   - NOISE: Suppress, track for fatigue analysis

5. For CRITICAL: delegate to Investigator with full alert context
   ```
   hermes -p investigator delegate "Investigate alert: {alert_id}
   Rule: {rule_name}
   Service: {service}
   Current value: {current_value}
   Threshold: {threshold}
   Severity: {severity}
   Fired at: {fired_at}"
   ```

## Classification Rules

- Latency breach > 2x baseline → CRITICAL
- Error rate > 5% → CRITICAL
- Pod CrashLoopBackOff > 3 restarts → CRITICAL
- Known pattern with changed behavior → CRITICAL (re-evaluate)
- Below threshold or during maintenance → NOISE
- Duplicate within 5 minutes → NOISE

## Verification

- Alert classification logged with reasoning
- CRITICAL alerts delegated within 3 seconds
- KNOWN patterns logged with resolution note
