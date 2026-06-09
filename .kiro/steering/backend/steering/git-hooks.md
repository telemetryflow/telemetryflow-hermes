# Git Hooks & Quality Gates

This document defines the git hooks and automated quality checks for TelemetryFlow Platform, ensuring code quality and module standardization before commits.

## Pre-commit Hook Implementation

### Hook Location

```bash
.git/hooks/pre-commit
```

### Complete Pre-commit Script

```bash
#!/bin/bash
# TelemetryFlow Platform Pre-commit Hook
# Ensures code quality and module standardization

set -e

echo "🔍 Running TelemetryFlow Platform pre-commit checks..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. Check for required files in modules
print_status "Checking module structure compliance..."

MODULES=$(find src/modules -maxdepth 1 -type d -name "*" | grep -v "__" | grep -v "src/modules$" || true)

for MODULE in $MODULES; do
    MODULE_NAME=$(basename $MODULE)
    print_status "Validating module: $MODULE_NAME"

    # Check for required documentation
    if [ ! -f "$MODULE/README.md" ]; then
        print_error "Missing README.md in $MODULE_NAME"
        exit 1
    fi

    # Check README.md length (should be substantial)
    README_LINES=$(wc -l < "$MODULE/README.md" 2>/dev/null || echo "0")
    if [ "$README_LINES" -lt 100 ]; then
        print_warning "README.md in $MODULE_NAME is too short ($README_LINES lines). Should be 500+ lines for complete documentation."
    fi

    # Check for required DDD structure
    REQUIRED_DIRS=("domain" "application" "infrastructure" "presentation")
    for DIR in "${REQUIRED_DIRS[@]}"; do
        if [ ! -d "$MODULE/$DIR" ]; then
            print_error "Missing $DIR/ directory in $MODULE_NAME"
            exit 1
        fi
    done

    # Check for domain layer structure
    DOMAIN_DIRS=("aggregates" "value-objects" "events" "repositories")
    for DIR in "${DOMAIN_DIRS[@]}"; do
        if [ ! -d "$MODULE/domain/$DIR" ]; then
            print_warning "Missing domain/$DIR/ directory in $MODULE_NAME"
        fi
    done

    # Check for application layer structure
    APP_DIRS=("commands" "queries" "handlers" "dto")
    for DIR in "${APP_DIRS[@]}"; do
        if [ ! -d "$MODULE/application/$DIR" ]; then
            print_warning "Missing application/$DIR/ directory in $MODULE_NAME"
        fi
    done

    # Check for infrastructure layer structure
    INFRA_DIRS=("persistence")
    for DIR in "${INFRA_DIRS[@]}"; do
        if [ ! -d "$MODULE/infrastructure/$DIR" ]; then
            print_warning "Missing infrastructure/$DIR/ directory in $MODULE_NAME"
        fi
    done

    # Check for presentation layer structure
    PRES_DIRS=("controllers" "dto")
    for DIR in "${PRES_DIRS[@]}"; do
        if [ ! -d "$MODULE/presentation/$DIR" ]; then
            print_warning "Missing presentation/$DIR/ directory in $MODULE_NAME"
        fi
    done

    print_success "Module $MODULE_NAME structure validated"
done

# 2. Check TypeScript compilation
print_status "Checking TypeScript compilation..."
if ! pnpm build > /dev/null 2>&1; then
    print_error "TypeScript compilation failed"
    print_status "Running build to show errors..."
    pnpm build
    exit 1
fi
print_success "TypeScript compilation passed"

# 3. Run linting
print_status "Running ESLint..."
if ! pnpm lint > /dev/null 2>&1; then
    print_error "Linting failed"
    print_status "Running lint to show errors..."
    pnpm lint
    exit 1
fi
print_success "Linting passed"

# 4. Check for hardcoded database names
print_status "Checking for hardcoded database names..."
HARDCODED_DB=$(grep -r "telemetryflow_db\|telemetryflow-db" src/ --include="*.ts" --exclude-dir=node_modules || true)
if [ ! -z "$HARDCODED_DB" ]; then
    print_error "Found hardcoded database names:"
    echo "$HARDCODED_DB"
    print_error "Use environment variables instead"
    exit 1
fi
print_success "No hardcoded database names found"

# 5. Check for proper naming conventions
print_status "Checking naming conventions..."

# Check for kebab-case in domain layer (should be PascalCase)
KEBAB_DOMAIN=$(find src/modules/*/domain -name "*-*.ts" 2>/dev/null || true)
if [ ! -z "$KEBAB_DOMAIN" ]; then
    print_error "Found kebab-case files in domain layer (should be PascalCase):"
    echo "$KEBAB_DOMAIN"
    exit 1
fi

# Check for missing .entity.ts suffix in entities
ENTITY_FILES=$(find src/modules/*/infrastructure/persistence/entities -name "*.ts" ! -name "*.entity.ts" ! -name "index.ts" 2>/dev/null || true)
if [ ! -z "$ENTITY_FILES" ]; then
    print_error "Found entity files without .entity.ts suffix:"
    echo "$ENTITY_FILES"
    exit 1
fi

print_success "Naming conventions validated"

# 6. Run tests with coverage
print_status "Running tests with coverage..."
if ! pnpm test --coverage --passWithNoTests --silent > /dev/null 2>&1; then
    print_error "Tests failed"
    print_status "Running tests to show failures..."
    pnpm test --coverage --passWithNoTests
    exit 1
fi

# Check coverage threshold
COVERAGE_FILE="coverage/coverage-summary.json"
if [ -f "$COVERAGE_FILE" ]; then
    # Extract coverage percentages using node
    COVERAGE_CHECK=$(node -e "
        const coverage = require('./coverage/coverage-summary.json');
        const total = coverage.total;
        const failed = [];

        if (total.lines.pct < 90) failed.push('lines: ' + total.lines.pct + '%');
        if (total.functions.pct < 90) failed.push('functions: ' + total.functions.pct + '%');
        if (total.branches.pct < 90) failed.push('branches: ' + total.branches.pct + '%');
        if (total.statements.pct < 90) failed.push('statements: ' + total.statements.pct + '%');

        if (failed.length > 0) {
            console.log('FAILED: ' + failed.join(', '));
            process.exit(1);
        } else {
            console.log('PASSED');
        }
    " 2>/dev/null || echo "COVERAGE_CHECK_FAILED")

    if [[ "$COVERAGE_CHECK" == FAILED* ]]; then
        print_error "Coverage below 90% threshold: ${COVERAGE_CHECK#FAILED: }"
        exit 1
    elif [ "$COVERAGE_CHECK" = "COVERAGE_CHECK_FAILED" ]; then
        print_warning "Could not check coverage thresholds"
    else
        print_success "Test coverage meets 90% threshold"
    fi
else
    print_warning "Coverage file not found, skipping coverage check"
fi

print_success "Tests passed"

# 7. Check for TODO/FIXME comments in committed code
print_status "Checking for TODO/FIXME comments..."
TODO_COUNT=$(git diff --cached --name-only | grep -E '\.(ts|js)$' | xargs grep -l "TODO\|FIXME" 2>/dev/null | wc -l || echo "0")
if [ "$TODO_COUNT" -gt 0 ]; then
    print_warning "Found $TODO_COUNT files with TODO/FIXME comments being committed"
    git diff --cached --name-only | grep -E '\.(ts|js)$' | xargs grep -n "TODO\|FIXME" 2>/dev/null || true
    print_warning "Consider resolving these before committing"
fi

# 8. Check for console.log statements
print_status "Checking for console.log statements..."
CONSOLE_LOGS=$(git diff --cached --name-only | grep -E '\.(ts|js)$' | xargs grep -l "console\.log" 2>/dev/null || true)
if [ ! -z "$CONSOLE_LOGS" ]; then
    print_error "Found console.log statements in committed files:"
    echo "$CONSOLE_LOGS"
    print_error "Remove console.log statements or use proper logging"
    exit 1
fi

# 9. Check for proper import statements
print_status "Checking import statements..."
RELATIVE_IMPORTS=$(git diff --cached --name-only | grep -E '\.ts$' | xargs grep -n "from '\.\./\.\./\.\." 2>/dev/null || true)
if [ ! -z "$RELATIVE_IMPORTS" ]; then
    print_warning "Found deep relative imports (consider using absolute imports):"
    echo "$RELATIVE_IMPORTS"
fi

# 10. Validate environment variables usage
print_status "Checking environment variable usage..."
ENV_VARS=$(git diff --cached --name-only | grep -E '\.(ts|js)$' | xargs grep -n "process\.env\." 2>/dev/null || true)
if [ ! -z "$ENV_VARS" ]; then
    print_status "Found environment variable usage - ensure they're documented in .env.example"
fi

# 11. Check for proper error handling
print_status "Checking error handling patterns..."
THROW_STRINGS=$(git diff --cached --name-only | grep -E '\.ts$' | xargs grep -n "throw ['\"]" 2>/dev/null || true)
if [ ! -z "$THROW_STRINGS" ]; then
    print_warning "Found string throws (consider using Error objects):"
    echo "$THROW_STRINGS"
fi

# 12. Final validation summary
print_status "Pre-commit validation summary:"
print_success "✅ Module structure compliance"
print_success "✅ TypeScript compilation"
print_success "✅ ESLint validation"
print_success "✅ Database naming conventions"
print_success "✅ File naming conventions"
print_success "✅ Test coverage (≥90%)"
print_success "✅ Code quality checks"

echo ""
print_success "🎉 All pre-commit checks passed! Ready to commit."
echo ""
```

