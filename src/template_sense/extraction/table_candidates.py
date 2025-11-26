"""
Global table candidate detection for Template Sense.

This module implements field-agnostic, heuristics-only detection of table regions
(line-item data blocks) anywhere on a sheet. Tables refer to regions containing
product lists, charge tables, quantity/weight sections, etc.

IMPORTANT: This module uses ONLY structural patterns (cell density, data types,
column consistency). It does NOT use field names, keywords, or domain knowledge.

This module does NOT:
- Call any AI services
- Perform semantic classification
- Interpret field meanings or values
- Assume tables are in specific positions
- Use hardcoded field names or keywords

This module DOES:
- Scan the entire grid for table-like patterns
- Detect multiple distinct table blocks (e.g., items + shipping charges)
- Return structured, deterministic output ready for AI consumption
- Support multilingual content (content-agnostic)

Functions:
    score_row_as_table_candidate: Score a single row's likelihood of being table data
    find_table_candidate_rows: Scan grid and identify high-scoring rows
    cluster_table_blocks: Group consecutive rows into distinct table blocks
    detect_table_candidate_blocks: Main entry point for table detection

Usage Example:
    from template_sense.extraction.sheet_extractor import extract_raw_grid
    from template_sense.extraction.table_candidates import detect_table_candidate_blocks
    from template_sense.file_loader import load_excel_file
    from template_sense.adapters.excel_adapter import ExcelWorkbook

    raw_workbook = load_excel_file(Path("invoice.xlsx"))
    workbook = ExcelWorkbook(raw_workbook)
    grid = extract_raw_grid(workbook, "Sheet1")

    blocks = detect_table_candidate_blocks(grid)
    for block in blocks:
        print(f"Table block at R{block.row_start}:R{block.row_end}, "
              f"C{block.col_start}:C{block.col_end}, score={block.score:.2f}")
"""

import logging
import re
from dataclasses import dataclass
from typing import Any

from template_sense.constants import DEFAULT_MIN_TABLE_ROWS, DEFAULT_TABLE_MIN_SCORE

# Set up module logger
logger = logging.getLogger(__name__)


@dataclass
class TableCandidateBlock:
    """
    Represents a detected table/line-item data block.

    A table candidate block is a region of the sheet that likely contains
    tabular line-item data (as opposed to metadata/headers). Examples include
    product lists, charge tables, quantity/weight sections, etc.

    Attributes:
        row_start: First row of block (1-based, Excel convention)
        row_end: Last row of block (1-based, inclusive)
        col_start: First column of block (1-based, Excel convention)
        col_end: Last column of block (1-based, inclusive)
        content: List of (row, col, value) tuples for all non-empty cells in block
        score: Confidence score (0.0-1.0) indicating likelihood this is a table block
        detected_pattern: Description of detection pattern (e.g., "numeric_density",
                          "column_consistency")
    """

    row_start: int
    row_end: int
    col_start: int
    col_end: int
    content: list[tuple[int, int, Any]]
    score: float
    detected_pattern: str


def _contains_key_value_pattern(text: str) -> bool:
    """
    Check if text contains key-value separator patterns.

    This helps distinguish header metadata ("Label: Value") from table data.

    Args:
        text: Text to check

    Returns:
        True if key-value pattern detected, False otherwise
    """
    if not isinstance(text, str):
        return False

    # Colon pattern: at least one non-whitespace char, colon, optional space, value
    if re.search(r"\S+\s*:\s*\S", text):
        return True

    # Multiple spaces pattern: word, 2+ spaces, word
    return bool(re.search(r"\S+\s{2,}\S", text))


def _calculate_cell_density(row: list[Any]) -> float:
    """
    Calculate the ratio of non-empty cells to total cells in a row.

    Args:
        row: List of cell values

    Returns:
        Density ratio (0.0-1.0)
    """
    if not row:
        return 0.0

    non_empty_count = sum(1 for cell in row if cell not in (None, ""))
    return non_empty_count / len(row)


