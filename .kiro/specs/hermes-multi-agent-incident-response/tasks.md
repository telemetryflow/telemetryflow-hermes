# Implementation Plan: Hermes Multi-Agent Incident Response

## Overview

This plan implements the Hermes multi-agent incident response pipeline across 44 tasks organized into 11 phases. Each task references the requirements it satisfies and includes acceptance criteria derived from the design document.

The implementation follows a bottom-up approach: configure the infrastructure first (Docker, profiles, tools), then implement the pipeline logic (hooks, delegation, memory), then add the proactive monitoring layer (cron jobs), and finally verify everything with the test suite.

**Estimated effort**: 3-4 weeks for a single engineer. Most tasks are configuration-driven (YAML, shell scripts) rather than complex code, since the core agent logic is driven by SOUL.md personalities and the plugin tools already exist.

**Dependencies**: Tasks within a phase can run in parallel unless noted. Phase N+1 depends on Phase N completion.

---

## Tasks

### Phase 1: Foundation & Configuration

- [ ] 1. Create root `config.yaml` with global Hermes settings
  - Define: model defaults (glm-5.1, opencode-go), agent max_turns (90), terminal backend (local, 300s timeout), delegation limits (50 iterations, 1 concurrent child), tools (terminal, cronjob, delegation, web), memory limits (tier1_max_memory_chars=2200, tier1_max_user_chars=1375), curator settings (stale_after_days=30, archive_after_days=90, idle_before_run_hours=2, max_review_iterations=8), logging (level=info, path=~/.hermes/logs)
  - Acceptance: config.yaml exists with all fields, YAML parses without errors
  - _Requirements: REQ-015_

- [ ] 2. Create Triage agent profile (`profiles/triage/`)
  - Create `config.yaml` with: glm-5.1/opencode-go, max_turns=30, timeout=120s, delegation max_iterations=10, 20 allowed ClickHouse tables, readonly=true, telegram gateway
  - Create empty `memories/MEMORY.md` and `memories/USER.md`
  - Create empty `skills/` directory
  - Acceptance: Profile directory structure exists, config.yaml matches specification
  - _Requirements: REQ-015_

- [ ] 3. Create Investigator agent profile (`profiles/investigator/`)
  - Create `config.yaml` with: claude-sonnet-4-5/anthropic, max_turns=45, timeout=300s, delegation max_iterations=20, 20 allowed ClickHouse tables, readonly=true, telegram gateway
  - Create empty `memories/MEMORY.md` and `memories/USER.md`
  - Create empty `skills/` directory
  - Acceptance: Profile directory structure exists, config.yaml matches specification
  - _Requirements: REQ-015_

- [ ] 4. Create Reviewer agent profile (`profiles/reviewer/`)
  - Create `config.yaml` with: glm-5.1/opencode-go, max_turns=20, timeout=180s, delegation max_iterations=5, 20 allowed ClickHouse tables, readonly=true, telegram gateway, no delegation tool
  - Create empty `memories/MEMORY.md` and `memories/USER.md`
  - Create empty `skills/` directory
  - Acceptance: Profile directory structure exists, config.yaml matches specification
  - _Requirements: REQ-015_

- [ ] 5. Create Remediator agent profile (`profiles/remediator/`)
  - Create `config.yaml` with: glm-5.1/opencode-go, max_turns=15, timeout=180s, delegation max_iterations=5, 20 allowed ClickHouse tables, readonly=false, require_approval=true, approval_timeout_seconds=600, auto_escalate_on_timeout=true, no delegation tool
  - Create empty `memories/MEMORY.md` and `memories/USER.md`
  - Create empty `skills/` directory
  - Acceptance: Profile directory structure exists, readonly=false, require_approval=true present
  - _Requirements: REQ-015, REQ-008_

### Phase 2: Agent Identity & Personality

