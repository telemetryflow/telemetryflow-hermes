"""Tests for check_db_monitoring.py tool."""

import contextlib
import json
import os
from unittest import mock


def _import_tool():
    import importlib

    import check_db_monitoring

    importlib.reload(check_db_monitoring)
    return check_db_monitoring


class TestCheckDbMonitoring:
    def test_inventory_no_db_type(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_db_monitoring.py", "--resource", "inventory"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/db-monitoring/inventory" in call_url
        assert "dbType=" not in call_url

    def test_inventory_with_db_type(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": [{"instance": "pg-prod-1", "dbType": "postgresql"}]}).encode(
            "utf-8"
        )

        with mock.patch("sys.argv", ["check_db_monitoring.py", "--resource", "inventory", "--db_type", "postgresql"]):
            tool = _import_tool()
            tool.main()

        output = json.loads(capture_stdout.getvalue())
        assert "data" in output
        call_url = m.call_args[0][0].full_url
        assert "/db-monitoring/inventory" in call_url
        assert "dbType=postgresql" in call_url

    def test_qan_with_db_type(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_db_monitoring.py", "--resource", "qan", "--db_type", "mysql"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "/db-monitoring/query-analytics" in call_url
        assert "dbType=mysql" in call_url

    def test_qan_with_workspace(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_db_monitoring.py", "--resource", "qan"]):
            tool = _import_tool()
            tool.main()

        call_url = m.call_args[0][0].full_url
        assert "workspaceId=" in call_url

    def test_slow_queries(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_db_monitoring.py", "--resource", "slow-queries", "--db_type", "mysql"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert "mysql" in body.get("sql", "")
        assert "qan_metrics" in body.get("sql", "")

    def test_slow_queries_with_min_duration(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            [
                "check_db_monitoring.py",
                "--resource",
                "slow-queries",
                "--db_type",
                "postgresql",
                "--min_duration",
                "100",
            ],
        ):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert "100" in body.get("sql", "")

    def test_slow_queries_missing_db_type(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["check_db_monitoring.py", "--resource", "slow-queries"]):
            tool = _import_tool()
            with contextlib.suppress(UnboundLocalError):
                tool.main()
            mock_exit.assert_called_with(1)

    def test_engine_metrics_clickhouse(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch(
            "sys.argv", ["check_db_monitoring.py", "--resource", "engine-metrics", "--db_type", "clickhouse"]
        ):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert "db_clickhouse_metrics" in body.get("sql", "")

    def test_engine_metrics_aurora(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_db_monitoring.py", "--resource", "engine-metrics", "--db_type", "aurora"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert "db_aurora_metrics_1m" in body.get("sql", "")

    def test_engine_metrics_mssql(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_db_monitoring.py", "--resource", "engine-metrics", "--db_type", "mssql"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert "db_mssql_metrics" in body.get("sql", "")

    def test_engine_metrics_timescaledb(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch(
            "sys.argv", ["check_db_monitoring.py", "--resource", "engine-metrics", "--db_type", "timescaledb"]
        ):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert "db_timescaledb_metrics" in body.get("sql", "")

    def test_engine_metrics_with_instance_id(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            ["check_db_monitoring.py", "--resource", "engine-metrics", "--db_type", "mysql", "--instance_id", "inst-1"],
        ):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert "inst-1" in body.get("sql", "")

    def test_engine_metrics_missing_db_type(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["check_db_monitoring.py", "--resource", "engine-metrics"]):
            tool = _import_tool()
            with contextlib.suppress(UnboundLocalError, KeyError):
                tool.main()
            mock_exit.assert_called_with(1)

    def test_engine_metrics_unsupported_db_type(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["check_db_monitoring.py", "--resource", "engine-metrics", "--db_type", "foobar"]):
            tool = _import_tool()
            with contextlib.suppress(UnboundLocalError, KeyError):
                tool.main()
            mock_exit.assert_called_with(1)

    def test_wait_stats(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_db_monitoring.py", "--resource", "wait-stats", "--db_type", "mssql"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert "db_mssql_waits" in body.get("sql", "")

    def test_wait_stats_with_instance(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            ["check_db_monitoring.py", "--resource", "wait-stats", "--db_type", "mssql", "--instance_id", "sql-prod-1"],
        ):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert "sql-prod-1" in body.get("sql", "")

    def test_wait_stats_non_mssql(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["check_db_monitoring.py", "--resource", "wait-stats", "--db_type", "mysql"]):
            tool = _import_tool()
            with contextlib.suppress(UnboundLocalError):
                tool.main()
            mock_exit.assert_called_with(1)

    def test_top_queries(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_db_monitoring.py", "--resource", "top-queries", "--db_type", "mysql"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert "db_mysql_queries" in body.get("sql", "")

    def test_top_queries_postgresql(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch("sys.argv", ["check_db_monitoring.py", "--resource", "top-queries", "--db_type", "postgresql"]):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert "db_postgresql_queries" in body.get("sql", "")

    def test_top_queries_with_instance(self, mock_env, mock_urlopen, capture_stdout):
        m, mock_resp = mock_urlopen
        mock_resp.read.return_value = json.dumps({"data": []}).encode("utf-8")

        with mock.patch(
            "sys.argv",
            ["check_db_monitoring.py", "--resource", "top-queries", "--db_type", "aurora", "--instance_id", "aur-1"],
        ):
            tool = _import_tool()
            tool.main()

        body = json.loads(m.call_args[0][0].data)
        assert "aur-1" in body.get("sql", "")

    def test_top_queries_missing_db_type(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["check_db_monitoring.py", "--resource", "top-queries"]):
            tool = _import_tool()
            with contextlib.suppress(UnboundLocalError):
                tool.main()
            mock_exit.assert_called_with(1)

    def test_top_queries_unsupported_db_type(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["check_db_monitoring.py", "--resource", "top-queries", "--db_type", "sqlite3"]):
            tool = _import_tool()
            with contextlib.suppress(UnboundLocalError, KeyError):
                tool.main()
            mock_exit.assert_called_with(1)

    def test_unknown_resource(self, mock_env, mock_exit):
        with mock.patch("sys.argv", ["check_db_monitoring.py", "--resource", "foobar"]):
            tool = _import_tool()
            with contextlib.suppress(UnboundLocalError):
                tool.main()
            mock_exit.assert_called_with(1)

    def test_no_api_key_exits(self, mock_exit):
        env = {k: v for k, v in os.environ.items() if k != "TELEMETRYFLOW_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True):
            with mock.patch("sys.argv", ["check_db_monitoring.py", "--resource", "inventory"]):
                tool = _import_tool()
                tool.main()
                mock_exit.assert_called()

    def test_api_error_exits(self, mock_env, mock_urlopen_error, mock_exit):
        with mock.patch("sys.argv", ["check_db_monitoring.py", "--resource", "inventory"]):
            tool = _import_tool()
            tool.main()
            mock_exit.assert_called_with(1)
