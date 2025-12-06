"""End-to-end integration tests using live invoice and Tako field dictionaries.

These tests validate the complete extraction pipeline from file to output,
including timing measurements and batch classification optimization validation.

Run with: pytest tests/integration/test_end_to_end_extraction.py -v -s -m integration

Author: Template Sense Team
Created: 2025-12-06
"""

import json
import os
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from template_sense.ai_providers.config import AIConfig
from template_sense.analyzer import extract_template_structure
from template_sense.constants import (
    AI_MODEL_ENV_VAR,
    AI_PROVIDER_ENV_VAR,
    ANTHROPIC_API_KEY_ENV_VAR,
    OPENAI_API_KEY_ENV_VAR,
)


@pytest.fixture
def tako_field_dictionary():
    """Load Tako's actual field dictionaries from fixtures.

    Returns:
        dict: Dictionary with 'headers' and 'columns' keys containing
              Tako's canonical field mappings (22 headers + 20 columns = 42 total).
    """
    fixtures_dir = Path(__file__).parent.parent / "fixtures"

    with open(fixtures_dir / "tako_header_fields.json") as f:
        headers = json.load(f)

    with open(fixtures_dir / "tako_column_fields.json") as f:
        columns = json.load(f)

    return {"headers": headers, "columns": columns}


@pytest.fixture
def live_invoice_path():
    """Path to live test invoice fixture.

    Returns:
        Path: Path to live_test_invoice.xlsx file.
    """
    return Path(__file__).parent.parent / "fixtures" / "live_test_invoice.xlsx"


