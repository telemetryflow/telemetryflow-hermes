import json
from unittest import mock

MUST_HAVE_SECTIONS = [
    "Root Cause Analysis",
    "5W",
    "Timeline",
    "Impact",
    "What Happened",
    "Where Did It Happen",
    "When Did It Happen",
    "Why Did It Happen",
    "How Was It Resolved",
    "mermaid",
    "Action Items",
    "Lessons Learned",
]


def _import_tool():
    import importlib

    import generate_rca_report

    importlib.reload(generate_rca_report)
    return generate_rca_report


class TestGenerateRCAReport:
    def test_rca_action_default(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            [
                "generate_rca_report.py",
                "--action",
                "rca",
                "--alert_id",
                "alert-001",
                "--service",
                "payments-api",
                "--root_cause",
                "OOM due to memory leak in v2.3.1",
                "--remediation",
                "Rollback to v2.3.0",
                "--start_time",
                "2026-06-05T10:00:00Z",
                "--end_time",
                "2026-06-05T10:15:00Z",
                "--severity",
                "critical",
            ],
        ):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert output["format"] == "rca"
        assert "rca_report" in output
        assert "jira_ticket" in output
        assert "trello_card" in output
        assert output["submit_requested"] is False
        assert output["jira_enabled"] is False
        assert output["trello_enabled"] is False
        for section in MUST_HAVE_SECTIONS:
            assert section in output["rca_report"], f"Missing section: {section}"

    def test_jira_action_no_submit(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            [
                "generate_rca_report.py",
                "--action",
                "jira",
                "--alert_id",
                "alert-002",
                "--service",
                "auth-service",
                "--root_cause",
                "Cert rotation failure",
                "--remediation",
                "Restart after rotation",
                "--start_time",
                "2026-06-05T12:00:00Z",
                "--severity",
                "high",
                "--project_key",
                "INFRA",
            ],
        ):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert output["format"] == "jira"
        assert output["jira_ticket"]["project_key"] == "INFRA"
        assert "[RCA]" in output["jira_ticket"]["summary"]
        assert "jira_submission" not in output

    def test_trello_action_no_submit(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            [
                "generate_rca_report.py",
                "--action",
                "trello",
                "--alert_id",
                "alert-003",
                "--service",
                "api-gateway",
                "--root_cause",
                "Upstream timeout",
                "--start_time",
                "2026-06-05T14:00:00Z",
                "--severity",
                "medium",
            ],
        ):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert output["format"] == "trello"
        assert "[RCA]" in output["trello_card"]["name"]
        assert "trello_submission" not in output

    def test_all_action_no_submit(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            [
                "generate_rca_report.py",
                "--action",
                "all",
                "--alert_id",
                "alert-004",
                "--service",
                "redis-cluster",
                "--root_cause",
                "Backup window impact",
                "--remediation",
                "Wait for backup completion",
                "--start_time",
                "2026-06-05T02:00:00Z",
                "--severity",
                "low",
            ],
        ):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert output["format"] == "all"
        assert "rca_report" in output
        assert "jira_ticket" in output
        assert "trello_card" in output
        assert "jira_submission" not in output
        assert "trello_submission" not in output

    def test_submit_true_but_disabled(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            [
                "generate_rca_report.py",
                "--action",
                "all",
                "--submit",
                "true",
                "--service",
                "test-svc",
                "--root_cause",
                "Test",
                "--start_time",
                "2026-06-05T10:00:00Z",
            ],
        ):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert output["submit_requested"] is True
        assert output["jira_enabled"] is False
        assert output["trello_enabled"] is False
        assert "jira_submission" not in output
        assert "trello_submission" not in output

    def test_submit_true_with_jira_enabled(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        env = {
            "TELEMETRYFLOW_API_URL": "http://localhost:3000/api/v2",
            "TELEMETRYFLOW_API_KEY": "tfs_test",
            "JIRA_ENABLED": "true",
            "JIRA_URL": "https://test.atlassian.net",
            "JIRA_EMAIL": "test@test.com",
            "JIRA_API_TOKEN": "test-token",
        }
        with mock.patch.dict("os.environ", env, clear=False):
            with mock.patch(
                "sys.argv",
                [
                    "generate_rca_report.py",
                    "--action",
                    "all",
                    "--submit",
                    "true",
                    "--service",
                    "test-svc",
                    "--root_cause",
                    "Test",
                    "--start_time",
                    "2026-06-05T10:00:00Z",
                ],
            ):
                tool = _import_tool()
                jira_result = {
                    "submitted": True,
                    "issue_key": "INFRA-123",
                    "issue_id": "10001",
                    "issue_url": "https://test.atlassian.net/browse/INFRA-123",
                }
                with mock.patch.object(tool, "_submit_jira", return_value=jira_result):
                    tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert output["jira_enabled"] is True
        assert "jira_submission" in output
        sub = output["jira_submission"]
        assert sub["submitted"] is True
        assert sub["issue_key"] == "INFRA-123"

    def test_submit_true_with_trello_enabled(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        env = {
            "TELEMETRYFLOW_API_URL": "http://localhost:3000/api/v2",
            "TELEMETRYFLOW_API_KEY": "tfs_test",
            "TRELLO_ENABLED": "true",
            "TRELLO_API_KEY": "test-key",
            "TRELLO_API_TOKEN": "test-token",
            "TRELLO_BOARD_ID": "board-123",
            "TRELLO_LIST_ID_INCIDENTS": "list-456",
        }
        with mock.patch.dict("os.environ", env, clear=False):
            with mock.patch(
                "sys.argv",
                [
                    "generate_rca_report.py",
                    "--action",
                    "all",
                    "--submit",
                    "true",
                    "--service",
                    "test-svc",
                    "--root_cause",
                    "Test",
                    "--start_time",
                    "2026-06-05T10:00:00Z",
                ],
            ):
                tool = _import_tool()
                trello_result = {
                    "submitted": True,
                    "card_id": "card-999",
                    "card_url": "https://trello.com/c/abc123",
                    "board_id": "board-123",
                    "labels_added": 6,
                    "checklist_added": 7,
                }
                with mock.patch.object(tool, "_submit_trello", return_value=trello_result):
                    tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert output["trello_enabled"] is True
        assert "trello_submission" in output
        sub = output["trello_submission"]
        assert sub["submitted"] is True
        assert sub["card_url"] == "https://trello.com/c/abc123"

    def test_submit_false_by_default(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            [
                "generate_rca_report.py",
                "--action",
                "all",
                "--service",
                "test-svc",
                "--root_cause",
                "Test",
                "--start_time",
                "2026-06-05T10:00:00Z",
            ],
        ):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert output["submit_requested"] is False

    def test_mermaid_timeline_present(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            [
                "generate_rca_report.py",
                "--action",
                "rca",
                "--service",
                "test-svc",
                "--root_cause",
                "Test cause",
                "--start_time",
                "2026-06-05T10:00:00Z",
                "--severity",
                "high",
            ],
        ):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        report = output["rca_report"]
        assert "```mermaid" in report
        assert "timeline" in report
        assert "flowchart TD" in report

    def test_unknown_action_exits(self, mock_env, mock_urlopen, mock_exit):
        with mock.patch(
            "sys.argv",
            [
                "generate_rca_report.py",
                "--action",
                "invalid",
            ],
        ):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)


def _mock_ctx_resp(data):
    resp = mock.MagicMock()
    resp.status = 200
    resp.read.return_value = json.dumps(data).encode("utf-8")
    resp.__enter__ = mock.MagicMock(return_value=resp)
    resp.__exit__ = mock.MagicMock(return_value=False)
    return resp


class TestSubmitJiraDirect:
    def test_submit_jira_success(self, mock_env):
        env = {
            "TELEMETRYFLOW_API_URL": "http://localhost:3000/api/v2",
            "TELEMETRYFLOW_API_KEY": "tfs_test",
            "JIRA_URL": "https://test.atlassian.net",
            "JIRA_EMAIL": "test@test.com",
            "JIRA_API_TOKEN": "test-token",
        }
        jira_resp = _mock_ctx_resp({"key": "PROJ-42", "id": "99999"})
        with mock.patch.dict("os.environ", env, clear=False):
            with mock.patch("urllib.request.urlopen", return_value=jira_resp):
                tool = _import_tool()
                ticket = {
                    "project_key": "PROJ",
                    "summary": "[RCA] test",
                    "description": "desc",
                    "issue_type": "Incident",
                    "priority": "HIGH",
                    "labels": ["rca", "hermes"],
                    "components": ["backend"],
                }
                result = tool._submit_jira(ticket)

        assert result["submitted"] is True
        assert result["issue_key"] == "PROJ-42"
        assert "PROJ-42" in result["issue_url"]

    def test_submit_jira_missing_credentials(self, mock_env):
        env = {
            "TELEMETRYFLOW_API_URL": "http://localhost:3000/api/v2",
            "TELEMETRYFLOW_API_KEY": "tfs_test",
        }
        with mock.patch.dict("os.environ", env, clear=False):
            tool = _import_tool()
            result = tool._submit_jira({"project_key": "X", "summary": "s", "description": "d"})

        assert result["submitted"] is False
        assert "not configured" in result["error"]

    def test_submit_jira_http_error(self, mock_env):
        import urllib.error

        env = {
            "TELEMETRYFLOW_API_URL": "http://localhost:3000/api/v2",
            "TELEMETRYFLOW_API_KEY": "tfs_test",
            "JIRA_URL": "https://test.atlassian.net",
            "JIRA_EMAIL": "test@test.com",
            "JIRA_API_TOKEN": "test-token",
        }
        err_resp = mock.MagicMock()
        err_resp.read.return_value = b'{"errors":{}}'
        with mock.patch.dict("os.environ", env, clear=False):
            with mock.patch(
                "urllib.request.urlopen",
                side_effect=urllib.error.HTTPError(
                    url="https://test.atlassian.net/rest/api/2/issue",
                    code=400,
                    msg="Bad Request",
                    hdrs={},
                    fp=err_resp,
                ),
            ):
                tool = _import_tool()
                result = tool._submit_jira({"project_key": "X", "summary": "s", "description": "d"})

        assert result["submitted"] is False
        assert "400" in result["error"]


class TestSubmitTrelloDirect:
    def test_submit_trello_success(self, mock_env):
        env = {
            "TELEMETRYFLOW_API_URL": "http://localhost:3000/api/v2",
            "TELEMETRYFLOW_API_KEY": "tfs_test",
            "TRELLO_API_KEY": "tk",
            "TRELLO_API_TOKEN": "tt",
            "TRELLO_BOARD_ID": "b1",
            "TRELLO_LIST_ID_INCIDENTS": "l1",
        }
        card_resp = _mock_ctx_resp({"id": "c1", "shortUrl": "https://trello.com/c/x"})
        label_resp1 = _mock_ctx_resp({"id": "lbl1"})
        label_resp2 = _mock_ctx_resp({"id": "lbl2"})
        checklist_resp = _mock_ctx_resp({"id": "cl1", "checkItems": []})
        item_resps = [_mock_ctx_resp({"id": f"it{i}"}) for i in range(7)]
        all_resps = [card_resp, label_resp1, label_resp2, checklist_resp] + item_resps

        with mock.patch.dict("os.environ", env, clear=False):
            with mock.patch("urllib.request.urlopen", side_effect=all_resps):
                tool = _import_tool()
                card = {
                    "name": "[RCA] test",
                    "description": "desc",
                    "labels": ["critical", "rca"],
                    "list": "Incidents",
                }
                result = tool._submit_trello(card)

        assert result["submitted"] is True
        assert result["card_url"] == "https://trello.com/c/x"
        assert result["labels_added"] == 2
        assert result["checklist_added"] == 7

    def test_submit_trello_missing_credentials(self, mock_env):
        env = {
            "TELEMETRYFLOW_API_URL": "http://localhost:3000/api/v2",
            "TELEMETRYFLOW_API_KEY": "tfs_test",
        }
        with mock.patch.dict("os.environ", env, clear=False):
            tool = _import_tool()
            result = tool._submit_trello({"name": "n", "description": "d"})

        assert result["submitted"] is False
        assert "not configured" in result["error"]

    def test_submit_trello_http_error(self, mock_env):
        import urllib.error

        env = {
            "TELEMETRYFLOW_API_URL": "http://localhost:3000/api/v2",
            "TELEMETRYFLOW_API_KEY": "tfs_test",
            "TRELLO_API_KEY": "tk",
            "TRELLO_API_TOKEN": "tt",
            "TRELLO_LIST_ID_INCIDENTS": "l1",
        }
        err_resp = mock.MagicMock()
        err_resp.read.return_value = b'{"error":"bad"}'
        with mock.patch.dict("os.environ", env, clear=False):
            with mock.patch(
                "urllib.request.urlopen",
                side_effect=urllib.error.HTTPError(
                    url="https://api.trello.com/1/cards",
                    code=401,
                    msg="Unauthorized",
                    hdrs={},
                    fp=err_resp,
                ),
            ):
                tool = _import_tool()
                result = tool._submit_trello({"name": "n", "description": "d"})

        assert result["submitted"] is False
        assert "401" in result["error"]


class TestShouldSubmitFlags:
    def test_jira_enabled_true(self, mock_env):
        with mock.patch.dict("os.environ", {"JIRA_ENABLED": "true"}, clear=False):
            tool = _import_tool()
            assert tool._should_submit_jira() is True

    def test_jira_enabled_false(self, mock_env):
        with mock.patch.dict("os.environ", {"JIRA_ENABLED": "false"}, clear=False):
            tool = _import_tool()
            assert tool._should_submit_jira() is False

    def test_jira_enabled_default(self, mock_env):
        env = {"TELEMETRYFLOW_API_URL": "http://localhost:3000/api/v2", "TELEMETRYFLOW_API_KEY": "tfs_test"}
        with mock.patch.dict("os.environ", env, clear=True):
            tool = _import_tool()
            assert tool._should_submit_jira() is False

    def test_trello_enabled_true(self, mock_env):
        with mock.patch.dict("os.environ", {"TRELLO_ENABLED": "yes"}, clear=False):
            tool = _import_tool()
            assert tool._should_submit_trello() is True

    def test_trello_enabled_one(self, mock_env):
        with mock.patch.dict("os.environ", {"TRELLO_ENABLED": "1"}, clear=False):
            tool = _import_tool()
            assert tool._should_submit_trello() is True


class TestSubmitConnectionErrors:
    def test_submit_jira_connection_error(self, mock_env):
        import urllib.error

        env = {
            "TELEMETRYFLOW_API_URL": "http://localhost:3000/api/v2",
            "TELEMETRYFLOW_API_KEY": "tfs_test",
            "JIRA_URL": "https://test.atlassian.net",
            "JIRA_EMAIL": "test@test.com",
            "JIRA_API_TOKEN": "test-token",
        }
        with mock.patch.dict("os.environ", env, clear=False):
            with mock.patch(
                "urllib.request.urlopen",
                side_effect=urllib.error.URLError(reason="Connection refused"),
            ):
                tool = _import_tool()
                result = tool._submit_jira({"project_key": "X", "summary": "s", "description": "d"})

        assert result["submitted"] is False
        assert "Connection refused" in result["error"]

    def test_submit_trello_connection_error(self, mock_env):
        import urllib.error

        env = {
            "TELEMETRYFLOW_API_URL": "http://localhost:3000/api/v2",
            "TELEMETRYFLOW_API_KEY": "tfs_test",
            "TRELLO_API_KEY": "tk",
            "TRELLO_API_TOKEN": "tt",
            "TRELLO_LIST_ID_INCIDENTS": "l1",
        }
        with mock.patch.dict("os.environ", env, clear=False):
            with mock.patch(
                "urllib.request.urlopen",
                side_effect=urllib.error.URLError(reason="Network unreachable"),
            ):
                tool = _import_tool()
                result = tool._submit_trello({"name": "n", "description": "d"})

        assert result["submitted"] is False
        assert "Network unreachable" in result["error"]


class TestTrelloHelpers:
    def test_add_labels_empty(self, mock_env):
        tool = _import_tool()
        result = tool._trello_add_labels("c1", "k", "t", [])
        assert result == {"added": 0}

    def test_add_checklist_error(self, mock_env):
        import urllib.error

        with mock.patch(
            "urllib.request.urlopen",
            side_effect=urllib.error.HTTPError(
                url="https://api.trello.com/1/cards/c1/checklists",
                code=500,
                msg="Server Error",
                hdrs={},
                fp=mock.MagicMock(read=lambda: b"error"),
            ),
        ):
            tool = _import_tool()
            result = tool._trello_add_checklist("c1", "k", "t")
        assert result == {"added": 0}

    def test_add_labels_success(self, mock_env):
        resp = mock.MagicMock()
        resp.read.return_value = b'{"id":"lbl1"}'
        resp.__enter__ = mock.MagicMock(return_value=resp)
        resp.__exit__ = mock.MagicMock(return_value=False)

        with mock.patch("urllib.request.urlopen", return_value=resp):
            tool = _import_tool()
            result = tool._trello_add_labels("c1", "k", "t", ["critical", "hermes"])
        assert result["added"] == 2


class TestRCAMainJiraTrelloSubmitActions:
    def test_jira_submit_action(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        env = {
            "TELEMETRYFLOW_API_URL": "http://localhost:3000/api/v2",
            "TELEMETRYFLOW_API_KEY": "tfs_test",
        }
        with mock.patch.dict("os.environ", env, clear=False):
            with mock.patch(
                "sys.argv",
                [
                    "generate_rca_report.py",
                    "--action",
                    "jira-submit",
                    "--service",
                    "svc",
                    "--root_cause",
                    "Test",
                    "--start_time",
                    "2026-06-05T10:00:00Z",
                ],
            ):
                tool = _import_tool()
                jira_result = {"submitted": True, "issue_key": "X-1", "issue_id": "1", "issue_url": "https://x/X-1"}
                with mock.patch.object(tool, "_submit_jira", return_value=jira_result):
                    tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert output["format"] == "jira"
        assert "jira_submission" in output
        assert output["jira_submission"]["issue_key"] == "X-1"

    def test_trello_submit_action(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        env = {
            "TELEMETRYFLOW_API_URL": "http://localhost:3000/api/v2",
            "TELEMETRYFLOW_API_KEY": "tfs_test",
        }
        with mock.patch.dict("os.environ", env, clear=False):
            with mock.patch(
                "sys.argv",
                [
                    "generate_rca_report.py",
                    "--action",
                    "trello-submit",
                    "--service",
                    "svc",
                    "--root_cause",
                    "Test",
                    "--start_time",
                    "2026-06-05T10:00:00Z",
                ],
            ):
                tool = _import_tool()
                trello_result = {
                    "submitted": True,
                    "card_id": "c1",
                    "card_url": "https://trello.com/c/x",
                    "labels_added": 0,
                    "checklist_added": 0,
                }
                with mock.patch.object(tool, "_submit_trello", return_value=trello_result):
                    tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert output["format"] == "trello"
        assert "trello_submission" in output


class TestRCATimelineWithData:
    def test_rca_with_alert_id(self, mock_env, mock_urlopen, capture_stdout):
        _, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": [{"id": "a1", "status": "firing"}]}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            [
                "generate_rca_report.py",
                "--action",
                "rca",
                "--alert_id",
                "a1",
                "--service",
                "payments-api",
                "--root_cause",
                "OOM",
                "--start_time",
                "2026-06-05T10:00:00Z",
                "--end_time",
                "2026-06-05T10:15:00Z",
                "--severity",
                "critical",
            ],
        ):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert "rca_report" in output
        assert "ALERT_FIRED" in output["rca_report"]
