"""Integration tests for full TelemetryFlow Hermes tool pipeline."""

import json
from unittest import mock


def _import(module_name):
    import importlib

    mod = __import__(module_name)
    importlib.reload(mod)
    return mod


def _extract_json(text):
    decoder = json.JSONDecoder()
    idx = 0
    while idx < len(text):
        try:
            obj, end = decoder.raw_decode(text, idx)
            if isinstance(obj, dict):
                return obj
            idx = end
        except json.JSONDecodeError:
            idx += 1
    return None


class TestMetricsPipeline:
    def test_query_metrics_end_to_end(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps(
            {
                "data": [
                    {
                        "timestamp": "2026-06-04T03:45:00Z",
                        "service": "payments-api",
                        "metric": "cpu_usage",
                        "value": 75.2,
                    },
                ],
                "rows": 1,
            }
        ).encode("utf-8")

        with mock.patch("sys.argv", ["query_metrics.py", "--service", "payments-api"]):
            tool = _import("query_metrics")
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert output["rows"] == 1
        assert output["data"][0]["service"] == "payments-api"


class TestLogsPipeline:
    def test_search_logs(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps(
            {
                "data": [
                    {
                        "timestamp": "2026-06-04T03:45:12Z",
                        "severity": "ERROR",
                        "service": "payments-api",
                        "trace_id": "abc123",
                        "message": "OOMKilled",
                    },
                ],
                "rows": 1,
            }
        ).encode("utf-8")

        with mock.patch("sys.argv", ["search_logs.py", "--service", "payments-api", "--severity", "ERROR"]):
            tool = _import("search_logs")
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert output["rows"] == 1
        assert output["data"][0]["trace_id"] == "abc123"


class TestTracesPipeline:
    def test_list_traces_by_id(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps(
            {
                "data": [
                    {"trace_id": "abc123", "span_id": "span1", "service_name": "payments-api", "duration_ms": 650},
                ],
                "rows": 1,
            }
        ).encode("utf-8")

        with mock.patch("sys.argv", ["list_traces.py", "--trace_id", "abc123"]):
            tool = _import("list_traces")
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert output["data"][0]["trace_id"] == "abc123"


class TestK8sPipeline:
    def test_check_k8s_deployments(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps(
            {
                "data": [{"name": "payments-api", "namespace": "production", "replicas": 1, "status": "Running"}],
            }
        ).encode("utf-8")

        with mock.patch("sys.argv", ["check_k8s.py", "--resource", "deployments", "--namespace", "production"]):
            tool = _import("check_k8s")
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert len(output["data"]) == 1

    def test_scale_deployment(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps(
            {
                "data": {"name": "payments-api", "replicas": 3, "scaled": True},
            }
        ).encode("utf-8")

        with mock.patch(
            "sys.argv",
            ["scale_deployment.py", "--name", "payments-api", "--namespace", "production", "--replicas", "3"],
        ):
            tool = _import("scale_deployment")
            tool.main()

        raw = capture_stdout.getvalue()
        output = _extract_json(raw)
        assert output["data"]["replicas"] == 3
        body = json.loads(m.call_args[0][0].data)
        assert body["name"] == "payments-api"


class TestChatPipeline:
    def test_chat_with_metrics(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps(
            {
                "data": {"response": "Memory spike detected", "messageId": "msg-1", "conversationId": "conv-1"},
            }
        ).encode("utf-8")

        with mock.patch(
            "sys.argv", ["chat_with_context.py", "--message", "Analyze memory", "--context_type", "metrics"]
        ):
            tool = _import("chat_with_context")
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert output["data"]["response"] == "Memory spike detected"


class TestInsightPipeline:
    def test_generate_root_cause(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps(
            {
                "data": {
                    "id": "ins-1",
                    "insightType": "root-cause",
                    "content": "Memory spike caused by deploy",
                    "confidence": 0.92,
                },
            }
        ).encode("utf-8")

        with mock.patch(
            "sys.argv", ["generate_insight.py", "--insight_type", "root-cause", "--context_type", "metrics"]
        ):
            tool = _import("generate_insight")
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert output["data"]["insightType"] == "root-cause"


class TestAlertPipeline:
    def test_update_alert_threshold(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps(
            {"data": {"rule_id": "rule-1", "threshold": 95.0, "enabled": True}}
        ).encode("utf-8")

        with mock.patch("sys.argv", ["update_alert.py", "--rule_id", "rule-1", "--threshold", "95"]):
            tool = _import("update_alert")
            tool.main()

        raw = capture_stdout.getvalue()
        output = _extract_json(raw)
        assert output["data"]["threshold"] == 95.0
        body = json.loads(m.call_args[0][0].data)
        assert body["threshold"] == 95.0


class TestProviderPipeline:
    def test_list_providers(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps(
            {
                "data": [
                    {"id": "prov-1", "name": "Production Claude", "isDefault": False},
                    {"id": "prov-2", "name": "Dev GLM", "isDefault": False},
                ],
            }
        ).encode("utf-8")

        with mock.patch("sys.argv", ["manage_provider.py", "--action", "list"]):
            tool = _import("manage_provider")
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert len(output["data"]) == 2

    def test_set_default_provider(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"id": "prov-1", "isDefault": True}}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_provider.py", "--action", "set-default", "--provider_id", "prov-1"]):
            tool = _import("manage_provider")
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert output["data"]["isDefault"] is True
