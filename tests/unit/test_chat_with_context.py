"""Tests for chat_with_context.py tool."""

import json
import os
from unittest import mock


def _import_tool():
    import importlib

    import chat_with_context

    importlib.reload(chat_with_context)
    return chat_with_context


class TestChatWithContext:
    def test_basic_chat(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps(
            {"data": {"response": "Analysis complete", "messageId": "msg-1"}}
        ).encode("utf-8")

        with mock.patch("sys.argv", ["chat_with_context.py", "--message", "Analyze recent errors"]):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert "data" in output

    def test_context_type(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"response": "ok"}}).encode("utf-8")

        with mock.patch("sys.argv", ["chat_with_context.py", "--message", "show logs", "--context_type", "logs"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert body["contextType"] == "logs"

    def test_context_id(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"response": "ok"}}).encode("utf-8")

        with mock.patch("sys.argv", ["chat_with_context.py", "--message", "details", "--context_id", "ctx-123"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert body["contextId"] == "ctx-123"

    def test_conversation_continuation(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"response": "ok"}}).encode("utf-8")

        with mock.patch("sys.argv", ["chat_with_context.py", "--message", "follow up", "--conversation_id", "conv-1"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert body["conversationId"] == "conv-1"

    def test_provider_id(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"response": "ok"}}).encode("utf-8")

        with mock.patch("sys.argv", ["chat_with_context.py", "--message", "test", "--provider_id", "prov-1"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert body["providerId"] == "prov-1"

    def test_explicit_time_from(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"response": "ok"}}).encode("utf-8")

        with mock.patch(
            "sys.argv", ["chat_with_context.py", "--message", "test", "--time_from", "2026-06-04T00:00:00Z"]
        ):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert body["timeFrom"] == "2026-06-04T00:00:00Z"

    def test_explicit_time_to(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"response": "ok"}}).encode("utf-8")

        with mock.patch("sys.argv", ["chat_with_context.py", "--message", "test", "--time_to", "2026-06-04T12:00:00Z"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert body["timeTo"] == "2026-06-04T12:00:00Z"

    def test_missing_message_exits(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["chat_with_context.py"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_invalid_context_type_exits(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["chat_with_context.py", "--message", "test", "--context_type", "foobar"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_no_api_key_exits(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True):
            with mock.patch("sys.argv", ["chat_with_context.py", "--message", "test"]):
                tool = _import_tool()
                tool.main()
                mock_exit.assert_called()

    def test_api_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch("sys.argv", ["chat_with_context.py", "--message", "test"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
