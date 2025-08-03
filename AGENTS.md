# Basic Instructions

- Follow all instructions in the .github/copilot-instructions.md file.

# Before Checking In Code

- Fix all code formatting and quality issues in the entire codebase.
- Ensure all new code is covered by appropriate unit tests.

## Python

Fix all Python formatting and linting issues.

### Steps:

2. **Format with ruff**: `uv run ruff format .`
3. **Lint with ruff**: `uv run ruff check . --output-format=github`
4. **Run unit tests**: `uv run pytest tests`

## General Process:

1. Run automated formatters first
2. Fix remaining linting issues manually
3. Resolve type checking errors
4. Verify all tools pass with no errors
5. Review changes before committing

## Common Issues:

- Import order conflicts between tools
- Line length violations
- Unused imports/variables
- Type annotation requirements
- Missing return types
- Inconsistent quotes/semicolons
