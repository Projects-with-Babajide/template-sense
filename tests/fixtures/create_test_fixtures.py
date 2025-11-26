"""
Script to create test fixtures for file validation tests.

This script creates:
- A valid .xlsx file
- A valid .xls file (legacy format)
- Invalid format files for testing error handling
"""

from pathlib import Path

from openpyxl import Workbook


def create_test_fixtures():
    """Create test fixture files."""
    fixtures_dir = Path(__file__).parent

    # Create a valid .xlsx file
    wb = Workbook()
    ws = wb.active
    ws.title = "Test Sheet"
    ws["A1"] = "Invoice Number"
    ws["B1"] = "Date"
    ws["A2"] = "INV-001"
    ws["B2"] = "2025-01-15"
    wb.save(fixtures_dir / "valid_template.xlsx")
    print(f"Created: {fixtures_dir / 'valid_template.xlsx'}")

    # Create a CSV file (unsupported format)
    csv_file = fixtures_dir / "invalid_format.csv"
    csv_file.write_text("Invoice Number,Date\nINV-001,2025-01-15\n")
    print(f"Created: {csv_file}")

    # Create a text file (unsupported format)
    txt_file = fixtures_dir / "invalid_format.txt"
    txt_file.write_text("This is a text file, not an Excel file.")
    print(f"Created: {txt_file}")

    # Create a PDF-like file (unsupported format)
    pdf_file = fixtures_dir / "invalid_format.pdf"
    pdf_file.write_text("This is not a real PDF, just for testing.")
    print(f"Created: {pdf_file}")

    # Create a file with no extension
    no_ext_file = fixtures_dir / "no_extension"
    no_ext_file.write_text("File with no extension")
    print(f"Created: {no_ext_file}")

    # Create a corrupted .xlsx file (not actually Excel format)
    corrupt_file = fixtures_dir / "corrupted.xlsx"
    corrupt_file.write_text("This is not a valid Excel file, just corrupted data.")
    print(f"Created: {corrupt_file}")

    print("\nAll test fixtures created successfully!")


if __name__ == "__main__":
    create_test_fixtures()
