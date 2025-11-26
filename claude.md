# Template Sense — Claude Project Context Document

**Version:** 1.0
**Last Updated:** 2025-11-25
**Project:** Tako AI Enablement — Invoice Template Extraction Package

---

## 1. Overview

### Business Domain
Template Sense is a **standalone, model-agnostic Python package** designed to extract structured metadata from Excel-based invoice templates and draft invoices. The package is built for **Tako**, a business that processes invoices in multiple languages and formats.

**Core Problem:**
Tako receives invoice templates from various clients in different languages (especially Japanese). These templates have:
- Header fields (invoice number, dates, shipper info, etc.) scattered across cells
- Line-item tables with varying column arrangements
- Non-English field labels that need translation and normalization

**Solution:**
Template Sense provides a hybrid extraction pipeline that:
1. Uses **heuristics** to identify candidate regions (headers, tables)
2. Leverages **AI** (provider-agnostic) to classify fields and columns semantically
3. **Translates** non-English labels to English
4. Performs **fuzzy matching** against Tako's canonical field dictionary
5. Returns a **normalized JSON structure** describing the template layout

### Primary User Types
1. **Tako Engineering Team** — Integrates Template Sense into their backend
2. **Automated Agents (Devin, Claude)** — Implement features, fix bugs, run tests
3. **Template Sense Maintainers** — Extend functionality, add new adapters

### Key Business Workflows Supported
- Upload an Excel template or draft invoice
- Extract header fields with cell positions
- Detect line-item table structure and column mappings
- Translate foreign language labels to English
- Map extracted fields to Tako's canonical field keys
- Return structured, normalized output for Tako's database ingestion
- Provide recovery events for unmapped or low-confidence fields

### Integration Points with Other Systems
- **Tako Backend:** Consumes Template Sense's normalized output via the public API
- **AI Providers:** OpenAI, Anthropic (future: others) for semantic analysis
- **Translation Services:** Dictionary-based translation (Tako provides dictionaries)
- **Excel Files:** `.xlsx` format (future: PDF, Word)

### What Template Sense Does NOT Do
- No receipt-to-invoice data mapping
- No UI logic or validation
- No direct interaction with Tako's database
- No PDF/Word support in this phase
- No business rule enforcement

---

## 2. Architecture & Patterns

### Folder Structure

```
template-sense/
├── src/
│   └── template_sense/
│       ├── __init__.py
│       ├── analyzer.py                  # Public API entry point
│       ├── errors.py                    # Custom exception hierarchy
│       ├── logging_utils.py             # Centralized logging
│       ├── adapters/
│       │   ├── __init__.py
│       │   ├── interface.py             # DocumentAdapter ABC
│       │   └── excel_adapter.py         # Excel-specific implementation
│       ├── extraction/
│       │   ├── __init__.py
│       │   ├── grid_normalizer.py       # Raw grid preprocessing
│       │   ├── header_candidates.py     # Heuristic header detection
│       │   ├── table_candidates.py      # Heuristic table detection
│       │   └── table_header_detection.py # Table header row detection
│       ├── ai_providers/
│       │   ├── __init__.py
│       │   ├── interface.py             # AIProvider ABC
│       │   ├── config.py                # Environment-based config
│       │   ├── payload_builder.py       # AI request payload construction
│       │   ├── openai_provider.py       # OpenAI implementation
│       │   └── anthropic_provider.py    # Anthropic implementation
│       ├── ai/
│       │   ├── __init__.py
│       │   ├── header_classification.py  # AI-based header field classification
│       │   └── table_column_classification.py # AI-based table column classification
│       ├── translation/
│       │   ├── __init__.py
│       │   └── field_translator.py      # Dictionary-based translation
│       ├── mapping/
│       │   ├── __init__.py
│       │   ├── fuzzy_matcher.py         # Fuzzy matching to canonical keys
│       │   └── canonical_template_aggregator.py # Canonical template builder
│       └── output/
│           ├── __init__.py
│           ├── normalized_output_builder.py # Public JSON output
│           └── recovery_event_logger.py     # Recovery/fallback tracking
├── tests/
│   ├── __init__.py
│   ├── test_*.py                        # Unit tests mirroring src/ structure
│   └── fixtures/                        # Test Excel files, mock data
├── docs/
│   ├── architecture.md
│   ├── dev-setup.md
│   └── tako_integration.md
├── pyproject.toml                       # Package metadata, dependencies, tooling config
├── .gitignore
├── .pre-commit-config.yaml
├── README.md
└── claude.md                            # This file
```

