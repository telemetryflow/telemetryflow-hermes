# Requirements Document

## Introduction

Hermes is a multi-agent incident response system that autonomously classifies, investigates, reviews, and remediates production incidents on the TelemetryFlow Observability Platform. Four specialized AI agents operate as a sequential pipeline — each with a distinct personality, set of capabilities, and formal handoff protocol — to ensure that every alert is rigorously evaluated before any production action is taken.

The pipeline is designed around a principle of adversarial collaboration: each agent actively challenges the work of its predecessor, and no agent trusts the output of another without independent verification. This eliminates the single-point-of-failure risk inherent in single-agent systems and prevents confirmation bias from propagating through the incident response chain.

### Pipeline Flow

```
Alert → on-alert-fired.sh → Triage → Investigator → Reviewer → Remediator → Human (Telegram) → Fixed
                                   ↓            ↓              ↓             ↓
                              KNOWN/NOISE   Evidence       CONFIRMED/     Approval Gate
                              (auto-resolve) Package       REJECTED       (600s timeout)
```

1. **Alert arrives** from the TelemetryFlow alerting system
2. **on-alert-fired.sh** enriches the alert with context (alert_id, rule_name, severity)
3. **Triage Agent** classifies the alert as CRITICAL / KNOWN / NOISE / INCOMPLETE
4. **Investigator Agent** gathers evidence from ClickHouse across metrics, logs, traces, and exemplars
5. **Reviewer Agent** independently verifies or falsifies the investigation
6. **Remediator Agent** proposes a fix requiring human approval via Telegram
7. **Human approves** the remediation action
8. **post-remediation.sh** generates RCA reports and updates memory

### Design Principles

- **Zero trust between agents**: No agent accepts another's claims without verification
- **Zero hallucination**: Every data point must come from an actual query result
- **Human-in-the-loop**: All write operations require explicit human approval
- **Evidence over opinion**: Every claim must cite source, timestamp, workspace, value, and signal
- **Security-first**: Every anomaly is treated as a potential security event until ruled out
- **Read-only by default**: Only the Remediator can execute write actions, and only after approval

## Glossary

