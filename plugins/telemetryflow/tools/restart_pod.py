#!/usr/bin/env python3
"""Restart Kubernetes pods via TFO API. Requires human approval.

Usage:
  python3 restart_pod.py --deployment payments-api --namespace production
  python3 restart_pod.py --pod payments-api-7b8cf-abc --namespace production
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _shared import output_json, parse_args, tfo_request


def main():
    args = parse_args()
    deployment = args.get("deployment", "")
    pod = args.get("pod", "")
    namespace = args.get("namespace", "default")

    if not deployment and not pod:
        print("ERROR: --deployment or --pod is required", file=sys.stderr)
        sys.exit(1)

    if deployment:
        print(f"PROPOSAL: Restart deployment '{deployment}' in namespace '{namespace}'")
        print("Risk: HIGH - may lose in-flight requests, temporary disruption")
        result = tfo_request(
            "/kubernetes/deployments/restart",
            method="POST",
            data={"name": deployment, "namespace": namespace},
        )
    else:
        print(f"PROPOSAL: Delete pod '{pod}' in namespace '{namespace}' (will restart)")
        print("Risk: HIGH - single pod disruption")
        result = tfo_request(
            "/kubernetes/pods/restart",
            method="POST",
            data={"name": pod, "namespace": namespace},
        )

    print("Awaiting human approval...")
    output_json(result)


if __name__ == "__main__":
    main()
