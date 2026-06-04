"""Tests for manage_iam.py tool."""

import contextlib
import json
import os
from unittest import mock


def _import_tool():
    import importlib

    import manage_iam

    importlib.reload(manage_iam)
    return manage_iam


class TestManageIAM:
    def test_users(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_iam.py", "--resource", "users"]):
            tool = _import_tool()
            tool.main()

        assert "/iam/users" in m.call_args[0][0].full_url

    def test_user_detail(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"id": "u-1"}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_iam.py", "--resource", "user-detail", "--user_id", "u-1"]):
            tool = _import_tool()
            tool.main()

        assert "/iam/users/u-1" in m.call_args[0][0].full_url

    def test_user_detail_missing_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_iam.py", "--resource", "user-detail"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_user_permissions_missing_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_iam.py", "--resource", "user-permissions"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_user_roles(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_iam.py", "--resource", "user-roles", "--user_id", "u-1"]):
            tool = _import_tool()
            tool.main()

        assert "/iam/users/u-1/roles" in m.call_args[0][0].full_url

    def test_user_permissions(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_iam.py", "--resource", "user-permissions", "--user_id", "u-1"]):
            tool = _import_tool()
            tool.main()

        assert "/iam/users/u-1/permissions" in m.call_args[0][0].full_url

    def test_roles(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_iam.py", "--resource", "roles"]):
            tool = _import_tool()
            tool.main()

        assert "/iam/roles" in m.call_args[0][0].full_url

    def test_role_detail(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"id": "r-1"}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_iam.py", "--resource", "role-detail", "--role_id", "r-1"]):
            tool = _import_tool()
            tool.main()

        assert "/iam/roles/r-1" in m.call_args[0][0].full_url

    def test_role_detail_missing_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_iam.py", "--resource", "role-detail"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_role_permissions(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_iam.py", "--resource", "role-permissions", "--role_id", "r-1"]):
            tool = _import_tool()
            tool.main()

        assert "/iam/roles/r-1/permissions" in m.call_args[0][0].full_url

    def test_role_permissions_missing_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_iam.py", "--resource", "role-permissions"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_permissions(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_iam.py", "--resource", "permissions"]):
            tool = _import_tool()
            tool.main()

        assert "/iam/permissions" in m.call_args[0][0].full_url

    def test_groups(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_iam.py", "--resource", "groups"]):
            tool = _import_tool()
            tool.main()

        assert "/iam/groups" in m.call_args[0][0].full_url

    def test_group_detail(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"id": "g-1"}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_iam.py", "--resource", "group-detail", "--group_id", "g-1"]):
            tool = _import_tool()
            tool.main()

        assert "/iam/groups/g-1" in m.call_args[0][0].full_url

    def test_group_detail_missing_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_iam.py", "--resource", "group-detail"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_group_users_missing_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_iam.py", "--resource", "group-users"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_group_users(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_iam.py", "--resource", "group-users", "--group_id", "g-1"]):
            tool = _import_tool()
            tool.main()

        assert "/iam/groups/g-1/users" in m.call_args[0][0].full_url

    def test_audit_logs(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_iam.py", "--resource", "audit-logs"]):
            tool = _import_tool()
            tool.main()

        assert "/iam/audit-logs" in m.call_args[0][0].full_url

    def test_missing_user_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_iam.py", "--resource", "user-roles"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_unknown_resource(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_iam.py", "--resource", "foobar"]):
            tool = _import_tool()
            with contextlib.suppress(UnboundLocalError):
                tool.main()
            mock_exit.assert_called_with(1)

    def test_no_api_key_exits(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True), mock.patch(
            "sys.argv", ["manage_iam.py", "--resource", "users"]
        ):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called()

    def test_api_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch("sys.argv", ["manage_iam.py", "--resource", "users"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
