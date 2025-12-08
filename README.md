# Template Sense

AI-powered invoice template extraction library for structured metadata analysis.

Template Sense analyzes Excel-based invoice templates using heuristics and AI to extract structured metadata, supporting multi-language translation and fuzzy matching against canonical field dictionaries.

## Installation

### From PyPI (Recommended)

```bash
# Latest version
pip install template-sense

# Specific version
pip install template-sense==0.1.1
```

### From GitHub

```bash
# Latest release
pip install git+https://github.com/Projects-with-Babajide/template-sense.git@main

# Specific release tag
pip install git+https://github.com/Projects-with-Babajide/template-sense.git@v0.1.1
```

### For Development

```bash
git clone https://github.com/Projects-with-Babajide/template-sense.git
cd template-sense
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .[dev]
```

## AI Configuration

Template Sense requires an AI provider for semantic field classification.

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `TEMPLATE_SENSE_AI_PROVIDER` | Yes | AI provider to use: `openai` or `anthropic` | None |
| `OPENAI_API_KEY` | If using OpenAI | Your OpenAI API key | None |
| `ANTHROPIC_API_KEY` | If using Anthropic | Your Anthropic API key | None |
| `TEMPLATE_SENSE_AI_MODEL` | No | Override default model (e.g., `gpt-4o`, `claude-3-sonnet-20240229`) | `gpt-4o` for OpenAI, `claude-3-sonnet-20240229` for Anthropic |
| `TEMPLATE_SENSE_LOG_LEVEL` | No | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR` | `INFO` |

### Configuration Methods

**Option 1: Environment Variables (Recommended for Production)**

```bash
export TEMPLATE_SENSE_AI_PROVIDER=openai
export OPENAI_API_KEY=sk-your-api-key-here
```

**Option 2: .env File (Recommended for Development)**

Create a `.env` file in your project root:

```
TEMPLATE_SENSE_AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key-here
TEMPLATE_SENSE_LOG_LEVEL=DEBUG
```

**Option 3: Programmatic Configuration**

```python
from template_sense.analyzer import extract_template_structure
from template_sense.ai_providers.config import AIConfig

ai_config = AIConfig(
    provider="openai",
    api_key="sk-your-api-key-here",
    model="gpt-4o",  # Optional: override default
    timeout_seconds=120  # Optional: override default timeout
)

result = extract_template_structure("template.xlsx", field_dictionary, ai_config=ai_config)
```

## Quick Start

### Basic Usage

```python
from template_sense.analyzer import extract_template_structure

# Define your canonical field dictionary
# Keys are YOUR canonical field names, values are expected labels in templates
field_dictionary = {
    "headers": {
        "invoice_number": "Invoice number",
        "shipper": "Shipper",
        "consignee": "Consignee",
        "invoice_date": "Invoice date",
        "due_date": "Due date",
    },
    "columns": {
        "product_name": "Product name",
        "quantity": "Quantity",
        "price": "Price",
        "amount": "Amount",
    }
}

# Extract template structure
result = extract_template_structure("path/to/template.xlsx", field_dictionary)

# Access matched headers
for header in result["normalized_output"]["headers"]["matched"]:
    print(f"{header['canonical_key']}: {header['value']} (confidence: {header['ai_confidence']})")

# Access matched table columns
for table in result["normalized_output"]["tables"]:
    for column in table["columns"]:
        print(f"Column: {column['canonical_key']} at position {column['column_position']}")

# Check recovery events (warnings, low confidence fields, etc.)
for event in result["recovery_events"]:
    print(f"[{event['severity']}] {event['message']}")
```

### With Error Handling

```python
from template_sense.analyzer import extract_template_structure
from template_sense.errors import (
    FileValidationError,
    UnsupportedFileTypeError,
    AIProviderError,
    InvalidFieldDictionaryError,
)

field_dictionary = {
    "headers": {"invoice_number": "Invoice number"},
    "columns": {"product_name": "Product name"}
}

try:
    result = extract_template_structure("template.xlsx", field_dictionary)

    # Process results
    matched_headers = result["normalized_output"]["headers"]["matched"]
    print(f"Found {len(matched_headers)} matched headers")

except FileValidationError as e:
    print(f"File error: {e}")
    # Handle: Check file exists, has correct permissions

except UnsupportedFileTypeError as e:
    print(f"Unsupported format: {e}")
    # Handle: Only .xlsx and .xls files are supported

except AIProviderError as e:
    print(f"AI provider error: {e}")
    # Handle: Check API key, network connection, provider status

except InvalidFieldDictionaryError as e:
    print(f"Invalid field dictionary: {e}")
    # Handle: Check dictionary has 'headers' and 'columns' keys
