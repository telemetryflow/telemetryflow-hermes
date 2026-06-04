"""Tests for query_metrics.py tool."""

import json
import os
from unittest import mock


def _import_tool():
    import importlib

    import query_metrics

    importlib.reload(query_metrics)
    return query_metrics


class TestQueryMetrics:
    def test_basic_query(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        from tests.conftest import SAMPLE_METRICS

        mock_resp.read.return_value = json.dumps({"data": SAMPLE_METRICS, "rows": len(SAMPLE_METRICS)}).encode("utf-8")

        with mock.patch("sys.argv", ["query_metrics.py", "--service", "payments-api"]):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert "data" in output
        call_args = m.call_args
        body = json.loads(call_args[0][0].data)
        assert "metrics_5m" in body.get("sql", "")

    def test_with_metric(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": [], "rows": 0}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            [
                "query_metrics.py",
                "--service",
                "payments-api",
                "--metric",
                "process.memory.usage",
            ],
        ):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert "process.memory.usage" in body["sql"]
        assert "p95" in body["sql"]

    def test_with_duration_and_resolution(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": [], "rows": 0}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            [
                "query_metrics.py",
                "--service",
                "payments-api",
                "--duration",
                "6h",
                "--resolution",
                "1h",
            ],
        ):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert "metrics_1h" in body["sql"]
        assert "INTERVAL 6 HOUR" in body["sql"]

    def test_with_workspace_id(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": [], "rows": 0}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            [
                "query_metrics.py",
                "--service",
                "payments-api",
                "--workspace_id",
                "ws_custom",
            ],
        ):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert "ws_custom" in body["sql"]

    def test_missing_service_exits(self, mock_exit):
        with mock.patch("sys.argv", ["query_metrics.py"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_no_api_key_exits(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True):
            with mock.patch("sys.argv", ["query_metrics.py", "--service", "test"]):
                tool = _import_tool()
                tool.main()
                mock_exit.assert_called()

    def test_api_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch("sys.argv", ["query_metrics.py", "--service", "test"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_default_resolution_is_5m(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["query_metrics.py", "--service", "test"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert "metrics_5m" in body["sql"]

    def test_default_duration_is_1h(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["query_metrics.py", "--service", "test"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert "INTERVAL 1 HOUR" in body["sql"]
