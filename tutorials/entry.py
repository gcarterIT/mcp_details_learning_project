import asyncio

from application import inspect_profile
from presentation import render_report


async def _run_async(server_name: str) -> str:
    """Perform the asynchronous application operation."""

    result = await inspect_profile(server_name)

    return render_report(result)


def run(server_name: str) -> str:
    """Bridge synchronous execution into async execution."""

    return asyncio.run(_run_async(server_name))


def main() -> None:
    """Synchronous terminal-facing application entry."""

    report = run("Demo MCP Server")

    print(report)