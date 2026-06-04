#!/usr/bin/env python3
"""Manage TFO Tenancy: regions, tenants, organizations, workspaces.

Usage:
  python3 manage_tenancy.py --resource regions
  python3 manage_tenancy.py --resource tenants
  python3 manage_tenancy.py --resource organizations
  python3 manage_tenancy.py --resource organizations --region-id <id>
  python3 manage_tenancy.py --resource workspaces --org-id <id>
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _shared import output_json, parse_args, tfo_request


def main():
    args = parse_args()
    resource = args.get("resource", "regions")

    if resource == "regions":
        result = tfo_request("/tenancy/regions")

    elif resource == "region-detail":
        region_id = args.get("region_id", "")
        if not region_id:
            print("ERROR: --region-id is required", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/tenancy/regions/{region_id}")

    elif resource == "tenants":
        result = tfo_request("/tenancy/tenants")

    elif resource == "tenant-detail":
        tenant_id = args.get("tenant_id", "")
        if not tenant_id:
            print("ERROR: --tenant-id is required", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/tenancy/tenants/{tenant_id}")

    elif resource == "organizations":
        params = {}
        if args.get("region_id"):
            params["regionId"] = args["region_id"]
        result = tfo_request("/tenancy/organizations", params=params)

    elif resource == "org-detail":
        org_id = args.get("org_id", "")
        if not org_id:
            print("ERROR: --org-id is required", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/tenancy/organizations/{org_id}")

    elif resource == "workspaces":
        org_id = args.get("org_id", "")
        if not org_id:
            print("ERROR: --org-id is required for workspaces", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/tenancy/organizations/{org_id}/workspaces")

    else:
        print(
            f"ERROR: unknown resource '{resource}'. Valid: regions, region-detail, tenants, tenant-detail, organizations, org-detail, workspaces"
        )
        sys.exit(1)

    output_json(result)


if __name__ == "__main__":
    main()
