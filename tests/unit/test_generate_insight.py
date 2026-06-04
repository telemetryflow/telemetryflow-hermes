"""Tests for generate_insight.py tool."""

import json
import os
from unittest import mock


def _import_tool():
    import importlib

    import generate_insight

    importlib.reload(generate_insight)
    return generate_insight


class TestGenerateInsight:
    def test_root_cause_type(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        from tests.conftest import SAMPLE_INSIGHT

        mock_resp.read.return_value = json.dumps({"data": SAMPLE_INSIGHT}).encode("utf-8")

        with mock.patch(
            "sys.argv", ["generate_insight.py", "--insight_type", "root-cause", "--context_type", "metrics"]
        ):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert "data" in output
        body = json.loads(m.call_args[0][0].data)
        assert body["insightType"] == "root-cause"

    def test_chronology_type(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"insightType": "chronology"}}).encode("utf-8")

        with mock.patch("sys.argv", ["generate_insight.py", "--insight_type", "chronology", "--context_type", "logs"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert body["insightType"] == "chronology"

    def test_with_time_range(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {}}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            [
                "generate_insight.py",
                "--insight_type",
                "root-cause",
                "--context_type",
                "metrics",
                "--time_from",
                "2026-06-04T00:00:00Z",
                "--time_to",
                "2026-06-04T03:00:00Z",
            ],
        ):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert body["timeFrom"] == "2026-06-04T00:00:00Z"
        assert body["timeTo"] == "2026-06-04T03:00:00Z"

    def test_with_context_id(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {}}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            [
                "generate_insight.py",
                "--insight_type",
                "root-cause",
                "--context_type",
                "alerts",
                "--context_id",
                "alert-123",
            ],
        ):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert body["contextId"] == "alert-123"

    def test_with_provider_id(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {}}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            [
                "generate_insight.py",
                "--insight_type",
                "prediction",
                "--context_type",
                "metrics",
                "--provider_id",
                "prov-1",
            ],
        ):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert body["providerId"] == "prov-1"

    def test_with_additional_context_json(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {}}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            [
                "generate_insight.py",
                "--insight_type",
                "root-cause",
                "--context_type",
                "metrics",
                "--additional_context",
                '{"key": "value"}',
            ],
        ):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert body["additionalContext"] == {"key": "value"}

    def test_with_additional_context_plain_text(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {}}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            [
                "generate_insight.py",
                "--insight_type",
                "root-cause",
                "--context_type",
                "metrics",
                "--additional_context",
                "some note text",
            ],
        ):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert body["additionalContext"] == {"note": "some note text"}

    def test_invalid_insight_type(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["generate_insight.py", "--insight_type", "foobar", "--context_type", "metrics"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_invalid_context_type(self, mock_env, mock_exit):
        with mock.patch(
            "sys.argv", ["generate_insight.py", "--insight_type", "root-cause", "--context_type", "foobar"]
        ):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_no_api_key_exits(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True):
            with mock.patch("sys.argv", ["generate_insight.py", "--insight_type", "root-cause"]):
                tool = _import_tool()
                tool.main()
                mock_exit.assert_called()

    def test_api_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch(
            "sys.argv", ["generate_insight.py", "--insight_type", "root-cause", "--context_type", "metrics"]
        ):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
