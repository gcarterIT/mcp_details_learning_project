"""Application-level inspection composition for MCP Details."""

from mcp import Client

from mcp_details.connection import build_stdio_server_parameters
from mcp_details.inspection import inspect_mcp
from mcp_details.profiles import StdioConnectionProfile
from mcp_details.results import (
    ApplicationInspectionResult,
    InspectionTargetSummary,
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

    async with client:
        inspection = await inspect_mcp(client)

    return ApplicationInspectionResult(
        target=target,
        inspection=inspection,
    )