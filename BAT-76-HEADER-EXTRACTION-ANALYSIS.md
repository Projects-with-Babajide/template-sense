# Template Sense Header Extraction Implementation Analysis

## Executive Summary

The header extraction pipeline in template-sense is a sophisticated two-phase system:

1. **Heuristic Detection Phase** (`header_candidates.py`): Identifies candidate header blocks using pattern matching and metadata keyword detection
2. **AI Classification Phase** (downstream in `header_classification.py`): Semantically classifies detected headers and adds multi-cell pairing information

This analysis covers the current implementation and integration points for the proposed multi-cell label/value pairing logic.

---

## Part 1: Current Implementation Details

### 1.1 Core Data Structure: `HeaderCandidateBlock`

**Location**: `src/template_sense/extraction/header_candidates.py` (lines 103-132)

```python
@dataclass
class HeaderCandidateBlock:
    row_start: int              # First row (1-based, Excel convention)
    row_end: int                # Last row (1-based, inclusive)
    col_start: int              # First column (1-based)
    col_end: int                # Last column (1-based)
    content: list[tuple[int, int, Any]]  # All non-empty cells: (row, col, value)
    label_value_pairs: list[tuple[str | None, Any, int, int]]  # Extracted pairs: (label, value, row, col)
    score: float                # Confidence 0.0-1.0
    detected_pattern: str       # Detection method (e.g., "key_value_patterns")
```

**Key Point**: The `label_value_pairs` currently extracts simple label/value pairs from single cells using `_extract_label_value_from_cell()`, which only handles colon-delimited patterns within a single cell.

### 1.2 Current Label/Value Extraction: `_extract_label_value_from_cell()`

**Location**: Lines 216-250

Current behavior:
- Takes a single cell value
- Splits on colon (`:`) if present
- Returns `(label, value)` tuple
- Returns `(None, value)` if no colon found

**Limitation**: Only works for same-cell patterns like `"Invoice Number: 12345"`. Does NOT detect multi-cell patterns where label and value are in adjacent cells.

### 1.3 Cell Density Analysis

**Location**: Lines 253-268

```python
def _calculate_cell_density(row: list[Any]) -> float:
    """Calculate ratio of non-empty cells to total cells."""
```

Used in scoring to identify sparse metadata rows (typically 10-70% filled) vs. dense table data (>85% filled).

### 1.4 Header Detection Pipeline

**Main Entry Point**: `detect_header_candidate_blocks()` (lines 597-710)

Two-phase detection approach:

**Phase A: Scoring Heuristics** (when `table_blocks=None`):
1. Scan every row in grid
2. Score each row: `score_row_as_header_candidate(row, row_index)`
3. Filter rows with score >= min_score (default 0.3)
4. Cluster nearby rows into blocks

**Phase B: Table Exclusion** (when `table_blocks` provided):
1. Get all non-table rows
2. Cluster them into blocks
3. Bypass scoring heuristics

**Scoring Criteria** (from `score_row_as_header_candidate()`):
- +0.6 if 2+ cells have key-value patterns
- +0.4 if 1 cell has key-value pattern
- +0.5 if 2+ cells have metadata keywords
- +0.3 if 1 cell has metadata keyword
- +0.2 if contains substantial text
- +0.2 if density 10-70% (sparse like metadata)
- +0.1 if very sparse (<10%)
- -0.3 if very dense (>85%, likely table)

### 1.5 Constants

**Location**: `src/template_sense/constants.py`

Relevant constants:
```python
DEFAULT_ADJACENT_CELL_RADIUS = 3  # Line 38
```

This constant is used downstream when building AI payloads to extract context from adjacent cells.

---

## Part 2: Downstream Data Flow

### 2.1 Summary Builder Integration

**Location**: `src/template_sense/extraction/summary_builder.py`

The `normalize_header_blocks()` function (lines 166-284) converts `HeaderCandidateBlock` to JSON dicts:

