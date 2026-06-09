# Hermes Remediation Gate — Requirements

## Overview

The Remediation Gate is the human-in-the-loop approval system that governs the
Remediator agent's execution of write operations. It ensures that no
infrastructure-changing action is performed without explicit human approval,
enforced via Telegram notifications, a state-machine approval workflow, and a
timeout-based escalation policy.

The gate covers four remediation tools declared with `requires_approval: true`
in `plugins/telemetryflow/plugin.yaml`:

| Tool               | Action                            | Risk Level |
| ------------------ | --------------------------------- | ---------- |
| `scale_deployment` | Scale K8s deployment replicas     | MEDIUM     |
| `restart_pod`      | Restart K8s pods (deployment/pod) | HIGH       |
| `rollback_deploy`  | Rollback K8s deployment           | LOW        |
| `update_alert`     | Update TFO alert rule             | LOW        |

---

## REQ-1: Human Approval Gate

### REQ-1.1: Approval Workflow

- When the Remediator agent invokes a `requires_approval` tool, the tool
  execution SHALL be suspended before the API call is made.
- The gate SHALL send an approval request to the configured Telegram chat
  containing all required proposal fields (see REQ-1.3).
- The tool execution SHALL NOT proceed until a human explicitly approves.
- The gate SHALL support three human responses: **Approve**, **Reject**, and
  **Manual Review**.

### REQ-1.2: Approval Prerequisites (Three Gates)

Before any approval request is sent, the Remediator SHALL verify:

1. **Gate 1 — Confirmed Root Cause**: The Reviewer agent must have issued a
   `CONFIRMED` verdict. If the verdict is `NEEDS_MORE_EVIDENCE` or `REJECTED`,
   no approval request SHALL be sent.
2. **Gate 2 — Proportional Response**: The proposed remediation must be
   proportional to the confirmed root cause. The Remediator SHALL NOT propose a
   broader action when a narrower one suffices.
3. **Gate 3 — Human Approval**: Explicit human approval via Telegram is
   required regardless of confidence level.

### REQ-1.3: Approval Request Payload

Every approval request SHALL contain:

| Field            | Description                                                        |
| ---------------- | ------------------------------------------------------------------ |
| Alert summary    | What alert fired and why                                           |
| Root cause       | Confirmed hypothesis in one sentence                               |
| Evidence links   | Key metrics, logs, traces proving root cause                       |
| Proposed action  | Exact tool invocation with parameters (command-level specificity)  |
| Blast radius     | Affected services, potential side effects                          |
| Rollback plan    | Specific steps to undo if things worsen                            |
| Reviewer verdict | `CONFIRMED` + any caveats (e.g., "low confidence", "partial data") |
| Risk level       | LOW / MEDIUM / HIGH / CRITICAL                                     |
| Timeout deadline | Unix timestamp when the request expires                            |

### REQ-1.4: Response Handling

- **Approve**: Execute the proposed remediation action immediately.
- **Reject**: Abort the action. Do NOT rephrase or retry. Log the rejection
  reason if provided.
- **Manual Review**: Escalate to the on-call engineer with full context. Do NOT
  execute until a second explicit approval is received.

---

## REQ-2: Remediation Tool Execution

### REQ-2.1: scale_deployment

- **Parameters**: `--name` (required), `--namespace` (default: `default`),
  `--replicas` (default: `1`)
- **API endpoint**: `POST /kubernetes/deployments/scale`
- **Risk level**: MEDIUM — cost impact, may not solve root cause
- **Pre-condition**: Verify target deployment exists and current replica count
  differs from requested.
- **Post-action verification**: Query `kubernetes_metrics_1h` to confirm replica
  count matches target. Check pod readiness.

### REQ-2.2: restart_pod

- **Parameters**: `--deployment` XOR `--pod` (one required),
  `--namespace` (default: `default`)
- **API endpoint**: `POST /kubernetes/deployments/restart` or
  `POST /kubernetes/pods/restart`
- **Risk level**: HIGH — may lose in-flight requests, temporary disruption
- **Pre-condition**: Verify target deployment/pod exists. Warn if incident is a
  security event (evidence destruction risk).
- **Post-action verification**: Query pod status. Check for new errors in
  `otel_logs` within 60 seconds. Verify dependent services are healthy.

