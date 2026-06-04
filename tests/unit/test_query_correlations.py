"""Tests for query_correlations.py tool."""

import json
import os
from unittest import mock


def _import_tool():
    import importlib

    import query_correlations

    importlib.reload(query_correlations)
    return query_correlations


class TestQueryCorrelations:
    def test_basic_query(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        from tests.conftest import SAMPLE_CORRELATIONS

        mock_resp.read.return_value = json.dumps(
            {"data": SAMPLE_CORRELATIONS, "rows": len(SAMPLE_CORRELATIONS)}
        ).encode("utf-8")

        with mock.patch("sys.argv", ["query_correlations.py", "--service", "payments-api"]):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert "data" in output

    def test_signal_types_filter(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": [], "rows": 0}).encode("utf-8")

        with mock.patch("sys.argv", ["query_correlations.py", "--correlation_type", "metric-log"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert "metric-log" in body.get("sql", "")

    def test_no_api_key_exits(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True), mock.patch("sys.argv", ["query_correlations.py"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called()

    def test_api_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch("sys.argv", ["query_correlations.py"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
