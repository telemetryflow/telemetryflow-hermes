#!/usr/bin/env python3
"""Check Kubernetes cluster health via TFO monitoring API.

Uses TFO's hybrid PostgreSQL + ClickHouse Kubernetes monitoring.

Usage:
  python3 check_k8s.py --resource overview
  python3 check_k8s.py --resource nodes --cluster my-cluster
  python3 check_k8s.py --resource pods --namespace production
  python3 check_k8s.py --resource deployments --namespace production
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _shared import output_json, parse_args, tfo_request


def main():
    args = parse_args()
    resource = args.get("resource", "overview")
    cluster = args.get("cluster", "")
    namespace = args.get("namespace", "")

    if resource == "overview":
        result = tfo_request("/kubernetes/overview")

    elif resource == "clusters":
        result = tfo_request("/kubernetes/clusters")

    elif resource == "nodes":
        params = {}
        if cluster:
            params["cluster"] = cluster
        result = tfo_request("/kubernetes/nodes", params=params)

    elif resource == "namespaces":
        params = {}
        if cluster:
            params["cluster"] = cluster
        result = tfo_request("/kubernetes/namespaces", params=params)

    elif resource == "pods":
        params = {}
        if namespace:
            params["namespace"] = namespace
        if cluster:
            params["cluster"] = cluster
        result = tfo_request("/kubernetes/pods", params=params)

    elif resource == "deployments":
        params = {}
        if namespace:
            params["namespace"] = namespace
        if cluster:
            params["cluster"] = cluster
        result = tfo_request("/kubernetes/deployments", params=params)

    elif resource == "pv":
        params = {}
        if cluster:
            params["cluster"] = cluster
        result = tfo_request("/kubernetes/persistent-volumes", params=params)

    else:
        print(
            f"ERROR: unknown resource '{resource}'. Valid: overview, clusters, nodes, namespaces, pods, deployments, pv"
        )
        sys.exit(1)

    output_json(result)


if __name__ == "__main__":
    main()
