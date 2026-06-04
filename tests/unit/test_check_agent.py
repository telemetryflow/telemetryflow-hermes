"""Tests for check_agent.py tool."""

import contextlib
import json
import os
from unittest import mock


def _import_tool():
    import importlib

    import check_agent

    importlib.reload(check_agent)
    return check_agent


class TestCheckAgent:
    def test_list(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": [{"id": "ag-1", "name": "prod-agent"}]}).encode("utf-8")

        with mock.patch("sys.argv", ["check_agent.py", "--resource", "list"]):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert "data" in output
        assert "/monitoring/agents" in m.call_args[0][0].full_url

    def test_list_with_status(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_agent.py", "--resource", "list", "--status", "offline"]):
            tool = _import_tool()
            tool.main()

        assert "status=offline" in m.call_args[0][0].full_url

    def test_list_with_type(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_agent.py", "--resource", "list", "--type", "kubernetes"]):
            tool = _import_tool()
            tool.main()

        assert "type=kubernetes" in m.call_args[0][0].full_url

    def test_list_with_last_seen(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_agent.py", "--resource", "list", "--last_seen_within_minutes", "30"]):
            tool = _import_tool()
            tool.main()

        assert "last_seen_within_minutes=30" in m.call_args[0][0].full_url

    def test_health_with_params(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_agent.py", "--resource", "health", "--agent_id", "ag-1", "--limit", "50"]):
            tool = _import_tool()
            tool.main()

        assert "limit=50" in m.call_args[0][0].full_url

    def test_stats(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"total": 10, "online": 8}).encode("utf-8")

        with mock.patch("sys.argv", ["check_agent.py", "--resource", "stats"]):
            tool = _import_tool()
            tool.main()

        assert "/monitoring/agents/stats" in m.call_args[0][0].full_url

    def test_get(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"id": "ag-1"}).encode("utf-8")

        with mock.patch("sys.argv", ["check_agent.py", "--resource", "get", "--agent_id", "ag-1"]):
            tool = _import_tool()
            tool.main()

        assert "/monitoring/agents/ag-1" in m.call_args[0][0].full_url

    def test_health(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_agent.py", "--resource", "health", "--agent_id", "ag-1"]):
            tool = _import_tool()
            tool.main()

        assert "/monitoring/agents/ag-1/health" in m.call_args[0][0].full_url

    def test_get_missing_agent_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["check_agent.py", "--resource", "get"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_health_missing_agent_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["check_agent.py", "--resource", "health"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_unknown_resource(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["check_agent.py", "--resource", "foobar"]):
            tool = _import_tool()
            with contextlib.suppress(UnboundLocalError):
                tool.main()
            mock_exit.assert_called_with(1)

    def test_no_api_key_exits(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True), mock.patch(
            "sys.argv", ["check_agent.py", "--resource", "list"]
        ):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called()

    def test_api_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch("sys.argv", ["check_agent.py", "--resource", "list"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
