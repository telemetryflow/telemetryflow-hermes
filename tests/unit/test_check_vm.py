"""Tests for check_vm.py tool."""

import contextlib
import json
import os
from unittest import mock


def _import_tool():
    import importlib

    import check_vm

    importlib.reload(check_vm)
    return check_vm


class TestCheckVM:
    def test_list(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": [{"id": "vm-1", "name": "web-01"}]}).encode("utf-8")

        with mock.patch("sys.argv", ["check_vm.py", "--resource", "list"]):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert "data" in output
        assert "/monitoring/vms" in m.call_args[0][0].full_url

    def test_list_with_provider(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_vm.py", "--resource", "list", "--provider", "aws"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "provider=aws" in call_url

    def test_get(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"id": "vm-1"}).encode("utf-8")

        with mock.patch("sys.argv", ["check_vm.py", "--resource", "get", "--vm_id", "vm-1"]):
            tool = _import_tool()
            tool.main()

        assert "/monitoring/vms/vm-1" in m.call_args[0][0].full_url

    def test_metrics(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_vm.py", "--resource", "metrics", "--vm_id", "vm-1"]):
            tool = _import_tool()
            tool.main()

        assert "/monitoring/vms/vm-1/metrics" in m.call_args[0][0].full_url

    def test_metrics_with_time_range(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            ["check_vm.py", "--resource", "metrics", "--vm_id", "vm-1", "--from", "2026-01-01", "--to", "2026-01-02"],
        ):
            tool = _import_tool()
            tool.main()

        url = m.call_args[0][0].full_url
        assert "from=2026-01-01" in url
        assert "to=2026-01-02" in url

    def test_metrics_with_metric_name(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch(
            "sys.argv", ["check_vm.py", "--resource", "metrics", "--vm_id", "vm-1", "--metric_name", "cpu_usage"]
        ):
            tool = _import_tool()
            tool.main()

        assert "metricName=cpu_usage" in m.call_args[0][0].full_url

    def test_list_with_status(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_vm.py", "--resource", "list", "--status", "online"]):
            tool = _import_tool()
            tool.main()

        assert "status=online" in m.call_args[0][0].full_url

    def test_get_missing_vm_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["check_vm.py", "--resource", "get"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_metrics_missing_vm_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["check_vm.py", "--resource", "metrics"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_unknown_resource(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["check_vm.py", "--resource", "foobar"]):
            tool = _import_tool()
            with contextlib.suppress(UnboundLocalError):
                tool.main()
            mock_exit.assert_called_with(1)

    def test_no_api_key_exits(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True), mock.patch(
            "sys.argv", ["check_vm.py", "--resource", "list"]
        ):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called()

    def test_api_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch("sys.argv", ["check_vm.py", "--resource", "list"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
