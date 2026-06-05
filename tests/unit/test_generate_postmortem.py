import json
from unittest import mock

MUST_HAVE_SECTIONS = [
    "Postmortem",
    "Summary",
    "Timeline",
    "Root Cause",
    "Resolution",
    "Lessons Learned",
    "What Went Well",
    "What Could Be Improved",
    "Action Items",
    "5W",
    "mermaid",
    "Appendix",
]


def _import_tool():
    import importlib

    import generate_postmortem

    importlib.reload(generate_postmortem)
    return generate_postmortem


class TestGeneratePostmortem:
    def test_postmortem_full(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            [
                "generate_postmortem.py",
                "--action",
                "postmortem",
                "--alert_id",
                "alert-pm-001",
                "--service",
                "payments-api",
                "--root_cause",
                "Memory leak in v2.3.1",
                "--remediation",
                "Rollback to v2.3.0",
                "--start_time",
                "2026-06-05T10:00:00Z",
                "--end_time",
                "2026-06-05T10:15:00Z",
                "--severity",
                "critical",
                "--what",
                "OOM kills on payments-api pods",
                "--why",
                "Memory leak introduced in v2.3.1 deploy",
                "--went_well",
                "Fast detection|Automated triage|Quick rollback",
                "--improve",
                "Add memory threshold alert|Pre-deploy memory test",
                "--lucky",
                "Low traffic period",
            ],
        ):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert output["format"] == "markdown"
        for section in MUST_HAVE_SECTIONS:
            assert section in output["report"], f"Missing section: {section}"
        assert "Fast detection" in output["report"]
        assert "Add memory threshold" in output["report"]

    def test_postmortem_template(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            [
                "generate_postmortem.py",
                "--action",
                "template",
            ],
        ):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert output["format"] == "template"
        assert "{{" in output["template"]
        assert "INCIDENT_TITLE" in output["template"]
        assert "mermaid" in output["template"]

    def test_postmortem_with_timeline_events(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        timeline = json.dumps(
            [
                {"timestamp": "2026-06-05T10:00:00Z", "event": "ALERT_FIRED", "detail": "CPU spike detected"},
                {"timestamp": "2026-06-05T10:01:30Z", "event": "TRIAGE", "detail": "Classified CRITICAL"},
                {"timestamp": "2026-06-05T10:05:00Z", "event": "ROOT_CAUSE", "detail": "Memory leak found"},
            ]
        )

        with mock.patch(
            "sys.argv",
            [
                "generate_postmortem.py",
                "--action",
                "postmortem",
                "--alert_id",
                "alert-pm-002",
                "--service",
                "api-gateway",
                "--root_cause",
                "Memory leak",
                "--remediation",
                "Restart pods",
                "--start_time",
                "2026-06-05T10:00:00Z",
                "--severity",
                "high",
                "--timeline_events",
                timeline,
            ],
        ):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert "CPU spike detected" in output["report"]
        assert "10:00:00" in output["report"]

    def test_postmortem_with_alert_id(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": [{"id": "alert-pm-003"}]}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            [
                "generate_postmortem.py",
                "--action",
                "postmortem",
                "--alert_id",
                "alert-pm-003",
                "--service",
                "web-api",
                "--root_cause",
                "Timeout",
                "--start_time",
                "2026-06-05T10:00:00Z",
                "--severity",
                "high",
            ],
        ):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert "Postmortem" in output["report"]

    def test_postmortem_with_invalid_timeline_json(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            [
                "generate_postmortem.py",
                "--action",
                "postmortem",
                "--service",
                "web-api",
                "--root_cause",
                "Timeout",
                "--start_time",
                "2026-06-05T10:00:00Z",
                "--severity",
                "high",
                "--timeline_events",
                "not-valid-json",
            ],
        ):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert "Postmortem" in output["report"]

    def test_unknown_action_exits(self, mock_env, mock_urlopen, mock_exit):
        with mock.patch(
            "sys.argv",
            [
                "generate_postmortem.py",
                "--action",
                "invalid",
            ],
        ):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
