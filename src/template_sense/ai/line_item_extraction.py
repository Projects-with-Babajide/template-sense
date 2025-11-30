"""
Row-level line item extraction via AI.

This module takes table candidate blocks and their column classifications,
and uses AI providers to extract structured line items (rows) from the table data.
"""

import logging
from dataclasses import dataclass
from typing import Any

from template_sense.ai_providers.interface import AIProvider
from template_sense.errors import AIProviderError

# Set up module logger
logger = logging.getLogger(__name__)


@dataclass
class ExtractedLineItem:
    """
    Represents a single line item (row) extracted from a table via AI.

    This dataclass stores the result of AI-based line item extraction,
    including the row data mapped to column classifications. Line items
    may represent actual invoice items or special rows (subtotals, headers).

    Attributes:
        table_index: Index of the table this row belongs to.
        row_index: Row coordinate in original grid (1-based Excel convention).
        line_number: Sequential line item number if present in the data.
                    None if no explicit line number column exists.
        columns: Dict mapping column names to extracted values.
                Keys are canonical_key from column classification (e.g., "product_name").
                Values can be any type (str, int, float, None).
        is_subtotal: Flag indicating if this row is a subtotal/summary row.
                    True for non-item rows (section totals, headers within table).
        model_confidence: AI confidence score (0.0-1.0), if provided.
        metadata: Optional provider-specific data.
    """

    table_index: int
    row_index: int
    line_number: int | None
    columns: dict[str, Any]
    is_subtotal: bool = False
    model_confidence: float | None = None
    metadata: dict[str, Any] | None = None


