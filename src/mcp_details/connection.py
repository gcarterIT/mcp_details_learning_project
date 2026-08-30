"""MCP SDK connection-target construction for MCP Details."""

from mcp import StdioServerParameters

from mcp_details.profiles import StdioConnectionProfile


def build_stdio_server_parameters(
    profile: StdioConnectionProfile,
) -> StdioServerParameters:
    """Translate a project-owned STDIO profile into MCP SDK parameters."""
    return StdioServerParameters(
        command=profile.command,
        args=list(profile.args),
        cwd=profile.cwd,
    )