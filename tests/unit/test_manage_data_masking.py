"""Tests for manage_data_masking.py tool."""

import contextlib
import json
import os
from unittest import mock


def _import_tool():
    import importlib

    import manage_data_masking

    importlib.reload(manage_data_masking)
    return manage_data_masking


class TestManageDataMasking:
    def test_list_action(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": [{"id": "pol-1", "name": "Mask Emails"}]}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_data_masking.py", "--action", "list"]):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert "data" in output
        call_url = m.call_args[0][0].full_url
        assert "/data-masking/policies" in call_url

    def test_get_action(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"id": "pol-1", "name": "Mask Emails"}}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_data_masking.py", "--action", "get", "--policy_id", "pol-1"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/data-masking/policies/pol-1" in call_url

    def test_get_missing_policy_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_data_masking.py", "--action", "get"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_create_action(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"id": "pol-2", "name": "Mask Emails"}}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            [
                "manage_data_masking.py",
                "--action",
                "create",
                "--name",
                "Mask Emails",
                "--field",
                "body",
                "--pattern",
                "email",
            ],
        ):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert "data" in output
        req = m.call_args[0][0]
        assert req.method == "POST"
        body = json.loads(req.data)
        assert body["name"] == "Mask Emails"
        assert body["field"] == "body"
        assert body["pattern"] == "email"

    def test_create_missing_name(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_data_masking.py", "--action", "create"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_toggle_action(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"id": "pol-1", "enabled": False}}).encode("utf-8")

        with mock.patch(
            "sys.argv", ["manage_data_masking.py", "--action", "toggle", "--policy_id", "pol-1", "--enabled", "false"]
        ):
            tool = _import_tool()
            tool.main()

        req = m.call_args[0][0]
        assert req.method == "PATCH"
        body = json.loads(req.data)
        assert body["enabled"] is False

    def test_toggle_missing_policy_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_data_masking.py", "--action", "toggle", "--enabled", "true"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_unknown_action(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_data_masking.py", "--action", "delete"]):
            tool = _import_tool()
            with contextlib.suppress(UnboundLocalError):
                tool.main()
            mock_exit.assert_called_with(1)

    def test_no_api_key_exits(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True):
            with mock.patch("sys.argv", ["manage_data_masking.py", "--action", "list"]):
                tool = _import_tool()
                tool.main()
                mock_exit.assert_called()

    def test_api_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch("sys.argv", ["manage_data_masking.py", "--action", "list"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
