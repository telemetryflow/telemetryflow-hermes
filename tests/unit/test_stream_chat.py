"""Tests for stream_chat.py tool."""

import contextlib
import json
from unittest import mock


def _import_tool():
    import importlib

    import stream_chat

    importlib.reload(stream_chat)
    return stream_chat


class TestStreamChat:
    def test_basic_stream(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        sse_lines = [
            b'data: {"type": "start", "conversationId": "conv-1"}\n',
            b'data: {"type": "chunk", "content": "Hello"}\n',
            b'data: {"type": "chunk", "content": " world"}\n',
            b'data: {"type": "end", "messageId": "msg-1", "latencyMs": 250}\n',
        ]
        mock_resp.__iter__ = mock.MagicMock(return_value=iter(sse_lines))

        with mock.patch("sys.argv", ["stream_chat.py", "--message", "Analyze system health"]):
            tool = _import_tool()
            tool.main()

        output = capture_stdout.getvalue()
        assert "Hello world" in output

    def test_stream_with_provider_id(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        sse_lines = [
            b'data: {"type": "start", "conversationId": "conv-1"}\n',
            b'data: {"type": "end", "messageId": "msg-1"}\n',
        ]
        mock_resp.__iter__ = mock.MagicMock(return_value=iter(sse_lines))

        with mock.patch("sys.argv", ["stream_chat.py", "--message", "test", "--provider_id", "prov-1"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert body["providerId"] == "prov-1"

    def test_stream_with_conversation_id(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        sse_lines = [
            b'data: {"type": "start", "conversationId": "conv-2"}\n',
            b'data: {"type": "end", "messageId": "msg-2"}\n',
        ]
        mock_resp.__iter__ = mock.MagicMock(return_value=iter(sse_lines))

        with mock.patch("sys.argv", ["stream_chat.py", "--message", "follow up", "--conversation_id", "conv-2"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert body["conversationId"] == "conv-2"

    def test_stream_skips_non_data_lines(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        sse_lines = [
            b": this is a comment\n",
            b"event: message\n",
            b'data: {"type": "start", "conversationId": "conv-1"}\n',
            b"\n",
            b'data: {"type": "end", "messageId": "msg-1"}\n',
        ]
        mock_resp.__iter__ = mock.MagicMock(return_value=iter(sse_lines))

        with mock.patch("sys.argv", ["stream_chat.py", "--message", "test"]):
            tool = _import_tool()
            tool.main()

        output = capture_stdout.getvalue()
        assert "comment" not in output

    def test_stream_handles_invalid_json_payload(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        sse_lines = [
            b'data: {"type": "start", "conversationId": "conv-1"}\n',
            b"data: not valid json\n",
            b'data: {"type": "chunk", "content": "still works"}\n',
            b'data: {"type": "end", "messageId": "msg-1"}\n',
        ]
        mock_resp.__iter__ = mock.MagicMock(return_value=iter(sse_lines))

        with mock.patch("sys.argv", ["stream_chat.py", "--message", "test"]):
            tool = _import_tool()
            tool.main()

        output = capture_stdout.getvalue()
        assert "still works" in output

    def test_stream_error_event(self, mock_env, mock_urlopen, capture_stdout, mock_exit):
        _, mock_resp = mock_urlopen
        sse_lines = [
            b'data: {"type": "start", "conversationId": "conv-1"}\n',
            b'data: {"type": "error", "message": "Rate limit exceeded"}\n',
        ]
        mock_resp.__iter__ = mock.MagicMock(return_value=iter(sse_lines))

        with mock.patch("sys.argv", ["stream_chat.py", "--message", "test"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_invalid_context_type_exits(self, mock_env, mock_urlopen, mock_exit):
        with mock.patch("sys.argv", ["stream_chat.py", "--message", "test", "--context_type", "foobar"]):
            tool = _import_tool()
            with contextlib.suppress(UnboundLocalError):
                tool.main()
            mock_exit.assert_called_with(1)

    def test_missing_message_exits(self, mock_env, mock_urlopen, mock_exit):
        with mock.patch("sys.argv", ["stream_chat.py"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_any_call(1)

    def test_http_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch("sys.argv", ["stream_chat.py", "--message", "test"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
