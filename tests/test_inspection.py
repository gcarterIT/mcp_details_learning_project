"""Tests for the MCP Details inspection boundary."""

from types import SimpleNamespace

from mcp.types import (
    ListResourceTemplatesResult,
    ListResourcesResult,
    ListToolsResult,
    ListPromptsResult,
    ResourcesCapability,
    ServerCapabilities,
    ToolsCapability,
    PromptsCapability,
    Implementation,
)

from mcp_details.inspection import (
    InspectionCategory,
    inspect_resource_templates,
    inspect_resources,
    inspect_server_description,
    inspect_tools,
    inspect_prompts,
    is_category_advertised,
)

from mcp_details.results import InspectionStatus

from mcp.types import (
    PromptsCapability,
    ResourcesCapability,
    ToolsCapability,
)

from unittest.mock import AsyncMock, call

import pytest
from mcp.types import ListToolsResult, ListResourcesResult

@pytest.fixture
def anyio_backend() -> str:
    """Run async inspection tests only with AnyIO's asyncio backend."""
    return "asyncio"


def test_inspect_server_description_preserves_client_metadata() -> None:
    """Server description preserves negotiated metadata from the Client."""

    server_info = Implementation(
        name="test-server",
        version="1.0.0",
    )

    server_capabilities = ServerCapabilities()

    client = SimpleNamespace(
        protocol_version="2025-11-25",
        server_info=server_info,
        server_capabilities=server_capabilities,
        instructions="Test server instructions.",
    )

    result = inspect_server_description(client)

    assert result.protocol_version == "2025-11-25"
    assert result.server_info is server_info
    assert result.server_capabilities is server_capabilities
    assert result.instructions == "Test server instructions."
    
def test_inspect_server_description_preserves_missing_server_info() -> None:
    """Missing server-reported identity remains absent."""

    server_capabilities = ServerCapabilities()

    client = SimpleNamespace(
        protocol_version="2025-11-25",
        server_info=None,
        server_capabilities=server_capabilities,
        instructions=None,
    )

    result = inspect_server_description(client)

    assert result.server_info is None
    assert result.instructions is None
    
def test_tools_category_is_advertised_when_tools_capability_is_present() -> None:
    capabilities = ServerCapabilities(
        tools=ToolsCapability(),
    )

    assert is_category_advertised(
        capabilities,
        InspectionCategory.TOOLS,
    )


def test_tools_category_is_not_advertised_when_tools_capability_is_absent() -> None:
    capabilities = ServerCapabilities()

    assert not is_category_advertised(
        capabilities,
        InspectionCategory.TOOLS,
    )


def test_resources_and_resource_templates_share_resources_capability() -> None:
    capabilities = ServerCapabilities(
        resources=ResourcesCapability(),
    )

    assert is_category_advertised(
        capabilities,
        InspectionCategory.RESOURCES,
    )
    assert is_category_advertised(
        capabilities,
        InspectionCategory.RESOURCE_TEMPLATES,
    )


def test_resources_and_resource_templates_are_not_advertised_without_resources_capability() -> None:
    capabilities = ServerCapabilities()

    assert not is_category_advertised(
        capabilities,
        InspectionCategory.RESOURCES,
    )
    assert not is_category_advertised(
        capabilities,
        InspectionCategory.RESOURCE_TEMPLATES,
    )

def test_prompts_category_follows_prompts_capability() -> None:
    advertised_capabilities = ServerCapabilities(
        prompts=PromptsCapability(),
    )
    unadvertised_capabilities = ServerCapabilities()

    assert is_category_advertised(
        advertised_capabilities,
        InspectionCategory.PROMPTS,
    )
    assert not is_category_advertised(
        unadvertised_capabilities,
        InspectionCategory.PROMPTS,
    )


@pytest.mark.anyio
async def test_inspect_tools_returns_success_for_single_complete_page() -> None:
    """A first page without a continuation cursor completes tools inspection."""

    page = ListToolsResult(
        tools=[],
        next_cursor=None,
    )

    client = SimpleNamespace(
        server_capabilities=ServerCapabilities(
            tools=ToolsCapability(),
        ),
        list_tools=AsyncMock(return_value=page),
    )

    result = await inspect_tools(client)

    assert result.status is InspectionStatus.SUCCESS
    assert result.pages == (page,)
    assert result.pages[0] is page
    assert result.failure is None

    client.list_tools.assert_awaited_once_with()