### Module Boundaries and Layer Dependencies

**Dependency Flow (bottom-up):**

1. **Adapters Layer** (`adapters/`)
   - Converts external file formats into normalized grid representations
   - Depends on: `errors.py`, `logging_utils.py`

2. **Extraction Layer** (`extraction/`)
   - Applies heuristics to identify candidate header/table regions
   - Depends on: `adapters/`, `errors.py`, `logging_utils.py`

3. **AI Providers Layer** (`ai_providers/`)
   - Provides provider-agnostic interface to external AI models
   - Depends on: `errors.py`, `logging_utils.py`

4. **AI Analysis Layer** (`ai/`)
   - Calls AI providers to semantically classify headers and table columns
   - Depends on: `ai_providers/`, `extraction/`, `errors.py`

5. **Translation Layer** (`translation/`)
   - Translates non-English labels using dictionaries
   - Depends on: `errors.py`, `logging_utils.py`

6. **Mapping Layer** (`mapping/`)
   - Fuzzy matches translated labels to canonical field keys
   - Aggregates all extracted data into canonical template structure
   - Depends on: `ai/`, `translation/`, `extraction/`

7. **Output Layer** (`output/`)
   - Builds the final normalized JSON output for Tako
   - Tracks recovery events for unmapped/low-confidence fields
   - Depends on: `mapping/`

8. **Public API** (`analyzer.py`)
   - Orchestrates all layers
   - Provides a single entry point for Tako
   - Depends on: All layers

**Key Principles:**
- Each layer should only import from layers below it (or sideways within the same layer)
- No circular dependencies
- Public API abstracts all internal complexity

### Communication Patterns

1. **Dependency Injection**
   - AI providers are injected via configuration
   - Adapters implement `DocumentAdapter` interface
   - No hard-coded provider logic in core modules

2. **Provider-Agnostic Design**
   - All AI logic uses the `AIProvider` abstract base class
   - Config-driven provider selection (`TEMPLATE_SENSE_AI_PROVIDER`)
   - New providers can be added without modifying core logic

3. **Dataclass-Based Data Transfer**
   - Structured data passed between layers via Python dataclasses
   - Example: `HeaderCandidateBlock`, `TableCandidateBlock`, `CanonicalHeaderField`

4. **Error Propagation**
   - Custom exception hierarchy (all inherit from `TemplateSenseError`)
   - Errors bubble up with context (file paths, field names)
   - Public API catches and wraps errors appropriately

5. **Recovery Events**
   - When extraction fails or confidence is low, log a recovery event
   - Never fail silently — always surface issues in `recovery_events` array

### External Service Integrations

**AI Providers:**
- OpenAI (via `openai` Python SDK)
- Anthropic (via `anthropic` Python SDK)
- Future: Cohere, Gemini, etc.

**Configuration:**
- Environment variables for provider selection and API keys
- Tako can override config by passing an explicit `AIConfig` object

---

## 3. Stack Best Practices

### Language-Specific Idioms and Conventions

**Python Version:**
- Target: Python 3.10+
- Use modern Python features (match statements, union types with `|`, etc.)

**Type Hints:**
- **Required** for all function signatures
- Use `from typing import Any, Dict, List, Optional` for older constructs
- Prefer `dict`, `list`, `str | None` for Python 3.10+
- Example:
  ```python
  def extract_headers(grid: list[list[Any]], threshold: float = 0.7) -> list[HeaderCandidateBlock]:
      ...
  ```

**Dataclasses:**
- Use `@dataclass` for structured data types
- Always include type annotations
- Example:
  ```python
  from dataclasses import dataclass
  from typing import Any

  @dataclass
  class HeaderCandidateBlock:
      row_index: int
      col_index: int
      value: Any
      score: float
  ```