def _calculate_numeric_density(row: list[Any]) -> float:
    """
    Calculate the ratio of numeric cells to non-empty cells in a row.

    Numeric cells are: int, float, or numeric strings.
    This is a key indicator of table data (prices, quantities, weights, etc.)

    Args:
        row: List of cell values

    Returns:
        Numeric density ratio (0.0-1.0)
    """
    non_empty_cells = [cell for cell in row if cell not in (None, "")]

    if not non_empty_cells:
        return 0.0

    numeric_count = 0
    for cell in non_empty_cells:
        # Direct numeric types
        if isinstance(cell, int | float):
            numeric_count += 1
        # Numeric strings
        elif isinstance(cell, str):
            # Try to parse as number
            try:
                float(cell.strip())
                numeric_count += 1
            except (ValueError, AttributeError):
                pass

    return numeric_count / len(non_empty_cells)


def _calculate_average_cell_length(row: list[Any]) -> float:
    """
    Calculate average character length of non-empty cells in a row.

    Table cells tend to be shorter than metadata cells (which have long text).

    Args:
        row: List of cell values

    Returns:
        Average cell length in characters
    """
    non_empty_cells = [cell for cell in row if cell not in (None, "")]

    if not non_empty_cells:
        return 0.0

    total_length = sum(len(str(cell)) for cell in non_empty_cells)
    return total_length / len(non_empty_cells)


def score_row_as_table_candidate(row: list[Any], row_index: int) -> float:
    """
    Score a single row's likelihood of containing table/line-item data.

    This function uses ONLY field-agnostic structural heuristics. It does NOT
    check for specific field names or keywords.

    Scoring criteria (all field-agnostic):
    - High cell density (>70% filled) → +0.4 (tables are dense)
    - High numeric density (>40% numeric) → +0.3 to +0.5 (tables have numbers)
    - Short cell values (avg < 30 chars) → +0.2 (table cells are concise)
    - No key-value patterns → +0.2 (distinguishes from headers)
    - Moderate density (30-70% filled) → +0.2
    - Very sparse rows (<30% filled) → -0.3 (likely metadata)
    - Key-value patterns present → -0.4 (likely headers)

    Args:
        row: List of cell values (Any type: str, int, float, datetime, None, etc.)
        row_index: 1-based row index (for logging/debugging)

    Returns:
        Score from 0.0 to 1.0 (clamped)
    """
    score = 0.0
    pattern_details = []

    # Count non-empty cells
    non_empty_cells = [cell for cell in row if cell not in (None, "")]

    if not non_empty_cells:
        return 0.0  # Empty row

    # Calculate metrics
    cell_density = _calculate_cell_density(row)
    numeric_density = _calculate_numeric_density(row)
    avg_cell_length = _calculate_average_cell_length(row)

    # Heuristic 1: High cell density (tables are densely populated)
    if cell_density > 0.7:
        score += 0.4
        pattern_details.append("high_density")
    elif 0.3 <= cell_density <= 0.7:
        # Moderate density also suggests table (some columns might be empty)
        score += 0.2
        pattern_details.append("moderate_density")
    elif cell_density < 0.3:
        # Very sparse - likely metadata
        score -= 0.3
        pattern_details.append("sparse_row")

    # Heuristic 2: High numeric density (tables contain numbers)
    if numeric_density > 0.6:
        score += 0.5
        pattern_details.append("high_numeric")
    elif numeric_density > 0.4:
        score += 0.3
        pattern_details.append("moderate_numeric")

    # Heuristic 3: Short cell values (table cells are concise)
    if avg_cell_length < 30:
        score += 0.2
        pattern_details.append("short_cells")

    # Heuristic 4: Absence of key-value patterns (distinguishes from headers)
    key_value_count = sum(1 for cell in non_empty_cells if _contains_key_value_pattern(str(cell)))
    if key_value_count == 0:
        score += 0.2
        pattern_details.append("no_key_value")
    else:
        # Presence of key-value patterns suggests header, not table
        score -= 0.4
        pattern_details.append("has_key_value")

    # Clamp score to 0.0-1.0 range
    score = max(0.0, min(1.0, score))

    logger.debug(
        "Row %d scored %.2f as table candidate (patterns: %s, "
        "density: %.2f, numeric: %.2f, avg_len: %.1f, cells: %d)",
        row_index,
        score,
        ", ".join(pattern_details) if pattern_details else "none",
        cell_density,
        numeric_density,
        avg_cell_length,
        len(non_empty_cells),
    )

    return score


