"""Application-entry composition for MCP Details."""

import asyncio

from pathlib import Path

from mcp_details.application import (
    inspect_stdio_profile,
    inspect_streamable_http_profile,
)
from mcp_details.presentation import render_report

from mcp_details.profiles import (
    HttpHeaderEnvironmentReference,
    StdioConnectionProfile,
    StreamableHttpConnectionProfile,
)

import argparse
from collections.abc import Sequence


async def inspect_and_render_streamable_http(
    display_name: str,
    url: str,
    header_references: tuple[HttpHeaderEnvironmentReference, ...] = (),
) -> str:
    profile = StreamableHttpConnectionProfile(
        display_name=display_name,
        url=url,
        header_references=header_references,
    )
    result = await inspect_streamable_http_profile(profile)
    return render_report(result)


async def inspect_and_render_stdio(
    display_name: str,
    command: str,
    args: tuple[str, ...] = (),
    cwd: Path | None = None,
    environment_variables: tuple[str, ...] = (),
) -> str:
    """Inspect a STDIO MCP target and render its report."""

    profile = StdioConnectionProfile(
        display_name=display_name,
        command=command,
        args=args,
        cwd=cwd,
        environment_variables=environment_variables,
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

    http_parser.add_argument(
        "--header-env",
        dest="header_environment_references",
        action="append",
        nargs=2,
        metavar=("HEADER", "ENV_VAR"),
        default=[],
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
        "--env",
        dest="environment_variables",
        action="append",
        default=[],
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
        header_references = tuple(
            HttpHeaderEnvironmentReference(
                header_name=header_name,
                environment_variable=environment_variable,
            )
            for header_name, environment_variable
            in parsed.header_environment_references
        )

        return await inspect_and_render_streamable_http(
            display_name=parsed.name,
            url=parsed.url,
            header_references=header_references,
        )

    if parsed.transport == "stdio":
        cwd = Path(parsed.cwd) if parsed.cwd is not None else None

        return await inspect_and_render_stdio(
            display_name=parsed.name,
            command=parsed.command,
            args=tuple(parsed.server_args),
            cwd=cwd,
            environment_variables=tuple(parsed.environment_variables),
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