# Development Setup Guide

This guide will help you set up your local development environment for Template Sense.

## Prerequisites

- **Python 3.10+** (recommended: Python 3.10, 3.11, or 3.12)
- **Git** for version control
- **pip** for package management

## Initial Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Projects-with-Babajide/template-sense.git
cd template-sense
```

### 2. Create a Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

### 3. Install Development Dependencies

```bash
# Install package in editable mode with dev dependencies
pip install -e .[dev]
```

This will install:
- **Black** - Code formatter
- **Ruff** - Fast Python linter
- **Pytest** - Testing framework
- **pytest-cov** - Code coverage tool
- **pre-commit** - Git hook management
- All runtime dependencies (openpyxl, openai, anthropic, etc.)

### 4. Install Pre-commit Hooks

```bash
pre-commit install
```

This will automatically run Black, Ruff, and other checks before each commit.

---

## Development Tools

### Code Formatting (Black)

Black automatically formats your Python code to follow a consistent style.

```bash
# Format all files
black .

# Format specific directories
black src/ tests/

# Check formatting without modifying files
black --check .

# Show what would be changed
black --diff .
```

**Configuration:** Line length is set to 100 characters (see `pyproject.toml`).

### Linting (Ruff)

Ruff checks your code for errors, style issues, and potential bugs.

```bash
# Lint all files
ruff check .

# Auto-fix issues where possible
ruff check --fix .

# Lint specific directories
ruff check src/ tests/

# Show statistics
ruff check --statistics .
```

**Configuration:** See `[tool.ruff]` section in `pyproject.toml` for enabled rules.

### Testing (Pytest)

Pytest runs your test suite and generates coverage reports.

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_placeholder.py

# Run tests matching a pattern
pytest -k "test_adapter"

# Run with coverage report
pytest --cov

# Generate HTML coverage report
pytest --cov --cov-report=html
# Open htmlcov/index.html in browser to view
```

**Configuration:** See `[tool.pytest.ini_options]` section in `pyproject.toml`.

---

## Environment Variables

Template Sense requires environment variables for AI provider configuration.

### Local Development Setup

Create a `.env` file in the project root (never commit this file):

```bash
# .env
TEMPLATE_SENSE_AI_PROVIDER=openai  # or "anthropic"
TEMPLATE_SENSE_AI_MODEL=gpt-4      # Optional: provider-specific model
OPENAI_API_KEY=sk-...              # If using OpenAI
ANTHROPIC_API_KEY=sk-...           # If using Anthropic
TEMPLATE_SENSE_LOG_LEVEL=INFO      # Optional: DEBUG, INFO, WARNING, ERROR
```

The package will automatically load these variables using `python-dotenv`.

---

## Git Workflow

### Working on a Linear Ticket

1. **Fetch the ticket:**
   ```bash
   # Linear ticket: BAT-XX
   ```

2. **Create branch using exact name from Linear:**
   ```bash
   git checkout -b jideokus/bat-XX-description-from-linear
   ```

3. **Make your changes and commit:**
   ```bash
   git add .
   git commit -m "Description of changes

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>"
   ```

4. **Push and create PR:**
   ```bash
   git push -u origin jideokus/bat-XX-description-from-linear
   ```

### Pre-commit Hooks

When you commit, pre-commit hooks will automatically:
- Format code with Black
- Lint with Ruff (and auto-fix where possible)
- Remove trailing whitespace
- Ensure files end with newline
- Check YAML/TOML syntax
- Block large files

If hooks fail, fix the issues and commit again.

---

## Running Everything

To ensure your code is ready for review:

```bash
# Format code
black .

# Lint and auto-fix
ruff check --fix .

# Run tests with coverage
pytest --cov

# Or let pre-commit check everything
pre-commit run --all-files
```

---

## Troubleshooting

### Import Errors

If you get import errors after installing:
```bash
pip install -e .[dev] --force-reinstall
```

### Pre-commit Hook Failures

If pre-commit hooks fail:
1. Review the error messages
2. Fix the issues manually or let tools auto-fix
3. Stage the changes: `git add .`
4. Commit again

To skip hooks temporarily (not recommended):
```bash
git commit --no-verify
```

### Virtual Environment Issues

If your virtual environment is corrupted:
```bash
deactivate  # Exit current venv
rm -rf .venv  # Remove old venv
python3 -m venv .venv  # Create new venv
source .venv/bin/activate  # Activate
pip install -e .[dev]  # Reinstall
```

---

## Additional Resources

- **Project Documentation:** See [CLAUDE.md](../CLAUDE.md) for architecture details
- **Architecture:** See [architecture.md](architecture.md) for module structure
- **Linear Workspace:** [Projects with Babajide - Agentic Team](https://linear.app/projects-with-babajide)
- **GitHub Repository:** [template-sense](https://github.com/Projects-with-Babajide/template-sense)

---

## Questions?

For questions or issues, refer to:
1. This development guide
2. CLAUDE.md for project context
3. Linear tickets for task-specific info
4. Team in project channel