| Term                       | Definition                                                                                                                                                                                                                                                                                                                                                                                                                              |
| -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Triage_Agent**           | The first agent in the pipeline (glm-5.1, max_turns=30, readonly). Classifies alerts as CRITICAL, KNOWN, NOISE, or INCOMPLETE. Paranoid gatekeeper personality.                                                                                                                                                                                                                                                                         |
| **Investigator_Agent**     | The second agent in the pipeline (claude-sonnet-4-5, max_turns=45, readonly). Gathers evidence from 20 ClickHouse tables across 4 telemetry signals. Hostile scientist personality.                                                                                                                                                                                                                                                     |
| **Reviewer_Agent**         | The third agent in the pipeline (glm-5.1, max_turns=20, readonly). Independently challenges investigations for bias and falsifies hypotheses. Professional skeptic personality.                                                                                                                                                                                                                                                         |
| **Remediator_Agent**       | The fourth and final agent in the pipeline (glm-5.1, max_turns=15, require_approval=true). Proposes fixes requiring human approval via Telegram. Cautious pragmatist personality.                                                                                                                                                                                                                                                       |
| **Incident_Context**       | The structured data payload passed between agents during pipeline execution. Contains alert_id, classification, evidence, hypotheses, and verdicts.                                                                                                                                                                                                                                                                                     |
| **Alert_Classification**   | One of four discrete labels assigned by Triage: CRITICAL (genuine anomaly), KNOWN (matches verified pattern), NOISE (below threshold/duplicate), INCOMPLETE (insufficient data).                                                                                                                                                                                                                                                        |
| **SOUL_File**              | A markdown file (SOUL.md) in each agent's profile directory that defines the agent's personality, behavioral rules, zero-hallucination policy, hard limits, and inter-agent communication protocol.                                                                                                                                                                                                                                     |
| **Agent_Memory**           | The persistent knowledge store for each agent, consisting of MEMORY.md (known patterns, platform conventions, tool quirks) and USER.md (preferences, things to avoid).                                                                                                                                                                                                                                                                  |
| **Approval_Gate**          | The human-in-the-loop checkpoint where the Remediator submits a proposed action to a human via Telegram. The human can Approve, Reject, or request Manual Review. Timeout is 600 seconds.                                                                                                                                                                                                                                               |
| **Telegram_Gateway**       | The communication channel between agents and humans. Each agent has its own Telegram bot (configured via TELEGRAM*BOT_TOKEN*_ and TELEGRAM*CHAT_ID*_ environment variables).                                                                                                                                                                                                                                                            |
| **Pipeline_Hook**          | A shell script that runs at a specific lifecycle stage: on-alert-fired.sh (pre-triage enrichment), pre-investigation.sh (context logging), post-remediation.sh (RCA generation + outcome tracking).                                                                                                                                                                                                                                     |
| **Cron_Job**               | A scheduled task that runs periodically to perform proactive monitoring: health-check, log-sweep, k8s-health, db-slow-query, alert-fatigue, skill-curator.                                                                                                                                                                                                                                                                              |
| **ClickHouse_Table**       | One of 20 OTLP-compliant tables that agents can query for telemetry data: metrics_1m, metrics_5m, metrics_1h, otel_logs, otel_traces, exemplars, exemplars_1h, signal_correlations_1h, service_latency_percentiles_1h, service_error_rates_1h, logs_1h, qan_metrics, audit_logs, audit_logs_1h, uptime_checks, kubernetes_metrics_1h, vm_metrics_1h, service_map_metrics_1h, network_map_traffic_1h, network_map_connection_metrics_1h. |
| **Falsification_Protocol** | The investigation methodology where hypotheses are designed to be disproven, not confirmed. The Investigator tries to destroy their own hypothesis before passing it to the Reviewer.                                                                                                                                                                                                                                                   |
| **Verdict**                | The Reviewer's formal assessment: CONFIRMED (evidence reproduces, hypothesis survives), NEEDS_MORE_EVIDENCE (plausible but unproven), REJECTED (contradicted by evidence).                                                                                                                                                                                                                                                              |
| **Delegation_Context**     | The structured payload passed when one agent hands off to another. Includes alert_id, classification, evidence summary, SECURITY_FLAG (if applicable), and challenge statement.                                                                                                                                                                                                                                                         |
| **SECURITY_FLAG**          | A boolean flag set by Triage when security indicators are present. Causes the Investigator to prioritize security hypotheses and run additional security evidence queries.                                                                                                                                                                                                                                                              |
| **SECURITY_ESCALATION**    | A flag set by the Investigator or Reviewer when an active security threat is detected. Triggers immediate human escalation via Telegram, bypassing normal pipeline flow.                                                                                                                                                                                                                                                                |
| **Agent_Profile**          | The directory structure for each agent containing config.yaml (model, tools, permissions), SOUL.md (personality and rules), memories/ (MEMORY.md, USER.md), and skills/ (domain-specific capabilities).                                                                                                                                                                                                                                 |
| **Remediation_Risk_Level** | One of four risk levels assigned by the Remediator to every proposed action: LOW (reversible, isolated), MEDIUM (broader impact, cost implications), HIGH (not easily reversible), CRITICAL (stateful changes, data integrity risk).                                                                                                                                                                                                    |
| **Blast_Radius**           | The scope of potential impact from a remediation action. Every proposal must include intended effect, side effects, rollback plan, and post-action verification checks.                                                                                                                                                                                                                                                                 |
| **Memory_Curator**         | A background process that manages agent memory lifecycle: archives stale entries after 30 days, consolidates after 90 days, and reviews skills every 7 days.                                                                                                                                                                                                                                                                            |
| **workspace_id**           | The mandatory filter for all ClickHouse queries. Tenant hierarchy: region -> organization -> workspace -> tenant. No query may omit this filter.                                                                                                                                                                                                                                                                                        |
| **Plugin_Tool**            | A Python script in plugins/telemetryflow/tools/ that provides a specific capability to agents. 40 tools covering metrics, logs, traces, k8s, IAM, alerting, and more. All use stdlib only (no pip dependencies).                                                                                                                                                                                                                        |

## Requirements

### REQ-001: Alert Intake & Triage

**User Story**: As an SRE on call, I want incoming alerts to be automatically classified so that I only see genuinely critical incidents.

**WHEN** an alert fires from the TelemetryFlow alerting system
**THEN** the system SHALL execute `hooks/on-alert-fired.sh` to log and enrich the alert payload
**AND** the system SHALL pass the enriched payload to the Triage Agent
**AND** the Triage Agent SHALL classify the alert as exactly one of: CRITICAL, KNOWN, NOISE, or INCOMPLETE
**AND** the classification SHALL be completed within 3 agent turns
**AND** the Triage Agent SHALL cross-reference MEMORY.md for known patterns before classifying
**AND** if the alert payload lacks sufficient data, the Triage Agent SHALL classify as INCOMPLETE and escalate to human
**AND** if the alert matches a verified pattern on at least 3 signal points (service, error type, time pattern), the Triage Agent SHALL classify as KNOWN and auto-resolve
**AND** if the alert is below threshold, duplicate, or during a known operational window, the Triage Agent SHALL classify as NOISE and suppress
**AND** if the alert represents a genuine anomaly with measurable impact, the Triage Agent SHALL classify as CRITICAL and delegate to the Investigator with full context