@pytest.mark.anyio
async def test_inspect_tools_follows_cursors_until_complete() -> None:
    """Tools inspection follows every continuation cursor until complete."""

    first_page = ListToolsResult(
        tools=[],
        next_cursor="cursor-2",
    )

    second_page = ListToolsResult(
        tools=[],
        next_cursor="cursor-3",
    )

    third_page = ListToolsResult(
        tools=[],
        next_cursor=None,
    )

    client = SimpleNamespace(
        server_capabilities=ServerCapabilities(
            tools=ToolsCapability(),
        ),
        list_tools=AsyncMock(
            side_effect=[
                first_page,
                second_page,
                third_page,
            ]
        ),
    )

    result = await inspect_tools(client)

    assert result.status is InspectionStatus.SUCCESS

    assert result.pages == (
        first_page,
        second_page,
        third_page,
    )

    assert result.pages[0] is first_page
    assert result.pages[1] is second_page
    assert result.pages[2] is third_page

    assert result.failure is None

    assert client.list_tools.await_args_list == [
        call(),
        call(cursor="cursor-2"),
        call(cursor="cursor-3"),
    ]


@pytest.mark.anyio
async def test_inspect_tools_skips_unadvertised_tools() -> None:
    """Tools inspection must not probe an unadvertised category."""

    client = SimpleNamespace(
        server_capabilities=ServerCapabilities(),
        list_tools=AsyncMock(),
    )

    result = await inspect_tools(client)

    assert result.status is InspectionStatus.NOT_ADVERTISED
    assert result.pages == ()
    assert result.failure is None

    client.list_tools.assert_not_awaited()


@pytest.mark.anyio
async def test_inspect_tools_preserves_pages_when_later_page_fails() -> None:
    """Successful pages are preserved when later tools pagination fails."""

    first_page = ListToolsResult(
        tools=[],
        next_cursor="cursor-2",
    )

    second_page = ListToolsResult(
        tools=[],
        next_cursor="cursor-3",
    )

    failure = RuntimeError("third tools page failed")

    client = SimpleNamespace(
        server_capabilities=ServerCapabilities(
            tools=ToolsCapability(),
        ),
        list_tools=AsyncMock(
            side_effect=[
                first_page,
                second_page,
                failure,
            ]
        ),
    )

    result = await inspect_tools(client)

    assert result.status is InspectionStatus.PARTIAL

    assert result.pages == (
        first_page,
        second_page,
    )

    assert result.pages[0] is first_page
    assert result.pages[1] is second_page

    assert result.failure is failure

    assert client.list_tools.await_args_list == [
        call(),
        call(cursor="cursor-2"),
        call(cursor="cursor-3"),
    ]


@pytest.mark.anyio
async def test_inspect_tools_reports_failed_when_first_page_fails() -> None:
    """Advertised tools inspection is FAILED when no page can be obtained."""

    failure = RuntimeError("first tools page failed")

    client = SimpleNamespace(
        server_capabilities=ServerCapabilities(
            tools=ToolsCapability(),
        ),
        list_tools=AsyncMock(
            side_effect=failure,
        ),
    )

    result = await inspect_tools(client)

    assert result.status is InspectionStatus.FAILED
    assert result.pages == ()
    assert result.failure is failure

    client.list_tools.assert_awaited_once_with()


@pytest.mark.anyio
async def test_inspect_resources_returns_success_for_single_complete_page() -> None:
    """A complete first resources page produces successful inspection."""

    page = ListResourcesResult(
        resources=[],
        next_cursor=None,
    )

    client = SimpleNamespace(
        server_capabilities=ServerCapabilities(
            resources=ResourcesCapability(),
        ),
        list_resources=AsyncMock(return_value=page),
    )

    result = await inspect_resources(client)

    assert result.status is InspectionStatus.SUCCESS
    assert result.pages == (page,)
    assert result.pages[0] is page
    assert result.failure is None

    client.list_resources.assert_awaited_once_with()

