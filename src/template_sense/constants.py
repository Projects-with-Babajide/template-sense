"""
Central configuration constants for the template_sense package.

This module defines all shared configuration values used across the package.
Constants should be imported and used directly - never redefined in other modules.

Usage:
    from template_sense.constants import DEFAULT_CONFIDENCE_THRESHOLD, SUPPORTED_FILE_EXTENSIONS
"""

# ============================================================
# File-related Constants
# ============================================================

SUPPORTED_FILE_EXTENSIONS = (".xlsx", ".xls")  # Canonical source - tuple for immutability

# ============================================================
# Extraction-related Constants
# ============================================================

# Extraction limits
DEFAULT_MAX_HEADER_ROWS = 50  # Maximum rows to scan for headers
DEFAULT_MIN_TABLE_ROWS = 3  # Minimum consecutive rows to qualify as a table

# Confidence thresholds
DEFAULT_CONFIDENCE_THRESHOLD = 0.7  # Heuristic/AI confidence (0.0-1.0)
DEFAULT_AUTO_MAPPING_THRESHOLD = 80.0  # Fuzzy match score for auto-mapping (0.0-100.0)

# Table detection thresholds
DEFAULT_TABLE_MIN_SCORE = 0.5  # Minimum score for table candidate rows (0.0-1.0)
DEFAULT_TABLE_HEADER_MIN_SCORE = 0.6  # Minimum score for table header row detection (0.0-1.0)

# AI timeouts
DEFAULT_AI_TIMEOUT_SECONDS = 30  # Timeout per AI request

# AI payload configuration
DEFAULT_AI_SAMPLE_ROWS = 5  # Number of sample data rows to include in AI payload

# Grid validation
MIN_GRID_ROWS = 1
MIN_GRID_COLUMNS = 1

# ============================================================
# AI Provider Constants
# ============================================================

# AI Provider Configuration
AI_PROVIDER_ENV_VAR = "TEMPLATE_SENSE_AI_PROVIDER"
AI_MODEL_ENV_VAR = "TEMPLATE_SENSE_AI_MODEL"
OPENAI_API_KEY_ENV_VAR = "OPENAI_API_KEY"
ANTHROPIC_API_KEY_ENV_VAR = "ANTHROPIC_API_KEY"
LOG_LEVEL_ENV_VAR = "TEMPLATE_SENSE_LOG_LEVEL"

# Supported providers
SUPPORTED_AI_PROVIDERS = ("openai", "anthropic")

# ============================================================
# Translation Constants
# ============================================================

DEFAULT_TARGET_LANGUAGE = "en"  # Default target language for translation
TRANSLATION_TIMEOUT_SECONDS = 30  # Timeout for translation requests

# ============================================================
# Mapping/Normalization Constants
# ============================================================

# (Reserved for future constants as other modules are implemented)

# ============================================================
# Output Constants
# ============================================================

OUTPUT_SCHEMA_VERSION = "1.0"  # Default version for normalized output schema


__all__ = [
    "SUPPORTED_FILE_EXTENSIONS",
    "DEFAULT_MAX_HEADER_ROWS",
    "DEFAULT_MIN_TABLE_ROWS",
    "DEFAULT_CONFIDENCE_THRESHOLD",
    "DEFAULT_AUTO_MAPPING_THRESHOLD",
    "DEFAULT_TABLE_MIN_SCORE",
    "DEFAULT_TABLE_HEADER_MIN_SCORE",
    "DEFAULT_AI_TIMEOUT_SECONDS",
    "DEFAULT_AI_SAMPLE_ROWS",
    "MIN_GRID_ROWS",
    "MIN_GRID_COLUMNS",
    "AI_PROVIDER_ENV_VAR",
    "AI_MODEL_ENV_VAR",
    "OPENAI_API_KEY_ENV_VAR",
    "ANTHROPIC_API_KEY_ENV_VAR",
    "LOG_LEVEL_ENV_VAR",
    "SUPPORTED_AI_PROVIDERS",
    "DEFAULT_TARGET_LANGUAGE",
    "TRANSLATION_TIMEOUT_SECONDS",
    "OUTPUT_SCHEMA_VERSION",
]
