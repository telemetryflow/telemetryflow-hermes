#!/usr/bin/env python3
"""Generate AI insight using TFO's /api/v2/llm/insights endpoints.

Insight types: root-cause, chronology, prediction, recommendation, pattern

Usage:
  python3 generate_insight.py --insight-type root-cause --context-type alerts --context-id <alert-uuid>
  python3 generate_insight.py --insight-type chronology --context-type kubernetes-pods
  python3 generate_insight.py --insight-type prediction --context-type metrics
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _shared import CONTEXT_TYPES, INSIGHT_TYPES, output_json, parse_args, tfo_request


def main():
    args = parse_args()
    insight_type = args.get("insight_type", "root-cause")
    context_type = args.get("context_type", "metrics")
    context_id = args.get("context_id")
    provider_id = args.get("provider_id")
    time_from = args.get("time_from")
    time_to = args.get("time_to")
    additional_context = args.get("additional_context")

    if insight_type not in INSIGHT_TYPES:
        print(f"ERROR: invalid insight_type. Valid: {', '.join(INSIGHT_TYPES)}", file=sys.stderr)
        sys.exit(1)

    if context_type not in CONTEXT_TYPES:
        print(f"ERROR: invalid context_type. Valid: {', '.join(CONTEXT_TYPES[:10])}...", file=sys.stderr)
        sys.exit(1)

    data = {
        "insightType": insight_type,
        "contextType": context_type,
    }
    if context_id:
        data["contextId"] = context_id
    if provider_id:
        data["providerId"] = provider_id
    if time_from:
        data["timeFrom"] = time_from
    if time_to:
        data["timeTo"] = time_to
    if additional_context:
        import json

        try:
            data["additionalContext"] = json.loads(additional_context)
        except json.JSONDecodeError:
            data["additionalContext"] = {"note": additional_context}

    endpoint = f"/llm/insights/{insight_type}"
    result = tfo_request(endpoint, method="POST", data=data)
    output_json(result)


if __name__ == "__main__":
    main()
