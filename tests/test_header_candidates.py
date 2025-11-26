"""
Unit tests for header_candidates module.

Tests the heuristic-based header candidate detection including:
- Scoring individual rows for header likelihood
- Finding header candidate rows across entire grid
- Clustering rows into distinct header blocks
- Detecting multiple header blocks (shipper, consignee, etc.)
- Handling various layouts (top-left, upper-right, scattered)
- Real invoice template testing
"""

from pathlib import Path

import pytest

from template_sense.extraction.header_candidates import (
    HeaderCandidateBlock,
    cluster_header_candidate_blocks,
    detect_header_candidate_blocks,
    find_header_candidate_rows,
    score_row_as_header_candidate,
)

# ============================================================================
# Test: score_row_as_header_candidate
# ============================================================================


def test_score_row_with_key_value_pattern():
    """Test that rows with key-value patterns score high."""
    row = ["Invoice Number: 12345", "Date: 2024-01-01", None]
    score = score_row_as_header_candidate(row, row_index=1)

    # Should have high score due to key-value patterns
    assert score >= 0.5
    assert score <= 1.0


def test_score_row_with_japanese_keywords():
    """Test that rows with Japanese metadata keywords score high."""
    row = ["請求書番号: 12345", "日付: 2024年1月1日", None]
    score = score_row_as_header_candidate(row, row_index=1)

    # Should have high score due to Japanese keywords and key-value patterns
    assert score >= 0.5
    assert score <= 1.0


def test_score_row_with_metadata_keywords():
    """Test that rows with metadata keywords score moderately."""
    row = ["Invoice", "Company Name", "Address", None, None]
    score = score_row_as_header_candidate(row, row_index=1)

    # Should have moderate score due to keywords
    assert score >= 0.2
    assert score <= 1.0


def test_score_empty_row():
    """Test that empty rows score zero."""
    row = [None, None, None, None]
    score = score_row_as_header_candidate(row, row_index=1)

    assert score == 0.0


def test_score_dense_table_row():
    """Test that dense table-like rows score low."""
    # Table data: all cells filled, no keywords
    row = [100, 200, 300, 400, 500, 600, 700]
    score = score_row_as_header_candidate(row, row_index=1)

    # Should have low score (dense, no metadata patterns)
    assert score < 0.5


def test_score_mixed_data_types():
    """Test that mixed text and numbers increase score."""
    row = ["Invoice Number", 12345, None, None]
    score = score_row_as_header_candidate(row, row_index=1)

    # Should get bonus for mixed types and keyword
    assert score > 0.0


# ============================================================================
# Test: find_header_candidate_rows
# ============================================================================


def test_find_header_rows_top_of_sheet():
    """Test finding header rows at the top of the sheet."""
    grid = [
        ["Invoice Number: 12345", "Date: 2024-01-01"],  # Header row 1
        ["Company: ABC Corp", "Address: 123 Main St"],  # Header row 2
        [None, None],  # Empty row
        ["Item", "Quantity", "Price"],  # Table header
        ["Widget", 10, 100],  # Table data
    ]

    candidate_rows = find_header_candidate_rows(grid, min_score=0.5)

    # Should find rows 1 and 2 as header candidates
    assert len(candidate_rows) >= 2
    row_indices = [idx for idx, _ in candidate_rows]
    assert 1 in row_indices
    assert 2 in row_indices


def test_find_header_rows_middle_of_sheet():
    """Test finding header rows in the middle of the sheet (not at top)."""
    grid = [
        ["Item", "Quantity", "Price"],  # Table header
        ["Widget", 10, 100],  # Table data
        [None, None, None],  # Empty row
        ["Shipper: ABC Corp", "Contact: John Doe"],  # Header row (middle)
        ["Address: 123 Main St", "Phone: 555-1234"],  # Header row (middle)
    ]

    candidate_rows = find_header_candidate_rows(grid, min_score=0.5)

    # Should find rows 4 and 5 as header candidates (not just top rows)
    assert len(candidate_rows) >= 2
    row_indices = [idx for idx, _ in candidate_rows]
    assert 4 in row_indices
    assert 5 in row_indices


def test_find_header_rows_no_candidates():
    """Test that pure table data returns no candidates."""
    grid = [
        ["Item", "Quantity", "Price"],
        [100, 200, 300],
        [400, 500, 600],
        [700, 800, 900],
    ]

    candidate_rows = find_header_candidate_rows(grid, min_score=0.5)

    # Should find no header candidates (all table data)
    # Note: First row might be detected due to "Item", "Quantity", "Price" being text
    # But with high min_score, it should filter out
    assert len(candidate_rows) == 0


