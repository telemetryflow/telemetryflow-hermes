"""Tests for check_infra.py tool."""

import json
import os
from unittest import mock


def _import_tool():
    import importlib

    import check_infra

    importlib.reload(check_infra)
    return check_infra


class TestCheckInfra:
    def test_overview(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"hosts": 2}}).encode("utf-8")

        with mock.patch("sys.argv", ["check_infra.py", "--resource", "overview"]):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert "data" in output
        call_url = m.call_args[0][0].full_url
        assert "/monitoring/vm/overview" in call_url

    def test_cpu(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_infra.py", "--resource", "cpu"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/monitoring/vm/cpu" in call_url

    def test_memory(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_infra.py", "--resource", "memory"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/monitoring/vm/memory" in call_url

    def test_storage(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_infra.py", "--resource", "storage"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/monitoring/vm/storage" in call_url

    def test_network(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_infra.py", "--resource", "network"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/monitoring/vm/network" in call_url

    def test_unknown_resource(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["check_infra.py", "--resource", "foobar"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_no_api_key_exits(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True):
            with mock.patch("sys.argv", ["check_infra.py", "--resource", "overview"]):
                tool = _import_tool()
                tool.main()
                mock_exit.assert_called()

    def test_api_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch("sys.argv", ["check_infra.py", "--resource", "overview"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
