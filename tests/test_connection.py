"""Tests for MCP Details connection-target construction."""

from pathlib import Path

from mcp import StdioServerParameters

from mcp_details.connection import build_stdio_server_parameters
from mcp_details.profiles import StdioConnectionProfile


def test_build_stdio_server_parameters_returns_sdk_parameters() -> None:
    profile = StdioConnectionProfile(
        display_name="Demo MCP",
        command="python",
    )

    parameters = build_stdio_server_parameters(profile)

    assert isinstance(parameters, StdioServerParameters)


def test_build_stdio_server_parameters_translates_minimal_profile() -> None:
    profile = StdioConnectionProfile(
        display_name="Demo MCP",
        command="python",
    )

    parameters = build_stdio_server_parameters(profile)

    assert parameters.command == "python"
    assert parameters.args == []
    assert parameters.cwd is None


def test_build_stdio_server_parameters_translates_arguments() -> None:
    profile = StdioConnectionProfile(
        display_name="Demo MCP",
        command="python",
        args=("server.py", "--verbose"),
    )

    parameters = build_stdio_server_parameters(profile)

    assert parameters.args == ["server.py", "--verbose"]


def test_build_stdio_server_parameters_preserves_cwd() -> None:
    cwd = Path(r"C:\AI_Projects\demo_server")

    profile = StdioConnectionProfile(
        display_name="Demo MCP",
        command="python",
        cwd=cwd,
    )

    parameters = build_stdio_server_parameters(profile)

    assert parameters.cwd == cwd