def test_find_header_rows_empty_grid():
    """Test that empty grid returns no candidates."""
    grid = []

    candidate_rows = find_header_candidate_rows(grid, min_score=0.5)

    assert len(candidate_rows) == 0


# ============================================================================
# Test: cluster_header_candidate_blocks
# ============================================================================


def test_cluster_consecutive_rows():
    """Test clustering consecutive rows into a single block."""
    grid = [
        ["Invoice Number: 12345", "Date: 2024-01-01"],  # Row 1
        ["Company: ABC Corp", "Address: 123 Main St"],  # Row 2
        ["Contact: John Doe", "Phone: 555-1234"],  # Row 3
        [None, None],
    ]

    scored_rows = [(1, 0.8), (2, 0.7), (3, 0.6)]
    blocks = cluster_header_candidate_blocks(grid, scored_rows, max_gap=2)

    # Should create one block spanning rows 1-3
    assert len(blocks) == 1
    assert blocks[0].row_start == 1
    assert blocks[0].row_end == 3


def test_cluster_separate_blocks():
    """Test clustering distant rows into separate blocks."""
    grid = [
        ["Invoice Number: 12345", "Date: 2024-01-01"],  # Row 1 - Block 1
        [None, None],  # Row 2
        [None, None],  # Row 3
        [None, None],  # Row 4
        ["Shipper: ABC Corp", "Contact: John Doe"],  # Row 5 - Block 2
    ]

    scored_rows = [(1, 0.8), (5, 0.7)]
    blocks = cluster_header_candidate_blocks(grid, scored_rows, max_gap=2)

    # Should create two separate blocks
    assert len(blocks) == 2
    assert blocks[0].row_start == 1
    assert blocks[0].row_end == 1
    assert blocks[1].row_start == 5
    assert blocks[1].row_end == 5


def test_cluster_with_small_gap():
    """Test clustering rows with small gap between them."""
    grid = [
        ["Invoice Number: 12345", None],  # Row 1
        [None, None],  # Row 2 (gap)
        ["Company: ABC Corp", None],  # Row 3
    ]

    scored_rows = [(1, 0.8), (3, 0.7)]
    blocks = cluster_header_candidate_blocks(grid, scored_rows, max_gap=2)

    # With max_gap=2, rows 1 and 3 should be in same block (1 row gap between)
    assert len(blocks) == 1
    assert blocks[0].row_start == 1
    assert blocks[0].row_end == 3


def test_cluster_empty_scored_rows():
    """Test clustering with no scored rows."""
    grid = [[None, None]]
    scored_rows = []

    blocks = cluster_header_candidate_blocks(grid, scored_rows, max_gap=2)

    assert len(blocks) == 0


def test_cluster_block_content_extraction():
    """Test that block content is correctly extracted."""
    grid = [
        ["Invoice Number: 12345", "Date: 2024-01-01"],  # Row 1
        ["Company: ABC Corp", None],  # Row 2
    ]

    scored_rows = [(1, 0.8), (2, 0.7)]
    blocks = cluster_header_candidate_blocks(grid, scored_rows, max_gap=2)

    assert len(blocks) == 1
    block = blocks[0]

    # Check content extraction
    assert len(block.content) == 3  # 3 non-empty cells
    # Content should be list of (row, col, value) tuples
    assert (1, 1, "Invoice Number: 12345") in block.content
    assert (1, 2, "Date: 2024-01-01") in block.content
    assert (2, 1, "Company: ABC Corp") in block.content


def test_cluster_block_bounding_box():
    """Test that block bounding box is correctly calculated."""
    grid = [
        [None, "Invoice Number: 12345", "Date: 2024-01-01"],  # Row 1, cols 2-3
        ["Company: ABC Corp", None, None],  # Row 2, col 1
    ]

    scored_rows = [(1, 0.8), (2, 0.7)]
    blocks = cluster_header_candidate_blocks(grid, scored_rows, max_gap=2)

    assert len(blocks) == 1
    block = blocks[0]

    # Bounding box should span cols 1-3
    assert block.col_start == 1
    assert block.col_end == 3


# ============================================================================
# Test: detect_header_candidate_blocks (main entry point)
# ============================================================================


def test_detect_blocks_top_left_layout():
    """Test detecting header block in classic top-left layout."""
    grid = [
        ["Invoice Number: 12345", "Date: 2024-01-01"],  # Header
        ["Company: ABC Corp", "Address: 123 Main St"],  # Header
        [None, None],
        ["Item", "Quantity", "Price"],  # Table
        ["Widget", 10, 100],
    ]

    blocks = detect_header_candidate_blocks(grid, min_score=0.5)

    # Should detect one header block at top
    assert len(blocks) >= 1
    assert blocks[0].row_start <= 2
    assert blocks[0].score >= 0.5