- [ ] 6. Write Triage SOUL.md (`profiles/triage/SOUL.md`)
  - Sections: Core Personality (ruthlessly pragmatic), Zero Hallucination Policy, Adversarial Mindset, Cybersecurity Defense Posture, Classification Protocol (CRITICAL/KNOWN/NOISE/INCOMPLETE), Debate Attitude, Hard Limits (3 turns max per classification, never investigate, never skip MEMORY.md)
  - Acceptance: SOUL.md follows format, all classification types defined, zero-hallucination policy present
  - _Requirements: REQ-016_

- [ ] 7. Write Investigator SOUL.md (`profiles/investigator/SOUL.md`)
  - Sections: Core Personality (hostile scientist), Zero Hallucination Policy, Cybersecurity Defense Posture, Falsification-First Protocol (metrics→logs→traces→exemplars), Cross-Examination Rules, Evidence Standards (source/timestamp/workspace/value/signal), Attitude Toward Other Agents, Hard Limits (45 turns, never propose remediation, always filter by workspace_id)
  - Acceptance: SOUL.md follows format, falsification protocol defined, evidence format specified
  - _Requirements: REQ-016_

- [ ] 8. Write Reviewer SOUL.md (`profiles/reviewer/SOUL.md`)
  - Sections: Core Personality (professional skeptic), Zero Hallucination Policy, Cybersecurity Defense Posture, Falsification Protocol (5-step verification), Verdict Protocol (CONFIRMED/NEEDS_MORE_EVIDENCE/REJECTED), Independence Rules, Attitude Toward Other Agents, Hard Limits (20 turns, read-only only, never propose remediation)
  - Acceptance: SOUL.md follows format, verdict types defined, independence rules explicit
  - _Requirements: REQ-016_

- [ ] 9. Write Remediator SOUL.md (`profiles/remediator/SOUL.md`)
  - Sections: Core Personality (cautious pragmatist), Zero Hallucination Policy, Cybersecurity Defense Posture, The Three Gates (Confirmed Root Cause, Proportional Response, Human Approval), Post-Action Verification, Risk Assessment Framework (LOW/MEDIUM/HIGH/CRITICAL), Attitude Toward Other Agents, Hard Limits (15 turns, never execute without approval, always include rollback)
  - Acceptance: SOUL.md follows format, three gates defined, risk levels specified, approval gate documented
  - _Requirements: REQ-016, REQ-007, REQ-008_

- [ ] 10. Write root SOUL.md (`SOUL.md`)
  - Top-level personality: pragmatic senior SRE, observability expertise, signal over noise, root cause over symptoms, never fabricate metrics, never guess without ClickHouse evidence, concise evidence-based communication
  - Acceptance: Root SOUL.md exists with core behavioral rules
  - _Requirements: REQ-016_

### Phase 3: Memory & Knowledge

- [ ] 11. Write system-level MEMORY.md (`memories/MEMORY.md`)
  - Sections: Known Patterns (payments-api OOM, workspace_id mandatory, node-pool-3 memory, alert fatigue, auth-service cert rotation, redis-cluster-01 backup), Platform Conventions (OTLP tables, tenant hierarchy, workspace_id filter, materialized views), Tool Quirks (ClickHouse JSON format, kubectl --previous, trace span_id requirement)
  - Acceptance: MEMORY.md has all three sections with real entries
  - _Requirements: REQ-010, REQ-017_

- [ ] 12. Write system-level USER.md (`memories/USER.md`)
  - Sections: Profile (TelemetryFlow Observability Bot, Platform Engineer/SRE, TelemetryFlow Core, expert in observability/ClickHouse/K8s/OTLP), Preferences (concise/evidence-based, actionable alerts with runbooks, human approval for production changes, English), Things to Avoid (no pod restarts without approval, no skipping cross-signal correlation, no assuming alert noise, no ClickHouse queries without workspace_id)
  - Acceptance: USER.md has all three sections with real entries
  - _Requirements: REQ-010, REQ-017_

- [ ] 13. Write per-agent MEMORY.md files
  - Copy system-level memory as initial seed to each agent's `profiles/{agent}/memories/MEMORY.md`
  - Acceptance: All 4 agent directories have memories/MEMORY.md
  - _Requirements: REQ-010_

