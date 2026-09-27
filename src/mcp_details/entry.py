"""Application-entry composition for MCP Details."""

import asyncio

from pathlib import Path

from mcp_details.application import (
    inspect_stdio_profile,
    inspect_streamable_http_profile,
)
from mcp_details.presentation import render_report
from mcp_details.profiles import (
    StdioConnectionProfile,
    StreamableHttpConnectionProfile,
)

import argparse
from collections.abc import Sequence


async def inspect_and_render_streamable_http(
    display_name: str,
    url: str,
) -> str:
    """Inspect a Streamable HTTP MCP target and render its report."""

    profile = StreamableHttpConnectionProfile(
        display_name=display_name,
        url=url,
    )

    result = await inspect_streamable_http_profile(profile)

    return render_report(result)


async def inspect_and_render_stdio(
    display_name: str,
    command: str,
    args: tuple[str, ...] = (),
    cwd: Path | None = None,
) -> str:
    """Inspect a STDIO MCP target and render its report."""

    profile = StdioConnectionProfile(
        display_name=display_name,
        command=command,
        args=args,
        cwd=cwd,
    )

    result = await inspect_stdio_profile(profile)

    return render_report(result)
    
def _parse_arguments(argv: Sequence[str]) -> argparse.Namespace:
    """Parse MCP Details command-line arguments."""

    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(
        dest="transport",
        required=True,
    )

    http_parser = subparsers.add_parser("streamable-http")

    http_parser.add_argument(
        "--name",
        required=True,
    )

    http_parser.add_argument(
        "--url",
        required=True,
    )

    stdio_parser = subparsers.add_parser("stdio")

    stdio_parser.add_argument(
        "--name",
        required=True,
    )

    stdio_parser.add_argument(
        "--command",
        required=True,
    )

    stdio_parser.add_argument(
        "--cwd",
    )

    stdio_parser.add_argument(
        "server_args",
        nargs="*",
    )

    return parser.parse_args(argv)
    
async def _run_parsed_arguments(
    parsed: argparse.Namespace,
) -> str:
    """Run the entry operation selected by parsed command-line arguments."""

    if parsed.transport == "streamable-http":
        return await inspect_and_render_streamable_http(
            display_name=parsed.name,
            url=parsed.url,
        )

    if parsed.transport == "stdio":
        cwd = Path(parsed.cwd) if parsed.cwd is not None else None

        return await inspect_and_render_stdio(
            display_name=parsed.name,
            command=parsed.command,
            args=tuple(parsed.server_args),
            cwd=cwd,
        )

    raise ValueError(f"unsupported transport: {parsed.transport}")
    
def run(argv: Sequence[str]) -> str:
    """Run MCP Details synchronously for explicit command-line arguments."""

    parsed = _parse_arguments(argv)

    return asyncio.run(
        _run_parsed_arguments(parsed)
    )
    
def main(argv: Sequence[str]) -> None:
    """Run MCP Details and write the successful report to stdout."""

    report = run(argv)

    print(report)