@pytest.mark.anyio
async def test_inspect_resources_follows_cursors_until_complete() -> None:
    """Resources inspection follows every continuation cursor until complete."""

    first_page = ListResourcesResult(
        resources=[],
        next_cursor="cursor-2",
    )

    second_page = ListResourcesResult(
        resources=[],
        next_cursor="cursor-3",
    )

    third_page = ListResourcesResult(
        resources=[],
        next_cursor=None,
    )

    client = SimpleNamespace(
        server_capabilities=ServerCapabilities(
            resources=ResourcesCapability(),
        ),
        list_resources=AsyncMock(
            side_effect=[
                first_page,
                second_page,
                third_page,
            ]
        ),
    )

    result = await inspect_resources(client)

    assert result.status is InspectionStatus.SUCCESS

    assert result.pages == (
        first_page,
        second_page,
        third_page,
    )

    assert result.pages[0] is first_page
    assert result.pages[1] is second_page
    assert result.pages[2] is third_page

    assert result.failure is None

    assert client.list_resources.await_args_list == [
        call(),
        call(cursor="cursor-2"),
        call(cursor="cursor-3"),
    ]

@pytest.mark.anyio
async def test_inspect_resources_skips_unadvertised_resources() -> None:
    """Resources inspection must not probe an unadvertised category."""

    client = SimpleNamespace(
        server_capabilities=ServerCapabilities(),
        list_resources=AsyncMock(),
    )

    result = await inspect_resources(client)

    assert result.status is InspectionStatus.NOT_ADVERTISED
    assert result.pages == ()
    assert result.failure is None

    client.list_resources.assert_not_awaited()

@pytest.mark.anyio
async def test_inspect_resources_preserves_pages_when_later_page_fails() -> None:
    """Successful resource pages survive a later pagination failure."""

    first_page = ListResourcesResult(
        resources=[],
        next_cursor="cursor-2",
    )

    second_page = ListResourcesResult(
        resources=[],
        next_cursor="cursor-3",
    )

    failure = RuntimeError("third resources page failed")

    client = SimpleNamespace(
        server_capabilities=ServerCapabilities(
            resources=ResourcesCapability(),
        ),
        list_resources=AsyncMock(
            side_effect=[
                first_page,
                second_page,
                failure,
            ]
        ),
    )

    result = await inspect_resources(client)

    assert result.status is InspectionStatus.PARTIAL

    assert result.pages == (
        first_page,
        second_page,
    )

    assert result.pages[0] is first_page
    assert result.pages[1] is second_page

    assert result.failure is failure

    assert client.list_resources.await_args_list == [
        call(),
        call(cursor="cursor-2"),
        call(cursor="cursor-3"),
    ]

@pytest.mark.anyio
async def test_inspect_resources_reports_failed_when_first_page_fails() -> None:
    """Advertised resources inspection is FAILED when no page can be obtained."""

    failure = RuntimeError("first resources page failed")

    client = SimpleNamespace(
        server_capabilities=ServerCapabilities(
            resources=ResourcesCapability(),
        ),
        list_resources=AsyncMock(
            side_effect=failure,
        ),
    )

    result = await inspect_resources(client)

    assert result.status is InspectionStatus.FAILED
    assert result.pages == ()
    assert result.failure is failure

    client.list_resources.assert_awaited_once_with()

@pytest.mark.anyio
async def test_inspect_resource_templates_returns_success_for_single_complete_page() -> None:
    """A complete empty template page is still successful inspection."""

    page = ListResourceTemplatesResult(
        resource_templates=[],
        next_cursor=None,
    )

    client = SimpleNamespace(
        server_capabilities=ServerCapabilities(
            resources=ResourcesCapability(),
        ),
        list_resource_templates=AsyncMock(return_value=page),
    )

    result = await inspect_resource_templates(client)

    assert result.status is InspectionStatus.SUCCESS
    assert result.pages == (page,)
    assert result.pages[0] is page
    assert result.failure is None

    client.list_resource_templates.assert_awaited_once_with()
    
