"""Tests for _shared.py — shared utilities for all plugin tools."""

import json
import os
from unittest import mock


class TestGetApiUrl:
    def test_returns_env_value(self, mock_env):
        import importlib

        import _shared

        importlib.reload(_shared)
        assert _shared.get_api_url() == "http://localhost:3000/api/v2"

    def test_returns_default_when_not_set(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            import importlib

            import _shared

            importlib.reload(_shared)
            assert _shared.get_api_url() == "http://localhost:3000/api/v2"


class TestGetApiKey:
    def test_returns_env_value(self, mock_env):
        import importlib

        import _shared

        importlib.reload(_shared)
        assert _shared.get_api_key() == "tfs_test_api_key_1234567890abcdef"

    def test_exits_when_not_set(self, mock_exit):
        with mock.patch.dict(os.environ, {"TELEMETRYFLOW_API_KEY": ""}, clear=False):
            import importlib

            import _shared

            importlib.reload(_shared)
            _shared.get_api_key()
            mock_exit.assert_called_with(1)

    def test_exits_when_missing(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True):
            import importlib

            import _shared

            importlib.reload(_shared)
            _shared.get_api_key()
            mock_exit.assert_called_with(1)


class TestTfoRequest:
    def test_get_request(self, mock_env, mock_urlopen):
        import importlib

        import _shared

        importlib.reload(_shared)

        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": "test"}).encode("utf-8")

        result = _shared.tfo_request("/test/path")
        assert result == {"data": "test"}
        m.assert_called_once()
        call_args = m.call_args
        req = call_args[0][0]
        assert req.get_header("Authorization") == "Bearer tfs_test_api_key_1234567890abcdef"
        assert req.get_header("Content-type") == "application/json"

    def test_post_request_with_data(self, mock_env, mock_urlopen):
        import importlib

        import _shared

        importlib.reload(_shared)

        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"created": True}).encode("utf-8")

        result = _shared.tfo_request("/test", method="POST", data={"key": "value"})
        assert result == {"created": True}
        call_args = m.call_args
        req = call_args[0][0]
        assert req.method == "POST"
        body = req.data
        assert json.loads(body) == {"key": "value"}

    def test_get_request_with_params(self, mock_env, mock_urlopen):
        import importlib

        import _shared

        importlib.reload(_shared)

        m, _ = mock_urlopen
        _shared.tfo_request("/test", params={"key": "val", "empty": None})
        call_args = m.call_args
        url = call_args[0][0].full_url
        assert "key=val" in url
        assert "empty" not in url

    def test_returns_none_on_204(self, mock_env, mock_urlopen):
        import importlib

        import _shared

        importlib.reload(_shared)

        _, mock_resp = mock_urlopen
        mock_resp.status = 204

        result = _shared.tfo_request("/test")
        assert result is None

    def test_http_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        import importlib

        import _shared

        importlib.reload(_shared)

        _shared.tfo_request("/test")
        mock_exit.assert_called_with(1)

    def test_connection_error_exits(self, mock_env, mock_urlopen_conn_error, mock_exit):
        import importlib

        import _shared

        importlib.reload(_shared)

        _shared.tfo_request("/test")
        mock_exit.assert_called_with(1)


class TestClickhouseQuery:
    def test_sends_sql_to_telemetry_query(self, mock_env, mock_urlopen):
        import importlib

        import _shared

        importlib.reload(_shared)

        m, _ = mock_urlopen
        _shared.clickhouse_query("SELECT 1", fmt="JSON")
        call_args = m.call_args
        req = call_args[0][0]
        body = json.loads(req.data)
        assert body["sql"] == "SELECT 1"
        assert body["format"] == "JSON"

    def test_default_format_is_json(self, mock_env, mock_urlopen):
        import importlib

        import _shared

        importlib.reload(_shared)

        m, _ = mock_urlopen
        _shared.clickhouse_query("SELECT 1")
        body = json.loads(m.call_args[0][0].data)
        assert body["format"] == "JSON"


class TestParseArgs:
    def test_parses_key_value_pairs(self):
        import importlib

        import _shared

        importlib.reload(_shared)

        with mock.patch("sys.argv", ["tool.py", "--service", "payments-api", "--limit", "10"]):
            args = _shared.parse_args()
        assert args == {"service": "payments-api", "limit": "10"}

    def test_parses_flag_without_value(self):
        import importlib

        import _shared

        importlib.reload(_shared)

        with mock.patch("sys.argv", ["tool.py", "--verbose"]):
            args = _shared.parse_args()
        assert args == {"verbose": "true"}

    def test_handles_empty_args(self):
        import importlib

        import _shared

        importlib.reload(_shared)

        with mock.patch("sys.argv", ["tool.py"]):
            args = _shared.parse_args()
        assert args == {}

    def test_handles_flag_before_value(self):
        import importlib

        import _shared

        importlib.reload(_shared)

        with mock.patch("sys.argv", ["tool.py", "--flag", "--key", "val"]):
            args = _shared.parse_args()
        assert args == {"flag": "true", "key": "val"}

    def test_ignores_non_flag_args(self):
        import importlib

        import _shared

        importlib.reload(_shared)

        with mock.patch("sys.argv", ["prog", "positional", "--key", "val", "another_pos"]):
            result = _shared.parse_args()
        assert result["key"] == "val"


