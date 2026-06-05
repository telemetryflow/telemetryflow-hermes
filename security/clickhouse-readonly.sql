-- Create read-only ClickHouse user for Hermes agents
-- Run via: bash security/setup-readonly-user.sh <password>
-- Or manually replace ${TELEMETRYFLOW_DB_NAME} with your database name

CREATE USER IF NOT EXISTS hermes_readonly
  IDENTIFIED BY 'CHANGE_ME_SECURE_PASSWORD'
  DEFAULT DATABASE ${TELEMETRYFLOW_DB_NAME}
  SETTINGS readonly = 1;

GRANT SELECT ON ${TELEMETRYFLOW_DB_NAME}.* TO hermes_readonly;

-- Restrict to telemetry tables only (no access to system/config tables)
-- Only grant on the tables Hermes actually queries:
GRANT SELECT ON ${TELEMETRYFLOW_DB_NAME}.metrics_1m TO hermes_readonly;
GRANT SELECT ON ${TELEMETRYFLOW_DB_NAME}.metrics_5m TO hermes_readonly;
GRANT SELECT ON ${TELEMETRYFLOW_DB_NAME}.metrics_1h TO hermes_readonly;
GRANT SELECT ON ${TELEMETRYFLOW_DB_NAME}.otel_logs TO hermes_readonly;
GRANT SELECT ON ${TELEMETRYFLOW_DB_NAME}.otel_traces TO hermes_readonly;
GRANT SELECT ON ${TELEMETRYFLOW_DB_NAME}.exemplars TO hermes_readonly;
GRANT SELECT ON ${TELEMETRYFLOW_DB_NAME}.exemplars_1h TO hermes_readonly;
GRANT SELECT ON ${TELEMETRYFLOW_DB_NAME}.signal_correlations_1h TO hermes_readonly;
GRANT SELECT ON ${TELEMETRYFLOW_DB_NAME}.service_latency_percentiles_1h TO hermes_readonly;
GRANT SELECT ON ${TELEMETRYFLOW_DB_NAME}.service_error_rates_1h TO hermes_readonly;
GRANT SELECT ON ${TELEMETRYFLOW_DB_NAME}.logs_1h TO hermes_readonly;
GRANT SELECT ON ${TELEMETRYFLOW_DB_NAME}.qan_metrics TO hermes_readonly;
GRANT SELECT ON ${TELEMETRYFLOW_DB_NAME}.audit_logs TO hermes_readonly;
GRANT SELECT ON ${TELEMETRYFLOW_DB_NAME}.audit_logs_1h TO hermes_readonly;
GRANT SELECT ON ${TELEMETRYFLOW_DB_NAME}.uptime_checks TO hermes_readonly;
GRANT SELECT ON ${TELEMETRYFLOW_DB_NAME}.kubernetes_metrics_1h TO hermes_readonly;
GRANT SELECT ON ${TELEMETRYFLOW_DB_NAME}.vm_metrics_1h TO hermes_readonly;
GRANT SELECT ON ${TELEMETRYFLOW_DB_NAME}.service_map_metrics_1h TO hermes_readonly;
GRANT SELECT ON ${TELEMETRYFLOW_DB_NAME}.network_map_traffic_1h TO hermes_readonly;
GRANT SELECT ON ${TELEMETRYFLOW_DB_NAME}.network_map_connection_metrics_1h TO hermes_readonly;

-- Verify
SHOW GRANTS FOR hermes_readonly;
