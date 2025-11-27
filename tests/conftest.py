"""
Pytest configuration and fixtures.

This file loads environment variables from .env before running tests.
"""

from dotenv import load_dotenv

# Load .env file at the start of test session
load_dotenv()
