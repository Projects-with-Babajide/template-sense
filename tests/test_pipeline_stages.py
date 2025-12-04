"""
Unit tests for pipeline stages.

This module tests each pipeline stage in isolation to ensure correct behavior
and proper context updates.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from template_sense.errors import FileValidationError, InvalidFieldDictionaryError
from template_sense.pipeline.stages.ai_provider_setup import AIProviderSetupStage
from template_sense.pipeline.stages.base import PipelineContext
from template_sense.pipeline.stages.file_loading import FileLoadingStage
from template_sense.pipeline.stages.metadata import MetadataStage
from template_sense.pipeline.stages.validation import ValidationStage
from template_sense.recovery.error_recovery import RecoveryEvent, RecoverySeverity


class TestPipelineContext:
    """Test PipelineContext dataclass."""

    def test_context_initialization(self):
        """Context initializes with required fields."""
        file_path = Path("test.xlsx")
        field_dict = {"invoice_number": ["Invoice No"]}

        context = PipelineContext(
            file_path=file_path,
            field_dictionary=field_dict,
        )

        assert context.file_path == file_path
        assert context.field_dictionary == field_dict
        assert context.workbook is None
        assert context.sheet_name is None
        assert context.recovery_events == []

    def test_context_to_dict(self):
        """Context.to_dict() returns correct structure."""
        context = PipelineContext(
            file_path=Path("test.xlsx"),
            field_dictionary={"invoice_number": ["Invoice No"]},
        )
        context.normalized_output = {"test": "data"}
        context.metadata = {"sheet_name": "Sheet1"}
        context.recovery_events = [
            RecoveryEvent(
                severity=RecoverySeverity.WARNING,
                stage="test",
                message="test message",
            )
        ]

        result = context.to_dict()

        assert "normalized_output" in result
        assert "recovery_events" in result
        assert "metadata" in result
        assert result["normalized_output"] == {"test": "data"}
        assert result["metadata"] == {"sheet_name": "Sheet1"}
        assert len(result["recovery_events"]) == 1


class TestValidationStage:
    """Test ValidationStage."""

    def test_validation_stage_valid_inputs(self, tmp_path):
        """ValidationStage accepts valid inputs."""
        # Create a temporary test file
        test_file = tmp_path / "test.xlsx"
        test_file.write_text("test")

        context = PipelineContext(
            file_path=test_file,
            field_dictionary={"invoice_number": ["Invoice No"]},
        )

        stage = ValidationStage()
        result = stage.execute(context)

        # Context should be returned unchanged
        assert result.file_path == test_file
        assert result.field_dictionary == {"invoice_number": ["Invoice No"]}

    def test_validation_stage_file_not_found(self):
        """ValidationStage raises error for non-existent file."""
        context = PipelineContext(
            file_path=Path("nonexistent.xlsx"),
            field_dictionary={"invoice_number": ["Invoice No"]},
        )

        stage = ValidationStage()
        with pytest.raises(FileValidationError, match="File not found"):
            stage.execute(context)

    def test_validation_stage_invalid_file_extension(self, tmp_path):
        """ValidationStage raises error for invalid file extension."""
        test_file = tmp_path / "test.pdf"
        test_file.write_text("test")

        context = PipelineContext(
            file_path=test_file,
            field_dictionary={"invoice_number": ["Invoice No"]},
        )

        stage = ValidationStage()
        with pytest.raises(FileValidationError, match="Unsupported file format"):
            stage.execute(context)

    def test_validation_stage_empty_field_dictionary(self, tmp_path):
        """ValidationStage raises error for empty field dictionary."""
        test_file = tmp_path / "test.xlsx"
        test_file.write_text("test")

        context = PipelineContext(
            file_path=test_file,
            field_dictionary={},
        )

        stage = ValidationStage()
        with pytest.raises(InvalidFieldDictionaryError, match="cannot be empty"):
            stage.execute(context)

    def test_validation_stage_invalid_field_dictionary_structure(self, tmp_path):
        """ValidationStage raises error for malformed field dictionary."""
        test_file = tmp_path / "test.xlsx"
        test_file.write_text("test")

        # Empty list value
        context = PipelineContext(
            file_path=test_file,
            field_dictionary={"invoice_number": []},
        )

        stage = ValidationStage()
        with pytest.raises(InvalidFieldDictionaryError, match="cannot be empty list"):
            stage.execute(context)


class TestFileLoadingStage:
    """Test FileLoadingStage."""

    @patch("template_sense.pipeline.stages.file_loading.load_excel_file")
    @patch("template_sense.pipeline.stages.file_loading.ExcelWorkbook")
    def test_file_loading_stage_success(self, mock_workbook_class, mock_load_file, tmp_path):
        """FileLoadingStage loads workbook and selects sheet."""
        test_file = tmp_path / "test.xlsx"
        test_file.write_text("test")

        # Mock workbook
        mock_raw_workbook = Mock()
        mock_load_file.return_value = mock_raw_workbook

        mock_workbook = Mock()
        mock_workbook.get_sheet_names.return_value = ["Sheet1", "Sheet2"]
        mock_workbook_class.return_value = mock_workbook

        context = PipelineContext(
            file_path=test_file,
            field_dictionary={"invoice_number": ["Invoice No"]},
        )

        stage = FileLoadingStage()
        result = stage.execute(context)

        # Workbook should be set
        assert result.workbook == mock_workbook
        # First sheet should be selected
        assert result.sheet_name == "Sheet1"
        # load_excel_file should be called with correct path
        mock_load_file.assert_called_once_with(test_file)


class TestAIProviderSetupStage:
    """Test AIProviderSetupStage."""

    @patch("template_sense.pipeline.stages.ai_provider_setup.get_ai_provider")
    def test_ai_provider_setup_stage_success(self, mock_get_provider):
        """AIProviderSetupStage initializes AI provider."""
        # Mock AI provider
        mock_provider = Mock()
        mock_provider.config = Mock(provider="openai", model="gpt-4")
        mock_get_provider.return_value = mock_provider

        context = PipelineContext(
            file_path=Path("test.xlsx"),
            field_dictionary={"invoice_number": ["Invoice No"]},
        )

        stage = AIProviderSetupStage()
        result = stage.execute(context)

        # AI provider should be set
        assert result.ai_provider == mock_provider
        # get_ai_provider should be called with context.ai_config
        mock_get_provider.assert_called_once_with(context.ai_config)


class TestMetadataStage:
    """Test MetadataStage."""

    def test_metadata_stage_builds_metadata(self):
        """MetadataStage builds metadata and closes workbook."""
        # Mock workbook
        mock_workbook = Mock()

        # Mock AI provider
        mock_provider = Mock()
        mock_provider.config = Mock(provider="openai", model="gpt-4")

        context = PipelineContext(
            file_path=Path("test.xlsx"),
            field_dictionary={"invoice_number": ["Invoice No"]},
        )
        context.workbook = mock_workbook
        context.sheet_name = "Sheet1"
        context.ai_provider = mock_provider

        stage = MetadataStage()
        result = stage.execute(context)

        # Metadata should be set
        assert result.metadata is not None
        assert result.metadata["sheet_name"] == "Sheet1"
        # Workbook should be closed
        mock_workbook.close.assert_called_once()

    def test_metadata_stage_without_ai_provider(self):
        """MetadataStage works without AI provider."""
        mock_workbook = Mock()

        context = PipelineContext(
            file_path=Path("test.xlsx"),
            field_dictionary={"invoice_number": ["Invoice No"]},
        )
        context.workbook = mock_workbook
        context.sheet_name = "Sheet1"
        context.ai_provider = None  # No AI provider

        stage = MetadataStage()
        result = stage.execute(context)

        # Metadata should still be set
        assert result.metadata is not None
        assert result.metadata["sheet_name"] == "Sheet1"
        # Workbook should be closed
        mock_workbook.close.assert_called_once()
