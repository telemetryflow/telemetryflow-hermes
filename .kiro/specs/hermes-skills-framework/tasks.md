# Implementation Plan: Hermes Skills Framework

## Overview

This plan implements the Hermes Skills Framework in six phases, progressing from validation and linting (Phase 1) through skill discovery and loading infrastructure (Phase 2), context assembly (Phase 3), comprehensive testing (Phase 4), authoring tooling (Phase 5), and documentation and polish (Phase 6). The approach builds foundational validation first, then core parsing and registry infrastructure, enabling all downstream features.

## Tasks

- [ ] 1. Skill File Validator Script
  - Walks `skills/` recursively, finds all `SKILL.md` files
  - Parses YAML frontmatter from each file
  - Validates required fields: `name`, `description`, `version`, `author`, `platforms`
  - Validates `version` is valid semver (MAJOR.MINOR.PATCH)
  - Validates `author` is one of `agent`, `human`
  - Validates `platforms` is a non-empty list
  - Checks that `## Procedure` section exists with at least 1 numbered step
  - Checks that `## Verification` section exists with at least 1 bullet point
  - Checks for empty sections (any `##` heading with no content before the next heading)
  - Checks skill name uniqueness across all skills
  - Validates all cross-references in `depends_on` exist in the discovered skill set
  - Detects circular dependency chains
  - Reports all errors with file path and line number
  - Exit code 0 if all skills pass, 1 if any validation error found
  - Can be run standalone: `python3 scripts/validate_skills.py`
  - _Priority: P0 | Effort: S | Depends on: None_

- [ ] 2. Add Validator to CI
  - Add `validate-skills` target to `Makefile`
  - Add step to `.gitlab-ci.yml` (or `.github/workflows/`) that runs the validator
  - Pipeline fails if any skill file is invalid
  - Pipeline reports which files failed and why
  - _Priority: P1 | Effort: XS | Depends on: 1_

