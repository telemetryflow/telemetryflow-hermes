"""Tests for update_alert.py tool."""

import json
import os
from unittest import mock


def _import_tool():
    import importlib

    import update_alert

    importlib.reload(update_alert)
    return update_alert


class TestUpdateAlert:
    def test_update_threshold(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"rule_id": "rule-1", "threshold": 90.0}}).encode("utf-8")

        with mock.patch("sys.argv", ["update_alert.py", "--rule_id", "rule-1", "--threshold", "90"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert body["threshold"] == 90.0

    def test_enable(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"rule_id": "rule-1", "enabled": True}}).encode("utf-8")

        with mock.patch("sys.argv", ["update_alert.py", "--rule_id", "rule-1", "--enabled", "true"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert body["enabled"] is True

    def test_disable(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"rule_id": "rule-1", "enabled": False}}).encode("utf-8")

        with mock.patch("sys.argv", ["update_alert.py", "--rule_id", "rule-1", "--enabled", "false"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert body["enabled"] is False

    def test_update_severity(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"rule_id": "rule-1", "severity": "critical"}}).encode(
            "utf-8"
        )

        with mock.patch("sys.argv", ["update_alert.py", "--rule_id", "rule-1", "--severity", "critical"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert body["severity"] == "critical"

    def test_no_update_fields(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["update_alert.py", "--rule_id", "rule-1"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_missing_rule_id_exits(self, mock_exit):
        with mock.patch("sys.argv", ["update_alert.py", "--threshold", "90"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_no_api_key_exits(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True):
            with mock.patch("sys.argv", ["update_alert.py", "--rule_id", "rule-1", "--threshold", "90"]):
                tool = _import_tool()
                tool.main()
                mock_exit.assert_called()

    def test_api_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch("sys.argv", ["update_alert.py", "--rule_id", "rule-1", "--threshold", "90"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
