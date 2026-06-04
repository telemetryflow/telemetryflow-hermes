#!/usr/bin/env python3
"""Query TFO uptime monitoring: monitors, checks, stats, SSL, status pages, incidents.

Usage:
  python3 check_uptime.py --resource monitors
  python3 check_uptime.py --resource monitors --monitor-id <id>
  python3 check_uptime.py --resource stats --monitor-id <id>
  python3 check_uptime.py --resource checks --monitor-id <id>
  python3 check_uptime.py --resource daily-stats --monitor-id <id>
  python3 check_uptime.py --resource hourly-stats --monitor-id <id>
  python3 check_uptime.py --resource ssl-summary
  python3 check_uptime.py --resource ssl-trend --monitor-id <id>
  python3 check_uptime.py --resource status-pages
  python3 check_uptime.py --resource incidents --status-page-id <id>
  python3 check_uptime.py --resource subscribers --status-page-id <id>
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _shared import output_json, parse_args, tfo_request


def main():
    args = parse_args()
    resource = args.get("resource", "monitors")
    monitor_id = args.get("monitor_id", "")
    status_page_id = args.get("status_page_id", "")

    if resource == "monitors":
        if monitor_id:
            result = tfo_request(f"/monitoring/uptime/monitors/{monitor_id}")
        else:
            result = tfo_request("/monitoring/uptime/monitors")

    elif resource == "stats":
        if not monitor_id:
            print("ERROR: --monitor-id is required for stats", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/monitoring/uptime/monitors/{monitor_id}/stats")

    elif resource == "checks":
        if not monitor_id:
            print("ERROR: --monitor-id is required for checks", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/monitoring/uptime/monitors/{monitor_id}/checks")

    elif resource == "daily-stats":
        if not monitor_id:
            print("ERROR: --monitor-id is required for daily-stats", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/monitoring/uptime/monitors/{monitor_id}/daily-stats")

    elif resource == "hourly-stats":
        if not monitor_id:
            print("ERROR: --monitor-id is required for hourly-stats", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/monitoring/uptime/monitors/{monitor_id}/hourly-stats")

    elif resource == "ssl-summary":
        result = tfo_request("/monitoring/uptime/monitors/ssl-summary")

    elif resource == "ssl-trend":
        if not monitor_id:
            print("ERROR: --monitor-id is required for ssl-trend", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/monitoring/uptime/monitors/{monitor_id}/ssl-trend")

    elif resource == "status-pages":
        if status_page_id:
            result = tfo_request(f"/monitoring/status-pages/{status_page_id}")
        else:
            result = tfo_request("/monitoring/status-pages")

    elif resource == "incidents":
        if not status_page_id:
            print("ERROR: --status-page-id is required for incidents", file=sys.stderr)
            sys.exit(1)
        params = {}
        if args.get("status"):
            params["status"] = args["status"]
        result = tfo_request(f"/monitoring/status-pages/{status_page_id}/incidents", params=params)

    elif resource == "subscribers":
        if not status_page_id:
            print("ERROR: --status-page-id is required for subscribers", file=sys.stderr)
            sys.exit(1)
        result = tfo_request(f"/monitoring/status-pages/{status_page_id}/subscribers")

    else:
        print(
            f"ERROR: unknown resource '{resource}'. Valid: monitors, stats, checks, daily-stats, hourly-stats, ssl-summary, ssl-trend, status-pages, incidents, subscribers"
        )
        sys.exit(1)

    output_json(result)


if __name__ == "__main__":
    main()
