import json
from unittest import mock

TEMPLATE_SECTIONS = [
    "Document Control",
    "Executive Summary",
    "Impact Assessment",
    "5W Analysis",
    "What Happened",
    "Where Did It Happen",
    "When Did It Happen",
    "Why Did It Happen",
    "How Was It Resolved",
    "Timeline",
    "Root Cause Deep Dive",
    "Contributing Factors",
    "Causal Chain",
    "Lessons Learned",
    "Action Items",
    "Jira",
    "Trello",
    "Approval",
    "mermaid",
    "Blast Radius",
    "Document Control",
]


def _import_tool():
    import importlib

    import generate_rca_template

    importlib.reload(generate_rca_template)
    return generate_rca_template


class TestGenerateRCATemplate:
    def test_template_has_all_sections(self, mock_env, mock_urlopen, capture_stdout):
        with mock.patch(
            "sys.argv",
            [
                "generate_rca_template.py",
                "--title",
                "Test Incident",
                "--service",
                "payments-api",
                "--severity",
                "critical",
            ],
        ):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert output["type"] == "blank_rca_template"
        assert output["format"] == "markdown"
        for section in TEMPLATE_SECTIONS:
            assert section in output["report"], f"Missing section: {section}"

    def test_template_has_placeholders(self, mock_env, mock_urlopen, capture_stdout):
        with mock.patch(
            "sys.argv",
            [
                "generate_rca_template.py",
            ],
        ):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert "{{" in output["report"]
        assert "SERVICE_NAME" in output["report"]
        assert "SEVERITY" in output["report"]

    def test_template_mermaid_diagrams(self, mock_env, mock_urlopen, capture_stdout):
        with mock.patch(
            "sys.argv",
            [
                "generate_rca_template.py",
                "--service",
                "auth-service",
            ],
        ):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        report = output["report"]
        assert report.count("```mermaid") >= 3

    def test_template_jira_trello_sections(self, mock_env, mock_urlopen, capture_stdout):
        with mock.patch(
            "sys.argv",
            [
                "generate_rca_template.py",
                "--service",
                "api-gateway",
                "--severity",
                "high",
            ],
        ):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        report = output["report"]
        assert "Jira Ticket" in report
        assert "Trello Card" in report
        assert "JIRA_PROJECT" in report
