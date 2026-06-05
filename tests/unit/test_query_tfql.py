"""Tests for query_tfql.py tool."""

import contextlib
import json
import os
from unittest import mock


def _import_tool():
    import importlib

    import query_tfql

    importlib.reload(query_tfql)
    return query_tfql


class TestQueryTFQL:
    def test_metrics_query(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["query_tfql.py", "--signal", "metrics", "--metric_name", "cpu_usage"]):
            tool = _import_tool()
            tool.main()

        assert "/query/signals/metrics" in m.call_args[0][0].full_url

    def test_metrics_names(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["query_tfql.py", "--signal", "metrics", "--action", "names"]):
            tool = _import_tool()
            tool.main()

        assert "/query/signals/metrics/names" in m.call_args[0][0].full_url

    def test_metrics_names_with_prefix(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["query_tfql.py", "--signal", "metrics", "--action", "names", "--prefix", "http"]):
            tool = _import_tool()
            tool.main()

        assert "prefix=http" in m.call_args[0][0].full_url

    def test_metrics_with_aggregation(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            [
                "query_tfql.py",
                "--signal",
                "metrics",
                "--metric_name",
                "cpu",
                "--aggregation",
                "avg",
                "--interval",
                "5m",
            ],
        ):
            tool = _import_tool()
            tool.main()

        assert "/query/signals/metrics" in m.call_args[0][0].full_url

    def test_logs_count_by_severity(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch(
            "sys.argv", ["query_tfql.py", "--signal", "logs", "--action", "count-by-severity", "--query", "ERROR"]
        ):
            tool = _import_tool()
            tool.main()

        assert "/query/signals/logs/count-by-severity" in m.call_args[0][0].full_url

    def test_traces_with_duration(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch(
            "sys.argv", ["query_tfql.py", "--signal", "traces", "--min_duration", "100ms", "--max_duration", "10s"]
        ):
            tool = _import_tool()
            tool.main()

        assert "/query/signals/traces" in m.call_args[0][0].full_url

    def test_traces_with_span_name(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            ["query_tfql.py", "--signal", "traces", "--span_name", "POST /api/payments", "--status_code", "ERROR"],
        ):
            tool = _import_tool()
            tool.main()

        assert "/query/signals/traces" in m.call_args[0][0].full_url

    def test_logs_with_service_and_trace(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch(
            "sys.argv", ["query_tfql.py", "--signal", "logs", "--service_name", "api", "--trace_id", "abc123"]
        ):
            tool = _import_tool()
            tool.main()

        assert "/query/signals/logs" in m.call_args[0][0].full_url

    def test_metrics_labels(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch(
            "sys.argv", ["query_tfql.py", "--signal", "metrics", "--action", "labels", "--label_name", "service"]
        ):
            tool = _import_tool()
            tool.main()

        assert "/query/signals/metrics/labels/service" in m.call_args[0][0].full_url

    def test_metrics_labels_missing_name(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["query_tfql.py", "--signal", "metrics", "--action", "labels"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_logs_query(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["query_tfql.py", "--signal", "logs", "--query", "ERROR"]):
            tool = _import_tool()
            tool.main()

        assert "/query/signals/logs" in m.call_args[0][0].full_url

    def test_logs_severity_distribution(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["query_tfql.py", "--signal", "logs", "--action", "severity-distribution"]):
            tool = _import_tool()
            tool.main()

        assert "/query/signals/logs/severity-levels" in m.call_args[0][0].full_url

    def test_traces_query(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["query_tfql.py", "--signal", "traces", "--service_name", "payments-api"]):
            tool = _import_tool()
            tool.main()

        assert "/query/signals/traces" in m.call_args[0][0].full_url

    def test_traces_by_id(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"spans": []}).encode("utf-8")

        with mock.patch("sys.argv", ["query_tfql.py", "--signal", "traces", "--trace_id", "abc123"]):
            tool = _import_tool()
            tool.main()

        assert "/query/signals/traces/abc123" in m.call_args[0][0].full_url

    def test_traces_services(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["query_tfql.py", "--signal", "traces", "--action", "services"]):
            tool = _import_tool()
            tool.main()

        assert "/query/signals/traces/services" in m.call_args[0][0].full_url

    def test_traces_operations(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["query_tfql.py", "--signal", "traces", "--action", "operations"]):
            tool = _import_tool()
            tool.main()

        assert "/query/signals/traces/operations" in m.call_args[0][0].full_url

    def test_traces_summaries(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["query_tfql.py", "--signal", "traces", "--action", "summaries"]):
            tool = _import_tool()
            tool.main()

        assert "/query/signals/traces/summaries" in m.call_args[0][0].full_url

    def test_unknown_signal(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["query_tfql.py", "--signal", "foobar"]):
            tool = _import_tool()
            with contextlib.suppress(UnboundLocalError):
                tool.main()
            mock_exit.assert_called_with(1)

    def test_metrics_with_service_name(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            ["query_tfql.py", "--signal", "metrics", "--service_name", "payments-api", "--percentiles", "50,95,99"],
        ):
            tool = _import_tool()
            tool.main()

        assert m.call_count >= 1

    def test_logs_query_with_service_name(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            ["query_tfql.py", "--signal", "logs", "--action", "query", "--service_name", "auth-svc"],
        ):
            tool = _import_tool()
            tool.main()

        assert m.call_count >= 1

    def test_no_api_key_exits(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True), mock.patch(
            "sys.argv", ["query_tfql.py", "--signal", "metrics"]
        ):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called()

    def test_api_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch("sys.argv", ["query_tfql.py", "--signal", "metrics"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
