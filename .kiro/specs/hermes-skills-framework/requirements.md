# Hermes Skills Framework — Requirements

## 1. Overview

Hermes is the agentic SRE layer for TelemetryFlow. It operates through 4 agent profiles (triage, investigator, reviewer, remediator), each with its own SOUL.md personality and skill set. The skills framework provides domain-specific instructions that teach agents how to use TelemetryFlow's 40 tools effectively across 14 categories and 29 individual skills.

A **skill** is a Markdown file (`SKILL.md`) containing structured metadata, procedures, domain knowledge, and verification criteria. Skills are the primary mechanism by which agents gain expertise beyond their base personality.

---

## 2. Skill File Format

### 2.1 File Naming and Location

- Every skill MUST be named `SKILL.md` (uppercase).
- Every skill MUST reside in its own directory under `skills/<category>/` or `skills/<category>/<skill-name>/`.
- Directory name MUST use kebab-case (e.g., `cross-signal-correlation`, `qan-analysis`).
- Flat categories (e.g., `alerting/`, `iam/`) contain a single `SKILL.md` directly.
- Nested categories (e.g., `monitoring/`, `observability/`) contain subdirectories, each with its own `SKILL.md`.

### 2.2 Frontmatter Metadata

Every `SKILL.md` MUST begin with YAML frontmatter delimited by `---`:

```yaml
---
name: <skill-name>
description: >
  <One-paragraph description of when to activate this skill
  and what it provides. Written as a natural-language trigger
  condition followed by a capability summary.>
version: <semver>
author: agent
platforms: [linux, macos]
---
```

**Required fields:**

| Field         | Type   | Description                                                                                                                                                                  |
| ------------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`        | string | Unique kebab-case identifier matching the directory name. MUST be globally unique across all skills.                                                                         |
| `description` | string | Multi-line description written as an activation trigger ("Activate when...") followed by capability summary. This is the primary text used for skill discovery and matching. |
| `version`     | semver | Semantic version (MAJOR.MINOR.PATCH). Increment MAJOR on breaking structural changes, MINOR on new sections, PATCH on corrections.                                           |
| `author`      | enum   | MUST be `agent` for skills authored by the system. Human-authored skills use `author: human`.                                                                                |
| `platforms`   | array  | Supported platforms. Currently always `[linux, macos]`.                                                                                                                      |

**Optional fields:**

| Field                 | Type             | Description                                                                                                                          |
| --------------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `depends_on`          | array of strings | Names of other skills that this skill references or requires (e.g., `["cross-signal-correlation", "clickhouse-query-patterns"]`).    |
| `tools_used`          | array of strings | TelemetryFlow tools this skill teaches the agent to use (e.g., `["query_metrics", "search_logs", "list_traces"]`).                   |
| `applicable_profiles` | array of strings | Agent profiles that SHOULD load this skill (e.g., `["investigator", "triage"]`). If absent, the skill is applicable to all profiles. |
| `tags`                | array of strings | Freeform tags for search and categorization (e.g., `["kubernetes", "pods", "debugging"]`).                                           |

### 2.3 Body Structure

After frontmatter, the body MUST use these sections in order. Sections marked **REQUIRED** MUST appear in every skill. Sections marked **OPTIONAL** SHOULD be included when applicable.

#### 2.3.1 `## Procedure` (REQUIRED)

Step-by-step instructions the agent follows when the skill is activated. Steps MUST be numbered. Each step MUST be atomic and actionable. Steps MAY include:

