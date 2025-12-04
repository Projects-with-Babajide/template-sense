# End-to-End Pipeline Test - Quick Start Guide

## ✅ Setup Complete!

I've created an interactive end-to-end test suite that lets you run the Template Sense pipeline stage-by-stage, review outputs, and ask questions between each step.

---

## How It Works

Each stage:
1. Reads output from previous stage(s)
2. Performs its processing
3. Saves results to JSON files
4. Generates a markdown report
5. Tells you what to run next

You can pause, review, ask questions, and create tickets between stages!

---

## Quick Start

### Run Stage by Stage

```bash
# Activate environment
source .venv/bin/activate

# Stage 0: Setup (✅ Already completed!)
python e2e_stages/stage_0_setup.py

# Review: e2e_stages/output/stage_0_report.md
# Ask questions, then continue...

# Stage 1-2: Load Excel file
python e2e_stages/stage_1_loading.py

# Stage 3: Extract grid and run heuristics
python e2e_stages/stage_2_extraction.py

# Stage 4-5: Build AI payload
python e2e_stages/stage_3_ai_payload.py

# Stage 6: AI Classification (⚠️ Uses API credits!)
python e2e_stages/stage_4_classification.py

# Stage 7: Translation (⚠️ Uses API credits!)
python e2e_stages/stage_5_translation.py

# Stage 8: Fuzzy matching
python e2e_stages/stage_6_fuzzy_matching.py

# Stage 9-10: Build final output
python e2e_stages/stage_7_final_output.py
```

---

## What Gets Generated

### After Each Stage

- **JSON file**: Raw data output
- **Markdown report**: Human-readable summary
- **Next step instruction**: What to run next

### After All Stages

- `e2e_stages/output/stage_7_final_output.json` - **This is what Tako receives from the API!**
- `e2e_stages/output/COMPLETE_PIPELINE_SUMMARY.md` - Full pipeline summary

---

## Review Process

After each stage:

1. **Check terminal output** for summary statistics
2. **Read the markdown report** in `e2e_stages/output/stage_X_report.md`
3. **Examine JSON files** for detailed data
4. **Ask questions** about anything unclear
5. **Create Linear tickets** for issues found
6. **Continue to next stage** when ready

---

## Stages Overview

| Stage | Name | API Calls | What to Review |
|-------|------|-----------|----------------|
| 0 | Setup | No | Field dictionary, environment |
| 1-2 | File Loading | No | Sheet names, dimensions |
| 3 | Grid Extraction | No | Header/table blocks detected |
| 4-5 | AI Payload | No | Payload structure |
| 6 | AI Classification | **Yes** | Classification accuracy, confidence |
| 7 | Translation | **Yes** | Translation accuracy |
| 8 | Fuzzy Matching | No | Match rates, unmatched fields |
| 9-10 | Final Output | No | Complete pipeline results |

---

## Test Configuration

- **Template**: `tests/fixtures/invoice_templates/CO.xlsx`
- **Field Dictionary**: Tako's canonical fields (40 total)
- **AI Provider**: OpenAI (gpt-4o) - from your .env
- **Fuzzy Threshold**: 80.0

---

## Questions to Ask at Each Stage

### Stage 3: Grid Extraction
- Are the right header/table regions being detected?
- Are heuristic scores reasonable?
- Any missing blocks?

### Stage 6: AI Classification
- Are headers classified correctly?
- Are confidence scores reasonable?
- Any misclassifications?

### Stage 7: Translation
- Are translations accurate?
- Any language detection issues?

### Stage 8: Fuzzy Matching
- Is the match threshold appropriate (80.0)?
- Why are certain fields unmatched?
- Should threshold be adjusted?

### Stage 9-10: Final Output
- Is the output structure correct for Tako?
- Any data loss in the pipeline?
- Overall quality acceptable?

---

## Creating Tickets

When you find an issue:

```markdown
Title: [E2E Test] Issue in Stage X: Brief description

Description:
## Stage
Stage X: [Name]

## Issue
[Describe the issue]

## Evidence
- Report: e2e_stages/output/stage_X_report.md
- Data: [paste relevant section]

## Expected vs Actual
[What should happen vs what happened]

## Priority
[High/Medium/Low]
```

---

## Full Documentation

See `e2e_stages/README.md` for:
- Detailed stage descriptions
- Output file structure
- Troubleshooting tips
- How to modify test parameters

---

## Next Step

You're ready to start! Run the next stage:

```bash
python e2e_stages/stage_1_loading.py
```

Then review `e2e_stages/output/stage_1_report.md` and let me know if you have questions!

---

**Happy Testing! 🚀**
