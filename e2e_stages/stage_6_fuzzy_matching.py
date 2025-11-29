"""
STAGE 8: Fuzzy Matching

This script performs fuzzy matching of translated labels to canonical field keys.

Input:
  - e2e_stages/output/stage_0_field_dictionary.json
  - e2e_stages/output/stage_4_classified_headers.json
  - e2e_stages/output/stage_4_classified_columns.json
  - e2e_stages/output/stage_5_translations.json

Output:
  - e2e_stages/output/stage_6_matched_headers.json
  - e2e_stages/output/stage_6_matched_columns.json
  - e2e_stages/output/stage_6_report.md
"""

import json
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from template_sense.ai.translation import TranslatedLabel
from template_sense.constants import DEFAULT_AUTO_MAPPING_THRESHOLD, DEFAULT_TARGET_LANGUAGE
from template_sense.mapping.fuzzy_field_matching import match_fields


def main():
    print("=" * 80)
    print("STAGE 8: FUZZY MATCHING")
    print("=" * 80)

    output_dir = Path("e2e_stages/output")

    # ========================================================================
    # Load Previous Stage Outputs
    # ========================================================================
    print("\n📥 Loading previous stage outputs...")

    field_dict_file = output_dir / "stage_0_field_dictionary.json"
    headers_file = output_dir / "stage_4_classified_headers.json"
    columns_file = output_dir / "stage_4_classified_columns.json"
    translations_file = output_dir / "stage_5_translations.json"

    if not all(
        [
            field_dict_file.exists(),
            headers_file.exists(),
            columns_file.exists(),
            translations_file.exists(),
        ]
    ):
        print("❌ Error: Previous stage outputs not found!")
        print("Please run previous stages first.")
        sys.exit(1)

    with open(field_dict_file) as f:
        field_dictionary = json.load(f)
    with open(headers_file) as f:
        classified_headers = json.load(f)
    with open(columns_file) as f:
        classified_columns = json.load(f)
    with open(translations_file) as f:
        translations_data = json.load(f)

    translation_map = translations_data["translation_map"]

    print(f"✓ Field dictionary: {len(field_dictionary)} fields")
    print(f"✓ Classified headers: {len(classified_headers)}")
    print(f"✓ Classified columns: {len(classified_columns)}")
    print(f"✓ Translation map: {len(translation_map)} entries")

    # ========================================================================
    # Prepare Translated Labels for Headers
    # ========================================================================
    print(f"\n📋 Matching headers (threshold: {DEFAULT_AUTO_MAPPING_THRESHOLD})...")

    header_translated_labels = []
    for header in classified_headers:
        raw_label = header.get("raw_label", "")
        if not raw_label:
            continue

        # Get translation or use original
        translation = translation_map.get(
            raw_label,
            {
                "translated_text": raw_label,
                "detected_source_language": None,
                "target_language": DEFAULT_TARGET_LANGUAGE,
            },
        )

        # Create TranslatedLabel instance
        tl = TranslatedLabel(
            original_text=raw_label,
            translated_text=translation["translated_text"],
            detected_source_language=translation.get("detected_source_language"),
            target_language=translation.get("target_language", DEFAULT_TARGET_LANGUAGE),
            model_confidence=translation.get("model_confidence"),
            metadata=translation.get("metadata"),
        )
        header_translated_labels.append(tl)

    # Match headers
    print(f"⏳ Matching {len(header_translated_labels)} header fields...")
    start_time = time.perf_counter()

    header_match_results = match_fields(
        translated_labels=header_translated_labels,
        field_dictionary=field_dictionary,
        threshold=DEFAULT_AUTO_MAPPING_THRESHOLD,
    )

    header_time = time.perf_counter() - start_time

    print(f"✓ Matched headers in {header_time:.3f}s")

    # Analyze matches
    matched_headers = sum(1 for r in header_match_results if r.canonical_key)
    unmatched_headers = len(header_match_results) - matched_headers

    print(f"  • Matched: {matched_headers} ({matched_headers/len(header_match_results)*100:.1f}%)")
    print(
        f"  • Unmatched: {unmatched_headers} ({unmatched_headers/len(header_match_results)*100:.1f}%)"
    )

    # Show sample matches
    print("\n  Sample header matches (first 10):")
    for i, result in enumerate(header_match_results[:10], 1):
        if result.canonical_key:
            print(
                f"    {i}. ✓ '{result.translated_text}' → '{result.canonical_key}' (score: {result.match_score:.1f})"
            )
        else:
            print(
                f"    {i}. ✗ '{result.translated_text}' → NO MATCH (best: {result.match_score:.1f})"
            )

    # ========================================================================
    # Prepare Translated Labels for Columns
    # ========================================================================
    print(f"\n📊 Matching columns (threshold: {DEFAULT_AUTO_MAPPING_THRESHOLD})...")

    column_translated_labels = []
    for column in classified_columns:
        raw_label = column.get("raw_label", "")
        if not raw_label:
            continue

        # Get translation or use original
        translation = translation_map.get(
            raw_label,
            {
                "translated_text": raw_label,
                "detected_source_language": None,
                "target_language": DEFAULT_TARGET_LANGUAGE,
            },
        )

        # Create TranslatedLabel instance
        tl = TranslatedLabel(
            original_text=raw_label,
            translated_text=translation["translated_text"],
            detected_source_language=translation.get("detected_source_language"),
            target_language=translation.get("target_language", DEFAULT_TARGET_LANGUAGE),
            model_confidence=translation.get("model_confidence"),
            metadata=translation.get("metadata"),
        )
        column_translated_labels.append(tl)

    # Match columns
    print(f"⏳ Matching {len(column_translated_labels)} column fields...")
    start_time = time.perf_counter()

    column_match_results = match_fields(
        translated_labels=column_translated_labels,
        field_dictionary=field_dictionary,
        threshold=DEFAULT_AUTO_MAPPING_THRESHOLD,
    )

    column_time = time.perf_counter() - start_time

    print(f"✓ Matched columns in {column_time:.3f}s")

    # Analyze matches
    matched_columns = sum(1 for r in column_match_results if r.canonical_key)
    unmatched_columns = len(column_match_results) - matched_columns

    print(f"  • Matched: {matched_columns} ({matched_columns/len(column_match_results)*100:.1f}%)")
    print(
        f"  • Unmatched: {unmatched_columns} ({unmatched_columns/len(column_match_results)*100:.1f}%)"
    )

    # Show sample matches
    print("\n  Sample column matches (first 10):")
    for i, result in enumerate(column_match_results[:10], 1):
        if result.canonical_key:
            print(
                f"    {i}. ✓ '{result.translated_text}' → '{result.canonical_key}' (score: {result.match_score:.1f})"
            )
        else:
            print(
                f"    {i}. ✗ '{result.translated_text}' → NO MATCH (best: {result.match_score:.1f})"
            )

    # ========================================================================
    # Save Output
    # ========================================================================
    print("\n💾 Saving output...")

    # Convert match results to dicts
    header_matches_data = [
        {
            "original_text": r.original_text,
            "translated_text": r.translated_text,
            "canonical_key": r.canonical_key,
            "match_score": r.match_score,
            "matched_variant": r.matched_variant,
            "detected_source_language": r.detected_source_language,
        }
        for r in header_match_results
    ]

    column_matches_data = [
        {
            "original_text": r.original_text,
            "translated_text": r.translated_text,
            "canonical_key": r.canonical_key,
            "match_score": r.match_score,
            "matched_variant": r.matched_variant,
            "detected_source_language": r.detected_source_language,
        }
        for r in column_match_results
    ]

    # Save header matches
    headers_output = output_dir / "stage_6_matched_headers.json"
    with open(headers_output, "w") as f:
        json.dump(header_matches_data, f, indent=2)
    print(f"✓ Header matches saved to: {headers_output}")

    # Save column matches
    columns_output = output_dir / "stage_6_matched_columns.json"
    with open(columns_output, "w") as f:
        json.dump(column_matches_data, f, indent=2)
    print(f"✓ Column matches saved to: {columns_output}")

    # Save statistics
    stats = {
        "threshold": DEFAULT_AUTO_MAPPING_THRESHOLD,
        "headers": {
            "total": len(header_match_results),
            "matched": matched_headers,
            "unmatched": unmatched_headers,
            "match_rate": matched_headers / len(header_match_results)
            if header_match_results
            else 0,
            "avg_score": sum(r.match_score for r in header_match_results)
            / len(header_match_results)
            if header_match_results
            else 0,
            "matching_time_seconds": header_time,
        },
        "columns": {
            "total": len(column_match_results),
            "matched": matched_columns,
            "unmatched": unmatched_columns,
            "match_rate": matched_columns / len(column_match_results)
            if column_match_results
            else 0,
            "avg_score": sum(r.match_score for r in column_match_results)
            / len(column_match_results)
            if column_match_results
            else 0,
            "matching_time_seconds": column_time,
        },
    }

    stats_file = output_dir / "stage_6_statistics.json"
    with open(stats_file, "w") as f:
        json.dump(stats, f, indent=2)
    print(f"✓ Statistics saved to: {stats_file}")

    # Generate markdown report
    report = f"""# Stage 8: Fuzzy Matching

## Summary
✅ **Stage completed successfully**

## Configuration
- **Threshold**: {DEFAULT_AUTO_MAPPING_THRESHOLD}
- **Algorithm**: token_set_ratio (rapidfuzz)

## Performance
- **Header matching**: {header_time:.3f}s ({len(header_match_results)/header_time:.0f} fields/sec)
- **Column matching**: {column_time:.3f}s ({len(column_match_results)/column_time:.0f} fields/sec)
- **Total time**: {header_time + column_time:.3f}s

## Headers
- **Total**: {len(header_match_results)}
- **Matched**: {matched_headers} ({matched_headers/len(header_match_results)*100:.1f}%)
- **Unmatched**: {unmatched_headers} ({unmatched_headers/len(header_match_results)*100:.1f}%)
- **Average score**: {stats['headers']['avg_score']:.1f}

### Matched Headers (Top 15)
"""

    for i, r in enumerate([r for r in header_match_results if r.canonical_key][:15], 1):
        report += (
            f"{i}. `{r.translated_text}` → **`{r.canonical_key}`** (score: {r.match_score:.1f})\n"
        )

    if unmatched_headers > 0:
        report += """

### Unmatched Headers (First 10)
"""
        for i, r in enumerate([r for r in header_match_results if not r.canonical_key][:10], 1):
            report += f"{i}. `{r.translated_text}` (best score: {r.match_score:.1f})\n"

    report += f"""

## Columns
- **Total**: {len(column_match_results)}
- **Matched**: {matched_columns} ({matched_columns/len(column_match_results)*100:.1f}%)
- **Unmatched**: {unmatched_columns} ({unmatched_columns/len(column_match_results)*100:.1f}%)
- **Average score**: {stats['columns']['avg_score']:.1f}

### Matched Columns (Top 15)
"""

    for i, r in enumerate([r for r in column_match_results if r.canonical_key][:15], 1):
        report += (
            f"{i}. `{r.translated_text}` → **`{r.canonical_key}`** (score: {r.match_score:.1f})\n"
        )

    if unmatched_columns > 0:
        report += """

### Unmatched Columns (First 10)
"""
        for i, r in enumerate([r for r in column_match_results if not r.canonical_key][:10], 1):
            report += f"{i}. `{r.translated_text}` (best score: {r.match_score:.1f})\n"

    report += f"""

## Output Files
- `{headers_output}` - Matched headers JSON
- `{columns_output}` - Matched columns JSON
- `{stats_file}` - Matching statistics JSON

## Next Step
Run: `python e2e_stages/stage_7_final_output.py`
"""

    report_file = output_dir / "stage_6_report.md"
    with open(report_file, "w") as f:
        f.write(report)
    print(f"✓ Report saved to: {report_file}")

    print("\n" + "=" * 80)
    print("✅ STAGE 8 COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print(f"\n📖 Review the report: {report_file}")
    print("\n▶️  Next step: python e2e_stages/stage_7_final_output.py")


if __name__ == "__main__":
    main()
