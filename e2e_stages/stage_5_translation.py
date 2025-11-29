"""
STAGE 7: Translation

This script translates non-English labels to English.
⚠️  WARNING: This stage makes real AI API calls and consumes credits/tokens!

Input:
  - e2e_stages/output/stage_4_classified_headers.json
  - e2e_stages/output/stage_4_classified_columns.json

Output:
  - e2e_stages/output/stage_5_translations.json
  - e2e_stages/output/stage_5_report.md
"""

import json
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from template_sense.ai.translation import translate_labels
from template_sense.ai_providers.factory import get_ai_provider
from template_sense.constants import DEFAULT_TARGET_LANGUAGE


def main():
    print("=" * 80)
    print("STAGE 7: TRANSLATION")
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

    headers_file = output_dir / "stage_4_classified_headers.json"
    columns_file = output_dir / "stage_4_classified_columns.json"

    if not all([headers_file.exists(), columns_file.exists()]):
        print("❌ Error: Previous stage outputs not found!")
        print("Please run previous stages first.")
        sys.exit(1)

    with open(headers_file) as f:
        classified_headers = json.load(f)
    with open(columns_file) as f:
        classified_columns = json.load(f)

    print(f"✓ Loaded {len(classified_headers)} headers")
    print(f"✓ Loaded {len(classified_columns)} columns")

    # ========================================================================
    # Collect Unique Labels
    # ========================================================================
    print("\n📋 Collecting labels for translation...")

    all_labels = []
    for header in classified_headers:
        if header.get("raw_label"):
            all_labels.append(header["raw_label"])
    for column in classified_columns:
        if column.get("raw_label"):
            all_labels.append(column["raw_label"])

    unique_labels = list(set(all_labels))
    print(f"✓ Collected {len(all_labels)} total labels")
    print(f"✓ Found {len(unique_labels)} unique labels")

    # ========================================================================
    # Translate Labels
    # ========================================================================
    print(f"\n🌐 Translating to {DEFAULT_TARGET_LANGUAGE}...")
    print("⏳ Making AI API call...")

    ai_provider = get_ai_provider()
    start_time = time.perf_counter()

    translated_labels = translate_labels(
        ai_provider=ai_provider,
        labels=unique_labels,
        source_language=None,  # Auto-detect
        target_language=DEFAULT_TARGET_LANGUAGE,
    )

    translation_time = time.perf_counter() - start_time

    print(f"✓ Translated {len(translated_labels)} labels in {translation_time:.2f}s")

    # ========================================================================
    # Analyze Translations
    # ========================================================================
    print("\n📊 Translation analysis:")

    # Count by detected language
    lang_counts = {}
    for tl in translated_labels:
        lang = tl.detected_source_language or "unknown"
        lang_counts[lang] = lang_counts.get(lang, 0) + 1

    print("  Languages detected:")
    for lang, count in sorted(lang_counts.items(), key=lambda x: -x[1]):
        print(f"    • {lang}: {count} labels")

    # Show samples of actually translated labels (where original != translated)
    actually_translated = [tl for tl in translated_labels if tl.original_text != tl.translated_text]
    print(f"\n  Labels requiring translation: {len(actually_translated)}/{len(translated_labels)}")

    if actually_translated:
        print("\n  Sample translations (first 10):")
        for i, tl in enumerate(actually_translated[:10], 1):
            print(
                f"    {i}. '{tl.original_text}' → '{tl.translated_text}' ({tl.detected_source_language})"
            )

    # ========================================================================
    # Build Translation Map
    # ========================================================================
    print("\n🗺️  Building translation map...")

    translation_map = {}
    for tl in translated_labels:
        translation_map[tl.original_text] = {
            "translated_text": tl.translated_text,
            "detected_source_language": tl.detected_source_language,
            "target_language": tl.target_language,
            "model_confidence": tl.model_confidence,
            "metadata": tl.metadata,
        }

    print(f"✓ Translation map created with {len(translation_map)} entries")

    # ========================================================================
    # Save Output
    # ========================================================================
    print("\n💾 Saving output...")

    # Save translations
    translations_data = {
        "translation_map": translation_map,
        "statistics": {
            "total_labels": len(all_labels),
            "unique_labels": len(unique_labels),
            "actually_translated": len(actually_translated),
            "languages_detected": lang_counts,
            "translation_time_seconds": translation_time,
        },
    }

    output_file = output_dir / "stage_5_translations.json"
    with open(output_file, "w") as f:
        json.dump(translations_data, f, indent=2)
    print(f"✓ Translations saved to: {output_file}")

    # Generate markdown report
    report = f"""# Stage 7: Translation

## Summary
✅ **Stage completed successfully**

## Performance
- **Translation time**: {translation_time:.2f}s
- **Labels per second**: {len(unique_labels)/translation_time:.1f}

## Statistics
- **Total labels collected**: {len(all_labels)}
- **Unique labels**: {len(unique_labels)}
- **Labels requiring translation**: {len(actually_translated)} ({len(actually_translated)/len(translated_labels)*100:.1f}%)

## Languages Detected
"""

    for lang, count in sorted(lang_counts.items(), key=lambda x: -x[1]):
        percentage = count / len(translated_labels) * 100
        report += f"- **{lang}**: {count} labels ({percentage:.1f}%)\n"

    if actually_translated:
        report += """

## Sample Translations
"""
        for i, tl in enumerate(actually_translated[:15], 1):
            report += f"{i}. `{tl.original_text}` → `{tl.translated_text}` ({tl.detected_source_language})\n"

    report += f"""

## Output Files
- `{output_file}` - Translation map and statistics JSON

## Next Step
Run: `python e2e_stages/stage_6_fuzzy_matching.py`
"""

    report_file = output_dir / "stage_5_report.md"
    with open(report_file, "w") as f:
        f.write(report)
    print(f"✓ Report saved to: {report_file}")

    print("\n" + "=" * 80)
    print("✅ STAGE 7 COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print(f"\n📖 Review the report: {report_file}")
    print("\n▶️  Next step: python e2e_stages/stage_6_fuzzy_matching.py")


if __name__ == "__main__":
    main()
