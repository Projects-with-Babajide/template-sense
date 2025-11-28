"""
Table column classification via AI.

This module takes table candidate blocks detected by heuristics and uses
AI providers to classify table columns semantically, identifying their
meaning based on header labels and sample data.
"""

import logging
from dataclasses import dataclass
from typing import Any

from template_sense.ai_providers.interface import AIProvider
from template_sense.errors import AIProviderError

# Set up module logger
logger = logging.getLogger(__name__)


@dataclass
class ClassifiedTableColumn:
    """
    Represents a single table column classified by AI.

    This dataclass stores the result of AI-based column classification,
    including the original column header, sample values, and position information.
    The canonical_key will be populated later by the mapping layer (fuzzy matching).

    Attributes:
        canonical_key: Semantic key after mapping (populated by mapping layer).
                      None until mapping is performed.
        raw_label: Original column header text from template (may be non-English).
                  Can be None if no clear header was detected.
        raw_position: Column position within the table (0-based).
        table_block_index: Index of the table candidate block this column came from.
        row_index: Row coordinate of the column header in the original grid
                  (1-based Excel convention).
        col_index: Column coordinate in the original grid (1-based Excel convention).
        sample_values: List of sample data values from this column for validation.
        model_confidence: AI confidence score (0.0-1.0), if provided by the model.
                         None if the provider doesn't return confidence scores.
        metadata: Optional provider-specific or additional classification metadata.
    """

    canonical_key: str | None
    raw_label: str | None
    raw_position: int
    table_block_index: int
    row_index: int
    col_index: int
    sample_values: list[Any]
    model_confidence: float | None = None
    metadata: dict[str, Any] | None = None


