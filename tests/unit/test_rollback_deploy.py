"""Tests for rollback_deploy.py tool."""

import json
import os
from unittest import mock


def _import_tool():
    import importlib

    import rollback_deploy

    importlib.reload(rollback_deploy)
    return rollback_deploy


class TestRollbackDeploy:
    def test_basic_rollback(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"name": "payments-api", "rolledBack": True}}).encode("utf-8")

        with mock.patch("sys.argv", ["rollback_deploy.py", "--name", "payments-api", "--namespace", "production"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert body["name"] == "payments-api"

    def test_with_specific_revision(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"name": "payments-api", "revision": 2}}).encode("utf-8")

        with mock.patch(
            "sys.argv", ["rollback_deploy.py", "--name", "payments-api", "--namespace", "production", "--revision", "2"]
        ):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert body["revision"] == 2

    def test_missing_name_exits(self, mock_exit):
        with mock.patch("sys.argv", ["rollback_deploy.py"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_no_api_key_exits(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True):
            with mock.patch("sys.argv", ["rollback_deploy.py", "--name", "test"]):
                tool = _import_tool()
                tool.main()
                mock_exit.assert_called()

    def test_api_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch("sys.argv", ["rollback_deploy.py", "--name", "payments-api"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
