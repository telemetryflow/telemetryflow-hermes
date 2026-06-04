#!/usr/bin/env python3
"""Query TFO Service Map: topology, services, dependencies, health, metrics.

Usage:
  python3 check_service_map.py --resource map
  python3 check_service_map.py --resource services
  python3 check_service_map.py --resource services --type MICROSERVICE
  python3 check_service_map.py --resource get --service-id <id>
  python3 check_service_map.py --resource dependencies --service-id <id>
  python3 check_service_map.py --resource health --service-id <id>
  python3 check_service_map.py --resource metrics --service-id <id>
  python3 check_service_map.py --resource topology --depth 3
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _shared import output_json, parse_args, tfo_request


def main():
    args = parse_args()
    resource = args.get("resource", "map")
    service_id = args.get("service_id", "")

    if resource == "map":
        result = tfo_request("/monitoring/service-map")

    elif resource == "services":
        params = {}
        if args.get("type"):
            params["type"] = args["type"]
        if args.get("status"):
            params["status"] = args["status"]
        if args.get("namespace"):
            params["namespace"] = args["namespace"]
        result = tfo_request("/monitoring/service-map/services", params=params)

    elif resource == "get":
        if not service_id:
            print("ERROR: --service-id is required for get", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/monitoring/service-map/services/{service_id}")

    elif resource == "dependencies":
        if not service_id:
            print("ERROR: --service-id is required for dependencies", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/monitoring/service-map/services/{service_id}/dependencies")

    elif resource == "health":
        if not service_id:
            print("ERROR: --service-id is required for health", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/monitoring/service-map/services/{service_id}/health")

    elif resource == "metrics":
        if not service_id:
            print("ERROR: --service-id is required for metrics", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/monitoring/service-map/services/{service_id}/metrics")

    elif resource == "topology":
        params = {}
        if args.get("depth"):
            params["depth"] = args["depth"]
        result = tfo_request("/monitoring/service-map/topology", params=params)

    elif resource == "trace-dependencies":
        result = tfo_request("/monitoring/service-map/dependencies")

    else:
        print(
            f"ERROR: unknown resource '{resource}'. Valid: map, services, get, dependencies, health, metrics, topology, trace-dependencies"
        )
        sys.exit(1)

    output_json(result)


if __name__ == "__main__":
    main()
