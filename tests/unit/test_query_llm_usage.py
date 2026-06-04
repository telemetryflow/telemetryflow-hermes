"""Tests for query_llm_usage.py tool."""

import contextlib
import json
import os
from unittest import mock


def _import_tool():
    import importlib

    import query_llm_usage

    importlib.reload(query_llm_usage)
    return query_llm_usage


class TestQueryLlmUsage:
    def test_summary_action(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": [{"total_requests": 1500, "total_tokens": 500000}]}).encode(
            "utf-8"
        )

        with mock.patch("sys.argv", ["query_llm_usage.py", "--action", "summary"]):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert "data" in output
        body = json.loads(m.call_args[0][0].data)
        assert "total_requests" in body.get("sql", "")

    def test_by_provider_action(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["query_llm_usage.py", "--action", "by-provider", "--duration", "7d"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert "provider_type" in body.get("sql", "")

    def test_by_model_action(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["query_llm_usage.py", "--action", "by-model"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert "model_id" in body.get("sql", "")

    def test_by_context_action(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["query_llm_usage.py", "--action", "by-context"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert "context_type" in body.get("sql", "")

    def test_top_users_action(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["query_llm_usage.py", "--action", "top-users"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert "user_id" in body.get("sql", "")

    def test_interval_action_default(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["query_llm_usage.py", "--action", "interval"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert "llm_usage_5m" in body.get("sql", "")

    def test_interval_action_15m(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["query_llm_usage.py", "--action", "interval", "--view", "15m"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert "llm_usage_15m" in body.get("sql", "")

    def test_interval_action_6h(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["query_llm_usage.py", "--action", "interval", "--view", "6h"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert "llm_usage_6h" in body.get("sql", "")

    def test_unknown_action(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["query_llm_usage.py", "--action", "foobar"]):
            tool = _import_tool()
            with contextlib.suppress(UnboundLocalError, NameError):
                tool.main()
            mock_exit.assert_called_with(1)

    def test_no_api_key_exits(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True):
            with mock.patch("sys.argv", ["query_llm_usage.py", "--action", "summary"]):
                tool = _import_tool()
                tool.main()
                mock_exit.assert_called()

    def test_api_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch("sys.argv", ["query_llm_usage.py", "--action", "summary"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
