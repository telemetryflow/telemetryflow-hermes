"""Tests for manage_reports.py tool."""

import contextlib
import json
import os
from unittest import mock


def _import_tool():
    import importlib

    import manage_reports

    importlib.reload(manage_reports)
    return manage_reports


class TestManageReports:
    def test_definitions(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_reports.py", "--resource", "definitions"]):
            tool = _import_tool()
            tool.main()

        assert "/reports/definitions" in m.call_args[0][0].full_url

    def test_definition_detail(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"id": "def-1"}).encode("utf-8")

        with mock.patch(
            "sys.argv", ["manage_reports.py", "--resource", "definition-detail", "--definition_id", "def-1"]
        ):
            tool = _import_tool()
            tool.main()

        assert "/reports/definitions/def-1" in m.call_args[0][0].full_url

    def test_definition_detail_missing_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_reports.py", "--resource", "definition-detail"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_execution_detail(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"id": "exec-1"}).encode("utf-8")

        with mock.patch(
            "sys.argv", ["manage_reports.py", "--resource", "execution-detail", "--execution_id", "exec-1"]
        ):
            tool = _import_tool()
            tool.main()

        assert "/reports/executions/exec-1" in m.call_args[0][0].full_url

    def test_execution_detail_missing_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_reports.py", "--resource", "execution-detail"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_executions(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_reports.py", "--resource", "executions"]):
            tool = _import_tool()
            tool.main()

        assert "/reports/executions" in m.call_args[0][0].full_url

    def test_stats(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"total": 5}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_reports.py", "--resource", "stats"]):
            tool = _import_tool()
            tool.main()

        assert "/reports/stats" in m.call_args[0][0].full_url

    def test_generate(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"id": "exec-1"}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_reports.py", "--resource", "generate", "--definition_id", "def-1"]):
            tool = _import_tool()
            tool.main()

        assert "/reports/definitions/def-1/generate" in m.call_args[0][0].full_url

    def test_generate_missing_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_reports.py", "--resource", "generate"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_unknown_resource(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_reports.py", "--resource", "foobar"]):
            tool = _import_tool()
            with contextlib.suppress(UnboundLocalError):
                tool.main()
            mock_exit.assert_called_with(1)

    def test_definitions_with_filters(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            ["manage_reports.py", "--resource", "definitions", "--type", "pdf", "--schedule", "daily"],
        ):
            tool = _import_tool()
            tool.main()

        url = m.call_args[0][0].full_url
        assert "type=pdf" in url
        assert "schedule=daily" in url

    def test_no_api_key_exits(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True), mock.patch(
            "sys.argv", ["manage_reports.py", "--resource", "definitions"]
        ):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called()

    def test_api_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch("sys.argv", ["manage_reports.py", "--resource", "definitions"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
