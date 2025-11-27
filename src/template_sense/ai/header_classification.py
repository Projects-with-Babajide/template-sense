"""
Header field classification via AI.

This module takes header candidate blocks detected by heuristics and uses
AI providers to classify them semantically, identifying label/value pairs
and their meaning.
"""

import logging
from dataclasses import dataclass
from typing import Any

from template_sense.ai_providers.interface import AIProvider
from template_sense.errors import AIProviderError

# Set up module logger
logger = logging.getLogger(__name__)


@dataclass
class ClassifiedHeaderField:
    """
    Represents a header field classified by AI with semantic meaning.

    This dataclass stores the result of AI-based field classification,
    including the original label/value and coordinates. The canonical_key
    will be populated later by the mapping layer (fuzzy matching).

    Attributes:
        canonical_key: Semantic key after mapping (populated by mapping layer).
                      None until mapping is performed.
        raw_label: Original label text from template (may be non-English).
                  Can be None if no clear label was detected.
        raw_value: Associated value from the template.
        block_index: Index of the HeaderCandidateBlock this field came from.
        row_index: Row coordinate in the original grid (1-based Excel convention).
        col_index: Column coordinate in the original grid (1-based Excel convention).
        model_confidence: AI confidence score (0.0-1.0), if provided by the model.
                         None if the provider doesn't return confidence scores.
        metadata: Optional provider-specific or additional classification metadata.
    """

    canonical_key: str | None
    raw_label: str | None
    raw_value: Any
    block_index: int
    row_index: int
    col_index: int
    model_confidence: float | None = None
    metadata: dict[str, Any] | None = None


def classify_header_fields(
    ai_provider: AIProvider,
    payload: dict,
) -> list[ClassifiedHeaderField]:
    """
    Classify header fields using an AI provider.

    This function takes an AI payload (from build_ai_payload()) and uses the
    provided AI provider to classify header fields semantically. The AI model
    identifies label/value pairs and provides confidence scores.

    The function is provider-agnostic and works with any AIProvider implementation.
    It handles malformed responses gracefully and prefers partial success over
    complete failure.

    Args:
        ai_provider: An instance implementing the AIProvider interface.
        payload: AI payload dictionary from build_ai_payload(), containing:
                - sheet_name: str
                - header_candidates: list of header field dicts
                - table_candidates: list of table dicts
                - field_dictionary: canonical field mappings

    Returns:
        List of ClassifiedHeaderField instances. Returns empty list if no
        headers could be classified.

    Raises:
        AIProviderError: If the API request fails or the response structure
                        is completely invalid (missing required keys, not a dict).
                        Individual field parsing errors are logged but don't raise.

    Example:
        >>> from template_sense.ai_providers import get_ai_provider
        >>> from template_sense.ai_payload_schema import build_ai_payload
        >>>
        >>> provider = get_ai_provider()
        >>> payload = build_ai_payload(sheet_summary, field_dictionary)
        >>> classified = classify_header_fields(provider, payload)
        >>> for field in classified:
        ...     print(f"{field.raw_label}: {field.raw_value}")
    """
    provider_name = ai_provider.provider_name
    model_name = ai_provider.model

    # Calculate payload size for logging (approximate)
    payload_size = len(str(payload))
    header_count = len(payload.get("header_candidates", []))

    logger.debug(
        "Calling AI provider for header classification: provider=%s, model=%s, "
        "payload_size=%d bytes, header_candidates=%d",
        provider_name,
        model_name,
        payload_size,
        header_count,
    )

    # Call the AI provider
    try:
        response = ai_provider.classify_fields(payload)
    except Exception as e:
        # AIProvider implementations should wrap errors in AIProviderError,
        # but catch any unexpected errors here as well
        error_msg = f"AI provider request failed: {str(e)}"
        logger.error(
            "Header classification failed for provider=%s, model=%s: %s",
            provider_name,
            model_name,
            error_msg,
        )
        if isinstance(e, AIProviderError):
            raise
        raise AIProviderError(
            provider_name=provider_name,
            error_details=str(e),
            request_type="classify_fields",
        ) from e

    # Validate response structure
    if not isinstance(response, dict):
        error_msg = f"Expected dict response, got {type(response).__name__}"
        logger.error(
            "Invalid response structure from provider=%s: %s",
            provider_name,
            error_msg,
        )
        raise AIProviderError(
            provider_name=provider_name,
            error_details=error_msg,
            request_type="classify_fields",
        )

    if "headers" not in response:
        error_msg = "Response missing required 'headers' key"
        logger.error(
            "Invalid response structure from provider=%s: %s",
            provider_name,
            error_msg,
        )
        raise AIProviderError(
            provider_name=provider_name,
            error_details=error_msg,
            request_type="classify_fields",
        )

    headers_data = response["headers"]
    if not isinstance(headers_data, list):
        error_msg = f"'headers' must be a list, got {type(headers_data).__name__}"
        logger.error(
            "Invalid response structure from provider=%s: %s",
            provider_name,
            error_msg,
        )
        raise AIProviderError(
            provider_name=provider_name,
            error_details=error_msg,
            request_type="classify_fields",
        )

    # Parse individual header fields
    # Prefer partial success: skip invalid fields but continue processing
    classified_fields: list[ClassifiedHeaderField] = []
    parse_errors = 0

    for idx, header_dict in enumerate(headers_data):
        try:
            field = _parse_header_field(header_dict, idx)
            classified_fields.append(field)
        except (KeyError, TypeError, ValueError) as e:
            # Log the error but continue processing other fields
            parse_errors += 1
            logger.warning(
                "Failed to parse header field at index %d from provider=%s: %s. "
                "Skipping this field.",
                idx,
                provider_name,
                str(e),
            )
            continue

    # Log summary statistics
    total_fields = len(headers_data)
    success_count = len(classified_fields)
    logger.info(
        "Header classification completed: provider=%s, model=%s, "
        "total_fields=%d, successfully_parsed=%d, parse_errors=%d",
        provider_name,
        model_name,
        total_fields,
        success_count,
        parse_errors,
    )

    # Calculate average confidence if available
    confidences = [f.model_confidence for f in classified_fields if f.model_confidence is not None]
    if confidences:
        avg_confidence = sum(confidences) / len(confidences)
        logger.debug(
            "Average model confidence: %.2f (based on %d fields)",
            avg_confidence,
            len(confidences),
        )

    return classified_fields


