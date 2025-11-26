# Template-Sense Architecture

This document describes the folder structure and module organization for the template-sense Python package.

## Project Structure

```
template-sense/
├── AGENTS.md
├── claude.md
├── src/
│   └── template_sense/
│       ├── __init__.py
│       ├── adapters/
│       │   └── __init__.py
│       ├── ai_providers/
│       │   └── __init__.py
│       ├── ai/
│       │   └── __init__.py
│       ├── extraction/
│       │   └── __init__.py
│       ├── translation/
│       │   └── __init__.py
│       ├── mapping/
│       │   └── __init__.py
│       └── output/
│           └── __init__.py
├── tests/
│   ├── __init__.py
│   └── test_placeholder.py
└── docs/
    └── architecture.md
```

## Module Descriptions

### adapters/

Converts external file formats into normalized grid representations. This module handles the ingestion of various document formats and transforms them into a consistent internal structure that can be processed by downstream modules.

### extraction/

Applies heuristics to identify candidate header/table regions. This module analyzes the normalized grid data to detect potential headers, table boundaries, and structural elements within documents.

### ai_providers/

Provides provider-agnostic interface to external AI models. This module abstracts the communication with various AI services, allowing the system to work with different providers without changing the core logic.

### ai/

Calls AI providers to semantically classify headers and table columns. This module leverages the ai_providers interface to perform intelligent classification of document elements based on their semantic meaning.

### translation/

Translates non-English labels using dictionaries. This module handles internationalization by converting labels from various languages into a standardized form for consistent processing.

### mapping/

Fuzzy matches translated labels to canonical field keys and aggregates extracted data. This module performs the critical task of mapping extracted and translated labels to a predefined schema, handling variations and inconsistencies in naming.

### output/

Builds the final normalized JSON output and tracks recovery events. This module assembles the processed data into the final output format and maintains a record of any data recovery or correction events that occurred during processing.

## Additional Documentation

For detailed architecture information, design decisions, and implementation guidelines, refer to `claude.md` in the repository root.
