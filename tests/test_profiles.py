"""Tests for MCP Details connection profile models."""

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from mcp_details.profiles import (
    HttpHeaderEnvironmentReference,
    StdioConnectionProfile,
    StreamableHttpConnectionProfile,
)

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

def test_stdio_profile_preserves_configured_environment_variables() -> None:
    profile = StdioConnectionProfile(
        display_name="Demo MCP",
        command="python",
        environment_variables=(
            "WEATHER_API_KEY",
            "WEATHER_REGION",
        ),
    )

    assert profile.environment_variables == (
        "WEATHER_API_KEY",
        "WEATHER_REGION",
    )


def test_stdio_profile_defaults_environment_variables_to_empty_tuple() -> None:
    profile = StdioConnectionProfile(
        display_name="Demo MCP",
        command="python",
    )

    assert profile.environment_variables == ()
    
@pytest.mark.parametrize("environment_variable", ["", "   "])
def test_stdio_profile_rejects_blank_environment_variable_name(
    environment_variable: str,
) -> None:
    with pytest.raises(ValueError):
        StdioConnectionProfile(
            display_name="Demo MCP",
            command="python",
            environment_variables=(environment_variable,),
        )    

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
        
def test_streamable_http_profile_can_be_created_with_minimal_configuration() -> None:
    profile = StreamableHttpConnectionProfile(
        display_name="Remote Demo MCP",
        url="http://localhost:8000/mcp",
    )

    assert profile.display_name == "Remote Demo MCP"
    assert profile.url == "http://localhost:8000/mcp"


def test_streamable_http_profile_has_fixed_streamable_http_transport() -> None:
    profile = StreamableHttpConnectionProfile(
        display_name="Remote Demo MCP",
        url="http://localhost:8000/mcp",
    )

    assert profile.transport == "streamable_http"


@pytest.mark.parametrize("display_name", ["", "   "])
def test_streamable_http_profile_rejects_blank_display_name(
    display_name: str,
) -> None:
    with pytest.raises(ValueError):
        StreamableHttpConnectionProfile(
            display_name=display_name,
            url="http://localhost:8000/mcp",
        )


@pytest.mark.parametrize("url", ["", "   "])
def test_streamable_http_profile_rejects_blank_url(url: str) -> None:
    with pytest.raises(ValueError):
        StreamableHttpConnectionProfile(
            display_name="Remote Demo MCP",
            url=url,
        )


def test_streamable_http_profile_is_immutable() -> None:
    profile = StreamableHttpConnectionProfile(
        display_name="Remote Demo MCP",
        url="http://localhost:8000/mcp",
    )

    with pytest.raises(FrozenInstanceError):
        profile.url = "http://localhost:9000/mcp"  # type: ignore[misc]
        
def test_http_header_environment_reference_preserves_names() -> None:
    reference = HttpHeaderEnvironmentReference(
        header_name="Authorization",
        environment_variable="MCP_AUTHORIZATION",
    )

    assert reference.header_name == "Authorization"
    assert reference.environment_variable == "MCP_AUTHORIZATION"


@pytest.mark.parametrize("header_name", ["", "   "])
def test_http_header_environment_reference_rejects_blank_header_name(
    header_name: str,
) -> None:
    with pytest.raises(ValueError):
        HttpHeaderEnvironmentReference(
            header_name=header_name,
            environment_variable="MCP_AUTHORIZATION",
        )


@pytest.mark.parametrize("environment_variable", ["", "   "])
def test_http_header_environment_reference_rejects_blank_environment_variable(
    environment_variable: str,
) -> None:
    with pytest.raises(ValueError):
        HttpHeaderEnvironmentReference(
            header_name="Authorization",
            environment_variable=environment_variable,
        )


def test_streamable_http_profile_preserves_header_references() -> None:
    reference = HttpHeaderEnvironmentReference(
        header_name="Authorization",
        environment_variable="MCP_AUTHORIZATION",
    )

    profile = StreamableHttpConnectionProfile(
        display_name="Authenticated Demo MCP",
        url="https://example.com/mcp",
        header_references=(reference,),
    )

    assert profile.header_references == (reference,)
    
def test_streamable_http_profile_defaults_header_references_to_empty_tuple() -> None:
    profile = StreamableHttpConnectionProfile(
        display_name="Remote Demo MCP",
        url="http://localhost:8000/mcp",
    )

    assert profile.header_references == ()    