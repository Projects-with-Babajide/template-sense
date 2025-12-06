"""
Unit tests for CanonicalAggregationStage pipeline stage.

Tests the stage's ability to extract candidate blocks from sheet_summary
and pass them to the canonical aggregator.

This test file addresses a critical gap in test coverage that allowed BAT-72
to go undetected: unit tests for build_canonical_template() bypassed the stage
entirely by passing dataclasses directly.
"""

from pathlib import Path

from template_sense.pipeline.stages.base import PipelineContext
from template_sense.pipeline.stages.canonical_aggregation import CanonicalAggregationStage


def test_canonical_aggregation_extracts_table_blocks():
    """
    Test that table blocks from sheet_summary are passed to aggregator.

    This is a regression test for BAT-72: table_candidate_blocks were
    hardcoded to empty lists, causing all tables to be lost.
    """
    # Setup context with sheet_summary containing table blocks
    context = PipelineContext(
        file_path=Path("test.xlsx"),
        field_dictionary={"headers": {}, "columns": {}},
    )
    context.sheet_name = "Sheet1"
    context.sheet_summary = {
        "header_blocks": [],
        "table_blocks": [
            {
                "row_start": 18,
                "row_end": 23,
                "col_start": 2,
                "col_end": 8,
                "content": [[18, 2, "Item"], [18, 3, "Quantity"]],
                "score": 0.93,
                "detected_pattern": "high_density_consistent",
            }
        ],
    }
    context.classified_headers = []
    context.classified_columns = []  # Minimal for test
    context.extracted_line_items = []
    context.header_match_results = []
    context.column_match_results = []

    # Execute stage
    stage = CanonicalAggregationStage()
    result_context = stage.execute(context)

    # CRITICAL ASSERTION - This would have caught BAT-72:
    assert result_context.canonical_template is not None, "Canonical template should be created"
    assert (
        result_context.canonical_template.total_tables == 1
    ), "Table blocks from sheet_summary should be passed to aggregator"
    assert result_context.canonical_template.tables[0].row_start == 18
    assert result_context.canonical_template.tables[0].row_end == 23
    assert result_context.canonical_template.tables[0].col_start == 2
    assert result_context.canonical_template.tables[0].col_end == 8


def test_canonical_aggregation_extracts_header_blocks():
    """Test that header blocks from sheet_summary are passed to aggregator."""
    context = PipelineContext(
        file_path=Path("test.xlsx"),
        field_dictionary={"headers": {}, "columns": {}},
    )
    context.sheet_name = "Sheet1"
    context.sheet_summary = {
        "header_blocks": [
            {
                "row_start": 1,
                "row_end": 5,
                "col_start": 1,
                "col_end": 4,
                "content": [[1, 1, "Invoice No"], [1, 2, "INV-001"]],
                "label_value_pairs": [],
                "score": 0.85,
                "detected_pattern": "key_value_pairs",
            }
        ],
        "table_blocks": [],
    }
    context.classified_headers = []
    context.classified_columns = []
    context.extracted_line_items = []
    context.header_match_results = []
    context.column_match_results = []

    stage = CanonicalAggregationStage()
    result_context = stage.execute(context)

    # Verify header blocks were passed (metadata preserved)
    assert result_context.canonical_template is not None
    # Header blocks provide context but don't directly create canonical headers
    # (those come from classified_headers), but we verify no crash occurred
    assert result_context.canonical_template.total_header_fields == 0  # No classified headers


def test_canonical_aggregation_handles_empty_sheet_summary():
    """Test that stage handles missing or empty sheet_summary gracefully."""
    context = PipelineContext(
        file_path=Path("test.xlsx"),
        field_dictionary={"headers": {}, "columns": {}},
    )
    context.sheet_name = "Sheet1"
    context.sheet_summary = None  # Missing
    context.classified_headers = []
    context.classified_columns = []
    context.extracted_line_items = []
    context.header_match_results = []
    context.column_match_results = []

    stage = CanonicalAggregationStage()
    result_context = stage.execute(context)

    assert result_context.canonical_template is not None
    assert result_context.canonical_template.total_tables == 0
    assert result_context.canonical_template.total_header_fields == 0


def test_canonical_aggregation_handles_empty_blocks_lists():
    """Test that stage handles sheet_summary with empty blocks lists."""
    context = PipelineContext(
        file_path=Path("test.xlsx"),
        field_dictionary={"headers": {}, "columns": {}},
    )
    context.sheet_name = "Sheet1"
    context.sheet_summary = {
        "header_blocks": [],
        "table_blocks": [],
    }
    context.classified_headers = []
    context.classified_columns = []
    context.extracted_line_items = []
    context.header_match_results = []
    context.column_match_results = []

    stage = CanonicalAggregationStage()
    result_context = stage.execute(context)

    assert result_context.canonical_template is not None
    assert result_context.canonical_template.total_tables == 0
    assert result_context.canonical_template.total_header_fields == 0


def test_canonical_aggregation_with_multiple_table_blocks():
    """Test that stage handles multiple table blocks correctly."""
    context = PipelineContext(
        file_path=Path("test.xlsx"),
        field_dictionary={"headers": {}, "columns": {}},
    )
    context.sheet_name = "Sheet1"
    context.sheet_summary = {
        "header_blocks": [],
        "table_blocks": [
            {
                "row_start": 10,
                "row_end": 15,
                "col_start": 1,
                "col_end": 5,
                "content": [[10, 1, "Item"], [10, 2, "Qty"]],
                "score": 0.90,
                "detected_pattern": "high_numeric_density",
            },
            {
                "row_start": 20,
                "row_end": 23,
                "col_start": 1,
                "col_end": 3,
                "content": [[20, 1, "Charge"], [20, 2, "Amount"]],
                "score": 0.85,
                "detected_pattern": "column_consistency",
            },
        ],
    }
    context.classified_headers = []
    context.classified_columns = []
    context.extracted_line_items = []
    context.header_match_results = []
    context.column_match_results = []

    stage = CanonicalAggregationStage()
    result_context = stage.execute(context)

    assert result_context.canonical_template is not None
    assert result_context.canonical_template.total_tables == 2
    assert result_context.canonical_template.tables[0].row_start == 10
    assert result_context.canonical_template.tables[1].row_start == 20
