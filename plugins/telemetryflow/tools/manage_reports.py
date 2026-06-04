#!/usr/bin/env python3
"""Manage TFO Reports: definitions, executions, generation, stats.

Usage:
  python3 manage_reports.py --resource definitions
  python3 manage_reports.py --resource definitions --type weekly
  python3 manage_reports.py --resource executions
  python3 manage_reports.py --resource stats
  python3 manage_reports.py --resource generate --definition-id <id>
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _shared import output_json, parse_args, tfo_request


def main():
    args = parse_args()
    resource = args.get("resource", "definitions")

    if resource == "definitions":
        params = {}
        for key in ("type", "schedule", "enabled", "search"):
            if args.get(key):
                params[key] = args[key]
        result = tfo_request("/reports/definitions", params=params)

    elif resource == "definition-detail":
        def_id = args.get("definition_id", "")
        if not def_id:
            print("ERROR: --definition-id is required", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/reports/definitions/{def_id}")

    elif resource == "executions":
        result = tfo_request("/reports/executions")

    elif resource == "execution-detail":
        exec_id = args.get("execution_id", "")
        if not exec_id:
            print("ERROR: --execution-id is required", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/reports/executions/{exec_id}")

    elif resource == "stats":
        result = tfo_request("/reports/stats")

    elif resource == "generate":
        def_id = args.get("definition_id", "")
        if not def_id:
            print("ERROR: --definition-id is required for generate", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/reports/definitions/{def_id}/generate", method="POST")

    else:
        print(
            f"ERROR: unknown resource '{resource}'. Valid: definitions, definition-detail, executions, execution-detail, stats, generate"
        )
        sys.exit(1)

    output_json(result)


if __name__ == "__main__":
    main()
