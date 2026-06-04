"""Tests for restart_pod.py tool."""

import json
import os
from unittest import mock


def _import_tool():
    import importlib

    import restart_pod

    importlib.reload(restart_pod)
    return restart_pod


class TestRestartPod:
    def test_restart_deployment(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"restarted": True}}).encode("utf-8")

        with mock.patch("sys.argv", ["restart_pod.py", "--deployment", "payments-api", "--namespace", "production"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert body["name"] == "payments-api"
        call_url = m.call_args[0][0].full_url
        assert "/kubernetes/deployments/restart" in call_url

    def test_restart_specific_pod(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"restarted": True}}).encode("utf-8")

        with mock.patch("sys.argv", ["restart_pod.py", "--pod", "payments-api-7b8cf-abc", "--namespace", "production"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert body["name"] == "payments-api-7b8cf-abc"
        call_url = m.call_args[0][0].full_url
        assert "/kubernetes/pods/restart" in call_url

    def test_missing_target_exits(self, mock_exit):
        with mock.patch("sys.argv", ["restart_pod.py"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_no_api_key_exits(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True):
            with mock.patch("sys.argv", ["restart_pod.py", "--deployment", "test"]):
                tool = _import_tool()
                tool.main()
                mock_exit.assert_called()

    def test_api_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch("sys.argv", ["restart_pod.py", "--deployment", "payments-api"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
