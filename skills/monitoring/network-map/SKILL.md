---
name: network-map
description: >
  Activate for network topology and traffic investigations. Uses eBPF flows,
  DNS observations, SNMP polling, and OTEL trace-based discovery. Supports
  Kubernetes pod-to-pod network flows, SNMP v1/v2c/v3, and traceroute paths.
version: 1.0.0
author: agent
platforms: [linux, macos]
---

## Procedure

1. Get complete network topology
   ```
   python3 check_network_map.py --resource topology
   ```

2. List network nodes
   ```
   python3 check_network_map.py --resource nodes
   python3 check_network_map.py --resource nodes --type KUBERNETES_POD
   ```

3. Check node connections and traffic
   ```
   python3 check_network_map.py --resource connections --node-id <id>
   python3 check_network_map.py --resource traffic --node-id <id>
   ```

4. Analyze network flows
   ```
   python3 check_network_map.py --resource flows
   python3 check_network_map.py --resource k8s-flows
   ```

5. Check DNS observations
   ```
   python3 check_network_map.py --resource dns
   ```

6. Review SNMP devices
   ```
   python3 check_network_map.py --resource snmp-configs
   ```

## Node Types

SERVER, CLIENT, ROUTER, SWITCH, FIREWALL, LOAD_BALANCER, DATABASE,
KUBERNETES_POD, KUBERNETES_SERVICE, CLOUD_RESOURCE, EXTERNAL

## Connection Types

TCP, UDP, HTTP, GRPC, ICMP

## Discovery Mechanisms

1. **OTEL traces** — every 5 min, extracts network nodes from trace spans
2. **SNMP polling** — every 1 min, polls network devices (v1/v2c/v3)
3. **eBPF ingestion** — real-time flow data from TFO Agent
4. **K8s network flows** — Cilium Hubble-compatible pod-to-pod flows

## TFO API Endpoints

- `GET /monitoring/network-map` — Complete network topology
- `GET /monitoring/network-map/topology` — Topology with depth filter
- `GET /monitoring/network-map/nodes` — List nodes
- `GET /monitoring/network-map/nodes/:id/connections` — Node connections
- `GET /monitoring/network-map/nodes/:id/traffic` — Traffic time-series
- `GET /monitoring/network-map/flows` — Flow analytics
- `GET /monitoring/network-map/dns` — DNS observations
- `GET /monitoring/network-map/k8s/flows` — K8s network flows
- `GET /monitoring/network-map/snmp/configs` — SNMP configurations

## Classification Rules

- Connection status DEGRADED → WARNING
- Packet loss > 1% → WARNING
- Packet loss > 5% → CRITICAL
- Latency > 100ms for inter-service → WARNING
- DNS resolution failures > 0 → WARNING
- SNMP device unreachable → WARNING
- External node with high traffic anomaly → INVESTIGATE

## Verification

- All expected nodes are discovered
- No unreachable SNMP devices
- DNS resolution working for all observed queries
- K8s pod-to-pod flows show expected patterns
- No significant packet loss on any connection
