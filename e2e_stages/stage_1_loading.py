"""
STAGE 1-2: File Loading and Workbook Setup

This script loads the Excel file and extracts basic workbook information.

Input:
  - e2e_stages/output/stage_0_config.json

Output:
  - e2e_stages/output/stage_1_workbook_info.json
  - e2e_stages/output/stage_1_report.md
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from template_sense.adapters.excel_adapter import ExcelWorkbook
from template_sense.file_loader import load_excel_file


def main():
    print("=" * 80)
    print("STAGE 1-2: FILE LOADING AND WORKBOOK SETUP")
    print("=" * 80)

    output_dir = Path("e2e_stages/output")
    output_dir.mkdir(parents=True, exist_ok=True)

    # ========================================================================
    # Load Configuration from Stage 0
    # ========================================================================
    print("\n📥 Loading configuration from Stage 0...")
    config_file = output_dir / "stage_0_config.json"

    if not config_file.exists():
        print(f"❌ Error: {config_file} not found!")
        print("Please run stage_0_setup.py first.")
        sys.exit(1)

    with open(config_file) as f:
        config = json.load(f)

    test_file = Path(config["test_file"])
    print(f"✓ Test file: {test_file}")

    # ========================================================================
    # Load Excel File
    # ========================================================================
    print("\n📂 Loading Excel file...")
    raw_workbook = load_excel_file(test_file)
    workbook = ExcelWorkbook(raw_workbook)
    print("✓ Workbook loaded successfully")

    # ========================================================================
    # Extract Workbook Information
    # ========================================================================
    print("\n📊 Extracting workbook information...")
    sheet_names = workbook.get_sheet_names()
    print(f"✓ Found {len(sheet_names)} sheet(s)")

    # Select first sheet
    selected_sheet = sheet_names[0]
    print(f"✓ Selected sheet: '{selected_sheet}'")

    # Get sheet dimensions
    sheet = workbook._workbook[selected_sheet]
    max_row = sheet.max_row
    max_col = sheet.max_column
    print(f"✓ Sheet dimensions: {max_row} rows × {max_col} columns")

    # ========================================================================
    # Save Output
    # ========================================================================
    print("\n💾 Saving output...")

    workbook_info = {
        "file_path": str(test_file),
        "file_size_bytes": test_file.stat().st_size,
        "sheet_names": sheet_names,
        "selected_sheet": selected_sheet,
        "max_row": max_row,
        "max_column": max_col,
        "total_sheets": len(sheet_names),
    }

    output_file = output_dir / "stage_1_workbook_info.json"
    with open(output_file, "w") as f:
        json.dump(workbook_info, f, indent=2)
    print(f"✓ Workbook info saved to: {output_file}")

    # Generate markdown report
    report = f"""# Stage 1-2: File Loading and Workbook Setup

## Summary
✅ **Stage completed successfully**

## Workbook Information
- **File**: `{test_file}`
- **File size**: {test_file.stat().st_size:,} bytes
- **Total sheets**: {len(sheet_names)}
- **Selected sheet**: `{selected_sheet}`
- **Dimensions**: {max_row} rows × {max_col} columns

## Sheet Names
"""
    for i, name in enumerate(sheet_names, 1):
        marker = "← **SELECTED**" if name == selected_sheet else ""
        report += f"{i}. `{name}` {marker}\n"

    report += f"""

## Output Files
- `{output_file}` - Workbook information JSON

## Next Step
Run: `python e2e_stages/stage_2_extraction.py`
"""

    report_file = output_dir / "stage_1_report.md"
    with open(report_file, "w") as f:
        f.write(report)
    print(f"✓ Report saved to: {report_file}")

    # Close workbook
    workbook.close()

    print("\n" + "=" * 80)
    print("✅ STAGE 1-2 COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print(f"\n📖 Review the report: {report_file}")
    print("\n▶️  Next step: python e2e_stages/stage_2_extraction.py")


if __name__ == "__main__":
    main()