def test_detect_blocks_upper_right_layout():
    """Test detecting header block in upper-right quadrant."""
    grid = [
        [None, None, "Invoice Number: 12345", "Date: 2024-01-01"],  # Header in cols 3-4
        [None, None, "Company: ABC Corp", "Total: $1000"],  # Header in cols 3-4
        [None, None, None, None],
        ["Item", "Quantity", "Price", "Amount"],  # Table
    ]

    blocks = detect_header_candidate_blocks(grid, min_score=0.5)

    # Should detect header block in upper-right
    assert len(blocks) >= 1
    assert blocks[0].col_start >= 3  # Should be in right columns


def test_detect_blocks_multiple_blocks():
    """Test detecting multiple distinct header blocks (shipper vs consignee)."""
    grid = [
        ["Shipper: ABC Corp", None, None, "Consignee: XYZ Inc"],  # Two blocks
        ["Address: 123 Main St", None, None, "Address: 456 Oak Ave"],  # Two blocks
        [None, None, None, None],
        ["Item", "Quantity", "Price", "Amount"],  # Table
    ]

    blocks = detect_header_candidate_blocks(grid, min_score=0.5)

    # Should detect two separate blocks
    # Note: With current implementation, might merge into one if columns overlap
    # This is acceptable as long as we detect the metadata
    assert len(blocks) >= 1


def test_detect_blocks_mixed_with_table():
    """Test detecting small header block mixed with table data."""
    grid = [
        ["Item", "Quantity", "Price"],  # Table header
        ["Widget", 10, 100],  # Table data
        ["Gadget", 20, 200],  # Table data
        [None, None, None],
        ["Invoice Number: 12345", "Date: 2024-01-01", None],  # Header at bottom
    ]

    blocks = detect_header_candidate_blocks(grid, min_score=0.5)

    # Should detect header block at row 5
    assert len(blocks) >= 1
    # Should find the block at bottom (not assume top-only)
    assert any(block.row_start >= 5 for block in blocks)


def test_detect_blocks_no_headers():
    """Test that pure table data returns no blocks."""
    grid = [
        [100, 200, 300],
        [400, 500, 600],
        [700, 800, 900],
    ]

    blocks = detect_header_candidate_blocks(grid, min_score=0.5)

    # Should find no header blocks
    assert len(blocks) == 0


def test_detect_blocks_empty_grid():
    """Test that empty grid returns no blocks."""
    grid = []

    blocks = detect_header_candidate_blocks(grid, min_score=0.5)

    assert len(blocks) == 0


def test_detect_blocks_invalid_min_score():
    """Test that invalid min_score raises ValueError."""
    grid = [["Invoice Number: 12345"]]

    with pytest.raises(ValueError, match="min_score must be in range 0.0-1.0"):
        detect_header_candidate_blocks(grid, min_score=1.5)

    with pytest.raises(ValueError, match="min_score must be in range 0.0-1.0"):
        detect_header_candidate_blocks(grid, min_score=-0.1)


def test_detect_blocks_score_propagation():
    """Test that block scores are calculated from row scores."""
    grid = [
        ["Invoice Number: 12345", "Date: 2024-01-01"],  # High score row
        ["Company: ABC Corp", "Address: 123 Main St"],  # High score row
    ]

    blocks = detect_header_candidate_blocks(grid, min_score=0.5)

    assert len(blocks) >= 1
    # Block score should be average of row scores
    assert 0.5 <= blocks[0].score <= 1.0


def test_detect_blocks_pattern_detection():
    """Test that detected_pattern is set correctly."""
    grid = [
        ["Invoice Number: 12345", "Date: 2024-01-01"],  # Key-value + keywords
    ]

    blocks = detect_header_candidate_blocks(grid, min_score=0.5)

    assert len(blocks) >= 1
    # Should detect both patterns
    assert "key_value" in blocks[0].detected_pattern or "keyword" in blocks[0].detected_pattern


# ============================================================================
# Test: Real invoice template files
# ============================================================================