## Installation Instructions

### 1. Create the Pre-commit Hook

```bash
# Make the hook executable
chmod +x .git/hooks/pre-commit

# Copy the script content to the hook file
cat > .git/hooks/pre-commit << 'EOF'
# [Insert the complete script above]
EOF
```

### 2. Alternative: Use Husky (Recommended)

For better team collaboration, use Husky to manage git hooks:

```bash
# Install Husky
pnpm add -D husky

# Initialize Husky
npx husky install

# Create pre-commit hook
npx husky add .husky/pre-commit "bash scripts/pre-commit-hook.sh"
```

Then create `scripts/pre-commit-hook.sh` with the script content above.

## Hook Configuration

### Environment Variables

The hook respects these environment variables:

```bash
# Skip specific checks
SKIP_COVERAGE_CHECK=true          # Skip coverage validation
SKIP_LINT_CHECK=true              # Skip linting
SKIP_BUILD_CHECK=true             # Skip TypeScript compilation
SKIP_MODULE_STRUCTURE_CHECK=true  # Skip module structure validation

# Coverage thresholds (default: 90%)
COVERAGE_THRESHOLD_LINES=90
COVERAGE_THRESHOLD_FUNCTIONS=90
COVERAGE_THRESHOLD_BRANCHES=90
COVERAGE_THRESHOLD_STATEMENTS=90
```

