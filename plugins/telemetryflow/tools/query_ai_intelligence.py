#!/usr/bin/env python3
"""Query TFO AI Intelligence modules.

Covers: anomaly-detection, corrective-maintenance, predictive-maintenance, cost-optimization

Usage:
  python3 query_ai_intelligence.py --module anomaly-detection --action list
  python3 query_ai_intelligence.py --module anomaly-detection --action get --id <uuid>
  python3 query_ai_intelligence.py --module predictive-maintenance --action predictions
  python3 query_ai_intelligence.py --module cost-optimization --action recommendations
  python3 query_ai_intelligence.py --module corrective-maintenance --action plans
  python3 query_ai_intelligence.py --module anomaly-detection --action analyze --id <uuid>
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _shared import output_json, parse_args, tfo_request

MODULES = ["anomaly-detection", "corrective-maintenance", "predictive-maintenance", "cost-optimization"]


def main():
    args = parse_args()
    module = args.get("module", "anomaly-detection")
    action = args.get("action", "list")
    item_id = args.get("id", "")
    limit = int(args.get("limit", "20"))

    if module not in MODULES:
        print(f"ERROR: invalid module. Valid: {', '.join(MODULES)}")
        sys.exit(1)

    if module == "anomaly-detection":
        if action == "list":
            result = tfo_request(
                "/ai-intelligence/anomaly-detection/anomalies",
                params={
                    "page": args.get("page", "1"),
                    "pageSize": str(limit),
                    "severity": args.get("severity", ""),
                },
            )
        elif action == "get":
            result = tfo_request(f"/ai-intelligence/anomaly-detection/anomalies/{item_id}")
        elif action == "analyze":
            result = tfo_request(f"/ai-intelligence/anomaly-detection/anomalies/{item_id}/analyze", method="POST")
        else:
            print("Valid actions: list, get, analyze")
            sys.exit(1)

    elif module == "predictive-maintenance":
        if action in ("list", "predictions"):
            result = tfo_request(
                "/ai-intelligence/predictive-maintenance/predictions",
                params={
                    "page": args.get("page", "1"),
                    "pageSize": str(limit),
                },
            )
        elif action == "get":
            result = tfo_request(f"/ai-intelligence/predictive-maintenance/predictions/{item_id}")
        else:
            print("Valid actions: list, predictions, get")
            sys.exit(1)

    elif module == "cost-optimization":
        if action in ("list", "recommendations"):
            result = tfo_request(
                "/ai-intelligence/cost-optimization/recommendations",
                params={
                    "page": args.get("page", "1"),
                    "pageSize": str(limit),
                    "provider": args.get("provider", ""),
                },
            )
        elif action == "get":
            result = tfo_request(f"/ai-intelligence/cost-optimization/recommendations/{item_id}")
        else:
            print("Valid actions: list, recommendations, get")
            sys.exit(1)

    elif module == "corrective-maintenance":
        if action in ("list", "plans"):
            result = tfo_request(
                "/ai-intelligence/corrective-maintenance/plans",
                params={
                    "page": args.get("page", "1"),
                    "pageSize": str(limit),
                },
            )
        elif action == "get":
            result = tfo_request(f"/ai-intelligence/corrective-maintenance/plans/{item_id}")
        else:
            print("Valid actions: list, plans, get")
            sys.exit(1)

    output_json(result)


if __name__ == "__main__":
    main()
