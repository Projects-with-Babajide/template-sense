"""
STAGE 4-5: AI Provider Setup and Payload Construction

This script initializes the AI provider and builds the AI payload.

Input:
  - e2e_stages/output/stage_0_field_dictionary.json
  - e2e_stages/output/stage_0_config.json
  - e2e_stages/output/stage_2_sheet_summary.json

Output:
  - e2e_stages/output/stage_3_ai_payload.json
  - e2e_stages/output/stage_3_report.md
"""

import json
import sys
from pathlib import Path

from dotenv import load_dotenv

# Add src to path BEFORE imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from template_sense.adapters.excel_adapter import ExcelWorkbook  # noqa: E402
from template_sense.ai_payload_schema import build_ai_payload  # noqa: E402
from template_sense.ai_providers.factory import get_ai_provider  # noqa: E402
from template_sense.extraction.sheet_extractor import extract_raw_grid  # noqa: E402
from template_sense.file_loader import load_excel_file  # noqa: E402

load_dotenv()


def main():
    print("=" * 80)
    print("STAGE 4-5: AI PROVIDER SETUP AND PAYLOAD CONSTRUCTION")
    print("=" * 80)

    output_dir = Path("e2e_stages/output")

    # ========================================================================
    # Load Previous Stage Outputs
    # ========================================================================
    print("\n📥 Loading previous stage outputs...")

    config_file = output_dir / "stage_0_config.json"
    field_dict_file = output_dir / "stage_0_field_dictionary.json"
    sheet_summary_file = output_dir / "stage_2_sheet_summary.json"

    if not all([config_file.exists(), field_dict_file.exists(), sheet_summary_file.exists()]):
        print("❌ Error: Previous stage outputs not found!")
        print("Please run previous stages first.")
        sys.exit(1)

    with open(config_file) as f:
        config = json.load(f)
    with open(field_dict_file) as f:
        field_dictionary = json.load(f)
    with open(sheet_summary_file) as f:
        sheet_summary = json.load(f)

    print(f"✓ Config loaded: {config.get('test_file')}")
    print(f"✓ Field dictionary: {len(field_dictionary)} fields")
    print("✓ Sheet summary loaded")

    # Load Excel file to extract grid for adjacent cell context (BAT-53)
    print("\n📂 Loading Excel file for grid extraction...")
    test_file = config.get("test_file")
    raw_workbook = load_excel_file(Path(test_file))
    workbook = ExcelWorkbook(raw_workbook)
    sheet_name = sheet_summary.get("sheet_name", workbook.get_sheet_names()[0])
    grid = extract_raw_grid(workbook, sheet_name)
    workbook.close()
    print(f"✓ Grid extracted: {len(grid)} rows × {len(grid[0]) if grid else 0} columns")

    # ========================================================================
    # Stage 4: AI Provider Setup
    # ========================================================================
    print("\n🤖 Stage 4: Initializing AI provider...")

    ai_provider = get_ai_provider()
    print("✓ AI provider initialized")
    print(f"  • Provider: {ai_provider.config.provider}")
    print(f"  • Model: {ai_provider.config.model or 'default'}")
    print(f"  • Timeout: {ai_provider.config.timeout_seconds}s")

    # ========================================================================
    # Stage 5: AI Payload Construction
    # ========================================================================
    print("\n🏗️  Stage 5: Building AI payload...")

    ai_payload = build_ai_payload(sheet_summary, field_dictionary, grid=grid)
    print("✓ AI payload built successfully (with adjacent cell context from BAT-53)")

    # Extract statistics
    header_candidates = ai_payload.get("header_candidates", [])
    table_candidates = ai_payload.get("table_candidates", [])

    print("\n📊 Payload contents:")
    print(f"  • Sheet name: {ai_payload.get('sheet_name')}")
    print(f"  • Header candidates: {len(header_candidates)}")
    print(f"  • Table candidates: {len(table_candidates)}")
    print(f"  • Field dictionary: {len(ai_payload.get('field_dictionary', {}))} keys")

    # ========================================================================
    # Analyze Payload Detail
    # ========================================================================
    print("\n📋 Header candidates (first 10):")
    for i, candidate in enumerate(header_candidates[:10], 1):
        print(f"  {i}. Label: '{candidate.get('label')}' → Value: '{candidate.get('value')}'")
        print(
            f"     Location: Row {candidate.get('row')}, Col {candidate.get('col')}, Score: {candidate.get('score', 0):.2f}"
        )

    print("\n📊 Table candidates:")
    for i, table in enumerate(table_candidates, 1):
        print(f"\n  Table {i}:")
        print(
            f"    Location: Rows {table.get('start_row')}-{table.get('end_row')}, Cols {table.get('start_col')}-{table.get('end_col')}"
        )
        print(f"    Score: {table.get('score', 0):.2f}")
        print(f"    Total data rows: {table.get('total_data_rows', 0)}")

        if table.get("header_row"):
            header_row = table["header_row"]
            print(f"    Header row: {header_row.get('row_index')}")
            cells = header_row.get("cells", [])
            print(f"    Header cells ({len(cells)}):")
            for cell in cells[:5]:
                print(f"      • Col {cell.get('col')}: '{cell.get('value')}'")

        if table.get("sample_data_rows"):
            print(f"    Sample data rows: {len(table['sample_data_rows'])}")

    # ========================================================================
    # Save Output
    # ========================================================================
    print("\n💾 Saving output...")

    # Save AI payload
    output_file = output_dir / "stage_3_ai_payload.json"
    with open(output_file, "w") as f:
        json.dump(ai_payload, f, indent=2, default=str)
    print(f"✓ AI payload saved to: {output_file}")

    # Save AI provider info
    provider_info = {
        "provider": ai_provider.config.provider,
        "model": ai_provider.config.model or "default",
        "timeout_seconds": ai_provider.config.timeout_seconds,
    }
    provider_file = output_dir / "stage_3_ai_provider.json"
    with open(provider_file, "w") as f:
        json.dump(provider_info, f, indent=2)
    print(f"✓ AI provider info saved to: {provider_file}")

    # Generate markdown report
    report = f"""# Stage 4-5: AI Provider Setup and Payload Construction

## Summary
✅ **Stage completed successfully**

## Stage 4: AI Provider
- **Provider**: {ai_provider.config.provider}
- **Model**: {ai_provider.config.model or 'default'}
- **Timeout**: {ai_provider.config.timeout_seconds}s

## Stage 5: AI Payload
- **Sheet name**: `{ai_payload.get('sheet_name')}`
- **Header candidates**: {len(header_candidates)}
- **Table candidates**: {len(table_candidates)}
- **Field dictionary keys**: {len(ai_payload.get('field_dictionary', {}))}

### Header Candidates (First 10)
"""

    for i, candidate in enumerate(header_candidates[:10], 1):
        report += f"{i}. **`{candidate.get('label')}`** = `{candidate.get('value')}` (Row {candidate.get('row')}, Col {candidate.get('col')}, Score: {candidate.get('score', 0):.2f})\n"

    report += "\n### Table Candidates\n"

    for i, table in enumerate(table_candidates, 1):
        report += f"""
#### Table {i}
- **Location**: Rows {table.get('start_row')}-{table.get('end_row')}, Cols {table.get('start_col')}-{table.get('end_col')}
- **Score**: {table.get('score', 0):.2f}
- **Total data rows**: {table.get('total_data_rows', 0)}
"""
        if table.get("header_row"):
            header_row = table["header_row"]
            cells = header_row.get("cells", [])
            report += f"- **Header row**: {header_row.get('row_index')}\n"
            report += f"- **Header cells** ({len(cells)}):\n"
            for cell in cells[:5]:
                report += f"  - Col {cell.get('col')}: `{cell.get('value')}`\n"

    report += f"""

## Output Files
- `{output_file}` - Complete AI payload JSON
- `{provider_file}` - AI provider configuration JSON

## Next Step
⚠️  **The next stage makes real AI API calls!**

Run: `python e2e_stages/stage_4_classification.py`
"""

    report_file = output_dir / "stage_3_report.md"
    with open(report_file, "w") as f:
        f.write(report)
    print(f"✓ Report saved to: {report_file}")

    print("\n" + "=" * 80)
    print("✅ STAGE 4-5 COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print(f"\n📖 Review the report: {report_file}")
    print("\n⚠️  Next stage makes real AI API calls!")
    print("▶️  Next step: python e2e_stages/stage_4_classification.py")


if __name__ == "__main__":
    main()
