"""
End-to-end extraction pipeline for Template Sense.

This module provides the high-level orchestration that wires together all
extraction, AI classification, translation, mapping, and output building
components into a unified pipeline.

The pipeline executes the following stages:
1. File loading and workbook setup
2. Grid extraction from the selected sheet
3. Heuristic detection of header and table candidates
4. AI provider initialization
5. AI payload construction
6. AI-based classification (headers, columns, line items)
7. Translation of non-English labels
8. Fuzzy matching to canonical field dictionary
9. Confidence filtering and recovery event generation
10. Canonical template aggregation
11. Normalized output building
12. Metadata attachment and return

This module is provider-agnostic and designed to be the internal wrapper
that coordinates all pipeline steps. The public API (Task 38) will build
on top of this module.
"""

import logging
import time
from pathlib import Path
from typing import Any

from template_sense.adapters.excel_adapter import ExcelWorkbook
from template_sense.ai.header_classification import classify_header_fields
from template_sense.ai.line_item_extraction import extract_line_items
from template_sense.ai.table_column_classification import classify_table_columns
from template_sense.ai.translation import TranslatedLabel, translate_labels
from template_sense.ai_payload_schema import build_ai_payload
from template_sense.ai_providers.config import AIConfig
from template_sense.ai_providers.factory import get_ai_provider
from template_sense.ai_providers.interface import AIProvider
from template_sense.constants import (
    DEFAULT_AUTO_MAPPING_THRESHOLD,
    DEFAULT_TARGET_LANGUAGE,
    MIN_AI_CONFIDENCE_WARNING,
    MIN_FUZZY_MATCH_WARNING,
    PIPELINE_VERSION,
    SUPPORTED_FILE_EXTENSIONS,
)
from template_sense.errors import (
    AIProviderError,
    ExtractionError,
    FileValidationError,
    InvalidFieldDictionaryError,
)
from template_sense.extraction.summary_builder import build_sheet_summary
from template_sense.file_loader import load_excel_file
from template_sense.mapping.fuzzy_field_matching import match_fields
from template_sense.output.canonical_aggregator import build_canonical_template
from template_sense.output.normalized_output_builder import build_normalized_output
from template_sense.recovery.error_recovery import (
    RecoveryEvent,
    RecoverySeverity,
    filter_by_ai_confidence,
    filter_by_fuzzy_match_score,
)

# Set up module logger
logger = logging.getLogger(__name__)


def _validate_inputs(file_path: str | Path, field_dictionary: dict[str, list[str]]) -> None:
    """
    Validate pipeline inputs early.

    Args:
        file_path: Path to the Excel file
        field_dictionary: Canonical field dictionary with multilingual variants

    Raises:
        FileValidationError: If file path is invalid or file doesn't exist
        InvalidFieldDictionaryError: If field dictionary is malformed
    """
    # Convert to Path if string
    if isinstance(file_path, str):
        file_path = Path(file_path)

    # Check file exists
    if not file_path.exists():
        raise FileValidationError(
            reason=f"File not found: {file_path}",
            file_path=str(file_path),
        )

    # Check file extension
    if file_path.suffix.lower() not in SUPPORTED_FILE_EXTENSIONS:
        raise FileValidationError(
            reason=f"Unsupported file format: {file_path.suffix}. "
            f"Supported formats: {SUPPORTED_FILE_EXTENSIONS}",
            file_path=str(file_path),
        )

    # Validate field dictionary structure
    if not isinstance(field_dictionary, dict):
        raise InvalidFieldDictionaryError(
            reason="Field dictionary must be a dict[str, list[str]]",
            field_dictionary=field_dictionary,
        )

    if not field_dictionary:
        raise InvalidFieldDictionaryError(
            reason="Field dictionary cannot be empty",
            field_dictionary=field_dictionary,
        )

    # Validate all keys are strings and all values are non-empty lists of strings
    for key, variants in field_dictionary.items():
        if not isinstance(key, str):
            raise InvalidFieldDictionaryError(
                reason=f"Field dictionary key must be string, got {type(key)}",
                field_dictionary=field_dictionary,
            )

        if not isinstance(variants, list):
            raise InvalidFieldDictionaryError(
                reason=f"Field dictionary value for key '{key}' must be list, got {type(variants)}",
                field_dictionary=field_dictionary,
            )

        if not variants:
            raise InvalidFieldDictionaryError(
                reason=f"Field dictionary value for key '{key}' cannot be empty list",
                field_dictionary=field_dictionary,
            )

        if not all(isinstance(v, str) for v in variants):
            raise InvalidFieldDictionaryError(
                reason=f"Field dictionary value for key '{key}' must be list of strings",
                field_dictionary=field_dictionary,
            )

    logger.debug(
        "Input validation passed: file=%s, field_dict_keys=%d",
        file_path,
        len(field_dictionary),
    )


