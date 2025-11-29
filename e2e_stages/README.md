# End-to-End Pipeline Test - Interactive Stages

This directory contains a complete end-to-end test of the Template Sense pipeline, split into individual stages. Each stage can be run independently, generates output files, and creates a markdown report for review.

**Purpose**: Simulate how Tako would use the Template Sense API, with the ability to pause, review, and ask questions between stages.

---

## Quick Start

### 1. Prerequisites

Ensure your environment is set up:

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Verify .env file has API keys
cat .env | grep API_KEY

# 3. Ensure all dependencies are installed
pip install -e .[dev]
```

### 2. Run All Stages

Execute the stages in order:

```bash
# Stage 0: Setup
python e2e_stages/stage_0_setup.py

# Review: e2e_stages/output/stage_0_report.md
# Then continue...

# Stage 1-2: File Loading
python e2e_stages/stage_1_loading.py

# Stage 3: Grid Extraction
python e2e_stages/stage_2_extraction.py

# Stage 4-5: AI Payload
python e2e_stages/stage_3_ai_payload.py

# Stage 6: AI Classification (⚠️ Uses API credits)
python e2e_stages/stage_4_classification.py

# Stage 7: Translation (⚠️ Uses API credits)
python e2e_stages/stage_5_translation.py

# Stage 8: Fuzzy Matching
python e2e_stages/stage_6_fuzzy_matching.py

