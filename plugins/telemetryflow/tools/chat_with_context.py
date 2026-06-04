#!/usr/bin/env python3
"""Send a chat message to TFO LLM with telemetry context.

Uses TFO's /api/v2/llm/chat/message endpoint with ContextCollector
for automatic telemetry context injection.

Usage:
  python3 chat_with_context.py --message "Analyze recent error logs" --context-type logs
  python3 chat_with_context.py --message "Why is payments-api slow?" --context-type kubernetes-pods --service payments-api
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _shared import CONTEXT_TYPES, now_iso, output_json, parse_args, tfo_request


def main():
    args = parse_args()
    message = args.get("message")
    context_type = args.get("context_type", "metrics")
    context_id = args.get("context_id")
    provider_id = args.get("provider_id")
    conversation_id = args.get("conversation_id")
    time_from = args.get("time_from")
    time_to = args.get("time_to")

    if not message:
        print("ERROR: --message is required", file=sys.stderr)
        sys.exit(1)

    if context_type not in CONTEXT_TYPES:
        print(f"ERROR: invalid context_type. Valid: {', '.join(CONTEXT_TYPES)}", file=sys.stderr)
        sys.exit(1)

    data = {
        "message": message,
        "contextType": context_type,
    }
    if context_id:
        data["contextId"] = context_id
    if provider_id:
        data["providerId"] = provider_id
    if conversation_id:
        data["conversationId"] = conversation_id
    if time_from:
        data["timeFrom"] = time_from
    else:
        from datetime import datetime, timedelta, timezone

        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        data["timeFrom"] = one_hour_ago.isoformat()
    if time_to:
        data["timeTo"] = time_to
    else:
        data["timeTo"] = now_iso()

    result = tfo_request("/llm/chat/message", method="POST", data=data)
    output_json(result)


if __name__ == "__main__":
    main()
