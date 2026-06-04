---
name: vm-monitoring
description: >
  Activate for VM-related investigations. Covers virtual machine inventory,
  heartbeat monitoring, multi-cloud provider tracking (AWS/GCP/Azure/on-prem),
  and per-VM metrics from ClickHouse (CPU, memory, disk, network).
version: 1.0.0
author: agent
platforms: [linux, macos]
---

## Procedure

1. List all VMs and their status
   ```
   python3 check_vm.py --resource list
   python3 check_vm.py --resource list --provider aws
   ```

2. Get individual VM details
   ```
   python3 check_vm.py --resource get --vm-id <id>
   ```

3. Check VM metrics from ClickHouse
   ```
   python3 check_vm.py --resource metrics --vm-id <id>
   python3 check_vm.py --resource metrics --vm-id <id> --metric-name cpu_usage
   ```

4. Verify heartbeat recency
   - VMs should heartbeat every 60 seconds
   - Stale heartbeat > 5 minutes → potential agent failure
   - Check `lastHeartbeatAt` timestamp

## VM Properties

- **Provider**: AWS, GCP, Azure, on-prem, custom
- **OS Type**: Linux, Windows, macOS
- **Specs**: cpuCores, memoryGb, diskGb
- **Location**: region, zone
- **Labels/Tags**: for filtering and grouping
- **Status**: tracked via heartbeat pattern

## TFO API Endpoints

- `GET /monitoring/vms` — List VMs (filter by provider, status)
- `POST /monitoring/vms` — Register VM
- `GET /monitoring/vms/:id` — Get VM detail
- `PUT /monitoring/vms/:id` — Update VM
- `POST /monitoring/vms/:id/heartbeat` — Record heartbeat
- `GET /monitoring/vms/:id/metrics` — Get metrics from ClickHouse

## Classification Rules

- VM heartbeat stale > 15 min → CRITICAL
- CPU > 90% sustained 15 min → WARNING
- Memory > 95% → CRITICAL
- Disk > 85% → WARNING
- Disk > 95% → CRITICAL
- Multiple VMs down in same region → CRITICAL (infra issue)

## Verification

- All VMs have recent heartbeats
- Resource utilization within thresholds
- No orphaned VMs (registered but no metrics)
