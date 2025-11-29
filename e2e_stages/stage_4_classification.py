"""
STAGE 6: AI Classification

This script performs AI classification of headers, columns, and line items.
⚠️  WARNING: This stage makes real AI API calls and consumes credits/tokens!

Input:
  - e2e_stages/output/stage_3_ai_payload.json
  - e2e_stages/output/stage_3_ai_provider.json

Output:
  - e2e_stages/output/stage_4_classified_headers.json
  - e2e_stages/output/stage_4_classified_columns.json
  - e2e_stages/output/stage_4_line_items.json
  - e2e_stages/output/stage_4_report.md
"""

import json
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from template_sense.ai.header_classification import classify_header_fields
from template_sense.ai.line_item_extraction import extract_line_items
from template_sense.ai.table_column_classification import classify_table_columns
from template_sense.ai_providers.factory import get_ai_provider


def main():
    print("=" * 80)
    print("STAGE 6: AI CLASSIFICATION")
    print("=" * 80)
    print("\n⚠️  WARNING: This stage makes real AI API calls!")
    print("This will consume API credits/tokens.")
    print("\nPress Ctrl+C to cancel, or press Enter to continue...")
    try:
        input()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        sys.exit(0)

    output_dir = Path("e2e_stages/output")

    # ========================================================================
    # Load Previous Stage Outputs
    # ========================================================================
    print("\n📥 Loading previous stage outputs...")

    payload_file = output_dir / "stage_3_ai_payload.json"
    provider_file = output_dir / "stage_3_ai_provider.json"

    if not all([payload_file.exists(), provider_file.exists()]):
        print("❌ Error: Previous stage outputs not found!")
        print("Please run previous stages first.")
        sys.exit(1)

    with open(payload_file) as f:
        ai_payload = json.load(f)
    with open(provider_file) as f:
        provider_info = json.load(f)

    print("✓ AI payload loaded")
    print(f"✓ Using provider: {provider_info['provider']} ({provider_info['model']})")

    # ========================================================================
    # Initialize AI Provider
    # ========================================================================
    print("\n🤖 Initializing AI provider...")
    ai_provider = get_ai_provider()
    print("✓ AI provider ready")

    # ========================================================================
    # Stage 6a: Header Classification
    # ========================================================================
    print("\n📋 Stage 6a: Classifying header fields...")
    print("⏳ Making AI API call...")

    start_time = time.perf_counter()
    classified_headers = classify_header_fields(ai_provider, ai_payload)
    header_time = time.perf_counter() - start_time

    print(f"✓ Classified {len(classified_headers)} header fields in {header_time:.2f}s")

    # Show statistics
    with_confidence = sum(1 for h in classified_headers if h.model_confidence is not None)
    avg_confidence = (
        sum(h.model_confidence for h in classified_headers if h.model_confidence is not None)
        / with_confidence
        if with_confidence > 0
        else 0
    )

    print(f"  • Fields with confidence: {with_confidence}/{len(classified_headers)}")
    if avg_confidence > 0:
        print(f"  • Average confidence: {avg_confidence:.1%}")

    print("\n  Sample classified headers (first 5):")
    for i, header in enumerate(classified_headers[:5], 1):
        print(f"    {i}. '{header.raw_label}' = '{header.raw_value}'")
        print(f"       Row {header.row_index}, Col {header.col_index}")
        if header.model_confidence:
            print(f"       AI Confidence: {header.model_confidence:.1%}")

    # ========================================================================
    # Stage 6b: Column Classification
    # ========================================================================
    print("\n📊 Stage 6b: Classifying table columns...")
    print("⏳ Making AI API call...")

    start_time = time.perf_counter()
    classified_columns = classify_table_columns(ai_provider, ai_payload)
    column_time = time.perf_counter() - start_time

    print(f"✓ Classified {len(classified_columns)} table columns in {column_time:.2f}s")

    # Show statistics
    with_confidence = sum(1 for c in classified_columns if c.model_confidence is not None)
    avg_confidence = (
        sum(c.model_confidence for c in classified_columns if c.model_confidence is not None)
        / with_confidence
        if with_confidence > 0
        else 0
    )

    print(f"  • Columns with confidence: {with_confidence}/{len(classified_columns)}")
    if avg_confidence > 0:
        print(f"  • Average confidence: {avg_confidence:.1%}")

    print("\n  Sample classified columns (first 5):")
    for i, column in enumerate(classified_columns[:5], 1):
        print(f"    {i}. '{column.raw_label}' (Col {column.col_index})")
        if column.model_confidence:
            print(f"       AI Confidence: {column.model_confidence:.1%}")
        if column.raw_value_examples:
            print(f"       Sample values: {column.raw_value_examples[:3]}")

    # ========================================================================
    # Stage 6c: Line Item Extraction
    # ========================================================================
    print("\n📦 Stage 6c: Extracting line items...")
    print("⏳ Making AI API call...")

    start_time = time.perf_counter()
    extracted_line_items = extract_line_items(ai_provider, ai_payload)
    line_item_time = time.perf_counter() - start_time

    print(f"✓ Extracted {len(extracted_line_items)} line items in {line_item_time:.2f}s")

    print("\n  Sample line items (first 3):")
    for i, item in enumerate(extracted_line_items[:3], 1):
        print(f"    {i}. Row {item.row_index}, Table {item.table_index}")
        print(f"       Fields: {len(item.field_values)}")
        print(f"       Sample: {dict(list(item.field_values.items())[:3])}")

    # ========================================================================
    # Save Output
    # ========================================================================
    print("\n💾 Saving output...")

    # Convert dataclasses to dicts for JSON serialization
    headers_data = [
        {
            "canonical_key": h.canonical_key,
            "raw_label": h.raw_label,
            "raw_value": h.raw_value,
            "block_index": h.block_index,
            "row_index": h.row_index,
            "col_index": h.col_index,
            "model_confidence": h.model_confidence,
            "metadata": h.metadata,
        }
        for h in classified_headers
    ]

    columns_data = [
        {
            "canonical_key": c.canonical_key,
            "raw_label": c.raw_label,
            "raw_value_examples": c.raw_value_examples,
            "table_index": c.table_index,
            "col_index": c.col_index,
            "row_start": c.row_start,
            "row_end": c.row_end,
            "model_confidence": c.model_confidence,
            "metadata": c.metadata,
        }
        for c in classified_columns
    ]

    line_items_data = [
        {
            "row_index": item.row_index,
            "table_index": item.table_index,
            "field_values": item.field_values,
            "model_confidence": item.model_confidence,
            "metadata": item.metadata,
        }
        for item in extracted_line_items
    ]

    # Save headers
    headers_file = output_dir / "stage_4_classified_headers.json"
    with open(headers_file, "w") as f:
        json.dump(headers_data, f, indent=2)
    print(f"✓ Headers saved to: {headers_file}")

    # Save columns
    columns_file = output_dir / "stage_4_classified_columns.json"
    with open(columns_file, "w") as f:
        json.dump(columns_data, f, indent=2)
    print(f"✓ Columns saved to: {columns_file}")

    # Save line items
    line_items_file = output_dir / "stage_4_line_items.json"
    with open(line_items_file, "w") as f:
        json.dump(line_items_data, f, indent=2)
    print(f"✓ Line items saved to: {line_items_file}")

    # Save timing info
    timing = {
        "header_classification_seconds": header_time,
        "column_classification_seconds": column_time,
        "line_item_extraction_seconds": line_item_time,
        "total_seconds": header_time + column_time + line_item_time,
    }
    timing_file = output_dir / "stage_4_timing.json"
    with open(timing_file, "w") as f:
        json.dump(timing, f, indent=2)
    print(f"✓ Timing saved to: {timing_file}")

    # Generate markdown report
    header_conf = [h.model_confidence for h in classified_headers if h.model_confidence]
    column_conf = [c.model_confidence for c in classified_columns if c.model_confidence]

    report = f"""# Stage 6: AI Classification

## Summary
✅ **Stage completed successfully**

## Performance
- **Header classification**: {header_time:.2f}s
- **Column classification**: {column_time:.2f}s
- **Line item extraction**: {line_item_time:.2f}s
- **Total time**: {timing['total_seconds']:.2f}s

## Results

### Headers
- **Total classified**: {len(classified_headers)}
- **With confidence scores**: {len(header_conf)}
- **Average confidence**: {sum(header_conf)/len(header_conf):.1%} (if available)

**Sample headers** (first 10):
"""

    for i, header in enumerate(classified_headers[:10], 1):
        conf = f" (confidence: {header.model_confidence:.1%})" if header.model_confidence else ""
        report += f"{i}. `{header.raw_label}` = `{header.raw_value}` (Row {header.row_index}, Col {header.col_index}){conf}\n"

    report += f"""

### Columns
- **Total classified**: {len(classified_columns)}
- **With confidence scores**: {len(column_conf)}
- **Average confidence**: {sum(column_conf)/len(column_conf):.1%} (if available)

**Sample columns** (first 10):
"""

    for i, column in enumerate(classified_columns[:10], 1):
        conf = f" (confidence: {column.model_confidence:.1%})" if column.model_confidence else ""
        report += f"{i}. `{column.raw_label}` (Col {column.col_index}){conf}\n"

    report += f"""

### Line Items
- **Total extracted**: {len(extracted_line_items)}

**Sample line items** (first 5):
"""

    for i, item in enumerate(extracted_line_items[:5], 1):
        report += f"{i}. Row {item.row_index}, Table {item.table_index} - {len(item.field_values)} fields\n"

    report += f"""

## Output Files
- `{headers_file}` - Classified headers JSON
- `{columns_file}` - Classified columns JSON
- `{line_items_file}` - Extracted line items JSON
- `{timing_file}` - Performance timing JSON

## Next Step
Run: `python e2e_stages/stage_5_translation.py`
"""

    report_file = output_dir / "stage_4_report.md"
    with open(report_file, "w") as f:
        f.write(report)
    print(f"✓ Report saved to: {report_file}")

    print("\n" + "=" * 80)
    print("✅ STAGE 6 COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print(f"\n📖 Review the report: {report_file}")
    print("\n▶️  Next step: python e2e_stages/stage_5_translation.py")


if __name__ == "__main__":
    main()
