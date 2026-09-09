"""Transport-neutral MCP server inspection for MCP Details."""

from collections.abc import Awaitable, Callable
from enum import Enum
from typing import Protocol, TypeVar

from mcp import Client

from mcp.types import (
    ListPromptsResult,
    ListResourcesResult,
    ListResourceTemplatesResult,
    ListToolsResult,
    ServerCapabilities,
)

from mcp_details.results import (
    CategoryInspection,
    InspectionStatus,
    MCPInspectionResult,
    ServerDescription,
)


class PaginatedPage(Protocol):
    """Minimum SDK page contract required by inspection pagination."""

    next_cursor: str | None


PageT = TypeVar("PageT", bound=PaginatedPage)


class InspectionCategory(Enum):
    """Discovery categories supported by MCP Details."""

    TOOLS = "tools"
    RESOURCES = "resources"
    RESOURCE_TEMPLATES = "resource_templates"
    PROMPTS = "prompts"


def inspect_server_description(client: Client) -> ServerDescription:
    """Capture negotiated server description from an already-connected Client."""

    return ServerDescription(
        protocol_version=client.protocol_version,
        server_info=client.server_info,
        server_capabilities=client.server_capabilities,
        instructions=client.instructions,
    )


def is_category_advertised(
    capabilities: ServerCapabilities,
    category: InspectionCategory,
) -> bool:
    """Return whether the server advertised support for an inspection category."""

    match category:
        case InspectionCategory.TOOLS:
            return capabilities.tools is not None

        case InspectionCategory.RESOURCES | InspectionCategory.RESOURCE_TEMPLATES:
            return capabilities.resources is not None

        case InspectionCategory.PROMPTS:
            return capabilities.prompts is not None


async def _inspect_paginated_pages(
    list_pages: Callable[..., Awaitable[PageT]],
) -> CategoryInspection[PageT]:
    """Inspect all pages from an SDK list operation while preserving evidence."""

    pages: list[PageT] = []
    next_cursor: str | None = None

    try:
        while True:
            if next_cursor is None and not pages:
                page = await list_pages()
            else:
                page = await list_pages(cursor=next_cursor)

            pages.append(page)

            if page.next_cursor is None:
                return CategoryInspection(
                    status=InspectionStatus.SUCCESS,
                    pages=tuple(pages),
                )

            next_cursor = page.next_cursor

    except Exception as exc:
        status = (
            InspectionStatus.PARTIAL
            if pages
            else InspectionStatus.FAILED
        )

        return CategoryInspection(
            status=status,
            pages=tuple(pages),
            failure=exc,
        )


async def inspect_tools(
    client: Client,
) -> CategoryInspection[ListToolsResult]:
    """Inspect all advertised tools while preserving partial evidence."""

    if not is_category_advertised(
        client.server_capabilities,
        InspectionCategory.TOOLS,
    ):
        return CategoryInspection(
            status=InspectionStatus.NOT_ADVERTISED,
            pages=(),
        )

    return await _inspect_paginated_pages(client.list_tools)


async def inspect_resources(
    client: Client,
) -> CategoryInspection[ListResourcesResult]:
    """Inspect all advertised static resources while preserving partial evidence."""

    if not is_category_advertised(
        client.server_capabilities,
        InspectionCategory.RESOURCES,
    ):
        return CategoryInspection(
            status=InspectionStatus.NOT_ADVERTISED,
            pages=(),
        )

    return await _inspect_paginated_pages(client.list_resources)

async def inspect_resource_templates(
    client: Client,
) -> CategoryInspection[ListResourceTemplatesResult]:
    """Inspect all advertised resource templates while preserving partial evidence."""

    if not is_category_advertised(
        client.server_capabilities,
        InspectionCategory.RESOURCE_TEMPLATES,
    ):
        return CategoryInspection(
            status=InspectionStatus.NOT_ADVERTISED,
            pages=(),
        )

    return await _inspect_paginated_pages(client.list_resource_templates)
    
async def inspect_prompts(
    client: Client,
) -> CategoryInspection[ListPromptsResult]:
    """Inspect all advertised prompts while preserving partial evidence."""

    if not is_category_advertised(
        client.server_capabilities,
        InspectionCategory.PROMPTS,
    ):
        return CategoryInspection(
            status=InspectionStatus.NOT_ADVERTISED,
            pages=(),
        )

    return await _inspect_paginated_pages(client.list_prompts)
    
async def inspect_mcp(client: Client) -> MCPInspectionResult:
    """Inspect one already-connected MCP server completely."""

    server_description = inspect_server_description(client)

    tools = await inspect_tools(client)
    resources = await inspect_resources(client)
    resource_templates = await inspect_resource_templates(client)
    prompts = await inspect_prompts(client)

    return MCPInspectionResult(
        server_description=server_description,
        tools=tools,
        resources=resources,
        resource_templates=resource_templates,
        prompts=prompts,
    )