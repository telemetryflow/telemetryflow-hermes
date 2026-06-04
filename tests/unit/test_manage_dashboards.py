"""Tests for manage_dashboards.py tool."""

import contextlib
import json
import os
from unittest import mock


def _import_tool():
    import importlib

    import manage_dashboards

    importlib.reload(manage_dashboards)
    return manage_dashboards


class TestManageDashboards:
    def test_list(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_dashboards.py", "--resource", "list"]):
            tool = _import_tool()
            tool.main()

        assert "/dashboards" in m.call_args[0][0].full_url

    def test_list_with_tag(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_dashboards.py", "--resource", "list", "--tag", "production"]):
            tool = _import_tool()
            tool.main()

        assert "tag=production" in m.call_args[0][0].full_url

    def test_get(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"id": "dash-1"}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_dashboards.py", "--resource", "get", "--dashboard_id", "dash-1"]):
            tool = _import_tool()
            tool.main()

        assert "/dashboards/dash-1" in m.call_args[0][0].full_url

    def test_templates(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_dashboards.py", "--resource", "templates"]):
            tool = _import_tool()
            tool.main()

        assert "/dashboards/templates" in m.call_args[0][0].full_url

    def test_shared_graphs(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_dashboards.py", "--resource", "shared-graphs"]):
            tool = _import_tool()
            tool.main()

        assert "/dashboards/shared-graphs" in m.call_args[0][0].full_url

    def test_export_missing_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_dashboards.py", "--resource", "export"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_shared(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_dashboards.py", "--resource", "shared"]):
            tool = _import_tool()
            tool.main()

        assert "/dashboards" in m.call_args[0][0].full_url

    def test_public(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_dashboards.py", "--resource", "public"]):
            tool = _import_tool()
            tool.main()

        assert "/dashboards" in m.call_args[0][0].full_url

    def test_get_missing_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_dashboards.py", "--resource", "get"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_unknown_resource(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_dashboards.py", "--resource", "foobar"]):
            tool = _import_tool()
            with contextlib.suppress(UnboundLocalError):
                tool.main()
            mock_exit.assert_called_with(1)

    def test_no_api_key_exits(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True), mock.patch(
            "sys.argv", ["manage_dashboards.py", "--resource", "list"]
        ):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called()

    def test_api_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch("sys.argv", ["manage_dashboards.py", "--resource", "list"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
