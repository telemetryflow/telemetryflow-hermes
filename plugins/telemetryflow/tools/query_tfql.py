#!/usr/bin/env python3
"""Query TFO unified query engine (TFQL): metrics, logs, traces.

Usage:
  python3 query_tfql.py --signal metrics --metric-name http_requests_total
  python3 query_tfql.py --signal metrics --action names
  python3 query_tfql.py --signal metrics --action labels --label-name service
  python3 query_tfql.py --signal logs --query "ERROR AND timeout"
  python3 query_tfql.py --signal logs --severity ERROR --service-name payments-api
  python3 query_tfql.py --signal logs --action severity-distribution
  python3 query_tfql.py --signal traces --service-name payments-api
  python3 query_tfql.py --signal traces --trace-id <trace-id>
  python3 query_tfql.py --signal traces --action summaries
  python3 query_tfql.py --signal traces --action services
  python3 query_tfql.py --signal traces --action operations
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _shared import output_json, parse_args, tfo_request


def main():
    args = parse_args()
    signal = args.get("signal", "metrics")
    action = args.get("action", "")

    if signal == "metrics":
        if action == "names":
            params = {}
            if args.get("prefix"):
                params["prefix"] = args["prefix"]
            result = tfo_request("/query/signals/metrics/names", params=params)
        elif action == "labels":
            label_name = args.get("label_name", "")
            if not label_name:
                print("ERROR: --label-name is required for labels", file=sys.stderr)
                sys.exit(1)
            result = tfo_request(f"/query/signals/metrics/labels/{label_name}")
        else:
            data = {}
            if args.get("metric_name"):
                data["metricName"] = args["metric_name"]
            if args.get("aggregation"):
                data["aggregation"] = args["aggregation"]
            if args.get("interval"):
                data["interval"] = args["interval"]
            if args.get("service_name"):
                data["serviceName"] = args["service_name"]
            if args.get("percentiles"):
                data["percentiles"] = args["percentiles"]
            result = tfo_request("/query/signals/metrics", method="POST", data=data)

    elif signal == "logs":
        if action == "severity-distribution":
            result = tfo_request("/query/signals/logs/severity-levels")
        elif action == "count-by-severity":
            data = {}
            if args.get("query"):
                data["query"] = args["query"]
            result = tfo_request("/query/signals/logs/count-by-severity", method="POST", data=data)
        else:
            data = {}
            if args.get("query"):
                data["query"] = args["query"]
            if args.get("severity"):
                data["severityText"] = args["severity"]
            if args.get("service_name"):
                data["serviceName"] = args["service_name"]
            if args.get("trace_id"):
                data["traceId"] = args["trace_id"]
            result = tfo_request("/query/signals/logs", method="POST", data=data)

    elif signal == "traces":
        if action == "summaries":
            result = tfo_request("/query/signals/traces/summaries", method="POST", data={})
        elif action == "services":
            result = tfo_request("/query/signals/traces/services")
        elif action == "operations":
            result = tfo_request("/query/signals/traces/operations")
        else:
            trace_id = args.get("trace_id", "")
            if trace_id:
                result = tfo_request(f"/query/signals/traces/{trace_id}")
            else:
                data = {}
                if args.get("service_name"):
                    data["serviceName"] = args["service_name"]
                if args.get("span_name"):
                    data["spanName"] = args["span_name"]
                if args.get("status_code"):
                    data["statusCode"] = args["status_code"]
                if args.get("min_duration"):
                    data["minDuration"] = args["min_duration"]
                if args.get("max_duration"):
                    data["maxDuration"] = args["max_duration"]
                result = tfo_request("/query/signals/traces", method="POST", data=data)

    else:
        print(f"ERROR: unknown signal '{signal}'. Valid: metrics, logs, traces")
        sys.exit(1)

    output_json(result)


if __name__ == "__main__":
    main()