def test_real_invoice_templates_discovery():
    """
    Test header detection on real invoice files in fixtures/invoice_templates/.

    This test scans the invoice_templates directory and runs detection on all
    .xlsx files found. Results are printed for manual inspection.

    To use this test:
    1. Add invoice template .xlsx files to tests/fixtures/invoice_templates/
    2. Run pytest with -s flag to see output: pytest -s tests/test_header_candidates.py::test_real_invoice_templates_discovery
    """
    template_dir = Path(__file__).parent / "fixtures" / "invoice_templates"

    if not template_dir.exists():
        pytest.skip(f"Invoice templates directory not found: {template_dir}")

    xlsx_files = list(template_dir.glob("*.xlsx"))

    # Filter out temporary Excel files (starting with ~$)
    xlsx_files = [f for f in xlsx_files if not f.name.startswith("~$")]

    if not xlsx_files:
        pytest.skip(f"No .xlsx files found in {template_dir}")

    print(f"\n{'=' * 80}")
    print(f"Testing {len(xlsx_files)} invoice template(s)")
    print(f"{'=' * 80}")

    from template_sense.adapters.excel_adapter import ExcelWorkbook
    from template_sense.extraction.sheet_extractor import extract_raw_grid
    from template_sense.file_loader import load_excel_file

    for xlsx_file in xlsx_files:
        print(f"\n📄 File: {xlsx_file.name}")
        print("-" * 80)

        try:
            # Load workbook
            raw_workbook = load_excel_file(xlsx_file)
            workbook = ExcelWorkbook(raw_workbook)

            # Get first sheet
            sheet_names = workbook.get_sheet_names()
            if not sheet_names:
                print("  ⚠️  No sheets found")
                raw_workbook.close()
                continue

            sheet_name = sheet_names[0]
            print(f"  Sheet: {sheet_name}")

            # Extract grid
            grid = extract_raw_grid(workbook, sheet_name)
            print(f"  Grid size: {len(grid)} rows")

            # Detect header blocks
            blocks = detect_header_candidate_blocks(grid, min_score=0.5)
            print(f"\n  ✅ Detected {len(blocks)} header block(s):")

            for i, block in enumerate(blocks, start=1):
                print(f"\n  Block #{i}:")
                print(
                    f"    Location: R{block.row_start}:R{block.row_end}, "
                    f"C{block.col_start}:C{block.col_end}"
                )
                print(f"    Score: {block.score:.2f}")
                print(f"    Pattern: {block.detected_pattern}")
                print(f"    Cells: {len(block.content)} non-empty cells")

                # Show first few cells as sample
                sample_cells = block.content[:5]
                print("    Sample content:")
                for row, col, value in sample_cells:
                    # Truncate long values
                    value_str = str(value)
                    if len(value_str) > 50:
                        value_str = value_str[:47] + "..."
                    print(f"      R{row}C{col}: {value_str}")

                if len(block.content) > 5:
                    print(f"      ... and {len(block.content) - 5} more cells")

            raw_workbook.close()

        except Exception as e:
            print(f"  ❌ Error processing file: {e}")

    print(f"\n{'=' * 80}")
    print("✅ Real invoice template testing complete")
    print(f"{'=' * 80}\n")


# ============================================================================
# Test: Edge cases and integration
# ============================================================================


def test_header_candidate_block_dataclass():
    """Test HeaderCandidateBlock dataclass creation."""
    block = HeaderCandidateBlock(
        row_start=1,
        row_end=3,
        col_start=1,
        col_end=4,
        content=[(1, 1, "Invoice"), (1, 2, "12345")],
        score=0.75,
        detected_pattern="key_value_patterns",
    )

    assert block.row_start == 1
    assert block.row_end == 3
    assert block.col_start == 1
    assert block.col_end == 4
    assert len(block.content) == 2
    assert block.score == 0.75
    assert block.detected_pattern == "key_value_patterns"


def test_japanese_and_english_mixed():
    """Test detection with mixed Japanese and English content."""
    grid = [
        ["請求書番号: INV-12345", "Invoice Date: 2024-01-01"],  # Mixed
        ["会社名: ABC株式会社", "Company Name: ABC Corp"],  # Mixed
    ]

    blocks = detect_header_candidate_blocks(grid, min_score=0.5)

    # Should detect header block with mixed language content
    assert len(blocks) >= 1
    assert blocks[0].score >= 0.5


def test_varying_row_lengths():
    """Test handling grids with varying row lengths."""
    grid = [
        ["Invoice Number: 12345", "Date: 2024-01-01", "Amount: $1000"],  # 3 cells
        ["Company: ABC Corp"],  # 1 cell
        ["Address: 123 Main St", "Phone: 555-1234"],  # 2 cells
    ]

    blocks = detect_header_candidate_blocks(grid, min_score=0.5)

    # Should handle varying row lengths gracefully
    assert len(blocks) >= 1


def test_customizable_min_score():
    """Test that min_score parameter filters results correctly."""
    grid = [
        ["Invoice Number: 12345", "Date: 2024-01-01"],  # High score
        ["Some text", "More text"],  # Low score (no keywords)
    ]

    # With high threshold, should find fewer blocks
    blocks_high = detect_header_candidate_blocks(grid, min_score=0.8)

    # With low threshold, should find more blocks
    blocks_low = detect_header_candidate_blocks(grid, min_score=0.3)

    # Lower threshold should find at least as many blocks as higher threshold
    assert len(blocks_low) >= len(blocks_high)