```python
normalized_pairs = [
    {
        "label": _convert_value_to_primitive(label),
        "value": _convert_value_to_primitive(value),
        "row": row,
        "col": col,
    }
    for label, value, row, col in block.label_value_pairs
]
```

**Current Output Structure**:
```json
{
  "label_value_pairs": [
    {"label": "Invoice Number", "value": "12345", "row": 1, "col": 1},
    {"label": null, "value": "ABC Company", "row": 2, "col": 1}
  ]
}
```

### 2.2 AI Payload Schema

**Location**: `src/template_sense/ai_payload_schema.py`

#### 2.2.1 Adjacent Cell Extraction

Function `_extract_adjacent_cells()` (lines 246-329):
- Extracts cells in 4 directions (left, right, above, below)
- Uses `DEFAULT_ADJACENT_CELL_RADIUS = 3`
- Returns dict like:
  ```python
  {
      "left_1": "Invoice:",
      "left_2": None,
      "right_1": "12345",
      "right_2": None,
      "above_1": "Header",
      "below_1": None,
  }
  ```

#### 2.2.2 AIHeaderCandidate Schema

```python
@dataclass
class AIHeaderCandidate:
    row: int
    col: int
    label: str
    value: Any
    score: float
    adjacent_cells: dict[str, Any] | None = None
```

**Conversion Logic** (lines 332-399):
- Takes normalized header blocks
- Flattens label_value_pairs into individual candidates
- Extracts adjacent cells for context
- Includes block score for confidence

### 2.3 AI Classification

**Location**: `src/template_sense/ai/header_classification.py`

#### 2.3.1 ClassifiedHeaderField

```python
@dataclass
class ClassifiedHeaderField:
    canonical_key: str | None          # Set by mapping layer
    raw_label: str | None
    raw_value: Any
    block_index: int
    row_index: int
    col_index: int
    label_col_offset: int = 0          # NEW: BAT-53 fields
    value_col_offset: int = 0          # NEW: BAT-53 fields
    pattern_type: str | None = None    # NEW: BAT-53 fields
    model_confidence: float | None = None
    metadata: dict[str, Any] | None = None
```

**These fields are ready to be populated by AI response parsing** (lines 179-199).

---

## Part 3: AI Provider Expected Format

### 3.1 System Prompt for Header Classification

**Location**: `src/template_sense/ai_providers/base_provider.py` (lines 413-447)

The AI is instructed to detect two pattern types:

```
PATTERN DETECTION:
1. Multi-cell patterns: Label in one cell, value in adjacent cell
   - Check adjacent_cells to find related values
   - Common patterns: label on left, value on right (or above/below)
   - Example: "Invoice:" in col 1, "12345" in col 3 (right_2)

2. Same-cell patterns: Label and value in same cell with delimiter
   - Common delimiters: ":", "-", "=", "|"
   - Example: "Invoice Number: INV-12345"

When you detect these patterns, populate both raw_label and raw_value fields.
Set label_col_offset and value_col_offset to indicate where label/value are
relative to the main cell (0 = same cell, positive = cells to the right).
```

### 3.2 Expected AI Response Schema

```json
{
  "headers": [
    {
      "raw_label": "Invoice Number",
      "raw_value": "INV-12345",
      "block_index": 0,
      "row_index": 1,
      "col_index": 1,
      "label_col_offset": 0,
      "value_col_offset": 2,
      "pattern_type": "multi_cell",
      "model_confidence": 0.95
    }
  ]
}
```

### 3.3 Field Meanings

- **label_col_offset**: Offset from main cell to label cell
  - 0 = label is in same cell as value
  - 1 = label is 1 column to the right
  - -1 = label is 1 column to the left
  - etc.

- **value_col_offset**: Offset from main cell to value cell
  - 0 = value is in same cell as label
  - 1 = value is 1 column to the right
  - -1 = value is 1 column to the left
  - etc.

- **pattern_type**: One of:
  - `"same_cell"`: Both label and value in same cell with delimiter
  - `"multi_cell"`: Label and value in different cells
  - `null`/`None`: Unknown pattern

