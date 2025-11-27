# Template Sense — Claude Project Context Document

**Version:** 1.0
**Last Updated:** 2025-11-25
**Project:** Tako AI Enablement — Invoice Template Extraction Package

---

## 1. Overview

### Business Domain
Template Sense is a **standalone, model-agnostic Python package** that extracts structured metadata from Excel-based invoice templates for **Tako**, a business processing invoices in multiple languages (especially Japanese).

**Solution:**
1. Uses **heuristics** to identify candidate regions (headers, tables)
2. Leverages **AI** (provider-agnostic) to classify fields and columns semantically
3. **Translates** non-English labels to English
4. Performs **fuzzy matching** against Tako's canonical field dictionary
5. Returns a **normalized JSON structure** describing the template layout

### Primary User Types
1. **Tako Engineering Team** — Integrates Template Sense into their backend
2. **Automated Agents (Devin, Claude)** — Implement features, fix bugs, run tests

### What Template Sense Does NOT Do
- No receipt-to-invoice data mapping
- No UI logic or validation
- No direct interaction with Tako's database
- No PDF/Word support in this phase

---

## 2. Architecture & Patterns

### Folder Structure

```
template-sense/
├── src/template_sense/          # Main package (use underscores)
│   ├── analyzer.py              # Public API entry point
│   ├── errors.py                # Custom exception hierarchy
│   ├── adapters/                # Excel/file format readers
│   ├── extraction/              # Heuristic header/table detection
│   ├── ai_providers/            # AI provider abstraction (OpenAI, Anthropic)
│   ├── ai/                      # AI-based field/column classification
│   ├── translation/             # Dictionary-based translation
│   ├── mapping/                 # Fuzzy matching to canonical keys
│   └── output/                  # JSON output builder
├── tests/                       # Unit tests
└── docs/                        # Detailed documentation
```

### Module Boundaries and Layer Dependencies

**Dependency Flow (bottom-up):**
1. **Adapters** → Converts files to normalized grids
2. **Extraction** → Heuristic detection of headers/tables
3. **AI Providers** → Provider-agnostic AI interface
4. **AI Analysis** → Semantic classification
5. **Translation** → Label translation
6. **Mapping** → Fuzzy matching to canonical keys
7. **Output** → JSON output builder
8. **Public API** → Orchestrates all layers

**Key Principles:**
- Each layer only imports from layers below it
- No circular dependencies
- Provider-agnostic design throughout

---

## 3. Stack Best Practices

### Language-Specific Idioms

**Python Version:** 3.10+

**Type Hints:** Required for all functions
```python
def extract_headers(grid: list[list[Any]], threshold: float = 0.7) -> list[HeaderCandidateBlock]:
    ...
```

**Dataclasses:** Use for all structured data
```python
@dataclass
class HeaderCandidateBlock:
    row_index: int
    col_index: int
    value: Any
    score: float
```

**Abstract Base Classes:** Use for interfaces
```python
from abc import ABC, abstractmethod

class DocumentAdapter(ABC):
    @abstractmethod
    def read_grid(self, file_path: str) -> list[list[Any]]:
        raise NotImplementedError
```

### Constants Management

**Central Constants File:** `src/template_sense/constants.py`

All configuration values must be defined and imported from this module:
```python
from template_sense.constants import (
    DEFAULT_CONFIDENCE_THRESHOLD,
    DEFAULT_AUTO_MAPPING_THRESHOLD,
    DEFAULT_MAX_HEADER_ROWS,
    SUPPORTED_FILE_EXTENSIONS,
)
```

**What belongs in constants.py:**
- File extensions and format specifications
- Default thresholds (confidence, scoring, fuzzy matching)
- Extraction limits (max rows, min columns, etc.)
- Environment variable names
- Timeouts and performance limits
- Provider names and configurations

**Never hard-code these values** in other modules. Always import from `constants.py`.

### Framework-Specific Patterns

**Pytest:** `tests/test_<module_name>.py`, mock external dependencies
**Openpyxl:** `load_workbook(file_path, data_only=True)`
**AI Providers:** Always use `AIProvider` interface, never import directly

---

## 4. Anti-Patterns

### ❌ NEVER Do This:
1. **Log sensitive data** — No API keys, invoice values, full file paths
2. **Hard-code secrets** — Use environment variables only
3. **Use print()** — Use `get_logger(__name__)` from `logging_utils.py`
4. **Import AI providers directly** — Use `AIProvider` interface
5. **Return internal dataclasses from public API** — Convert to JSON dicts
6. **Swallow exceptions silently** — Always log with context
7. **Hard-code configuration values** — Use constants from `src/template_sense/constants.py`

