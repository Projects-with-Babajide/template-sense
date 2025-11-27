"""Tests for AI provider factory function."""

import pytest

from template_sense.ai_providers.config import AIConfig
from template_sense.ai_providers.factory import get_ai_provider
from template_sense.constants import (
    AI_PROVIDER_ENV_VAR,
    ANTHROPIC_API_KEY_ENV_VAR,
    OPENAI_API_KEY_ENV_VAR,
)
from template_sense.errors import AIProviderError


class TestGetAIProvider:
    """Tests for the get_ai_provider factory function."""

    def test_factory_with_explicit_openai_config(self):
        """Test factory with explicit OpenAI config."""
        config = AIConfig(provider="openai", api_key="sk-test-key", model="gpt-4")

        # In Task 27, no implementations exist yet, so this should raise error
        with pytest.raises(AIProviderError) as exc_info:
            get_ai_provider(config)

        error = exc_info.value
        assert error.provider_name == "openai"
        assert "implementation not found" in error.error_details.lower()
        assert "Task 28" in error.error_details  # References future task

    def test_factory_with_explicit_anthropic_config(self):
        """Test factory with explicit Anthropic config."""
        config = AIConfig(
            provider="anthropic",
            api_key="sk-ant-test-key",
            model="claude-3-sonnet-20240229",
        )

        # In Task 27, no implementations exist yet, so this should raise error
        with pytest.raises(AIProviderError) as exc_info:
            get_ai_provider(config)

        error = exc_info.value
        assert error.provider_name == "anthropic"
        assert "implementation not found" in error.error_details.lower()

    def test_factory_loads_from_env_when_config_is_none(self, monkeypatch):
        """Test that factory loads config from env when config is None."""
        monkeypatch.setenv(AI_PROVIDER_ENV_VAR, "openai")
        monkeypatch.setenv(OPENAI_API_KEY_ENV_VAR, "sk-env-key")

        # Should load from env and then fail because no implementation exists
        with pytest.raises(AIProviderError) as exc_info:
            get_ai_provider(config=None)

        error = exc_info.value
        assert error.provider_name == "openai"
        assert "implementation not found" in error.error_details.lower()

    def test_factory_propagates_config_loading_errors(self, monkeypatch):
        """Test that factory propagates errors from load_ai_config."""
        # Don't set any environment variables
        monkeypatch.delenv(AI_PROVIDER_ENV_VAR, raising=False)
        monkeypatch.delenv(OPENAI_API_KEY_ENV_VAR, raising=False)
        monkeypatch.delenv(ANTHROPIC_API_KEY_ENV_VAR, raising=False)

        with pytest.raises(AIProviderError) as exc_info:
            get_ai_provider(config=None)

        error = exc_info.value
        assert "Missing required environment variable" in error.error_details

    def test_factory_with_unsupported_provider_config(self):
        """Test factory with unsupported provider in config."""
        # This should fail at AIConfig validation level
        with pytest.raises(AIProviderError) as exc_info:
            config = AIConfig(provider="gemini", api_key="sk-test")
            get_ai_provider(config)

        error = exc_info.value
        assert error.provider_name == "gemini"
        assert "Unsupported provider" in error.error_details

    def test_factory_error_message_is_clear(self):
        """Test that factory error message clearly indicates implementation missing."""
        config = AIConfig(provider="openai", api_key="sk-test")

        with pytest.raises(AIProviderError) as exc_info:
            get_ai_provider(config)

        error = exc_info.value
        # Check error message is informative
        assert "openai" in error.error_details.lower()
        assert "not found" in error.error_details.lower()
        # Should reference Task 28 where implementations will be added
        assert "Task 28" in error.error_details or "task 28" in error.error_details.lower()

    def test_factory_preserves_config_settings(self, monkeypatch):
        """Test that factory preserves all config settings when loading from env."""
        monkeypatch.setenv(AI_PROVIDER_ENV_VAR, "anthropic")
        monkeypatch.setenv(ANTHROPIC_API_KEY_ENV_VAR, "sk-ant-key-xyz")

        # Even though factory will fail, we can check the error contains correct provider
        with pytest.raises(AIProviderError) as exc_info:
            get_ai_provider()

        error = exc_info.value
        assert error.provider_name == "anthropic"

    def test_factory_with_none_model_in_config(self):
        """Test factory with config that has model=None."""
        config = AIConfig(provider="openai", api_key="sk-test", model=None)

        with pytest.raises(AIProviderError) as exc_info:
            get_ai_provider(config)

        # Should fail with implementation not found, not config error
        error = exc_info.value
        assert error.provider_name == "openai"
        assert "implementation not found" in error.error_details.lower()

    def test_factory_default_parameter_is_none(self):
        """Test that calling factory without args defaults to config=None."""
        # Setup valid env vars
        import os

        os.environ[AI_PROVIDER_ENV_VAR] = "openai"
        os.environ[OPENAI_API_KEY_ENV_VAR] = "sk-test"

        try:
            # Both should behave the same
            with pytest.raises(AIProviderError):
                get_ai_provider()  # No args

            with pytest.raises(AIProviderError):
                get_ai_provider(None)  # Explicit None

        finally:
            # Cleanup
            os.environ.pop(AI_PROVIDER_ENV_VAR, None)
            os.environ.pop(OPENAI_API_KEY_ENV_VAR, None)
