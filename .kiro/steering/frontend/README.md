# Kiro Configuration Directory

This directory contains Kiro-specific configuration, steering files, and specifications for the TelemetryFlow-Viz project.

## Directory Structure

```
.kiro/
├── README.md                    # This file
├── REFACTORING_SUMMARY.md       # Summary of recent refactoring
├── steering/                    # Steering files (always-on guidance)
│   ├── product.md               # Product overview and features
│   ├── tech.md                  # Technology stack and build system
│   ├── structure.md             # Project structure and organization
│   ├── vue-patterns.md          # Vue 3 development patterns
│   ├── naming-conventions.md    # Naming conventions for Vue.js
│   └── testing.md               # Testing guide for Vue.js
└── specs/                       # Feature specifications (empty)
```

## Steering Files

Steering files provide always-on guidance to Kiro AI assistant. They are automatically included in the context when relevant to the user's request.

### Current Steering Files

1. **product.md** (Always included)
   - Product overview and core features
   - Technology stack summary
   - Architecture overview
   - Data source integration
   - Default access credentials

2. **tech.md** (Always included)
   - Detailed technology stack
   - Build system configuration
   - Development commands
   - Environment variables
   - Performance considerations

3. **structure.md** (Always included)
   - Project directory structure
   - Source code organization
   - Component organization
   - Mock data structure
   - Route structure

4. **vue-patterns.md** (Always included)
   - Vue 3 Composition API patterns
   - Composables pattern
   - Pinia store patterns
   - Component patterns
   - TypeScript patterns
   - Testing patterns

5. **naming-conventions.md** (Always included)
   - File naming conventions
   - Code naming conventions
   - CSS/SCSS naming
   - Environment variables
   - Route naming

6. **testing.md** (Always included)
   - Testing philosophy
   - Testing stack (Vitest)
   - Component testing patterns
   - Store testing patterns
   - Coverage requirements

## Specs Directory

The `specs/` directory is for feature specifications using the spec format. Currently empty.

### Spec Format

Specs follow a structured format:

- `requirements.md` - User stories and acceptance criteria
- `design.md` - Architecture and design decisions
- `tasks.md` - Implementation tasks and progress

## Usage

### For Developers

Steering files are automatically used by Kiro AI assistant. You don't need to reference them explicitly. They provide:

- Consistent coding patterns
- Project-specific conventions
- Technology stack guidance
- Testing strategies

### For Kiro AI

Steering files are included in the context based on:

- **Always included**: All steering files are always included
- **File match**: Can be configured to include only when specific files are read
- **Manual**: Can be configured to require explicit user reference

## Customization

### Adding New Steering Files

1. Create a new `.md` file in `.kiro/steering/`
2. Add front-matter for conditional inclusion (optional):
   ```markdown
   ---
   inclusion: fileMatch
   fileMatchPattern: "src/components/**/*.vue"
   ---
   ```
3. Write guidance in markdown format

### Creating Specs

1. Create a new directory in `.kiro/specs/` with the feature name
2. Add `requirements.md`, `design.md`, and `tasks.md`
3. Reference the spec in chat with `#[[spec:feature-name]]`

## Best Practices

### Steering Files

- ✅ Keep focused on specific topics
- ✅ Use clear, actionable guidance
- ✅ Include code examples
- ✅ Update when patterns change
- ❌ Don't duplicate information
- ❌ Don't include project-specific secrets

### Specs

- ✅ Start with requirements
- ✅ Design before implementation
- ✅ Track progress in tasks
- ✅ Update as you learn
- ❌ Don't over-specify
- ❌ Don't skip requirements

## Maintenance

### Regular Updates

- Review steering files quarterly
- Update when technology stack changes
- Add new patterns as they emerge
- Remove outdated guidance

### Version Control

- Commit steering file changes with clear messages
- Document why changes were made
- Review changes in pull requests

## Related Documentation

- [Main README](../README.md) - Project overview
- [Documentation](../docs/) - Detailed documentation
- [Contributing](../CONTRIBUTING.md) - Contribution guidelines

## Questions?

If you have questions about Kiro configuration:

1. Check the [Kiro documentation](https://kiro.dev/docs)
2. Ask in team chat
3. Create an issue in the repository

---

**Last Updated**: January 21, 2026  
**Project**: TelemetryFlow-Viz v0.3.3
