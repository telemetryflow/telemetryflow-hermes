---
name: k8s-pod-debug
description: >
  Activate for crashing pods, CrashLoopBackOff,
  "why is my pod restarting", container failures, ImagePullBackOff.
version: 1.2.0
author: agent
platforms: [linux, macos]
---

## Procedure

1. Get pod status and events
   ```bash
   kubectl get pods -n <namespace> -l app=<service> -o wide
   kubectl describe pod <pod-name> -n <namespace>
   ```

2. Check events for the pod
   ```bash
   kubectl get events -n <namespace> --field-selector involvedObject.name=<pod-name> --sort-by='.lastTimestamp'
   ```

3. Pull container logs
   ```bash
   kubectl logs <pod-name> -n <namespace> --tail=500
   kubectl logs <pod-name> -n <namespace> --previous
   ```

4. Look for common failure patterns:
   - OOMKilled: Check memory limits vs actual usage
   - ImagePullBackOff: Check image tag and registry access
   - CrashLoopBackOff: Check application error logs
   - ConfigMissing: Check ConfigMap and Secret mounts

5. Check resource usage
   ```bash
   kubectl top pods -n <namespace> -l app=<service>
   kubectl top nodes
   ```

## Pitfalls

- Forgetting `--previous` flag on restarted containers — you need the logs from before the crash
- Not checking node-level events — pod failures can be caused by node pressure
- Ignoring init container failures — check all containers in the pod

## Verification

- Pod stays Running with 0 restarts for 5+ minutes
- Memory usage is below 80% of limit
- No new error entries in logs
