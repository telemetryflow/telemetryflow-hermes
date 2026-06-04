"""Mock TelemetryFlow API responses."""

import json
from unittest import mock


def mock_tfo_response(data, status=200):
    mock_resp = mock.MagicMock()
    mock_resp.status = status
    mock_resp.read.return_value = json.dumps(data).encode("utf-8")
    mock_resp.__enter__ = mock.MagicMock(return_value=mock_resp)
    mock_resp.__exit__ = mock.MagicMock(return_value=False)
    return mock_resp


def mock_tfo_error_response(status, message="Error"):
    import urllib.error

    err_body = mock.MagicMock()
    err_body.read.return_value = json.dumps({"error": message}).encode("utf-8")
    return urllib.error.HTTPError(
        url="http://localhost:3000/api/v2/test",
        code=status,
        msg=message,
        hdrs={},
        fp=err_body,
    )


def mock_clickhouse_response(rows, columns=None):
    if columns is None and rows:
        columns = list(rows[0].keys())
    elif columns is None:
        columns = []
    data = {
        "meta": [{"name": c, "type": "String"} for c in columns],
        "data": rows,
        "rows": len(rows),
        "statistics": {"elapsed": 0.005, "rows_read": len(rows)},
    }
    return mock_tfo_response(data)


class MockTFOApi:
    def __init__(self):
        self.responses = {}
        self.call_log = []

    def register(self, path_pattern, response_data, method="GET"):
        self.responses[(method, path_pattern)] = response_data

    def register_clickhouse(self, rows, columns=None):
        self.register("POST", "/telemetry/query", mock_clickhouse_response(rows, columns).read.return_value)

    def get_response(self, method, path):
        for (m, pattern), data in self.responses.items():
            if m == method and pattern in path:
                return data
        return {"status": "ok", "data": []}

    def clear(self):
        self.responses.clear()
        self.call_log.clear()
