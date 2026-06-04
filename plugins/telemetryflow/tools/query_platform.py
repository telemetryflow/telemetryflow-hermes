#!/usr/bin/env python3
"""Query TFO platform management: IAM, Tenancy, Audit, Retention, Subscription, API Keys, Notifications.

Usage:
  python3 query_platform.py --resource iam-users
  python3 query_platform.py --resource iam-roles
  python3 query_platform.py --resource iam-permissions
  python3 query_platform.py --resource tenancy-orgs
  python3 query_platform.py --resource tenancy-workspaces
  python3 query_platform.py --resource audit-logs --duration 24h
  python3 query_platform.py --resource retention-policies
  python3 query_platform.py --resource subscriptions
  python3 query_platform.py --resource api-keys
  python3 query_platform.py --resource notification-channels
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _shared import output_json, parse_args, tfo_request

RESOURCES = {
    "iam-users": "/iam/users",
    "iam-roles": "/iam/roles",
    "iam-permissions": "/iam/permissions",
    "iam-assignments": "/iam/assignments",
    "tenancy-orgs": "/tenancy/organizations",
    "tenancy-workspaces": "/tenancy/workspaces",
    "tenancy-regions": "/tenancy/regions",
    "tenancy-tenants": "/tenancy/tenants",
    "audit-logs": "/audit/logs",
    "retention-policies": "/retention/policies",
    "subscriptions": "/subscription/plans",
    "api-keys": "/api-keys",
    "notification-channels": "/notification/channels",
}


def main():
    args = parse_args()
    resource = args.get("resource", "iam-users")

    if resource not in RESOURCES:
        print(f"ERROR: unknown resource '{resource}'")
        print(f"Valid: {', '.join(sorted(RESOURCES.keys()))}")
        sys.exit(1)

    params = {
        "page": args.get("page", "1"),
        "pageSize": args.get("page_size", "20"),
    }
    if resource == "audit-logs" and args.get("duration"):
        params["duration"] = args["duration"]

    result = tfo_request(RESOURCES[resource], params=params)
    output_json(result)


if __name__ == "__main__":
    main()