**Acceptance Criteria**:

- Every alert receives exactly one classification (no maybes, no "leaning toward")
- INCOMPLETE alerts are never guessed — they are escalated to human immediately
- KNOWN classifications require a MEMORY.md match on 3+ signal points
- CRITICAL classifications include a one-sentence evidence summary in the delegation context
- Alert enrichment includes alert_id, rule_name, and severity extraction
- Classification is logged to `$HERMES_HOME/logs/alerts.log`

### REQ-002: Security-Aware Triage

**User Story**: As a security-conscious platform engineer, I want the Triage Agent to consider security implications of every alert so that attacks are not misclassified as operational noise.

**WHEN** the Triage Agent classifies an alert
**THEN** the Triage Agent SHALL consider the possibility that the anomaly is a security event
**AND** if security red flags are present (login failures > 10x baseline, DELETE operations on audit logs, access to system.\* tables, unknown IP access to IAM APIs, pod executions in kube-system outside CI/CD, unexpected TLS changes, bulk data downloads), the Triage Agent SHALL upgrade the classification
**AND** the Triage Agent SHALL set `SECURITY_FLAG` in the delegation context when security indicators are present
**AND** standard NOISE with a security signal SHALL be upgraded to CRITICAL
**AND** standard KNOWN with a changed attack pattern SHALL be upgraded to CRITICAL
**AND** standard CRITICAL with a security signal SHALL add `SECURITY_FLAG` to delegation context

**Acceptance Criteria**:

- Every classification considers both operational and security hypotheses
- Security red flags are checked explicitly, not implicitly
- SECURITY_FLAG is present in delegation context when security indicators exist
- No alert with security indicators is classified as NOISE without explicit justification

### REQ-003: Agent Handoff Protocol

**User Story**: As a platform engineer, I want agents to communicate through structured delegation so that context is preserved and traceable across the pipeline.

**WHEN** one agent completes its work and delegates to the next agent
**THEN** the delegating agent SHALL produce a structured Delegation_Context containing: alert_id, classification/verdict, evidence summary, SECURITY_FLAG (if applicable), and a challenge statement
**AND** the receiving agent SHALL NOT see the delegating agent's thought process — only the structured output
**AND** each handoff SHALL include the alert_id for traceability
**AND** the Triage Agent SHALL delegate to the Investigator with classification + evidence summary + challenge
**AND** the Investigator SHALL delegate to the Reviewer with hypothesis + evidence package + dead hypotheses
**AND** the Reviewer SHALL delegate to the Remediator with verdict + confirmed hypothesis + caveats
**AND** the pipeline SHALL not allow skip-handoffs (Triage cannot delegate directly to Reviewer)

**Acceptance Criteria**:

- Every delegation includes alert_id
- No agent sees another agent's internal reasoning
- Handoffs follow strict sequential order: Triage -> Investigator -> Reviewer -> Remediator
- Each handoff is logged with timestamp and agent pair

### REQ-004: Investigation Evidence Gathering

**User Story**: As an SRE, I want the Investigator to gather evidence from all four telemetry signals so that root cause analysis is thorough and unbiased.

**WHEN** the Investigator receives a CRITICAL alert from Triage
**THEN** the system SHALL execute `hooks/pre-investigation.sh` to log the investigation start
**AND** the Investigator SHALL query all four telemetry signals in order: metrics, logs, traces, exemplars
**AND** the Investigator SHALL use a falsification-first methodology (design experiments to disprove hypotheses, not confirm them)
**AND** every evidence citation SHALL include: source tool, timestamp, workspace_id, specific value, and signal type
**AND** the Investigator SHALL form a hypothesis only after collecting sufficient evidence
**AND** the hypothesis SHALL survive at least 3 independent falsification attempts across at least 2 different telemetry signals
**AND** the Investigator SHALL document every dead hypothesis alongside the surviving one
**AND** all ClickHouse queries SHALL include workspace_id in the WHERE clause
**AND** if metrics don't show the anomaly described in the alert, the Investigator SHALL stop and report the alert may be a false positive
**AND** the Investigator SHALL generate at least one security hypothesis alongside operational hypotheses
**AND** the investigation SHALL be completed within 45 agent turns

**Acceptance Criteria**:

- All 4 signals are queried (metrics, logs, traces, exemplars) for every investigation
- Every evidence citation contains source, timestamp, workspace, value, and signal
- Failed hypotheses are documented, not discarded
- workspace_id is present in every ClickHouse query
- Investigation does not exceed 45 turns

