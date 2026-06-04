"""Tests for manage_tenancy.py tool."""

import contextlib
import json
import os
from unittest import mock


def _import_tool():
    import importlib

    import manage_tenancy

    importlib.reload(manage_tenancy)
    return manage_tenancy


class TestManageTenancy:
    def test_regions(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_tenancy.py", "--resource", "regions"]):
            tool = _import_tool()
            tool.main()

        assert "/tenancy/regions" in m.call_args[0][0].full_url

    def test_region_detail(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"id": "reg-1"}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_tenancy.py", "--resource", "region-detail", "--region_id", "reg-1"]):
            tool = _import_tool()
            tool.main()

        assert "/tenancy/regions/reg-1" in m.call_args[0][0].full_url

    def test_region_detail_missing_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_tenancy.py", "--resource", "region-detail"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_tenants(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_tenancy.py", "--resource", "tenants"]):
            tool = _import_tool()
            tool.main()

        assert "/tenancy/tenants" in m.call_args[0][0].full_url

    def test_tenant_detail(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"id": "t-1"}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_tenancy.py", "--resource", "tenant-detail", "--tenant_id", "t-1"]):
            tool = _import_tool()
            tool.main()

        assert "/tenancy/tenants/t-1" in m.call_args[0][0].full_url

    def test_tenant_detail_missing_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_tenancy.py", "--resource", "tenant-detail"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_organizations(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_tenancy.py", "--resource", "organizations"]):
            tool = _import_tool()
            tool.main()

        assert "/tenancy/organizations" in m.call_args[0][0].full_url

    def test_organizations_with_region(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_tenancy.py", "--resource", "organizations", "--region_id", "reg-1"]):
            tool = _import_tool()
            tool.main()

        assert "regionId=reg-1" in m.call_args[0][0].full_url

    def test_org_detail(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"id": "org-1"}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_tenancy.py", "--resource", "org-detail", "--org_id", "org-1"]):
            tool = _import_tool()
            tool.main()

        assert "/tenancy/organizations/org-1" in m.call_args[0][0].full_url

    def test_org_detail_missing_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_tenancy.py", "--resource", "org-detail"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_workspaces(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_tenancy.py", "--resource", "workspaces", "--org_id", "org-1"]):
            tool = _import_tool()
            tool.main()

        assert "/tenancy/organizations/org-1/workspaces" in m.call_args[0][0].full_url

    def test_workspaces_missing_org_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_tenancy.py", "--resource", "workspaces"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_unknown_resource(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_tenancy.py", "--resource", "foobar"]):
            tool = _import_tool()
            with contextlib.suppress(UnboundLocalError):
                tool.main()
            mock_exit.assert_called_with(1)

    def test_no_api_key_exits(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True), mock.patch(
            "sys.argv", ["manage_tenancy.py", "--resource", "regions"]
        ):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called()

    def test_api_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch("sys.argv", ["manage_tenancy.py", "--resource", "regions"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