- [ ] 14. Write per-agent USER.md files
  - Copy system-level user preferences to each agent's `profiles/{agent}/memories/USER.md`
  - Acceptance: All 4 agent directories have memories/USER.md
  - _Requirements: REQ-010_

### Phase 4: Pipeline Hooks

- [ ] 15. Implement `hooks/on-alert-fired.sh`
  - Accept alert payload as $1, parse JSON to extract alert_id/rule_name/severity, log to $HERMES_HOME/logs/alerts.log with ISO 8601 timestamp, print enrichment metadata, use set -euo pipefail
  - Acceptance: Script is executable, logs correctly, handles malformed JSON gracefully
  - _Requirements: REQ-011_

- [ ] 16. Implement `hooks/pre-investigation.sh`
  - Accept alert_id/service/severity as $1/$2/$3, log to $HERMES_HOME/logs/investigations.log, warn on missing alert_id, use set -euo pipefail
  - Acceptance: Script is executable, logs correctly, warns on empty alert_id
  - _Requirements: REQ-011_

- [ ] 17. Implement `hooks/post-remediation.sh`
  - Accept 8 parameters (alert_id, action, outcome, approved_by, service, root_cause, start_time, severity), log to remediations.log, generate RCA report on success via generate_rca_report.py, write to $HERMES_HOME/reports/RCA-{alert_id}-{date}.md, handle RCA generation failure gracefully (|| exit 0)
  - Acceptance: Script is executable, logs correctly, generates RCA on success, non-blocking on failure
  - _Requirements: REQ-011, REQ-009_

### Phase 5: Cron Jobs

- [ ] 18. Define `cron/jobs.json` with all 6 scheduled tasks
  - Jobs: health-check-metrics (every 15m, investigator), log-error-sweep (every 30m, investigator), k8s-health-check (every 10m, investigator), db-slow-query-check (every 1h, investigator), alert-fatigue-review (every 6h, triage), skill-curator (every 7d, default)
  - Each job: id, profile, schedule, task description, enabled, output_dir
  - Acceptance: jobs.json is valid JSON, all 6 jobs defined with correct profiles
  - _Requirements: REQ-012_

- [ ] 19. Create `cron/output/` directory
  - Create output directory with .gitkeep
  - Acceptance: cron/output/ exists
  - _Requirements: REQ-012_

### Phase 6: Delegation & Handoff Protocol

- [ ] 20. Validate delegation configuration across all agents
  - Verify: Triage (max_iterations=10), Investigator (max_iterations=20), Reviewer (max_iterations=5), Remediator (max_iterations=5), all have max_concurrent_children=1
  - Verify: Delegation flows are sequential (Triage→Investigator→Reviewer→Remediator)
  - Acceptance: No agent allows parallel children, iteration limits match spec
  - _Requirements: REQ-003, REQ-013_

- [ ] 21. Define Delegation Context schema documentation
  - Document the structured context format: alert_id, from_agent, to_agent, classification, security_flag, challenge_statement, evidence_summary, hypothesis, dead_hypotheses, verdict, caveats, timestamp
  - Acceptance: Schema documented in design.md, format agreed upon
  - _Requirements: REQ-003_

### Phase 7: Security Integration

- [ ] 22. Verify Triage security classification rules
  - Verify SOUL.md includes: threat-informed triage (DDoS, SQL injection, brute force, exfiltration, privilege escalation, lateral movement), security classification override (NOISE→CRITICAL, KNOWN→CRITICAL, CRITICAL+SECURITY_FLAG), security red flags list (login failures 10x baseline, DELETE on audit logs, system.\* tables, kube-system pod execs, unexpected secrets mounts, unknown IPs)
  - Acceptance: Triage SOUL.md has complete security section
  - _Requirements: REQ-002_