### REQ-2.3: rollback_deploy

- **Parameters**: `--name` (required), `--namespace` (default: `default`),
  `--revision` (optional, defaults to previous revision)
- **API endpoint**: `POST /kubernetes/deployments/rollback`
- **Risk level**: LOW — rollback to known-good version (reversible)
- **Pre-condition**: Verify revision history exists. Check that target revision
  has no known CVEs if security context is available.
- **Post-action verification**: Verify deployment rollout status. Check
  `service_error_rates_1h` for regression. Confirm pod health.

### REQ-2.4: update_alert

- **Parameters**: `--rule-id` (required), at least one of `--threshold`,
  `--enabled`, `--severity`
- **API endpoint**: `PATCH /alerts/rules/{rule_id}`
- **Risk level**: LOW — alert configuration change only
- **Pre-condition**: Verify rule ID exists. Log current rule state before
  modification.
- **Post-action verification**: Query rule state to confirm changes applied.
  Verify rule evaluation continues to function.

---

## REQ-3: Telegram Notification Integration

### REQ-3.1: Bot Configuration

- Each agent profile configures a Telegram gateway in its `config.yaml`:
  ```yaml
  gateway:
    type: telegram
    bot_token_env: TELEGRAM_BOT_TOKEN_<AGENT>
    chat_id_env: TELEGRAM_CHAT_ID_<AGENT>
  ```
- The Remediator uses `TELEGRAM_BOT_TOKEN_REMEDIATOR` and
  `TELEGRAM_CHAT_ID_REMEDIATOR`.

### REQ-3.2: Notification Types

The gate SHALL send the following notification types:

| Notification          | Trigger                                | Recipient                |
| --------------------- | -------------------------------------- | ------------------------ |
| Approval request      | Remediation proposed                   | Remediator Telegram chat |
| Approval response     | Human responds (approve/reject)        | Remediator (internal)    |
| Execution result      | Remediation executed                   | Remediator Telegram chat |
| Timeout warning       | 50% of timeout elapsed                 | Remediator Telegram chat |
| Timeout escalation    | 100% of timeout elapsed                | On-call engineer         |
| Post-action summary   | Verification complete                  | Remediator Telegram chat |
| Rollback notification | Remediation failed, rollback initiated | Remediator Telegram chat |

### REQ-3.3: Message Format

- All messages SHALL use Telegram MarkdownV2 or HTML formatting.
- Approval request messages SHALL include inline keyboard buttons:
  `[Approve] [Reject] [Manual Review]`
- Each button callback SHALL include a unique approval request ID for
  correlation.
- Messages SHALL be self-contained — no external links required to make a
  decision.

### REQ-3.4: Message Delivery Guarantees

- If Telegram API returns a recoverable error (rate limit, timeout), the gate
  SHALL retry up to 3 times with exponential backoff (1s, 2s, 4s).
- If all retries fail, the gate SHALL log the failure and treat it as an
  implicit timeout (escalation path).
- Duplicate messages (same approval request ID) SHALL be deduplicated.

---

## REQ-4: Approval State Management

### REQ-4.1: State Machine

Each approval request SHALL follow this state machine:

```
PENDING ──► APPROVED ──► EXECUTING ──► VERIFYING ──► COMPLETED
   │             │            │             │
   │             │            │             └──► FAILED ──► ROLLING_BACK ──► ROLLED_BACK
   │             │            │
   │             └──► REJECTED
   │
   ├──► TIMED_OUT ──► ESCALATED ──► MANUALLY_APPROVED ──► EXECUTING
   │                                    │
   │                                    └──► MANUALLY_REJECTED
   │
   └──► CANCELLED (by Remediator, e.g., new evidence invalidates action)
```

### REQ-4.2: State Transitions