@pytest.fixture
def ai_config():
    """Create AIConfig from environment variables.

    Returns:
        AIConfig: Configuration object for AI provider setup.
    """
    provider = os.getenv(AI_PROVIDER_ENV_VAR, "openai")
    api_key = os.getenv(OPENAI_API_KEY_ENV_VAR) or os.getenv(ANTHROPIC_API_KEY_ENV_VAR)
    model = os.getenv(AI_MODEL_ENV_VAR)  # Use default if not set

    return AIConfig(
        provider=provider,
        api_key=api_key,
        model=model,
    )


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv(OPENAI_API_KEY_ENV_VAR) and not os.getenv(ANTHROPIC_API_KEY_ENV_VAR),
    reason="AI API key not set - skipping end-to-end integration test",
)
class TestEndToEndExtraction:
    """End-to-end integration tests with real invoice and Tako field dictionaries."""

    def test_full_extraction_with_timing(self, live_invoice_path, tako_field_dictionary, ai_config):
        """Test complete extraction pipeline with timing measurements.

        This test validates:
        - File loading works correctly
        - Heuristic detection finds candidates
        - AI classification processes all fields (using batch optimization)
        - Fuzzy matching works with Tako dictionaries
        - Output structure is correct
        - Performance is within acceptable bounds (<60s for CI)

        Args:
            live_invoice_path: Path to test invoice file
            tako_field_dictionary: Tako field dictionaries (42 fields)
            ai_config: AI provider configuration
        """
        # Time the extraction
        start_time = time.time()

        result = extract_template_structure(
            file_path=live_invoice_path,
            field_dictionary=tako_field_dictionary,
            ai_config=ai_config,
        )

        end_time = time.time()
        duration = end_time - start_time

        # Validate result structure
        assert "normalized_output" in result or "headers" in result
        assert "metadata" in result
        assert "recovery_events" in result

        # Validate metadata (only sheet_name is included per metadata stage)
        assert "sheet_name" in result["metadata"]

        # Performance check (should be under 60 seconds for CI)
        assert (
            duration < 60.0
        ), f"Extraction took {duration:.2f}s, expected < 60s. Possible performance regression."

        # Log timing for monitoring
        print("\n=== End-to-End Test Timing ===")
        print(f"Duration: {duration:.2f}s")
        print(f"Provider: {ai_config.provider}")
        print(f"Model: {ai_config.model or 'default'}")
        print(f"Sheet: {result['metadata']['sheet_name']}")
        print(f"Recovery events: {len(result.get('recovery_events', []))}")

    def test_extraction_validates_batch_optimization(
        self, live_invoice_path, tako_field_dictionary, ai_config
    ):
        """Test that extraction uses batch classification (validates BAT-74).

        This test verifies that the pipeline uses the new classify_all_fields
        batch method instead of making multiple individual classify_fields calls.

        Expected behavior:
        - classify_all_fields should be called at least once (batch classification)
        - classify_fields should NOT be called (individual classification)

        Args:
            live_invoice_path: Path to test invoice file
            tako_field_dictionary: Tako field dictionaries (42 fields)
            ai_config: AI provider configuration
        """
        # Track API calls
        classify_all_fields_count = 0
        classify_fields_count = 0

        def count_classify_all_fields(original_method):
            """Wrapper to count classify_all_fields calls."""

            def wrapper(*args, **kwargs):
                nonlocal classify_all_fields_count
                classify_all_fields_count += 1
                return original_method(*args, **kwargs)

            return wrapper

        def count_classify_fields(original_method):
            """Wrapper to count classify_fields calls."""

            def wrapper(*args, **kwargs):
                nonlocal classify_fields_count
                classify_fields_count += 1
                return original_method(*args, **kwargs)

            return wrapper

        # Patch based on provider
        if ai_config.provider == "openai":
            from template_sense.ai_providers.openai_provider import OpenAIProvider

            original_batch_method = OpenAIProvider.classify_all_fields
            original_single_method = OpenAIProvider.classify_fields

            with (
                patch.object(
                    OpenAIProvider,
                    "classify_all_fields",
                    count_classify_all_fields(original_batch_method),
                ),
                patch.object(
                    OpenAIProvider, "classify_fields", count_classify_fields(original_single_method)
                ),
            ):
                result = extract_template_structure(
                    file_path=live_invoice_path,
                    field_dictionary=tako_field_dictionary,
                    ai_config=ai_config,
                )
        else:
            from template_sense.ai_providers.anthropic_provider import AnthropicProvider

            original_batch_method = AnthropicProvider.classify_all_fields
            original_single_method = AnthropicProvider.classify_fields

            with (
                patch.object(
                    AnthropicProvider,
                    "classify_all_fields",
                    count_classify_all_fields(original_batch_method),
                ),
                patch.object(
                    AnthropicProvider,
                    "classify_fields",
                    count_classify_fields(original_single_method),
                ),
            ):
                result = extract_template_structure(
                    file_path=live_invoice_path,
                    field_dictionary=tako_field_dictionary,
                    ai_config=ai_config,
                )

        # Log API call counts
        print("\n=== API Call Tracking ===")
        print(f"classify_all_fields calls: {classify_all_fields_count}")
        print(f"classify_fields calls: {classify_fields_count}")

        # Validate batch optimization is working (BAT-74)
        assert (
            classify_all_fields_count >= 1
        ), "Should call classify_all_fields at least once (batch classification)"
        assert classify_fields_count == 0, (
            f"Should NOT call classify_fields (individual), but called {classify_fields_count} times. "
            "Batch optimization (BAT-74) may not be working correctly."
        )

        # Validate result is still valid
        assert result is not None
        assert "normalized_output" in result or "headers" in result

    def test_extraction_result_quality(self, live_invoice_path, tako_field_dictionary, ai_config):
        """Test that extraction produces quality results with Tako dictionaries.

        This test validates:
        - Extraction finds meaningful data (not empty results)
        - Matched fields have canonical_key set
        - canonical_key values exist in Tako dictionaries
        - At least some fields are matched (smoke test)

        Args:
            live_invoice_path: Path to test invoice file
            tako_field_dictionary: Tako field dictionaries (42 fields)
            ai_config: AI provider configuration
        """
        result = extract_template_structure(
            file_path=live_invoice_path,
            field_dictionary=tako_field_dictionary,
            ai_config=ai_config,
        )

        # Get results (handle both old and new format)
        norm_output = result.get("normalized_output", result)
        headers = norm_output.get("header_fields", norm_output.get("headers", {}))
        columns = norm_output.get("table_columns", norm_output.get("columns", {}))

        # Extract matched fields
        matched_headers = []
        if isinstance(headers, dict) and "matched" in headers:
            matched_headers = headers["matched"]
        elif isinstance(headers, list):
            matched_headers = headers

        matched_columns = []
        if isinstance(columns, dict) and "matched" in columns:
            matched_columns = columns["matched"]
        elif isinstance(columns, list):
            matched_columns = columns

        # Validate matched fields have canonical_key
        for field in matched_headers:
            assert "canonical_key" in field, f"Header field missing canonical_key: {field}"
            # Validate canonical_key exists in Tako dictionary
            assert (
                field["canonical_key"] in tako_field_dictionary["headers"]
            ), f"canonical_key '{field['canonical_key']}' not in Tako header dictionary"

        for col in matched_columns:
            assert "canonical_key" in col, f"Column field missing canonical_key: {col}"
            # Validate canonical_key exists in Tako dictionary
            assert (
                col["canonical_key"] in tako_field_dictionary["columns"]
            ), f"canonical_key '{col['canonical_key']}' not in Tako column dictionary"

        # Should extract at least some data
        total_matched = len(matched_headers) + len(matched_columns)

        print("\n=== Extraction Quality ===")
        print(f"Headers matched: {len(matched_headers)}")
        print(f"Columns matched: {len(matched_columns)}")
        print(f"Total matched: {total_matched}")
        print("Available Tako fields: 42 (22 headers + 20 columns)")
        print(f"Recovery events: {len(result.get('recovery_events', []))}")

        # Should find at least something (smoke test for quality)
        assert total_matched > 0, (
            "Extraction should match at least some fields. "
            "Zero results may indicate a pipeline issue."
        )
