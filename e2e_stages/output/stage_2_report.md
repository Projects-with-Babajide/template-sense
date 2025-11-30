# Stage 3: Grid Extraction and Heuristic Detection

## Summary
✅ **Stage completed successfully**

## Grid Information
- **Sheet**: `CO`
- **Dimensions**: 0 rows × 0 columns
- **Header blocks**: 2
- **Table blocks**: 1

## Header Blocks

### Block 1
- **Location**: Rows 1-16, Cols 2-6
- **Score**: 1.00
- **Pattern**: key_value_and_keywords
- **Label-value pairs**: 17

**Sample pairs** (first 5):
- `label` = `value` (Row row, Col col)
- `label` = `value` (Row row, Col col)
- `label` = `value` (Row row, Col col)
- `label` = `value` (Row row, Col col)
- `label` = `value` (Row row, Col col)

### Block 2
- **Location**: Rows 37-44, Cols 1-4
- **Score**: 1.00
- **Pattern**: key_value_patterns
- **Label-value pairs**: 5

**Sample pairs** (first 5):
- `label` = `value` (Row row, Col col)
- `label` = `value` (Row row, Col col)
- `label` = `value` (Row row, Col col)
- `label` = `value` (Row row, Col col)
- `label` = `value` (Row row, Col col)


## Table Blocks

### Block 1
- **Location**: Rows 18-23, Cols 2-8
- **Score**: 1.00
- **Pattern**: moderate_numeric_density_with_header
- **Total cells**: 40


## Output Files
- `e2e_stages/output/stage_2_sheet_summary.json` - Complete sheet summary JSON

## Next Step
Run: `python e2e_stages/stage_3_ai_payload.py`
