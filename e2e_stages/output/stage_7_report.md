# Stage 9-10: Canonical Aggregation and Final Output

## Summary
✅ **ALL STAGES COMPLETED SUCCESSFULLY!**

## Final Output Structure

### Headers
- **Matched**: 0 fields
- **Unmatched**: 22 fields
- **Total**: 22
- **Match rate**: 0.0%

#### Top Matched Headers (First 15)


### Tables
- **Total tables**: 1

#### Table 0
- **Columns**: 7 (3 matched, 4 unmatched)
- **Location**: Row 18, Col 2
- **Matched columns**:
  - `number_of_boxes` (detected: `No of CTN`, score: 81.8)
  - `quantity` (detected: `None`, score: 100.0)
  - `net_weight` (detected: `Quantity`, score: 100.0)


### Line Items
- **Total extracted**: 5

## Pipeline Performance

### Timing
- **AI Classification**: 11.56s
- **Translation**: 6.46s
- **Fuzzy Matching**: 0.003s
- **Total AI time**: 18.02s

### Provider
- **Provider**: openai
- **Model**: gpt-4o

## Output Files
- `e2e_stages/output/stage_7_final_output.json` - Complete final output JSON

## What Tako Receives
This is the exact structure Tako would receive from the API:

\`\`\`json
{
  "normalized_output": {
    "headers": {
      "matched": [...],
      "unmatched": [...]
    },
    "tables": [...],
    "line_items": [...]
  },
  "metadata": {
    "sheet_name": "CO",
    "ai_provider": "openai",
    "ai_model": "gpt-4o"
  }
}
\`\`\`

See full output in: `e2e_stages/output/stage_7_final_output.json`