def find_table_candidate_rows(
    grid: list[list[Any]], min_score: float = DEFAULT_TABLE_MIN_SCORE
) -> list[tuple[int, float]]:
    """
    Scan entire grid and identify rows with high table scores.

    This function does NOT assume table position — it scans every row in the grid.

    Args:
        grid: 2D list of cell values (list of rows)
        min_score: Minimum score threshold (0.0-1.0). Default: 0.5

    Returns:
        List of (row_index, score) tuples for rows scoring above threshold.
        Row indices are 1-based (Excel convention).
        Returns empty list if no candidates found.

    Example:
        >>> grid = [["Invoice", "Date"], [None, None], ["Item", 10, 25.50, 255.00]]
        >>> find_table_candidate_rows(grid, min_score=0.5)
        [(3, 0.8)]
    """
    logger.debug(
        "Scanning grid (%d rows) for table candidates (min_score=%.2f)",
        len(grid),
        min_score,
    )

    candidate_rows = []

    for row_idx, row in enumerate(grid, start=1):
        score = score_row_as_table_candidate(row, row_idx)

        if score >= min_score:
            candidate_rows.append((row_idx, score))
            logger.debug("Row %d is a table candidate (score: %.2f)", row_idx, score)

    logger.info(
        "Found %d table candidate rows out of %d total rows",
        len(candidate_rows),
        len(grid),
    )

    return candidate_rows


def cluster_table_blocks(
    grid: list[list[Any]],
    scored_rows: list[tuple[int, float]],
    min_consecutive: int = DEFAULT_MIN_TABLE_ROWS,
) -> list[TableCandidateBlock]:
    """
    Group consecutive high-scoring rows into distinct table blocks.

    Tables are defined as regions with at least `min_consecutive` consecutive rows.
    Single or double isolated rows are NOT considered tables.

    Args:
        grid: 2D list of cell values
        scored_rows: List of (row_index, score) tuples (1-based indices)
        min_consecutive: Minimum consecutive rows required to form a table. Default: 3

    Returns:
        List of TableCandidateBlock instances, sorted by row_start.
        Returns empty list if no valid table blocks found.

    Example:
        >>> scored_rows = [(5, 0.8), (6, 0.7), (7, 0.9), (8, 0.8)]
        >>> blocks = cluster_table_blocks(grid, scored_rows, min_consecutive=3)
        >>> len(blocks)
        1  # One block spanning rows 5-8
    """
    if not scored_rows:
        logger.info("No scored rows to cluster")
        return []

    logger.debug(
        "Clustering %d scored rows into table blocks (min_consecutive=%d)",
        len(scored_rows),
        min_consecutive,
    )

    # Sort by row index
    sorted_rows = sorted(scored_rows, key=lambda x: x[0])

    blocks = []
    current_cluster = [sorted_rows[0]]

    # Cluster consecutive rows
    for row_idx, score in sorted_rows[1:]:
        last_row_idx = current_cluster[-1][0]

        # If consecutive (next row), add to current cluster
        if row_idx == last_row_idx + 1:
            current_cluster.append((row_idx, score))
        else:
            # Non-consecutive: finalize current cluster if it meets minimum
            if len(current_cluster) >= min_consecutive:
                blocks.append(_create_table_block_from_cluster(grid, current_cluster))
            else:
                logger.debug(
                    "Discarding cluster of %d rows (below min_consecutive=%d)",
                    len(current_cluster),
                    min_consecutive,
                )
            current_cluster = [(row_idx, score)]

    # Finalize last cluster
    if len(current_cluster) >= min_consecutive:
        blocks.append(_create_table_block_from_cluster(grid, current_cluster))
    else:
        logger.debug(
            "Discarding final cluster of %d rows (below min_consecutive=%d)",
            len(current_cluster),
            min_consecutive,
        )

    logger.info(
        "Clustered %d rows into %d table block(s) (min_consecutive=%d)",
        len(scored_rows),
        len(blocks),
        min_consecutive,
    )

    return blocks


