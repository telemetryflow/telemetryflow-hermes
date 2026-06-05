"""Tests for manage_retention.py tool."""

import contextlib
import json
import os
from unittest import mock


def _import_tool():
    import importlib

    import manage_retention

    importlib.reload(manage_retention)
    return manage_retention


class TestManageRetention:
    def test_policies(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_retention.py", "--resource", "policies"]):
            tool = _import_tool()
            tool.main()

        assert "/retention/policies" in m.call_args[0][0].full_url

    def test_policies_with_data_type(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_retention.py", "--resource", "policies", "--data_type", "logs"]):
            tool = _import_tool()
            tool.main()

        assert "dataType=logs" in m.call_args[0][0].full_url

    def test_statistics(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"logs": "120GB"}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_retention.py", "--resource", "statistics"]):
            tool = _import_tool()
            tool.main()

        assert "/retention/policies/statistics" in m.call_args[0][0].full_url

    def test_enforce_dry_run(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"dryRun": True}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_retention.py", "--resource", "enforce", "--dry_run", "true"]):
            tool = _import_tool()
            tool.main()

        assert "/retention/policies/enforce" in m.call_args[0][0].full_url

    def test_policy_detail_missing_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_retention.py", "--resource", "policy-detail"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_unknown_resource(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_retention.py", "--resource", "foobar"]):
            tool = _import_tool()
            with contextlib.suppress(UnboundLocalError):
                tool.main()
            mock_exit.assert_called_with(1)

    def test_no_api_key_exits(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True), mock.patch(
            "sys.argv", ["manage_retention.py", "--resource", "policies"]
        ):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called()

    def test_policies_with_include_defaults(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_retention.py", "--resource", "policies", "--include_defaults", "true"]):
            tool = _import_tool()
            tool.main()

        url = m.call_args[0][0].full_url
        assert "includeDefaults=true" in url

    def test_api_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch("sys.argv", ["manage_retention.py", "--resource", "policies"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