**Abstract Base Classes:**
- Use `ABC` and `@abstractmethod` for interfaces
- Example:
  ```python
  from abc import ABC, abstractmethod

  class DocumentAdapter(ABC):
      @abstractmethod
      def read_grid(self, file_path: str) -> list[list[Any]]:
          raise NotImplementedError
  ```

### Framework-Specific Patterns

**Pytest:**
- Test files: `tests/test_<module_name>.py`
- Fixtures in `tests/conftest.py` or inline
- Use `pytest.raises` for exception testing
- Mock external dependencies (AI providers, file I/O)

**Openpyxl (Excel):**
- Use `load_workbook(file_path, data_only=True)` to read computed values
- Always handle missing cells gracefully (default to `None`)

**AI Provider SDKs:**
- Never call OpenAI/Anthropic APIs directly in core logic
- Always go through the `AIProvider` interface

### Dependency Injection Patterns

**AI Provider Injection:**
```python
from template_sense.ai_providers.interface import AIProvider
from template_sense.ai_providers.config import get_ai_provider, AIConfig

# Option 1: From environment
provider = get_ai_provider()

# Option 2: Explicit config (Tako's use case)
config = AIConfig(provider="openai", model="gpt-4", api_key="sk-...")
provider = get_ai_provider(config)

# Use provider
result = provider.analyze_template(payload)
```

**Adapter Injection:**
```python
from template_sense.adapters.interface import DocumentAdapter
from template_sense.adapters.excel_adapter import ExcelAdapter

adapter: DocumentAdapter = ExcelAdapter()
grid = adapter.read_grid("path/to/file.xlsx")
```

### Error Handling and Validation Patterns

**Custom Exceptions:**
- Always inherit from `TemplateSenseError`
- Raise specific exceptions (e.g., `ExtractionError`, `AIProviderError`)
- Include context in error messages:
  ```python
  raise FileValidationError(f"File does not exist: {file_path}")
  ```

**Validation:**
- Validate inputs early (at public API boundary)
- Use type hints + runtime checks for critical paths
- Example:
  ```python
  if not isinstance(field_dictionary, dict):
      raise MappingError("field_dictionary must be a dict")
  ```

**Graceful Degradation:**
- Prefer logging warnings + partial results over hard failures
- Use recovery events to track issues
- Example: If a field cannot be mapped, log it in `recovery_events` instead of crashing

---

## 4. Anti-Patterns

### Logging of Sensitive Data
- **Never log:**
  - API keys or secrets
  - Full file paths that might expose user info
  - Raw invoice data values (unless explicitly in debug mode with user consent)
- **Do log:**
  - Provider name and model (without key)
  - Row/column indices
  - Confidence scores
  - Generic error messages

### Hard-Coded Secrets
- **Never:**
  - Commit API keys to the repo
  - Hard-code provider names in core logic
  - Store secrets in `pyproject.toml` or config files
- **Always:**
  - Use environment variables for secrets
  - Document required env vars in `README.md` and `claude.md`
  - Use `.env` files locally (never committed)

### Non-Parameterized Data Queries
- While this package does not use SQL, the principle applies:
  - Always use structured data (dataclasses, dicts) for passing info
  - Never construct JSON payloads via string concatenation
  - Use `json.dumps()` with validated structures

### Direct Print Statements
- **Never:**
  - Use `print()` for logging or debugging
  - Output directly to stdout/stderr in library code
- **Always:**
  - Use `get_logger(__name__)` from `logging_utils.py`
  - Log at appropriate levels (DEBUG, INFO, WARNING, ERROR)

### Provider-Specific Logic in Core Modules
- **Never:**
  - Import `openai` or `anthropic` directly in `extraction/`, `mapping/`, or `output/`
  - Check provider name in non-provider modules
- **Always:**
  - Use the `AIProvider` interface
  - Keep provider-specific code in `ai_providers/<provider>_provider.py`

### Exposing Internal Types in Public API
- **Never:**
  - Return dataclasses directly from `analyzer.py`
  - Expose `HeaderCandidateBlock` or `TableCandidateBlock` in output
- **Always:**
  - Convert internal representations to JSON-serializable dicts
  - Use `normalized_output_builder.py` for output shaping

### Silently Swallowing Exceptions
- **Never:**
  - Catch exceptions without logging
  - Return `None` or empty dict when an error occurred
