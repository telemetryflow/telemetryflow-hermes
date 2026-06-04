#!/usr/bin/env python3
"""Query TFO infrastructure monitoring.

Covers: infra-overview, infra-cpu, infra-memory, infra-storage, infra-network

Usage:
  python3 check_infra.py --resource overview
  python3 check_infra.py --resource cpu
  python3 check_infra.py --resource memory
  python3 check_infra.py --resource storage
  python3 check_infra.py --resource network
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _shared import output_json, parse_args, tfo_request


def main():
    args = parse_args()
    resource = args.get("resource", "overview")

    valid = {"overview", "cpu", "memory", "storage", "network"}
    if resource not in valid:
        print(f"ERROR: unknown resource '{resource}'. Valid: {', '.join(sorted(valid))}")
        sys.exit(1)

    result = tfo_request(f"/monitoring/vm/{resource}")
    output_json(result)


if __name__ == "__main__":
    main()
