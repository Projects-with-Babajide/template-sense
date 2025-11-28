"""
AI-assisted classification and analysis modules.

This package contains modules for AI-based template analysis, including
header field classification and table column classification.
"""

from template_sense.ai.header_classification import (
    ClassifiedHeaderField,
    classify_header_fields,
)
from template_sense.ai.table_column_classification import (
    ClassifiedTableColumn,
    classify_table_columns,
)

__all__ = [
    "ClassifiedHeaderField",
    "classify_header_fields",
    "ClassifiedTableColumn",
    "classify_table_columns",
]
