"""Tests for list_traces.py tool."""

import json
import os
from unittest import mock


def _import_tool():
    import importlib

    import list_traces

    importlib.reload(list_traces)
    return list_traces


class TestListTraces:
    def test_basic_listing(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        from tests.conftest import SAMPLE_TRACES

        mock_resp.read.return_value = json.dumps({"data": SAMPLE_TRACES, "rows": len(SAMPLE_TRACES)}).encode("utf-8")

        with mock.patch("sys.argv", ["list_traces.py", "--service", "payments-api"]):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert "data" in output

    def test_min_duration_filter(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": [], "rows": 0}).encode("utf-8")

        with mock.patch("sys.argv", ["list_traces.py", "--min-duration", "1000"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert "1000" in body.get("sql", "")

    def test_service_filter(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": [], "rows": 0}).encode("utf-8")

        with mock.patch("sys.argv", ["list_traces.py", "--service", "auth-service"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert "auth-service" in body.get("sql", "")

    def test_status_filter(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": [], "rows": 0}).encode("utf-8")

        with mock.patch("sys.argv", ["list_traces.py", "--status", "ERROR"]):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert "data" in output

    def test_no_api_key_exits(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True), mock.patch("sys.argv", ["list_traces.py"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called()

    def test_api_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch("sys.argv", ["list_traces.py"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
