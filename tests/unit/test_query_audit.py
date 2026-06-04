"""Tests for query_audit.py tool."""

import contextlib
import json
import os
from unittest import mock


def _import_tool():
    import importlib

    import query_audit

    importlib.reload(query_audit)
    return query_audit


class TestQueryAudit:
    def test_logs(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["query_audit.py", "--resource", "logs"]):
            tool = _import_tool()
            tool.main()

        assert "/audit/logs" in m.call_args[0][0].full_url

    def test_logs_with_filters(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch(
            "sys.argv", ["query_audit.py", "--resource", "logs", "--event_type", "AUTH", "--result", "FAILURE"]
        ):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "event_type=AUTH" in call_url
        assert "result=FAILURE" in call_url

    def test_logs_with_duration(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["query_audit.py", "--resource", "logs", "--duration", "24h"]):
            tool = _import_tool()
            tool.main()

        assert "duration=24h" in m.call_args[0][0].full_url

    def test_unknown_resource(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["query_audit.py", "--resource", "foobar"]):
            tool = _import_tool()
            with contextlib.suppress(UnboundLocalError):
                tool.main()
            mock_exit.assert_called_with(1)

    def test_no_api_key_exits(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True), mock.patch(
            "sys.argv", ["query_audit.py", "--resource", "logs"]
        ):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called()

    def test_api_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch("sys.argv", ["query_audit.py", "--resource", "logs"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
