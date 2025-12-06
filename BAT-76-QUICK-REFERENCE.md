# BAT-76 Quick Reference Guide

## What's This About?

Enhance header extraction to detect **multi-cell label/value pairs** (e.g., label in column A, value in column C).

Currently: Only detects `"Label: Value"` in same cell
Goal: Also detect when label and value are in adjacent cells

## Key Files

| File | Role | Status |
|------|------|--------|
| `src/template_sense/extraction/header_candidates.py` | Heuristic detection | **NEEDS CHANGES** |
| `src/template_sense/constants.py` | DEFAULT_ADJACENT_CELL_RADIUS = 3 | Ready |
| `src/template_sense/ai_payload_schema.py` | Adjacent cell extraction | Ready |
| `src/template_sense/ai/header_classification.py` | ClassifiedHeaderField parsing | **READY** |
| `src/template_sense/ai_providers/base_provider.py` | AI prompt templates | **READY** |
| `tests/fixtures/invoice_templates/CO.xlsx` | Test data | Ready |

## Core Concepts

### Current: Same-Cell Patterns (Working)
```
Cell A1: "Invoice Number: 12345"
         ↓ _extract_label_value_from_cell()
Result: ("Invoice Number", "12345")
```

### New: Multi-Cell Patterns (To Implement)
```
Cell A1: "Invoice Number"    Cell B1: 12345
         ↓ _detect_multi_cell_pairs()
Result: ("Invoice Number", 12345)
        + metadata: label_col_offset=0, value_col_offset=1
```

## Where to Add Code

**Location**: `header_candidates.py` → `_create_block_from_cluster()` (line ~508)

**Current Code**:
```python
label_value_pairs = []
for row_idx, col_idx, cell in content:
    label, value = _extract_label_value_from_cell(cell)
    label_value_pairs.append((label, value, row_idx, col_idx))
```

**What to Add**:
```python
# Phase 1: Same-cell patterns (existing code stays)
label_value_pairs = []
for row_idx, col_idx, cell in content:
    label, value = _extract_label_value_from_cell(cell)
    label_value_pairs.append((label, value, row_idx, col_idx))

# Phase 2: Multi-cell patterns (NEW)
multi_cell_pairs = _detect_multi_cell_pairs(grid, block)
label_value_pairs.extend(multi_cell_pairs)
```

## Function to Implement

```python
def _detect_multi_cell_pairs(
    grid: list[list[Any]],
    block: HeaderCandidateBlock,
    max_offset: int = DEFAULT_ADJACENT_CELL_RADIUS,
) -> list[tuple[str | None, Any, int, int]]:
    """
    Detect multi-cell label/value pairs within a header block.

    Scans cells in block.content for potential label-value adjacencies.
    For example, if cell (1,1) has text like "Invoice:" and cell (1,2)
    has a numeric value like "12345", detect this as a pair.

    Args:
        grid: 2D list of cell values (0-based access)
        block: HeaderCandidateBlock with content to scan
        max_offset: Maximum distance to look for adjacent cells (default: 3)

    Returns:
        List of (label, value, row, col) tuples, same format as
        existing label_value_pairs

    Note:
        - Return tuples are in the same format as existing pairs
        - Additional offset info is handled by AI layer (not here)
        - Must not duplicate existing same-cell pairs
    """
    # TODO: Implement detection logic
    pass
```

## Detection Algorithm Ideas

### Approach 1: Simple Adjacency
1. For each cell in block.content
2. Check adjacent cells (left, right, above, below) up to max_offset
3. If adjacent cell seems to be a value and current cell is label-like
4. Create pair entry

### Approach 2: Pattern Matching
1. For each cell, check if it looks like a label (ends with ":", has metadata keyword)
2. Look at adjacent cells for values
3. Score adjacency based on spatial proximity and cell content types

### Approach 3: Heuristic Scoring
1. Calculate "label score" for each cell (keyword presence, punctuation)
2. Calculate "value score" for each cell (numeric, text, non-empty)
3. Find high-scoring label/value adjacencies
4. Return top matches

## Testing Checklist

- [ ] Same-cell patterns still work (regression test)
- [ ] Detect label in col 1, value in col 2
- [ ] Detect label in col 1, value in col 3 (with offset > 1)
- [ ] Handle Japanese labels/values
- [ ] Avoid duplicate detection (don't extract same pair twice)
- [ ] Handle edge cases (empty blocks, single-cell blocks)
- [ ] Test with CO.xlsx real template
- [ ] Verify structure preserved through summary_builder → ai_payload_schema → classification

## Offset Calculation

If you detect label at (row_l, col_l) and value at (row_v, col_v):
- `label_col_offset = col_l - col_v` (offset from value position)
- `value_col_offset = 0` (or calculate from label position)

BUT: In this ticket, we only populate label_value_pairs (4-tuple).
The AI layer will calculate and parse offsets from the adjacent_cells context.

## Key Constants

```python
from template_sense.constants import DEFAULT_ADJACENT_CELL_RADIUS
# DEFAULT_ADJACENT_CELL_RADIUS = 3
```

## Data Structure Unchanged

The `label_value_pairs` structure stays as:
```python
list[tuple[str | None, Any, int, int]]
# (label, value, row, col)
```

**No changes needed to downstream code!** The offset info is added by the AI layer.

## Backward Compatibility

✓ No breaking changes - existing tuple structure preserved
✓ Same-cell extraction continues to work
✓ Can extend label_value_pairs without affecting consumers
✓ All offset info is optional (added by AI, not heuristics)

## Files That Don't Need Changes

- `summary_builder.py` - Just passes label_value_pairs through
- `ai_payload_schema.py` - Already extracts adjacent cells
- `header_classification.py` - Already parses offsets from AI response
- `base_provider.py` - Already documents expected format

## Next Steps After Implementation

1. Run existing tests to ensure regression-free
2. Add unit tests for new multi-cell detection
3. Integration test through full pipeline
4. Test with CO.xlsx to verify real-world template handling
5. Performance check on large templates

---

**Remember**: This is the HEURISTIC layer - the goal is to detect candidates.
The AI layer will later refine and validate these candidates with confidence scores.

For detailed architecture, see `BAT-76-HEADER-EXTRACTION-ANALYSIS.md`
