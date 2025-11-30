# Stage 6: AI Classification

## Summary
✅ **Stage completed successfully**

## Performance
- **Header classification**: 7.59s
- **Column classification**: 2.12s
- **Line item extraction**: 1.85s
- **Total time**: 11.56s

## Results

### Headers
- **Total classified**: 22
- **With confidence scores**: 22
- **Average confidence**: 100.0% (if available)

**Sample headers** (first 10):
1. `None` = `UTAMARU TRADING LLC` (Row 1, Col 2) (confidence: 100.0%)
2. `None` = `2-19-11-603, Azabujuban, Minato-ku, Tokyo, 106-0045 Japan` (Row 2, Col 2) (confidence: 100.0%)
3. `None` = `COPY` (Row 5, Col 6) (confidence: 100.0%)
4. `None` = `GREEN CONTINENT TRADING` (Row 6, Col 2) (confidence: 100.0%)
5. `None` = `Abu Hail Building 13, plot, 16940,` (Row 7, Col 2) (confidence: 100.0%)
6. `None` = `GCT20240509` (Row 7, Col 6) (confidence: 100.0%)
7. `None` = `G-04 Office, Abu Hail. Dubai, UAE` (Row 8, Col 2) (confidence: 100.0%)
8. `None` = `2024-05-08T00:00:00` (Row 8, Col 6) (confidence: 100.0%)
9. `None` = `JAPAN` (Row 11, Col 6) (confidence: 100.0%)
10. `FROM` = `None` (Row 13, Col 2) (confidence: 100.0%)


### Columns
- **Total classified**: 7
- **With confidence scores**: 7
- **Average confidence**: 95.0% (if available)

**Sample columns** (first 10):
1. `Item/NO` (Col 2) (confidence: 95.0%)
2. `No of CTN` (Col 3) (confidence: 95.0%)
3. `Items` (Col 4) (confidence: 95.0%)
4. `None` (Col 5) (confidence: 95.0%)
5. `Quantity` (Col 6) (confidence: 95.0%)
6. `None` (Col 7) (confidence: 95.0%)
7. `Net Weight
(KGS)` (Col 8) (confidence: 95.0%)


### Line Items
- **Total extracted**: 5

**Sample line items** (first 5):
1. Row 0, Table 0 - 5 fields
2. Row 1, Table 0 - 5 fields
3. Row 2, Table 0 - 5 fields
4. Row 3, Table 0 - 5 fields
5. Row 4, Table 0 - 5 fields


## Output Files
- `e2e_stages/output/stage_4_classified_headers.json` - Classified headers JSON
- `e2e_stages/output/stage_4_classified_columns.json` - Classified columns JSON
- `e2e_stages/output/stage_4_line_items.json` - Extracted line items JSON
- `e2e_stages/output/stage_4_timing.json` - Performance timing JSON

## Next Step
Run: `python e2e_stages/stage_5_translation.py`
