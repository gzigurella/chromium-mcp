"""Pytest configuration for chromium-mcp tests."""

import asyncio
import pytest


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_server():
    """Create a mock MCP server for testing."""
    from mcp.server import Server

    server = Server("test-server")
    return server
