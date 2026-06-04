"""Tests for check_network_map.py tool."""

import contextlib
import json
import os
from unittest import mock


def _import_tool():
    import importlib

    import check_network_map

    importlib.reload(check_network_map)
    return check_network_map


class TestCheckNetworkMap:
    def test_topology(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"nodes": [], "edges": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_network_map.py", "--resource", "topology"]):
            tool = _import_tool()
            tool.main()

        assert "/monitoring/network-map/topology" in m.call_args[0][0].full_url

    def test_nodes(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_network_map.py", "--resource", "nodes"]):
            tool = _import_tool()
            tool.main()

        assert "/monitoring/network-map/nodes" in m.call_args[0][0].full_url

    def test_nodes_with_type(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_network_map.py", "--resource", "nodes", "--type", "KUBERNETES_POD"]):
            tool = _import_tool()
            tool.main()

        assert "type=KUBERNETES_POD" in m.call_args[0][0].full_url

    def test_connections(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_network_map.py", "--resource", "connections", "--node_id", "n-1"]):
            tool = _import_tool()
            tool.main()

        assert "/monitoring/network-map/nodes/n-1/connections" in m.call_args[0][0].full_url

    def test_traffic(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_network_map.py", "--resource", "traffic", "--node_id", "n-1"]):
            tool = _import_tool()
            tool.main()

        assert "/monitoring/network-map/nodes/n-1/traffic" in m.call_args[0][0].full_url

    def test_flows(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_network_map.py", "--resource", "flows"]):
            tool = _import_tool()
            tool.main()

        assert "/monitoring/network-map/flows" in m.call_args[0][0].full_url

    def test_dns(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_network_map.py", "--resource", "dns"]):
            tool = _import_tool()
            tool.main()

        assert "/monitoring/network-map/dns" in m.call_args[0][0].full_url

    def test_k8s_flows(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_network_map.py", "--resource", "k8s-flows"]):
            tool = _import_tool()
            tool.main()

        assert "/monitoring/network-map/k8s/flows" in m.call_args[0][0].full_url

    def test_snmp_configs(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_network_map.py", "--resource", "snmp-configs"]):
            tool = _import_tool()
            tool.main()

        assert "/monitoring/network-map/snmp/configs" in m.call_args[0][0].full_url

    def test_connections_missing_node_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["check_network_map.py", "--resource", "connections"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_traffic_missing_node_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["check_network_map.py", "--resource", "traffic"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_paths(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_network_map.py", "--resource", "paths"]):
            tool = _import_tool()
            tool.main()

        assert "/monitoring/network-map/paths" in m.call_args[0][0].full_url

    def test_nodes_with_status(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_network_map.py", "--resource", "nodes", "--status", "DEGRADED"]):
            tool = _import_tool()
            tool.main()

        assert "status=DEGRADED" in m.call_args[0][0].full_url

    def test_nodes_with_cluster(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_network_map.py", "--resource", "nodes", "--cluster", "prod-eks"]):
            tool = _import_tool()
            tool.main()

        assert "cluster=prod-eks" in m.call_args[0][0].full_url

    def test_topology_with_depth(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_network_map.py", "--resource", "topology", "--depth", "2"]):
            tool = _import_tool()
            tool.main()

        assert "depth=2" in m.call_args[0][0].full_url

    def test_unknown_resource(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["check_network_map.py", "--resource", "foobar"]):
            tool = _import_tool()
            with contextlib.suppress(UnboundLocalError):
                tool.main()
            mock_exit.assert_called_with(1)

    def test_no_api_key_exits(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True), mock.patch(
            "sys.argv", ["check_network_map.py", "--resource", "topology"]
        ):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called()

    def test_api_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch("sys.argv", ["check_network_map.py", "--resource", "topology"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
