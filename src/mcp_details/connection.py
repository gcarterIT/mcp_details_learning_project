"""MCP SDK connection-target construction for MCP Details."""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from mcp import StdioServerParameters
from mcp.client.streamable_http import (
    create_mcp_http_client,
    streamable_http_client,
)

from mcp_details.profiles import (
    StdioConnectionProfile,
    StreamableHttpConnectionProfile,
)

def build_stdio_server_parameters(
    profile: StdioConnectionProfile,
) -> StdioServerParameters:
    """Translate a project-owned STDIO profile into MCP SDK parameters."""
    resolved_environment: dict[str, str] | None = None

    if profile.environment_variables:
        resolved_environment = {}

        for name in profile.environment_variables:
            value = os.environ.get(name)

            if value is None:
                raise ValueError(
                    f"required environment variable is not set: {name}"
                )

            resolved_environment[name] = value

    return StdioServerParameters(
        command=profile.command,
        args=list(profile.args),
        env=resolved_environment,
        cwd=profile.cwd,
    )
    
@asynccontextmanager
async def configured_streamable_http_transport(
    profile: StreamableHttpConnectionProfile,
) -> AsyncIterator[Any]:
    """Construct a Streamable HTTP transport with resolved runtime headers."""
    resolved_headers: dict[str, str] = {}

    for reference in profile.header_references:
        value = os.environ.get(reference.environment_variable)

        if value is None:
            raise ValueError(
                "required environment variable is not set: "
                f"{reference.environment_variable}"
            )

        resolved_headers[reference.header_name] = value

    async with create_mcp_http_client(
        headers=resolved_headers,
    ) as http_client:
        transport = streamable_http_client(
            profile.url,
            http_client=http_client,
        )

        yield transport