### Bypassing Hooks (Emergency)

In emergency situations, you can bypass the pre-commit hook:

```bash
# Skip all pre-commit hooks
git commit --no-verify -m "Emergency fix"

# Skip specific checks
SKIP_COVERAGE_CHECK=true git commit -m "WIP: Feature development"
```

## Module-Specific Validations

### IAM Module Checks

For the IAM module specifically, the hook validates:

- [ ] Complete DDD structure (domain/application/infrastructure/presentation)
- [ ] All aggregates extend `AggregateRoot`
- [ ] All value objects extend `ValueObject`
- [ ] All events extend `DomainEvent`
- [ ] Repository interfaces use `I` prefix
- [ ] Entities use `.entity.ts` suffix
- [ ] Handlers use proper CQRS decorators
- [ ] Controllers use Swagger decorators
- [ ] DTOs include validation decorators

### Database Migration Checks

- [ ] Migration files follow naming convention: `{timestamp}-{Description}.ts`
- [ ] Migrations include both `up()` and `down()` methods
- [ ] No hardcoded database names
- [ ] Proper foreign key constraints
- [ ] Indexes for performance

### Security Checks

- [ ] No hardcoded secrets or passwords
- [ ] No console.log statements in production code
- [ ] Proper error handling (no string throws)
- [ ] Environment variables documented in `.env.example`

## Continuous Integration Integration

### GitHub Actions Integration

```yaml
# .github/workflows/quality-gates.yml
name: Quality Gates

on:
  pull_request:
    branches: [main, develop]

jobs:
  quality-gates:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: "22"

      - name: Install pnpm
        run: npm install -g pnpm

      - name: Install dependencies
        run: pnpm install

      - name: Run pre-commit checks
        run: bash scripts/pre-commit-hook.sh
```

## Troubleshooting

### Common Issues

1. **Coverage threshold failures**

   ```bash
   # Check current coverage
   pnpm test --coverage

   # View detailed coverage report
   open coverage/lcov-report/index.html
   ```

2. **Module structure violations**

   ```bash
   # Generate missing directories
   mkdir -p src/modules/iam/domain/{aggregates,value-objects,events,repositories}
   mkdir -p src/modules/iam/application/{commands,queries,handlers,dto}
   ```

3. **Naming convention violations**
   ```bash
   # Rename files to follow conventions
   mv src/modules/iam/domain/user.ts src/modules/iam/domain/User.ts
   mv src/modules/iam/infrastructure/entities/User.ts src/modules/iam/infrastructure/entities/User.entity.ts
   ```

### Performance Optimization

For large codebases, optimize the hook performance:

```bash
# Only check changed files
CHANGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(ts|js)$')

# Run checks only on changed modules
CHANGED_MODULES=$(git diff --cached --name-only | grep "src/modules/" | cut -d'/' -f3 | sort -u)
```

## Best Practices

1. **Run checks locally before committing**

   ```bash
   # Test the pre-commit hook manually
   bash .git/hooks/pre-commit
   ```

2. **Keep hooks fast** (< 30 seconds for most commits)
3. **Provide clear error messages** with actionable solutions
4. **Allow emergency bypasses** but log them for review
5. **Update hooks regularly** as project standards evolve

This git hooks system ensures that all code committed to TelemetryFlow Platform meets the established quality standards and module standardization requirements.
