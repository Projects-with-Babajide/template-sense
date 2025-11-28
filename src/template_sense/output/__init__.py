"""
Output layer for Template Sense.

This module provides canonical data structures and aggregation functionality
for merging all pipeline outputs into a unified template representation.
"""

from template_sense.output.canonical_aggregator import (
    CanonicalHeaderField,
    CanonicalLineItem,
    CanonicalTable,
    CanonicalTableColumn,
    CanonicalTemplate,
    build_canonical_template,
)

__all__ = [
    "CanonicalHeaderField",
    "CanonicalTableColumn",
    "CanonicalLineItem",
    "CanonicalTable",
    "CanonicalTemplate",
    "build_canonical_template",
]
