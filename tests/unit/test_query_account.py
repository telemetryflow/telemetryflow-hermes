"""Tests for query_account.py tool."""

import contextlib
import json
import os
from unittest import mock


def _import_tool():
    import importlib

    import query_account

    importlib.reload(query_account)
    return query_account


class TestQueryAccount:
    def test_profile(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"email": "admin@example.com", "name": "Admin"}}).encode(
            "utf-8"
        )

        with mock.patch("sys.argv", ["query_account.py", "--resource", "profile"]):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert "data" in output
        call_url = m.call_args[0][0].full_url
        assert "/account/profile" in call_url

    def test_security(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"mfaEnabled": True}}).encode("utf-8")

        with mock.patch("sys.argv", ["query_account.py", "--resource", "security"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/account/security" in call_url

    def test_sessions(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["query_account.py", "--resource", "sessions"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/account/sessions" in call_url

    def test_preferences(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"theme": "dark"}}).encode("utf-8")

        with mock.patch("sys.argv", ["query_account.py", "--resource", "preferences"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/account/preferences" in call_url

    def test_unknown_resource(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["query_account.py", "--resource", "foobar"]):
            tool = _import_tool()
            with contextlib.suppress(UnboundLocalError):
                tool.main()
            mock_exit.assert_called_with(1)

    def test_no_api_key_exits(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True):
            with mock.patch("sys.argv", ["query_account.py", "--resource", "profile"]):
                tool = _import_tool()
                tool.main()
                mock_exit.assert_called()

    def test_api_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch("sys.argv", ["query_account.py", "--resource", "profile"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
