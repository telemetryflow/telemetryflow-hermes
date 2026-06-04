# MEMORY.md — Remediator Agent

## Approved Remediation Patterns
- payments-api OOM: rollback to previous version OR increase memory to 1GiB
- auth-service cert: restart after cert rotation completes
- node-pool-3 memory: cordon + drain, scale if needed

## Risk Assessment Templates
- LOW: Rollback to known-good version (reversible)
- MEDIUM: Scale deployment (cost impact, may not solve root cause)
- HIGH: Restart pods (temporary, may lose in-flight requests)
- CRITICAL: Any database or statefulset change

## Post-Remediation Verification
- Wait 30 seconds, then check pod status
- Verify metric returns to baseline within 5 minutes
- Check for new error spikes in logs
- Confirm no cascading failures in other services