def extract_line_items(
    ai_provider: AIProvider,
    payload: dict,
) -> list[ExtractedLineItem]:
    """
    Extract line items from table data using an AI provider.

    This function takes an AI payload (containing table candidates and column
    classifications) and uses the provided AI provider to extract structured
    line items row by row. The AI model identifies actual line items vs. subtotal
    rows and maps cell values to the appropriate columns.

    The function is provider-agnostic and works with any AIProvider implementation.
    It handles malformed responses gracefully and prefers partial success over
    complete failure.

    Args:
        ai_provider: An instance implementing the AIProvider interface.
        payload: AI payload dictionary containing:
                - table_candidates: list of table dicts with column classifications
                - field_dictionary: canonical field mappings
                - (optional) other context fields

    Returns:
        List of ExtractedLineItem instances. Returns empty list if no
        line items could be extracted.

    Raises:
        AIProviderError: If the API request fails or the response structure
                        is completely invalid (missing required keys, not a dict).
                        Individual item parsing errors are logged but don't raise.

    Example:
        >>> from template_sense.ai_providers import get_ai_provider
        >>> from template_sense.ai_payload_schema import build_ai_payload
        >>>
        >>> provider = get_ai_provider()
        >>> payload = build_ai_payload(sheet_summary, field_dictionary)
        >>> line_items = extract_line_items(provider, payload)
        >>> for item in line_items:
        ...     print(f"Row {item.row_index}: {item.columns}")
    """
    provider_name = ai_provider.provider_name
    model_name = ai_provider.model

    # Calculate payload size for logging (approximate)
    payload_size = len(str(payload))
    table_count = len(payload.get("table_candidates", []))

    logger.debug(
        "Calling AI provider for line item extraction: provider=%s, model=%s, "
        "payload_size=%d bytes, table_count=%d",
        provider_name,
        model_name,
        payload_size,
        table_count,
    )

    # Call the AI provider
    try:
        response = ai_provider.classify_fields(payload, context="line_items")
    except Exception as e:
        # AIProvider implementations should wrap errors in AIProviderError,
        # but catch any unexpected errors here as well
        error_msg = f"AI provider request failed: {str(e)}"
        logger.error(
            "Line item extraction failed for provider=%s, model=%s: %s",
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

    if "line_items" not in response:
        error_msg = "Response missing required 'line_items' key"
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

    line_items_data = response["line_items"]
    if not isinstance(line_items_data, list):
        error_msg = f"'line_items' must be a list, got {type(line_items_data).__name__}"
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

    # Parse individual line items
    # Prefer partial success: skip invalid items but continue processing
    extracted_items: list[ExtractedLineItem] = []
    parse_errors = 0

    for idx, item_dict in enumerate(line_items_data):
        try:
            item = _parse_line_item(item_dict, idx)
            extracted_items.append(item)
        except (KeyError, TypeError, ValueError) as e:
            # Log the error but continue processing other items
            parse_errors += 1
            logger.warning(
                "Failed to parse line item at index %d from provider=%s: %s. "
                "Skipping this item.",
                idx,
                provider_name,
                str(e),
            )
            continue

    # Log summary statistics
    total_items = len(line_items_data)
    success_count = len(extracted_items)
    logger.info(
        "Line item extraction completed: provider=%s, model=%s, "
        "total_items=%d, successfully_parsed=%d, parse_errors=%d",
        provider_name,
        model_name,
        total_items,
        success_count,
        parse_errors,
    )

    # Calculate average confidence if available
    confidences = [
        item.model_confidence for item in extracted_items if item.model_confidence is not None
    ]
    if confidences:
        avg_confidence = sum(confidences) / len(confidences)
        logger.debug(
            "Average model confidence: %.2f (based on %d items)",
            avg_confidence,
            len(confidences),
        )

    return extracted_items


def _parse_line_item(
    item_dict: dict[str, Any],
    item_index: int,
) -> ExtractedLineItem:
    """
    Parse a single line item dictionary into an ExtractedLineItem.

    This helper function validates and extracts required fields from the
    AI response. It handles missing optional fields gracefully.

    Args:
        item_dict: Dictionary containing line item data from AI response.
        item_index: Index of this item in the response list (for error messages).

    Returns:
        ExtractedLineItem instance.

    Raises:
        KeyError: If required fields are missing.
        TypeError: If field types are invalid.
        ValueError: If field values are invalid (e.g., negative indices).
    """
    if not isinstance(item_dict, dict):
        raise TypeError(
            f"Line item at index {item_index} must be a dict, got {type(item_dict).__name__}"
        )

    # Extract required fields
    try:
        table_index = int(item_dict["table_index"])
        row_index = int(item_dict["row_index"])
    except KeyError as e:
        raise KeyError(f"Missing required field: {e}") from e
    except (TypeError, ValueError) as e:
        raise TypeError(f"Index fields must be integers: {e}") from e

    # Validate index values (must be non-negative)
    if table_index < 0 or row_index < 0:
        raise ValueError(
            f"Indices must be non-negative: table_index={table_index}, row_index={row_index}"
        )

    # Extract line_number (optional, can be None)
    line_number = item_dict.get("line_number")
    if line_number is not None:
        try:
            line_number = int(line_number)
        except (TypeError, ValueError) as e:
            raise TypeError(f"'line_number' must be an integer or None: {e}") from e

    # Extract columns (required, must be dict, can be empty)
    columns = item_dict.get("columns")
    if columns is None:
        raise KeyError("Missing required field: 'columns'")
    if not isinstance(columns, dict):
        raise TypeError(f"'columns' must be a dict, got {type(columns).__name__}")

    # Extract is_subtotal (optional, defaults to False)
    is_subtotal = item_dict.get("is_subtotal", False)
    if not isinstance(is_subtotal, bool):
        raise TypeError(f"'is_subtotal' must be a bool, got {type(is_subtotal).__name__}")

    # Extract optional model_confidence
    model_confidence = item_dict.get("model_confidence")
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
    metadata = item_dict.get("metadata")
    if metadata is not None and not isinstance(metadata, dict):
        logger.warning(
            "metadata must be a dict, got %s. Setting to None.",
            type(metadata).__name__,
        )
        metadata = None

    return ExtractedLineItem(
        table_index=table_index,
        row_index=row_index,
        line_number=line_number,
        columns=columns,
        is_subtotal=is_subtotal,
        model_confidence=model_confidence,
        metadata=metadata,
    )
