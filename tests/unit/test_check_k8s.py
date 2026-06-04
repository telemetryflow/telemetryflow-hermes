"""Tests for check_k8s.py tool."""

import contextlib
import json
import os
from unittest import mock


def _import_tool():
    import importlib

    import check_k8s

    importlib.reload(check_k8s)
    return check_k8s


class TestCheckK8s:
    def test_overview(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"clusters": 2, "pods": 15}}).encode("utf-8")

        with mock.patch("sys.argv", ["check_k8s.py", "--resource", "overview"]):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert "data" in output
        call_url = m.call_args[0][0].full_url
        assert "/kubernetes/overview" in call_url

    def test_clusters(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_k8s.py", "--resource", "clusters"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/kubernetes/clusters" in call_url

    def test_nodes(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_k8s.py", "--resource", "nodes"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/kubernetes/nodes" in call_url

    def test_nodes_with_cluster(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_k8s.py", "--resource", "nodes", "--cluster", "prod-cluster"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "cluster=prod-cluster" in call_url

    def test_namespaces(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_k8s.py", "--resource", "namespaces"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/kubernetes/namespaces" in call_url

    def test_namespaces_with_cluster(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_k8s.py", "--resource", "namespaces", "--cluster", "prod-cluster"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "cluster=prod-cluster" in call_url

    def test_pods(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        from tests.conftest import SAMPLE_K8S_PODS

        mock_resp.read.return_value = json.dumps({"data": SAMPLE_K8S_PODS}).encode("utf-8")

        with mock.patch("sys.argv", ["check_k8s.py", "--resource", "pods"]):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert "data" in output
        call_url = m.call_args[0][0].full_url
        assert "/kubernetes/pods" in call_url

    def test_pods_with_namespace(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_k8s.py", "--resource", "pods", "--namespace", "production"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "namespace=production" in call_url

    def test_pods_with_cluster(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_k8s.py", "--resource", "pods", "--cluster", "prod-cluster"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "cluster=prod-cluster" in call_url

    def test_deployments(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_k8s.py", "--resource", "deployments"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/kubernetes/deployments" in call_url

    def test_deployments_with_namespace_and_cluster(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            ["check_k8s.py", "--resource", "deployments", "--namespace", "staging", "--cluster", "dev-cluster"],
        ):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "namespace=staging" in call_url
        assert "cluster=dev-cluster" in call_url

    def test_pv(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_k8s.py", "--resource", "pv"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/kubernetes/persistent-volumes" in call_url

    def test_pv_with_cluster(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_k8s.py", "--resource", "pv", "--cluster", "prod"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "cluster=prod" in call_url

    def test_unknown_resource(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["check_k8s.py", "--resource", "foobar"]):
            tool = _import_tool()
            with contextlib.suppress(UnboundLocalError):
                tool.main()
            mock_exit.assert_called_with(1)

    def test_no_api_key_exits(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True):
            with mock.patch("sys.argv", ["check_k8s.py", "--resource", "overview"]):
                tool = _import_tool()
                tool.main()
                mock_exit.assert_called()

    def test_api_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch("sys.argv", ["check_k8s.py", "--resource", "overview"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
