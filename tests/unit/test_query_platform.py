"""Tests for query_platform.py tool."""

import contextlib
import json
import os
from unittest import mock


def _import_tool():
    import importlib

    import query_platform

    importlib.reload(query_platform)
    return query_platform


class TestQueryPlatform:
    def test_iam_users(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": [{"id": "user-1", "name": "admin"}]}).encode("utf-8")

        with mock.patch("sys.argv", ["query_platform.py", "--resource", "iam-users"]):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert "data" in output
        call_url = m.call_args[0][0].full_url
        assert "/iam/users" in call_url

    def test_tenancy_orgs(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["query_platform.py", "--resource", "tenancy-orgs"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/tenancy/organizations" in call_url

    def test_audit_logs_with_duration(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["query_platform.py", "--resource", "audit-logs", "--duration", "24h"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/audit/logs" in call_url
        assert "duration=24h" in call_url

    def test_unknown_resource(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["query_platform.py", "--resource", "foobar"]):
            tool = _import_tool()
            with contextlib.suppress(UnboundLocalError, KeyError):
                tool.main()
            mock_exit.assert_called_with(1)

    def test_no_api_key_exits(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True):
            with mock.patch("sys.argv", ["query_platform.py", "--resource", "iam-users"]):
                tool = _import_tool()
                tool.main()
                mock_exit.assert_called()

    def test_api_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch("sys.argv", ["query_platform.py", "--resource", "iam-users"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