def _select_sheet(workbook: ExcelWorkbook) -> str:
    """
    Select the first visible sheet from the workbook.

    Args:
        workbook: ExcelWorkbook instance

    Returns:
        Name of the first visible sheet

    Raises:
        ExtractionError: If no visible sheets are found
    """
    sheet_names = workbook.get_sheet_names()

    if not sheet_names:
        raise ExtractionError(
            extraction_type="sheet_selection",
            reason="No visible sheets found in workbook",
        )

    selected_sheet = sheet_names[0]
    logger.info("Selected sheet: '%s' (first visible sheet)", selected_sheet)
    return selected_sheet


def _build_metadata(
    sheet_name: str,
    ai_provider: AIProvider,
    timing_ms: int,
) -> dict[str, Any]:
    """
    Build pipeline metadata dictionary.

    Args:
        sheet_name: Name of the sheet that was processed
        ai_provider: AI provider instance used
        timing_ms: Total pipeline execution time in milliseconds

    Returns:
        Metadata dictionary with all required fields
    """
    metadata = {
        "sheet_name": sheet_name,
        "ai_provider": ai_provider.config.provider,
        "ai_model": ai_provider.config.model or "default",
        "pipeline_version": PIPELINE_VERSION,
        "timing_ms": timing_ms,
    }

    logger.debug("Built pipeline metadata: %s", metadata)
    return metadata