### ✅ ALWAYS Do This:
1. **Validate inputs early** at public API boundary
2. **Use dependency injection** for providers/adapters
3. **Log recovery events** for non-fatal issues
4. **Provider-agnostic design** — No provider checks in core logic
5. **Import constants from `constants.py`** — All thresholds, limits, file extensions, environment variable names, etc. should be imported from `src/template_sense/constants.py`

---

## 5. Data Models

### Core Domain Entities

**Pipeline Flow:**
```
Raw Excel → Grid → HeaderCandidateBlock/TableCandidateBlock →
ClassifiedHeaderField/ClassifiedTableColumn → Translated labels →
Fuzzy matched → CanonicalTemplate → Normalized JSON
```

**Key Dataclasses:**
- `HeaderCandidateBlock` — Heuristic output
- `ClassifiedHeaderField` — AI output
- `CanonicalHeaderField` — Final mapped output
- `TableCandidateBlock` — Heuristic table detection
- `CanonicalTemplate` — Final aggregated output

**Canonical Field Keys Example:**
```python
{
    "invoice_number": ["invoice no", "inv no", "請求書番号"],
    "shipper_name": ["shipper", "sender", "荷送人"],
}
```

**Validation Rules:**
- Must be `.xlsx` or `.xls` format (Excel files only)
- Grid must have at least 1 row and 1 column
- Confidence thresholds: 0.0–1.0 (heuristic/AI), 0.0–100.0 (fuzzy match)
- Recommended auto-mapping threshold: 80.0

---

## 6. Configuration, Security, and Authentication

### Environment Variable Management

**Required:**
```bash
TEMPLATE_SENSE_AI_PROVIDER=openai  # or "anthropic"
OPENAI_API_KEY=sk-...              # if using OpenAI
ANTHROPIC_API_KEY=sk-...           # if using Anthropic
```

**Optional:**
```bash
TEMPLATE_SENSE_AI_MODEL=gpt-4      # Provider-specific model
TEMPLATE_SENSE_LOG_LEVEL=INFO      # DEBUG, INFO, WARNING, ERROR
```

### Secrets Handling
- Never log API keys (even partially)
- Never commit `.env` files
- Use `python-dotenv` for local dev

### API Security Patterns
- Validate file paths (no directory traversal)
- Generic errors to external callers
- Timeouts: 30 seconds per AI request (default)

---

## 7. Testing Strategy

### Unit Tests
- Located in `tests/test_<module_name>.py`
- Must mock external dependencies (AI providers, file I/O)
- Coverage target: 80%+
- Run: `pytest`

### Fixtures
- Test Excel files in `tests/fixtures/`
- Mock AI responses in `tests/fixtures/mock_ai_responses.json`

---

## 8. Development Workflow

### Setting Up the Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pre-commit install
pytest
```

### Code Quality Tools
- **Black:** `black .`
- **Ruff:** `ruff check .`
- **Pytest:** `pytest`

### Git Workflow
- Main branch: `main`
- Feature branches: **MUST use the branch name from Linear ticket**
- Commit messages: Follow conventional commits format

---

## 9. How Claude Should Use This Document

### When Implementing a New Feature
1. Review **Architecture & Patterns**
2. Check **Data Models** for required types
3. Follow **Stack Best Practices**
4. Avoid **Anti-Patterns**
5. Add unit tests

### When Fixing a Bug
1. Identify which layer the bug is in
2. Check **Data Models** to understand expected flow
3. Add a regression test

---

## 10. Future Enhancements

**Planned:** PDF adapter, Word adapter, additional AI providers, multi-sheet support
**Not Planned:** UI/frontend, database management, receipt-to-invoice mapping

---

## 11. Contact and Support

**Primary Maintainer:** Babajide (Tako AI Enablement Team)
**Repository:** https://github.com/Projects-with-Babajide/template-sense
**Linear Workspace:** Projects with Babajide
**Linear Team:** Agentic Team
**Linear Project:** Tako AI Enablement

**Linear Integration Details:**
- **Team Name:** `Agentic Team` (use this exact name when filtering issues by team)
- **Project Name:** `Tako AI Enablement` (use this exact name when filtering issues by project)
- **Issue Pattern:** `BAT-{number}` (e.g., BAT-12, BAT-15)

**For Detailed Documentation:**
- Architecture details → See folder structure above + code
- Development setup → See Section 8
- Tako integration → See Section 1

---

**End of Document**
