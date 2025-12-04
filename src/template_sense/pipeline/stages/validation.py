"""
ValidationStage: Validates pipeline inputs early.

This stage performs validation of file path and field dictionary before
any expensive operations are performed.
"""

import logging
from pathlib import Path

from template_sense.constants import SUPPORTED_FILE_EXTENSIONS
from template_sense.errors import FileValidationError, InvalidFieldDictionaryError
from template_sense.pipeline.stages.base import PipelineContext, PipelineStage

logger = logging.getLogger(__name__)


class ValidationStage(PipelineStage):
    """
    Stage 1: Validate pipeline inputs.

    Validates:
    - File path exists and has supported extension
    - Field dictionary is well-formed (non-empty dict with string keys/list values)

    Raises:
        FileValidationError: If file is invalid or not found
        InvalidFieldDictionaryError: If field dictionary is malformed
    """

    def execute(self, context: PipelineContext) -> PipelineContext:
        """Execute validation stage."""
        logger.info("Stage 1: Validating inputs...")

        # Validate file path
        self._validate_file_path(context.file_path)

        # Validate field dictionary
        self._validate_field_dictionary(context.field_dictionary)

        logger.debug(
            "Input validation passed: file=%s, field_dict_keys=%d",
            context.file_path,
            len(context.field_dictionary),
        )
        logger.info("Stage 1: Validation complete")

        return context

    def _validate_file_path(self, file_path: Path) -> None:
        """
        Validate file path.

        Args:
            file_path: Path to validate

        Raises:
            FileValidationError: If file is invalid or not found
        """
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

    def _validate_field_dictionary(self, field_dictionary: dict[str, list[str]]) -> None:
        """
        Validate field dictionary structure.

        Args:
            field_dictionary: Dictionary to validate

        Raises:
            InvalidFieldDictionaryError: If dictionary is malformed
        """
        # Check type
        if not isinstance(field_dictionary, dict):
            raise InvalidFieldDictionaryError(
                reason="Field dictionary must be a dict[str, list[str]]",
                field_dictionary=field_dictionary,
            )

        # Check not empty
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


__all__ = ["ValidationStage"]
