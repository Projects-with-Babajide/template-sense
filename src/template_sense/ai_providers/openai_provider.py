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

    def classify_fields(self, payload: dict[str, Any], context: str = "headers") -> dict[str, Any]:
        """
        Classify header fields and table columns using OpenAI.

        Sends the AI payload to OpenAI with instructions to classify fields
        semantically and return structured JSON.

        Args:
            payload: AI payload dict from build_ai_payload()
            context: Classification context - "headers", "columns", or "line_items"

        Returns:
            Dict with classification results (structure depends on context)

        Raises:
            AIProviderError: On API errors, timeouts, or invalid responses
            ValueError: If context is not a supported value
        """
        # Validate context
        if context not in ["headers", "columns", "line_items"]:
            raise ValueError(
                f"Invalid context: {context}. Must be 'headers', 'columns', or 'line_items'"
            )

        try:
            # Build context-aware prompts
            system_message = self._build_system_prompt(context)
            user_message = self._build_user_prompt(payload, context)

            logger.debug(
                "Sending classify_fields request to OpenAI (model=%s, context=%s)",
                self.model,
                context,
            )

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

                # Validate expected response key
                expected_key = self._get_expected_response_key(context)
                if expected_key not in result:
                    raise AIProviderError(
                        provider_name="openai",
                        error_details=f"Response missing '{expected_key}' key for context '{context}'",
                        request_type="classify_fields",
                    )

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
        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            # Catch any unexpected errors
            raise AIProviderError(
                provider_name="openai",
                error_details=f"Unexpected error: {str(e)}",
                request_type="classify_fields",
            ) from e

    def _build_system_prompt(self, context: str) -> str:
        """
        Build context-aware system prompt.

        Args:
            context: Classification context

        Returns:
            System prompt string tailored to the context
        """
        if context == "headers":
            return (
                "You are a field classification assistant for invoice templates. "
                "Analyze the provided header fields and classify each field "
                "semantically based on common invoice terminology. Return your "
                "response as valid JSON with a 'headers' key containing an array "
                "of classified fields."
            )
        if context == "columns":
            return (
                "You are a table column classification assistant for invoice templates. "
                "Analyze the provided table columns and classify each column "
                "semantically based on common invoice table structures (e.g., "
                "item name, quantity, unit price, amount). Return your response "
                "as valid JSON with a 'columns' key containing an array of "
                "classified columns."
            )
        if context == "line_items":
            return (
                "You are a line item extraction assistant for invoice templates. "
                "Analyze the provided table rows and extract individual line items, "
                "identifying subtotals and non-item rows. Return your response "
                "as valid JSON with a 'line_items' key containing an array of "
                "extracted items."
            )
        return ""

    def _build_user_prompt(self, payload: dict[str, Any], context: str) -> str:
        """
        Build context-aware user prompt.

        Args:
            payload: AI payload data
            context: Classification context

        Returns:
            User prompt string tailored to the context
        """
        context_descriptions = {
            "headers": "invoice template header fields",
            "columns": "invoice table columns",
            "line_items": "invoice table line items",
        }

        description = context_descriptions.get(context, "invoice template fields")

        return (
            f"Please classify the following {description}:\n\n"
            f"{json.dumps(payload, indent=2)}\n\n"
            "Respond with a JSON object containing your classifications."
        )

    def _get_expected_response_key(self, context: str) -> str:
        """
        Get expected response key for context.

        Args:
            context: Classification context

        Returns:
            Expected top-level key in response JSON
        """
        mapping = {
            "headers": "headers",
            "columns": "columns",
            "line_items": "line_items",
        }
        return mapping[context]

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