- CLI commands in fenced code blocks with language annotation (`bash, `sql, ```python)
- API endpoint references
- Decision points ("if X, then Y")
- Cross-references to other skills by name

Example pattern:

```markdown
## Procedure

1. Get cluster overview and statistics
```

python3 check_k8s.py --resource overview

```

2. List clusters and their resources
```

python3 check_k8s.py --resource clusters

```

3. Investigate pod issues
```

python3 check_k8s.py --resource pods --cluster <cluster-id> --namespace production

```

```

#### 2.3.2 Domain Knowledge Sections (OPTIONAL but RECOMMENDED)

Named sections that provide domain context the agent needs. Common patterns observed in existing skills:

| Section                   | Purpose                              | Example                                  |
| ------------------------- | ------------------------------------ | ---------------------------------------- |
| `## Supported Databases`  | Enumerate supported systems          | 9 database types for QAN                 |
| `## K8s Resource Types`   | Entity catalog                       | 11 entity types for Kubernetes           |
| `## Agent Properties`     | Key-value attribute reference        | Agent types, auth models                 |
| `## Alert Rule Structure` | JSON schema examples                 | Alert condition format                   |
| `## Alert Lifecycle`      | State machine description            | firing → acknowledged → resolved         |
| `## Hierarchy`            | Organizational/data hierarchy        | Region → Tenant → Org → Workspace        |
| `## Data Types`           | Enumerated data categories           | logs, metrics, traces, alerts, exemplars |
| `## Permission Format`    | Syntax specification                 | `module:submodule:action`                |
| `## Security Features`    | Security controls list               | bcrypt, TOTP, MFA                        |
| `## Domain Model`         | DDD aggregate/event counts           | 8 aggregates, 28 domain events           |
| `## Auto-Provisioning`    | Automatic behavior description       | Default policies on org creation         |
| `## Root Cause Pattern`   | Known RCA patterns                   | Memory leak in connection pool refactor  |
| `## Correlation Patterns` | Pattern matching table               | Metric → Log → Trace → Cause             |
| `## Classification Rules` | Threshold-based classification rules | Latency > 2x baseline → CRITICAL         |
| `## Action Tools`         | Remediation command reference        | kubectl scale, rollout restart           |
| `## Example Queries`      | Natural language → API examples      | "What is the p95 latency?"               |
| `## TFO API Endpoints`    | REST API reference                   | `GET /monitoring/agents/:id`             |
| `## Reporting Format`     | Output template for agent reports    | Structured report template               |
| `## Pitfalls`             | Common mistakes and gotchas          | Same pod name in different namespaces    |

Section naming MUST be descriptive and specific. Avoid generic names like "Details" or "Notes".

#### 2.3.3 `## Pitfalls` (OPTIONAL but RECOMMENDED)

Bullet list of common mistakes, incorrect assumptions, or edge cases the agent must be aware of. Each pitfall MUST state:

1. What the mistake is
2. Why it happens
3. What to do instead

Example:

```markdown
## Pitfalls

- Forgetting `--previous` flag on restarted containers — you need the logs from before the crash
- Not checking node-level events — pod failures can be caused by node pressure
```

#### 2.3.4 `## Verification` (REQUIRED)

Bullet list of conditions that confirm the skill's objective has been achieved. These serve as the agent's success criteria and MUST be testable/observable.

Example:

```markdown
## Verification

- All nodes in Ready state
- No pods in CrashLoopBackOff
- Deployments have desired == available replicas
```

---

## 3. Skill Categories and Organization

### 3.1 Category Taxonomy

Skills are organized into 14 categories. Each category represents a TelemetryFlow platform domain:

| Category            | Path                          | Skill Count | Description                                                                                                                                                |
| ------------------- | ----------------------------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| AI Intelligence     | `skills/ai-intelligence/`     | 1           | LLM/AI integration and analysis                                                                                                                            |
| Alerting            | `skills/alerting/`            | 1           | Alert rules, instances, notifications                                                                                                                      |
| Audit               | `skills/audit/`               | 1           | Audit logging and trail                                                                                                                                    |
| Dashboard           | `skills/dashboard/`           | 1           | Dashboard management                                                                                                                                       |
| Database Monitoring | `skills/database-monitoring/` | 2           | QAN analysis, slow query detection                                                                                                                         |
| IAM                 | `skills/iam/`                 | 1           | Users, roles, permissions, groups, MFA                                                                                                                     |
| Monitoring          | `skills/monitoring/`          | 7           | Agent, Kubernetes, network-map, service-map, status-page, uptime, VM                                                                                       |
| Observability       | `skills/observability/`       | 8           | Alert triage, ClickHouse patterns, cross-signal correlation, K8s pod debug, memory pressure, payments API OOM RCA, remediation gate, TFQL natural language |
| Query               | `skills/query/`               | 1           | TFQL query engine                                                                                                                                          |
| Reporting           | `skills/reporting/`           | 1           | Report generation                                                                                                                                          |
| Retention           | `skills/retention/`           | 1           | Data retention policies                                                                                                                                    |
| SSO                 | `skills/sso/`                 | 1           | SSO provider management                                                                                                                                    |
| Subscription        | `skills/subscription/`        | 1           | Subscription management                                                                                                                                    |
| Tenancy             | `skills/tenancy/`             | 1           | Multi-tenancy hierarchy                                                                                                                                    |

**Total: 29 skills across 14 categories.**

### 3.2 Category Rules

- A category MUST be a single directory under `skills/`.
- Category names MUST use kebab-case.
- A category MUST contain either:
  - A single `SKILL.md` (flat category), OR
  - Multiple subdirectories, each containing a `SKILL.md` (nested category).
- A category MUST NOT mix flat and nested organization (no `SKILL.md` alongside subdirectories with `SKILL.md`).
- Nested skills MUST be in a single level of subdirectory (no `skills/monitoring/kubernetes/pods/SKILL.md` — use `skills/monitoring/kubernetes/SKILL.md`).

### 3.3 Adding New Skills

When adding a new skill:

1. Identify the correct category. If no category fits, create a new one.
2. Create the skill directory: `skills/<category>/<skill-name>/` (or `skills/<category>/` for flat).
3. Write `SKILL.md` following the format in Section 2.
4. Set `version: 1.0.0` for new skills.
5. Add the skill to any relevant agent profile configurations.
6. Update this requirements document's category table.

### 3.4 Adding New Categories

When creating a new category:

1. Create the directory under `skills/`.
2. Add an initial skill to the category.
3. Update the category taxonomy table in this document.
4. Consider whether existing skills should be reorganized into the new category.

---

## 4. Skill Authoring Guidelines

### 4.1 Writing Principles

1. **Actionable over descriptive**: Every instruction must be something the agent can DO, not just know. Prefer "Run `python3 check_k8s.py --resource pods`" over "Understand pod concepts."

2. **Specific over vague**: Use exact values, thresholds, and patterns. Prefer "Latency breach > 2x baseline → CRITICAL" over "If latency is high, flag as critical."

3. **Evidence-based**: Procedures must reference specific data sources (ClickHouse tables, API endpoints, CLI commands). The agent must never guess.

4. **Concise but complete**: Skills should be long enough to be useful but not so long that the agent loses critical instructions. Target 50–120 lines per skill.

5. **No duplication**: If a pattern appears in multiple skills, define it once and reference it via cross-skill references.

### 4.2 Code Block Conventions

- CLI commands MUST use ` ```bash ` or ` ``` ` fences.
- SQL queries MUST use ` ```sql ` fences.
- JSON payloads MUST use ` ```json ` fences.
- Python scripts MUST use ` ```python ` fences.
- Plain output MUST use ` ``` ` fences (no language annotation).

Placeholder values in code blocks MUST use `<angle-bracket>` notation:

```
python3 check_k8s.py --resource pods --cluster <cluster-id>
```

### 4.3 Threshold and Classification Rules

When writing classification rules or thresholds:

- MUST include exact numeric values with units.
- MUST specify the severity level (CRITICAL, WARNING, INFO, SECURITY ALERT).
- MUST be written as condition → consequence pairs.
- SHOULD be presented as bullet lists, not prose.

Example:

```markdown
## Classification Rules

- Agent offline > 10 min → CRITICAL
- Agent version mismatch across fleet → WARNING
- Heartbeat response time > 5s → WARNING
```

### 4.4 API Endpoint References

When referencing TelemetryFlow API endpoints:

- Use the path relative to the API base (`/api/v2/`).
- Include the HTTP method as a prefix.
- Group by resource or entity.
- Example: `GET /monitoring/agents/:id/health`

### 4.5 ClickHouse Query Patterns

When including ClickHouse queries:

- MUST filter by `workspace_id` in the WHERE clause.
- MUST include a time range filter (`timestamp >= now() - INTERVAL ...`).
- MUST end with `FORMAT JSON` for API queries.
- SHOULD use appropriate table names from `allowed_clickhouse_tables`.
- SHOULD include aggregations that reduce result size (LIMIT, GROUP BY).

### 4.6 Cross-referencing MEMORY.md

Skills that support the investigator profile SHOULD reference MEMORY.md for historical pattern matching:

- "Cross-reference MEMORY.md known patterns"
- "Check for similar patterns in MEMORY.md"
- NEVER include actual memory content in the skill — memory is dynamic and profile-specific.

---

## 5. Skill Loading and Discovery

### 5.1 Discovery Mechanism

Skills are discovered by scanning the `skills/` directory tree for files named `SKILL.md`. The discovery algorithm:

1. Walk `skills/` recursively.
2. For each `SKILL.md` found:
   a. Parse YAML frontmatter.
   b. Extract `name`, `description`, `applicable_profiles`, `depends_on`, `tags`.
   c. Build a skill registry entry.
3. Index entries by name, category, tags, and profile applicability.

### 5.2 Profile-Based Loading

Each agent profile (triage, investigator, reviewer, remediator) loads a subset of skills. The loading mechanism:

1. Read profile's `config.yaml` for skill configuration.
2. Resolve `applicable_profiles` from each skill's frontmatter.
3. A skill is loaded for a profile if:
   - `applicable_profiles` is absent (applicable to all), OR
   - The profile name appears in `applicable_profiles`.
4. Skills are loaded in category-alphabetical order, then skill-name-alphabetical order within category.
5. Skills listed in `depends_on` are loaded before the depending skill.

### 5.3 Runtime Activation

Skills are NOT all activated simultaneously. Activation follows:

1. Agent receives a task or message.
2. Agent evaluates the task against loaded skill descriptions.
3. Skills whose `description` trigger condition matches the task are activated.
4. Activated skill's `## Procedure` is followed step-by-step.
5. Multiple skills MAY be activated simultaneously for complex tasks.

### 5.4 Skill Resolution Order

When multiple skills match a task:

1. Most specific match wins (a skill whose trigger exactly describes the situation).
2. If tied, the skill with more `depends_on` (more integrated) wins.
3. If still tied, alphabetical by name.

---

## 6. Skill Content Quality

### 6.1 Validation Rules

Every `SKILL.md` MUST pass these validation checks:

| Rule                         | Description                                                                                     |
| ---------------------------- | ----------------------------------------------------------------------------------------------- |
| Frontmatter present          | File begins with `---` delimited YAML block.                                                    |
| Required fields              | `name`, `description`, `version`, `author`, `platforms` all present.                            |
| Name matches directory       | `name` field matches the containing directory name (for nested) or parent directory (for flat). |
| Version is semver            | `version` follows MAJOR.MINOR.PATCH format.                                                     |
| Procedure section present    | `## Procedure` exists and has at least 1 numbered step.                                         |
| Verification section present | `## Verification` exists and has at least 1 bullet point.                                       |
| No empty sections            | Every `##` section must have content.                                                           |
| Code blocks annotated        | All fenced code blocks have a language annotation where applicable (bash, sql, json, python).   |
| No hardcoded secrets         | No API keys, tokens, or passwords in skill content.                                             |
| Workspace filtering          | All ClickHouse queries include `workspace_id` filter.                                           |

### 6.2 Quality Metrics

| Metric                         | Target            |
| ------------------------------ | ----------------- |
| Line count per skill           | 40–150 lines      |
| Procedure steps                | 3–10 steps        |
| Verification criteria          | 2–6 bullet points |
| Classification rules           | 3–8 rules         |
| Pitfalls                       | 2–5 items         |
| Frontmatter description length | 15–60 words       |

### 6.3 Anti-patterns

The following are explicitly forbidden in skill files:

1. **Vague thresholds**: "if latency is high" without a number.
2. **Prose procedures**: Procedures written as paragraphs instead of numbered steps.
3. **Missing code fences**: Commands or queries written inline instead of in code blocks.
4. **Duplicate content**: Same instructions repeated across multiple skills (use cross-references).
5. **Hallucinated APIs**: Endpoints or tools that don't exist in TelemetryFlow.
6. **Hardcoded values**: Workspace IDs, API keys, service names (use placeholders).
7. **Remediation in investigation skills**: Investigator skills must not prescribe fixes.

---

## 7. Cross-Skill References

### 7.1 Reference Format

Skills MAY reference other skills using the skill name in backticks:

```markdown
If TFQL is unavailable, fall back to `clickhouse-query-patterns` skill.
```

### 7.2 Dependency Declaration

Skills that depend on other skills MUST declare this in frontmatter:

```yaml
depends_on:
  - cross-signal-correlation
  - clickhouse-query-patterns
```

### 7.3 Reference Graph

The skills framework maintains a directed acyclic graph (DAG) of dependencies. Requirements:

- No circular dependencies (if A depends on B, B MUST NOT depend on A).
- Transitive dependencies are resolved automatically (if A depends on B and B depends on C, A has access to C's knowledge).
- The `depends_on` field is advisory — it informs loading order and context, not hard requirements.

### 7.4 Common Cross-Skill Patterns

These skill combinations are frequently used together:

| Scenario               | Skills Involved                                                                            |
| ---------------------- | ------------------------------------------------------------------------------------------ |
| Alert investigation    | `alert-triage` → `cross-signal-correlation` → `k8s-pod-debug`                              |
| Performance RCA        | `cross-signal-correlation` → `memory-pressure-investigation` → `clickhouse-query-patterns` |
| Database slowdown      | `qan-analysis` → `slow-query-detection` → `clickhouse-query-patterns`                      |
| Natural language query | `tfql-natural-language` → `clickhouse-query-patterns`                                      |
| Remediation flow       | `remediation-gate` → `k8s-pod-debug` → `alert-triage`                                      |
| K8s incident           | `kubernetes-monitoring` → `k8s-pod-debug` → `cross-signal-correlation`                     |
| Payments OOM           | `payments-api-oom-rca` → `cross-signal-correlation` → `memory-pressure-investigation`      |

---

## 8. Skill Testing and Validation

### 8.1 Static Validation

A validation script MUST check all skill files for:

1. Frontmatter completeness (all required fields present and correctly typed).
2. Name uniqueness across all skills.
3. Section presence (Procedure, Verification at minimum).
4. Code block language annotations.
5. Cross-reference integrity (every skill referenced in `depends_on` exists).
6. No circular dependency chains.
7. Directory naming consistency (kebab-case, matches skill name).
8. File size limits (no skill > 300 lines).

### 8.2 Semantic Validation

Beyond structural checks, skills SHOULD be validated for:

1. **ClickHouse query correctness**: All SQL queries in skills are syntactically valid.
2. **API endpoint accuracy**: All referenced endpoints exist in the TelemetryFlow API surface.
3. **Tool existence**: All referenced tools exist in the agent's tool registry.
4. **Threshold consistency**: Classification rules don't contradict across skills.

### 8.3 Integration Testing

When a skill is added or modified:

1. Load the skill into the relevant agent profile(s).
2. Send a test prompt that matches the skill's activation trigger.
3. Verify the agent follows the skill's procedure steps.
4. Verify the agent produces output matching the verification criteria.
5. Verify cross-skill references resolve correctly.

### 8.4 Version Control

- Skills are versioned with semver in their frontmatter.
- When modifying a skill, increment the version:
  - PATCH: Typo fixes, formatting, clarification (no behavioral change).
  - MINOR: New sections, additional procedure steps, expanded knowledge.
  - MAJOR: Breaking changes to procedure, removed sections, changed thresholds.
- Skill version history SHOULD be tracked in git commit messages.

---

## 9. Integration with Agent Profiles

### 9.1 Profile Structure

Each agent profile lives in `profiles/<profile-name>/` with:

```
profiles/<profile-name>/
├── config.yaml        # Model, tools, gateway, delegation settings
├── SOUL.md            # Personality, behavior rules, hard limits
├── memories/
│   ├── MEMORY.md      # Historical patterns and learned knowledge
│   └── USER.md        # User preferences and context
└── skills/            # Profile-specific skill symlinks or references (if any)
```

### 9.2 Skill-Profile Binding

The binding between skills and profiles is determined by:

1. **Applicability**: The `applicable_profiles` field in skill frontmatter.
2. **Profile configuration**: Explicit skill references in `config.yaml` (future).
3. **Category mapping**: Default mapping of skill categories to profile roles.

Default category-to-profile mapping:

| Category            | Triage | Investigator | Reviewer | Remediator |
| ------------------- | ------ | ------------ | -------- | ---------- |
| AI Intelligence     |        | ✓            | ✓        |            |
| Alerting            | ✓      | ✓            | ✓        | ✓          |
| Audit               |        | ✓            | ✓        |            |
| Dashboard           |        | ✓            |          |            |
| Database Monitoring |        | ✓            | ✓        |            |
| IAM                 | ✓      | ✓            | ✓        |            |
| Monitoring (all)    | ✓      | ✓            | ✓        | ✓          |
| Observability (all) | ✓      | ✓            | ✓        | ✓          |
| Query               | ✓      | ✓            | ✓        | ✓          |
| Reporting           |        |              | ✓        |            |
| Retention           |        | ✓            |          |            |
| SSO                 | ✓      | ✓            | ✓        |            |
| Subscription        |        |              |          | ✓          |
| Tenancy             | ✓      | ✓            |          |            |

### 9.3 Profile-Specific Behavior

Skills MAY behave differently depending on the agent profile:

- **Triage**: Skills provide classification rules and routing decisions.
- **Investigator**: Skills provide investigation procedures and evidence collection.
- **Reviewer**: Skills provide verification criteria and consistency checks.
- **Remediator**: Skills provide action tools and risk assessment.

The skill content SHOULD NOT branch on profile type. Instead, each profile uses the relevant sections of the skill. For example:

- Triage reads `Classification Rules` to route alerts.
- Investigator follows `Procedure` to collect evidence.
- Reviewer checks `Verification` to validate findings.
- Remediator uses `Action Tools` to execute fixes.

### 9.4 Skill Loading at Agent Startup

When an agent starts with a profile:

1. Load `SOUL.md` — establishes personality and hard rules.
2. Load `MEMORY.md` — provides historical context.
3. Load `USER.md` — provides user preferences.
4. Discover and load applicable skills based on `applicable_profiles`.
5. Resolve `depends_on` and ensure load order.
6. Agent is ready to receive tasks.

---

## 10. Non-Functional Requirements

### 10.1 Performance

- Skill discovery and loading MUST complete in < 500ms.
- Skill frontmatter parsing MUST complete in < 10ms per skill.
- Cross-reference resolution MUST complete in < 50ms total.

### 10.2 Maintainability

- Adding a new skill MUST NOT require changes to the framework code.
- Adding a new category MUST NOT require changes to existing skills.
- A skill MUST be self-contained (no external file dependencies other than cross-references).

### 10.3 Extensibility

- The framework MUST support future skill metadata fields without breaking existing skills.
- The framework MUST support new agent profiles without changing existing skills.
- The framework MUST support skills in languages other than English (future).

### 10.4 Observability

- Skill activation events SHOULD be logged with: skill name, agent profile, timestamp, trigger context.
- Skill execution completion SHOULD be logged with: skill name, duration, success/failure.
- Skill version mismatches (skill version changed since last load) SHOULD generate warnings.
