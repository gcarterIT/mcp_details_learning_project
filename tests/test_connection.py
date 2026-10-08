"""Tests for MCP Details connection-target construction."""
import pytest

from pathlib import Path

from mcp import StdioServerParameters

from mcp_details import connection
from mcp_details.connection import build_stdio_server_parameters
from mcp_details.profiles import (
    HttpHeaderEnvironmentReference,
    StdioConnectionProfile,
    StreamableHttpConnectionProfile,
)

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
    
def test_build_stdio_server_parameters_leaves_env_unset_without_references() -> None:
    profile = StdioConnectionProfile(
        display_name="Demo MCP",
        command="python",
    )

    parameters = build_stdio_server_parameters(profile)

    assert parameters.env is None    
    
def test_build_stdio_server_parameters_resolves_environment_variables(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MCP_DETAILS_TEST_API_KEY", "test-secret-value")

    profile = StdioConnectionProfile(
        display_name="Demo MCP",
        command="python",
        environment_variables=("MCP_DETAILS_TEST_API_KEY",),
    )

    parameters = build_stdio_server_parameters(profile)

    assert parameters.env == {
        "MCP_DETAILS_TEST_API_KEY": "test-secret-value",
    }    
    
def test_build_stdio_server_parameters_rejects_missing_environment_variable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("MCP_DETAILS_MISSING_TEST_VARIABLE", raising=False)

    profile = StdioConnectionProfile(
        display_name="Demo MCP",
        command="python",
        environment_variables=("MCP_DETAILS_MISSING_TEST_VARIABLE",),
    )

    with pytest.raises(ValueError):
        build_stdio_server_parameters(profile)
        
@pytest.mark.anyio
async def test_configured_streamable_http_transport_resolves_header_references(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "MCP_DETAILS_TEST_AUTHORIZATION",
        "Bearer test-secret-value",
    )

    profile = StreamableHttpConnectionProfile(
        display_name="Authenticated Demo MCP",
        url="https://example.com/mcp",
        header_references=(
            HttpHeaderEnvironmentReference(
                header_name="Authorization",
                environment_variable="MCP_DETAILS_TEST_AUTHORIZATION",
            ),
        ),
    )

    captured_headers: dict[str, str] | None = None

    class FakeHttpClient:
        async def __aenter__(self) -> "FakeHttpClient":
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
            return None

    def fake_create_mcp_http_client(
        headers: dict[str, str] | None = None,
    ) -> FakeHttpClient:
        nonlocal captured_headers
        captured_headers = headers
        return FakeHttpClient()

    expected_transport = object()

    def fake_streamable_http_client(
        url: str,
        *,
        http_client: FakeHttpClient,
    ) -> object:
        assert url == "https://example.com/mcp"
        return expected_transport

    monkeypatch.setattr(
        connection,
        "create_mcp_http_client",
        fake_create_mcp_http_client,
    )
    monkeypatch.setattr(
        connection,
        "streamable_http_client",
        fake_streamable_http_client,
    )

    async with connection.configured_streamable_http_transport(profile) as transport:
        assert transport is expected_transport

    assert captured_headers == {
        "Authorization": "Bearer test-secret-value",
    }
    
@pytest.mark.anyio
async def test_configured_streamable_http_transport_rejects_missing_environment_variable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(
        "MCP_DETAILS_MISSING_HTTP_AUTHORIZATION",
        raising=False,
    )

    profile = StreamableHttpConnectionProfile(
        display_name="Authenticated Demo MCP",
        url="https://example.com/mcp",
        header_references=(
            HttpHeaderEnvironmentReference(
                header_name="Authorization",
                environment_variable="MCP_DETAILS_MISSING_HTTP_AUTHORIZATION",
            ),
        ),
    )

    with pytest.raises(ValueError):
        async with connection.configured_streamable_http_transport(profile):
            pass
            
@pytest.mark.anyio
async def test_configured_streamable_http_transport_closes_http_client_after_use(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "MCP_DETAILS_TEST_AUTHORIZATION",
        "Bearer test-secret-value",
    )

    profile = StreamableHttpConnectionProfile(
        display_name="Authenticated Demo MCP",
        url="https://example.com/mcp",
        header_references=(
            HttpHeaderEnvironmentReference(
                header_name="Authorization",
                environment_variable="MCP_DETAILS_TEST_AUTHORIZATION",
            ),
        ),
    )

    lifecycle_events: list[str] = []

    class FakeHttpClient:
        async def __aenter__(self) -> "FakeHttpClient":
            lifecycle_events.append("http_client_entered")
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
            lifecycle_events.append("http_client_exited")

    def fake_create_mcp_http_client(
        headers: dict[str, str] | None = None,
    ) -> FakeHttpClient:
        return FakeHttpClient()

    expected_transport = object()

    def fake_streamable_http_client(
        url: str,
        *,
        http_client: FakeHttpClient,
    ) -> object:
        return expected_transport

    monkeypatch.setattr(
        connection,
        "create_mcp_http_client",
        fake_create_mcp_http_client,
    )
    monkeypatch.setattr(
        connection,
        "streamable_http_client",
        fake_streamable_http_client,
    )

    async with connection.configured_streamable_http_transport(profile) as transport:
        assert transport is expected_transport
        assert lifecycle_events == ["http_client_entered"]

    assert lifecycle_events == [
        "http_client_entered",
        "http_client_exited",
    ]            