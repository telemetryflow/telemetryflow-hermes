"""Tests for check_uptime.py tool."""

import contextlib
import json
import os
from unittest import mock


def _import_tool():
    import importlib

    import check_uptime

    importlib.reload(check_uptime)
    return check_uptime


class TestCheckUptime:
    def test_monitors(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps(
            {"data": [{"id": "mon-1", "name": "API Health", "status": "up"}]}
        ).encode("utf-8")

        with mock.patch("sys.argv", ["check_uptime.py", "--resource", "monitors"]):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert "data" in output
        call_url = m.call_args[0][0].full_url
        assert "/monitoring/uptime/monitors" in call_url

    def test_checks_with_monitor_id(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_uptime.py", "--resource", "checks", "--monitor_id", "mon-1"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/monitoring/uptime/monitors/mon-1/checks" in call_url

    def test_checks_missing_monitor_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["check_uptime.py", "--resource", "checks"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_status_pages(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_uptime.py", "--resource", "status-pages"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/monitoring/status-page" in call_url

    def test_incidents_with_status_page_id(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_uptime.py", "--resource", "incidents", "--status_page_id", "sp-1"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/monitoring/status-pages/sp-1/incidents" in call_url

    def test_incidents_missing_status_page_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["check_uptime.py", "--resource", "incidents"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_unknown_resource(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["check_uptime.py", "--resource", "foobar"]):
            tool = _import_tool()
            with contextlib.suppress(UnboundLocalError):
                tool.main()
            mock_exit.assert_called_with(1)

    def test_no_api_key_exits(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True):
            with mock.patch("sys.argv", ["check_uptime.py", "--resource", "monitors"]):
                tool = _import_tool()
                tool.main()
                mock_exit.assert_called()

    def test_api_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch("sys.argv", ["check_uptime.py", "--resource", "monitors"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_monitors_with_id(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"id": "mon-1"}}).encode("utf-8")

        with mock.patch("sys.argv", ["check_uptime.py", "--resource", "monitors", "--monitor_id", "mon-1"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/monitoring/uptime/monitors/mon-1" in call_url

    def test_stats_with_monitor_id(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {}}).encode("utf-8")

        with mock.patch("sys.argv", ["check_uptime.py", "--resource", "stats", "--monitor_id", "mon-1"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/monitoring/uptime/monitors/mon-1/stats" in call_url

    def test_stats_missing_monitor_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["check_uptime.py", "--resource", "stats"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_daily_stats_with_monitor_id(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {}}).encode("utf-8")

        with mock.patch("sys.argv", ["check_uptime.py", "--resource", "daily-stats", "--monitor_id", "mon-1"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/monitoring/uptime/monitors/mon-1/daily-stats" in call_url

    def test_daily_stats_missing_monitor_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["check_uptime.py", "--resource", "daily-stats"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_hourly_stats_with_monitor_id(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {}}).encode("utf-8")

        with mock.patch("sys.argv", ["check_uptime.py", "--resource", "hourly-stats", "--monitor_id", "mon-1"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/monitoring/uptime/monitors/mon-1/hourly-stats" in call_url

    def test_hourly_stats_missing_monitor_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["check_uptime.py", "--resource", "hourly-stats"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_ssl_summary(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {}}).encode("utf-8")

        with mock.patch("sys.argv", ["check_uptime.py", "--resource", "ssl-summary"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/ssl-summary" in call_url

    def test_ssl_trend_with_monitor_id(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {}}).encode("utf-8")

        with mock.patch("sys.argv", ["check_uptime.py", "--resource", "ssl-trend", "--monitor_id", "mon-1"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/monitoring/uptime/monitors/mon-1/ssl-trend" in call_url

    def test_ssl_trend_missing_monitor_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["check_uptime.py", "--resource", "ssl-trend"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_status_pages_with_id(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"id": "sp-1"}}).encode("utf-8")

        with mock.patch("sys.argv", ["check_uptime.py", "--resource", "status-pages", "--status_page_id", "sp-1"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/monitoring/status-pages/sp-1" in call_url

    def test_incidents_with_status_filter(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            ["check_uptime.py", "--resource", "incidents", "--status_page_id", "sp-1", "--status", "open"],
        ):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "status=open" in call_url

    def test_subscribers_with_status_page_id(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_uptime.py", "--resource", "subscribers", "--status_page_id", "sp-1"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/monitoring/status-pages/sp-1/subscribers" in call_url

    def test_subscribers_missing_status_page_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["check_uptime.py", "--resource", "subscribers"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
