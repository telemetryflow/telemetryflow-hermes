#!/usr/bin/env python3
"""Query TFO account-scoped data: profile, security, sessions, preferences.

Usage:
  python3 query_account.py --resource profile
  python3 query_account.py --resource security
  python3 query_account.py --resource sessions
  python3 query_account.py --resource preferences
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _shared import output_json, parse_args, tfo_request


def main():
    args = parse_args()
    resource = args.get("resource", "profile")

    if resource == "profile":
        result = tfo_request("/account/profile")
    elif resource == "security":
        result = tfo_request("/account/security")
    elif resource == "sessions":
        result = tfo_request("/account/sessions")
    elif resource == "preferences":
        result = tfo_request("/account/preferences")
    else:
        print(f"ERROR: unknown resource '{resource}'. Valid: profile, security, sessions, preferences")
        sys.exit(1)

    output_json(result)


if __name__ == "__main__":
    main()
