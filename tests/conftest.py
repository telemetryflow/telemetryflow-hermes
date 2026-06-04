"""Shared test fixtures for TelemetryFlow Hermes plugin tools."""

import json
import os
import sys
from unittest import mock

import pytest

TOOLS_DIR = os.path.join(os.path.dirname(__file__), "..", "plugins", "telemetryflow", "tools")


@pytest.fixture(autouse=True)
def _setup_path():
    if TOOLS_DIR not in sys.path:
        sys.path.insert(0, TOOLS_DIR)
    yield
    [m for m in sys.modules if m.startswith("_shared") or m in sys.modules]
    for mod_name in list(sys.modules.keys()):
        if mod_name in (
            "_shared",
            "query_metrics",
            "search_logs",
            "list_traces",
            "get_exemplars",
            "query_correlations",
            "check_k8s",
            "check_infra",
            "check_db_monitoring",
            "check_uptime",
            "query_ai_intelligence",
            "query_platform",
            "query_account",
            "manage_data_masking",
            "chat_with_context",
            "stream_chat",
            "manage_conversation",
            "generate_insight",
            "query_llm_usage",
            "manage_provider",
            "scale_deployment",
            "restart_pod",
            "rollback_deploy",
            "update_alert",
        ):
            del sys.modules[mod_name]


@pytest.fixture
def mock_env():
    env = {
        "TELEMETRYFLOW_API_URL": "http://localhost:3000/api/v2",
        "TELEMETRYFLOW_API_KEY": "tfs_test_api_key_1234567890abcdef",
        "TELEMETRYFLOW_WORKSPACE_ID": "ws_test_123",
        "TELEMETRYFLOW_ORGANIZATION_ID": "org_test_456",
        "CLICKHOUSE_HOST": "localhost",
        "CLICKHOUSE_PORT": "9000",
        "CLICKHOUSE_USER": "hermes_readonly",
        "CLICKHOUSE_PASSWORD": "test_password",
        "CLICKHOUSE_DATABASE": "telemetryflow",
    }
    with mock.patch.dict(os.environ, env, clear=False):
        yield env


@pytest.fixture
def mock_urlopen():
    mock_response = mock.MagicMock()
    mock_response.status = 200
    mock_response.read.return_value = json.dumps({"status": "ok", "data": []}).encode("utf-8")
    mock_response.__enter__ = mock.MagicMock(return_value=mock_response)
    mock_response.__exit__ = mock.MagicMock(return_value=False)
    mock_response.headers = {"Content-Type": "application/json"}

    with mock.patch("urllib.request.urlopen", return_value=mock_response) as m:
        m.return_value = mock_response
        yield m, mock_response


@pytest.fixture
def mock_urlopen_error():
    import urllib.error

    error_response = mock.MagicMock()
    error_response.read.return_value = b'{"error": "Not Found"}'

    with mock.patch("urllib.request.urlopen") as m:
        m.side_effect = urllib.error.HTTPError(
            url="http://localhost:3000/api/v2/test",
            code=404,
            msg="Not Found",
            hdrs={},
            fp=error_response,
        )
        yield m


@pytest.fixture
def mock_urlopen_conn_error():
    import urllib.error

    with mock.patch("urllib.request.urlopen") as m:
        m.side_effect = urllib.error.URLError(reason="Connection refused")
        yield m


@pytest.fixture
def capture_stdout(capsys):
    yield CapstdOut(capsys)


class CapstdOut:
    def __init__(self, capsys):
        self._capsys = capsys

    def getvalue(self):
        return self._capsys.readouterr().out


@pytest.fixture
def mock_exit():
    with mock.patch("sys.exit") as m:
        yield m


def make_response(data, status=200):
    mock_resp = mock.MagicMock()
    mock_resp.status = status
    mock_resp.read.return_value = json.dumps(data).encode("utf-8")
    mock_resp.__enter__ = mock.MagicMock(return_value=mock_resp)
    mock_resp.__exit__ = mock.MagicMock(return_value=False)
    mock_resp.headers = {"Content-Type": "application/json"}
    return mock_resp


@pytest.fixture
def tfo_response_factory():
    return make_response


SAMPLE_METRICS = [
    {"timestamp": "2026-06-04T03:45:00Z", "service": "payments-api", "metric": "memory_usage", "value": 890.5},
    {"timestamp": "2026-06-04T03:46:00Z", "service": "payments-api", "metric": "memory_usage", "value": 895.2},
    {"timestamp": "2026-06-04T03:47:00Z", "service": "payments-api", "metric": "memory_usage", "value": 910.1},
]

SAMPLE_LOGS = [
    {"timestamp": "2026-06-04T03:45:12Z", "severity": "ERROR", "service": "payments-api", "message": "OOMKilled"},
    {"timestamp": "2026-06-04T03:45:45Z", "severity": "ERROR", "service": "payments-api", "message": "OOMKilled"},
]

SAMPLE_TRACES = [
    {
        "trace_id": "abc123",
        "span_id": "span1",
        "service": "payments-api",
        "duration_ms": 650,
        "operation": "POST /api/payments",
    },
    {
        "trace_id": "def456",
        "span_id": "span2",
        "service": "payments-api",
        "duration_ms": 820,
        "operation": "POST /api/payments",
    },
]

SAMPLE_EXEMPLARS = [
    {"metric": "memory_usage", "trace_id": "abc123", "value": 890.5, "timestamp": "2026-06-04T03:45:00Z"},
]

SAMPLE_CORRELATIONS = [
    {"metric_name": "memory_usage", "log_pattern": "OOMKilled", "trace_id": "abc123", "correlation_score": 0.95},
]

SAMPLE_PROVIDERS = [
    {
        "id": "prov-1",
        "name": "Production Claude",
        "providerType": "anthropic",
        "modelId": "claude-sonnet-4-5",
        "isActive": True,
        "isDefault": True,
    },
    {
        "id": "prov-2",
        "name": "Dev GLM",
        "providerType": "zhipu",
        "modelId": "glm-5.1",
        "isActive": True,
        "isDefault": False,
    },
]

SAMPLE_CONVERSATIONS = {
    "conversations": [
        {"id": "conv-1", "title": "Memory investigation", "contextType": "metrics", "isArchived": False},
        {"id": "conv-2", "title": "Log analysis", "contextType": "logs", "isArchived": True},
    ],
    "total": 2,
}

SAMPLE_INSIGHT = {
    "id": "ins-1",
    "insightType": "root-cause",
    "contextType": "metrics",
    "content": "Memory spike caused by v2.4.1 deploy exceeding 512MiB request.",
    "confidence": 0.92,
}

SAMPLE_K8S_PODS = [
    {"name": "payments-api-7b8cf", "namespace": "production", "status": "Running", "restarts": 3},
    {"name": "auth-service-9d2ef", "namespace": "production", "status": "Running", "restarts": 0},
]

SAMPLE_INFRA = [
    {"host": "node-1", "cpu_percent": 45.2, "memory_percent": 62.1, "storage_percent": 38.5},
    {"host": "node-2", "cpu_percent": 78.9, "memory_percent": 85.3, "storage_percent": 71.2},
]
