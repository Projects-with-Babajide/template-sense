"""
STAGE 3: Grid Extraction and Heuristic Detection

This script extracts the grid and runs heuristic detection for headers and tables.

Input:
  - e2e_stages/output/stage_0_config.json
  - e2e_stages/output/stage_1_workbook_info.json

Output:
  - e2e_stages/output/stage_2_sheet_summary.json
  - e2e_stages/output/stage_2_report.md
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from template_sense.adapters.excel_adapter import ExcelWorkbook
from template_sense.extraction.summary_builder import build_sheet_summary
from template_sense.file_loader import load_excel_file


def main():
    print("=" * 80)
    print("STAGE 3: GRID EXTRACTION AND HEURISTIC DETECTION")
    print("=" * 80)

    output_dir = Path("e2e_stages/output")

    # ========================================================================
    # Load Previous Stage Outputs
    # ========================================================================
    print("\n📥 Loading previous stage outputs...")

    config_file = output_dir / "stage_0_config.json"
    workbook_file = output_dir / "stage_1_workbook_info.json"

    if not config_file.exists() or not workbook_file.exists():
        print("❌ Error: Previous stage outputs not found!")
        print("Please run stage_0_setup.py and stage_1_loading.py first.")
        sys.exit(1)

    with open(config_file) as f:
        config = json.load(f)
    with open(workbook_file) as f:
        workbook_info = json.load(f)

    test_file = Path(config["test_file"])
    selected_sheet = workbook_info["selected_sheet"]
    print(f"✓ Test file: {test_file}")
    print(f"✓ Selected sheet: {selected_sheet}")

    # ========================================================================
    # Load Workbook and Extract Sheet Summary
    # ========================================================================
    print("\n🔍 Running grid extraction and heuristic detection...")
    raw_workbook = load_excel_file(test_file)
    workbook = ExcelWorkbook(raw_workbook)

    sheet_summary = build_sheet_summary(workbook, selected_sheet)
    print("✓ Sheet summary built successfully")

    # Extract statistics
    row_count = sheet_summary.get("row_count", 0)
    col_count = sheet_summary.get("col_count", 0)
    header_blocks = sheet_summary.get("header_blocks", [])
    table_blocks = sheet_summary.get("table_blocks", [])

    print("\n📊 Extraction results:")
    print(f"  • Grid: {row_count} rows × {col_count} columns")
    print(f"  • Header blocks detected: {len(header_blocks)}")
    print(f"  • Table blocks detected: {len(table_blocks)}")

    # ========================================================================
    # Analyze Header Blocks
    # ========================================================================
    print("\n📋 Header blocks detail:")
    for i, block in enumerate(header_blocks, 1):
        print(f"\n  Block {i}:")
        print(
            f"    Location: Rows {block['row_start']}-{block['row_end']}, Cols {block['col_start']}-{block['col_end']}"
        )
        print(f"    Score: {block['score']:.2f}")
        print(f"    Pattern: {block['detected_pattern']}")
        print(f"    Label-value pairs: {len(block.get('label_value_pairs', []))}")

        # Show first 3 pairs
        pairs = block.get("label_value_pairs", [])[:3]
        if pairs:
            print("    Sample pairs:")
            for label, value, row, col in pairs:
                print(f"      • '{label}' = '{value}' (R{row}, C{col})")

    # ========================================================================
    # Analyze Table Blocks
    # ========================================================================
    print("\n📊 Table blocks detail:")
    for i, block in enumerate(table_blocks, 1):
        print(f"\n  Block {i}:")
        print(
            f"    Location: Rows {block['row_start']}-{block['row_end']}, Cols {block['col_start']}-{block['col_end']}"
        )
        print(f"    Score: {block['score']:.2f}")
        print(f"    Pattern: {block['detected_pattern']}")
        print(f"    Total cells: {len(block.get('content', []))}")

    # ========================================================================
    # Save Output
    # ========================================================================
    print("\n💾 Saving output...")

    output_file = output_dir / "stage_2_sheet_summary.json"
    with open(output_file, "w") as f:
        json.dump(sheet_summary, f, indent=2, default=str)
    print(f"✓ Sheet summary saved to: {output_file}")

    # Generate markdown report
    report = f"""# Stage 3: Grid Extraction and Heuristic Detection

## Summary
✅ **Stage completed successfully**

## Grid Information
- **Sheet**: `{selected_sheet}`
- **Dimensions**: {row_count} rows × {col_count} columns
- **Header blocks**: {len(header_blocks)}
- **Table blocks**: {len(table_blocks)}

## Header Blocks
"""

    for i, block in enumerate(header_blocks, 1):
        pairs_count = len(block.get("label_value_pairs", []))
        report += f"""
### Block {i}
- **Location**: Rows {block['row_start']}-{block['row_end']}, Cols {block['col_start']}-{block['col_end']}
- **Score**: {block['score']:.2f}
- **Pattern**: {block['detected_pattern']}
- **Label-value pairs**: {pairs_count}

**Sample pairs** (first 5):
"""
        for label, value, row, col in block.get("label_value_pairs", [])[:5]:
            report += f"- `{label}` = `{value}` (Row {row}, Col {col})\n"

    report += """

## Table Blocks
"""

    for i, block in enumerate(table_blocks, 1):
        report += f"""
### Block {i}
- **Location**: Rows {block['row_start']}-{block['row_end']}, Cols {block['col_start']}-{block['col_end']}
- **Score**: {block['score']:.2f}
- **Pattern**: {block['detected_pattern']}
- **Total cells**: {len(block.get('content', []))}
"""

    report += f"""

## Output Files
- `{output_file}` - Complete sheet summary JSON

## Next Step
Run: `python e2e_stages/stage_3_ai_payload.py`
"""

    report_file = output_dir / "stage_2_report.md"
    with open(report_file, "w") as f:
        f.write(report)
    print(f"✓ Report saved to: {report_file}")

    # Close workbook
    workbook.close()

    print("\n" + "=" * 80)
    print("✅ STAGE 3 COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print(f"\n📖 Review the report: {report_file}")
    print("\n▶️  Next step: python e2e_stages/stage_3_ai_payload.py")


if __name__ == "__main__":
    main()
