"""
Integration tests for Template Sense.

These tests make real API calls to external services and are optional.
They only run when the required API keys are available as environment variables.

To run integration tests locally:
    export OPENAI_API_KEY=sk-...
    export ANTHROPIC_API_KEY=sk-ant-...
    pytest tests/integration -v -m integration

To skip integration tests:
    pytest -v -m "not integration"
"""