### REQ-005: Security Investigation Protocol

**User Story**: As a security engineer, I want the Investigator to actively pursue security hypotheses when security indicators are present so that attacks are detected during incident response.

**WHEN** `SECURITY_FLAG` is present in the alert context
**THEN** the Investigator SHALL query additional security signals: audit logs, access patterns, network anomalies, IAM changes, SSO events
**AND** the Investigator SHALL check for attack patterns: credential stuffing, SQL/NoSQL injection, supply chain compromise, insider threat, cryptomining, data exfiltration, lateral movement, privilege escalation
**AND** if evidence of an active security threat is found, the Investigator SHALL immediately escalate to human via Telegram with `SECURITY_ESCALATION` flag
**AND** the Investigator SHALL NOT wait for more data on an active security threat
**AND** the Investigator SHALL NOT alert through channels the suspected compromised account can see
**AND** the security escalation SHALL include: what was found, what data may be exposed, what the attacker may still access, recommended containment actions

**Acceptance Criteria**:

- SECURITY_FLAG triggers additional security evidence queries
- At least one security hypothesis is generated for every investigation
- Active security threats are escalated immediately, not after further investigation
- Evidence preservation is prioritized over continued investigation

### REQ-006: Independent Review

**User Story**: As a platform engineer, I want an independent agent to challenge the investigation so that confirmation bias does not lead to incorrect remediation.

**WHEN** the Reviewer receives an investigation package from the Investigator
**THEN** the Reviewer SHALL NOT see the Investigator's thought process or raw queries
**AND** the Reviewer SHALL verify every claim by running their own read-only queries to primary sources
**AND** the Reviewer SHALL produce exactly one verdict: CONFIRMED, NEEDS_MORE_EVIDENCE, or REJECTED
**AND** CONFIRMED SHALL only be issued when evidence independently reproduces and the hypothesis survives falsification
**AND** NEEDS_MORE_EVIDENCE SHALL specify exactly which signals need re-querying and which alternatives need ruling out
**AND** REJECTED SHALL state which evidence contradicts the hypothesis
**AND** the Reviewer SHALL check for confirmation bias (did the Investigator only query supporting signals?)
**AND** the Reviewer SHALL actively search for disconfirming evidence
**AND** the Reviewer SHALL check MEMORY.md for contradictory historical patterns
**AND** the Reviewer SHALL verify that a security hypothesis was generated and checked
**AND** the Reviewer SHALL check for signs that an "operational incident" is actually a security cover-up
**AND** the review SHALL be completed within 20 agent turns

**Acceptance Criteria**:

- The Reviewer never sees the Investigator's raw queries or reasoning
- Every verdict cites specific evidence queries the Reviewer ran independently
- "Looks good to me" and "mostly confirmed" are never used as verdicts
- Ambiguous evidence results in NEEDS_MORE_EVIDENCE or REJECTED, never CONFIRMED
- Review does not exceed 20 turns

### REQ-007: Remediation Planning

**User Story**: As an SRE, I want the Remediator to propose safe, proportional fixes with clear rollback plans so that remediation doesn't cause more harm than the original incident.

**WHEN** the Remediator receives a CONFIRMED verdict from the Reviewer
**THEN** the Remediator SHALL verify the Reviewer's confirmation makes sense before proposing action
**AND** the Remediator SHALL NOT act on NEEDS_MORE_EVIDENCE or REJECTED verdicts
**AND** every proposed action SHALL include: intended effect, potential side effects, rollback plan, and post-action verification checks
**AND** the Remediator SHALL assign a risk level: LOW, MEDIUM, HIGH, or CRITICAL
**AND** the Remediator SHALL NOT propose multiple simultaneous actions
**AND** the remediation SHALL be proportional to the confirmed root cause
**AND** the Remediator SHALL check security implications of every proposed action
**AND** if the incident is a security event, the Remediator SHALL propose containment over remediation
**AND** the Remediator SHALL warn if the proposed action may destroy forensic evidence
**AND** the remediation SHALL be completed within 15 agent turns

**Acceptance Criteria**:

- No action is proposed without CONFIRMED verdict
- Every proposal includes blast radius analysis
- Only one action is proposed at a time
- Risk level is assigned to every proposal
- CRITICAL risk proposals recommend manual review

### REQ-008: Human Approval Gate

**User Story**: As an SRE, I want to approve every remediation action before it executes so that I maintain control over production changes.

