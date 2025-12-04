# Stage 8: Fuzzy Matching

## Summary
✅ **Stage completed successfully**

## Configuration
- **Threshold**: 80.0
- **Algorithm**: token_set_ratio (rapidfuzz)

## Performance
- **Header matching**: 0.002s (1902 fields/sec)
- **Column matching**: 0.001s (8549 fields/sec)
- **Total time**: 0.003s

## Headers
- **Total**: 4
- **Matched**: 0 (0.0%)
- **Unmatched**: 4 (100.0%)
- **Average score**: 45.2

### Matched Headers (Top 15)


### Unmatched Headers (First 10)
1. `DE` (best score: 40.0)
2. `TO` (best score: 40.0)
3. `Shipment Day` (best score: 52.6)
4. `Transportation` (best score: 48.0)


## Columns
- **Total**: 5
- **Matched**: 3 (60.0%)
- **Unmatched**: 2 (40.0%)
- **Average score**: 81.7

### Matched Columns (Top 15)
1. `Number of CTN` → **`number_of_boxes`** (score: 81.8)
2. `Quantity` → **`quantity`** (score: 100.0)
3. `Net Weight (KGS)` → **`net_weight`** (score: 100.0)


### Unmatched Columns (First 10)
1. `Item/Number` (best score: 66.7)
2. `Items` (best score: 60.0)


## Output Files
- `e2e_stages/output/stage_6_matched_headers.json` - Matched headers JSON
- `e2e_stages/output/stage_6_matched_columns.json` - Matched columns JSON
- `e2e_stages/output/stage_6_statistics.json` - Matching statistics JSON

## Next Step
Run: `python e2e_stages/stage_7_final_output.py`
