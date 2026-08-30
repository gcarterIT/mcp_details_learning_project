"""Integration tests for a real MCP STDIO connection."""

import sys
from pathlib import Path

import pytest
from mcp import Client

from mcp_details.connection import build_stdio_server_parameters
from mcp_details.profiles import StdioConnectionProfile


@pytest.fixture
def anyio_backend() -> str:
    """Run this integration test only with AnyIO's asyncio backend."""
    return "asyncio"


@pytest.mark.anyio
async def test_stdio_profile_can_connect_to_real_mcp_server() -> None:
    server_path = (
        Path(__file__).parent
        / "support"
        / "minimal_stdio_server.py"
    ).resolve()

    profile = StdioConnectionProfile(
        display_name="MCP Details Test Server",
        command=sys.executable,
        args=(str(server_path),),
    )

    parameters = build_stdio_server_parameters(profile)

    async with Client(parameters) as client:
        assert client.server_info is not None
        assert client.server_info.name == "mcp-details-test-server"
        assert client.protocol_version is not None
        assert client.server_capabilities is not None