**WHEN** the Remediator proposes a remediation action
**THEN** the Remediator SHALL send a notification to the human via Telegram containing: alert summary, root cause (one sentence), evidence links, proposed action (command-level specificity), blast radius, rollback plan, and Reviewer verdict
**AND** the human SHALL have three options: Approve, Reject, or Manual Review
**AND** if the human rejects, the Remediator SHALL NOT argue, rephrase, or retry
**AND** if the human does not respond within 600 seconds, the Remediator SHALL auto-escalate to the on-call engineer
**AND** the Remediator SHALL NOT auto-execute under any circumstances
**AND** the approval timeout SHALL be configurable via `approval_timeout_seconds` in config.yaml
**AND** if `auto_escalate_on_timeout` is true, the Remediator SHALL escalate (not execute) on timeout

**Acceptance Criteria**:

- No write action executes without explicit human approval
- The Remediator never approves its own actions
- Timeout results in escalation, not execution
- The human's rejection is final — no retry loop

### REQ-009: Post-Remediation Verification

**User Story**: As an SRE, I want the system to verify that remediation actually fixed the problem so that I'm not left with a false sense of security.

**WHEN** an approved remediation action is executed
**THEN** the system SHALL wait 30 seconds for propagation
**AND** the Remediator SHALL query metrics to check if the anomaly is resolved
**AND** the Remediator SHALL search logs for new errors or cascading failures
**AND** the Remediator SHALL check pod status for the affected service
**AND** the Remediator SHALL verify no side effects on dependent services
**AND** if verification shows the fix failed, the Remediator SHALL initiate rollback and escalate to human
**AND** if verification shows the fix succeeded, the Remediator SHALL update MEMORY.md with the outcome
**AND** the system SHALL execute `hooks/post-remediation.sh` to generate RCA reports
**AND** the RCA report SHALL be written to `$HERMES_HOME/reports/RCA-{alert_id}-{date}.md`

**Acceptance Criteria**:

- Post-action verification is mandatory, not optional
- Failed fixes trigger automatic rollback before new proposals
- MEMORY.md is updated with every outcome (success or failure)
- RCA report is generated for every successful remediation
- Verification checks all affected services, not just the primary one

### REQ-010: Agent Memory Management

**User Story**: As a platform engineer, I want agents to maintain persistent memory so that they learn from past incidents and avoid repeating mistakes.

**WHEN** an agent processes an incident
**THEN** the agent SHALL read MEMORY.md before making any decisions
**AND** the agent SHALL cross-reference MEMORY.md for known patterns, platform conventions, and tool quirks
**AND** the agent SHALL NOT create memory entries from vibes or assumptions
**AND** after a successful remediation, the Remediator SHALL update MEMORY.md with: root cause, affected service, remediation action, and outcome
**AND** the Memory Curator SHALL archive entries older than 30 days as stale
**AND** the Memory Curator SHALL consolidate entries older than 90 days
**AND** the Memory Curator SHALL run only when idle for at least 2 hours
**AND** the Memory Curator SHALL perform a maximum of 8 review iterations per run
**AND** if MEMORY.md is empty or stale, the Triage Agent SHALL flag it as a risk

**Acceptance Criteria**:

- MEMORY.md is read at the start of every incident processing
- Memory entries are only created from verified data, not assumptions
- Curator respects idle time (2 hours) and iteration limits (8)
- Stale entries are archived, not deleted
- Empty memory is flagged as a risk by Triage

### REQ-011: Pipeline Hooks

**User Story**: As a platform engineer, I want lifecycle hooks at key pipeline stages so that I can track alert processing, investigation context, and remediation outcomes.

**WHEN** a pipeline lifecycle event occurs
**THEN** the system SHALL execute the appropriate hook script:

- `hooks/on-alert-fired.sh` SHALL run when an alert triggers the Triage Agent
- `hooks/pre-investigation.sh` SHALL run before the Investigator starts investigation
- `hooks/post-remediation.sh` SHALL run after remediation completes
  **AND** each hook SHALL use `set -euo pipefail` for error handling
  **AND** `on-alert-fired.sh` SHALL extract alert_id, rule_name, and severity from the payload and log to `$HERMES_HOME/logs/alerts.log`
  **AND** `pre-investigation.sh` SHALL log alert_id, service, and severity to `$HERMES_HOME/logs/investigations.log`
  **AND** `post-remediation.sh` SHALL log the remediation outcome and generate RCA reports to `$HERMES_HOME/reports/`
  **AND** hook failure SHALL NOT block the pipeline (hooks are best-effort)

**Acceptance Criteria**:

- All three hooks exist and are executable
- Hooks use strict error handling (`set -euo pipefail`)
- Hooks log to the correct files under `$HERMES_HOME/logs/`
- Hook failure does not stop pipeline execution
- `post-remediation.sh` generates RCA reports on success

