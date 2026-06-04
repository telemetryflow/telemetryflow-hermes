#!/usr/bin/env python3
"""Query TFO Subscription: plans, usage, billing, invoices.

Usage:
  python3 query_subscription.py --resource current
  python3 query_subscription.py --resource plans
  python3 query_subscription.py --resource usage
  python3 query_subscription.py --resource usage-check --metric-type LOG_INGESTION_GB
  python3 query_subscription.py --resource invoices
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _shared import output_json, parse_args, tfo_request


def main():
    args = parse_args()
    resource = args.get("resource", "current")

    if resource == "current":
        result = tfo_request("/subscription")

    elif resource == "plans":
        result = tfo_request("/subscription/plans")

    elif resource == "plan-detail":
        plan_id = args.get("plan_id", "")
        if not plan_id:
            print("ERROR: --plan-id is required", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/subscription/plans/{plan_id}")

    elif resource == "usage":
        result = tfo_request("/subscription/usage")

    elif resource == "usage-check":
        metric_type = args.get("metric_type", "")
        if not metric_type:
            print("ERROR: --metric-type is required for usage-check", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/subscription/usage/check/{metric_type}")

    elif resource == "invoices":
        result = tfo_request("/subscription/invoices")

    elif resource == "invoice-detail":
        invoice_id = args.get("invoice_id", "")
        if not invoice_id:
            print("ERROR: --invoice-id is required", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/subscription/invoices/{invoice_id}")

    else:
        print(
            f"ERROR: unknown resource '{resource}'. Valid: current, plans, plan-detail, usage, usage-check, invoices, invoice-detail"
        )
        sys.exit(1)

    output_json(result)


if __name__ == "__main__":
    main()
