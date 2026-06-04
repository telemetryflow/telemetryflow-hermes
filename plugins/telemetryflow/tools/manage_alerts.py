#!/usr/bin/env python3
"""Manage TFO Alerting: rules, instances, notification channels, TFQL validation.

Usage:
  python3 manage_alerts.py --resource rules
  python3 manage_alerts.py --resource rules --severity critical
  python3 manage_alerts.py --resource instances --status firing
  python3 manage_alerts.py --resource stats
  python3 manage_alerts.py --resource channels
  python3 manage_alerts.py --resource validate-tfql --query "SELECT avg(value) FROM metrics"
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _shared import output_json, parse_args, tfo_request


def main():
    args = parse_args()
    resource = args.get("resource", "rules")

    if resource == "rules":
        params = {}
        for key in ("enabled", "severity", "state", "search"):
            if args.get(key):
                params[key] = args[key]
        result = tfo_request("/alert-rules", params=params)

    elif resource == "rule-detail":
        rule_id = args.get("rule_id", "")
        if not rule_id:
            print("ERROR: --rule-id is required", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/alert-rules/{rule_id}")

    elif resource == "instances":
        params = {}
        for key in ("status", "severity", "rule", "from", "to"):
            if args.get(key):
                params[key] = args[key]
        result = tfo_request("/alert-instances", params=params)

    elif resource == "instance-detail":
        instance_id = args.get("instance_id", "")
        if not instance_id:
            print("ERROR: --instance-id is required", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/alert-instances/{instance_id}")

    elif resource == "stats":
        result = tfo_request("/alert-instances/stats")

    elif resource == "channels":
        params = {}
        for key in ("enabled", "type"):
            if args.get(key):
                params[key] = args[key]
        result = tfo_request("/notification-channels", params=params)

    elif resource == "validate-tfql":
        query = args.get("query", "")
        if not query:
            print("ERROR: --query is required for validate-tfql", file=sys.stderr)
            sys.exit(1)
        result = tfo_request("/alert-rules/validate-tfql", method="POST", data={"query": query})

    else:
        print(
            f"ERROR: unknown resource '{resource}'. Valid: rules, rule-detail, instances, instance-detail, stats, channels, validate-tfql"
        )
        sys.exit(1)

    output_json(result)


if __name__ == "__main__":
    main()