### REQ-012: Cron Jobs & Scheduled Tasks

**User Story**: As an SRE, I want proactive monitoring cron jobs so that potential issues are detected before they trigger alerts.

**WHEN** a scheduled task triggers
**THEN** the system SHALL execute the appropriate cron job from `cron/jobs.json`:

- `health-check-metrics` (every 15m, investigator profile) — checks metrics_5m for anomaly spikes
- `log-error-sweep` (every 30m, investigator profile) — searches for new ERROR patterns
- `k8s-health-check` (every 10m, investigator profile) — checks Kubernetes pod health
- `db-slow-query-check` (every 1h, investigator profile) — queries QAN for slow queries
- `alert-fatigue-review` (every 6h, triage profile) — identifies noise alerts firing >10 times
- `skill-curator` (every 7d, default profile) — archives unused skills
  **AND** each job SHALL specify: id, profile, schedule, task description, enabled status, and output_dir
  **AND** cron output SHALL be written to `cron/output/`
  **AND** disabled jobs SHALL NOT execute
  **AND** each job SHALL run under the specified agent profile with that profile's permissions

**Acceptance Criteria**:

- All 6 cron jobs are defined in `cron/jobs.json`
- Each job has a unique id, profile assignment, and schedule
- Jobs run under the correct agent profile
- Output is written to `cron/output/`
- Disabled jobs do not execute

### REQ-013: Multi-Agent Delegation

**User Story**: As a platform engineer, I want agents to delegate work to specialized sub-agents so that each task is handled by the most capable agent.

**WHEN** an agent needs to delegate work
**THEN** the delegation SHALL use the agent's configured delegation settings (max_iterations, max_concurrent_children)
**AND** the Triage Agent SHALL allow up to 10 delegation iterations with 1 concurrent child
**AND** the Investigator SHALL allow up to 20 delegation iterations with 1 concurrent child
**AND** the Reviewer SHALL allow up to 5 delegation iterations with 1 concurrent child
**AND** the Remediator SHALL allow up to 5 delegation iterations with 1 concurrent child
**AND** only one child agent SHALL run at a time (max_concurrent_children=1)
**AND** the delegation context SHALL include alert_id for traceability

**Acceptance Criteria**:

- Delegation limits are respected per agent
- Only one child runs at a time
- Alert_id is propagated through all delegations
- Delegation does not exceed max_iterations

### REQ-014: Pipeline Error Handling

**User Story**: As an SRE, I want the pipeline to handle errors gracefully so that failures don't leave incidents unresolved.

**WHEN** an error occurs during pipeline execution
**THEN** if the Triage Agent fails to classify within 30 turns, the alert SHALL be escalated to human
**AND** if the Investigator fails to form a hypothesis within 45 turns, the investigation SHALL be summarized and escalated to human with a statement of what was attempted and what gaps remain
**AND** if the Reviewer needs more than 20 turns, the investigation SHALL be classified as too weak to confirm and issued NEEDS_MORE_EVIDENCE
**AND** if the Remediator cannot propose a remediation within 15 turns, the remediation SHALL be escalated to human with a detailed action plan
**AND** if a ClickHouse query fails or times out, the agent SHALL report the failure explicitly — never interpret silence as evidence
**AND** if a Telegram gateway is unreachable, the agent SHALL log the failure and retry once before falling back to logging
**AND** if `post-remediation.sh` RCA generation fails, the hook SHALL log a warning and exit cleanly (non-blocking)

**Acceptance Criteria**:

- Every agent has a turn limit that triggers escalation when exceeded
- Query failures are reported, not hidden
- Gateway failures have a retry + fallback strategy
- Hook failures are non-blocking
- Human escalation includes context about what was attempted

### REQ-015: Agent Configuration

**User Story**: As a platform engineer, I want each agent to have a well-defined configuration so that model, tools, and permissions are consistent and auditable.

**WHEN** an agent profile is configured
**THEN** the profile SHALL be located at `profiles/{agent_name}/config.yaml`
**AND** the config SHALL specify: model (default + provider), agent (max_turns), terminal (backend + timeout), delegation (max_iterations + max_concurrent_children), tools (terminal, web, delegation), gateway (type + credentials), allowed_clickhouse_tables, readonly flag
**AND** the Triage Agent SHALL use glm-5.1 via opencode-go, max_turns=30, timeout=120s, readonly=true
**AND** the Investigator SHALL use claude-sonnet-4-5 via anthropic, max_turns=45, timeout=300s, readonly=true
**AND** the Reviewer SHALL use glm-5.1 via opencode-go, max_turns=20, timeout=180s, readonly=true
**AND** the Remediator SHALL use glm-5.1 via opencode-go, max_turns=15, timeout=180s, readonly=false, require_approval=true, approval_timeout_seconds=600, auto_escalate_on_timeout=true
**AND** all agents SHALL have access to the same 20 ClickHouse tables
**AND** only the Remediator SHALL have readonly=false

