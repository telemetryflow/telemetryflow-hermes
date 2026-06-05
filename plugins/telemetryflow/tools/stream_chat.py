#!/usr/bin/env python3
"""Send a streaming chat message to TFO LLM (SSE).

Usage:
  python3 stream_chat.py --message "Analyze current system health" --context-type metrics
  python3 stream_chat.py --message "Why is auth-service failing?" --context-type kubernetes-pods
"""

import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(__file__))
from _shared import CONTEXT_TYPES, _validate_url, get_api_key, get_api_url, now_iso, parse_args


def main():
    args = parse_args()
    message = args.get("message")
    context_type = args.get("context_type", "metrics")
    provider_id = args.get("provider_id")
    conversation_id = args.get("conversation_id")

    if not message:
        print("ERROR: --message is required", file=sys.stderr)
        sys.exit(1)

    if context_type not in CONTEXT_TYPES:
        print(f"ERROR: invalid context_type. Must be one of: {', '.join(CONTEXT_TYPES[:10])}...", file=sys.stderr)
        sys.exit(1)

    from datetime import datetime, timedelta, timezone

    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)

    data = {
        "message": message,
        "contextType": context_type,
        "timeFrom": one_hour_ago.isoformat(),
        "timeTo": now_iso(),
    }
    if provider_id:
        data["providerId"] = provider_id
    if conversation_id:
        data["conversationId"] = conversation_id

    url = f"{get_api_url()}/llm/chat/stream"
    headers = {
        "Authorization": f"Bearer {get_api_key()}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
    }

    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
    _validate_url(url)

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            conversation_id_out = None
            for line in resp:
                decoded = line.decode("utf-8").strip()
                if not decoded.startswith("data: "):
                    continue
                payload = decoded[6:]
                try:
                    event = json.loads(payload)
                except json.JSONDecodeError:
                    continue

                if event.get("type") == "start":
                    conversation_id_out = event.get("conversationId")
                elif event.get("type") == "chunk":
                    print(event.get("content", ""), end="", flush=True)
                elif event.get("type") == "end":
                    print()
                    if event.get("messageId"):
                        print(f"[messageId: {event['messageId']}]", file=sys.stderr)
                    if event.get("latencyMs"):
                        print(f"[latency: {event['latencyMs']}ms]", file=sys.stderr)
                elif event.get("type") == "error":
                    print(f"\nERROR: {event.get('message', 'Stream failed')}", file=sys.stderr)
                    sys.exit(1)

            if conversation_id_out:
                print(f"[conversationId: {conversation_id_out}]", file=sys.stderr)

    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode('utf-8', errors='replace')}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
