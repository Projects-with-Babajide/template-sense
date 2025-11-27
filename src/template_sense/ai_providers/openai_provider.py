"""
OpenAI provider implementation for Template Sense.

This module provides a concrete implementation of the AIProvider interface
for OpenAI's API (GPT models). It handles:
- Field classification using structured output
- Text translation
- Error handling and timeout management
"""

import json
import logging
from typing import Any

from openai import APIError, APITimeoutError, AuthenticationError, OpenAI

from template_sense.ai_providers.config import AIConfig
from template_sense.ai_providers.interface import AIProvider
from template_sense.constants import DEFAULT_AI_TIMEOUT_SECONDS
from template_sense.errors import AIProviderError

logger = logging.getLogger(__name__)


class OpenAIProvider(AIProvider):
    """
    OpenAI API provider implementation.

    Uses OpenAI's chat completion API with JSON mode for structured outputs.
    Supports GPT-4 and GPT-3.5 models.
    """

    def __init__(self, config: AIConfig):
        """
        Initialize OpenAI provider.

        Args:
            config: AIConfig with provider="openai", api_key, optional model

        Raises:
            AIProviderError: If API key is missing or client initialization fails
        """
        super().__init__(config)

        if not config.api_key:
            raise AIProviderError(
                provider_name="openai",
                error_details="API key is required",
                request_type="initialization",
            )

        try:
            self.client = OpenAI(
                api_key=config.api_key,
                timeout=config.timeout_seconds or DEFAULT_AI_TIMEOUT_SECONDS,
            )
            logger.debug("OpenAI client initialized successfully")
        except Exception as e:
            raise AIProviderError(
                provider_name="openai",
                error_details=f"Failed to initialize client: {str(e)}",
                request_type="initialization",
            ) from e

    @property
    def provider_name(self) -> str:
        """Returns 'openai'."""
        return "openai"

    @property
    def model(self) -> str:
        """Returns the configured model or default 'gpt-4'."""
        return self.config.model or "gpt-4"

    def classify_fields(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Classify header fields and table columns using OpenAI.

        Sends the AI payload to OpenAI with instructions to classify fields
        semantically and return structured JSON.

        Args:
            payload: AI payload dict from build_ai_payload()

        Returns:
            Dict with classification results (structure TBD by downstream consumers)

        Raises:
            AIProviderError: On API errors, timeouts, or invalid responses
        """
        try:
            # Construct system message
            system_message = (
                "You are a field classification assistant for invoice templates. "
                "Analyze the provided template structure and classify each field "
                "semantically. Return your response as valid JSON only."
            )

            # Construct user message with payload
            user_message = (
                "Please classify the following invoice template fields:\n\n"
                f"{json.dumps(payload, indent=2)}\n\n"
                "Respond with a JSON object containing your classifications."
            )

            logger.debug("Sending classify_fields request to OpenAI (model=%s)", self.model)

            # Call OpenAI API with JSON mode
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message},
                ],
                response_format={"type": "json_object"},
                temperature=0.0,  # Deterministic for classification
            )

            # Extract and parse response
            content = response.choices[0].message.content

            if not content:
                raise AIProviderError(
                    provider_name="openai",
                    error_details="Empty response from API",
                    request_type="classify_fields",
                )

            try:
                result = json.loads(content)
                logger.debug("Successfully parsed JSON response from OpenAI")
                return result
            except json.JSONDecodeError as e:
                raise AIProviderError(
                    provider_name="openai",
                    error_details=f"Invalid JSON in response: {str(e)}",
                    request_type="classify_fields",
                ) from e

        except AuthenticationError as e:
            raise AIProviderError(
                provider_name="openai",
                error_details=f"Authentication failed: {str(e)}",
                request_type="classify_fields",
            ) from e
        except APITimeoutError as e:
            raise AIProviderError(
                provider_name="openai",
                error_details=f"Request timed out: {str(e)}",
                request_type="classify_fields",
            ) from e
        except APIError as e:
            raise AIProviderError(
                provider_name="openai",
                error_details=f"API error: {str(e)}",
                request_type="classify_fields",
            ) from e
        except AIProviderError:
            # Re-raise our own errors
            raise
        except Exception as e:
            # Catch any unexpected errors
            raise AIProviderError(
                provider_name="openai",
                error_details=f"Unexpected error: {str(e)}",
                request_type="classify_fields",
            ) from e

    def translate_text(self, text: str, source_lang: str, target_lang: str = "en") -> str:
        """
        Translate text using OpenAI.

        Args:
            text: Text to translate
            source_lang: Source language code (e.g., "ja", "zh")
            target_lang: Target language code (default: "en")

        Returns:
            Translated text

        Raises:
            AIProviderError: On API errors, timeouts, or invalid responses
        """
        try:
            system_message = (
                f"You are a professional translator. Translate the given text "
                f"from {source_lang} to {target_lang}. "
                f"Return only the translated text, nothing else."
            )

            user_message = text

            logger.debug(
                "Sending translate_text request to OpenAI (model=%s, %s→%s)",
                self.model,
                source_lang,
                target_lang,
            )

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.3,  # Slight creativity for natural translations
            )

            translated = response.choices[0].message.content

            if not translated:
                raise AIProviderError(
                    provider_name="openai",
                    error_details="Empty translation response from API",
                    request_type="translate_text",
                )

            logger.debug("Successfully translated text via OpenAI")
            return translated.strip()

        except AuthenticationError as e:
            raise AIProviderError(
                provider_name="openai",
                error_details=f"Authentication failed: {str(e)}",
                request_type="translate_text",
            ) from e
        except APITimeoutError as e:
            raise AIProviderError(
                provider_name="openai",
                error_details=f"Request timed out: {str(e)}",
                request_type="translate_text",
            ) from e
        except APIError as e:
            raise AIProviderError(
                provider_name="openai",
                error_details=f"API error: {str(e)}",
                request_type="translate_text",
            ) from e
        except AIProviderError:
            # Re-raise our own errors
            raise
        except Exception as e:
            # Catch any unexpected errors
            raise AIProviderError(
                provider_name="openai",
                error_details=f"Unexpected error: {str(e)}",
                request_type="translate_text",
            ) from e


__all__ = ["OpenAIProvider"]