def run_extraction_pipeline(
    file_path: str | Path,
    field_dictionary: dict[str, list[str]],
    ai_config: AIConfig | None = None,
) -> dict[str, Any]:
    """
    Execute end-to-end template extraction pipeline.

    This function orchestrates the complete extraction workflow from file loading
    through AI classification, translation, fuzzy matching, and output generation.
    It is designed to be resilient to partial failures and will generate recovery
    events for non-fatal issues.

    Pipeline stages:
    1. Validation & Setup
    2. File Loading & Workbook Setup
    3. Grid Extraction
    4. Heuristic Detection (headers, tables)
    5. AI Provider Setup
    6. AI Payload Construction
    7. AI Classification (with error recovery)
    8. Translation
    9. Fuzzy Matching
    10. Confidence Filtering
    11. Canonical Aggregation
    12. Normalized Output Building
    13. Metadata & Return

    Args:
        file_path: Path to the Excel file (.xlsx or .xls)
        field_dictionary: Canonical field dictionary with multilingual variants.
                         Format: {"canonical_key": ["variant1", "variant2", ...]}
        ai_config: Optional AI provider configuration. If None, loads from environment.

    Returns:
        Dictionary with the following structure:
        {
            "normalized_output": {...},  # JSON-serializable normalized output
            "recovery_events": [...],     # List of recovery event dicts
            "metadata": {
                "sheet_name": str,
                "ai_provider": str,
                "ai_model": str,
                "pipeline_version": str,
                "timing_ms": int
            }
        }

    Raises:
        FileValidationError: If file is invalid, not found, or unsupported format
        InvalidFieldDictionaryError: If field dictionary is malformed
        ExtractionError: If workbook is empty or grid extraction fails fatally
        AIProviderError: If AI provider initialization fails (not for request failures)

    Example:
        >>> from pathlib import Path
        >>> from template_sense.pipeline.extraction_pipeline import run_extraction_pipeline
        >>>
        >>> field_dict = {
        ...     "invoice_number": ["Invoice Number", "Invoice No", "請求書番号"],
        ...     "due_date": ["Due Date", "Payment Due", "支払期日"],
        ... }
        >>>
        >>> result = run_extraction_pipeline(
        ...     file_path=Path("invoice.xlsx"),
        ...     field_dictionary=field_dict
        ... )
        >>>
        >>> print(result["normalized_output"]["headers"]["matched"])
        >>> print(result["recovery_events"])
        >>> print(result["metadata"]["timing_ms"])
    """
    # Start timing
    start_time = time.perf_counter()

    # Accumulated recovery events from all stages
    recovery_events: list[RecoveryEvent] = []

    logger.info("=== Starting extraction pipeline ===")
    logger.info("File: %s", file_path)
    logger.info("Field dictionary keys: %d", len(field_dictionary))

    # ============================================================
    # Stage 1: Validation & Setup
    # ============================================================
    logger.info("Stage 1: Validating inputs")
    _validate_inputs(file_path, field_dictionary)

    # Convert file_path to Path if string
    if isinstance(file_path, str):
        file_path = Path(file_path)

    # ============================================================
    # Stage 2: File Loading & Workbook Setup
    # ============================================================
    logger.info("Stage 2: Loading Excel file")
    try:
        raw_workbook = load_excel_file(file_path)
        workbook = ExcelWorkbook(raw_workbook)
        logger.info("Workbook loaded successfully")
    except FileValidationError:
        logger.error("File validation failed during loading")
        raise
    except Exception as e:
        logger.error("Unexpected error loading workbook: %s", str(e))
        raise FileValidationError(
            reason=f"Failed to load workbook: {str(e)}",
            file_path=str(file_path),
        ) from e

    # Select first visible sheet
    try:
        sheet_name = _select_sheet(workbook)
    except ExtractionError:
        logger.error("No visible sheets found")
        workbook.close()
        raise

    # ============================================================
    # Stage 3: Grid Extraction
    # ============================================================
    logger.info("Stage 3: Extracting grid from sheet '%s'", sheet_name)
    try:
        # Build sheet summary (includes grid extraction + heuristic detection)
        sheet_summary = build_sheet_summary(workbook, sheet_name)
        logger.info(
            "Sheet summary built: %d header blocks, %d table blocks",
            len(sheet_summary.get("header_blocks", [])),
            len(sheet_summary.get("table_blocks", [])),
        )

        # Extract grid for adjacent cell context (BAT-53)
        # Note: summary_builder already extracts the grid internally, but we need
        # it here for build_ai_payload. Could optimize later to avoid double extraction.
        from template_sense.extraction.sheet_extractor import extract_raw_grid

        grid = extract_raw_grid(workbook, sheet_name)
        logger.debug("Extracted grid for adjacent cell context (%d rows)", len(grid))
    except ExtractionError:
        logger.error("Grid extraction failed")
        workbook.close()
        raise

    # ============================================================
    # Stage 4: AI Provider Setup
    # ============================================================
    logger.info("Stage 4: Initializing AI provider")
    try:
        ai_provider = get_ai_provider(ai_config)
        logger.info(
            "AI provider initialized: provider=%s, model=%s",
            ai_provider.config.provider,
            ai_provider.config.model or "default",
        )
    except AIProviderError:
        logger.error("AI provider initialization failed")
        workbook.close()
        raise

    # ============================================================
    # Stage 5: AI Payload Construction
    # ============================================================
    logger.info("Stage 5: Building AI payload")
    try:
        ai_payload = build_ai_payload(
            sheet_summary=sheet_summary,
            field_dictionary=field_dictionary,
            grid=grid,  # Pass grid for adjacent cell context (BAT-53)
        )
        logger.info("AI payload built successfully")
    except Exception as e:
        logger.error("Failed to build AI payload: %s", str(e))
        workbook.close()
        raise ExtractionError(
            extraction_type="ai_payload",
            reason=f"Failed to build AI payload: {str(e)}",
        ) from e

    # ============================================================
    # Stage 6: AI Classification (with error recovery)
    # ============================================================
    classified_headers = []
    classified_columns = []
    extracted_line_items = []

    # Classify header fields
    logger.info("Stage 6a: Classifying header fields")
    try:
        classified_headers = classify_header_fields(ai_provider, ai_payload)
        logger.info("Classified %d header fields", len(classified_headers))
    except AIProviderError as e:
        logger.error("Header classification failed: %s", str(e))
        recovery_events.append(
            RecoveryEvent(
                severity=RecoverySeverity.ERROR,
                stage="ai_classification",
                message=f"Header classification failed: {str(e)}",
                metadata={"error_type": "AIProviderError"},
            )
        )

    # Classify table columns
    logger.info("Stage 6b: Classifying table columns")
    try:
        classified_columns = classify_table_columns(ai_provider, ai_payload)
        logger.info("Classified %d table columns", len(classified_columns))
    except AIProviderError as e:
        logger.error("Column classification failed: %s", str(e))
        recovery_events.append(
            RecoveryEvent(
                severity=RecoverySeverity.ERROR,
                stage="ai_classification",
                message=f"Column classification failed: {str(e)}",
                metadata={"error_type": "AIProviderError"},
            )
        )

    # Extract line items
    logger.info("Stage 6c: Extracting line items")
    try:
        extracted_line_items = extract_line_items(ai_provider, ai_payload)
        logger.info("Extracted %d line items", len(extracted_line_items))
    except AIProviderError as e:
        logger.error("Line item extraction failed: %s", str(e))
        recovery_events.append(
            RecoveryEvent(
                severity=RecoverySeverity.ERROR,
                stage="ai_classification",
                message=f"Line item extraction failed: {str(e)}",
                metadata={"error_type": "AIProviderError"},
            )
        )

    # ============================================================
    # Stage 7: Translation
    # ============================================================
    logger.info("Stage 7: Translating labels")

    # Collect all labels from headers and columns
    all_labels: list[str] = []

    for header in classified_headers:
        if header.raw_label:
            all_labels.append(header.raw_label)

    for column in classified_columns:
        if column.raw_label:
            all_labels.append(column.raw_label)

    # Deduplicate labels
    unique_labels = list(set(all_labels))
    logger.info("Collected %d unique labels for translation", len(unique_labels))

    # Translate if there are labels
    translation_map: dict[str, TranslatedLabel] = {}
    if unique_labels:
        try:
            translated_labels = translate_labels(
                ai_provider=ai_provider,
                labels=unique_labels,
                source_language=None,  # Auto-detect
                target_language=DEFAULT_TARGET_LANGUAGE,
            )

            # Build translation map
            for translated in translated_labels:
                translation_map[translated.original_text] = translated

            logger.info("Translated %d labels", len(translated_labels))

        except AIProviderError as e:
            logger.error("Translation failed: %s", str(e))
            recovery_events.append(
                RecoveryEvent(
                    severity=RecoverySeverity.ERROR,
                    stage="translation",
                    message=f"Translation failed: {str(e)}",
                    metadata={"error_type": "AIProviderError"},
                )
            )

            # Build fallback translation map (use original text as translated)
            for label in unique_labels:
                translation_map[label] = TranslatedLabel(
                    original_text=label,
                    translated_text=label,
                    target_language=DEFAULT_TARGET_LANGUAGE,
                )

            logger.info("Using fallback translations (original text)")

    # ============================================================
    # Stage 8: Fuzzy Matching
    # ============================================================
    logger.info("Stage 8: Performing fuzzy matching")

    # Match header fields
    header_translated_labels = [
        translation_map.get(
            header.raw_label,
            TranslatedLabel(
                original_text=header.raw_label or "",
                translated_text=header.raw_label or "",
                target_language=DEFAULT_TARGET_LANGUAGE,
            ),
        )
        for header in classified_headers
        if header.raw_label
    ]

    header_match_results = []
    if header_translated_labels:
        try:
            header_match_results = match_fields(
                translated_labels=header_translated_labels,
                field_dictionary=field_dictionary,
                threshold=DEFAULT_AUTO_MAPPING_THRESHOLD,
            )
            logger.info(
                "Matched %d header fields (threshold=%.1f)",
                len(header_match_results),
                DEFAULT_AUTO_MAPPING_THRESHOLD,
            )
        except Exception as e:
            logger.error("Header fuzzy matching failed: %s", str(e))
            recovery_events.append(
                RecoveryEvent(
                    severity=RecoverySeverity.ERROR,
                    stage="fuzzy_matching",
                    message=f"Header fuzzy matching failed: {str(e)}",
                    metadata={"error_type": type(e).__name__},
                )
            )

    # Match column fields
    column_translated_labels = [
        translation_map.get(
            column.raw_label,
            TranslatedLabel(
                original_text=column.raw_label or "",
                translated_text=column.raw_label or "",
                target_language=DEFAULT_TARGET_LANGUAGE,
            ),
        )
        for column in classified_columns
        if column.raw_label
    ]

    column_match_results = []
    if column_translated_labels:
        try:
            column_match_results = match_fields(
                translated_labels=column_translated_labels,
                field_dictionary=field_dictionary,
                threshold=DEFAULT_AUTO_MAPPING_THRESHOLD,
            )
            logger.info(
                "Matched %d column fields (threshold=%.1f)",
                len(column_match_results),
                DEFAULT_AUTO_MAPPING_THRESHOLD,
            )
        except Exception as e:
            logger.error("Column fuzzy matching failed: %s", str(e))
            recovery_events.append(
                RecoveryEvent(
                    severity=RecoverySeverity.ERROR,
                    stage="fuzzy_matching",
                    message=f"Column fuzzy matching failed: {str(e)}",
                    metadata={"error_type": type(e).__name__},
                )
            )

    # ============================================================
    # Stage 9: Confidence Filtering
    # ============================================================
    logger.info("Stage 9: Filtering by confidence thresholds")

    # Filter headers by AI confidence
    _, header_ai_events = filter_by_ai_confidence(
        fields=classified_headers,
        min_confidence=MIN_AI_CONFIDENCE_WARNING,
    )
    recovery_events.extend(header_ai_events)
    logger.info("Generated %d AI confidence warnings for headers", len(header_ai_events))

    # Filter columns by AI confidence
    _, column_ai_events = filter_by_ai_confidence(
        fields=classified_columns,
        min_confidence=MIN_AI_CONFIDENCE_WARNING,
    )
    recovery_events.extend(column_ai_events)
    logger.info("Generated %d AI confidence warnings for columns", len(column_ai_events))

    # Filter header matches by fuzzy score
    _, header_fuzzy_events = filter_by_fuzzy_match_score(
        fields=header_match_results,
        min_score=MIN_FUZZY_MATCH_WARNING,
    )
    recovery_events.extend(header_fuzzy_events)
    logger.info("Generated %d fuzzy match warnings for headers", len(header_fuzzy_events))

    # Filter column matches by fuzzy score
    _, column_fuzzy_events = filter_by_fuzzy_match_score(
        fields=column_match_results,
        min_score=MIN_FUZZY_MATCH_WARNING,
    )
    recovery_events.extend(column_fuzzy_events)
    logger.info("Generated %d fuzzy match warnings for columns", len(column_fuzzy_events))

    # ============================================================
    # Stage 10: Canonical Aggregation
    # ============================================================
    logger.info("Stage 10: Building canonical template")

    try:
        # Note: build_sheet_summary returns dicts, but build_canonical_template expects dataclasses
        # For now, we'll pass empty lists since we need proper conversion layer
        # This is a simplification - in production we'd need proper conversion

        canonical_template = build_canonical_template(
            sheet_name=sheet_name,
            header_candidate_blocks=[],  # Will be populated from sheet_summary in real impl
            table_candidate_blocks=[],  # Will be populated from sheet_summary in real impl
            classified_headers=classified_headers,
            classified_columns=classified_columns,
            extracted_line_items=extracted_line_items,
            header_match_results=header_match_results,
            column_match_results=column_match_results,
        )

        logger.info("Canonical template built successfully")

    except Exception as e:
        logger.error("Canonical aggregation failed: %s", str(e))
        workbook.close()
        raise ExtractionError(
            extraction_type="canonical_aggregation",
            reason=f"Failed to build canonical template: {str(e)}",
        ) from e

    # ============================================================
    # Stage 11: Normalized Output Building
    # ============================================================
    logger.info("Stage 11: Building normalized output")

    try:
        normalized_output = build_normalized_output(canonical_template)
        logger.info("Normalized output built successfully")
    except Exception as e:
        logger.error("Normalized output building failed: %s", str(e))
        workbook.close()
        raise ExtractionError(
            extraction_type="normalized_output",
            reason=f"Failed to build normalized output: {str(e)}",
        ) from e

    # ============================================================
    # Stage 12: Build Metadata & Return
    # ============================================================
    logger.info("Stage 12: Building metadata and preparing final output")

    # Calculate timing
    end_time = time.perf_counter()
    timing_ms = int((end_time - start_time) * 1000)

    # Build metadata
    metadata = _build_metadata(
        sheet_name=sheet_name,
        ai_provider=ai_provider,
        timing_ms=timing_ms,
    )

    # Convert recovery events to dicts directly (no aggregation needed for now)
    # aggregate_recovery_events returns a dict summary, not a list
    recovery_events_dicts = [event.to_dict() for event in recovery_events]

    # Close workbook
    workbook.close()

    # Build final result
    result = {
        "normalized_output": normalized_output,
        "recovery_events": recovery_events_dicts,
        "metadata": metadata,
    }

    logger.info("=== Pipeline completed successfully ===")
    logger.info("Total time: %d ms", timing_ms)
    logger.info("Recovery events: %d", len(recovery_events_dicts))

    return result


__all__ = ["run_extraction_pipeline"]