```

## Output Structure

The `extract_template_structure()` function returns a dictionary with three main sections:

### Example Output

```json
{
  "normalized_output": {
    "version": "1.0",
    "sheet_name": "Sheet1",
    "headers": {
      "matched": [
        {
          "canonical_key": "invoice_number",
          "original_label": "請求書番号",
          "translated_label": "Invoice Number",
          "value": "INV-2024-001",
          "row_index": 2,
          "col_index": 1,
          "ai_confidence": 0.95,
          "fuzzy_match_score": 88.5,
          "metadata": {
            "ai_provider": "openai",
            "ai_model": "gpt-4o"
          }
        }
      ],
      "unmatched": [
        {
          "original_label": "備考",
          "translated_label": "Notes",
          "value": "Sample note",
          "row_index": 5,
          "col_index": 1,
          "ai_confidence": 0.82,
          "fuzzy_match_score": 45.2
        }
      ]
    },
    "tables": [
      {
        "table_block_index": 0,
        "row_start": 10,
        "row_end": 15,
        "col_start": 1,
        "col_end": 5,
        "columns": [
          {
            "canonical_key": "product_name",
            "original_label": "商品名",
            "translated_label": "Product Name",
            "column_position": 0,
            "sample_values": ["Item A", "Item B", "Item C"],
            "ai_confidence": 0.92,
            "fuzzy_match_score": 85.0
          }
        ],
        "line_items": [
          {
            "row_index": 11,
            "line_number": 1,
            "columns": {
              "product_name": "Item A",
              "quantity": 10,
              "price": 100.0,
              "amount": 1000.0
            },
            "is_subtotal": false,
            "ai_confidence": 0.88
          }
        ],
        "heuristic_score": 0.85,
        "detected_pattern": "standard_table"
      }
    ],
    "summary": {
      "total_header_fields": 8,
      "matched_header_fields": 6,
      "unmatched_header_fields": 2,
      "total_tables": 1,
      "total_line_items": 5
    }
  },
  "recovery_events": [
    {
      "severity": "WARNING",
      "category": "low_confidence",
      "message": "Field 'shipper' matched with low AI confidence: 0.65",
      "context": {
        "field_name": "shipper",
        "ai_confidence": 0.65,
        "fuzzy_match_score": 72.5
      }
    }
  ],
  "metadata": {
    "sheet_name": "Sheet1",
    "extraction_timestamp": "2024-11-25T12:34:56Z",
    "pipeline_version": "1.0"
  }
}
```

### Field Descriptions

| Field Path | Type | Description |
|------------|------|-------------|
| `normalized_output.version` | string | Output schema version (currently `1.0`) |
| `normalized_output.sheet_name` | string | Name of the Excel sheet analyzed |
| `normalized_output.headers.matched` | array | Headers successfully mapped to canonical keys |
| `normalized_output.headers.unmatched` | array | Headers detected but not mapped (low fuzzy match score) |
| `normalized_output.tables` | array | Detected tables with columns and line items |
| `normalized_output.summary` | object | Statistics about extraction results |
| `recovery_events` | array | Warnings and recovery information (non-fatal issues) |
| `metadata.sheet_name` | string | Sheet name from Excel file |
| `metadata.extraction_timestamp` | string | ISO 8601 timestamp of extraction |
| `metadata.pipeline_version` | string | Pipeline version used for extraction |

**Header/Column Fields:**
- `canonical_key`: Your canonical field name (from field dictionary)
- `original_label`: Raw text from template (may be non-English)
- `translated_label`: English translation of original label
- `value`: Associated data value (for headers only)
- `row_index`, `col_index`: 1-based Excel coordinates
- `ai_confidence`: AI classification confidence (0.0-1.0)
- `fuzzy_match_score`: Fuzzy matching score (0.0-100.0)

**Recovery Events:**
- `severity`: `INFO`, `WARNING`, or `ERROR`
- `category`: Event type (e.g., `low_confidence`, `translation_failure`)
- `message`: Human-readable description
- `context`: Additional context data

## Limitations

- **Excel files only**: Supports `.xlsx` and `.xls` formats. PDF and Word documents are not supported.
- **Single sheet processing**: Analyzes only the first sheet in the workbook.
- **Structure extraction only**: Extracts template structure and field locations, but does not map receipt data to invoices.
- **AI provider dependency**: Requires an active API key for OpenAI or Anthropic.
- **English translation**: Non-English labels are translated to English for fuzzy matching.

## Troubleshooting

### Common Errors

**`FileValidationError: File validation failed: File does not exist`**
- **Cause**: File path is invalid or file doesn't exist
- **Fix**: Verify file path is correct and file exists

**`UnsupportedFileTypeError: Unsupported file type: .csv. Expected: .xlsx, .xls`**
- **Cause**: File format is not supported
- **Fix**: Convert file to `.xlsx` or `.xls` format

**`AIProviderError: AI provider 'openai' request failed`**
- **Cause**: API key missing, invalid, or network issue
- **Fix**:
  - Verify `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` environment variable is set
  - Check API key is valid and has sufficient quota
  - Verify network connectivity to provider

**`InvalidFieldDictionaryError: Invalid field dictionary: Missing required key 'headers'`**
- **Cause**: Field dictionary structure is incorrect
- **Fix**: Ensure dictionary has both `"headers"` and `"columns"` keys:
  ```python
  field_dictionary = {
      "headers": { ... },
      "columns": { ... }
  }
  ```

**Low confidence warnings in `recovery_events`**
- **Cause**: Template labels don't closely match field dictionary values
- **Fix**:
  - Review unmatched fields and update field dictionary with alternative labels
  - Check for typos or non-standard terminology in templates
  - Consider lowering fuzzy match threshold (default: 80.0) for more lenient matching

## Requirements

- Python 3.10+
- OpenAI API key (if using OpenAI provider)
- Anthropic API key (if using Anthropic provider)

## License

MIT
