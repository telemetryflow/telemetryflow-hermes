#!/usr/bin/env python3
"""Scale a Kubernetes deployment via TFO API. Requires human approval.

Usage:
  python3 scale_deployment.py --name payments-api --namespace production --replicas 3
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _shared import output_json, parse_args, tfo_request


def main():
    args = parse_args()
    name = args.get("name")
    namespace = args.get("namespace", "default")
    replicas = int(args.get("replicas", "1"))

    if not name:
        print("ERROR: --name is required", file=sys.stderr)
        sys.exit(1)

    print(f"PROPOSAL: Scale deployment '{name}' in namespace '{namespace}' to {replicas} replicas")
    print("Risk: MEDIUM - cost impact, may not solve root cause")
    print("Awaiting human approval...")

    result = tfo_request(
        "/kubernetes/deployments/scale",
        method="POST",
        data={
            "name": name,
            "namespace": namespace,
            "replicas": replicas,
        },
    )
    output_json(result)


if __name__ == "__main__":
    main()
