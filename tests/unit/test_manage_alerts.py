"""Tests for manage_alerts.py tool."""

import contextlib
import json
import os
from unittest import mock


def _import_tool():
    import importlib

    import manage_alerts

    importlib.reload(manage_alerts)
    return manage_alerts


class TestManageAlerts:
    def test_rules(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_alerts.py", "--resource", "rules"]):
            tool = _import_tool()
            tool.main()

        assert "/alert-rules" in m.call_args[0][0].full_url

    def test_rules_with_severity(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_alerts.py", "--resource", "rules", "--severity", "critical"]):
            tool = _import_tool()
            tool.main()

        assert "severity=critical" in m.call_args[0][0].full_url

    def test_instances(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_alerts.py", "--resource", "instances", "--status", "firing"]):
            tool = _import_tool()
            tool.main()

        assert "/alert-instances" in m.call_args[0][0].full_url
        assert "status=firing" in m.call_args[0][0].full_url

    def test_stats(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"total": 10}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_alerts.py", "--resource", "stats"]):
            tool = _import_tool()
            tool.main()

        assert "/alert-instances/stats" in m.call_args[0][0].full_url

    def test_channels(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_alerts.py", "--resource", "channels"]):
            tool = _import_tool()
            tool.main()

        assert "/notification-channels" in m.call_args[0][0].full_url

    def test_validate_tfql(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"valid": True}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_alerts.py", "--resource", "validate-tfql", "--query", "SELECT 1"]):
            tool = _import_tool()
            tool.main()

        assert "/alert-rules/validate-tfql" in m.call_args[0][0].full_url

    def test_validate_tfql_missing_query(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_alerts.py", "--resource", "validate-tfql"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_rule_detail(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"id": "rule-1"}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_alerts.py", "--resource", "rule-detail", "--rule_id", "rule-1"]):
            tool = _import_tool()
            tool.main()

        assert "/alert-rules/rule-1" in m.call_args[0][0].full_url

    def test_instance_detail(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"id": "inst-1"}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_alerts.py", "--resource", "instance-detail", "--instance_id", "inst-1"]):
            tool = _import_tool()
            tool.main()

        assert "/alert-instances/inst-1" in m.call_args[0][0].full_url

    def test_instance_detail_missing_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_alerts.py", "--resource", "instance-detail"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_channels_with_type(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_alerts.py", "--resource", "channels", "--type", "slack"]):
            tool = _import_tool()
            tool.main()

        assert "type=slack" in m.call_args[0][0].full_url

    def test_rules_with_enabled(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_alerts.py", "--resource", "rules", "--enabled", "true"]):
            tool = _import_tool()
            tool.main()

        assert "enabled=true" in m.call_args[0][0].full_url

    def test_unknown_resource(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_alerts.py", "--resource", "foobar"]):
            tool = _import_tool()
            with contextlib.suppress(UnboundLocalError):
                tool.main()
            mock_exit.assert_called_with(1)

    def test_no_api_key_exits(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True), mock.patch(
            "sys.argv", ["manage_alerts.py", "--resource", "rules"]
        ):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called()

    def test_api_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch("sys.argv", ["manage_alerts.py", "--resource", "rules"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
