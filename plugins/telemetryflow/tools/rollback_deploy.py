#!/usr/bin/env python3
"""Rollback a Kubernetes deployment via TFO API. Requires human approval.

Usage:
  python3 rollback_deploy.py --name payments-api --namespace production
  python3 rollback_deploy.py --name payments-api --namespace production --revision 2
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _shared import output_json, parse_args, tfo_request


def main():
    args = parse_args()
    name = args.get("name")
    namespace = args.get("namespace", "default")
    revision = args.get("revision")

    if not name:
        print("ERROR: --name is required", file=sys.stderr)
        sys.exit(1)

    print(f"PROPOSAL: Rollback deployment '{name}' in namespace '{namespace}'")
    if revision:
        print(f"  Target revision: {revision}")
    print("Risk: LOW - rollback to known-good version (reversible)")

    data = {"name": name, "namespace": namespace}
    if revision:
        data["revision"] = int(revision)

    print("Awaiting human approval...")
    result = tfo_request("/kubernetes/deployments/rollback", method="POST", data=data)
    output_json(result)


if __name__ == "__main__":
    main()
