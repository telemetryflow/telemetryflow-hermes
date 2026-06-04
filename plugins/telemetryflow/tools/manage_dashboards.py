#!/usr/bin/env python3
"""Manage TFO Dashboards: CRUD, export/import, sharing, public dashboards.

Usage:
  python3 manage_dashboards.py --resource list
  python3 manage_dashboards.py --resource list --tag production
  python3 manage_dashboards.py --resource get --dashboard-id <id>
  python3 manage_dashboards.py --resource export --dashboard-id <id>
  python3 manage_dashboards.py --resource shared
  python3 manage_dashboards.py --resource public
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _shared import output_json, parse_args, tfo_request


def main():
    args = parse_args()
    resource = args.get("resource", "list")
    dashboard_id = args.get("dashboard_id", "")

    if resource == "list":
        params = {}
        for key in ("tag", "tags", "isPublic", "isFavorite", "search"):
            if args.get(key):
                params[key] = args[key]
        result = tfo_request("/dashboards", params=params)

    elif resource == "get":
        if not dashboard_id:
            print("ERROR: --dashboard-id is required for get", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/dashboards/{dashboard_id}")

    elif resource == "export":
        if not dashboard_id:
            print("ERROR: --dashboard-id is required for export", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/dashboards/{dashboard_id}/export")

    elif resource == "shared":
        result = tfo_request("/dashboards", params={"shared": "true"})

    elif resource == "public":
        result = tfo_request("/dashboards", params={"isPublic": "true"})

    elif resource == "templates":
        result = tfo_request("/dashboards/templates")

    elif resource == "shared-graphs":
        result = tfo_request("/dashboards/shared-graphs")

    else:
        print(
            f"ERROR: unknown resource '{resource}'. Valid: list, get, export, shared, public, templates, shared-graphs"
        )
        sys.exit(1)

    output_json(result)


if __name__ == "__main__":
    main()
