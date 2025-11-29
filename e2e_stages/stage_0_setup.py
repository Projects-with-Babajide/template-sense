"""
STAGE 0: Setup and Field Dictionary Loading

This script loads the Tako field dictionaries and prepares the test environment.

Output:
  - e2e_stages/output/stage_0_field_dictionary.json
  - e2e_stages/output/stage_0_report.md
"""

import json
import os
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv

load_dotenv()


def main():
    print("=" * 80)
    print("STAGE 0: SETUP AND FIELD DICTIONARY LOADING")
    print("=" * 80)

    # Create output directory
    output_dir = Path("e2e_stages/output")
    output_dir.mkdir(parents=True, exist_ok=True)

    # ========================================================================
    # Load Field Dictionaries
    # ========================================================================
    print("\n📚 Loading Tako field dictionaries...")

    header_dict_path = Path("tests/fixtures/tako_header_fields.json")
    column_dict_path = Path("tests/fixtures/tako_column_fields.json")

    # Load header fields
    with open(header_dict_path) as f:
        header_fields = json.load(f)
    print(f"✓ Loaded {len(header_fields)} header fields from {header_dict_path}")

    # Load column fields
    with open(column_dict_path) as f:
        column_fields = json.load(f)
    print(f"✓ Loaded {len(column_fields)} column fields from {column_dict_path}")

    # Merge into single dictionary with variants list
    # Note: The JSON files have format {"key": "Single Value"}
    # We need to convert to {"key": ["List of variants"]}
    field_dictionary = {}
    for key, value in header_fields.items():
        field_dictionary[key] = [value] if isinstance(value, str) else value
    for key, value in column_fields.items():
        field_dictionary[key] = [value] if isinstance(value, str) else value

    print(f"\n✓ Combined field dictionary: {len(field_dictionary)} total fields")

    # ========================================================================
    # Environment Check
    # ========================================================================
    print("\n🔧 Environment configuration:")
    ai_provider = os.getenv("TEMPLATE_SENSE_AI_PROVIDER", "openai")
    ai_model = os.getenv("TEMPLATE_SENSE_AI_MODEL", "default")
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))

    print(f"  • AI Provider: {ai_provider}")
    print(f"  • AI Model: {ai_model}")
    print(f"  • OpenAI API Key: {'✓ Set' if has_openai else '✗ Not set'}")
    print(f"  • Anthropic API Key: {'✓ Set' if has_anthropic else '✗ Not set'}")

    # ========================================================================
    # Test File
    # ========================================================================
    print("\n📄 Test template:")
    test_file = Path("tests/fixtures/invoice_templates/CO.xlsx")
    print(f"  • File: {test_file}")
    print(f"  • Exists: {'✓ Yes' if test_file.exists() else '✗ No'}")
    if test_file.exists():
        print(f"  • Size: {test_file.stat().st_size:,} bytes")

    # ========================================================================
    # Save Output
    # ========================================================================
    print("\n💾 Saving output...")

    # Save field dictionary
    output_file = output_dir / "stage_0_field_dictionary.json"
    with open(output_file, "w") as f:
        json.dump(field_dictionary, f, indent=2)
    print(f"✓ Field dictionary saved to: {output_file}")

    # Save configuration
    config = {
        "test_file": str(test_file),
        "ai_provider": ai_provider,
        "ai_model": ai_model,
        "field_dictionary_path": str(output_file),
        "total_fields": len(field_dictionary),
    }
    config_file = output_dir / "stage_0_config.json"
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
    print(f"✓ Configuration saved to: {config_file}")

    # Generate markdown report
    report = f"""# Stage 0: Setup and Field Dictionary Loading

## Summary
✅ **Stage completed successfully**

## Field Dictionary
- **Total fields**: {len(field_dictionary)}
- **Header fields**: {len(header_fields)}
- **Column fields**: {len(column_fields)}

### Sample Fields (First 10)
"""
    for i, (key, variants) in enumerate(list(field_dictionary.items())[:10], 1):
        report += f"\n{i}. **`{key}`**: {variants}"

    report += f"""

## Environment
- **AI Provider**: {ai_provider}
- **AI Model**: {ai_model}
- **OpenAI API Key**: {'✓ Set' if has_openai else '✗ Not set'}
- **Anthropic API Key**: {'✓ Set' if has_anthropic else '✗ Not set'}

## Test File
- **Path**: `{test_file}`
- **Exists**: {'✓ Yes' if test_file.exists() else '✗ No'}
- **Size**: {test_file.stat().st_size:,} bytes (if exists)

## Output Files
- `{output_file}` - Field dictionary JSON
- `{config_file}` - Configuration JSON

## Next Step
Run: `python e2e_stages/stage_1_loading.py`
"""

    report_file = output_dir / "stage_0_report.md"
    with open(report_file, "w") as f:
        f.write(report)
    print(f"✓ Report saved to: {report_file}")

    print("\n" + "=" * 80)
    print("✅ STAGE 0 COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print(f"\n📖 Review the report: {report_file}")
    print("\n▶️  Next step: python e2e_stages/stage_1_loading.py")


if __name__ == "__main__":
    main()
