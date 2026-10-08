"""Streamable HTTP MCP server requiring a test header for acceptance tests."""

import sys

import anyio
import uvicorn
from mcp.server.mcpserver import MCPServer
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import PlainTextResponse


REQUIRED_HEADER_NAME = "X-MCP-Details-Test"
REQUIRED_HEADER_VALUE = "expected-test-value"


class RequireTestHeaderMiddleware(BaseHTTPMiddleware):
    """Reject requests that do not contain the required test header."""

    async def dispatch(self, request: Request, call_next):
        if request.headers.get(REQUIRED_HEADER_NAME) != REQUIRED_HEADER_VALUE:
            return PlainTextResponse(
                "Missing or incorrect test header",
                status_code=401,
            )

        return await call_next(request)


async def main(port: int) -> None:
    """Run a Streamable HTTP MCP server requiring a known test header."""
    server = MCPServer(
        name="mcp-details-header-required-http-test-server",
    )

    app = server.streamable_http_app(
        streamable_http_path="/mcp",
        host="127.0.0.1",
    )

    app.add_middleware(RequireTestHeaderMiddleware)

    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=port,
        log_level=server.settings.log_level.lower(),
    )

    uvicorn_server = uvicorn.Server(config)
    await uvicorn_server.serve()


if __name__ == "__main__":
    anyio.run(main, int(sys.argv[1]))