| From         | To                | Trigger                                   |
| ------------ | ----------------- | ----------------------------------------- |
| PENDING      | APPROVED          | Human clicks "Approve"                    |
| PENDING      | REJECTED          | Human clicks "Reject"                     |
| PENDING      | TIMED_OUT         | `approval_timeout_seconds` (600s) elapsed |
| PENDING      | CANCELLED         | Remediator cancels (new evidence)         |
| TIMED_OUT    | ESCALATED         | Auto-escalation triggers                  |
| ESCALATED    | MANUALLY_APPROVED | On-call engineer approves                 |
| ESCALATED    | MANUALLY_REJECTED | On-call engineer rejects                  |
| APPROVED     | EXECUTING         | Tool execution begins                     |
| EXECUTING    | VERIFYING         | API call returns success                  |
| EXECUTING    | FAILED            | API call returns error                    |
| VERIFYING    | COMPLETED         | Post-action checks pass                   |
| VERIFYING    | FAILED            | Post-action checks detect issues          |
| FAILED       | ROLLING_BACK      | Automatic rollback initiated              |
| ROLLING_BACK | ROLLED_BACK       | Rollback action completed                 |

### REQ-4.3: Persistence

- Approval state SHALL be persisted to disk (SQLite or JSON file in
  `sessions/` directory).
- State SHALL survive agent restarts.
- Each approval request SHALL have a unique ID (UUID v4).
- State records SHALL include: request ID, tool name, parameters, proposed
  action, risk level, reviewer verdict, timestamps for each state transition,
  human approver identity (Telegram user ID), and outcome.

### REQ-4.4: Concurrent Request Handling

- Only ONE approval request SHALL be active at a time per Remediator instance.
- If a new remediation is proposed while one is PENDING, the Remediator SHALL
  queue the new proposal (max queue depth: 5).
- If the queue is full, the Remediator SHALL escalate to human rather than
  drop the request.

---

## REQ-5: Timeout and Escalation Handling

### REQ-5.1: Timeout Configuration

- Default timeout: 600 seconds (10 minutes), configured via
  `approval_timeout_seconds` in `profiles/remediator/config.yaml`.
- A warning notification SHALL be sent at 50% of timeout (300 seconds).
- At 100% of timeout, the request SHALL transition to `TIMED_OUT`.

### REQ-5.2: Auto-Escalation

- When `auto_escalate_on_timeout: true` is configured, the gate SHALL
  automatically escalate timed-out requests.
- Escalation SHALL send a high-priority notification to the on-call engineer
  with full context plus the timeout history.
- The escalated request SHALL have an additional 600-second window.
- If the escalated request also times out, the remediation SHALL be abandoned
  and logged as `ESCALATION_TIMEOUT`.

### REQ-5.3: Escalation Chain

1. **Primary**: Remediator Telegram chat (`TELEGRAM_CHAT_ID_REMEDIATOR`)
2. **Secondary**: On-call engineer (configurable escalation target)
3. **Terminal**: Log as `ESCALATION_TIMEOUT`, notify all 4 agent Telegram chats

### REQ-5.4: Non-Auto-Execute Guarantee

- Under NO circumstances SHALL the gate auto-execute a timed-out remediation.
- Timeout ALWAYS means "stop and wait for human" — never "proceed anyway."
- This is non-negotiable, zero exceptions, even for `LOW` risk actions.

---

## REQ-6: Remediation Safety Constraints

### REQ-6.1: One Action at a Time

- The Remediator SHALL NOT execute more than one write action simultaneously.
- Sequential execution only: propose → approve → execute → verify → next.

### REQ-6.2: Maximum Turns

- Maximum 15 turns per remediation cycle (configured via `agent.max_turns`).
- If the remediation requires more than 15 turns, the Remediator SHALL escalate
  to human with a detailed action plan.

### REQ-6.3: Mandatory Rollback Plan

- Every proposed action SHALL include a specific rollback plan.
- If the action fails or verification detects new issues, the rollback SHALL be
  executed automatically before proposing new actions.

### REQ-6.4: Post-Action Verification

- After ANY approved action, verification is MANDATORY:
  1. Wait 30 seconds for propagation.
  2. Query metrics — compare to pre-incident baseline.
  3. Search logs — check for new errors.
  4. Check pod/service health.
  5. Verify no cascading side effects on dependent services.

### REQ-6.5: Security Considerations

- For security incidents (`SECURITY_ESCALATION` verdict), the gate SHALL:
  - Prefer containment actions over destructive actions.
  - Warn if an action may destroy forensic evidence.
  - Require explicit `Manual Review` path (one-click approve not sufficient).