def _parse_header_field(
    header_dict: dict[str, Any],
    field_index: int,
) -> ClassifiedHeaderField:
    """
    Parse a single header field dictionary into a ClassifiedHeaderField.

    This helper function validates and extracts required fields from the
    AI response. It handles missing optional fields gracefully.

    Args:
        header_dict: Dictionary containing header field data from AI response.
        field_index: Index of this field in the response list (for error messages).

    Returns:
        ClassifiedHeaderField instance.

    Raises:
        KeyError: If required fields are missing.
        TypeError: If field types are invalid.
        ValueError: If field values are invalid (e.g., negative coordinates).
    """
    if not isinstance(header_dict, dict):
        raise TypeError(
            f"Header field at index {field_index} must be a dict, "
            f"got {type(header_dict).__name__}"
        )

    # Extract required fields
    # Note: raw_label can be None, but the key must be present
    raw_label = header_dict.get("raw_label")
    if raw_label is not None and not isinstance(raw_label, str):
        raise TypeError(f"'raw_label' must be a string or None, got {type(raw_label).__name__}")

    raw_value = header_dict.get("raw_value")
    # raw_value can be any type (including None)

    # Coordinates must be present and be integers
    try:
        block_index = int(header_dict["block_index"])
        row_index = int(header_dict["row_index"])
        col_index = int(header_dict["col_index"])
    except KeyError as e:
        raise KeyError(f"Missing required coordinate field: {e}") from e
    except (TypeError, ValueError) as e:
        raise TypeError(f"Coordinate fields must be integers: {e}") from e

    # Validate coordinate values (must be non-negative)
    if block_index < 0 or row_index < 0 or col_index < 0:
        raise ValueError(
            f"Coordinates must be non-negative: block_index={block_index}, "
            f"row_index={row_index}, col_index={col_index}"
        )

    # Extract optional fields
    model_confidence = header_dict.get("model_confidence")
    if model_confidence is not None:
        try:
            model_confidence = float(model_confidence)
            # Validate confidence range
            if not 0.0 <= model_confidence <= 1.0:
                logger.warning(
                    "model_confidence out of range [0.0, 1.0]: %.2f. Setting to None.",
                    model_confidence,
                )
                model_confidence = None
        except (TypeError, ValueError):
            logger.warning(
                "Invalid model_confidence value: %s. Setting to None.",
                model_confidence,
            )
            model_confidence = None

    # Extract metadata (optional)
    metadata = header_dict.get("metadata")
    if metadata is not None and not isinstance(metadata, dict):
        logger.warning(
            "metadata must be a dict, got %s. Setting to None.",
            type(metadata).__name__,
        )
        metadata = None

    # canonical_key is not populated by AI (will be set by mapping layer)
    canonical_key = None

    return ClassifiedHeaderField(
        canonical_key=canonical_key,
        raw_label=raw_label,
        raw_value=raw_value,
        block_index=block_index,
        row_index=row_index,
        col_index=col_index,
        model_confidence=model_confidence,
        metadata=metadata,
    )