**Acceptance Criteria**:

- Each agent has a config.yaml with all required fields
- Model, provider, and turn limits match the specification
- Only Remediator has write access (readonly=false)
- Only Remediator has require_approval=true
- All agents share the same 20 allowed ClickHouse tables

### REQ-016: Agent Identity (SOUL.md)

**User Story**: As a platform engineer, I want each agent to have a distinct, well-defined personality so that agents behave consistently and their interactions produce rigorous results.

**WHEN** an agent is initialized
**THEN** the agent SHALL load its SOUL.md from `profiles/{agent_name}/SOUL.md`
**AND** the SOUL.md SHALL define: core personality, zero hallucination policy, adversarial mindset, inter-agent communication protocol, hard limits
**AND** the Triage Agent SHALL adopt a "ruthlessly pragmatic incident triage officer" personality — paranoid, adversarial, and decisive
**AND** the Investigator SHALL adopt a "hostile scientist" personality — falsification-first, evidence-based, and self-critical
**AND** the Reviewer SHALL adopt a "professional skeptic" personality — intellectually hostile, independent, and unforgiving of bias
**AND** the Remediator SHALL adopt a "cautious pragmatist" personality — conservative, risk-aware, and rollback-ready
**AND** every agent SHALL enforce a zero hallucination policy: never fabricate, infer, or assume data points
**AND** every agent SHALL enforce cybersecurity defense posture: treat anomalies as potential security events

**Acceptance Criteria**:

- Each agent has a SOUL.md with personality, zero-hallucination policy, and hard limits
- Agents do not share SOUL.md files — each is unique
- Zero hallucination policy is present in every SOUL.md
- Cybersecurity defense posture is present in every SOUL.md
- Hard limits include turn limits and behavioral boundaries

### REQ-017: Agent Memory Files

**User Story**: As a platform engineer, I want each agent to have structured memory files so that persistent knowledge is organized and accessible.

**WHEN** an agent accesses its memory
**THEN** the agent SHALL read `profiles/{agent_name}/memories/MEMORY.md` for known patterns, platform conventions, and tool quirks
**AND** the agent SHALL read `profiles/{agent_name}/memories/USER.md` for user preferences and things to avoid
**AND** MEMORY.md SHALL be organized into sections: Known Patterns, Platform Conventions, Tool Quirks
**AND** USER.md SHALL be organized into sections: Profile, Preferences, Things to Avoid
**AND** memory entries SHALL be verified data points, not assumptions
**AND** the system-level memory at `memories/MEMORY.md` and `memories/USER.md` SHALL serve as defaults when agent-specific memory is empty

**Acceptance Criteria**:

- Each agent has a memories/ directory with MEMORY.md and USER.md
- Memory files are organized into the required sections
- Entries are verified data, not vibes
- System-level memory exists as fallback

### REQ-018: Docker Deployment

**User Story**: As a DevOps engineer, I want Hermes to run in a minimal, secure Docker container so that it can be deployed consistently across environments.

**WHEN** Hermes is deployed via Docker
**THEN** the container SHALL use python:3.13-slim-trixie as the base image
**AND** the container SHALL have zero pip dependencies (stdlib only)
**AND** the build SHALL strip attack-surface packages: pip, setuptools, wheel, perl, ncurses, gnupg, curl, tar, mount, bzip2, login, passwd, util-linux
**AND** the container SHALL run as a non-root user (telemetryflow, uid=10001)
**AND** the container SHALL include: plugins/, profiles/, skills/, hooks/, cron/, config.yaml, SOUL.md, docker-entrypoint.py
**AND** the container SHALL have a HEALTHCHECK with 30s interval, 10s timeout, 5s start period, 3 retries
**AND** the entrypoint SHALL be `python3 /app/docker-entrypoint.py`
**AND** environment variables SHALL include PYTHONDONTWRITEBYTECODE=1, PYTHONUNBUFFERED=1, TELEMETRYFLOW_API_URL, TELEMETRYFLOW_ENVIRONMENT

**Acceptance Criteria**:

- Dockerfile uses python:3.13-slim-trixie
- No pip packages are installed
- Attack-surface packages are removed
- Container runs as non-root user
- HEALTHCHECK is configured
- All required files are copied into the image

### REQ-019: Testing

**User Story**: As a platform engineer, I want comprehensive test coverage so that I can trust the reliability of the agent tools and pipeline.