- [ ] 23. Verify Investigator security investigation protocol
  - Verify SOUL.md includes: threat hypothesis generation (8 alert patterns with operational+security hypotheses), security evidence queries (audit logs, access patterns, network anomalies, IAM changes, SSO events), attack pattern recognition (credential stuffing, injection, supply chain, insider, crypto, exfiltration, lateral movement, privilege escalation), security escalation protocol (STOP, don't alert attacker, escalate to human, preserve evidence)
  - Acceptance: Investigator SOUL.md has complete security section
  - _Requirements: REQ-005_

- [ ] 24. Verify Reviewer security review checklist
  - Verify SOUL.md includes: security review checklist (6 items), security verdict override (operational confirmed but security blind spot → NEEDS_MORE_EVIDENCE, active threat → CONFIRMED+SECURITY_ESCALATION), attack cover-up detection (6 patterns)
  - Acceptance: Reviewer SOUL.md has complete security section
  - _Requirements: REQ-006_

- [ ] 25. Verify Remediator security-aware remediation
  - Verify SOUL.md includes: security-aware remediation (4 checks: access controls, forensic evidence, attack surface, attack vector), security incident containment (network isolation, rate limiting, access revocation), post-action security verification (audit logs, RBAC, secrets, network policies, anomaly scan)
  - Acceptance: Remediator SOUL.md has complete security section
  - _Requirements: REQ-022_

### Phase 8: Docker Configuration

- [ ] 26. Create Dockerfile
  - FROM python:3.13-slim-trixie, ARG VERSION/GIT_COMMIT/GIT_BRANCH/BUILD_TIME, LABEL metadata, ENV PYTHONDONTWRITEBYTECODE/PYTHONUNBUFFERED/TELEMETRYFLOW_API_URL/TELEMETRYFLOW_ENVIRONMENT, apt dist-upgrade, create telemetryflow user (uid=10001), strip attack-surface packages (perl, ncurses, gnupg, curl, binutils, tar, mount, bzip2, login, passwd, util-linux, e2fsprogs), remove pip/setuptools/wheel and Python idlelib/pydoc/unittest/lib2to3, autoremove + clean, COPY plugins/profiles/skills/hooks/cron/config.yaml/SOUL.md/docker-entrypoint.py, USER telemetryflow, WORKDIR /app, HEALTHCHECK
  - Acceptance: Dockerfile builds successfully, container runs as non-root, no pip packages installed
  - _Requirements: REQ-018_

- [ ] 27. Create docker-entrypoint.py
  - Python stdlib entrypoint that handles --check flag for healthcheck, loads config.yaml, initializes the agent pipeline
  - Acceptance: Entry point runs, --check exits 0
  - _Requirements: REQ-018_

- [ ] 28. Create docker-compose.yaml
  - Define hermes service with build context, environment variables (from .env), volume mounts for memories and logs, Telegram gateway configuration
  - Acceptance: docker-compose config validates
  - _Requirements: REQ-018_

- [ ] 29. Create .env.example
  - Template for: TELEMETRYFLOW*API_URL, TELEMETRYFLOW_API_KEY, TELEMETRYFLOW_WORKSPACE_ID, TELEMETRYFLOW_ORGANIZATION_ID, CLICKHOUSE*_, TELEGRAM*BOT_TOKEN*_, TELEGRAM*CHAT_ID*
  - Acceptance: .env.example has all required variables documented
  - _Requirements: REQ-018, REQ-020_

### Phase 9: Plugin Tools

- [ ] 30. Verify all 40 plugin tools exist
  - Tools: \_shared.py, chat_with_context, check_agent, check_db_monitoring, check_infra, check_k8s, check_network_map, check_service_map, check_uptime, check_vm, generate_insight, generate_postmortem, generate_rca_report, generate_rca_template, get_exemplars, list_traces, manage_alerts, manage_conversation, manage_dashboards, manage_data_masking, manage_iam, manage_provider, manage_reports, manage_retention, manage_sso, manage_tenancy, query_account, query_ai_intelligence, query_audit, query_correlations, query_llm_usage, query_metrics, query_platform, query_subscription, query_tfql, restart_pod, rollback_deploy, scale_deployment, search_logs, stream_chat, update_alert
  - Acceptance: All 40 .py files exist in plugins/telemetryflow/tools/
  - _Requirements: REQ-020_

- [ ] 31. Verify tools use stdlib only
  - Grep for non-stdlib imports (requests, httpx, aiohttp, etc.), verify all tools use urllib.request.urlopen
  - Acceptance: No non-stdlib HTTP libraries imported
  - _Requirements: REQ-020_

- [ ] 32. Verify plugin.yaml manifest
  - Verify plugins/telemetryflow/plugin.yaml exists and declares all 40 tools
  - Acceptance: plugin.yaml is valid and lists all tools
  - _Requirements: REQ-020_

### Phase 10: Testing

- [*] 33. Verify test configuration in pyproject.toml
  - Verify: testpaths=["tests"], addopts includes strict-markers, markers defined (unit/integration/slow), coverage source=["plugins/telemetryflow/tools"], coverage fail_under=95
  - Acceptance: pyproject.toml test configuration matches spec
  - _Requirements: REQ-019_

- [*] 34. Verify conftest.py fixtures
  - Verify fixtures: mock_env, mock_urlopen, mock_urlopen_error, mock_urlopen_conn_error, capture_stdout, mock_exit, tfo_response_factory, SAMPLE_METRICS/LOGS/TRACES/EXEMPLARS/CORRELATIONS data
  - Acceptance: All fixtures present and functional
  - _Requirements: REQ-019_

- [*] 35. Verify unit test coverage (41 files)
  - Run: `pytest tests/unit/ -v --tb=short`
  - Verify: All tests pass, coverage >= 95%
  - Acceptance: All unit tests pass, coverage report shows >= 95% for tools/
  - _Requirements: REQ-019_

- [*] 36. Verify integration tests
  - Run: `pytest tests/integration/ -v --tb=short -m integration` (requires TFO Platform or mocked)
  - Verify: TestMetricsPipeline, TestLogsPipeline, TestTracesPipeline, TestK8sPipeline, TestChatPipeline, TestInsightPipeline, TestAlertPipeline, TestProviderPipeline
  - Acceptance: All integration test classes present and runnable
  - _Requirements: REQ-019_

- [*] 37. Run linting and type checking
  - Run: `ruff check plugins/`, `mypy plugins/`
  - Acceptance: No linting errors, no type errors
  - _Requirements: REQ-019_

- [*] 38. Verify total test count
  - Run: `pytest tests/ --co -q | tail -1`
  - Verify: 472 tests
  - Acceptance: Test count >= 472
  - _Requirements: REQ-019_

### Phase 11: Documentation & Verification

- [ ] 39. Create Makefile with all commands
  - Commands: init (first-time setup), configure (install profiles/skills/plugins/cron/hooks), deploy (start gateways), stop (stop gateways), status (check gateway status), verify (e2e pipeline test), doctor (hermes doctor --fix), docker-build, docker-up, test, lint, typecheck, coverage
  - Acceptance: Makefile targets exist and run correctly
  - _Requirements: REQ-021_

- [ ] 40. Verify logging configuration
  - Verify: config.yaml has logging.level and logging.path, hooks log to correct files, log format includes ISO 8601 timestamps and alert_id
  - Acceptance: Logs are written to configured path with correct format
  - _Requirements: REQ-021_

- [ ] 41. End-to-end pipeline verification
  - Run: `make verify`
  - Verify: Alert → Hook → Triage → Investigator → Reviewer → Remediator → Human → RCA flow works with mock data
  - Acceptance: Full pipeline completes without errors, RCA report generated
  - _Requirements: All requirements_

- [ ] 42. Security review of Docker image
  - Run: `trivy image telemetryflow-hermes:latest` or equivalent
  - Verify: No critical/high CVEs, attack-surface packages removed
  - Acceptance: Docker image passes security scan
  - _Requirements: REQ-018_

### Checkpoints

- [ ] 43. Checkpoint - Pipeline verification complete
  - All pipeline hooks functional
  - All agent profiles configured and tested
  - Delegation flow verified end-to-end
  - _Requirements: REQ-011, REQ-013, REQ-016_

- [ ] 44. Final Checkpoint - All requirements satisfied
  - All 44 tasks completed
  - Full test suite passing (472 tests, >= 95% coverage)
  - Docker image built and security-scanned
  - Documentation complete
  - _Requirements: All requirements_