- **Always:**
  - Log errors with context
  - Re-raise or wrap in a higher-level exception
  - Add recovery events for non-fatal issues

---

## 5. Data Models

### Core Domain Entities

#### 1. Grid Representation
**Raw Grid:**
- `list[list[Any]]` — 2D array of cell values
- Rows and columns are 0-indexed
- Empty cells are `None`

**Normalized Grid:**
- Consistent dimensions (no ragged arrays)
- Missing cells filled with `None`

#### 2. Header Fields

**HeaderCandidateBlock (Heuristic Output):**
```python
@dataclass
class HeaderCandidateBlock:
    row_index: int
    col_index: int
    value: Any
    label: Any | None
    score: float  # Heuristic confidence
```

**ClassifiedHeaderField (AI Output):**
```python
@dataclass
class ClassifiedHeaderField:
    row_index: int
    col_index: int
    raw_label: Any
    inferred_role: str | None  # e.g., "invoice_number"
    value: Any
    model_confidence: float | None
    metadata: dict[str, Any] | None
```

**CanonicalHeaderField (Final Mapped Output):**
```python
@dataclass
class CanonicalHeaderField:
    canonical_key: str | None  # e.g., "invoice_number"
    raw_label: Any
    translated_label: str | None
    value: Any
    location: dict  # {"row": int, "col": int}
    confidence: float
    match_score: float | None  # Fuzzy match score
```

#### 3. Tables

**TableCandidateBlock (Heuristic Output):**
```python
@dataclass
class TableCandidateBlock:
    start_row: int
    end_row: int
    start_col: int
    end_col: int
    grid: list[list[Any]]
    score: float
```

**TableHeader (Detected Header Row):**
```python
@dataclass
class TableHeader:
    row_index: int
    column_values: list[Any]
```

**ClassifiedTableColumn (AI Output):**
```python
@dataclass
class ClassifiedTableColumn:
    column_index: int
    raw_header_value: Any
    inferred_role: str | None  # e.g., "description", "quantity"
    model_confidence: float | None
    sample_values: list[Any] | None
```

**CanonicalTable (Final Mapped Output):**
```python
@dataclass
class CanonicalTable:
    table_index: int
    location: dict  # {"start_row", "end_row", "start_col", "end_col"}
    columns: list[CanonicalTableColumn]
    line_items: list[CanonicalLineItem]
```

**CanonicalTableColumn:**
```python
@dataclass
class CanonicalTableColumn:
    canonical_key: str | None  # e.g., "quantity"
    column_index: int
    raw_header: Any
    translated_header: str | None
    confidence: float
    match_score: float | None
```

**CanonicalLineItem:**
```python
@dataclass
class CanonicalLineItem:
    row_index: int
    values: dict[str, Any]  # Keyed by canonical_key
    confidence: float
```

#### 4. Canonical Template (Aggregated)

**CanonicalTemplate:**
```python
@dataclass
class CanonicalTemplate:
    sheet_name: str
    headers: list[CanonicalHeaderField]
    tables: list[CanonicalTable]
    unknown_fields: list[dict]  # Fields that couldn't be mapped
```

### Canonical Mapping Flow

**Pipeline:**
```
1. Raw Excel → Grid (Adapter)
2. Grid → HeaderCandidateBlock + TableCandidateBlock (Heuristics)
3. Candidates → ClassifiedHeaderField + ClassifiedTableColumn (AI)
4. Classified → Translated labels (Translation)
5. Translated → Fuzzy matched to canonical keys (Mapping)
6. Canonical → CanonicalTemplate (Aggregator)
7. CanonicalTemplate → Normalized JSON Output (Output Builder)
```

