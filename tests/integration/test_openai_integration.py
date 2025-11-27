"""
Integration tests for OpenAI provider with real API calls.

These tests are skipped if OPENAI_API_KEY is not set.
Run with: pytest tests/integration -v -m integration
"""

import os

import pytest

from template_sense.ai_providers.config import AIConfig
from template_sense.ai_providers.openai_provider import OpenAIProvider


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set - skipping OpenAI integration test",
)
class TestOpenAIIntegration:
    """Integration tests with real OpenAI API calls."""

    @pytest.fixture
    def provider(self):
        """Create real OpenAI provider with API key from environment."""
        config = AIConfig(
            provider="openai",
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-3.5-turbo",  # Use cheaper model for tests
        )
        return OpenAIProvider(config)

    def test_classify_fields_real_api(self, provider):
        """Test classify_fields with real OpenAI API call."""
        # Minimal test payload
        payload = {
            "sheet_name": "Invoice",
            "header_candidates": [
                {"row": 1, "col": 1, "label": "Invoice Number", "value": "INV-001"}
            ],
            "table_candidates": [],
            "field_dictionary": {"invoice_number": ["Invoice Number", "Invoice No"]},
        }

        result = provider.classify_fields(payload)

        # Verify response structure (don't validate exact content)
        assert isinstance(result, dict), "Response should be a dictionary"
        assert len(result) > 0, "Response should not be empty"
        # OpenAI should return valid JSON - if it doesn't, this test will fail

    def test_translate_text_real_api(self, provider):
        """Test translate_text with real OpenAI API call."""
        result = provider.translate_text("請求書番号", source_lang="ja", target_lang="en")

        # Verify result is a non-empty string
        assert isinstance(result, str), "Translation should be a string"
        assert len(result) > 0, "Translation should not be empty"
        # Should contain "invoice" or "number" in some form
        assert (
            "invoice" in result.lower() or "number" in result.lower()
        ), f"Translation '{result}' should relate to invoice/number"