class TestOutputJson:
    def test_prints_formatted_json(self, capture_stdout):
        import importlib

        import _shared

        importlib.reload(_shared)

        _shared.output_json({"key": "value"})
        output = capture_stdout.getvalue()
        parsed = json.loads(output)
        assert parsed == {"key": "value"}

    def test_handles_datetime(self, capture_stdout):
        import importlib
        from datetime import datetime, timezone

        import _shared

        importlib.reload(_shared)

        dt = datetime(2026, 6, 4, 3, 47, 0, tzinfo=timezone.utc)
        _shared.output_json({"time": dt})
        output = capture_stdout.getvalue()
        assert "2026-06-04" in output


class TestNowIso:
    def test_returns_iso_string(self):
        import importlib

        import _shared

        importlib.reload(_shared)

        result = _shared.now_iso()
        assert "T" in result
        assert "Z" in result or "+" in result

    def test_returns_utc(self):
        import importlib

        import _shared

        importlib.reload(_shared)

        result = _shared.now_iso()
        from datetime import datetime

        dt = datetime.fromisoformat(result)
        assert dt.tzinfo is not None


class TestConstants:
    def test_context_types_not_empty(self):
        import importlib

        import _shared

        importlib.reload(_shared)

        assert len(_shared.CONTEXT_TYPES) >= 70

    def test_context_types_contains_core(self):
        import importlib

        import _shared

        importlib.reload(_shared)

        for ct in ["metrics", "logs", "traces", "exemplars", "correlations"]:
            assert ct in _shared.CONTEXT_TYPES

    def test_context_types_contains_k8s(self):
        import importlib

        import _shared

        importlib.reload(_shared)

        for ct in ["kubernetes-overview", "kubernetes-pods", "kubernetes-deployments"]:
            assert ct in _shared.CONTEXT_TYPES

    def test_context_types_contains_db_monitoring(self):
        import importlib

        import _shared

        importlib.reload(_shared)

        for ct in ["db-monitoring-clickhouse", "db-monitoring-postgresql", "db-monitoring-qan"]:
            assert ct in _shared.CONTEXT_TYPES

    def test_insight_types(self):
        import importlib

        import _shared

        importlib.reload(_shared)

        assert set(_shared.INSIGHT_TYPES) == {"chronology", "prediction", "recommendation", "root-cause", "pattern"}

    def test_provider_types_count(self):
        import importlib

        import _shared

        importlib.reload(_shared)

        assert len(_shared.PROVIDER_TYPES) >= 15

    def test_provider_types_contains_all(self):
        import importlib

        import _shared

        importlib.reload(_shared)

        for pt in [
            "anthropic",
            "openai",
            "google",
            "deepseek",
            "qwen",
            "ollama",
            "mistral",
            "grok",
            "kimi",
            "zhipu",
            "mimo",
            "openrouter",
            "custom",
        ]:
            assert pt in _shared.PROVIDER_TYPES

    def test_no_duplicate_context_types(self):
        import importlib

        import _shared

        importlib.reload(_shared)

        assert len(_shared.CONTEXT_TYPES) == len(set(_shared.CONTEXT_TYPES))

    def test_no_duplicate_provider_types(self):
        import importlib

        import _shared

        importlib.reload(_shared)

        assert len(_shared.PROVIDER_TYPES) == len(set(_shared.PROVIDER_TYPES))


class TestValidateUrl:
    def test_allows_http(self):
        import importlib

        import _shared

        importlib.reload(_shared)

        _shared._validate_url("http://localhost:3000/api/v2/test")

    def test_allows_https(self):
        import importlib

        import _shared

        importlib.reload(_shared)

        _shared._validate_url("https://api.example.com/path")

    def test_blocks_file_scheme(self, mock_exit):
        import importlib

        import _shared

        importlib.reload(_shared)

        _shared._validate_url("file:///etc/passwd")
        mock_exit.assert_called_with(1)

    def test_blocks_ftp_scheme(self, mock_exit):
        import importlib

        import _shared

        importlib.reload(_shared)

        _shared._validate_url("ftp://evil.com/payload")
        mock_exit.assert_called_with(1)

    def test_blocks_javascript_scheme(self, mock_exit):
        import importlib

        import _shared

        importlib.reload(_shared)

        _shared._validate_url("javascript:alert(1)")
        mock_exit.assert_called_with(1)

    def test_blocks_data_scheme(self, mock_exit):
        import importlib

        import _shared

        importlib.reload(_shared)

        _shared._validate_url("data:text/html,<script>alert(1)</script>")
        mock_exit.assert_called_with(1)

    def test_case_insensitive_scheme(self):
        import importlib

        import _shared

        importlib.reload(_shared)

        _shared._validate_url("HTTP://EXAMPLE.COM/path")
        _shared._validate_url("HTTPS://example.com/path")
