---
name: remediation-gate
description: >
  Activate when proposing remediation actions. Ensures every write
  operation requires human approval via Telegram notification.
version: 1.0.0
author: agent
platforms: [linux, macos]
---

## Procedure

1. Receive confirmed root cause from Reviewer
2. Assess remediation options from most to least invasive:
   a. No action needed (self-healing, transient)
   b. Configuration change (alert threshold, resource limit)
   c. Rollback deployment
   d. Scale deployment
   e. Restart pods
   f. Escalate to human

3. For each proposed action, prepare risk assessment:
   - Risk level: LOW / MEDIUM / HIGH / CRITICAL
   - Reversibility: Can it be undone? How?
   - Blast radius: What else could be affected?
   - Estimated recovery time

4. Send Telegram notification with approval request:
   ```
   🔔 Remediation Proposal
   
   Alert: {alert_summary}
   Root Cause: {root_cause}
   Risk: {risk_level}
   
   Proposed: {action_description}
   Reversibility: {reversibility}
   Blast Radius: {blast_radius}
   
   Reviewer: {verdict}
   
   [Approve] [Reject] [Manual Review]
   ```

5. Wait for human response (timeout: 10 minutes)
   - Approved → Execute action
   - Rejected → Log and stop
   - Timeout → Auto-escalate to human

6. Execute approved action
7. Post-action verification (see Verification section)

## Action Tools

### Scale Deployment
```bash
kubectl scale deployment <name> -n <namespace> --replicas=<count>
```

### Restart Pod
```bash
kubectl rollout restart deployment <name> -n <namespace>
```

### Rollback Deploy
```bash
kubectl rollout undo deployment <name> -n <namespace>
```

### Update Alert Rule
```bash
curl -X PUT "${TELEMETRYFLOW_API_URL}/api/v1/alerts/rules/{rule_id}" \
  -H "Authorization: Bearer ${TELEMETRYFLOW_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"threshold": <new_value>}'
```

## Verification

- 30s after action: check pod status
- 2 min after action: check metrics returning to baseline
- 5 min after action: check for new error spikes
- Log outcome to MEMORY.md
