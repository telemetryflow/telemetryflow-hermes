#!/usr/bin/env python3
"""Manage TFO LLM provider configurations.

Usage:
  python3 manage_provider.py --action list
  python3 manage_provider.py --action get --provider-id <uuid>
  python3 manage_provider.py --action create --name "Claude" --type anthropic --api-key sk-xxx --model claude-sonnet-4-5
  python3 manage_provider.py --action validate --provider-id <uuid>
  python3 manage_provider.py --action test-key --type anthropic --api-key sk-xxx
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _shared import PROVIDER_TYPES, output_json, parse_args, tfo_request


def main():
    args = parse_args()
    action = args.get("action", "list")
    provider_id = args.get("provider_id", "")

    if action == "list":
        result = tfo_request(
            "/llm/providers",
            params={
                "page": args.get("page", "1"),
                "pageSize": args.get("page_size", "20"),
            },
        )
        output_json(result)

    elif action == "get":
        if not provider_id:
            print("ERROR: --provider-id is required for get", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/llm/providers/{provider_id}")
        output_json(result)

    elif action == "default":
        result = tfo_request("/llm/providers/default")
        output_json(result)

    elif action == "create":
        name = args.get("name")
        ptype = args.get("type", "anthropic")
        api_key = args.get("api_key", "")
        model_id = args.get("model", "")
        base_url = args.get("base_url", "")
        temperature = float(args.get("temperature", "0.7"))
        max_tokens = int(args.get("max_tokens", "4096"))
        top_p = float(args.get("top_p", "1.0"))
        is_default = args.get("is_default", "false").lower() == "true"

        if not name or not api_key or not model_id:
            print("ERROR: --name, --api-key, and --model are required for create", file=sys.stderr)
            sys.exit(1)
        if ptype not in PROVIDER_TYPES:
            print(f"ERROR: invalid type. Valid: {', '.join(PROVIDER_TYPES)}", file=sys.stderr)
            sys.exit(1)

        data = {
            "name": name,
            "providerType": ptype,
            "apiKey": api_key,
            "modelId": model_id,
            "temperature": temperature,
            "maxTokens": max_tokens,
            "topP": top_p,
            "isDefault": is_default,
        }
        if base_url:
            data["baseUrl"] = base_url

        result = tfo_request("/llm/providers", method="POST", data=data)
        output_json(result)

    elif action == "validate":
        if not provider_id:
            print("ERROR: --provider-id is required for validate", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/llm/providers/{provider_id}/validate", method="POST")
        output_json(result)

    elif action == "test-key":
        ptype = args.get("type", "anthropic")
        api_key = args.get("api_key", "")
        base_url = args.get("base_url", "")

        if not api_key:
            print("ERROR: --api-key is required for test-key", file=sys.stderr)
            sys.exit(1)

        data = {
            "providerType": ptype,
            "apiKey": api_key,
        }
        if base_url:
            data["baseUrl"] = base_url

        result = tfo_request("/llm/providers/test-key", method="POST", data=data)
        output_json(result)

    elif action == "set-default":
        if not provider_id:
            print("ERROR: --provider-id is required for set-default", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/llm/providers/{provider_id}/set-default", method="POST")
        output_json(result)

    else:
        print(f"ERROR: unknown action '{action}'. Valid: list, get, default, create, validate, test-key, set-default")
        sys.exit(1)


if __name__ == "__main__":
    main()
