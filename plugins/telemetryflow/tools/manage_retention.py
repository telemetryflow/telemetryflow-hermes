#!/usr/bin/env python3
"""Manage TFO Data Retention: policies, statistics, enforcement.

Usage:
  python3 manage_retention.py --resource policies
  python3 manage_retention.py --resource policies --data-type logs
  python3 manage_retention.py --resource statistics
  python3 manage_retention.py --resource enforce --dry-run true
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _shared import output_json, parse_args, tfo_request


def main():
    args = parse_args()
    resource = args.get("resource", "policies")

    if resource == "policies":
        params = {}
        if args.get("data_type"):
            params["dataType"] = args["data_type"]
        if args.get("include_defaults"):
            params["includeDefaults"] = args["include_defaults"]
        result = tfo_request("/retention/policies", params=params)

    elif resource == "policy-detail":
        policy_id = args.get("policy_id", "")
        if not policy_id:
            print("ERROR: --policy-id is required", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/retention/policies/{policy_id}")

    elif resource == "statistics":
        result = tfo_request("/retention/policies/statistics")

    elif resource == "enforce":
        data = {}
        if args.get("dry_run") == "true":
            data["dryRun"] = True
        result = tfo_request("/retention/policies/enforce", method="POST", data=data)

    else:
        print(f"ERROR: unknown resource '{resource}'. Valid: policies, policy-detail, statistics, enforce")
        sys.exit(1)

    output_json(result)


if __name__ == "__main__":
    main()