**Canonical Field Keys (Tako's Dictionary):**
- Examples: `invoice_number`, `invoice_date`, `shipper_name`, `consignee_name`, `description`, `quantity`, `unit_price`, `total`
- Tako provides a `field_dictionary: dict[str, list[str]]` mapping canonical keys to known variants:
  ```python
  {
      "invoice_number": ["invoice no", "invoice number", "inv no", "請求書番号"],
      "shipper_name": ["shipper", "sender", "exporter", "荷送人"],
  }
  ```

### Validation Rules

1. **File Validation:**
   - Must be `.xlsx` format
   - Must exist and be readable
   - Must contain at least one sheet

2. **Grid Validation:**
   - Grid must have at least 1 row and 1 column
   - Cells can be `None`, but not entire grid

3. **Field Dictionary Validation:**
   - Must be a `dict[str, list[str]]`
   - Keys are canonical field names
   - Values are lists of known variants (at least 1 per key)

4. **Confidence Thresholds:**
   - Heuristic confidence: 0.0–1.0
   - AI confidence: 0.0–1.0 (provider-dependent)
   - Fuzzy match score: 0.0–100.0 (from RapidFuzz)
   - Recommended minimum for auto-mapping: 80.0

5. **Recovery Events:**
   - Triggered when:
     - Confidence below threshold
     - No canonical key match found
     - AI provider error (fallback to heuristics)
     - Translation missing
   - Logged in `recovery_events` array for Tako to review

### Database Migration Patterns
- Not applicable — Template Sense does not manage a database
- Tako is responsible for ingesting the normalized output into their database

---

## 6. Configuration, Security, and Authentication

### Environment Variable Management

**Required Environment Variables:**

1. **AI Provider Configuration:**
   - `TEMPLATE_SENSE_AI_PROVIDER` (string)
     - Values: `"openai"`, `"anthropic"`
     - Default: None (must be set)

   - `TEMPLATE_SENSE_AI_MODEL` (string, optional)
     - Examples: `"gpt-4"`, `"claude-3-sonnet-20240229"`
     - Default: Provider-specific default

2. **API Keys:**
   - `OPENAI_API_KEY` (string, if using OpenAI)
   - `ANTHROPIC_API_KEY` (string, if using Anthropic)

**Optional Environment Variables:**
- `TEMPLATE_SENSE_LOG_LEVEL` (string)
  - Values: `DEBUG`, `INFO`, `WARNING`, `ERROR`
  - Default: `INFO`

**Example `.env` file (never committed):**
```bash
TEMPLATE_SENSE_AI_PROVIDER=openai
TEMPLATE_SENSE_AI_MODEL=gpt-4-turbo
OPENAI_API_KEY=sk-...
TEMPLATE_SENSE_LOG_LEVEL=INFO
```

**Loading Environment Variables:**
- Use `python-dotenv` to load `.env` in local dev
- In production, Tako should set environment variables directly
- Example:
  ```python
  from dotenv import load_dotenv
  load_dotenv()
  ```

### Secrets Handling

**1Password / Vaults:**
- Not applicable at the library level
- Tako is responsible for secure storage of API keys
- Template Sense only reads from environment variables

**Best Practices:**
- Never log API keys (even partially)
- Never include keys in error messages
- Never commit `.env` files
- Document all required secrets in `README.md`

### Authentication / Authorization Flow

**AI Provider Authentication:**
1. Template Sense reads API key from environment
2. AI provider SDK handles authentication (OpenAI, Anthropic)
3. No custom auth logic in Template Sense

**Tako Integration:**
- Template Sense has no user authentication
- Tako's backend is responsible for:
  - User authentication
  - File upload authorization
  - Rate limiting
  - API key rotation

### API Security Patterns

**Input Validation:**
- Validate file paths (no directory traversal)
- Validate field dictionary structure
- Validate AI config (no injection attacks)

**Error Messages:**
- Generic errors to external callers
- Detailed errors in logs (internal only)
- Never expose API keys or sensitive data in exceptions

**Rate Limiting:**
- Not implemented in Template Sense
- Tako should implement rate limiting on their API

**Timeouts:**
- AI provider calls have configurable timeouts
- Default: 30 seconds per AI request
- Prevents hanging on slow responses

### Compliance Requirements

**GDPR / Data Privacy:**
- Template Sense does not store user data
- Invoice data is processed in-memory only
- Tako is responsible for data retention policies

**Data Sent to AI Providers:**
- Cell values (may contain PII — e.g., names, addresses)
- Field labels (template structure)
- Tako should review their AI provider's privacy policy

**Logging:**
- No PII logged by default
- In DEBUG mode, cell values may appear in logs (use cautiously)

---

## 7. Testing Strategy

### Unit Tests
- Located in `tests/test_<module_name>.py`
- Must mock external dependencies (AI providers, file I/O)
- Coverage target: 80%+
- Run: `pytest`

### Integration Tests
- Separate repo: `template-sense-integration-tests`
- Tests full pipeline with real Excel files
- Uses mocked AI responses (no live API calls in CI)

### Fixtures
- Test Excel files in `tests/fixtures/`
- Mock AI responses in `tests/fixtures/mock_ai_responses.json`

---

## 8. Development Workflow

### Setting Up the Environment
1. Clone the repo
2. Create virtual environment: `python3 -m venv .venv`
3. Activate: `source .venv/bin/activate`
4. Install dev dependencies: `pip install -e .[dev]`
5. Install pre-commit hooks: `pre-commit install`
6. Run tests: `pytest`

### Code Quality Tools
- **Black:** Auto-format code (`black .`)
- **Ruff:** Lint code (`ruff check .`)
- **Pytest:** Run tests (`pytest`)
- **Pre-commit hooks:** Auto-run Black + Ruff on commit

### Git Workflow
- Main branch: `main`
- Feature branches: **MUST use the branch name from Linear ticket**
  - Each Linear issue has a `gitBranchName` field (e.g., `jideokus/bat-10-task-7-create-claudemd-claude-project-context-document`)
  - When working on a Linear ticket, always create/checkout the branch with the exact name from Linear
  - This ensures proper integration between Linear and GitHub
- Commit messages: Follow conventional commits format
- Pull requests: Required for all changes

---

## 9. How Claude Should Use This Document

### Working with Linear Tickets

**IMPORTANT: When assigned a Linear ticket, you MUST:**
1. Fetch the ticket details using the Linear MCP integration
2. Extract the `gitBranchName` field from the ticket
3. Create or checkout that exact branch name before making any changes
4. Update the ticket status to "In Progress" when you start work
5. Update the ticket status to "Done" when you complete the work
6. Add a comment to the ticket summarizing what was done

**Example workflow:**
```
1. User: "Work on BAT-15"
2. Claude: Fetch issue BAT-15 from Linear
3. Claude: Extract gitBranchName (e.g., "jideokus/bat-15-implement-excel-adapter")
4. Claude: Create/checkout branch: git checkout -b jideokus/bat-15-implement-excel-adapter
5. Claude: Update Linear status to "In Progress"
6. Claude: Implement the feature following this document's guidelines
7. Claude: Update Linear status to "Done"
8. Claude: Add completion comment to Linear ticket
```

**Never:**
- Create your own branch names when working on Linear tickets
- Skip updating the Linear ticket status
- Forget to add a completion comment

### When Implementing a New Feature

1. Review the relevant section in **Architecture & Patterns**
2. Check **Data Models** for required types
3. Follow **Stack Best Practices** for implementation
4. Avoid **Anti-Patterns**
5. Add unit tests following **Testing Strategy**

### When Fixing a Bug

1. Identify which layer the bug is in (adapters, extraction, AI, etc.)
2. Check **Data Models** to understand expected data flow
3. Review **Error Handling and Validation Patterns**
4. Add a regression test

### When Answering Questions

1. Reference **Overview** for business context
2. Reference **Architecture & Patterns** for technical context
3. Reference **Configuration, Security, and Authentication** for operational context

### When Refactoring

1. Ensure changes align with **Module Boundaries and Layer Dependencies**
2. Maintain **Communication Patterns**
3. Update relevant sections of this document if architecture changes

---

## 10. Future Enhancements

**Planned:**
- PDF adapter
- Word document adapter
- Additional AI providers (Cohere, Gemini)
- Improved table detection heuristics
- Multi-sheet support
- Template caching

**Not Planned:**
- UI/frontend
- Database management
- Receipt-to-invoice mapping
- Business rule enforcement

---

## 11. Contact and Support

**Primary Maintainer:** Babajide (Tako AI Enablement Team)
**Repository:** [Link to GitHub repo once created]
**Linear Workspace:** Projects with Babajide → Agentic Team
**Project:** Tako AI Enablement

**For Questions:**
- Refer to this document first
- Check `docs/` folder
- Review relevant issue in Linear
- Ask the team in project channel

---

**End of Document**
