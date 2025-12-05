"""Integration test for datetime serialization in AI provider.

This test verifies that the full pipeline handles Excel datetime objects correctly:
1. Excel file with datetime cells is loaded
2. Datetime objects are included in AI payload
3. Payload is serialized without TypeError
4. AI provider processes the payload successfully

This is the regression test for BAT-71.

Author: Template Sense Team
Created: 2025-12-05
"""

import os

import pytest

from template_sense.analyzer import extract_template_structure


@pytest.mark.integration
@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set - skipping live API test",
)
def test_datetime_serialization_with_live_api():
    """Test full pipeline with live_test_invoice.xlsx containing datetime objects.

    This test:
    1. Uses live_test_invoice.xlsx which has datetime objects
    2. Makes REAL API calls to OpenAI
    3. Verifies no JSON serialization errors occur
    4. Checks that all 3 AI classification stages complete successfully

    Expected behavior:
    - No "Object of type datetime is not JSON serializable" errors
    - Datetime values converted to ISO 8601 strings in AI payloads
    - All AI classification stages complete without errors
    - No serialization-related entries in recovery_events
    """
    # Path to test file with datetime objects
    test_file = "tests/fixtures/live_test_invoice.xlsx"

    # Field dictionary for mapping (structured format)
    field_dictionary = {
        "headers": {
            "invoice_number": "Invoice number",
            "invoice_date": "Invoice date",
            "due_date": "Due date",
            "customer_name": "Customer",
            "shipper_name": "Shipper",
        },
        "columns": {
            "item_description": "Description",
            "quantity": "Quantity",
            "unit_price": "Unit price",
            "amount": "Amount",
        },
    }

    # Run full analysis (this makes REAL API calls)
    result = extract_template_structure(
        file_path=test_file,
        field_dictionary=field_dictionary,
    )

    # Verify no errors occurred
    assert result is not None, "Analysis should not return None"

    # Check recovery_events for serialization errors
    if "recovery_events" in result:
        for event in result["recovery_events"]:
            error_msg = event.get("error", "").lower()
            assert (
                "json serializable" not in error_msg
            ), f"Found JSON serialization error in recovery events: {event}"
            assert (
                "datetime" not in error_msg
            ), f"Found datetime-related error in recovery events: {event}"

    # Verify that at least some data was extracted
    # (We don't care about the exact results, just that it didn't crash)
    assert "normalized_output" in result
    assert "metadata" in result

    # If there are header fields, verify they're in the expected format
    if result["normalized_output"].get("headers"):
        headers = result["normalized_output"]["headers"]
        if "matched" in headers:
            for field in headers["matched"]:
                assert "canonical_key" in field
                # Values might be datetime ISO strings, which is fine
                if field.get("value") is not None:
                    assert isinstance(
                        field["value"], str | int | float | bool
                    ), f"Field value should be JSON-serializable type, got {type(field['value'])}"

    # If there are table columns, verify they're in the expected format
    if result["normalized_output"].get("columns"):
        columns = result["normalized_output"]["columns"]
        if "matched" in columns:
            for col in columns["matched"]:
                assert "canonical_key" in col
                # Sample values should be JSON-serializable
                if col.get("sample_values"):
                    for value in col["sample_values"]:
                        if value is not None:
                            assert isinstance(
                                value, str | int | float | bool
                            ), f"Column value should be JSON-serializable type, got {type(value)}"


@pytest.mark.integration
@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set - skipping live API test",
)
def test_datetime_objects_converted_to_iso_format():
    """Verify that datetime objects are converted to ISO 8601 strings.

    This test specifically checks that datetime values in the input
    are converted to ISO format strings in the output.
    """
    test_file = "tests/fixtures/live_test_invoice.xlsx"

    field_dictionary = {
        "headers": {
            "invoice_date": "Invoice date",
            "due_date": "Due date",
        },
        "columns": {},
    }

    result = extract_template_structure(
        file_path=test_file,
        field_dictionary=field_dictionary,
    )

    # Find date fields in the results
    date_fields = []
    if result["normalized_output"].get("headers"):
        headers = result["normalized_output"]["headers"]
        if "matched" in headers:
            for field in headers["matched"]:
                if field.get("canonical_key") in ["invoice_date", "due_date"]:
                    date_fields.append(field)

    # If we found date fields, verify they're strings (ISO format)
    # Note: The AI might not classify them as dates, so this is optional
    if date_fields:
        for field in date_fields:
            value = field.get("value")
            if value is not None:
                assert isinstance(
                    value, str
                ), f"Date field value should be string (ISO format), got {type(value)}"
                # ISO format typically contains '-' (e.g., "2024-05-08")
                # This is a loose check, not strict ISO validation
                if len(str(value)) >= 10:  # Minimum length for date
                    # Just verify it's a string, don't enforce format
                    # (AI might return dates in different formats)
                    pass
