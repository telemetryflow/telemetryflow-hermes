#!/usr/bin/env python3
"""Query TFO Agent monitoring: registration, health, stats.

Usage:
  python3 check_agent.py --resource list
  python3 check_agent.py --resource list --status offline
  python3 check_agent.py --resource stats
  python3 check_agent.py --resource get --agent-id <id>
  python3 check_agent.py --resource health --agent-id <id>
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _shared import output_json, parse_args, tfo_request


def main():
    args = parse_args()
    resource = args.get("resource", "list")
    agent_id = args.get("agent_id", "")

    if resource == "list":
        params = {"page": args.get("page", "1"), "pageSize": args.get("page_size", "20")}
        for key in ("status", "type", "name", "host", "last_seen_within_minutes"):
            if args.get(key):
                params[key] = args[key]
        result = tfo_request("/monitoring/agents", params=params)

    elif resource == "stats":
        result = tfo_request("/monitoring/agents/stats")

    elif resource == "get":
        if not agent_id:
            print("ERROR: --agent-id is required for get", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/monitoring/agents/{agent_id}")

    elif resource == "health":
        if not agent_id:
            print("ERROR: --agent-id is required for health", file=sys.stderr)
            sys.exit(1)
        params = {}
        if args.get("from"):
            params["from"] = args["from"]
        if args.get("to"):
            params["to"] = args["to"]
        if args.get("limit"):
            params["limit"] = args["limit"]
        result = tfo_request(f"/monitoring/agents/{agent_id}/health", params=params)

    else:
        print(f"ERROR: unknown resource '{resource}'. Valid: list, stats, get, health")
        sys.exit(1)

    output_json(result)


if __name__ == "__main__":
    main()
