"""Tests for query_subscription.py tool."""

import contextlib
import json
import os
from unittest import mock


def _import_tool():
    import importlib

    import query_subscription

    importlib.reload(query_subscription)
    return query_subscription


class TestQuerySubscription:
    def test_current(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"plan": "enterprise", "status": "active"}).encode("utf-8")

        with mock.patch("sys.argv", ["query_subscription.py", "--resource", "current"]):
            tool = _import_tool()
            tool.main()

        assert "/subscription" in m.call_args[0][0].full_url

    def test_plan_detail(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"id": "plan-1"}).encode("utf-8")

        with mock.patch("sys.argv", ["query_subscription.py", "--resource", "plan-detail", "--plan_id", "plan-1"]):
            tool = _import_tool()
            tool.main()

        assert "/subscription/plans/plan-1" in m.call_args[0][0].full_url

    def test_plan_detail_missing_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["query_subscription.py", "--resource", "plan-detail"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_invoice_detail(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"id": "inv-1"}).encode("utf-8")

        with mock.patch("sys.argv", ["query_subscription.py", "--resource", "invoice-detail", "--invoice_id", "inv-1"]):
            tool = _import_tool()
            tool.main()

        assert "/subscription/invoices/inv-1" in m.call_args[0][0].full_url

    def test_invoice_detail_missing_id(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["query_subscription.py", "--resource", "invoice-detail"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_plans(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["query_subscription.py", "--resource", "plans"]):
            tool = _import_tool()
            tool.main()

        assert "/subscription/plans" in m.call_args[0][0].full_url

    def test_usage(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"LOG_INGESTION_GB": 45.2}).encode("utf-8")

        with mock.patch("sys.argv", ["query_subscription.py", "--resource", "usage"]):
            tool = _import_tool()
            tool.main()

        assert "/subscription/usage" in m.call_args[0][0].full_url

    def test_usage_check(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"withinLimit": True}).encode("utf-8")

        with mock.patch(
            "sys.argv", ["query_subscription.py", "--resource", "usage-check", "--metric_type", "LOG_INGESTION_GB"]
        ):
            tool = _import_tool()
            tool.main()

        assert "/subscription/usage/check/LOG_INGESTION_GB" in m.call_args[0][0].full_url

    def test_invoices(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["query_subscription.py", "--resource", "invoices"]):
            tool = _import_tool()
            tool.main()

        assert "/subscription/invoices" in m.call_args[0][0].full_url

    def test_usage_check_missing_type(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["query_subscription.py", "--resource", "usage-check"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)

    def test_unknown_resource(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["query_subscription.py", "--resource", "foobar"]):
            tool = _import_tool()
            with contextlib.suppress(UnboundLocalError):
                tool.main()
            mock_exit.assert_called_with(1)

    def test_no_api_key_exits(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True), mock.patch(
            "sys.argv", ["query_subscription.py", "--resource", "current"]
        ):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called()

    def test_api_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch("sys.argv", ["query_subscription.py", "--resource", "current"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