def _create_table_block_from_cluster(
    grid: list[list[Any]], cluster: list[tuple[int, float]]
) -> TableCandidateBlock:
    """
    Create a TableCandidateBlock from a cluster of scored rows.

    Args:
        grid: 2D list of cell values
        cluster: List of (row_index, score) tuples (1-based)

    Returns:
        TableCandidateBlock instance
    """
    row_indices = [row_idx for row_idx, _ in cluster]
    scores = [score for _, score in cluster]

    row_start = min(row_indices)
    row_end = max(row_indices)

    # Calculate average score for the block
    avg_score = sum(scores) / len(scores)

    # Extract content and determine column range
    content = []
    col_indices = []

    for row_idx in range(row_start, row_end + 1):
        # Convert to 0-based index for grid access
        grid_row_idx = row_idx - 1

        if grid_row_idx < len(grid):
            row = grid[grid_row_idx]

            for col_idx, cell in enumerate(row, start=1):
                if cell not in (None, ""):
                    content.append((row_idx, col_idx, cell))
                    col_indices.append(col_idx)

    # Determine column range
    if col_indices:
        col_start = min(col_indices)
        col_end = max(col_indices)
    else:
        # Empty block (shouldn't happen, but handle gracefully)
        col_start = 1
        col_end = 1

    # Determine primary detection pattern
    # Analyze patterns across all cells in the block
    numeric_cells = sum(1 for _, _, cell in content if isinstance(cell, int | float))
    total_cells = len(content)
    numeric_ratio = numeric_cells / total_cells if total_cells > 0 else 0.0

    if numeric_ratio > 0.6:
        pattern = "high_numeric_density"
    elif numeric_ratio > 0.4:
        pattern = "moderate_numeric_density"
    elif avg_score > 0.7:
        pattern = "high_density_consistent"
    else:
        pattern = "column_consistency"

    return TableCandidateBlock(
        row_start=row_start,
        row_end=row_end,
        col_start=col_start,
        col_end=col_end,
        content=content,
        score=avg_score,
        detected_pattern=pattern,
    )


def detect_table_candidate_blocks(
    grid: list[list[Any]],
    min_score: float = DEFAULT_TABLE_MIN_SCORE,
    min_consecutive: int = DEFAULT_MIN_TABLE_ROWS,
) -> list[TableCandidateBlock]:
    """
    Main entry point for detecting table/line-item data blocks in a grid.

    This function orchestrates the entire table detection pipeline:
    1. Scan all rows for table-like patterns (field-agnostic)
    2. Cluster consecutive high-scoring rows into distinct blocks
    3. Filter blocks by minimum consecutive rows requirement
    4. Return structured TableCandidateBlock instances

    Important: This function scans the ENTIRE grid, not just specific regions.
    It can detect multiple table blocks (e.g., items + shipping charges).

    Args:
        grid: 2D list of cell values (list of rows)
        min_score: Minimum score threshold for table candidates (0.0-1.0). Default: 0.5
        min_consecutive: Minimum consecutive rows to form a table. Default: 3

    Returns:
        List of TableCandidateBlock instances, sorted by row_start (top to bottom).
        Returns empty list if no table candidates found or grid is empty.

    Raises:
        ValueError: If min_score is not in range 0.0-1.0 or min_consecutive < 1

    Example:
        >>> from template_sense.extraction.sheet_extractor import extract_raw_grid
        >>> grid = extract_raw_grid(workbook, "Sheet1")
        >>> blocks = detect_table_candidate_blocks(grid)
        >>> print(f"Found {len(blocks)} table blocks")
        Found 1 table blocks
        >>> for block in blocks:
        ...     print(f"Block at R{block.row_start}:R{block.row_end}, score={block.score:.2f}")
        Block at R5:R10, score=0.78
    """
    # Validate inputs
    if not 0.0 <= min_score <= 1.0:
        raise ValueError(f"min_score must be in range 0.0-1.0, got {min_score}")

    if min_consecutive < 1:
        raise ValueError(f"min_consecutive must be >= 1, got {min_consecutive}")

    if not grid:
        logger.info("Grid is empty, returning no table blocks")
        return []

    logger.info(
        "Detecting table candidate blocks in grid (%d rows, min_score=%.2f, min_consecutive=%d)",
        len(grid),
        min_score,
        min_consecutive,
    )

    # Step 1: Find candidate rows
    scored_rows = find_table_candidate_rows(grid, min_score=min_score)

    if not scored_rows:
        logger.info("No table candidate rows found")
        return []

    # Step 2: Cluster into blocks with minimum consecutive requirement
    blocks = cluster_table_blocks(grid, scored_rows, min_consecutive=min_consecutive)

    logger.info(
        "Table detection complete: found %d block(s) from %d candidate rows",
        len(blocks),
        len(scored_rows),
    )

    return blocks


__all__ = [
    "TableCandidateBlock",
    "score_row_as_table_candidate",
    "find_table_candidate_rows",
    "cluster_table_blocks",
    "detect_table_candidate_blocks",
]
