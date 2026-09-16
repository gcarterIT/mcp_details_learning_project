"""Run the MCP Details application against the presentation demo server."""

import sys
from pathlib import Path

import anyio

from mcp_details.application import inspect_stdio_profile
from mcp_details.presentation import render_report
from mcp_details.profiles import StdioConnectionProfile


async def main() -> None:
    """Inspect the demo STDIO server and print the resulting report."""
    server_path = (
        Path(__file__).parent
        / "presentation_demo_stdio_server.py"
    ).resolve()

    profile = StdioConnectionProfile(
        display_name="Presentation Demo Server",
        command=sys.executable,
        args=(str(server_path),),
    )

    result = await inspect_stdio_profile(profile)
 
    report = render_report(result)

    print(report)


if __name__ == "__main__":
    anyio.run(main)