---

## Part 4: Test File (CO.xlsx)

**Location**: `/Users/babajideokusanya/Documents/Projects-with-Babajide/codes/template-sense/tests/fixtures/invoice_templates/CO.xlsx`

- File type: Microsoft Excel 2007+ (XLSX)
- Purpose: Real invoice template for integration testing
- Status: Suitable for testing multi-cell pairing patterns

---

## Part 5: Integration Points for Multi-Cell Pairing Logic

### 5.1 Where Pairing Detection Should Occur

The pairing logic should be added to `header_candidates.py` as a NEW function:

```python
def _detect_multi_cell_pairs(
    grid: list[list[Any]],
    block: HeaderCandidateBlock,
    max_offset: int = DEFAULT_ADJACENT_CELL_RADIUS
) -> list[tuple[str | None, Any, int, int, int, int]]:
    """
    Detect multi-cell label/value pairs within a header block.

    Returns:
        List of (label, value, label_row, label_col, value_row, value_col) tuples
    """
```

### 5.2 Integration into Heuristic Detection

The function should be called in `_create_block_from_cluster()` (around line 508):

**Current code**:
```python
# Extract label/value pairs from content
label_value_pairs = []
for row_idx, col_idx, cell in content:
    label, value = _extract_label_value_from_cell(cell)
    label_value_pairs.append((label, value, row_idx, col_idx))
```

**After enhancement** (hypothetical):
```python
# Extract label/value pairs from content
label_value_pairs = []

# Phase 1: Same-cell patterns (current)
for row_idx, col_idx, cell in content:
    label, value = _extract_label_value_from_cell(cell)
    label_value_pairs.append((label, value, row_idx, col_idx))

# Phase 2: Multi-cell patterns (NEW - BAT-76)
if _should_detect_multi_cell_patterns(block):
    multi_cell_pairs = _detect_multi_cell_pairs(grid, block)
    label_value_pairs.extend(multi_cell_pairs)
```

### 5.3 Output Structure Enhancement

The `label_value_pairs` list will remain as `list[tuple[str | None, Any, int, int]]` to maintain backward compatibility. Additional metadata (offsets, pattern_type) will be added by the AI classification layer based on the detected patterns.

### 5.4 Downstream Processing

**Normalization** (summary_builder.py):
- Keep existing structure unchanged for backward compatibility
- Adjacent cells already extracted for AI context

**AI Classification** (header_classification.py):
- AI parses `label_col_offset`, `value_col_offset`, `pattern_type` from response
- These values are stored in `ClassifiedHeaderField` dataclass
- Already implemented! (Lines 180-198)

---

## Part 6: Data Flow Diagram

```
Raw Excel File
    ↓
extract_raw_grid() → grid (2D list)
    ↓
detect_header_candidate_blocks(grid)
    ├─ score_row_as_header_candidate() → heuristic scores
    ├─ find_header_candidate_rows() → high-scoring rows
    ├─ cluster_header_candidate_blocks() → group nearby rows
    │   └─ _create_block_from_cluster()
    │       ├─ _extract_label_value_from_cell() → same-cell pairs
    │       └─ [NEW] _detect_multi_cell_pairs() → adjacent-cell pairs (BAT-76)
    └─ HeaderCandidateBlock[] with label_value_pairs
        ↓
build_sheet_summary()
    └─ normalize_header_blocks() → JSON dicts with label_value_pairs
        ↓
build_ai_payload()
    ├─ _convert_header_candidates() → AIHeaderCandidate[]
    │   └─ _extract_adjacent_cells() → context for AI
    └─ AIPayload with adjacent_cells already included
        ↓
AI Provider (OpenAI, Anthropic)
    └─ Detects patterns + returns label_col_offset, value_col_offset, pattern_type
        ↓
classify_header_fields()
    ├─ _parse_header_field() → ClassifiedHeaderField
    │   └─ Validates label_col_offset, value_col_offset, pattern_type
    └─ ClassifiedHeaderField[] ready for mapping layer
        ↓
Mapping/Canonical Aggregation → CanonicalTemplate
```

