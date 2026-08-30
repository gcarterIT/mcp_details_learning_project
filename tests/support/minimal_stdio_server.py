"""Minimal STDIO MCP server used only by integration tests."""

import anyio

from mcp.server.lowlevel.server import Server
from mcp.server.stdio import stdio_server


async def main() -> None:
    """Run a minimal MCP server over STDIO."""
    server: Server[dict[str, object]] = Server(
        "mcp-details-test-server"
    )

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    anyio.run(main)