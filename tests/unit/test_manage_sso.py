"""Tests for manage_sso.py tool."""

import contextlib
import json
import os
from unittest import mock


def _import_tool():
    import importlib

    import manage_sso

    importlib.reload(manage_sso)
    return manage_sso


class TestManageSSO:
    def test_providers(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_sso.py", "--resource", "providers"]):
            tool = _import_tool()
            tool.main()

        assert "/sso/providers" in m.call_args[0][0].full_url

    def test_provider_detail(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"id": "prov-1"}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_sso.py", "--resource", "provider-detail", "--provider_id", "prov-1"]):
            tool = _import_tool()
            tool.main()

        assert "/sso/providers/prov-1" in m.call_args[0][0].full_url

    def test_public_providers(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_sso.py", "--resource", "public-providers", "--org_id", "org-1"]):
            tool = _import_tool()
            tool.main()

        assert "/sso/providers/org-1/public" in m.call_args[0][0].full_url

    def test_connections(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_sso.py", "--resource", "connections"]):
            tool = _import_tool()
            tool.main()

        assert "/sso/connections" in m.call_args[0][0].full_url

    def test_provider_detail_missing_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_sso.py", "--resource", "provider-detail"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_public_providers_missing_org_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_sso.py", "--resource", "public-providers"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_unknown_resource(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_sso.py", "--resource", "foobar"]):
            tool = _import_tool()
            with contextlib.suppress(UnboundLocalError):
                tool.main()
            mock_exit.assert_called_with(1)

    def test_no_api_key_exits(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True), mock.patch(
            "sys.argv", ["manage_sso.py", "--resource", "providers"]
        ):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called()

    def test_api_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch("sys.argv", ["manage_sso.py", "--resource", "providers"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
