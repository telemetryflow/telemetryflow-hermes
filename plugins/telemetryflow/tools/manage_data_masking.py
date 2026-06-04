#!/usr/bin/env python3
"""Manage TFO data masking policies.

Usage:
  python3 manage_data_masking.py --action list
  python3 manage_data_masking.py --action get --policy-id <uuid>
  python3 manage_data_masking.py --action create --name "Mask Emails" --field body --pattern email
  python3 manage_data_masking.py --action toggle --policy-id <uuid> --enabled false
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _shared import output_json, parse_args, tfo_request


def main():
    args = parse_args()
    action = args.get("action", "list")
    policy_id = args.get("policy_id", "")

    if action == "list":
        result = tfo_request(
            "/data-masking/policies",
            params={
                "page": args.get("page", "1"),
                "pageSize": args.get("page_size", "20"),
            },
        )
    elif action == "get":
        if not policy_id:
            print("ERROR: --policy-id is required", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/data-masking/policies/{policy_id}")
    elif action == "create":
        name = args.get("name", "")
        if not name:
            print("ERROR: --name is required for create", file=sys.stderr)
            sys.exit(1)
        data = {
            "name": name,
            "field": args.get("field", "body"),
            "pattern": args.get("pattern", "email"),
            "enabled": args.get("enabled", "true").lower() == "true",
        }
        result = tfo_request("/data-masking/policies", method="POST", data=data)
    elif action == "toggle":
        if not policy_id:
            print("ERROR: --policy-id is required", file=sys.stderr)
            sys.exit(1)
        enabled = args.get("enabled", "true").lower() == "true"
        result = tfo_request(f"/data-masking/policies/{policy_id}", method="PATCH", data={"enabled": enabled})
    else:
        print(f"ERROR: unknown action '{action}'. Valid: list, get, create, toggle")
        sys.exit(1)

    output_json(result)


if __name__ == "__main__":
    main()
