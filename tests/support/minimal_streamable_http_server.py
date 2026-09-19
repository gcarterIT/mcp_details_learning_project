"""Minimal Streamable HTTP MCP server used only by integration tests."""

import sys

import anyio

from mcp.server.mcpserver import MCPServer


async def main(port: int) -> None:
    """Run a minimal MCP server over Streamable HTTP."""
    server = MCPServer(
        name="mcp-details-http-test-server",
    )

    await server.run_streamable_http_async(
        host="127.0.0.1",
        port=port,
        streamable_http_path="/mcp",
    )


if __name__ == "__main__":
    anyio.run(main, int(sys.argv[1]))