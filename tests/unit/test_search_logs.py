"""Tests for search_logs.py tool."""

import json
import os
from unittest import mock


def _import_tool():
    import importlib

    import search_logs

    importlib.reload(search_logs)
    return search_logs


class TestSearchLogs:
    def test_basic_search(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        from tests.conftest import SAMPLE_LOGS

        mock_resp.read.return_value = json.dumps({"data": SAMPLE_LOGS, "rows": len(SAMPLE_LOGS)}).encode("utf-8")

        with mock.patch("sys.argv", ["search_logs.py", "--service", "payments-api"]):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert "data" in output

    def test_severity_filter(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": [], "rows": 0}).encode("utf-8")

        with mock.patch("sys.argv", ["search_logs.py", "--severity", "WARN"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert "WARN" in body.get("sql", "")

    def test_full_text_query(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": [], "rows": 0}).encode("utf-8")

        with mock.patch("sys.argv", ["search_logs.py", "--search", "OOM killed"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert "OOM killed" in body.get("sql", "")

    def test_time_range(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": [], "rows": 0}).encode("utf-8")

        with mock.patch("sys.argv", ["search_logs.py", "--duration", "6h"]):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert "data" in output

    def test_no_api_key_exits(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True):
            with mock.patch("sys.argv", ["search_logs.py", "--service", "payments-api"]):
                tool = _import_tool()
                tool.main()
                mock_exit.assert_called()

    def test_api_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch("sys.argv", ["search_logs.py", "--service", "payments-api"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
