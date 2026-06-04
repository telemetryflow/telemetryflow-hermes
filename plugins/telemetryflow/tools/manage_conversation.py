#!/usr/bin/env python3
"""Manage TFO LLM chat conversations.

Usage:
  python3 manage_conversation.py --action list
  python3 manage_conversation.py --action list --context-type logs
  python3 manage_conversation.py --action get --conversation-id <uuid>
  python3 manage_conversation.py --action archive --conversation-id <uuid>
  python3 manage_conversation.py --action delete --conversation-id <uuid>
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _shared import output_json, parse_args, tfo_request


def main():
    args = parse_args()
    action = args.get("action", "list")
    conversation_id = args.get("conversation_id", "")

    if action == "list":
        params = {
            "page": args.get("page", "1"),
            "pageSize": args.get("page_size", "20"),
        }
        if args.get("context_type"):
            params["contextType"] = args["context_type"]
        if args.get("search"):
            params["search"] = args["search"]
        if args.get("is_archived"):
            params["isArchived"] = args["is_archived"]
        result = tfo_request("/llm/chat/conversations", params=params)
        output_json(result)

    elif action == "get":
        if not conversation_id:
            print("ERROR: --conversation-id is required for get", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/llm/chat/conversations/{conversation_id}")
        output_json(result)

    elif action == "archive":
        if not conversation_id:
            print("ERROR: --conversation-id is required for archive", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/llm/chat/conversations/{conversation_id}/archive", method="POST")
        output_json(result)

    elif action == "delete":
        if not conversation_id:
            print("ERROR: --conversation-id is required for delete", file=sys.stderr)
            sys.exit(1)
        tfo_request(f"/llm/chat/conversations/{conversation_id}", method="DELETE")
        print("Conversation deleted")

    else:
        print(f"ERROR: unknown action '{action}'. Valid: list, get, archive, delete")
        sys.exit(1)


if __name__ == "__main__":
    main()
