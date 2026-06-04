#!/usr/bin/env python3
"""Query TFO Audit Trails: security and compliance event logging.

Usage:
  python3 query_audit.py --resource logs --duration 24h
  python3 query_audit.py --resource logs --event-type AUTH --result FAILURE
  python3 query_audit.py --resource logs --user-email admin@example.com
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _shared import output_json, parse_args, tfo_request


def main():
    args = parse_args()
    resource = args.get("resource", "logs")

    if resource == "logs":
        params = {"page": args.get("page", "1"), "pageSize": args.get("page_size", "20")}
        for key in ("duration", "event_type", "result", "user_email", "ip_address", "resource"):
            if args.get(key):
                params[key] = args[key]
        result = tfo_request("/audit/logs", params=params)

    else:
        print(f"ERROR: unknown resource '{resource}'. Valid: logs")
        sys.exit(1)

    output_json(result)


if __name__ == "__main__":
    main()
