# =============================================================================
# TelemetryFlow Hermes - Makefile
# =============================================================================
#
# TelemetryFlow Hermes — Self-Improving AI Agent for Observability
# Copyright (c) 2024-2026 Telemetri Data Indonesia. All rights reserved.
#
# This Makefile provides standardized commands for development, testing,
# deployment, and CI/CD of TelemetryFlow Hermes multi-agent integration.
#
# =============================================================================

# Build variables
PACKAGE_NAME := telemetryflow-hermes
VERSION := $(shell python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])" 2>/dev/null || echo "3.0.0")
GIT_COMMIT := $(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown")
GIT_BRANCH := $(shell git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
BUILD_TIME := $(shell date -u '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || echo "unknown")
PYTHON_VERSION := $(shell python3 --version 2>&1 | cut -d ' ' -f 2)

# Paths
HERMES_HOME ?= ~/.hermes
PROJECT_DIR := $(shell pwd)
BUILD_DIR := build
DIST_DIR := dist
PLUGINS_DIR := plugins
TESTS_DIR := tests
COVERAGE_SOURCE := plugins/telemetryflow/tools

# Tools
PYTHON := python3
PIP := pip3
PYTEST := pytest
RUFF := ruff
MYPY := mypy

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m

# Default target
.DEFAULT_GOAL := help

# =============================================================================
# Help
# =============================================================================

.PHONY: help
help: ## Show this help message
	@echo "$(BLUE)$(PRODUCT_NAME) - Makefile$(NC)"
	@echo ""
	@echo "$(YELLOW)Available targets:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-30s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)Variables:$(NC)"
	@echo "  VERSION      = $(VERSION)"
	@echo "  GIT_COMMIT   = $(GIT_COMMIT)"
	@echo "  GIT_BRANCH   = $(GIT_BRANCH)"
	@echo "  HERMES_HOME  = $(HERMES_HOME)"
	@echo "  PYTHON       = $(PYTHON_VERSION)"
	@echo "  PYTEST       = $(shell $(PYTEST) --version 2>/dev/null | head -1 || echo 'not installed')"
	@echo "  RUFF         = $(shell $(RUFF) --version 2>/dev/null || echo 'not installed')"

# =============================================================================
# Build
# =============================================================================

.PHONY: build
build: ## Build wheel package
	@echo "$(BLUE)Building $(PACKAGE_NAME)...$(NC)"
	@mkdir -p $(BUILD_DIR)
	$(PIP) install build
	$(PYTHON) -m build
	@echo "$(GREEN)Build complete: $(DIST_DIR)/$(NC)"

.PHONY: build-release
build-release: clean ## Build optimized release package
	@echo "$(BLUE)Building release $(PACKAGE_NAME)...$(NC)"
	$(PIP) install build
	$(PYTHON) -m build
	@echo "$(GREEN)Release build complete: $(DIST_DIR)/$(NC)"

# =============================================================================
# Install & Setup
# =============================================================================

.PHONY: install
install: ## Install Hermes Agent framework
	@echo "$(BLUE)Installing Hermes Agent...$(NC)"
	curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
	@echo "$(GREEN)Run: source ~/.bashrc$(NC)"

.PHONY: setup
setup: profiles skills cron security hooks plugins ## Deploy all profiles, skills, cron, security, hooks, plugins
	@echo "$(GREEN)TelemetryFlow Hermes setup complete.$(NC)"

.PHONY: profiles
profiles: ## Create 4 agent profiles (triage, investigator, reviewer, remediator)
	@echo "$(BLUE)Creating agent profiles...$(NC)"
	@bash scripts/setup-profiles.sh

.PHONY: skills
skills: ## Install all skills (monitoring, database, observability, platform)
	@echo "$(BLUE)Installing skills...$(NC)"
	@mkdir -p $(HERMES_HOME)/skills
	@for dir in $$(ls -d skills/*/ 2>/dev/null); do \
		category=$$(basename $$dir); \
		echo "  Installing category: $$category"; \
		mkdir -p $(HERMES_HOME)/skills/$$category; \
		for skill in $$(ls -d skills/$$category/*/ 2>/dev/null); do \
			skill_name=$$(basename $$skill); \
			echo "    Installing: $$category/$$skill_name"; \
			cp -r $$skill $(HERMES_HOME)/skills/$$category/ 2>/dev/null || true; \
		done; \
	done

.PHONY: cron
cron: ## Install 6 scheduled investigation jobs
	@echo "$(BLUE)Installing cron jobs...$(NC)"
	mkdir -p $(HERMES_HOME)/cron
	cp cron/jobs.json $(HERMES_HOME)/cron/jobs.json

.PHONY: security
security: ## Setup ClickHouse read-only user (hermes_readonly, 20 tables)
	@echo "$(BLUE)Setting up security...$(NC)"
	@bash security/setup-readonly-user.sh 2>/dev/null || echo "  $(YELLOW)Skipping ClickHouse setup (run manually)$(NC)"

.PHONY: hooks
hooks: ## Install 3 lifecycle hooks (on-alert-fired, pre-investigation, post-remediation)
	@echo "$(BLUE)Installing lifecycle hooks...$(NC)"
	mkdir -p $(HERMES_HOME)/hooks
	cp hooks/*.sh $(HERMES_HOME)/hooks/
	@chmod +x $(HERMES_HOME)/hooks/*.sh

.PHONY: plugins
plugins: ## Install TelemetryFlow plugin (37 tools)
	@echo "$(BLUE)Installing TelemetryFlow plugin...$(NC)"
	mkdir -p $(HERMES_HOME)/plugins/telemetryflow
	cp -r plugins/telemetryflow/* $(HERMES_HOME)/plugins/telemetryflow/

.PHONY: telegram
telegram: ## Configure 4 Telegram gateway bots
	@echo "$(BLUE)Setting up Telegram gateways...$(NC)"
	@bash scripts/setup-telegram.sh

# =============================================================================
# Deploy & Operations
# =============================================================================

.PHONY: deploy
deploy: setup ## Setup + start all 4 Telegram gateways
	@echo "$(BLUE)Starting gateways...$(NC)"
	hermes -p triage gateway start &
	hermes -p investigator gateway start &
	hermes -p reviewer gateway start &
	hermes -p remediator gateway start &
	@echo "$(GREEN)All gateways started. Use 'make status' to check.$(NC)"

.PHONY: status
status: ## Check all 4 gateway statuses
	@echo "$(BLUE)Checking gateway statuses...$(NC)"
	hermes -p triage gateway status
	hermes -p investigator gateway status
	hermes -p reviewer gateway status
	hermes -p remediator gateway status

.PHONY: verify
verify: ## Run end-to-end pipeline verification
	@echo "$(BLUE)Verifying pipeline...$(NC)"
	@bash scripts/verify-pipeline.sh

.PHONY: doctor
doctor: ## Run hermes doctor --fix
	hermes doctor --fix

.PHONY: air-gapped
air-gapped: ## Deploy with Ollama (offline, no external network)
	@echo "$(BLUE)Deploying air-gapped configuration...$(NC)"
	@bash scripts/deploy-air-gapped.sh

.PHONY: clean
clean: ## Remove all installed components, build artifacts, and coverage files
	@echo "$(BLUE)Cleaning...$(NC)"
	rm -rf $(HERMES_HOME)/profiles/triage
	rm -rf $(HERMES_HOME)/profiles/investigator
	rm -rf $(HERMES_HOME)/profiles/reviewer
	rm -rf $(HERMES_HOME)/profiles/remediator
	@for dir in $$(ls -d $(HERMES_HOME)/skills/*/ 2>/dev/null); do \
		rm -rf $$dir; \
	done
	rm -rf $(HERMES_HOME)/plugins/telemetryflow
	rm -f $(HERMES_HOME)/cron/jobs.json
	rm -rf $(BUILD_DIR) $(DIST_DIR)
	rm -rf *.egg-info/
	rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/
	rm -rf htmlcov/ .coverage coverage.xml coverage-unit.xml coverage-integration.xml
	rm -f junit.xml junit-unit.xml junit-integration.xml bandit-results.sarif
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)Clean complete$(NC)"

# =============================================================================
# Dependencies
# =============================================================================

.PHONY: deps
deps: ## Install development dependencies (pytest, ruff, bandit, mypy)
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install pytest pytest-cov ruff bandit mypy
	@echo "$(GREEN)Dependencies installed$(NC)"

.PHONY: deps-update
deps-update: ## Update all dependencies to latest versions
	@echo "$(BLUE)Updating dependencies...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade pytest pytest-cov ruff bandit mypy
	@echo "$(GREEN)Dependencies updated$(NC)"

.PHONY: deps-refresh
deps-refresh: ## Refresh all dependencies (clean and re-download)
	@echo "$(BLUE)Refreshing dependencies...$(NC)"
	$(PIP) cache purge 2>/dev/null || true
	$(PIP) install --upgrade pip
	$(PIP) install --force-reinstall pytest pytest-cov ruff bandit mypy
	@echo "$(GREEN)Dependencies refreshed$(NC)"

.PHONY: deps-check
deps-check: ## Check for dependency vulnerabilities
	@echo "$(BLUE)Checking dependencies for vulnerabilities...$(NC)"
	@if command -v pip-audit >/dev/null 2>&1; then \
		pip-audit; \
	else \
		echo "pip-audit not installed. Run: pip install pip-audit"; \
	fi

.PHONY: deps-lock
deps-lock: ## Generate requirements lock file
	@echo "$(BLUE)Generating requirements lock...$(NC)"
	$(PIP) freeze > requirements.lock
	@echo "$(GREEN)Lock file generated: requirements.lock$(NC)"

.PHONY: deps-tree
deps-tree: ## Show dependency tree
	@echo "$(BLUE)Dependency tree...$(NC)"
	@if command -v pipdeptree >/dev/null 2>&1; then \
		pipdeptree; \
	else \
		echo "pipdeptree not installed. Run: pip install pipdeptree"; \
	fi

.PHONY: deps-verify
deps-verify: ## Verify no broken dependencies
	@echo "$(BLUE)Verifying dependencies...$(NC)"
	$(PIP) check
	@echo "$(GREEN)Dependencies verified$(NC)"

# =============================================================================
# Code Quality
# =============================================================================

.PHONY: fmt
fmt: ## Format code with ruff
	@echo "$(BLUE)Formatting code...$(NC)"
	$(RUFF) check --fix $(PLUGINS_DIR) $(TESTS_DIR)
	$(RUFF) format $(PLUGINS_DIR) $(TESTS_DIR)
	@echo "$(GREEN)Code formatted$(NC)"

.PHONY: fmt-check
fmt-check: ## Check code formatting without fixing
	@echo "$(BLUE)Checking code formatting...$(NC)"
	$(RUFF) format --check $(PLUGINS_DIR) $(TESTS_DIR)
	@echo "$(GREEN)Format check passed$(NC)"

.PHONY: lint
lint: ## Run ruff linter on plugins and tests
	@echo "$(BLUE)Running linter...$(NC)"
	$(RUFF) check $(PLUGINS_DIR) $(TESTS_DIR)
	@echo "$(GREEN)Lint complete$(NC)"

.PHONY: lint-fix
lint-fix: ## Run ruff linter with auto-fix
	@echo "$(BLUE)Running linter with auto-fix...$(NC)"
	$(RUFF) check --fix $(PLUGINS_DIR) $(TESTS_DIR)
	@echo "$(GREEN)Lint fix complete$(NC)"

.PHONY: format
format: fmt ## Alias for fmt

.PHONY: typecheck
typecheck: ## Run mypy type checking on plugins
	@echo "$(BLUE)Running type checker...$(NC)"
	$(MYPY) $(PLUGINS_DIR)
	@echo "$(GREEN)Type check complete$(NC)"

.PHONY: check
check: fmt-check lint typecheck ## Run all code quality checks (format + lint + typecheck)
	@echo "$(GREEN)All checks passed$(NC)"

# =============================================================================
# Testing
# =============================================================================

.PHONY: test
test: ## Run all tests (unit + integration)
	@echo "$(BLUE)Running all tests...$(NC)"
	$(PYTEST) $(TESTS_DIR) -v --tb=short
	@echo "$(GREEN)All tests complete$(NC)"

.PHONY: test-unit
test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	$(PYTEST) $(TESTS_DIR)/unit -v --tb=short
	@echo "$(GREEN)Unit tests complete$(NC)"

.PHONY: test-integration
test-integration: ## Run integration tests only
	@echo "$(BLUE)Running integration tests...$(NC)"
	$(PYTEST) $(TESTS_DIR)/integration -v --tb=short
	@echo "$(GREEN)Integration tests complete$(NC)"

.PHONY: test-all
test-all: test ## Alias for test

.PHONY: test-fast
test-fast: ## Run tests without slow markers
	@echo "$(BLUE)Running fast tests...$(NC)"
	$(PYTEST) $(TESTS_DIR) -v -m "not slow"
	@echo "$(GREEN)Fast tests complete$(NC)"

.PHONY: test-cov
test-cov: ## Run all tests with coverage report (95%+ required)
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	@mkdir -p $(BUILD_DIR)
	$(PYTEST) $(TESTS_DIR) -v --tb=short \
		--cov=$(COVERAGE_SOURCE) \
		--cov-report=term-missing \
		--cov-report=html:$(BUILD_DIR)/htmlcov \
		--cov-report=xml:$(BUILD_DIR)/coverage.xml \
		--cov-fail-under=95
	@echo "$(GREEN)Coverage report: $(BUILD_DIR)/htmlcov/index.html$(NC)"

.PHONY: test-cov-unit
test-cov-unit: ## Run unit tests with coverage report
	@echo "$(BLUE)Running unit tests with coverage...$(NC)"
	$(PYTEST) $(TESTS_DIR)/unit -v --tb=short \
		--cov=$(COVERAGE_SOURCE) \
		--cov-report=term-missing \
		--cov-report=html:htmlcov \
		--cov-report=xml:coverage-unit.xml
	@echo "$(GREEN)Unit test coverage report generated$(NC)"

.PHONY: test-cov-integration
test-cov-integration: ## Run integration tests with coverage report
	@echo "$(BLUE)Running integration tests with coverage...$(NC)"
	$(PYTEST) $(TESTS_DIR)/integration -v --tb=short \
		--cov=$(COVERAGE_SOURCE) \
		--cov-append \
		--cov-report=term-missing \
		--cov-report=xml:coverage-integration.xml
	@echo "$(GREEN)Integration test coverage report generated$(NC)"

.PHONY: test-tool
test-tool: ## Run tests for specific tool (usage: make test-tool TOOL=query_metrics)
	@if [ -z "$(TOOL)" ]; then \
		echo "$(RED)TOOL is required. Usage: make test-tool TOOL=query_metrics$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Running tests for tool: $(TOOL)...$(NC)"
	$(PYTEST) $(TESTS_DIR)/unit/test_$(TOOL).py -v --tb=short

.PHONY: test-shared
test-shared: ## Run tests for _shared.py utilities
	@echo "$(BLUE)Running shared utilities tests...$(NC)"
	$(PYTEST) $(TESTS_DIR)/unit/test_shared.py -v --tb=short

.PHONY: test-watch
test-watch: ## Run all tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(NC)"
	$(PYTEST) $(TESTS_DIR) -v --tb=short -f -s

.PHONY: test-unit-watch
test-unit-watch: ## Run unit tests in watch mode
	@echo "$(BLUE)Running unit tests in watch mode...$(NC)"
	$(PYTEST) $(TESTS_DIR)/unit -v --tb=short -f -s

# =============================================================================
# CI/CD Pipeline
# =============================================================================

.PHONY: ci-deps
ci-deps: ## CI: Install CI dependencies (pytest, pytest-cov, ruff, bandit, mypy)
	@echo "$(BLUE)CI: Installing dependencies...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install pytest pytest-cov ruff bandit mypy
	@echo "$(GREEN)CI: Dependencies installed$(NC)"

.PHONY: ci-lint
ci-lint: ## CI: Run ruff check + format check + mypy type check
	@echo "$(BLUE)CI: Running linting...$(NC)"
	$(RUFF) check $(PLUGINS_DIR) $(TESTS_DIR)
	$(RUFF) format --check $(PLUGINS_DIR) $(TESTS_DIR)
	$(MYPY) $(PLUGINS_DIR)
	@echo "$(GREEN)CI: Linting completed$(NC)"

.PHONY: ci-test-unit
ci-test-unit: ## CI: Run unit tests with coverage XML + JUnit XML
	@echo "$(BLUE)CI: Running unit tests...$(NC)"
	$(PYTEST) $(TESTS_DIR)/unit -v --tb=short \
		--cov=$(COVERAGE_SOURCE) \
		--cov-report=xml:coverage-unit.xml \
		--cov-report=term-missing \
		--junitxml=junit-unit.xml
	@echo "$(GREEN)CI: Unit tests completed$(NC)"

.PHONY: ci-test-integration
ci-test-integration: ## CI: Run integration tests with coverage (continue-on-error)
	@echo "$(BLUE)CI: Running integration tests...$(NC)"
	$(PYTEST) $(TESTS_DIR)/integration -v --tb=short \
		--cov=$(COVERAGE_SOURCE) \
		--cov-append \
		--cov-report=xml:coverage-integration.xml \
		--cov-report=term-missing \
		--junitxml=junit-integration.xml || true
	@echo "$(GREEN)CI: Integration tests completed$(NC)"

.PHONY: ci-test
ci-test: ci-test-unit ci-test-integration ## CI: Run all tests (unit + integration)
	@echo "$(GREEN)CI: All tests completed$(NC)"

.PHONY: ci-build
ci-build: clean ## CI: Build package
	@echo "$(BLUE)CI: Building package...$(NC)"
	$(PIP) install build
	$(PYTHON) -m build
	@echo "$(GREEN)CI: Build complete$(NC)"
	@ls -la $(DIST_DIR)/

.PHONY: ci-security
ci-security: ## CI: Run bandit SARIF security scan
	@echo "$(BLUE)CI: Running security scan...$(NC)"
	@$(PIP) install bandit bandit-sarif-formatter 2>/dev/null || true
	bandit -r $(PLUGINS_DIR)/ --format sarif --output bandit-results.sarif -ll || true
	@echo "$(GREEN)CI: Security scan completed$(NC)"

.PHONY: ci-coverage
ci-coverage: ## CI: Generate coverage reports (xml, html, term) with 95% threshold
	@echo "$(BLUE)CI: Generating coverage reports...$(NC)"
	$(PYTEST) $(TESTS_DIR) --cov=$(COVERAGE_SOURCE) \
		--cov-report=xml:coverage.xml \
		--cov-report=html:$(BUILD_DIR)/htmlcov \
		--cov-report=term-missing \
		--cov-fail-under=95 \
		-q
	@echo "$(GREEN)CI: Coverage reports generated$(NC)"

.PHONY: ci-validate
ci-validate: ## CI: Validate project configuration
	@echo "$(BLUE)CI: Validating project...$(NC)"
	$(PIP) check
	@echo "$(GREEN)CI: Project validation completed$(NC)"

.PHONY: ci-pipeline
ci-pipeline: ci-deps ci-lint ci-test ci-security ## CI: Run complete pipeline (deps → lint → test → security)
	@echo "$(GREEN)CI Pipeline completed successfully$(NC)"

.PHONY: ci
ci: deps fmt-check lint typecheck test ## Run CI pipeline locally
	@echo "$(GREEN)CI pipeline complete$(NC)"

.PHONY: coverage-report
coverage-report: ## Generate merged coverage report
	@echo "$(BLUE)Generating coverage report...$(NC)"
	$(PYTEST) $(TESTS_DIR) --cov=$(COVERAGE_SOURCE) \
		--cov-report=html:$(BUILD_DIR)/htmlcov \
		--cov-report=term-missing \
		-q
	@echo "$(GREEN)Coverage report: $(BUILD_DIR)/htmlcov/index.html$(NC)"

# =============================================================================
# Security
# =============================================================================

.PHONY: security-check
security-check: ## Run security checks (bandit + pip-audit)
	@echo "$(BLUE)Running security checks...$(NC)"
	@if command -v bandit >/dev/null 2>&1; then \
		bandit -r $(PLUGINS_DIR) -ll; \
	else \
		echo "bandit not installed. Run: pip install bandit"; \
	fi
	@if command -v pip-audit >/dev/null 2>&1; then \
		pip-audit; \
	else \
		echo "pip-audit not installed. Run: pip install pip-audit"; \
	fi

.PHONY: audit
audit: deps-check security-check ## Run full security audit
	@echo "$(GREEN)Security audit complete$(NC)"

# =============================================================================
# Release
# =============================================================================

.PHONY: release-check
release-check: lint test-cov ## Pre-release checks (lint + test with coverage)
	@echo "$(GREEN)Release checks passed$(NC)"

.PHONY: release
release: clean build-release ## Create release artifacts
	@echo "$(BLUE)Creating release $(VERSION)...$(NC)"
	@mkdir -p $(DIST_DIR)/release
	@cp $(DIST_DIR)/*.whl $(DIST_DIR)/release/ 2>/dev/null || true
	@cp $(DIST_DIR)/*.tar.gz $(DIST_DIR)/release/ 2>/dev/null || true
	@echo "$(GREEN)Release artifacts created in $(DIST_DIR)/release$(NC)"
	@ls -la $(DIST_DIR)/release/

.PHONY: publish
publish: ## Publish to PyPI
	@echo "$(BLUE)Publishing to PyPI...$(NC)"
	@if command -v twine >/dev/null 2>&1; then \
		twine upload $(DIST_DIR)/*; \
	else \
		echo "twine not installed. Run: pip install twine"; \
	fi

.PHONY: publish-test
publish-test: ## Publish to Test PyPI
	@echo "$(BLUE)Publishing to Test PyPI...$(NC)"
	@if command -v twine >/dev/null 2>&1; then \
		twine upload --repository testpypi $(DIST_DIR)/*; \
	else \
		echo "twine not installed. Run: pip install twine"; \
	fi

# =============================================================================
# Pre-commit
# =============================================================================

.PHONY: pre-commit
pre-commit: ## Run pre-commit hooks on all files
	@echo "$(BLUE)Running pre-commit...$(NC)"
	@if command -v pre-commit >/dev/null 2>&1; then \
		pre-commit run --all-files; \
	else \
		echo "pre-commit not installed. Run: pip install pre-commit"; \
	fi

.PHONY: pre-commit-update
pre-commit-update: ## Update pre-commit hooks
	@echo "$(BLUE)Updating pre-commit hooks...$(NC)"
	pre-commit autoupdate

# =============================================================================
# Utilities
# =============================================================================

.PHONY: health
health: ## Check TelemetryFlow Platform health
	@echo "$(BLUE)Checking TelemetryFlow Platform health...$(NC)"
	@if curl -sf "$${TELEMETRYFLOW_API_URL:-http://localhost:3000/api/v2}/../health" >/dev/null 2>&1; then \
		echo "$(GREEN)TelemetryFlow Platform is healthy$(NC)"; \
	else \
		echo "$(RED)TelemetryFlow Platform is not responding$(NC)"; \
		exit 1; \
	fi

.PHONY: version
version: ## Show version information
	@echo "$(BLUE)Version Information:$(NC)"
	@echo "  Product:     $(PRODUCT_NAME)"
	@echo "  Version:     $(VERSION)"
	@echo "  Git Commit:  $(GIT_COMMIT)"
	@echo "  Git Branch:  $(GIT_BRANCH)"
	@echo "  Build Time:  $(BUILD_TIME)"
	@echo "  Python:      $(PYTHON_VERSION)"
	@echo "  Pytest:      $(shell $(PYTEST) --version 2>/dev/null | head -1 || echo 'not installed')"
	@echo "  Ruff:        $(shell $(RUFF) --version 2>/dev/null || echo 'not installed')"

.PHONY: info
info: version ## Alias for version

# =============================================================================
# Development Shortcuts
# =============================================================================

.PHONY: start
start: deps setup ## Install deps + deploy everything
	@echo "$(GREEN)Ready for development$(NC)"

.PHONY: reset
reset: clean setup ## Clean + re-deploy all components
	@echo "$(GREEN)Environment reset completed$(NC)"

# =============================================================================
# Special Targets
# =============================================================================

.PHONY: all
all: fmt lint typecheck test build ## Run full pipeline (format + lint + typecheck + test + build)

.PRECIOUS: pyproject.toml

SHELL := /bin/bash
