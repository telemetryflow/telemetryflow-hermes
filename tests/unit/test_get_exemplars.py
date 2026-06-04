"""Tests for get_exemplars.py tool."""

import json
import os
from unittest import mock


def _import_tool():
    import importlib

    import get_exemplars

    importlib.reload(get_exemplars)
    return get_exemplars


class TestGetExemplars:
    def test_basic_query(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        from tests.conftest import SAMPLE_EXEMPLARS

        mock_resp.read.return_value = json.dumps({"data": SAMPLE_EXEMPLARS, "rows": len(SAMPLE_EXEMPLARS)}).encode(
            "utf-8"
        )

        with mock.patch("sys.argv", ["get_exemplars.py", "--service", "payments-api"]):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert "data" in output

    def test_metric_filter(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": [], "rows": 0}).encode("utf-8")

        with mock.patch("sys.argv", ["get_exemplars.py", "--metric", "process.memory.usage"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert "process.memory.usage" in body.get("sql", "")

    def test_service_filter(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": [], "rows": 0}).encode("utf-8")

        with mock.patch("sys.argv", ["get_exemplars.py", "--service", "auth-service"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert "auth-service" in body.get("sql", "")

    def test_trace_id_filter(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": [], "rows": 0}).encode("utf-8")

        with mock.patch("sys.argv", ["get_exemplars.py", "--trace_id", "abc123"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert "abc123" in body.get("sql", "")

    def test_no_api_key_exits(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True), mock.patch("sys.argv", ["get_exemplars.py"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called()

    def test_api_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch("sys.argv", ["get_exemplars.py"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
