"""Tests for manage_provider.py tool."""

import json
import os
from unittest import mock


def _import_tool():
    import importlib

    import manage_provider

    importlib.reload(manage_provider)
    return manage_provider


class TestManageProvider:
    def test_list(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        from tests.conftest import SAMPLE_PROVIDERS

        mock_resp.read.return_value = json.dumps({"data": SAMPLE_PROVIDERS}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_provider.py", "--action", "list"]):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert "data" in output

    def test_get(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"id": "prov-1"}}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_provider.py", "--action", "get", "--provider_id", "prov-1"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/llm/providers/prov-1" in call_url

    def test_get_missing_provider_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_provider.py", "--action", "get"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_default(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"id": "prov-1", "isDefault": True}}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_provider.py", "--action", "default"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/llm/providers/default" in call_url

    def test_create(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"id": "prov-3", "name": "Test Provider"}}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            [
                "manage_provider.py",
                "--action",
                "create",
                "--name",
                "Test",
                "--type",
                "anthropic",
                "--api_key",
                "sk-test-key",
                "--model",
                "claude-sonnet-4-5",
            ],
        ):
            tool = _import_tool()
            tool.main()

        req = m.call_args[0][0]
        assert req.method == "POST"
        body = json.loads(req.data)
        assert body["name"] == "Test"
        assert body["providerType"] == "anthropic"

    def test_create_with_base_url(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"id": "prov-4"}}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            [
                "manage_provider.py",
                "--action",
                "create",
                "--name",
                "Custom",
                "--type",
                "openai",
                "--api_key",
                "sk-key",
                "--model",
                "gpt-4",
                "--base_url",
                "https://api.custom.com/v1",
            ],
        ):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert body["baseUrl"] == "https://api.custom.com/v1"

    def test_create_missing_fields(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_provider.py", "--action", "create", "--name", "Test"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_create_invalid_type(self, mock_env, mock_exit):
        with mock.patch(
            "sys.argv",
            [
                "manage_provider.py",
                "--action",
                "create",
                "--name",
                "Test",
                "--type",
                "invalid_type",
                "--api_key",
                "sk-key",
                "--model",
                "gpt-4",
            ],
        ):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_validate(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"valid": True}}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_provider.py", "--action", "validate", "--provider_id", "prov-1"]):
            tool = _import_tool()
            tool.main()

        req = m.call_args[0][0]
        assert req.method == "POST"
        assert "/llm/providers/prov-1/validate" in req.full_url

    def test_validate_missing_provider_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_provider.py", "--action", "validate"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_test_key(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"valid": True}}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_provider.py", "--action", "test-key", "--api_key", "sk-test"]):
            tool = _import_tool()
            tool.main()

        req = m.call_args[0][0]
        assert req.method == "POST"
        body = json.loads(req.data)
        assert body["apiKey"] == "sk-test"

    def test_test_key_with_base_url(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"valid": True}}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            [
                "manage_provider.py",
                "--action",
                "test-key",
                "--api_key",
                "sk-test",
                "--base_url",
                "https://custom.api.com",
            ],
        ):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert body["baseUrl"] == "https://custom.api.com"

    def test_test_key_missing_api_key(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_provider.py", "--action", "test-key"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_set_default(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"id": "prov-1", "isDefault": True}}).encode("utf-8")

        with mock.patch("sys.argv", ["manage_provider.py", "--action", "set-default", "--provider_id", "prov-1"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/set-default" in call_url

    def test_set_default_missing_provider_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_provider.py", "--action", "set-default"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_unknown_action(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["manage_provider.py", "--action", "delete"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_no_api_key_exits(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True):
            with mock.patch("sys.argv", ["manage_provider.py", "--action", "list"]):
                tool = _import_tool()
                tool.main()
                mock_exit.assert_called()

    def test_api_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch("sys.argv", ["manage_provider.py", "--action", "list"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
