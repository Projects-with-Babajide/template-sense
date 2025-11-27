"""
Integration tests for Anthropic provider with real API calls.

These tests are skipped if ANTHROPIC_API_KEY is not set.
Run with: pytest tests/integration -v -m integration
"""

import os

import pytest

from template_sense.ai_providers.anthropic_provider import AnthropicProvider
from template_sense.ai_providers.config import AIConfig


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set - skipping Anthropic integration test",
)
class TestAnthropicIntegration:
    """Integration tests with real Anthropic API calls."""

    @pytest.fixture
    def provider(self):
        """Create real Anthropic provider with API key from environment."""
        config = AIConfig(
            provider="anthropic",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            model="claude-3-haiku-20240307",  # Use cheaper model for tests
        )
        return AnthropicProvider(config)

    def test_classify_fields_real_api(self, provider):
        """Test classify_fields with real Anthropic API call."""
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
        # Anthropic should return valid JSON - if it doesn't, this test will fail

    def test_translate_text_real_api(self, provider):
        """Test translate_text with real Anthropic API call."""
        result = provider.translate_text("請求書番号", source_lang="ja", target_lang="en")

        # Verify result is a non-empty string
        assert isinstance(result, str), "Translation should be a string"
        assert len(result) > 0, "Translation should not be empty"
        # Should contain "invoice" or "number" in some form
        assert (
            "invoice" in result.lower() or "number" in result.lower()
        ), f"Translation '{result}' should relate to invoice/number"
