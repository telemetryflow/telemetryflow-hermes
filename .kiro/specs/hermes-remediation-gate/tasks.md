# Implementation Plan: Hermes Remediation Gate

## Phase 1: Foundation (Core State Machine and Models)

- [ ] 1. Create data models
  - [ ] 1.1 Define `RiskLevel` enum (LOW, MEDIUM, HIGH, CRITICAL)
    - File: `profiles/remediator/gate/models.py`
    - _Dependencies: None_
    - _Tests: `tests/test_gate/test_models.py`_
  - [ ] 1.2 Define `ApprovalState` enum (all states from state machine)
    - _Dependencies: None_
    - _Tests: `tests/test_gate/test_models.py`_
  - [ ] 1.3 Define `ApprovalContext` dataclass (alert_summary, root_cause, evidence_links, blast_radius, rollback_plan, reviewer_verdict, reviewer_caveats)
    - _Dependencies: Task 1_
    - _Tests: `tests/test_gate/test_models.py`_
  - [ ] 1.4 Define `StateTransition` dataclass (from_state, to_state, timestamp, actor, reason)
    - _Dependencies: Task 1_
    - _Tests: `tests/test_gate/test_models.py`_
  - [ ] 1.5 Define `ApprovalRequest` dataclass (request_id, tool, params, context, risk_level, state, created_at, updated_at, timeout_at, approver_id, escalation_target, transitions, outcome)
    - _Dependencies: Task 1_
    - _Tests: `tests/test_gate/test_models.py`_
  - [ ] 1.6 Define `HumanResponse` dataclass (request_id, action: approve|reject|manual, user_id, reason)
    - _Dependencies: Task 1_
    - _Tests: `tests/test_gate/test_models.py`_
  - [ ] 1.7 Define `VerificationResult` dataclass (passed, evidence, errors_found)
    - _Dependencies: Task 1_
    - _Tests: `tests/test_gate/test_models.py`_
  - [ ] 1.8 Add JSON serialization/deserialization and validation for all models
    - Validate all fields present, enum values valid, timestamps are ISO 8601
    - _Dependencies: Task 1_
    - _Tests: `tests/test_gate/test_models.py` — serialization round-trips, validation edge cases_

- [ ] 2. Implement state machine
  - [ ] 2.1 Define the valid state transitions map (from_state → set of valid to_states)
    - File: `profiles/remediator/gate/state_machine.py`
    - _Dependencies: Task 1_
    - _Tests: `tests/test_gate/test_state_machine.py`_
  - [ ] 2.2 Implement `ApprovalStateMachine.transition()` — validates transition is legal, appends StateTransition, updates updated_at
    - _Dependencies: Task 2_
    - _Tests: `tests/test_gate/test_state_machine.py`_
  - [ ] 2.3 Implement `ApprovalStateMachine.can_transition()` → bool
    - _Dependencies: Task 2_
    - _Tests: `tests/test_gate/test_state_machine.py`_
  - [ ] 2.4 Implement `ApprovalStateMachine.get_valid_transitions()` → set[ApprovalState]
    - _Dependencies: Task 2_
    - _Tests: `tests/test_gate/test_state_machine.py`_
  - [ ] 2.5 Implement `ApprovalStateMachine.is_terminal()` — COMPLETED, REJECTED, CANCELLED, ROLLED_BACK, MANUALLY_REJECTED, ESCALATION_TIMEOUT
    - _Dependencies: Task 2_
    - _Tests: `tests/test_gate/test_state_machine.py`_
  - [ ] 2.6 Reject invalid transitions with `InvalidTransitionError`; ensure idempotency (transitioning to current state is a no-op)
    - _Dependencies: Task 2_
    - _Tests: `tests/test_gate/test_state_machine.py` — all valid transitions, all invalid transitions, idempotency, terminal state detection_

