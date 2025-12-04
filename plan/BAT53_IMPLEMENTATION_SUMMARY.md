# BAT-53 Implementation Summary

## Objective
Improve label-value pair detection for multi-cell and same-cell patterns in invoice templates.

## Problem Statement
The current implementation extracts header fields cell-by-cell but misses important patterns:
- **Multi-cell patterns**: Label in one cell, value in adjacent cell (e.g., "FROM : " in Col 2, "NARITA JAPAN" in Col 4)
- **Same-cell patterns**: Label and value in one cell separated by delimiter (e.g., "Invoice Number: INV-12345")

## Implementation Details

### Phase 1: AI Payload Enhancement
**Files Modified:**
- `src/template_sense/constants.py` - Added `DEFAULT_ADJACENT_CELL_RADIUS = 3`
- `src/template_sense/ai_payload_schema.py` - Enhanced `AIHeaderCandidate` dataclass and extraction logic

**Changes:**
1. Added `adjacent_cells` field to `AIHeaderCandidate` dataclass
2. Implemented `_extract_adjacent_cells()` function to extract up to 3 cells in each direction (left, right, above, below)
3. Updated `_convert_header_candidates()` to optionally extract adjacent cells when grid is provided
4. Updated `build_ai_payload()` signature to accept `grid` parameter

### Phase 2: AI Provider Prompt Updates
**Files Modified:**
- `src/template_sense/ai_providers/openai_provider.py`
- `src/template_sense/ai_providers/anthropic_provider.py`

**Changes:**
1. Enhanced system prompts for context="headers" with pattern detection instructions:
   - Multi-cell pattern detection using adjacent_cells
   - Same-cell pattern detection with common delimiters
2. Instructed AI to populate label_col_offset, value_col_offset, and pattern_type fields

### Phase 3: Classification Response Parsing
**Files Modified:**
- `src/template_sense/ai/header_classification.py`

**Changes:**
1. Updated `ClassifiedHeaderField` dataclass with new fields:
   - `label_col_offset: int = 0`
   - `value_col_offset: int = 0`
   - `pattern_type: str | None = None`
2. Updated `_parse_header_field()` to extract and validate new optional fields

### Phase 4: Pipeline Integration
**Files Modified:**
- `src/template_sense/pipeline/extraction_pipeline.py`

**Changes:**
1. Extract grid using `extract_raw_grid()` after building sheet summary
2. Pass grid to `build_ai_payload()` for adjacent cell context

## Test Results

### Unit Tests
✅ **All 43 relevant tests passed** (test_ai_payload* and test_header_classification*)

Coverage maintained at 91% for header_classification.py

### Integration Test with CO.xlsx
```
Loading tests/fixtures/invoice_templates/CO.xlsx...
Sheet: CO
Header blocks: 2
Table blocks: 1
Grid size: 44 rows x 8 cols

First header candidate:
  Row: 1, Col: 2
  Adjacent cells included: YES ✅

Looking for FROM pattern (rows 13-14)...
Found at row 13, col 2
  Label: "FROM"
  Value: None
  Right cells (where value might be):
    right_1 (col 3): "None"
    right_2 (col 4): "NARITA JAPAN    " ✅
    right_3 (col 5): "None"
```

**Key Finding:** The AI now receives adjacent cell context showing "NARITA JAPAN" in column 4 (right_2) relative to the "FROM" label in column 2. This enables the AI to detect multi-cell label-value patterns.

### Code Quality
✅ **Black formatting:** Passed
✅ **Ruff linting:** All checks passed

## Architecture Impact

### Backward Compatibility
- All new fields are optional with default values
- Existing code works without changes
- Grid parameter is optional (defaults to None)

### Performance
- Minimal impact: Adjacent cell extraction is O(radius) per header candidate
- Grid extraction already happens in summary_builder (reused in pipeline)

## Files Changed Summary
1. `src/template_sense/constants.py` - New constant
2. `src/template_sense/ai_payload_schema.py` - Enhanced schema + extraction
3. `src/template_sense/ai_providers/openai_provider.py` - Updated prompts
4. `src/template_sense/ai_providers/anthropic_provider.py` - Updated prompts
5. `src/template_sense/ai/header_classification.py` - Enhanced dataclass + parsing
6. `src/template_sense/pipeline/extraction_pipeline.py` - Grid threading

## Next Steps
1. User approval of implementation
2. Commit changes with proper message
3. Create PR for review
4. Merge to main
5. Return to e2e-test-framework branch to continue E2E testing

## Expected Impact
- AI can now detect multi-cell patterns like "FROM : " → "NARITA JAPAN"
- AI can detect same-cell patterns like "Invoice Number: INV-12345"
- Better extraction accuracy for label-value pairs
- Reduces manual data entry for Tako's backend
