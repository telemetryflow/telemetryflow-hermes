#!/usr/bin/env python3
"""Query TFO VM monitoring: inventory, heartbeat, metrics.

Usage:
  python3 check_vm.py --resource list
  python3 check_vm.py --resource list --provider aws
  python3 check_vm.py --resource get --vm-id <id>
  python3 check_vm.py --resource metrics --vm-id <id>
  python3 check_vm.py --resource metrics --vm-id <id> --metric-name cpu_usage
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _shared import output_json, parse_args, tfo_request


def main():
    args = parse_args()
    resource = args.get("resource", "list")
    vm_id = args.get("vm_id", "")

    if resource == "list":
        params = {"page": args.get("page", "1"), "pageSize": args.get("page_size", "20")}
        if args.get("provider"):
            params["provider"] = args["provider"]
        if args.get("status"):
            params["status"] = args["status"]
        result = tfo_request("/monitoring/vms", params=params)

    elif resource == "get":
        if not vm_id:
            print("ERROR: --vm-id is required for get", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/monitoring/vms/{vm_id}")

    elif resource == "metrics":
        if not vm_id:
            print("ERROR: --vm-id is required for metrics", file=sys.stderr)
            sys.exit(1)
        params = {}
        if args.get("metric_name"):
            params["metricName"] = args["metric_name"]
        if args.get("from"):
            params["from"] = args["from"]
        if args.get("to"):
            params["to"] = args["to"]
        result = tfo_request(f"/monitoring/vms/{vm_id}/metrics", params=params)

    else:
        print(f"ERROR: unknown resource '{resource}'. Valid: list, get, metrics")
        sys.exit(1)

    output_json(result)


if __name__ == "__main__":
    main()