# Stage 9-10: Final Output
python e2e_stages/stage_7_final_output.py
```

### 3. Review Results

After all stages complete:

- **Complete summary**: `e2e_stages/output/COMPLETE_PIPELINE_SUMMARY.md`
- **Final output**: `e2e_stages/output/stage_7_final_output.json`
- **All reports**: `e2e_stages/output/stage_*_report.md`

---

## Stage Details

### Stage 0: Setup
**Script**: `stage_0_setup.py`
**No API calls**

- Loads Tako field dictionaries
- Verifies environment configuration
- Checks test file exists

**Output**:
- `stage_0_field_dictionary.json` - Combined field dictionary
- `stage_0_config.json` - Configuration settings
- `stage_0_report.md` - Setup report

**Review**: Field dictionary structure, environment settings

---

### Stage 1-2: File Loading & Workbook Setup
**Script**: `stage_1_loading.py`
**No API calls**

- Loads Excel file
- Extracts sheet names
- Gets sheet dimensions

**Output**:
- `stage_1_workbook_info.json` - Workbook metadata
- `stage_1_report.md` - Loading report

**Review**: Sheet names, dimensions

---

### Stage 3: Grid Extraction & Heuristic Detection
**Script**: `stage_2_extraction.py`
**No API calls**

- Extracts grid from Excel sheet
- Runs heuristic detection for headers
- Runs heuristic detection for tables

**Output**:
- `stage_2_sheet_summary.json` - Complete sheet summary
- `stage_2_report.md` - Extraction report

**Review**:
- Header blocks detected (locations, scores, patterns)
- Table blocks detected
- Label-value pairs identified

**Questions to ask**:
- Are the right regions being detected?
- Are scores reasonable?
- Any missing header/table blocks?

---

### Stage 4-5: AI Provider Setup & Payload Construction
**Script**: `stage_3_ai_payload.py`
**No API calls**

- Initializes AI provider
- Builds AI payload from sheet summary

**Output**:
- `stage_3_ai_payload.json` - Complete AI payload
- `stage_3_ai_provider.json` - Provider configuration
- `stage_3_report.md` - Payload report

**Review**:
- AI provider/model being used
- Header candidates being sent to AI
- Table candidates structure

**Questions to ask**:
- Is the payload structure correct?
- Are all candidates included?

---

### Stage 6: AI Classification
**Script**: `stage_4_classification.py`
**⚠️ MAKES REAL API CALLS - USES CREDITS**

- Classifies header fields via AI
- Classifies table columns via AI
- Extracts line items via AI

**Output**:
- `stage_4_classified_headers.json` - Classified headers
- `stage_4_classified_columns.json` - Classified columns
- `stage_4_line_items.json` - Extracted line items
- `stage_4_timing.json` - Performance metrics
- `stage_4_report.md` - Classification report

**Review**:
- AI classification results
- Confidence scores
- Classification accuracy

**Questions to ask**:
- Are headers being classified correctly?
- Are confidence scores reasonable?
- Any misclassifications?
- Performance acceptable?

---

### Stage 7: Translation
**Script**: `stage_5_translation.py`
**⚠️ MAKES REAL API CALLS - USES CREDITS**

- Collects all unique labels
- Translates non-English labels to English
- Builds translation map

**Output**:
- `stage_5_translations.json` - Translation map + statistics
- `stage_5_report.md` - Translation report

**Review**:
- Languages detected
- Translation accuracy
- Labels requiring translation

**Questions to ask**:
- Are translations correct?
- Any language detection issues?
- Performance acceptable?

---

### Stage 8: Fuzzy Matching
**Script**: `stage_6_fuzzy_matching.py`
**No API calls**

- Matches translated headers to canonical keys
- Matches translated columns to canonical keys
- Uses fuzzy matching algorithm (threshold: 80.0)

**Output**:
- `stage_6_matched_headers.json` - Header match results
- `stage_6_matched_columns.json` - Column match results
- `stage_6_statistics.json` - Matching statistics
- `stage_6_report.md` - Matching report

**Review**:
- Match rates (headers and columns)
- Match scores
- Unmatched fields

**Questions to ask**:
- Is the match threshold appropriate?
- Are good matches being found?
- Why are certain fields unmatched?
- Should threshold be adjusted?

---

### Stage 9-10: Canonical Aggregation & Final Output
**Script**: `stage_7_final_output.py`
**No API calls**

- Aggregates all results
- Builds final normalized output
- Separates matched/unmatched fields
- Generates complete summary

**Output**:
- `stage_7_final_output.json` - **FINAL OUTPUT** (this is what Tako receives!)
- `stage_7_report.md` - Final output report
- `COMPLETE_PIPELINE_SUMMARY.md` - Complete pipeline summary

**Review**:
- Final output structure
- Matched vs unmatched fields
- Overall pipeline performance
- Complete results

**Questions to ask**:
- Is the output structure correct for Tako?
- Are all fields properly categorized?
- Any data loss in the pipeline?
- Overall quality acceptable?

---

## Output Directory Structure

```
e2e_stages/output/
├── stage_0_field_dictionary.json
├── stage_0_config.json
├── stage_0_report.md
├── stage_1_workbook_info.json
├── stage_1_report.md
├── stage_2_sheet_summary.json
├── stage_2_report.md
├── stage_3_ai_payload.json
├── stage_3_ai_provider.json
├── stage_3_report.md
├── stage_4_classified_headers.json
├── stage_4_classified_columns.json
├── stage_4_line_items.json
├── stage_4_timing.json
├── stage_4_report.md
├── stage_5_translations.json
├── stage_5_report.md
├── stage_6_matched_headers.json
├── stage_6_matched_columns.json
├── stage_6_statistics.json
├── stage_6_report.md
├── stage_7_final_output.json          ← FINAL OUTPUT
├── stage_7_report.md
└── COMPLETE_PIPELINE_SUMMARY.md       ← COMPLETE SUMMARY
```

---

## Test Configuration

- **Test file**: `tests/fixtures/invoice_templates/CO.xlsx`
- **Field dictionary**: Combined from `tests/fixtures/tako_header_fields.json` and `tests/fixtures/tako_column_fields.json`
- **AI provider**: From `.env` file (TEMPLATE_SENSE_AI_PROVIDER)
- **AI model**: From `.env` file (TEMPLATE_SENSE_AI_MODEL)

---

## Tips

### Pausing Between Stages

After each stage:
1. Review the `stage_*_report.md` file
2. Examine the JSON output files
3. Ask questions or identify issues
4. Create Linear tickets if needed
5. Proceed to next stage when ready

### API Credits

Stages that make API calls:
- **Stage 6**: Classification (3 AI calls)
- **Stage 7**: Translation (1 AI call)

All other stages are free (no API calls).

### Modifying Test Parameters

To test with different settings:

**Different template**:
```python
# Edit stage_0_setup.py, line ~75
test_file = Path("tests/fixtures/invoice_templates/YOUR_FILE.xlsx")
```

**Different threshold**:
```python
# Edit stage_6_fuzzy_matching.py
# Change DEFAULT_AUTO_MAPPING_THRESHOLD import
```

**Different AI model**:
```bash
# Edit .env file
TEMPLATE_SENSE_AI_MODEL=gpt-4o  # or claude-3-5-sonnet-20241022
```

---

## Troubleshooting

### Error: "Previous stage outputs not found"
**Solution**: Run previous stages in order first

### Error: "API key not found"
**Solution**: Check `.env` file has `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`

### Error: "File not found"
**Solution**: Ensure test template exists at `tests/fixtures/invoice_templates/CO.xlsx`

### Want to re-run a stage
**Solution**: Just run the stage script again - it will overwrite previous output

### Want to reset everything
**Solution**:
```bash
rm -rf e2e_stages/output/*
python e2e_stages/stage_0_setup.py
```

---

## Creating Linear Tickets

As you review each stage, you may identify issues. Here's how to create tickets:

### Issue Template

**Title**: `[E2E Test] Issue in Stage X: Brief description`

**Description**:
```markdown
## Stage
Stage X: [Stage Name]

## Issue
[Describe the issue]

## Evidence
- Review file: `e2e_stages/output/stage_X_report.md`
- Data file: `e2e_stages/output/stage_X_*.json`
- Specific data: [paste relevant section]

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happened]

## Impact
- [ ] Blocks pipeline
- [ ] Reduces accuracy
- [ ] Performance issue
- [ ] Enhancement opportunity
```

---

## Next Steps After Testing

1. ✅ Review `COMPLETE_PIPELINE_SUMMARY.md`
2. ✅ Examine `stage_7_final_output.json` (what Tako receives)
3. ✅ Create Linear tickets for any issues
4. ✅ Test with additional templates if needed
5. ✅ Adjust thresholds/parameters based on results
6. ✅ Document findings

---

**Happy Testing! 🚀**
