#!/usr/bin/env python3
"""Update a TelemetryFlow alert rule. Requires human approval.

Usage:
  python3 update_alert.py --rule-id <uuid> --threshold 90
  python3 update_alert.py --rule-id <uuid> --enabled false
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _shared import output_json, parse_args, tfo_request


def main():
    args = parse_args()
    rule_id = args.get("rule_id")
    threshold = args.get("threshold")
    enabled = args.get("enabled")
    severity = args.get("severity")

    if not rule_id:
        print("ERROR: --rule-id is required", file=sys.stderr)
        sys.exit(1)

    data = {}
    if threshold is not None:
        data["threshold"] = float(threshold)
    if enabled is not None:
        data["enabled"] = enabled.lower() == "true"
    if severity is not None:
        data["severity"] = severity

    if not data:
        print("ERROR: at least one update field is required (--threshold, --enabled, --severity)")
        sys.exit(1)

    print(f"PROPOSAL: Update alert rule '{rule_id}'")
    print(f"  Changes: {data}")
    print("Risk: LOW - alert configuration change only")

    print("Awaiting human approval...")
    result = tfo_request(f"/alerts/rules/{rule_id}", method="PATCH", data=data)
    output_json(result)


if __name__ == "__main__":
    main()
