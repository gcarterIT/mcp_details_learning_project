"""Application-level inspection composition for MCP Details."""

from mcp import Client

from mcp_details.connection import (
    build_stdio_server_parameters,
    configured_streamable_http_transport,
)

from mcp_details.inspection import inspect_mcp
from mcp_details.profiles import (
    StdioConnectionProfile,
    StreamableHttpConnectionProfile,
)
from mcp_details.results import (
    ApplicationInspectionResult,
    InspectionTargetSummary,
)

async def _inspect_client(
    client: Client,
    target: InspectionTargetSummary,
) -> ApplicationInspectionResult:
    """Inspect one MCP target through an already-constructed SDK client."""

    async with client:
        inspection = await inspect_mcp(client)

    return ApplicationInspectionResult(
        target=target,
        inspection=inspection,
    )

async def inspect_stdio_profile(
    profile: StdioConnectionProfile,
) -> ApplicationInspectionResult:
    """Inspect one STDIO MCP target through the complete application lifecycle."""

    target = InspectionTargetSummary(
        display_name=profile.display_name,
        transport=profile.transport,
    )

    parameters = build_stdio_server_parameters(profile)
    client = Client(parameters)

    return await _inspect_client(client, target)
    
async def inspect_streamable_http_profile(
    profile: StreamableHttpConnectionProfile,
) -> ApplicationInspectionResult:
    """Inspect one Streamable HTTP MCP target through the complete application lifecycle."""

    target = InspectionTargetSummary(
        display_name=profile.display_name,
        transport=profile.transport,
    )

    if not profile.header_references:
        client = Client(profile.url)
        return await _inspect_client(client, target)

    async with configured_streamable_http_transport(profile) as transport:
        client = Client(transport)
        return await _inspect_client(client, target)