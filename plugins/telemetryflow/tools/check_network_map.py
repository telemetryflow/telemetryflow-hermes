#!/usr/bin/env python3
"""Query TFO Network Map: topology, nodes, connections, traffic, flows, DNS, SNMP.

Usage:
  python3 check_network_map.py --resource topology
  python3 check_network_map.py --resource nodes
  python3 check_network_map.py --resource nodes --type KUBERNETES_POD
  python3 check_network_map.py --resource connections --node-id <id>
  python3 check_network_map.py --resource traffic --node-id <id>
  python3 check_network_map.py --resource flows
  python3 check_network_map.py --resource dns
  python3 check_network_map.py --resource k8s-flows
  python3 check_network_map.py --resource snmp-configs
  python3 check_network_map.py --resource paths
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _shared import output_json, parse_args, tfo_request


def main():
    args = parse_args()
    resource = args.get("resource", "topology")
    node_id = args.get("node_id", "")

    if resource == "topology":
        params = {}
        if args.get("depth"):
            params["depth"] = args["depth"]
        result = tfo_request("/monitoring/network-map/topology", params=params)

    elif resource == "nodes":
        params = {}
        for key in ("type", "status", "cluster"):
            if args.get(key):
                params[key] = args[key]
        result = tfo_request("/monitoring/network-map/nodes", params=params)

    elif resource == "connections":
        if not node_id:
            print("ERROR: --node-id is required for connections", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/monitoring/network-map/nodes/{node_id}/connections")

    elif resource == "traffic":
        if not node_id:
            print("ERROR: --node-id is required for traffic", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/monitoring/network-map/nodes/{node_id}/traffic")

    elif resource == "flows":
        result = tfo_request("/monitoring/network-map/flows")

    elif resource == "dns":
        result = tfo_request("/monitoring/network-map/dns")

    elif resource == "k8s-flows":
        result = tfo_request("/monitoring/network-map/k8s/flows")

    elif resource == "snmp-configs":
        result = tfo_request("/monitoring/network-map/snmp/configs")

    elif resource == "paths":
        result = tfo_request("/monitoring/network-map/paths")

    else:
        print(
            f"ERROR: unknown resource '{resource}'. Valid: topology, nodes, connections, traffic, flows, dns, k8s-flows, snmp-configs, paths"
        )
        sys.exit(1)

    output_json(result)


if __name__ == "__main__":
    main()
