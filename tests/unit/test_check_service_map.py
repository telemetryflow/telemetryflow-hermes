"""Tests for check_service_map.py tool."""

import contextlib
import json
import os
from unittest import mock


def _import_tool():
    import importlib

    import check_service_map

    importlib.reload(check_service_map)
    return check_service_map


class TestCheckServiceMap:
    def test_map(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"services": [], "dependencies": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_service_map.py", "--resource", "map"]):
            tool = _import_tool()
            tool.main()

        assert "/monitoring/service-map" in m.call_args[0][0].full_url

    def test_services(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_service_map.py", "--resource", "services"]):
            tool = _import_tool()
            tool.main()

        assert "/monitoring/service-map/services" in m.call_args[0][0].full_url

    def test_services_with_type(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_service_map.py", "--resource", "services", "--type", "MICROSERVICE"]):
            tool = _import_tool()
            tool.main()

        assert "type=MICROSERVICE" in m.call_args[0][0].full_url

    def test_get(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"id": "svc-1"}).encode("utf-8")

        with mock.patch("sys.argv", ["check_service_map.py", "--resource", "get", "--service_id", "svc-1"]):
            tool = _import_tool()
            tool.main()

        assert "/monitoring/service-map/services/svc-1" in m.call_args[0][0].full_url

    def test_dependencies(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_service_map.py", "--resource", "dependencies", "--service_id", "svc-1"]):
            tool = _import_tool()
            tool.main()

        assert "/monitoring/service-map/services/svc-1/dependencies" in m.call_args[0][0].full_url

    def test_health(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"score": 95}).encode("utf-8")

        with mock.patch("sys.argv", ["check_service_map.py", "--resource", "health", "--service_id", "svc-1"]):
            tool = _import_tool()
            tool.main()

        assert "/monitoring/service-map/services/svc-1/health" in m.call_args[0][0].full_url

    def test_metrics(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_service_map.py", "--resource", "metrics", "--service_id", "svc-1"]):
            tool = _import_tool()
            tool.main()

        assert "/monitoring/service-map/services/svc-1/metrics" in m.call_args[0][0].full_url

    def test_trace_dependencies(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_service_map.py", "--resource", "trace-dependencies"]):
            tool = _import_tool()
            tool.main()

        assert "/monitoring/service-map/dependencies" in m.call_args[0][0].full_url

    def test_services_with_status(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_service_map.py", "--resource", "services", "--status", "UNHEALTHY"]):
            tool = _import_tool()
            tool.main()

        assert "status=UNHEALTHY" in m.call_args[0][0].full_url

    def test_services_with_namespace(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_service_map.py", "--resource", "services", "--namespace", "production"]):
            tool = _import_tool()
            tool.main()

        assert "namespace=production" in m.call_args[0][0].full_url

    def test_topology_with_depth(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"nodes": [], "edges": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_service_map.py", "--resource", "topology"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/monitoring/service-map/topology" in call_url

    def test_missing_service_id_dependencies(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["check_service_map.py", "--resource", "dependencies"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_missing_service_id_health(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["check_service_map.py", "--resource", "health"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_missing_service_id_metrics(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["check_service_map.py", "--resource", "metrics"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_missing_service_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["check_service_map.py", "--resource", "get"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_unknown_resource(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["check_service_map.py", "--resource", "foobar"]):
            tool = _import_tool()
            with contextlib.suppress(UnboundLocalError):
                tool.main()
            mock_exit.assert_called_with(1)

    def test_no_api_key_exits(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True), mock.patch(
            "sys.argv", ["check_service_map.py", "--resource", "map"]
        ):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called()

    def test_api_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch("sys.argv", ["check_service_map.py", "--resource", "map"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
