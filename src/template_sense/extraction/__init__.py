"""
Extraction utilities for Template Sense.

This package contains modules for extracting structured data from Excel templates,
including sheet-level extraction utilities and future heuristic-based detection modules.
"""

from template_sense.extraction.sheet_extractor import (
    extract_non_empty_columns,
    extract_non_empty_rows,
    extract_raw_grid,
    get_used_range,
)

__all__ = [
    "extract_raw_grid",
    "extract_non_empty_rows",
    "extract_non_empty_columns",
    "get_used_range",
]
