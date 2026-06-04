#!/usr/bin/env python3
"""Query LLM usage analytics from TFO ClickHouse.

Queries the llm_usage_analytics table and materialized interval views.

Usage:
  python3 query_llm_usage.py --action summary --duration 24h
  python3 query_llm_usage.py --action by-provider --duration 7d
  python3 query_llm_usage.py --action by-model --duration 7d
  python3 query_llm_usage.py --action by-context --duration 24h
  python3 query_llm_usage.py --action top-users --duration 7d --limit 10
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _shared import clickhouse_query, output_json, parse_args

DURATION_MAP = {
    "1h": "INTERVAL 1 HOUR",
    "6h": "INTERVAL 6 HOUR",
    "24h": "INTERVAL 24 HOUR",
    "7d": "INTERVAL 7 DAY",
    "30d": "INTERVAL 30 DAY",
}


def main():
    args = parse_args()
    action = args.get("action", "summary")
    duration = args.get("duration", "24h")
    limit = int(args.get("limit", "20"))

    interval = DURATION_MAP.get(duration, "INTERVAL 24 HOUR")

    if action == "summary":
        sql = f"""
            SELECT
              count() AS total_requests,
              sum(total_tokens) AS total_tokens,
              sum(prompt_tokens) AS total_prompt_tokens,
              sum(completion_tokens) AS total_completion_tokens,
              avg(latency_ms) AS avg_latency_ms,
              quantile(0.95)(latency_ms) AS p95_latency_ms,
              uniqExact(provider_type) AS provider_count,
              uniqExact(model_id) AS model_count
            FROM llm_usage_analytics
            WHERE timestamp >= now() - {interval}
            FORMAT JSON
        """

    elif action == "by-provider":
        sql = f"""
            SELECT
              provider_type,
              count() AS requests,
              sum(total_tokens) AS total_tokens,
              avg(latency_ms) AS avg_latency_ms,
              sum(total_tokens) * 1.0 / count() AS avg_tokens_per_request
            FROM llm_usage_analytics
            WHERE timestamp >= now() - {interval}
            GROUP BY provider_type
            ORDER BY total_tokens DESC
            LIMIT {limit}
            FORMAT JSON
        """

    elif action == "by-model":
        sql = f"""
            SELECT
              model_id,
              provider_type,
              count() AS requests,
              sum(total_tokens) AS total_tokens,
              avg(latency_ms) AS avg_latency_ms
            FROM llm_usage_analytics
            WHERE timestamp >= now() - {interval}
            GROUP BY model_id, provider_type
            ORDER BY total_tokens DESC
            LIMIT {limit}
            FORMAT JSON
        """

    elif action == "by-context":
        sql = f"""
            SELECT
              context_type,
              count() AS requests,
              sum(total_tokens) AS total_tokens,
              avg(latency_ms) AS avg_latency_ms
            FROM llm_usage_analytics
            WHERE timestamp >= now() - {interval}
            GROUP BY context_type
            ORDER BY total_tokens DESC
            LIMIT {limit}
            FORMAT JSON
        """

    elif action == "top-users":
        sql = f"""
            SELECT
              user_id,
              count() AS requests,
              sum(total_tokens) AS total_tokens,
              uniqExact(context_type) AS context_types_used
            FROM llm_usage_analytics
            WHERE timestamp >= now() - {interval}
            GROUP BY user_id
            ORDER BY total_tokens DESC
            LIMIT {limit}
            FORMAT JSON
        """

    elif action == "interval":
        view = args.get("view", "5m")
        view_map = {"5m": "llm_usage_5m", "15m": "llm_usage_15m", "6h": "llm_usage_6h"}
        table = view_map.get(view, "llm_usage_5m")
        sql = f"""
            SELECT
              bucket,
              sum(total_tokens) AS tokens,
              count() AS requests,
              avg(avg_latency) AS avg_latency_ms
            FROM {table}
            WHERE bucket >= now() - {interval}
            GROUP BY bucket
            ORDER BY bucket
            FORMAT JSON
        """

    else:
        print(f"ERROR: unknown action '{action}'")
        print("Valid: summary, by-provider, by-model, by-context, top-users, interval")
        sys.exit(1)

    result = clickhouse_query(sql)
    output_json(result)


if __name__ == "__main__":
    main()
