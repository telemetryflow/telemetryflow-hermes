#!/usr/bin/env python3
"""Shared utilities for TelemetryFlow Hermes tools."""

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

ALLOWED_URL_SCHEMES = {"http", "https"}


def _validate_url(url):
    scheme = url.split("://")[0].lower() if "://" in url else ""
    if scheme not in ALLOWED_URL_SCHEMES:
        print(f"ERROR: Blocked URL scheme '{scheme}' — only {ALLOWED_URL_SCHEMES} allowed", file=sys.stderr)
        sys.exit(1)


def get_api_url():
    return os.environ.get("TELEMETRYFLOW_API_URL", "http://localhost:3000/api/v2")


def get_api_key():
    key = os.environ.get("TELEMETRYFLOW_API_KEY", "")
    if not key:
        print("ERROR: TELEMETRYFLOW_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    return key


def tfo_request(path, method="GET", data=None, params=None):
    base = get_api_url().rstrip("/")
    url = f"{base}{path}"
    if params:
        qs = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
        if qs:
            url = f"{url}?{qs}"

    headers = {
        "Authorization": f"Bearer {get_api_key()}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    _validate_url(url)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            if resp.status == 204:
                return None
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code}: {err_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def clickhouse_query(sql, fmt="JSON"):
    return tfo_request(
        "/telemetry/query",
        method="POST",
        data={
            "sql": sql,
            "format": fmt,
        },
    )


def parse_args():
    args = {}
    i = 1
    while i < len(sys.argv):
        if sys.argv[i].startswith("--"):
            key = sys.argv[i][2:]
            if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith("--"):
                args[key] = sys.argv[i + 1]
                i += 2
            else:
                args[key] = "true"
                i += 1
        else:
            i += 1
    return args


def output_json(data):
    print(json.dumps(data, indent=2, default=str))


def now_iso():
    return datetime.now(timezone.utc).isoformat()


CONTEXT_TYPES = [
    "metrics",
    "logs",
    "traces",
    "exemplars",
    "correlations",
    "alerts",
    "alert-rules",
    "agents",
    "uptime",
    "status-page",
    "kubernetes-overview",
    "kubernetes-clusters",
    "kubernetes-namespaces",
    "kubernetes-nodes",
    "kubernetes-pods",
    "kubernetes-deployments",
    "kubernetes-pv",
    "kubernetes-api-server",
    "kubernetes-coredns",
    "infra-overview",
    "infra-cpu",
    "infra-memory",
    "infra-storage",
    "infra-network",
    "service-map",
    "network-map",
    "dashboard",
    "reports",
    "iam",
    "iam-users",
    "iam-roles",
    "iam-permissions",
    "iam-matrix",
    "iam-assignments",
    "tenancy",
    "tenancy-regions",
    "tenancy-organizations",
    "tenancy-workspaces",
    "tenancy-tenants",
    "audit",
    "retention",
    "subscription",
    "api-keys",
    "notifications",
    "data-masking",
    "system-setup",
    "system-channels",
    "ai-assistant",
    "account-profile",
    "account-security",
    "account-sessions",
    "account-notifications",
    "account-preferences",
    "account-organization",
    "anomaly-detection",
    "corrective-maintenance",
    "cost-optimization",
    "predictive-maintenance",
    "db-monitoring-inventory",
    "db-monitoring-clickhouse",
    "db-monitoring-mysql",
    "db-monitoring-postgresql",
    "db-monitoring-mongodb-community",
    "db-monitoring-mongodb-atlas",
    "db-monitoring-mssql",
    "db-monitoring-sqlite3",
    "db-monitoring-timescaledb",
    "db-monitoring-aurora",
    "db-monitoring-aws-rds-mysql",
    "db-monitoring-aws-rds-aurora",
    "db-monitoring-aws-rds-postgresql",
    "db-monitoring-aws-dynamodb",
    "db-monitoring-cockroachdb",
    "db-monitoring-qan",
]

INSIGHT_TYPES = ["chronology", "prediction", "recommendation", "root-cause", "pattern"]

PROVIDER_TYPES = [
    "anthropic",
    "claude",
    "openai",
    "google",
    "gemini",
    "deepseek",
    "qwen",
    "ollama",
    "mistral",
    "grok",
    "kimi",
    "zhipu",
    "mimo",
    "openrouter",
    "custom",
]