- [ ] 3. Implement state persistence
  - [ ] 3.1 Implement `FilePersistence.__init__(persistence_dir)` — create directory if not exists
    - File: `profiles/remediator/gate/persistence.py`
    - _Dependencies: Task 1_
    - _Tests: `tests/test_gate/test_persistence.py`_
  - [ ] 3.2 Implement `FilePersistence.save(request)` — write `{request_id}.json` atomically (write to `.tmp`, then rename)
    - _Dependencies: Task 3_
    - _Tests: `tests/test_gate/test_persistence.py`_
  - [ ] 3.3 Implement `FilePersistence.load(request_id)` → ApprovalRequest | None
    - _Dependencies: Task 3_
    - _Tests: `tests/test_gate/test_persistence.py`_
  - [ ] 3.4 Implement `FilePersistence.load_active()` — load all non-terminal requests
    - _Dependencies: Task 3_
    - _Tests: `tests/test_gate/test_persistence.py`_
  - [ ] 3.5 Implement `FilePersistence.load_history(limit)` — load recent terminal-state requests, sorted by updated_at desc
    - _Dependencies: Task 3_
    - _Tests: `tests/test_gate/test_persistence.py`_
  - [ ] 3.6 Implement `FilePersistence.delete(request_id)` — remove state file
    - _Dependencies: Task 3_
    - _Tests: `tests/test_gate/test_persistence.py`_
  - [ ] 3.7 Implement `FilePersistence.cleanup_older_than(days)` — archive/delete old records, return count
    - _Dependencies: Task 3_
    - _Tests: `tests/test_gate/test_persistence.py`_
  - [ ] 3.8 Use file-level locking (fcntl/flock) for concurrent access; handle corrupted files gracefully (log warning, skip, don't crash)
    - _Dependencies: Task 3_
    - _Tests: `tests/test_gate/test_persistence.py` — save/load round-trip, concurrent writes, corrupted file handling, cleanup_

## Phase 2: Telegram Gateway

- [ ] 4. Implement Telegram Bot API client
  - [ ] 4.1 Implement `TelegramGateway.__init__(bot_token, chat_id, config)` — store credentials and config
    - File: `profiles/remediator/gate/telegram_gateway.py`
    - _Dependencies: Task 1_
    - _Tests: `tests/test_gate/test_telegram_gateway.py`_
  - [ ] 4.2 Implement `send_approval_request(request)` → message_id — format and send approval message with inline keyboard
    - _Dependencies: Task 4_
    - _Tests: `tests/test_gate/test_telegram_gateway.py`_
  - [ ] 4.3 Implement `send_timeout_warning`, `send_escalation`, `send_execution_result`, `send_rollback_notification`
    - _Dependencies: Task 4_
    - _Tests: `tests/test_gate/test_telegram_gateway.py`_
  - [ ] 4.4 Implement `start_polling(callback_handler)` and `stop_polling()` — long-poll getUpdates, route callbacks
    - _Dependencies: Task 4_
    - _Tests: `tests/test_gate/test_telegram_gateway.py`_
  - [ ] 4.5 Implement `format_approval_message(request)` — MarkdownV2 format with all required fields
    - _Dependencies: Task 4_
    - _Tests: `tests/test_gate/test_telegram_gateway.py`_
  - [ ] 4.6 Implement `format_timeout_warning`, `format_escalation_message`, `format_result_message`
    - _Dependencies: Task 4_
    - _Tests: `tests/test_gate/test_telegram_gateway.py`_
  - [ ] 4.7 Implement `build_approval_keyboard(request_id)` — three buttons: Approve, Reject, Manual Review; callback data format: `approve:{request_id}`, `reject:{request_id}`, `manual:{request_id}`
    - _Dependencies: Task 4_
    - _Tests: `tests/test_gate/test_telegram_gateway.py`_
  - [ ] 4.8 Implement retry logic: up to 3 retries on recoverable errors (429, 502/503/504), exponential backoff 1s/2s/4s; non-recoverable errors (400, 401, 403) → log and raise immediately
    - _Dependencies: Task 4_
    - _Tests: `tests/test_gate/test_telegram_gateway.py`_
  - [ ] 4.9 Implement message deduplication (track sent message IDs per request_id) and parse callback queries into `HumanResponse` objects
    - _Dependencies: Task 4_
    - _Tests: `tests/test_gate/test_telegram_gateway.py` — message formatting, keyboard building, retry logic, callback parsing, deduplication_

- [ ] 5. Implement callback routing and response handling
  - [ ] 5.1 Implement `CallbackRouter` — parse incoming callback_query updates from long poll
    - File: `profiles/remediator/gate/telegram_gateway.py` (continued)
    - _Dependencies: Task 4, Task 2_
    - _Tests: `tests/test_gate/test_telegram_gateway.py`_
  - [ ] 5.2 Extract action (approve/reject/manual) and request_id from callback_data
    - _Dependencies: Task 5_
    - _Tests: `tests/test_gate/test_telegram_gateway.py`_
  - [ ] 5.3 Validate request_id exists and is in PENDING or ESCALATED state
    - _Dependencies: Task 5_
    - _Tests: `tests/test_gate/test_telegram_gateway.py`_
  - [ ] 5.4 Answer callback query (acknowledge button press via answerCallbackQuery) and route to `ApprovalGate.handle_response()` with constructed `HumanResponse`
    - _Dependencies: Task 5_
    - _Tests: `tests/test_gate/test_telegram_gateway.py`_
  - [ ] 5.5 Update the original message to reflect the response (disable buttons, show chosen action)
    - _Dependencies: Task 5_
    - _Tests: `tests/test_gate/test_telegram_gateway.py`_
  - [ ] 5.6 Handle malformed callback data (log warning, answer with error) and stale callbacks (request in terminal state — answer with "Already processed")
    - _Dependencies: Task 5_
    - _Tests: `tests/test_gate/test_telegram_gateway.py` — callback routing, stale callbacks, malformed data_

## Phase 3: Tool Executor and Verifier

- [ ] 6. Implement tool executor
  - [ ] 6.1 Implement `ToolExecutor.__init__(tfo_api_url, tfo_api_key)`
    - File: `profiles/remediator/gate/tool_executor.py`
    - _Dependencies: Task 1_
    - _Tests: `tests/test_gate/test_tool_executor.py`_
  - [ ] 6.2 Implement `execute(request)` → ToolResult — execute the approved tool's API call
    - _Dependencies: Task 6_
    - _Tests: `tests/test_gate/test_tool_executor.py`_
  - [ ] 6.3 Implement `_execute_scale(params)` — POST `/kubernetes/deployments/scale`
    - _Dependencies: Task 6_
    - _Tests: `tests/test_gate/test_tool_executor.py`_
  - [ ] 6.4 Implement `_execute_restart(params)` — POST `/kubernetes/deployments/restart` or `/kubernetes/pods/restart`
    - _Dependencies: Task 6_
    - _Tests: `tests/test_gate/test_tool_executor.py`_
  - [ ] 6.5 Implement `_execute_rollback(params)` — POST `/kubernetes/deployments/rollback`
    - _Dependencies: Task 6_
    - _Tests: `tests/test_gate/test_tool_executor.py`_
  - [ ] 6.6 Implement `_execute_update_alert(params)` — PATCH `/alerts/rules/{rule_id}`
    - _Dependencies: Task 6_
    - _Tests: `tests/test_gate/test_tool_executor.py`_
  - [ ] 6.7 Implement pre-execution validation: `_pre_check_scale`, `_pre_check_restart`, `_pre_check_rollback`, `_pre_check_update_alert`
    - _Dependencies: Task 6_
    - _Tests: `tests/test_gate/test_tool_executor.py`_
  - [ ] 6.8 Return `ToolResult` with success/failure, HTTP status, response body; handle API errors; 30s timeout per call
    - _Dependencies: Task 6_
    - _Tests: `tests/test_gate/test_tool_executor.py` — pre-checks, execution, error handling, timeout_

- [ ] 7. Implement post-action verifier
  - [ ] 7.1 Implement `VerificationSuite.__init__(clickhouse_config, tfo_api_url, tfo_api_key)`
    - File: `profiles/remediator/gate/verifier.py`
    - _Dependencies: Task 1, Task 6_
    - _Tests: `tests/test_gate/test_verifier.py`_
  - [ ] 7.2 Implement `verify(request)` → VerificationResult — dispatch to tool-specific verification
    - _Dependencies: Task 7_
    - _Tests: `tests/test_gate/test_verifier.py`_
  - [ ] 7.3 Implement `_verify_scale(params)` — check replica count from `kubernetes_metrics_1h`, pod readiness
    - _Dependencies: Task 7_
    - _Tests: `tests/test_gate/test_verifier.py`_
  - [ ] 7.4 Implement `_verify_restart(params)` — pod status, check `otel_logs` for new errors within 60s
    - _Dependencies: Task 7_
    - _Tests: `tests/test_gate/test_verifier.py`_
  - [ ] 7.5 Implement `_verify_rollback(params)` — deployment rollout status, `service_error_rates_1h`
    - _Dependencies: Task 7_
    - _Tests: `tests/test_gate/test_verifier.py`_
  - [ ] 7.6 Implement `_verify_update_alert(params)` — query rule state, verify evaluation
    - _Dependencies: Task 7_
    - _Tests: `tests/test_gate/test_verifier.py`_
  - [ ] 7.7 Implement `_wait_for_propagation(seconds=30)` — configurable wait
    - _Dependencies: Task 7_
    - _Tests: `tests/test_gate/test_verifier.py`_
  - [ ] 7.8 Implement `_check_new_errors(namespace, since)` — query `otel_logs`
    - _Dependencies: Task 7_
    - _Tests: `tests/test_gate/test_verifier.py`_
  - [ ] 7.9 Implement `_check_dependent_services(service)` → HealthCheck — query `service_error_rates_1h`
    - _Dependencies: Task 7_
    - _Tests: `tests/test_gate/test_verifier.py`_
  - [ ] 7.10 Implement security verification: `_verify_audit_logs`, `_verify_rbac` (when context has SECURITY_ESCALATION)
    - _Dependencies: Task 7_
    - _Tests: `tests/test_gate/test_verifier.py`_
  - [ ] 7.11 Implement security verification: `_verify_secrets`, `_verify_network_policies` (when context has SECURITY_ESCALATION)
    - _Dependencies: Task 7_
    - _Tests: `tests/test_gate/test_verifier.py`_
  - [ ] 7.12 Overall timeout: 120 seconds
    - _Dependencies: Task 7_
    - _Tests: `tests/test_gate/test_verifier.py` — each verification path, timeout handling, security checks_

## Phase 4: Approval Gate Controller

- [ ] 8. Implement main controller
  - [ ] 8.1 Implement `ApprovalGate.__init__(config)` — load config, initialize sub-components
    - File: `profiles/remediator/gate/controller.py`
    - _Dependencies: Tasks 2, 3, 4, 5, 6, 7_
    - _Tests: `tests/test_gate/test_controller.py`_
  - [ ] 8.2 Implement `start()` — start Telegram polling, timeout checker
    - _Dependencies: Task 8_
    - _Tests: `tests/test_gate/test_controller.py`_
  - [ ] 8.3 Implement `stop()` — stop polling, flush state
    - _Dependencies: Task 8_
    - _Tests: `tests/test_gate/test_controller.py`_
  - [ ] 8.4 Implement `propose_action(tool, params, context)` — validate Three Gates (root cause confirmed, proportional response, readiness), assess risk level
    - _Dependencies: Task 8_
    - _Tests: `tests/test_gate/test_controller.py`_
  - [ ] 8.5 Implement `propose_action()` — create ApprovalRequest in PENDING state, persist, send via Telegram gateway, return request_id
    - _Dependencies: Task 8_
    - _Tests: `tests/test_gate/test_controller.py`_
  - [ ] 8.6 Implement `handle_response(response)` — load request, validate PENDING/ESCALATED state, transition state, persist, trigger execution if approved
    - _Dependencies: Task 8_
    - _Tests: `tests/test_gate/test_controller.py`_
  - [ ] 8.7 Implement `_execute_approved(request)` — transition to EXECUTING, run tool executor
    - _Dependencies: Task 8_
    - _Tests: `tests/test_gate/test_controller.py`_
  - [ ] 8.8 Implement `_execute_approved()` — if success transition to VERIFYING and run verifier; if execution or verification fails, transition to FAILED and trigger rollback
    - _Dependencies: Task 8_
    - _Tests: `tests/test_gate/test_controller.py`_
  - [ ] 8.9 Implement `_execute_rollback(request)` — transition to ROLLING_BACK, execute rollback from context.rollback_plan, transition to ROLLED_BACK, send notification; escalate immediately if rollback fails
    - _Dependencies: Task 8_
    - _Tests: `tests/test_gate/test_controller.py`_
  - [ ] 8.10 Implement `check_timeouts()` — load active requests, check if exceeded timeout_at, send warning at 50% timeout
    - _Dependencies: Task 8_
    - _Tests: `tests/test_gate/test_controller.py`_
  - [ ] 8.11 Implement `check_timeouts()` — transition timed-out requests; if auto_escalate_on_timeout, trigger escalation
    - _Dependencies: Task 8_
    - _Tests: `tests/test_gate/test_controller.py`_
  - [ ] 8.12 Implement `cancel_request(request_id, reason)`, `get_active_requests()`, `get_request_history(limit)`
    - _Dependencies: Task 8_
    - _Tests: `tests/test_gate/test_controller.py` — full lifecycle tests, timeout handling, cancellation, crash recovery_

- [ ] 9. Implement crash recovery
  - [ ] 9.1 Implement `_recover_on_startup()` — load all active (non-terminal) requests from persistence
    - File: `profiles/remediator/gate/controller.py` (continued)
    - _Dependencies: Task 8_
    - _Tests: `tests/test_gate/test_controller.py`_
  - [ ] 9.2 Recover EXECUTING requests: query TFO API to determine if the action completed
    - _Dependencies: Task 9_
    - _Tests: `tests/test_gate/test_controller.py`_
  - [ ] 9.3 EXECUTING recovery: if completed → transition to VERIFYING and run verification; if unknown → transition to FAILED and initiate rollback
    - _Dependencies: Task 9_
    - _Tests: `tests/test_gate/test_controller.py`_
  - [ ] 9.4 Recover VERIFYING requests: re-run verification
    - _Dependencies: Task 9_
    - _Tests: `tests/test_gate/test_controller.py`_
  - [ ] 9.5 Recover PENDING requests: check if timeout elapsed → TIMED_OUT; otherwise resume timeout monitoring
    - _Dependencies: Task 9_
    - _Tests: `tests/test_gate/test_controller.py`_
  - [ ] 9.6 Log all recovery actions
    - _Dependencies: Task 9_
    - _Tests: `tests/test_gate/test_controller.py` — recovery scenarios for each mid-crash state_

- [ ] 10. Implement queue management
  - [ ] 10.1 Implement `_enqueue_request(request)` — add to queue if another request is active
    - File: `profiles/remediator/gate/controller.py` (continued)
    - _Dependencies: Task 8_
    - _Tests: `tests/test_gate/test_controller.py`_
  - [ ] 10.2 Implement `_dequeue_next()` → ApprovalRequest | None — pop next request from queue
    - _Dependencies: Task 10_
    - _Tests: `tests/test_gate/test_controller.py`_
  - [ ] 10.3 Implement `_process_queue()` — if no active request, dequeue and start processing
    - _Dependencies: Task 10_
    - _Tests: `tests/test_gate/test_controller.py`_
  - [ ] 10.4 Implement `_check_queue_depth()` → int — current queue size
    - _Dependencies: Task 10_
    - _Tests: `tests/test_gate/test_controller.py`_
  - [ ] 10.5 Max queue depth from config (default: 5)
    - _Dependencies: Task 10_
    - _Tests: `tests/test_gate/test_controller.py`_
  - [ ] 10.6 If queue is full → escalate to human instead of enqueueing
    - _Dependencies: Task 10_
    - _Tests: `tests/test_gate/test_controller.py` — queue behavior, depth limits, overflow escalation_

## Phase 5: Integration and Configuration

- [ ] 11. Wire gate into Remediator profile
  - [ ] 11.1 Add `gate:` section to `profiles/remediator/config.yaml` with all configuration parameters
    - Files: `profiles/remediator/config.yaml`, `profiles/remediator/gate/__init__.py`
    - _Dependencies: Task 8_
    - _Tests: Manual integration test with live Telegram bot_
  - [ ] 11.2 Create `profiles/remediator/gate/__init__.py` with `create_gate(config)` factory function
    - _Dependencies: Task 11_
    - _Tests: Manual integration test_
  - [ ] 11.3 Export key classes: `ApprovalGate`, `ApprovalRequest`, `ApprovalContext`, `HumanResponse`
    - _Dependencies: Task 11_
    - _Tests: Manual integration test_
  - [ ] 11.4 Ensure gate is initialized on Remediator startup and stopped gracefully on shutdown
    - _Dependencies: Task 11_
    - _Tests: Manual integration test with live Telegram bot_

- [ ] 12. Implement gate middleware for tool interception
  - [ ] 12.1 When Remediator calls a `requires_approval` tool, intercept before execution
    - File: `profiles/remediator/gate/middleware.py`
    - _Dependencies: Task 11_
    - _Tests: `tests/test_gate/test_middleware.py`_
  - [ ] 12.2 Extract tool name and parameters
    - _Dependencies: Task 12_
    - _Tests: `tests/test_gate/test_middleware.py`_
  - [ ] 12.3 Call `ApprovalGate.propose_action()` instead of direct tool execution
    - _Dependencies: Task 12_
    - _Tests: `tests/test_gate/test_middleware.py`_
  - [ ] 12.4 Block until approval/rejection/timeout (async wait with timeout)
    - _Dependencies: Task 12_
    - _Tests: `tests/test_gate/test_middleware.py`_
  - [ ] 12.5 On approval, proceed with tool execution
    - _Dependencies: Task 12_
    - _Tests: `tests/test_gate/test_middleware.py`_
  - [ ] 12.6 On rejection, return rejection to Remediator
    - _Dependencies: Task 12_
    - _Tests: `tests/test_gate/test_middleware.py`_
  - [ ] 12.7 On timeout, return timeout to Remediator; for tools without `requires_approval`, pass through directly (no gate)
    - _Dependencies: Task 12_
    - _Tests: `tests/test_gate/test_middleware.py` — interception, passthrough, blocking behavior_

- [ ] 13. Update MEMORY.md integration
  - [ ] 13.1 After completed remediation (COMPLETED/FAILED/ROLLED_BACK), generate memory entry with action, parameters, outcome, verification results
    - File: `profiles/remediator/gate/controller.py` (update)
    - _Dependencies: Task 8_
    - _Tests: Verify MEMORY.md is updated correctly after simulated remediation_
  - [ ] 13.2 Append to `memories/MEMORY.md` in the established format
    - _Dependencies: Task 13_
    - _Tests: Verify MEMORY.md is updated correctly_
  - [ ] 13.3 Include timestamps and request_id for traceability
    - _Dependencies: Task 13_
    - _Tests: Verify MEMORY.md is updated correctly_

## Phase 6: Testing

- [*] 14. Integration test suite
  - [*] 14.1 End-to-end: propose → approve → execute → verify → complete
    - File: `tests/test_gate/test_integration.py`
    - _Dependencies: All previous tasks_
    - _Tests: `tests/test_gate/test_integration.py`_
  - [*] 14.2 End-to-end: propose → reject → stop
    - _Dependencies: Task 14_
    - _Tests: `tests/test_gate/test_integration.py`_
  - [*] 14.3 End-to-end: propose → timeout → escalate → approve → execute → complete
    - _Dependencies: Task 14_
    - _Tests: `tests/test_gate/test_integration.py`_
  - [*] 14.4 End-to-end: propose → approve → execute → fail → rollback → complete
    - _Dependencies: Task 14_
    - _Tests: `tests/test_gate/test_integration.py`_
  - [*] 14.5 End-to-end: propose → timeout → escalate → timeout → ESCALATION_TIMEOUT
    - _Dependencies: Task 14_
    - _Tests: `tests/test_gate/test_integration.py`_
  - [*] 14.6 Queue: propose two actions, first approved then second auto-starts
    - _Dependencies: Task 14_
    - _Tests: `tests/test_gate/test_integration.py`_
  - [*] 14.7 Crash recovery: kill mid-execution, restart, recover state
    - _Dependencies: Task 14_
    - _Tests: `tests/test_gate/test_integration.py`_
  - [*] 14.8 Idempotency: approve same request twice → single execution
    - _Dependencies: Task 14_
    - _Tests: `tests/test_gate/test_integration.py`_
  - [*] 14.9 All four tools through the gate
    - _Dependencies: Task 14_
    - _Tests: `tests/test_gate/test_integration.py`_

- [ ] 15. Add gate configuration validation
  - [ ] 15.1 Define `GateConfig` dataclass with all configuration parameters and defaults
    - File: `profiles/remediator/gate/config.py`
    - _Dependencies: Task 1_
    - _Tests: `tests/test_gate/test_config.py`_
  - [ ] 15.2 Validate required fields: `bot_token`, `chat_id`, `approval_timeout_seconds`
    - _Dependencies: Task 15_
    - _Tests: `tests/test_gate/test_config.py`_
  - [ ] 15.3 Validate ranges: `approval_timeout_seconds > 0`, `queue_depth > 0`, `poll_interval > 0`
    - _Dependencies: Task 15_
    - _Tests: `tests/test_gate/test_config.py`_
  - [ ] 15.4 Validate environment variables exist: `TELEGRAM_BOT_TOKEN_REMEDIATOR`, `TELEGRAM_CHAT_ID_REMEDIATOR`
    - _Dependencies: Task 15_
    - _Tests: `tests/test_gate/test_config.py`_
  - [ ] 15.5 Provide clear error messages for missing or invalid configuration
    - _Dependencies: Task 15_
    - _Tests: `tests/test_gate/test_config.py` — valid configs, missing fields, invalid ranges_

- [ ] 16. Add logging and observability
  - [ ] 16.1 Use Python `logging` module with structured log format
    - Files: All gate modules
    - _Dependencies: All previous tasks_
    - _Tests: `tests/test_gate/test_logging.py`_
  - [ ] 16.2 Log all state transitions at INFO level
    - _Dependencies: Task 16_
    - _Tests: `tests/test_gate/test_logging.py`_
  - [ ] 16.3 Log Telegram API calls at DEBUG level
    - _Dependencies: Task 16_
    - _Tests: `tests/test_gate/test_logging.py`_
  - [ ] 16.4 Log errors and retries at WARNING/ERROR level
    - _Dependencies: Task 16_
    - _Tests: `tests/test_gate/test_logging.py`_
  - [ ] 16.5 Include `request_id` in all log messages for correlation
    - _Dependencies: Task 16_
    - _Tests: `tests/test_gate/test_logging.py`_
  - [ ] 16.6 Add `hermes_gate_requests_total{tool, risk_level, state}` metric counter
    - _Dependencies: Task 16_
    - _Tests: `tests/test_gate/test_logging.py`_
  - [ ] 16.7 Add `hermes_gate_approval_duration_seconds{tool}` and `hermes_gate_execution_duration_seconds{tool}` metrics
    - _Dependencies: Task 16_
    - _Tests: `tests/test_gate/test_logging.py`_

- [ ] 17. Checkpoint - Remediation Gate Complete
  - Ensure all backend tests pass
  - Verify integration test suite passes
  - Validate end-to-end flow with live Telegram bot

## Task Dependency Graph

```
Phase 1: Foundation
  Task 1: Models ──────┬──► Task 2: State Machine ──┐
                        ├──► Task 3: Persistence ─────┤
                        │                              │
Phase 2: Telegram       │                              │
  Task 4: Gateway ──────┤                              │
  Task 5: Callbacks ────┤                              │
                        │                              │
Phase 3: Executor       │                              │
  Task 6: Executor ─────┤                              │
  Task 7: Verifier ─────┤                              │
                        │                              │
Phase 4: Controller     │                              │
  Task 8: Controller ◄──┴──────────────────────────────┘
  Task 9: Recovery ◄─── Task 8
  Task 10: Queue ◄───── Task 8
                        │
Phase 5: Integration
  Task 11: Wire up ◄─── Task 8
  Task 12: Middleware ◄── Task 11
  Task 13: Memory ◄──── Task 8
                        │
Phase 6: Testing
  Task 14: Integration ◄── All
  Task 15: Config ◄──── Task 1
  Task 16: Logging ◄─── All

  Task 17: Checkpoint
```

---

## Estimated Effort

| Phase     | Tasks  | Estimated Complexity                                      |
| --------- | ------ | --------------------------------------------------------- |
| 1         | 3      | Medium — data modeling, state machine logic               |
| 2         | 2      | Medium — Telegram API integration, callback routing       |
| 3         | 2      | Medium — API wrapping, ClickHouse verification queries    |
| 4         | 3      | High — orchestrator is the core logic, recovery and queue |
| 5         | 3      | Medium — wiring, middleware, memory integration           |
| 6         | 3      | Medium — testing, validation, observability               |
| **Total** | **17** |                                                           |