- [ ] 3. Lint Skill Markdown Style
  - All fenced code blocks have a language annotation (except plain ``` blocks for output)
  - No hardcoded workspace IDs, API keys, or tokens
  - All ClickHouse SQL queries include `workspace_id` filter
  - All ClickHouse SQL queries include a time range filter
  - All ClickHouse SQL queries end with `FORMAT JSON` (where appropriate for API queries)
  - Classification rules follow the `condition → severity` pattern
  - File line count is within 40–300 lines
  - Reports style violations separately from structural errors
  - _Priority: P2 | Effort: S | Depends on: 1_

- [ ] 4. Skill Parser Module
  - `skills_loader/parser.py` implements `parse_skill(path: str) -> Skill` with the Skill data model
  - `Skill` dataclass includes: `meta: SkillMeta`, `category: str`, `path: str`, `body: SkillBody`
  - `SkillMeta` dataclass includes all frontmatter fields (required + optional)
  - `SkillBody` dataclass includes: `procedure: list[ProcedureStep]`, `sections: dict`, `verification: list[str]`
  - `ProcedureStep` dataclass includes: `number: int`, `text: str`, `code_blocks: list[CodeBlock]`
  - Frontmatter parsing handles multi-line `description` with `>` and `|` YAML syntax
  - Body parsing splits into sections by `## ` headings
  - Procedure step parsing handles numbered steps with nested code blocks
  - Handles malformed files gracefully (returns parse errors, doesn't crash)
  - _Priority: P1 | Effort: M | Depends on: None_

- [ ] 5. Skill Discovery Module
  - `skills_loader/discovery.py` implements `discover_skills(root: str) -> list[Skill]`
  - Walks directory tree, finds all `SKILL.md` files
  - Derives category from first directory level under root
  - Calls parser for each file, collects results
  - Reports and skips files that fail parsing
  - Performance: completes in < 500ms for 29 skills
  - _Priority: P1 | Effort: S | Depends on: 4_

- [ ] 6. Skill Registry Module
  - `skills_loader/registry.py` implements `SkillRegistry` class
  - `build_registry(skills: list[Skill]) -> SkillRegistry` builds indexes from discovered skills
  - Indexes by: name, category, tag, profile applicability
  - `get_by_name(name) -> Skill | None`
  - `get_by_category(category) -> list[Skill]`
  - `get_by_tag(tag) -> list[Skill]`
  - `get_by_profile(profile) -> list[Skill]`
  - `get_all() -> list[Skill]`
  - `search(query: str) -> list[Skill]` with token-based scoring
  - Dependency graph: `get_dependencies(name) -> list[Skill]` and `get_dependents(name) -> list[Skill]`
  - Dependency resolution uses topological sort (Kahn's algorithm)
  - Cycle detection raises `CircularDependencyError` with cycle path
  - _Priority: P1 | Effort: M | Depends on: 4, 5_

- [ ] 7. Dependency Resolution
  - Builds a directed graph from `depends_on` fields
  - Topological sort produces a valid load order
  - Missing dependencies produce warnings (not errors)
  - Circular dependencies produce errors with the cycle path
  - Load order is deterministic (alphabetical tiebreaker)
  - _Priority: P1 | Effort: S | Depends on: 6_

- [ ] 8. Profile-Based Filtering
  - `filter_for_profile(registry: SkillRegistry, profile: str) -> list[Skill]`
  - Skills without `applicable_profiles` are included for all profiles
  - Skills with `applicable_profiles` are included only if the profile is listed
  - Filtered skill list respects dependency order (dependees come before dependents)
  - Works with the 4 existing profiles: triage, investigator, reviewer, remediator
  - _Priority: P1 | Effort: S | Depends on: 6_

- [ ] 9. Context Builder
  - `skills_loader/context.py` implements `build_context(profile_path: str, registry: SkillRegistry) -> str`
  - Loads `SOUL.md` from the profile directory
  - Loads `MEMORY.md` and `USER.md` from `memories/`
  - Assembles skills grouped by category (alphabetical), then by skill name (alphabetical)
  - Produces a single Markdown string suitable for injection into an agent's system prompt
  - Output format: `[SOUL.md content]` followed by `## Loaded Skills` with category sections
  - Handles missing files gracefully (MEMORY.md and USER.md are optional)
  - Configuration for max context size (warn if exceeding threshold)
  - _Priority: P1 | Effort: M | Depends on: 6, 8_

- [ ] 10. Configuration Integration
  - Profile `config.yaml` supports optional `skills` section with `include`, `exclude`, `extra_context`, `load_strategy`
  - `include` (whitelist): only load listed skills
  - `exclude` (blacklist): remove listed skills from applicable set
  - `extra_context`: load additional Markdown files
  - `load_strategy`: `eager` (default) or `lazy` (future)
  - Backward compatible: profiles without `skills` section get default behavior
  - _Priority: P2 | Effort: S | Depends on: 9_

- [*] 11. Unit Tests for Parser
  - Test parsing of valid SKILL.md with all frontmatter fields
  - Test parsing of minimal SKILL.md (required fields only)
  - Test parsing of SKILL.md with optional fields (`depends_on`, `tags`, `tools_used`, `applicable_profiles`)
  - Test multi-line description parsing (folded `>` and literal `|`)
  - Test procedure step parsing with code blocks
  - Test section extraction (all standard sections)
  - Test verification bullet parsing
  - Test malformed frontmatter (missing delimiters, invalid YAML)
  - Test missing required sections (no Procedure, no Verification)
  - Test edge cases: empty file, file with only frontmatter, file with no code blocks
  - Use pytest, co-locate in `skills_loader/__tests__/`
  - _Priority: P1 | Effort: M | Depends on: 4_

- [*] 12. Unit Tests for Registry
  - Test index building from a list of skills
  - Test `get_by_name` (found, not found)
  - Test `get_by_category` (single category, empty category)
  - Test `get_by_tag` (single tag, multiple tags, no tags)
  - Test `get_by_profile` (with applicable_profiles, without applicable_profiles)
  - Test `search` with various queries (name match, description match, tag match, no match)
  - Test dependency graph building
  - Test topological sort correctness
  - Test cycle detection
  - Test missing dependency handling
  - _Priority: P1 | Effort: M | Depends on: 6_

- [*] 13. Integration Tests
  - Discover all 29 skills successfully
  - Validate all 29 skills pass structural validation
  - All skill names are unique
  - No circular dependencies
  - Each of the 4 profiles gets a non-empty skill set
  - Context assembly produces valid Markdown for each profile
  - Context for investigator includes observability skills
  - Context for triage includes alert-triage skill
  - Context for remediator includes remediation-gate skill
  - Total context size is reasonable (< 50,000 tokens)
  - _Priority: P2 | Effort: M | Depends on: 5, 6, 8, 9_

- [*] 14. Validation CI Integration Tests
  - Validator passes on current skill set (all 29 skills)
  - Validator correctly catches a malformed SKILL.md (test with a fixture)
  - Validator correctly catches duplicate names
  - Validator correctly catches circular dependencies
  - Makefile target runs without error
  - _Priority: P2 | Effort: XS | Depends on: 1, 13_

- [ ] 15. Skill Scaffolding Script
  - `scripts/scaffold_skill.py --category <cat> --name <name>`
  - Creates the directory structure (flat or nested based on whether category already has subdirectories)
  - Generates a `SKILL.md` template with frontmatter with all required fields, `## Procedure` section with placeholder steps, `## Verification` section with placeholder bullets
  - Validates the generated file passes the validator
  - Prints the created file path
  - _Priority: P2 | Effort: S | Depends on: 1_

- [ ] 16. Skill Version Bumper
  - `scripts/bump_skill_version.py --skill <name> --level <major|minor|patch>`
  - Parses the skill, bumps the version in frontmatter
  - Writes the file back preserving all other content
  - Reports old and new version
  - _Priority: P3 | Effort: XS | Depends on: 4_

- [ ] 17. Skill Dependency Visualizer
  - `scripts/visualize_skills.py` generates a DOT/Graphviz graph
  - Nodes are skills, edges are `depends_on` relationships
  - Color-coded by category
  - Can output as SVG or PNG
  - Can output as text (adjacency list) for non-graphical environments
  - _Priority: P3 | Effort: S | Depends on: 6_

- [ ] 18. Skills Framework README
  - Documents the directory structure and naming conventions
  - Explains the SKILL.md format with examples
  - Documents the frontmatter fields (required and optional)
  - Provides a skill authoring guide with dos and don'ts
  - Documents the validator and how to run it
  - Documents the loader and registry API
  - Includes the category taxonomy table
  - Includes the profile-to-category mapping table
  - _Priority: P2 | Effort: S | Depends on: 4, 5, 6, 7, 8_

- [ ] 19. Skill Index Document
  - `scripts/generate_skill_index.py` generates a Markdown document listing all skills
  - Grouped by category with skill count per category
  - Each skill shows: name, description (truncated), version, applicable profiles, tags
  - Cross-reference table showing skill-to-profile mapping
  - Dependency graph in text form
  - Can be run as part of CI to keep the index up-to-date
  - _Priority: P3 | Effort: S | Depends on: 6_

- [ ] 20. Migrate Existing Skills to Full Spec Compliance
  - All skills pass the validator without errors
  - All skills have consistent frontmatter (add optional fields where appropriate)
  - Cross-references use the correct backtick format
  - Classification rules follow `condition → severity` format consistently
  - ClickHouse queries all have `workspace_id` filter
  - Add `depends_on` to skills that reference other skills
  - Add `tools_used` to skills that use specific TelemetryFlow tools
  - Add `applicable_profiles` to skills with clear profile affinity
  - Add `tags` to all skills for better discoverability
  - All skills within 40–300 line range
  - _Priority: P1 | Effort: M | Depends on: 1_

## Task Dependency Graph

```
Phase 1 (Validation):
  1 Validator ──→ 2 CI Integration
       │
       ├──→ 3 Markdown Lint
       └──→ 15 Scaffolding

Phase 2 (Infrastructure):
  4 Parser ──→ 5 Discovery ──→ 6 Registry ──→ 7 Dep Resolution
                    │                │
                    │                └──→ 8 Profile Filtering
                    │                          │
                    └──→ 7 Dep Resolution       │
                                                 │
Phase 3 (Context):                                │
  9 Context Builder ←── 6, 8 ←─────────────────┘
  10 Config Integration ←── 9

Phase 4 (Testing):
  11 Parser Tests ←── 4
  12 Registry Tests ←── 6
  13 Integration Tests ←── 5, 6, 8, 9
  14 CI Tests ←── 1, 13

Phase 5 (Tooling):
  15 Scaffolding ←── 1
  16 Version Bumper ←── 4
  17 Visualizer ←── 6

Phase 6 (Polish):
  18 README ←── Phase 2
  19 Skill Index ←── 6
  20 Migrate Skills ←── 1
```

## Effort Estimates

| ID  | Task                        | Effort | Priority |
| --- | --------------------------- | ------ | -------- |
| 1   | Skill File Validator        | S      | P0       |
| 2   | Add Validator to CI         | XS     | P1       |
| 3   | Lint Skill Markdown Style   | S      | P2       |
| 4   | Skill Parser Module         | M      | P1       |
| 5   | Skill Discovery Module      | S      | P1       |
| 6   | Skill Registry Module       | M      | P1       |
| 7   | Dependency Resolution       | S      | P1       |
| 8   | Profile-Based Filtering     | S      | P1       |
| 9   | Context Builder             | M      | P1       |
| 10  | Configuration Integration   | S      | P2       |
| 11  | Unit Tests for Parser       | M      | P1       |
| 12  | Unit Tests for Registry     | M      | P1       |
| 13  | Integration Tests           | M      | P2       |
| 14  | Validation CI Tests         | XS     | P2       |
| 15  | Skill Scaffolding Script    | S      | P2       |
| 16  | Skill Version Bumper        | XS     | P3       |
| 17  | Skill Dependency Visualizer | S      | P3       |
| 18  | Skills Framework README     | S      | P2       |
| 19  | Skill Index Document        | S      | P3       |
| 20  | Migrate Existing Skills     | M      | P1       |

**Legend**: XS = <1hr, S = 1-3hr, M = 3-8hr, L = 8-16hr

## Recommended Execution Order

1. **Sprint 1** (Foundation): 1 → 4 → 5 → 6 → 11 → 12
2. **Sprint 2** (Integration): 7 → 8 → 9 → 10 → 13 → 2 → 14
3. **Sprint 3** (Hardening): 20 → 3 → 15 → 18
4. **Sprint 4** (Polish): 16 → 17 → 19
