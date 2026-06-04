#!/usr/bin/env python3
"""Manage TFO IAM: users, roles, permissions, groups, audit logs.

Usage:
  python3 manage_iam.py --resource users
  python3 manage_iam.py --resource user-roles --user-id <id>
  python3 manage_iam.py --resource user-permissions --user-id <id>
  python3 manage_iam.py --resource roles
  python3 manage_iam.py --resource role-permissions --role-id <id>
  python3 manage_iam.py --resource permissions
  python3 manage_iam.py --resource groups
  python3 manage_iam.py --resource group-users --group-id <id>
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _shared import output_json, parse_args, tfo_request


def main():
    args = parse_args()
    resource = args.get("resource", "users")

    if resource == "users":
        result = tfo_request("/iam/users")

    elif resource == "user-detail":
        user_id = args.get("user_id", "")
        if not user_id:
            print("ERROR: --user-id is required", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/iam/users/{user_id}")

    elif resource == "user-roles":
        user_id = args.get("user_id", "")
        if not user_id:
            print("ERROR: --user-id is required", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/iam/users/{user_id}/roles")

    elif resource == "user-permissions":
        user_id = args.get("user_id", "")
        if not user_id:
            print("ERROR: --user-id is required", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/iam/users/{user_id}/permissions")

    elif resource == "roles":
        result = tfo_request("/iam/roles")

    elif resource == "role-detail":
        role_id = args.get("role_id", "")
        if not role_id:
            print("ERROR: --role-id is required", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/iam/roles/{role_id}")

    elif resource == "role-permissions":
        role_id = args.get("role_id", "")
        if not role_id:
            print("ERROR: --role-id is required", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/iam/roles/{role_id}/permissions")

    elif resource == "permissions":
        result = tfo_request("/iam/permissions")

    elif resource == "groups":
        result = tfo_request("/iam/groups")

    elif resource == "group-detail":
        group_id = args.get("group_id", "")
        if not group_id:
            print("ERROR: --group-id is required", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/iam/groups/{group_id}")

    elif resource == "group-users":
        group_id = args.get("group_id", "")
        if not group_id:
            print("ERROR: --group-id is required", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/iam/groups/{group_id}/users")

    elif resource == "audit-logs":
        params = {"page": args.get("page", "1"), "pageSize": args.get("page_size", "20")}
        result = tfo_request("/iam/audit-logs", params=params)

    else:
        print(
            f"ERROR: unknown resource '{resource}'. Valid: users, user-detail, user-roles, user-permissions, roles, role-detail, role-permissions, permissions, groups, group-detail, group-users, audit-logs"
        )
        sys.exit(1)

    output_json(result)


if __name__ == "__main__":
    main()
