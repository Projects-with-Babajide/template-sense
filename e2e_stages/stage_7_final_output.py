"""
STAGE 9-10: Canonical Aggregation and Final Output Building

This script aggregates all results and builds the final normalized output.

Input:
  - All previous stage outputs

Output:
  - e2e_stages/output/stage_7_final_output.json
  - e2e_stages/output/stage_7_report.md
  - e2e_stages/output/COMPLETE_PIPELINE_SUMMARY.md
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def main():
    print("=" * 80)
    print("STAGE 9-10: CANONICAL AGGREGATION AND FINAL OUTPUT")
    print("=" * 80)

    output_dir = Path("e2e_stages/output")

    # ========================================================================
    # Load All Previous Stage Outputs
    # ========================================================================
    print("\n📥 Loading all previous stage outputs...")

    # Load all data files
    with open(output_dir / "stage_0_config.json") as f:
        config = json.load(f)
    with open(output_dir / "stage_1_workbook_info.json") as f:
        workbook_info = json.load(f)
    with open(output_dir / "stage_2_sheet_summary.json") as f:
        sheet_summary = json.load(f)
    with open(output_dir / "stage_3_ai_provider.json") as f:
        ai_provider_info = json.load(f)
    with open(output_dir / "stage_4_classified_headers.json") as f:
        classified_headers = json.load(f)
    with open(output_dir / "stage_4_classified_columns.json") as f:
        classified_columns = json.load(f)
    with open(output_dir / "stage_4_line_items.json") as f:
        line_items = json.load(f)
    with open(output_dir / "stage_4_timing.json") as f:
        ai_timing = json.load(f)
    with open(output_dir / "stage_5_translations.json") as f:
        translations_data = json.load(f)
    with open(output_dir / "stage_6_matched_headers.json") as f:
        matched_headers = json.load(f)
    with open(output_dir / "stage_6_matched_columns.json") as f:
        matched_columns = json.load(f)
    with open(output_dir / "stage_6_statistics.json") as f:
        matching_stats = json.load(f)

    print("✓ All stage outputs loaded successfully")

    # ========================================================================
    # Build Final Normalized Output
    # ========================================================================
    print("\n🏗️  Building final normalized output...")

    # Separate matched and unmatched headers
    matched_header_fields = []
    unmatched_header_fields = []

    for i, header in enumerate(classified_headers):
        match_result = matched_headers[i] if i < len(matched_headers) else None

        field = {
            "detected_label": header.get("raw_label"),
            "cell_value": header.get("raw_value"),
            "location": {
                "row": header.get("row_index"),
                "column": header.get("col_index"),
            },
            "ai_confidence": header.get("model_confidence"),
        }

        if match_result and match_result.get("canonical_key"):
            field.update(
                {
                    "canonical_key": match_result["canonical_key"],
                    "translated_label": match_result["translated_text"],
                    "fuzzy_match_score": match_result["match_score"],
                    "matched_variant": match_result["matched_variant"],
                }
            )
            matched_header_fields.append(field)
        else:
            field.update(
                {
                    "translated_label": match_result["translated_text"]
                    if match_result
                    else header.get("raw_label"),
                    "best_match_score": match_result["match_score"] if match_result else 0.0,
                }
            )
            unmatched_header_fields.append(field)

    # Build table structures with matched columns
    tables = []
    current_table_idx = None
    current_table = None

    for i, column in enumerate(classified_columns):
        match_result = matched_columns[i] if i < len(matched_columns) else None

        # Start new table if needed
        if column.get("table_block_index") != current_table_idx:
            if current_table:
                tables.append(current_table)

            current_table_idx = column.get("table_block_index")
            current_table = {
                "table_index": current_table_idx,
                "location": {
                    "row_index": column.get("row_index"),
                    "col_index": column.get("col_index"),
                },
                "columns": [],
            }

        # Add column
        col_data = {
            "column_index": column.get("col_index"),
            "detected_label": column.get("raw_label"),
            "ai_confidence": column.get("model_confidence"),
        }

        if match_result and match_result.get("canonical_key"):
            col_data.update(
                {
                    "canonical_key": match_result["canonical_key"],
                    "translated_label": match_result["translated_text"],
                    "fuzzy_match_score": match_result["match_score"],
                }
            )
        else:
            col_data.update(
                {
                    "translated_label": match_result["translated_text"]
                    if match_result
                    else column.get("raw_label"),
                    "best_match_score": match_result["match_score"] if match_result else 0.0,
                }
            )

        current_table["columns"].append(col_data)

    if current_table:
        tables.append(current_table)

    # Build final output structure
    final_output = {
        "headers": {
            "matched": matched_header_fields,
            "unmatched": unmatched_header_fields,
        },
        "tables": tables,
        "line_items": line_items,
    }

    print("✓ Final output built")
    print(f"  • Matched headers: {len(matched_header_fields)}")
    print(f"  • Unmatched headers: {len(unmatched_header_fields)}")
    print(f"  • Tables: {len(tables)}")
    print(f"  • Line items: {len(line_items)}")

    # ========================================================================
    # Build Metadata
    # ========================================================================
    print("\n📊 Building metadata...")

    metadata = {
        "file_path": config["test_file"],
        "sheet_name": workbook_info["selected_sheet"],
        "ai_provider": ai_provider_info["provider"],
        "ai_model": ai_provider_info["model"],
        "pipeline_stages_completed": 10,
        "timing": {
            "ai_classification_seconds": ai_timing["total_seconds"],
            "translation_seconds": translations_data["statistics"]["translation_time_seconds"],
            "fuzzy_matching_seconds": (
                matching_stats["headers"]["matching_time_seconds"]
                + matching_stats["columns"]["matching_time_seconds"]
            ),
        },
    }

    print("✓ Metadata built")

    # ========================================================================
    # Save Final Output
    # ========================================================================
    print("\n💾 Saving final output...")

    complete_output = {
        "normalized_output": final_output,
        "metadata": metadata,
    }

    output_file = output_dir / "stage_7_final_output.json"
    with open(output_file, "w") as f:
        json.dump(complete_output, f, indent=2)
    print(f"✓ Final output saved to: {output_file}")

    # ========================================================================
    # Generate Final Report
    # ========================================================================
    print("\n📝 Generating final report...")

    report = f"""# Stage 9-10: Canonical Aggregation and Final Output

