#!/usr/bin/env python3
"""Manage TFO SSO: providers, connections, public providers.

Usage:
  python3 manage_sso.py --resource providers
  python3 manage_sso.py --resource provider-detail --provider-id <id>
  python3 manage_sso.py --resource public-providers --org-id <id>
  python3 manage_sso.py --resource connections
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _shared import output_json, parse_args, tfo_request


def main():
    args = parse_args()
    resource = args.get("resource", "providers")

    if resource == "providers":
        result = tfo_request("/sso/providers")

    elif resource == "provider-detail":
        provider_id = args.get("provider_id", "")
        if not provider_id:
            print("ERROR: --provider-id is required", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/sso/providers/{provider_id}")

    elif resource == "public-providers":
        org_id = args.get("org_id", "")
        if not org_id:
            print("ERROR: --org-id is required for public-providers", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/sso/providers/{org_id}/public")

    elif resource == "connections":
        result = tfo_request("/sso/connections")

    else:
        print(f"ERROR: unknown resource '{resource}'. Valid: providers, provider-detail, public-providers, connections")
        sys.exit(1)

    output_json(result)


if __name__ == "__main__":
    main()
