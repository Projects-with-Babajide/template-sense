"""
Provider-agnostic AI interface for Template Sense.

This module defines the abstract base class that all AI provider implementations
must inherit from. It ensures a consistent interface for AI operations regardless
of the underlying provider (OpenAI, Anthropic, etc.).

Classes:
    AIProvider: Abstract base class for all AI provider implementations

Usage Example:
    from abc import ABC
    from template_sense.ai_providers.interface import AIProvider
    from template_sense.ai_providers.config import AIConfig

    class OpenAIProvider(AIProvider):
        def classify_fields(self, payload):
            # Implementation for OpenAI
            ...

        def translate_text(self, text, source_lang, target_lang):
            # Implementation for OpenAI
            ...
"""

from abc import ABC, abstractmethod
from typing import Any

from template_sense.ai_providers.config import AIConfig


class AIProvider(ABC):
    """
    Abstract base class for AI provider implementations.

    This class defines the contract that all AI providers must implement.
    It provides a provider-agnostic interface for semantic classification
    and translation operations.

    All concrete provider implementations must:
    1. Inherit from this class
    2. Implement all abstract methods
    3. Accept an AIConfig in their constructor
    4. Set provider_name and model properties

    Attributes:
        config: AI provider configuration (provider, model, api_key, timeout)

    Abstract Methods:
        classify_fields: Classify header fields or table columns semantically
        translate_text: Translate text from source language to target language

    Properties:
        provider_name: Name of the AI provider (e.g., "openai", "anthropic")
        model: Model being used for inference

    Example:
        >>> from template_sense.ai_providers.config import AIConfig
        >>> config = AIConfig(provider="openai", api_key="sk-...", model="gpt-4")
        >>> # provider = OpenAIProvider(config)  # Concrete implementation
        >>> # result = provider.classify_fields(payload)
    """

    def __init__(self, config: AIConfig):
        """
        Initialize the AI provider with configuration.

        Args:
            config: AI provider configuration object

        Note:
            Concrete implementations should call super().__init__(config)
            and then set up their provider-specific clients.
        """
        self.config = config

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Get the name of the AI provider.

        Returns:
            Provider name (e.g., "openai", "anthropic")

        Example:
            >>> provider.provider_name
            'openai'
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def model(self) -> str:
        """
        Get the model being used for inference.

        Returns:
            Model name (e.g., "gpt-4", "claude-3-sonnet-20240229")

        Example:
            >>> provider.model
            'gpt-4'
        """
        raise NotImplementedError

    @abstractmethod
    def classify_fields(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Classify header fields or table columns using AI.

        This method sends a structured payload to the AI provider and receives
        semantic classifications for invoice template fields (e.g., invoice_number,
        shipper_name, item_description).

        Args:
            payload: Structured data containing fields/columns to classify
                Expected structure defined by ai_payload_schema module

        Returns:
            dict containing classified fields with confidence scores and labels

        Raises:
            AIProviderError: If the API request fails or returns invalid data

        Example:
            >>> payload = {
            ...     "header_fields": [
            ...         {"label": "Invoice No", "value": "INV-001", "position": "A1"}
            ...     ]
            ... }
            >>> result = provider.classify_fields(payload)
            >>> print(result["classifications"][0]["canonical_key"])
            'invoice_number'
        """
        raise NotImplementedError

    @abstractmethod
    def translate_text(self, text: str, source_lang: str, target_lang: str = "en") -> str:
        """
        Translate text from source language to target language.

        This method uses the AI provider to translate field labels and values,
        particularly useful for Japanese invoice templates that need English
        canonical mappings.

        Args:
            text: Text to translate (preserves Unicode characters)
            source_lang: Source language code (e.g., "ja", "en", "es")
            target_lang: Target language code (default: "en")

        Returns:
            Translated text

        Raises:
            AIProviderError: If the translation request fails

        Example:
            >>> translated = provider.translate_text("請求書番号", source_lang="ja")
            >>> print(translated)
            'Invoice Number'
        """
        raise NotImplementedError


__all__ = ["AIProvider"]
