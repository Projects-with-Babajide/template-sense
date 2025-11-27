# Integration Tests

This directory contains integration tests that make **real API calls** to external services (OpenAI, Anthropic).

## Running Integration Tests

### Locally (with API keys)
```bash
# Set your API keys
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...

# Run integration tests
pytest tests/integration -v -m integration
```

### Locally (without API keys - tests will skip)
```bash
# Integration tests will be skipped automatically
pytest tests/integration -v -m integration
```

### In CI
Integration tests run automatically when:
- API keys are configured as GitHub repository secrets
- They are marked with `continue-on-error: true` so failures don't break CI

## Test Coverage

### OpenAI Integration (`test_openai_integration.py`)
- ✅ Real `classify_fields()` API call with minimal payload
- ✅ Real `translate_text()` API call (Japanese → English)

### Anthropic Integration (`test_anthropic_integration.py`)
- ✅ Real `classify_fields()` API call with minimal payload
- ✅ Real `translate_text()` API call (Japanese → English)

## Cost Optimization

- Tests use **cheaper models** (gpt-3.5-turbo, claude-haiku)
- Tests use **minimal payloads** (single header candidate)
- Estimated cost: **<$0.01 per test run** (4 API calls total)

## Skipping Integration Tests

```bash
# Run only unit tests (skip integration)
pytest -v -m "not integration"

# This is the default in CI for pull requests
```

## Why Integration Tests?

1. **Catch real issues**: API response format changes, rate limits, authentication
2. **Build confidence**: Proves providers actually work, not just "should work"
3. **Fast feedback**: Detects breaking changes in provider APIs early
4. **Optional**: Tests skip gracefully when keys unavailable (forks still work)
