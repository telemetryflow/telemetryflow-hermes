"""Tests for scale_deployment.py tool."""

import json
import os
from unittest import mock


def _import_tool():
    import importlib

    import scale_deployment

    importlib.reload(scale_deployment)
    return scale_deployment


class TestScaleDeployment:
    def test_scale_with_replicas(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"name": "payments-api", "replicas": 3}}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            ["scale_deployment.py", "--name", "payments-api", "--namespace", "production", "--replicas", "3"],
        ):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert body["replicas"] == 3
        assert body["name"] == "payments-api"

    def test_missing_deployment_exits(self, mock_exit):
        with mock.patch("sys.argv", ["scale_deployment.py", "--replicas", "3"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_no_api_key_exits(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True):
            with mock.patch("sys.argv", ["scale_deployment.py", "--name", "test"]):
                tool = _import_tool()
                tool.main()
                mock_exit.assert_called()

    def test_api_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch("sys.argv", ["scale_deployment.py", "--name", "payments-api", "--replicas", "3"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
