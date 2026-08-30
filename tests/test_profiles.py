"""Tests for MCP Details connection profile models."""

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from mcp_details.profiles import StdioConnectionProfile


def test_stdio_profile_can_be_created_with_minimal_configuration() -> None:
    profile = StdioConnectionProfile(
        display_name="Demo MCP",
        command="python",
    )

    assert profile.display_name == "Demo MCP"
    assert profile.command == "python"


def test_stdio_profile_has_fixed_stdio_transport() -> None:
    profile = StdioConnectionProfile(
        display_name="Demo MCP",
        command="python",
    )

    assert profile.transport == "stdio"


def test_stdio_profile_preserves_configured_arguments_and_cwd() -> None:
    cwd = Path(r"C:\AI_Projects\demo_server")

    profile = StdioConnectionProfile(
        display_name="Demo MCP",
        command="python",
        args=("server.py", "--verbose"),
        cwd=cwd,
    )

    assert profile.args == ("server.py", "--verbose")
    assert profile.cwd == cwd


def test_stdio_profile_defaults_args_to_empty_tuple_and_cwd_to_none() -> None:
    profile = StdioConnectionProfile(
        display_name="Demo MCP",
        command="python",
    )

    assert profile.args == ()
    assert profile.cwd is None


@pytest.mark.parametrize("display_name", ["", "   "])
def test_stdio_profile_rejects_blank_display_name(display_name: str) -> None:
    with pytest.raises(ValueError):
        StdioConnectionProfile(
            display_name=display_name,
            command="python",
        )


@pytest.mark.parametrize("command", ["", "   "])
def test_stdio_profile_rejects_blank_command(command: str) -> None:
    with pytest.raises(ValueError):
        StdioConnectionProfile(
            display_name="Demo MCP",
            command=command,
        )


def test_stdio_profile_is_immutable() -> None:
    profile = StdioConnectionProfile(
        display_name="Demo MCP",
        command="python",
    )

    with pytest.raises(FrozenInstanceError):
        profile.command = "npx"  # type: ignore[misc]