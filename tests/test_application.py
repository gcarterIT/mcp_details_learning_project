import sys
from pathlib import Path

import pytest
from mcp.types import ServerCapabilities

from mcp_details import application
from mcp_details.profiles import StdioConnectionProfile
from mcp_details.results import (
    CategoryInspection,
    InspectionStatus,
    MCPInspectionResult,
    ServerDescription,
)


def make_inspection_result() -> MCPInspectionResult:
    """Create minimal successful inspection evidence for composition tests."""

    return MCPInspectionResult(
        server_description=ServerDescription(
            protocol_version="2025-06-18",
            server_info=None,
            server_capabilities=ServerCapabilities(),
            instructions=None,
        ),
        tools=CategoryInspection(
            status=InspectionStatus.NOT_ADVERTISED,
            pages=(),
        ),
        resources=CategoryInspection(
            status=InspectionStatus.NOT_ADVERTISED,
            pages=(),
        ),
        resource_templates=CategoryInspection(
            status=InspectionStatus.NOT_ADVERTISED,
            pages=(),
        ),
        prompts=CategoryInspection(
            status=InspectionStatus.NOT_ADVERTISED,
            pages=(),
        ),
    )


@pytest.fixture
def anyio_backend() -> str:
    """Run application async tests with AnyIO's asyncio backend."""
    return "asyncio"

@pytest.mark.anyio
async def test_inspect_stdio_profile_composes_connection_and_inspection(
    monkeypatch,
) -> None:
    profile = StdioConnectionProfile(
        display_name="Example MCP",
        command="example-command",
        args=("--example",),
    )

    inspection_result = make_inspection_result()
    expected_parameters = object()

    events: list[str] = []

    class FakeClient:
        def __init__(self, parameters) -> None:
            assert parameters is expected_parameters
            self.is_connected = False
            events.append("client_created")

        async def __aenter__(self):
            self.is_connected = True
            events.append("client_entered")
            return self

        async def __aexit__(self, exc_type, exc, tb) -> None:
            self.is_connected = False
            events.append("client_exited")

    def fake_build_stdio_server_parameters(received_profile):
        assert received_profile is profile
        events.append("parameters_built")
        return expected_parameters

    async def fake_inspect_mcp(client):
        assert client.is_connected
        events.append("inspection")
        return inspection_result

    monkeypatch.setattr(
        application,
        "build_stdio_server_parameters",
        fake_build_stdio_server_parameters,
    )
    monkeypatch.setattr(
        application,
        "Client",
        FakeClient,
    )
    monkeypatch.setattr(
        application,
        "inspect_mcp",
        fake_inspect_mcp,
    )

    result = await application.inspect_stdio_profile(profile)

    assert events == [
        "parameters_built",
        "client_created",
        "client_entered",
        "inspection",
        "client_exited",
    ]

    assert result.target.display_name == "Example MCP"
    assert result.target.transport == "stdio"
    assert result.inspection is inspection_result
    
@pytest.mark.anyio
async def test_inspect_stdio_profile_exits_client_when_inspection_raises(
    monkeypatch,
) -> None:
    profile = StdioConnectionProfile(
        display_name="Example MCP",
        command="example-command",
    )

    expected_parameters = object()
    expected_failure = RuntimeError("inspection failed")

    events: list[str] = []

    class FakeClient:
        def __init__(self, parameters) -> None:
            assert parameters is expected_parameters
            self.is_connected = False

        async def __aenter__(self):
            self.is_connected = True
            events.append("client_entered")
            return self

        async def __aexit__(self, exc_type, exc, tb) -> None:
            self.is_connected = False
            events.append("client_exited")

    def fake_build_stdio_server_parameters(received_profile):
        assert received_profile is profile
        return expected_parameters

    async def fake_inspect_mcp(client):
        assert client.is_connected
        events.append("inspection")
        raise expected_failure

    monkeypatch.setattr(
        application,
        "build_stdio_server_parameters",
        fake_build_stdio_server_parameters,
    )
    monkeypatch.setattr(
        application,
        "Client",
        FakeClient,
    )
    monkeypatch.setattr(
        application,
        "inspect_mcp",
        fake_inspect_mcp,
    )

    with pytest.raises(RuntimeError) as captured:
        await application.inspect_stdio_profile(profile)

    assert captured.value is expected_failure

    assert events == [
        "client_entered",
        "inspection",
        "client_exited",
    ]
    
@pytest.mark.anyio
async def test_inspect_stdio_profile_with_real_mcp_server() -> None:
    """Inspect a real STDIO MCP server through the application boundary."""

    server_path = (
        Path(__file__).parent
        / "support"
        / "minimal_stdio_server.py"
    ).resolve()

    profile = StdioConnectionProfile(
        display_name="MCP Details Test Server",
        command=sys.executable,
        args=(str(server_path),),
    )

    result = await application.inspect_stdio_profile(profile)

    # Confirm that the application preserves project-owned target identity.
    assert result.target.display_name == "MCP Details Test Server"
    assert result.target.transport == "stdio"

    # Confirm that the real server was connected, negotiated, and inspected.
    description = result.inspection.server_description

    assert description.server_info is not None
    assert description.server_info.name == "mcp-details-test-server"
    assert description.protocol_version is not None
    assert description.server_capabilities is not None