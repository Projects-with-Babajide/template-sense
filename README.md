# Template Sense

AI-powered invoice template extraction library for structured metadata analysis.

Template Sense analyzes Excel-based invoice templates using heuristics and AI to extract structured metadata, supporting multi-language translation and fuzzy matching against canonical field dictionaries.

## Installation

### From PyPI (Recommended)

```bash
# Latest version
pip install template-sense

# Specific version
pip install template-sense==0.1.0
```

### From GitHub

```bash
# Latest release
pip install git+https://github.com/Projects-with-Babajide/template-sense.git@main

# Specific release tag
pip install git+https://github.com/Projects-with-Babajide/template-sense.git@v0.1.0
```

### For Development

```bash
git clone https://github.com/Projects-with-Babajide/template-sense.git
cd template-sense
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .[dev]
```

## Quick Start

```python
from template_sense import TemplateAnalyzer

# Initialize analyzer
analyzer = TemplateAnalyzer(
    ai_provider="openai",  # or "anthropic"
    canonical_fields={
        "invoice_number": ["invoice no", "inv no", "請求書番号"],
        "shipper_name": ["shipper", "sender", "荷送人"],
    }
)

# Analyze template
result = analyzer.analyze("path/to/template.xlsx")

# Access extracted metadata
print(result["header_fields"])
print(result["table_columns"])
```

## Features

- Excel template parsing and analysis
- AI-based field and column classification (OpenAI & Anthropic)
- Multi-language translation support
- Fuzzy matching against canonical field dictionaries
- Structured JSON output

## Documentation

- [Release Process](docs/RELEASE_PROCESS.md) - How to create and publish releases
- [Development Setup](docs/dev-setup.md) - Setting up your development environment
- [Architecture](docs/architecture.md) - System design and module structure

## Requirements

- Python 3.10+
- OpenAI API key (if using OpenAI provider)
- Anthropic API key (if using Anthropic provider)

## License

MIT

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Support

- [Issue Tracker](https://github.com/Projects-with-Babajide/template-sense/issues)
- [GitHub Discussions](https://github.com/Projects-with-Babajide/template-sense/discussions)
