"""Tests for query_ai_intelligence.py tool."""

import contextlib
import json
import os
from unittest import mock


def _import_tool():
    import importlib

    import query_ai_intelligence

    importlib.reload(query_ai_intelligence)
    return query_ai_intelligence


class TestQueryAiIntelligence:
    def test_anomaly_detection_list(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": [{"id": "anom-1", "severity": "critical"}]}).encode("utf-8")

        with mock.patch("sys.argv", ["query_ai_intelligence.py", "--module", "anomaly-detection", "--action", "list"]):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert "data" in output
        call_url = m.call_args[0][0].full_url
        assert "/ai-intelligence/anomaly-detection/anomalies" in call_url

    def test_anomaly_detection_get(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"id": "anom-1"}}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            ["query_ai_intelligence.py", "--module", "anomaly-detection", "--action", "get", "--id", "anom-1"],
        ):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/ai-intelligence/anomaly-detection/anomalies/anom-1" in call_url

    def test_anomaly_detection_analyze(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"analysis": "complete"}}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            ["query_ai_intelligence.py", "--module", "anomaly-detection", "--action", "analyze", "--id", "anom-2"],
        ):
            tool = _import_tool()
            tool.main()

        req = m.call_args[0][0]
        assert req.method == "POST"
        assert "/anomalies/anom-2/analyze" in req.full_url

    def test_anomaly_detection_invalid_action(self, mock_env, mock_exit):
        with mock.patch(
            "sys.argv", ["query_ai_intelligence.py", "--module", "anomaly-detection", "--action", "delete"]
        ):
            tool = _import_tool()
            with contextlib.suppress(UnboundLocalError):
                tool.main()
            mock_exit.assert_called_with(1)

    def test_predictive_maintenance_list(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch(
            "sys.argv", ["query_ai_intelligence.py", "--module", "predictive-maintenance", "--action", "list"]
        ):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/ai-intelligence/predictive-maintenance/predictions" in call_url

    def test_predictive_maintenance_predictions(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch(
            "sys.argv", ["query_ai_intelligence.py", "--module", "predictive-maintenance", "--action", "predictions"]
        ):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/ai-intelligence/predictive-maintenance/predictions" in call_url

    def test_predictive_maintenance_get(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"id": "pred-1"}}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            ["query_ai_intelligence.py", "--module", "predictive-maintenance", "--action", "get", "--id", "pred-1"],
        ):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/ai-intelligence/predictive-maintenance/predictions/pred-1" in call_url

    def test_predictive_maintenance_invalid_action(self, mock_env, mock_exit):
        with mock.patch(
            "sys.argv", ["query_ai_intelligence.py", "--module", "predictive-maintenance", "--action", "delete"]
        ):
            tool = _import_tool()
            with contextlib.suppress(UnboundLocalError):
                tool.main()
            mock_exit.assert_called_with(1)

    def test_cost_optimization_list(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["query_ai_intelligence.py", "--module", "cost-optimization", "--action", "list"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/ai-intelligence/cost-optimization/recommendations" in call_url

    def test_cost_optimization_recommendations(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch(
            "sys.argv", ["query_ai_intelligence.py", "--module", "cost-optimization", "--action", "recommendations"]
        ):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/ai-intelligence/cost-optimization/recommendations" in call_url

    def test_cost_optimization_get(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"id": "rec-1"}}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            ["query_ai_intelligence.py", "--module", "cost-optimization", "--action", "get", "--id", "rec-1"],
        ):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/ai-intelligence/cost-optimization/recommendations/rec-1" in call_url

    def test_cost_optimization_invalid_action(self, mock_env, mock_exit):
        with mock.patch(
            "sys.argv", ["query_ai_intelligence.py", "--module", "cost-optimization", "--action", "delete"]
        ):
            tool = _import_tool()
            with contextlib.suppress(UnboundLocalError):
                tool.main()
            mock_exit.assert_called_with(1)

    def test_corrective_maintenance_list(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch(
            "sys.argv", ["query_ai_intelligence.py", "--module", "corrective-maintenance", "--action", "list"]
        ):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/ai-intelligence/corrective-maintenance/plans" in call_url

    def test_corrective_maintenance_plans(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch(
            "sys.argv", ["query_ai_intelligence.py", "--module", "corrective-maintenance", "--action", "plans"]
        ):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/ai-intelligence/corrective-maintenance/plans" in call_url

    def test_corrective_maintenance_get(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": {"id": "plan-1"}}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            ["query_ai_intelligence.py", "--module", "corrective-maintenance", "--action", "get", "--id", "plan-1"],
        ):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/ai-intelligence/corrective-maintenance/plans/plan-1" in call_url

    def test_corrective_maintenance_invalid_action(self, mock_env, mock_exit):
        with mock.patch(
            "sys.argv", ["query_ai_intelligence.py", "--module", "corrective-maintenance", "--action", "delete"]
        ):
            tool = _import_tool()
            with contextlib.suppress(UnboundLocalError):
                tool.main()
            mock_exit.assert_called_with(1)

    def test_invalid_module(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["query_ai_intelligence.py", "--module", "foobar"]):
            tool = _import_tool()
            with contextlib.suppress(UnboundLocalError):
                tool.main()
            mock_exit.assert_called_with(1)

    def test_no_api_key_exits(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True):
            with mock.patch("sys.argv", ["query_ai_intelligence.py", "--module", "anomaly-detection"]):
                tool = _import_tool()
                tool.main()
                mock_exit.assert_called()

    def test_api_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch("sys.argv", ["query_ai_intelligence.py", "--module", "anomaly-detection"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