def classify_table_columns(
    ai_provider: AIProvider,
    payload: dict,
) -> list[ClassifiedTableColumn]:
    """
    Classify table columns using an AI provider.

    This function takes an AI payload (from build_ai_payload()) and uses the
    provided AI provider to classify table columns semantically. The AI model
    identifies column meanings based on header labels and sample data values.

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
        List of ClassifiedTableColumn instances. Returns empty list if no
        columns could be classified.

    Raises:
        AIProviderError: If the API request fails or the response structure
                        is completely invalid (missing required keys, not a dict).
                        Individual column parsing errors are logged but don't raise.

    Example:
        >>> from template_sense.ai_providers import get_ai_provider
        >>> from template_sense.ai_payload_schema import build_ai_payload
        >>>
        >>> provider = get_ai_provider()
        >>> payload = build_ai_payload(sheet_summary, field_dictionary)
        >>> classified = classify_table_columns(provider, payload)
        >>> for column in classified:
        ...     print(f"{column.raw_label}: {column.sample_values}")
    """
    provider_name = ai_provider.provider_name
    model_name = ai_provider.model

    # Calculate payload size for logging (approximate)
    payload_size = len(str(payload))
    table_count = len(payload.get("table_candidates", []))

    logger.debug(
        "Calling AI provider for table column classification: provider=%s, model=%s, "
        "payload_size=%d bytes, table_candidates=%d",
        provider_name,
        model_name,
        payload_size,
        table_count,
    )

    # Call the AI provider
    try:
        response = ai_provider.classify_fields(payload)
    except Exception as e:
        # AIProvider implementations should wrap errors in AIProviderError,
        # but catch any unexpected errors here as well
        error_msg = f"AI provider request failed: {str(e)}"
        logger.error(
            "Table column classification failed for provider=%s, model=%s: %s",
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

    if "columns" not in response:
        error_msg = "Response missing required 'columns' key"
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

    columns_data = response["columns"]
    if not isinstance(columns_data, list):
        error_msg = f"'columns' must be a list, got {type(columns_data).__name__}"
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

    # Parse individual table columns
    # Prefer partial success: skip invalid columns but continue processing
    classified_columns: list[ClassifiedTableColumn] = []
    parse_errors = 0

    for idx, column_dict in enumerate(columns_data):
        try:
            column = _parse_table_column(column_dict, idx)
            classified_columns.append(column)
        except (KeyError, TypeError, ValueError) as e:
            # Log the error but continue processing other columns
            parse_errors += 1
            logger.warning(
                "Failed to parse table column at index %d from provider=%s: %s. "
                "Skipping this column.",
                idx,
                provider_name,
                str(e),
            )
            continue

    # Log summary statistics
    total_columns = len(columns_data)
    success_count = len(classified_columns)
    logger.info(
        "Table column classification completed: provider=%s, model=%s, "
        "total_columns=%d, successfully_parsed=%d, parse_errors=%d",
        provider_name,
        model_name,
        total_columns,
        success_count,
        parse_errors,
    )

    # Calculate average confidence if available
    confidences = [c.model_confidence for c in classified_columns if c.model_confidence is not None]
    if confidences:
        avg_confidence = sum(confidences) / len(confidences)
        logger.debug(
            "Average model confidence: %.2f (based on %d columns)",
            avg_confidence,
            len(confidences),
        )

    return classified_columns


def _parse_table_column(
    column_dict: dict[str, Any],
    column_index: int,
) -> ClassifiedTableColumn:
    """
    Parse a single table column dictionary into a ClassifiedTableColumn.

    This helper function validates and extracts required fields from the
    AI response. It handles missing optional fields gracefully.

    Args:
        column_dict: Dictionary containing table column data from AI response.
        column_index: Index of this column in the response list (for error messages).

    Returns:
        ClassifiedTableColumn instance.

    Raises:
        KeyError: If required fields are missing.
        TypeError: If field types are invalid.
        ValueError: If field values are invalid (e.g., negative coordinates).
    """
    if not isinstance(column_dict, dict):
        raise TypeError(
            f"Table column at index {column_index} must be a dict, "
            f"got {type(column_dict).__name__}"
        )

    # Extract required fields
    # Note: raw_label can be None, but the key must be present
    raw_label = column_dict.get("raw_label")
    if raw_label is not None and not isinstance(raw_label, str):
        raise TypeError(f"'raw_label' must be a string or None, got {type(raw_label).__name__}")

    # Coordinates and position must be present and be integers
    try:
        raw_position = int(column_dict["raw_position"])
        table_block_index = int(column_dict["table_block_index"])
        row_index = int(column_dict["row_index"])
        col_index = int(column_dict["col_index"])
    except KeyError as e:
        raise KeyError(f"Missing required field: {e}") from e
    except (TypeError, ValueError) as e:
        raise TypeError(f"Position/coordinate fields must be integers: {e}") from e

    # Validate coordinate values (must be non-negative)
    if raw_position < 0 or table_block_index < 0 or row_index < 0 or col_index < 0:
        raise ValueError(
            f"Position/coordinates must be non-negative: raw_position={raw_position}, "
            f"table_block_index={table_block_index}, row_index={row_index}, col_index={col_index}"
        )

    # Extract sample_values (required field)
    sample_values = column_dict.get("sample_values")
    if sample_values is None:
        raise KeyError("Missing required field: 'sample_values'")
    if not isinstance(sample_values, list):
        raise TypeError(f"'sample_values' must be a list, got {type(sample_values).__name__}")
    # sample_values can be an empty list, which is valid

    # Extract optional fields
    model_confidence = column_dict.get("model_confidence")
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
    metadata = column_dict.get("metadata")
    if metadata is not None and not isinstance(metadata, dict):
        logger.warning(
            "metadata must be a dict, got %s. Setting to None.",
            type(metadata).__name__,
        )
        metadata = None

    # canonical_key is not populated by AI (will be set by mapping layer)
    canonical_key = None

    return ClassifiedTableColumn(
        canonical_key=canonical_key,
        raw_label=raw_label,
        raw_position=raw_position,
        table_block_index=table_block_index,
        row_index=row_index,
        col_index=col_index,
        sample_values=sample_values,
        model_confidence=model_confidence,
        metadata=metadata,
    )
