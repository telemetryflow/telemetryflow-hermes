-- Create read-only ClickHouse user for Hermes agents
-- Run on ClickHouse server as admin

CREATE USER IF NOT EXISTS hermes_readonly
  IDENTIFIED BY 'CHANGE_ME_SECURE_PASSWORD'
  DEFAULT DATABASE telemetryflow
  SETTINGS readonly = 1;

GRANT SELECT ON telemetryflow.* TO hermes_readonly;

-- Restrict to telemetry tables only (no access to system/config tables)
-- Only grant on the tables Hermes actually queries:
GRANT SELECT ON telemetryflow.metrics_1m TO hermes_readonly;
GRANT SELECT ON telemetryflow.metrics_5m TO hermes_readonly;
GRANT SELECT ON telemetryflow.metrics_1h TO hermes_readonly;
GRANT SELECT ON telemetryflow.otel_logs TO hermes_readonly;
GRANT SELECT ON telemetryflow.otel_traces TO hermes_readonly;
GRANT SELECT ON telemetryflow.exemplars TO hermes_readonly;
GRANT SELECT ON telemetryflow.exemplars_1h TO hermes_readonly;
GRANT SELECT ON telemetryflow.signal_correlations_1h TO hermes_readonly;
GRANT SELECT ON telemetryflow.service_latency_percentiles_1h TO hermes_readonly;
GRANT SELECT ON telemetryflow.service_error_rates_1h TO hermes_readonly;
GRANT SELECT ON telemetryflow.logs_1h TO hermes_readonly;
GRANT SELECT ON telemetryflow.qan_metrics TO hermes_readonly;
GRANT SELECT ON telemetryflow.audit_logs TO hermes_readonly;
GRANT SELECT ON telemetryflow.audit_logs_1h TO hermes_readonly;
GRANT SELECT ON telemetryflow.uptime_checks TO hermes_readonly;
GRANT SELECT ON telemetryflow.kubernetes_metrics_1h TO hermes_readonly;
GRANT SELECT ON telemetryflow.vm_metrics_1h TO hermes_readonly;
GRANT SELECT ON telemetryflow.service_map_metrics_1h TO hermes_readonly;
GRANT SELECT ON telemetryflow.network_map_traffic_1h TO hermes_readonly;
GRANT SELECT ON telemetryflow.network_map_connection_metrics_1h TO hermes_readonly;

-- Verify
SHOW GRANTS FOR hermes_readonly;
