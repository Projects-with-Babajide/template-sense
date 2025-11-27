"""
AI provider configuration management for Template Sense.

This module handles loading and validating AI provider configuration from
environment variables or explicit config objects. It provides a type-safe
configuration container and loader function.

Classes:
    AIConfig: Strongly-typed configuration dataclass for AI providers

Functions:
    load_ai_config: Load AI configuration from environment variables

Usage Example:
    # Load from environment variables
    from template_sense.ai_providers.config import load_ai_config

    config = load_ai_config()
    print(f"Using provider: {config.provider}, model: {config.model}")

    # Or create explicit config
    from template_sense.ai_providers.config import AIConfig

    config = AIConfig(
        provider="openai",
        model="gpt-4",
        api_key="sk-...",
        timeout_seconds=30
    )
"""

import os
from dataclasses import dataclass

from template_sense.constants import (
    AI_MODEL_ENV_VAR,
    AI_PROVIDER_ENV_VAR,
    ANTHROPIC_API_KEY_ENV_VAR,
    DEFAULT_AI_TIMEOUT_SECONDS,
    OPENAI_API_KEY_ENV_VAR,
    SUPPORTED_AI_PROVIDERS,
)
from template_sense.errors import AIProviderError


@dataclass
class AIConfig:
    """
    Configuration container for AI provider settings.

    This dataclass stores all necessary configuration for connecting to
    and using an AI provider. It validates that the provider name is
    supported but does not validate API key formats.

    Attributes:
        provider: Name of the AI provider ("openai", "anthropic")
        api_key: API key for authentication with the provider
        model: Optional model name override (provider-specific)
        timeout_seconds: Request timeout in seconds (default from constants)

    Raises:
        AIProviderError: If provider name is not in SUPPORTED_AI_PROVIDERS

    Example:
        >>> config = AIConfig(
        ...     provider="openai",
        ...     api_key="sk-...",
        ...     model="gpt-4",
        ...     timeout_seconds=30
        ... )
    """

    provider: str
    api_key: str
    model: str | None = None
    timeout_seconds: int = DEFAULT_AI_TIMEOUT_SECONDS

    def __post_init__(self):
        """Validate provider name after initialization."""
        if self.provider not in SUPPORTED_AI_PROVIDERS:
            supported = ", ".join(SUPPORTED_AI_PROVIDERS)
            raise AIProviderError(
                provider_name=self.provider,
                error_details=f"Unsupported provider. Supported providers: {supported}",
            )


def load_ai_config() -> AIConfig:
    """
    Load AI provider configuration from environment variables.

    This function reads configuration from the following environment variables:
    - TEMPLATE_SENSE_AI_PROVIDER: Required provider name ("openai", "anthropic")
    - TEMPLATE_SENSE_AI_MODEL: Optional model name override
    - OPENAI_API_KEY: Required if provider is "openai"
    - ANTHROPIC_API_KEY: Required if provider is "anthropic"

    Returns:
        AIConfig: Validated configuration object

    Raises:
        AIProviderError: If required environment variables are missing or invalid

    Example:
        >>> import os
        >>> os.environ["TEMPLATE_SENSE_AI_PROVIDER"] = "openai"
        >>> os.environ["OPENAI_API_KEY"] = "sk-..."
        >>> config = load_ai_config()
        >>> print(config.provider)
        openai
    """
    # Read provider name
    provider = os.environ.get(AI_PROVIDER_ENV_VAR)
    if not provider:
        raise AIProviderError(
            provider_name="unknown",
            error_details=f"Missing required environment variable: {AI_PROVIDER_ENV_VAR}",
        )

    # Validate provider is supported (case-insensitive)
    provider = provider.lower()
    if provider not in SUPPORTED_AI_PROVIDERS:
        supported = ", ".join(SUPPORTED_AI_PROVIDERS)
        raise AIProviderError(
            provider_name=provider,
            error_details=f"Unsupported provider '{provider}'. Supported providers: {supported}",
        )

    # Read API key based on provider
    api_key_env_var = OPENAI_API_KEY_ENV_VAR if provider == "openai" else ANTHROPIC_API_KEY_ENV_VAR
    api_key = os.environ.get(api_key_env_var)
    if not api_key:
        raise AIProviderError(
            provider_name=provider,
            error_details=f"Missing required environment variable: {api_key_env_var}",
        )

    # Read optional model name
    model = os.environ.get(AI_MODEL_ENV_VAR)

    # Create and return config (validation happens in __post_init__)
    return AIConfig(
        provider=provider,
        api_key=api_key,
        model=model,
        timeout_seconds=DEFAULT_AI_TIMEOUT_SECONDS,
    )


__all__ = ["AIConfig", "load_ai_config"]