- Post-action security verification SHALL include: audit log check, RBAC
  verification, secrets mount verification, network policy verification.

### REQ-6.6: Risk Assessment Override

- If risk is assessed as `CRITICAL`, the gate SHALL:
  - Automatically route to `Manual Review` path (one-click approve disabled).
  - Recommend the human perform hands-on review.
  - Include explicit warning in the approval request message.

---

## REQ-7: Multi-Agent Coordination for Remediation

### REQ-7.1: Agent Pipeline

The remediation gate operates at the end of the Hermes agent pipeline:

```
Triage → Investigator → Reviewer → Remediator
  (filter)   (hypothesize)   (confirm)   (act — gated)
```

- **Triage**: Filters and prioritizes alerts. Never interacts with Remediator.
- **Investigator**: Generates hypotheses. Never interacts with Remediator.
- **Reviewer**: Peer-reviews hypotheses, issues `CONFIRMED`/`NEEDS_MORE_EVIDENCE`/`REJECTED` verdicts. Direct upstream of Remediator.
- **Remediator**: Only acts on `CONFIRMED` verdicts, proposes remediation through the approval gate.

### REQ-7.2: Reviewer Verdict Dependencies

| Verdict             | Remediator Action                                               |
| ------------------- | --------------------------------------------------------------- |
| CONFIRMED           | Proceed to Gate 2 (proportional response check), then Gate 3    |
| NEEDS_MORE_EVIDENCE | Stop. Do not propose remediation. Investigation must continue.  |
| REJECTED            | Stop. Do not propose remediation.                               |
| SECURITY_ESCALATION | Proceed with containment-first approach. Require Manual Review. |

### REQ-7.3: Cross-Agent Telegram Isolation

- Each agent has its own Telegram bot token and chat ID.
- The Remediator SHALL NOT send messages to Triage, Investigator, or Reviewer
  Telegram chats directly.
- Escalation notifications to on-call MAY use a shared channel, but this is a
  separate configuration from agent-specific chats.

### REQ-7.4: Memory Coordination

- After completed remediation (success or failure), the Remediator SHALL update
  `MEMORY.md` with:
  - Action taken and parameters.
  - Outcome (COMPLETED / FAILED / ROLLED_BACK).
  - Post-action verification results.
  - Any caveats or follow-up actions needed.
- This memory is available to all agents in future incident cycles.

---

## Non-Functional Requirements

### NFR-1: Reliability

- Approval state SHALL survive process crashes (persisted to disk).
- Telegram notification failures SHALL NOT silently drop approval requests.
- The gate SHALL be idempotent — duplicate approval responses for the same
  request SHALL NOT cause duplicate executions.

### NFR-2: Latency

- Approval request SHALL be sent to Telegram within 2 seconds of proposal.
- State transitions SHALL complete within 500ms.
- Post-action verification SHALL complete within 120 seconds.

### NFR-3: Audit Trail

- Every state transition SHALL be logged with timestamp, actor, and reason.
- Approval decisions SHALL record the Telegram user ID of the approver.
- The complete approval lifecycle SHALL be queryable for post-incident review.

### NFR-4: Configuration

All gate behavior SHALL be configurable via `profiles/remediator/config.yaml`:

| Parameter                  | Default | Description                               |
| -------------------------- | ------- | ----------------------------------------- |
| `require_approval`         | `true`  | Enable/disable the approval gate          |
| `approval_timeout_seconds` | `600`   | Seconds before auto-escalation            |
| `auto_escalate_on_timeout` | `true`  | Auto-escalate on timeout                  |
| `gateway.type`             | —       | Notification backend (`telegram`)         |
| `gateway.bot_token_env`    | —       | Env var name for Telegram bot token       |
| `gateway.chat_id_env`      | —       | Env var name for Telegram chat ID         |
| `agent.max_turns`          | `15`    | Maximum remediation turns before escalate |

---

## Out of Scope

- Integration with Slack, PagerDuty, or other notification platforms (Telegram only).
- Automated remediation without human approval (explicitly prohibited by design).
- Multi-cluster remediation coordination.
- Remediation policy engine (e.g., OPA-based approval rules).
- Mobile push notifications beyond Telegram.
