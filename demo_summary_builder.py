"""
Demo script to test summary_builder with real invoice templates.

This script demonstrates the sheet structure summary builder by processing
real invoice template files and displaying the AI-ready JSON output.
"""

import json
from pathlib import Path

from template_sense.adapters.excel_adapter import ExcelWorkbook
from template_sense.extraction.summary_builder import build_sheet_summary
from template_sense.file_loader import load_excel_file


def demo_invoice_template(file_path: Path, sheet_name: str | None = None):
    """
    Process an invoice template and display the summary.

    Args:
        file_path: Path to the Excel invoice template
        sheet_name: Optional sheet name (uses first sheet if None)
    """
    print(f"\n{'=' * 80}")
    print(f"Processing: {file_path.name}")
    print(f"{'=' * 80}\n")

    try:
        # Load workbook
        raw_workbook = load_excel_file(file_path)
        workbook = ExcelWorkbook(raw_workbook)

        # Get sheet names
        sheet_names = workbook.get_sheet_names()
        print(f"Available sheets: {sheet_names}")

        # Use specified sheet or first sheet
        target_sheet = sheet_name or sheet_names[0]
        print(f"Analyzing sheet: '{target_sheet}'\n")

        # Build summary
        summary = build_sheet_summary(workbook, sheet_name=target_sheet, min_score=0.5)

        # Display summary
        print("=" * 80)
        print("SHEET STRUCTURE SUMMARY")
        print("=" * 80)
        print(json.dumps(summary, indent=2, ensure_ascii=False))

        # Display statistics
        print("\n" + "=" * 80)
        print("SUMMARY STATISTICS")
        print("=" * 80)
        print(f"Sheet Name: {summary['sheet_name']}")
        print(f"Header Blocks: {len(summary['header_blocks'])}")
        print(f"Table Blocks: {len(summary['table_blocks'])}")

        # Display header block details
        if summary["header_blocks"]:
            print("\nHeader Blocks Details:")
            for idx, block in enumerate(summary["header_blocks"], 1):
                print(f"  Block {idx}:")
                print(
                    f"    Location: R{block['row_start']}:R{block['row_end']}, "
                    f"C{block['col_start']}:C{block['col_end']}"
                )
                print(f"    Score: {block['score']}")
                print(f"    Pattern: {block['detected_pattern']}")
                print(f"    Content cells: {len(block['content'])}")
                print(f"    Label-value pairs: {len(block['label_value_pairs'])}")

                # Show first few label-value pairs
                if block["label_value_pairs"]:
                    print("    Sample pairs:")
                    for pair in block["label_value_pairs"][:3]:
                        label = pair["label"] or "(no label)"
                        value = pair["value"]
                        print(f"      - {label}: {value}")

        # Display table block details
        if summary["table_blocks"]:
            print("\nTable Blocks Details:")
            for idx, block in enumerate(summary["table_blocks"], 1):
                print(f"  Block {idx}:")
                print(
                    f"    Location: R{block['row_start']}:R{block['row_end']}, "
                    f"C{block['col_start']}:C{block['col_end']}"
                )
                print(f"    Score: {block['score']}")
                print(f"    Pattern: {block['detected_pattern']}")
                print(f"    Content cells: {len(block['content'])}")

                if block["header_row"]:
                    print(f"    Header Row: R{block['header_row']['row_index']}")
                    print(f"    Header Score: {block['header_row']['score']}")
                    print(f"    Column Headers: {block['header_row']['values']}")
                else:
                    print("    Header Row: Not detected")

        workbook.close()

    except Exception as e:
        print(f"Error processing {file_path.name}: {e}")
        import traceback

        traceback.print_exc()


def main():
    """Run demo on all invoice templates."""
    fixtures_dir = Path("tests/fixtures/invoice_templates")

    if not fixtures_dir.exists():
        print(f"Error: {fixtures_dir} does not exist")
        return

    # Get all .xlsx files
    invoice_files = sorted(fixtures_dir.glob("*.xlsx"))

    if not invoice_files:
        print(f"No .xlsx files found in {fixtures_dir}")
        return

    print(f"\nFound {len(invoice_files)} invoice template(s)")
    print("Testing summary_builder module with real templates...\n")

    # Process each template
    for file_path in invoice_files:
        demo_invoice_template(file_path)

    print(f"\n{'=' * 80}")
    print("Demo complete!")
    print(f"{'=' * 80}\n")


if __name__ == "__main__":
    main()