---

## Part 7: Edge Cases to Consider

### 7.1 Multi-row Headers
**Scenario**: Label in row 1, value in row 2
**Consideration**: Current offset logic assumes horizontal (column) offsets only. May need to extend to vertical (row) offsets OR handle this as separate row entries.

### 7.2 Non-contiguous Pairing
**Scenario**: "Invoice:" in col 1, "12345" in col 5 with other cells in between
**Current Handling**: Adjacent cell extraction uses radius 3 by default, may not catch col 5
**Consideration**: Might need to increase radius or use smarter matching

### 7.3 Multiple Values per Label
**Scenario**: "Invoice Number:" in one cell, but "INV", "-", "12345" split across three cells
**Current Handling**: Single value pairing logic doesn't handle this
**Consideration**: Might require value concatenation logic

### 7.4 Ambiguous Pairing
**Scenario**: Both "Invoice:" (col 1) and "Amount:" (col 3), with values "12345" and "999" in cols 2 and 4
**Current Handling**: Adjacent cell extraction may not resolve which value pairs with which label
**Consideration**: Requires spatial reasoning (matching left/right proximity)

### 7.5 Different Languages
**Scenario**: Japanese label "請求書番号:" paired with numeric value
**Current Handling**: Keyword detection already handles Japanese, but pairing logic needs to work language-agnostic
**Consideration**: Offsets are language-independent (good!)

### 7.6 Dense Header Blocks
**Scenario**: Header block with all cells filled (10+ rows, 10+ columns)
**Current Handling**: May produce too many candidate pairs
**Consideration**: Might need filtering by metadata keywords or structure patterns

---

## Part 8: Implementation Strategy

### Phase 1: Heuristic Detection (BAT-76 - this ticket)
1. Implement `_detect_multi_cell_pairs()` in `header_candidates.py`
2. Integrate into `_create_block_from_cluster()`
3. Add unit tests for various multi-cell patterns
4. Test with CO.xlsx and other real templates

### Phase 2: AI Enhancement
- AI already expects and parses these fields (ready to go!)
- Just ensure heuristic provides good context via adjacent cells

### Phase 3: Integration Testing
- E2E test through full pipeline
- Verify offsets are correctly propagated to ClassifiedHeaderField
- Test mapping layer with offset information

---

## Part 9: Key Files Reference

| File | Purpose | Key Functions/Classes |
|------|---------|----------------------|
| `header_candidates.py` | Heuristic header detection | `detect_header_candidate_blocks()`, `HeaderCandidateBlock` |
| `constants.py` | Configuration values | `DEFAULT_ADJACENT_CELL_RADIUS = 3` |
| `summary_builder.py` | Normalization layer | `normalize_header_blocks()`, `build_sheet_summary()` |
| `ai_payload_schema.py` | AI payload building | `AIHeaderCandidate`, `_extract_adjacent_cells()` |
| `header_classification.py` | AI classification | `ClassifiedHeaderField`, `_parse_header_field()` |
| `base_provider.py` | AI prompt templates | `_build_system_prompt()` (lines 413-447) |
| `CO.xlsx` | Test fixture | Real invoice template |

---

## Part 10: Summary

**Current State**:
- Header detection identifies candidate blocks using heuristics
- Same-cell label/value extraction works via colon splitting
- Multi-cell patterns NOT detected in heuristic phase
- AI layer ALREADY READY to receive and parse multi-cell metadata

**Proposed Enhancement (BAT-76)**:
- Add heuristic multi-cell pair detection in `header_candidates.py`
- Detect label-value pairs in adjacent cells within header blocks
- Populate offset information for AI consumption
- Maintain backward compatibility with existing structures

**Data Flow**:
- Heuristics provide raw candidate pairs + adjacent cell context
- AI enhances with pattern classification + confidence scoring
- Downstream mapping layer uses offsets for disambiguation
- Canonical aggregation produces final normalized output