@pytest.mark.anyio
async def test_inspect_resource_templates_follows_cursors_until_complete() -> None:
    """Resource-template inspection follows every continuation cursor."""

    first_page = ListResourceTemplatesResult(
        resource_templates=[],
        next_cursor="cursor-2",
    )

    second_page = ListResourceTemplatesResult(
        resource_templates=[],
        next_cursor="cursor-3",
    )

    third_page = ListResourceTemplatesResult(
        resource_templates=[],
        next_cursor=None,
    )

    client = SimpleNamespace(
        server_capabilities=ServerCapabilities(
            resources=ResourcesCapability(),
        ),
        list_resource_templates=AsyncMock(
            side_effect=[
                first_page,
                second_page,
                third_page,
            ]
        ),
    )

    result = await inspect_resource_templates(client)

    assert result.status is InspectionStatus.SUCCESS

    assert result.pages == (
        first_page,
        second_page,
        third_page,
    )

    assert result.pages[0] is first_page
    assert result.pages[1] is second_page
    assert result.pages[2] is third_page

    assert result.failure is None

    assert client.list_resource_templates.await_args_list == [
        call(),
        call(cursor="cursor-2"),
        call(cursor="cursor-3"),
    ]    
    
@pytest.mark.anyio
async def test_inspect_resource_templates_skips_unadvertised_templates() -> None:
    """Template inspection must not probe when resources are unadvertised."""

    client = SimpleNamespace(
        server_capabilities=ServerCapabilities(),
        list_resource_templates=AsyncMock(),
    )

    result = await inspect_resource_templates(client)

    assert result.status is InspectionStatus.NOT_ADVERTISED
    assert result.pages == ()
    assert result.failure is None

    client.list_resource_templates.assert_not_awaited()
    
@pytest.mark.anyio
async def test_inspect_resource_templates_preserves_pages_when_later_page_fails() -> None:
    """Successful template pages survive a later pagination failure."""

    first_page = ListResourceTemplatesResult(
        resource_templates=[],
        next_cursor="cursor-2",
    )

    second_page = ListResourceTemplatesResult(
        resource_templates=[],
        next_cursor="cursor-3",
    )

    failure = RuntimeError("third resource-template page failed")

    client = SimpleNamespace(
        server_capabilities=ServerCapabilities(
            resources=ResourcesCapability(),
        ),
        list_resource_templates=AsyncMock(
            side_effect=[
                first_page,
                second_page,
                failure,
            ]
        ),
    )

    result = await inspect_resource_templates(client)

    assert result.status is InspectionStatus.PARTIAL

    assert result.pages == (
        first_page,
        second_page,
    )

    assert result.pages[0] is first_page
    assert result.pages[1] is second_page

    assert result.failure is failure

    assert client.list_resource_templates.await_args_list == [
        call(),
        call(cursor="cursor-2"),
        call(cursor="cursor-3"),
    ]
    
@pytest.mark.anyio
async def test_inspect_resource_templates_reports_failed_when_first_page_fails() -> None:
    """Advertised template inspection is FAILED when no page can be obtained."""

    failure = RuntimeError("first resource-template page failed")

    client = SimpleNamespace(
        server_capabilities=ServerCapabilities(
            resources=ResourcesCapability(),
        ),
        list_resource_templates=AsyncMock(
            side_effect=failure,
        ),
    )

    result = await inspect_resource_templates(client)

    assert result.status is InspectionStatus.FAILED
    assert result.pages == ()
    assert result.failure is failure

    client.list_resource_templates.assert_awaited_once_with()
    
@pytest.mark.anyio
async def test_inspect_prompts_returns_success_for_single_complete_page() -> None:
    """A complete empty prompt page is still successful inspection."""

    page = ListPromptsResult(
        prompts=[],
        next_cursor=None,
    )

    client = SimpleNamespace(
        server_capabilities=ServerCapabilities(
            prompts=PromptsCapability(),
        ),
        list_prompts=AsyncMock(return_value=page),
    )

    result = await inspect_prompts(client)

    assert result.status is InspectionStatus.SUCCESS
    assert result.pages == (page,)
    assert result.pages[0] is page
    assert result.failure is None

    client.list_prompts.assert_awaited_once_with()
    
