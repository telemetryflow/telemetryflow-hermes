---
name: kubernetes-monitoring
description: >
  Activate for Kubernetes/EKS cluster investigations. Covers clusters,
  nodes, namespaces, pods, deployments, workloads (StatefulSets, DaemonSets,
  ReplicaSets, Jobs, CronJobs), PVs/PVCs, services, ingresses, events,
  pod logs, API Server metrics, CoreDNS metrics, and Prometheus remote_write.
version: 1.2.0
author: agent
platforms: [linux, macos]
---

## Procedure

1. Get cluster overview and statistics
   ```
   python3 check_k8s.py --resource overview
   python3 check_k8s.py --resource stats
   ```

2. List clusters and their resources
   ```
   python3 check_k8s.py --resource clusters
   python3 check_k8s.py --resource nodes --cluster <cluster-id>
   python3 check_k8s.py --resource namespaces --cluster <cluster-id>
   ```

3. Investigate pod issues
   ```
   python3 check_k8s.py --resource pods --cluster <cluster-id> --namespace production
   ```

4. Check deployments and workloads
   ```
   python3 check_k8s.py --resource deployments --cluster <cluster-id> --namespace production
   ```

5. Review storage (PVs/PVCs)
   ```
   python3 check_k8s.py --resource pv --cluster <cluster-id>
   ```

6. Check control plane metrics
   - API Server: request latency, error rate, etcd performance
   - CoreDNS: query latency, cache hit rate, error rate

## K8s Resource Types

11 entity types tracked:
- **Cluster** — K8s cluster with version, node count
- **Node** — Worker/control plane nodes with capacity
- **Namespace** — Resource namespaces
- **Pod** — Running containers with phase/restarts
- **Deployment** — Managed replica sets
- **PV/PVC** — Persistent storage
- **Workload** — StatefulSets, DaemonSets, Jobs, CronJobs
- **Service** — ClusterIP, NodePort, LoadBalancer
- **Ingress** — HTTP routing rules
- **Event** — K8s events for all resources

## TFO API Endpoints

- `GET /monitoring/kubernetes/overview` — Dashboard with time-series
- `GET /monitoring/kubernetes/stats` — Stats overview
- `GET /monitoring/kubernetes/clusters` — List clusters
- `GET /monitoring/kubernetes/clusters/:id/nodes` — Node list
- `GET /monitoring/kubernetes/clusters/:id/pods` — Pod list
- `GET /monitoring/kubernetes/clusters/:id/deployments` — Deployments
- `GET /monitoring/kubernetes/clusters/:id/persistent-volumes` — PVs
- `GET /monitoring/kubernetes/clusters/:id/logs` — Unified log viewer
- `GET /monitoring/kubernetes/api-server` — API Server metrics
- `GET /monitoring/kubernetes/coredns` — CoreDNS metrics
- `POST /v2/prometheus/write` — Prometheus remote_write ingestion

## Classification Rules

- Pod CrashLoopBackOff > 3 restarts → CRITICAL
- Node NotReady > 5 min → CRITICAL
- Deployment unavailable replicas > 50% → CRITICAL
- PVC pending > 10 min → WARNING
- API Server latency P99 > 1s → WARNING
- CoreDNS error rate > 5% → WARNING
- Evicted pods accumulating → WARNING

## Pitfalls

- Pods in different namespaces may have same name — always include namespace
- PVC binding can take time in dynamic provisioning — check storage class
- API Server metrics come from Prometheus, not direct K8s API

## Verification

- All nodes in Ready state
- No pods in CrashLoopBackOff
- Deployments have desired == available replicas
- PVCs all in Bound state
- API Server and CoreDNS metrics normal