**WHEN** tests are executed
**THEN** the test suite SHALL use pytest with markers: unit (no external dependencies), integration (requires TFO Platform running), slow
**AND** the test suite SHALL contain at least 472 tests
**AND** test coverage SHALL be at least 97% for `plugins/telemetryflow/tools/`
**AND** unit tests SHALL be located in `tests/unit/`
**AND** integration tests SHALL be located in `tests/integration/`
**AND** shared fixtures SHALL be in `tests/conftest.py`
**AND** test configuration SHALL be in `pyproject.toml` under `[tool.pytest.ini_options]`
**AND** coverage configuration SHALL enforce a minimum of 95% (`fail_under = 95`)
**AND** all tools SHALL use `urllib` from stdlib (no requests library) so tests mock `urllib.request.urlopen`
**AND** linting SHALL use ruff with target-version py38 and line-length 120
**AND** type checking SHALL use mypy with python_version 3.8

**Acceptance Criteria**:

- pytest runs with the configured markers
- 472+ tests pass
- Coverage is >= 97% for plugin tools
- Unit tests have no external dependencies
- conftest.py provides mock_env, mock_urlopen, mock_urlopen_error, mock_urlopen_conn_error fixtures
- ruff linting passes
- mypy type checking passes

### REQ-020: Plugin Tools

**User Story**: As a platform engineer, I want 40 plugin tools available to agents so that they can interact with the TelemetryFlow platform and ClickHouse.

**WHEN** an agent uses a plugin tool
**THEN** the tool SHALL be located in `plugins/telemetryflow/tools/`
**AND** the tool SHALL use only Python stdlib (no pip dependencies)
**AND** the tool SHALL use `urllib.request.urlopen` for HTTP requests (no requests library)
**AND** the tool SHALL read configuration from environment variables: TELEMETRYFLOW_API_URL, TELEMETRYFLOW_API_KEY, TELEMETRYFLOW_WORKSPACE_ID, TELEMETRYFLOW_ORGANIZATION_ID
**AND** ClickHouse tools SHALL read: CLICKHOUSE_HOST, CLICKHOUSE_PORT, CLICKHOUSE_USER, CLICKHOUSE_PASSWORD, CLICKHOUSE_DATABASE
**AND** tools SHALL output JSON to stdout
**AND** tools SHALL exit with code 0 on success, 1 on error
**AND** the plugin manifest SHALL be at `plugins/telemetryflow/plugin.yaml`

**Acceptance Criteria**:

- 40 tools exist in plugins/telemetryflow/tools/
- No tool imports non-stdlib packages
- Tools output valid JSON
- Environment variables are used for configuration
- Exit codes are correct (0 success, 1 error)

### REQ-021: Logging & Observability

**User Story**: As an SRE, I want the Hermes system to produce structured logs so that I can audit agent actions and debug pipeline issues.

**WHEN** the Hermes system runs
**THEN** logs SHALL be written to `~/.hermes/logs/` (configurable via `logging.path` in config.yaml)
**AND** log level SHALL be configurable via `logging.level` (default: info)
**AND** alert processing SHALL be logged to `alerts.log`
**AND** investigation starts SHALL be logged to `investigations.log`
**AND** remediation outcomes SHALL be logged to `remediations.log`
**AND** each log entry SHALL include an ISO 8601 timestamp in UTC
**AND** each log entry SHALL include the alert_id for traceability

**Acceptance Criteria**:

- Log files are created in the configured directory
- Log level is respected
- Timestamps are ISO 8601 UTC
- Alert_id is present in all relevant log entries

### REQ-022: Remediator Security Checks

**User Story**: As a security engineer, I want the Remediator to check security implications of every proposed action so that remediation doesn't create new vulnerabilities.

**WHEN** the Remediator proposes a remediation action
**THEN** the Remediator SHALL check whether the action weakens access controls
**AND** the Remediator SHALL check whether the action destroys forensic evidence
**AND** the Remediator SHALL check whether the action creates new attack surface
**AND** the Remediator SHALL check whether the action itself could be a potential attack vector
**AND** if the incident is a security event (SECURITY_ESCALATION flag), the Remediator SHALL prioritize containment over remediation
**AND** the Remediator SHALL NEVER propose destructive actions on a potentially compromised pod without warning about evidence destruction
**AND** post-action verification SHALL include: audit log checks, RBAC verification, secrets verification, network policy verification, and anomaly scan

**Acceptance Criteria**:

- Security implications are checked for every proposed action
- Security incidents get containment, not remediation
- Evidence destruction warnings are included when applicable
- Post-action verification includes security checks
