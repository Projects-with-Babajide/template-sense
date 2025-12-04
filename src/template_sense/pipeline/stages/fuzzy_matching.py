"""
FuzzyMatchingStage: Performs fuzzy matching to canonical field dictionary.

This stage matches translated labels from headers and columns to the canonical
field dictionary using fuzzy matching algorithms.
"""

import logging

from template_sense.ai.translation import TranslatedLabel
from template_sense.constants import DEFAULT_AUTO_MAPPING_THRESHOLD, DEFAULT_TARGET_LANGUAGE
from template_sense.mapping.fuzzy_field_matching import match_fields
from template_sense.pipeline.stages.base import PipelineContext, PipelineStage
from template_sense.recovery.error_recovery import RecoveryEvent, RecoverySeverity

logger = logging.getLogger(__name__)


class FuzzyMatchingStage(PipelineStage):
    """
    Stage 8: Fuzzy matching.

    Performs fuzzy matching of translated labels against the canonical field
    dictionary. Sets context.header_match_results and context.column_match_results.

    Uses error recovery if matching fails.
    """

    def execute(self, context: PipelineContext) -> PipelineContext:
        """Execute fuzzy matching stage."""
        logger.info("Stage 8: Performing fuzzy matching")

        if context.ai_provider is None:
            logger.warning("AI provider not set, skipping fuzzy matching")
            return context

        # Match header fields
        header_translated_labels = [
            context.translation_map.get(
                header.raw_label,
                TranslatedLabel(
                    original_text=header.raw_label or "",
                    translated_text=header.raw_label or "",
                    target_language=DEFAULT_TARGET_LANGUAGE,
                ),
            )
            for header in context.classified_headers
            if header.raw_label
        ]

        if header_translated_labels:
            try:
                context.header_match_results = match_fields(
                    translated_labels=header_translated_labels,
                    field_dictionary=context.field_dictionary,
                    threshold=DEFAULT_AUTO_MAPPING_THRESHOLD,
                    ai_provider=context.ai_provider,  # Pass AI provider for semantic matching
                )
                logger.info(
                    "Matched %d header fields (threshold=%.1f)",
                    len(context.header_match_results),
                    DEFAULT_AUTO_MAPPING_THRESHOLD,
                )
            except Exception as e:
                logger.error("Header fuzzy matching failed: %s", str(e))
                context.recovery_events.append(
                    RecoveryEvent(
                        severity=RecoverySeverity.ERROR,
                        stage="fuzzy_matching",
                        message=f"Header fuzzy matching failed: {str(e)}",
                        metadata={"error_type": type(e).__name__},
                    )
                )

        # Match column fields
        column_translated_labels = [
            context.translation_map.get(
                column.raw_label,
                TranslatedLabel(
                    original_text=column.raw_label or "",
                    translated_text=column.raw_label or "",
                    target_language=DEFAULT_TARGET_LANGUAGE,
                ),
            )
            for column in context.classified_columns
            if column.raw_label
        ]

        if column_translated_labels:
            try:
                context.column_match_results = match_fields(
                    translated_labels=column_translated_labels,
                    field_dictionary=context.field_dictionary,
                    threshold=DEFAULT_AUTO_MAPPING_THRESHOLD,
                    ai_provider=context.ai_provider,  # Pass AI provider for semantic matching
                )
                logger.info(
                    "Matched %d column fields (threshold=%.1f)",
                    len(context.column_match_results),
                    DEFAULT_AUTO_MAPPING_THRESHOLD,
                )
            except Exception as e:
                logger.error("Column fuzzy matching failed: %s", str(e))
                context.recovery_events.append(
                    RecoveryEvent(
                        severity=RecoverySeverity.ERROR,
                        stage="fuzzy_matching",
                        message=f"Column fuzzy matching failed: {str(e)}",
                        metadata={"error_type": type(e).__name__},
                    )
                )

        logger.info("Stage 8: Fuzzy matching complete")
        return context


__all__ = ["FuzzyMatchingStage"]
