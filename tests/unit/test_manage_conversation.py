"""Tests for manage_conversation.py tool."""

import json
import os
from unittest import mock


def _import_tool():
    import importlib

    import manage_conversation

    importlib.reload(manage_conversation)
    return manage_conversation


class TestManageConversation:
    def test_list(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        from tests.conftest import SAMPLE_CONVERSATIONS

        mock_resp.read.return_value = json.dumps(SAMPLE_CONVERSATIONS).encode("utf-8")

        with mock.patch("sys.argv", ["manage_conversation.py", "--action", "list"]):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert "conversations" in output

    def test_list_with_context_type(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"conversations": [], "total": 0}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_conversation.py", "--action", "list", "--context_type", "logs"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "contextType=logs" in call_url

    def test_list_with_search(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"conversations": [], "total": 0}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_conversation.py", "--action", "list", "--search", "memory"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "search=memory" in call_url

    def test_list_with_is_archived(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"conversations": [], "total": 0}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_conversation.py", "--action", "list", "--is_archived", "true"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "isArchived=true" in call_url

    def test_get(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"id": "conv-1", "title": "Memory investigation"}}).encode(
            "utf-8"
        )

        with mock.patch("sys.argv", ["manage_conversation.py", "--action", "get", "--conversation_id", "conv-1"]):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert "data" in output
        call_url = m.call_args[0][0].full_url
        assert "/llm/chat/conversations/conv-1" in call_url

    def test_get_missing_conversation_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_conversation.py", "--action", "get"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_archive(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"archived": True}}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_conversation.py", "--action", "archive", "--conversation_id", "conv-1"]):
            tool = _import_tool()
            tool.main()

        req = m.call_args[0][0]
        assert req.method == "POST"

    def test_archive_missing_conversation_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_conversation.py", "--action", "archive"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_delete(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.status = 204

        with mock.patch("sys.argv", ["manage_conversation.py", "--action", "delete", "--conversation_id", "conv-1"]):
            tool = _import_tool()
            tool.main()

        output = capture_stdout.getvalue()
        assert "Conversation deleted" in output
        req = m.call_args[0][0]
        assert req.method == "DELETE"

    def test_delete_missing_conversation_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_conversation.py", "--action", "delete"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_unknown_action(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_conversation.py", "--action", "foobar"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_no_api_key_exits(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True):
            with mock.patch("sys.argv", ["manage_conversation.py", "--action", "list"]):
                tool = _import_tool()
                tool.main()
                mock_exit.assert_called()

    def test_api_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch("sys.argv", ["manage_conversation.py", "--action", "list"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