## Summary
✅ **ALL STAGES COMPLETED SUCCESSFULLY!**

## Final Output Structure

### Headers
- **Matched**: {len(matched_header_fields)} fields
- **Unmatched**: {len(unmatched_header_fields)} fields
- **Total**: {len(matched_header_fields) + len(unmatched_header_fields)}
- **Match rate**: {len(matched_header_fields)/(len(matched_header_fields) + len(unmatched_header_fields))*100:.1f}%

#### Top Matched Headers (First 15)
"""

    for i, field in enumerate(matched_header_fields[:15], 1):
        report += f"{i}. **`{field['canonical_key']}`** = `{field['cell_value']}` (detected: `{field['detected_label']}`, score: {field['fuzzy_match_score']:.1f})\n"

    report += f"""

### Tables
- **Total tables**: {len(tables)}
"""

    for table in tables:
        matched_cols = sum(1 for col in table["columns"] if "canonical_key" in col)
        total_cols = len(table["columns"])
        report += f"""
#### Table {table['table_index']}
- **Columns**: {total_cols} ({matched_cols} matched, {total_cols - matched_cols} unmatched)
- **Location**: Row {table['location']['row_index']}, Col {table['location']['col_index']}
- **Matched columns**:
"""
        for col in [c for c in table["columns"] if "canonical_key" in c][:10]:
            report += f"  - `{col['canonical_key']}` (detected: `{col['detected_label']}`, score: {col['fuzzy_match_score']:.1f})\n"

    report += rf"""

### Line Items
- **Total extracted**: {len(line_items)}

## Pipeline Performance

### Timing
- **AI Classification**: {ai_timing['total_seconds']:.2f}s
- **Translation**: {translations_data['statistics']['translation_time_seconds']:.2f}s
- **Fuzzy Matching**: {metadata['timing']['fuzzy_matching_seconds']:.3f}s
- **Total AI time**: {metadata['timing']['ai_classification_seconds'] + metadata['timing']['translation_seconds']:.2f}s

### Provider
- **Provider**: {ai_provider_info['provider']}
- **Model**: {ai_provider_info['model']}

## Output Files
- `{output_file}` - Complete final output JSON

## What Tako Receives
This is the exact structure Tako would receive from the API:

