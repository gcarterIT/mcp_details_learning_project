from mcp.types import (
    Implementation,
    ListPromptsResult,
    ListResourcesResult,
    ListResourceTemplatesResult,
    ListToolsResult,
    ServerCapabilities,
)

from mcp_details.results import (
    ApplicationInspectionResult,
    CategoryInspection,
    InspectionStatus,
    InspectionTargetSummary,
    MCPInspectionResult,
    ServerDescription,
)


def test_mcp_inspection_result_preserves_component_results() -> None:
    server_description = ServerDescription(
        protocol_version="2025-06-18",
        server_info=None,
        server_capabilities=ServerCapabilities(),
        instructions=None,
    )

    tools_page = ListToolsResult(tools=[])
    resources_page = ListResourcesResult(resources=[])
    resource_templates_page = ListResourceTemplatesResult(
        resourceTemplates=[]
    )
    prompts_page = ListPromptsResult(prompts=[])

    tools = CategoryInspection(
        status=InspectionStatus.SUCCESS,
        pages=(tools_page,),
    )

    resources = CategoryInspection(
        status=InspectionStatus.SUCCESS,
        pages=(resources_page,),
    )

    resource_templates = CategoryInspection(
        status=InspectionStatus.SUCCESS,
        pages=(resource_templates_page,),
    )

    prompts = CategoryInspection(
        status=InspectionStatus.SUCCESS,
        pages=(prompts_page,),
    )

    result = MCPInspectionResult(
        server_description=server_description,
        tools=tools,
        resources=resources,
        resource_templates=resource_templates,
        prompts=prompts,
    )

    assert result.server_description is server_description
    assert result.tools is tools
    assert result.resources is resources
    assert result.resource_templates is resource_templates
    assert result.prompts is prompts
    
def test_application_inspection_result_preserves_target_and_inspection() -> None:
    server_description = ServerDescription(
        protocol_version="2025-06-18",
        server_info=None,
        server_capabilities=ServerCapabilities(),
        instructions=None,
    )

    inspection = MCPInspectionResult(
        server_description=server_description,
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

    target = InspectionTargetSummary(
        display_name="Example MCP",
        transport="stdio",
    )

    result = ApplicationInspectionResult(
        target=target,
        inspection=inspection,
    )

    assert result.target is target
    assert result.inspection is inspection
    assert result.target.display_name == "Example MCP"
    assert result.target.transport == "stdio"    