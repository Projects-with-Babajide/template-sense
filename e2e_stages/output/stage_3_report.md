# Stage 4-5: AI Provider Setup and Payload Construction

## Summary
✅ **Stage completed successfully**

## Stage 4: AI Provider
- **Provider**: openai
- **Model**: gpt-4o
- **Timeout**: 30s

## Stage 5: AI Payload
- **Sheet name**: `CO`
- **Header candidates**: 27
- **Table candidates**: 1
- **Field dictionary keys**: 40

### Header Candidates (First 10)
1. **`None`** = `UTAMARU TRADING LLC` (Row 1, Col 2, Score: 1.00)
2. **`None`** = `2-19-11-603, Azabujuban, Minato-ku, Tokyo, 106-0045 Japan` (Row 2, Col 2, Score: 1.00)
3. **`None`** = `COPY` (Row 5, Col 6, Score: 1.00)
4. **`None`** = `GREEN CONTINENT TRADING` (Row 6, Col 2, Score: 1.00)
5. **`None`** = `Abu Hail Building 13, plot, 16940,` (Row 7, Col 2, Score: 1.00)
6. **`None`** = `GCT20240509` (Row 7, Col 6, Score: 1.00)
7. **`None`** = `G-04 Office, Abu Hail. Dubai, UAE` (Row 8, Col 2, Score: 1.00)
8. **`None`** = `2024-05-08T00:00:00` (Row 8, Col 6, Score: 1.00)
9. **`None`** = `JAPAN` (Row 11, Col 6, Score: 1.00)
10. **`FROM`** = `None` (Row 13, Col 2, Score: 1.00)

### Table Candidates

#### Table 1
- **Location**: Rows 19-23, Cols 2-8
- **Score**: 1.00
- **Total data rows**: 4
- **Header row**: 19
- **Header cells** (7):
  - Col 2: `G01-05`
  - Col 3: `5`
  - Col 4: `Frozen Wild Bluefin Tuna - Otoro`
  - Col 5: `Maguro`
  - Col 6: `5`


## Output Files
- `e2e_stages/output/stage_3_ai_payload.json` - Complete AI payload JSON
- `e2e_stages/output/stage_3_ai_provider.json` - AI provider configuration JSON

## Next Step
⚠️  **The next stage makes real AI API calls!**

Run: `python e2e_stages/stage_4_classification.py`
