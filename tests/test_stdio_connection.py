"""Integration tests for a real MCP STDIO connection."""

import sys
from pathlib import Path

import pytest
from mcp import Client

from mcp_details.connection import build_stdio_server_parameters
from mcp_details.inspection import inspect_server_description
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
        # First, confirm the real MCP connection and negotiation succeeded.
        assert client.server_info is not None
        assert client.server_info.name == "mcp-details-test-server"
        assert client.protocol_version is not None
        assert client.server_capabilities is not None

        # Then pass the already-connected Client into the new
        # transport-neutral inspection boundary.
        description = inspect_server_description(client)

        # Confirm that inspection preserves the negotiated server evidence.
        assert description.server_info is client.server_info
        assert description.server_info.name == "mcp-details-test-server"
        assert description.protocol_version == client.protocol_version
        assert description.server_capabilities is client.server_capabilities
        assert description.instructions == client.instructions