\`\`\`json
{{
  "normalized_output": {{
    "headers": {{
      "matched": [...],
      "unmatched": [...]
    }},
    "tables": [...],
    "line_items": [...]
  }},
  "metadata": {{
    "sheet_name": "{workbook_info['selected_sheet']}",
    "ai_provider": "{ai_provider_info['provider']}",
    "ai_model": "{ai_provider_info['model']}"
  }}
}}
\`\`\`

See full output in: `{output_file}`
"""

    report_file = output_dir / "stage_7_report.md"
    with open(report_file, "w") as f:
        f.write(report)
    print(f"✓ Report saved to: {report_file}")

    # ========================================================================
    # Generate Complete Pipeline Summary
    # ========================================================================
    summary = f"""# Complete E2E Pipeline Summary

## ✅ ALL STAGES COMPLETED SUCCESSFULLY

Test file: `{config['test_file']}`
Date: {Path(output_file).stat().st_mtime}

---

## Pipeline Execution Flow

### Stage 0: Setup ✅
- Loaded {config['total_fields']} canonical fields
- Configured AI provider: {ai_provider_info['provider']}

### Stage 1-2: File Loading ✅
- File: `{workbook_info['selected_sheet']}`
- Size: {workbook_info['max_row']} rows × {workbook_info['max_column']} columns

### Stage 3: Heuristic Detection ✅
- Header blocks: {len(sheet_summary.get('header_blocks', []))}
- Table blocks: {len(sheet_summary.get('table_blocks', []))}

### Stage 4-5: AI Payload Construction ✅
- Header candidates: {len(sheet_summary.get('header_blocks', []))}
- Table candidates: {len(sheet_summary.get('table_blocks', []))}

### Stage 6: AI Classification ✅
- Headers classified: {len(classified_headers)}
- Columns classified: {len(classified_columns)}
- Line items extracted: {len(line_items)}
- Time: {ai_timing['total_seconds']:.2f}s

### Stage 7: Translation ✅
- Labels translated: {translations_data['statistics']['unique_labels']}
- Languages detected: {len(translations_data['statistics']['languages_detected'])}
- Time: {translations_data['statistics']['translation_time_seconds']:.2f}s

### Stage 8: Fuzzy Matching ✅
- Headers matched: {matching_stats['headers']['matched']}/{matching_stats['headers']['total']} ({matching_stats['headers']['match_rate']*100:.1f}%)
- Columns matched: {matching_stats['columns']['matched']}/{matching_stats['columns']['total']} ({matching_stats['columns']['match_rate']*100:.1f}%)
- Time: {metadata['timing']['fuzzy_matching_seconds']:.3f}s

### Stage 9-10: Final Output ✅
- Matched headers: {len(matched_header_fields)}
- Unmatched headers: {len(unmatched_header_fields)}
- Tables: {len(tables)}
- Line items: {len(line_items)}

---

## Key Metrics

| Metric | Value |
|--------|-------|
| **Total Execution Time** | {ai_timing['total_seconds'] + translations_data['statistics']['translation_time_seconds'] + metadata['timing']['fuzzy_matching_seconds']:.2f}s |
| **Header Match Rate** | {matching_stats['headers']['match_rate']*100:.1f}% |
| **Column Match Rate** | {matching_stats['columns']['match_rate']*100:.1f}% |
| **AI Provider** | {ai_provider_info['provider']} |
| **AI Model** | {ai_provider_info['model']} |

---

## Files Generated

All stage outputs are in `e2e_stages/output/`:

- `stage_0_*.json/md` - Setup and field dictionary
- `stage_1_*.json/md` - Workbook information
- `stage_2_*.json/md` - Sheet summary and heuristics
- `stage_3_*.json/md` - AI payload
- `stage_4_*.json/md` - AI classification results
- `stage_5_*.json/md` - Translation results
- `stage_6_*.json/md` - Fuzzy matching results
- `stage_7_*.json/md` - **FINAL OUTPUT** ← This is what Tako receives!

---

## Review Final Output

**File**: `{output_file}`

This JSON file contains the complete normalized output that Tako would receive from the `extract_template_structure()` API call.

---

## Next Steps

1. ✅ Review all stage reports in `e2e_stages/output/`
2. ✅ Examine `{output_file}` for final structure
3. ✅ Create Linear tickets for any issues found
4. ✅ Test with additional templates if needed

**End of E2E Test**
"""

    summary_file = output_dir / "COMPLETE_PIPELINE_SUMMARY.md"
    with open(summary_file, "w") as f:
        f.write(summary)
    print(f"✓ Complete summary saved to: {summary_file}")

    print("\n" + "=" * 80)
    print("🎉 ALL STAGES COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print(f"\n📖 Review complete summary: {summary_file}")
    print(f"📄 Review final output: {output_file}")
    print("\n✅ End-to-end pipeline test complete!")


if __name__ == "__main__":
    main()