@pytest.mark.anyio
async def test_inspect_prompts_follows_cursors_until_complete() -> None:
    """Prompt inspection follows every continuation cursor."""

    first_page = ListPromptsResult(
        prompts=[],
        next_cursor="cursor-2",
    )

    second_page = ListPromptsResult(
        prompts=[],
        next_cursor="cursor-3",
    )

    third_page = ListPromptsResult(
        prompts=[],
        next_cursor=None,
    )

    client = SimpleNamespace(
        server_capabilities=ServerCapabilities(
            prompts=PromptsCapability(),
        ),
        list_prompts=AsyncMock(
            side_effect=[
                first_page,
                second_page,
                third_page,
            ]
        ),
    )

    result = await inspect_prompts(client)

    assert result.status is InspectionStatus.SUCCESS

    assert result.pages == (
        first_page,
        second_page,
        third_page,
    )

    assert result.pages[0] is first_page
    assert result.pages[1] is second_page
    assert result.pages[2] is third_page

    assert result.failure is None

    assert client.list_prompts.await_args_list == [
        call(),
        call(cursor="cursor-2"),
        call(cursor="cursor-3"),
    ]
    

@pytest.mark.anyio
async def test_inspect_prompts_preserves_pages_when_later_page_fails() -> None:
    """Successful prompt pages survive a later pagination failure."""

    first_page = ListPromptsResult(
        prompts=[],
        next_cursor="cursor-2",
    )

    second_page = ListPromptsResult(
        prompts=[],
        next_cursor="cursor-3",
    )

    failure = RuntimeError("third prompt page failed")

    client = SimpleNamespace(
        server_capabilities=ServerCapabilities(
            prompts=PromptsCapability(),
        ),
        list_prompts=AsyncMock(
            side_effect=[
                first_page,
                second_page,
                failure,
            ]
        ),
    )

    result = await inspect_prompts(client)

    assert result.status is InspectionStatus.PARTIAL

    assert result.pages == (
        first_page,
        second_page,
    )

    assert result.pages[0] is first_page
    assert result.pages[1] is second_page

    assert result.failure is failure

    assert client.list_prompts.await_args_list == [
        call(),
        call(cursor="cursor-2"),
        call(cursor="cursor-3"),
    ]   
    
@pytest.mark.anyio
async def test_inspect_prompts_skips_unadvertised_prompts() -> None:
    """Prompt inspection must not probe when prompts are unadvertised."""

    client = SimpleNamespace(
        server_capabilities=ServerCapabilities(),
        list_prompts=AsyncMock(),
    )

    result = await inspect_prompts(client)

    assert result.status is InspectionStatus.NOT_ADVERTISED
    assert result.pages == ()
    assert result.failure is None

    client.list_prompts.assert_not_awaited()
    
@pytest.mark.anyio
async def test_inspect_prompts_preserves_pages_when_later_page_fails() -> None:
    """Successful prompt pages survive a later pagination failure."""

    first_page = ListPromptsResult(
        prompts=[],
        next_cursor="cursor-2",
    )

    second_page = ListPromptsResult(
        prompts=[],
        next_cursor="cursor-3",
    )

    failure = RuntimeError("third prompt page failed")

    client = SimpleNamespace(
        server_capabilities=ServerCapabilities(
            prompts=PromptsCapability(),
        ),
        list_prompts=AsyncMock(
            side_effect=[
                first_page,
                second_page,
                failure,
            ]
        ),
    )

    result = await inspect_prompts(client)

    assert result.status is InspectionStatus.PARTIAL

    assert result.pages == (
        first_page,
        second_page,
    )

    assert result.pages[0] is first_page
    assert result.pages[1] is second_page

    assert result.failure is failure

    assert client.list_prompts.await_args_list == [
        call(),
        call(cursor="cursor-2"),
        call(cursor="cursor-3"),
    ]   
    
@pytest.mark.anyio
async def test_inspect_prompts_reports_failed_when_first_page_fails() -> None:
    """Advertised prompt inspection is FAILED when no page can be obtained."""

    failure = RuntimeError("first prompt page failed")

    client = SimpleNamespace(
        server_capabilities=ServerCapabilities(
            prompts=PromptsCapability(),
        ),
        list_prompts=AsyncMock(
            side_effect=failure,
        ),
    )

    result = await inspect_prompts(client)

    assert result.status is InspectionStatus.FAILED
    assert result.pages == ()
    assert result.failure is failure

    client.list_prompts.assert_awaited_once_with()