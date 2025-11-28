"""
AI-assisted classification and analysis modules.

This package contains modules for AI-based template analysis, including
header field classification, table column classification, and line item extraction.
"""

from template_sense.ai.header_classification import (
    ClassifiedHeaderField,
    classify_header_fields,
)
from template_sense.ai.line_item_extraction import (
    ExtractedLineItem,
    extract_line_items,
)

__all__ = [
    "ClassifiedHeaderField",
    "classify_header_fields",
    "ExtractedLineItem",
    "extract_line_items",
]
