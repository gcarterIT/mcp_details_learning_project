from mcp.types import (
    Implementation,
    ListPromptsResult,
    ListResourceTemplatesResult,
    ListResourcesResult,
    ListToolsResult,
    Prompt,
    PromptArgument,
    Resource,
    ResourceTemplate,
    ServerCapabilities,
    Tool,
)

from mcp_details.presentation import render_report

from mcp_details.results import (
    ApplicationInspectionResult,
    CategoryInspection,
    InspectionStatus,
    InspectionTargetSummary,
    MCPInspectionResult,
    ServerDescription,
)


def test_render_report_includes_core_application_inspection_summary() -> None:
    result = ApplicationInspectionResult(
        target=InspectionTargetSummary(
            display_name="Example MCP",
            transport="stdio",
        ),
        inspection=MCPInspectionResult(
            server_description=ServerDescription(
                protocol_version="2025-06-18",
                server_info=Implementation(
                    name="example-server",
                    version="1.2.3",
                ),
                server_capabilities=ServerCapabilities(),
                instructions=None,
            ),
            tools=CategoryInspection(
                status=InspectionStatus.SUCCESS,
                pages=(),
            ),
            resources=CategoryInspection(
                status=InspectionStatus.NOT_ADVERTISED,
                pages=(),
            ),
            resource_templates=CategoryInspection(
                status=InspectionStatus.PARTIAL,
                pages=(),
                failure=RuntimeError("template pagination failed"),
            ),
            prompts=CategoryInspection(
                status=InspectionStatus.FAILED,
                pages=(),
                failure=RuntimeError("prompt inspection failed"),
            ),
        ),
    )

    report = render_report(result)

    assert "MCP Inspection Report" in report

    assert "Example MCP" in report
    assert "stdio" in report

    assert "example-server" in report
    assert "1.2.3" in report
    assert "2025-06-18" in report

    assert "Tools" in report
    assert "SUCCESS" in report

    assert "Resources" in report
    assert "NOT_ADVERTISED" in report

    assert "Resource Templates" in report
    assert "PARTIAL" in report

    assert "Prompts" in report
    assert "FAILED" in report
    
def test_render_report_includes_tools_from_all_successful_pages() -> None:
    first_tool = Tool(
        name="get_weather",
        title="Current Weather",
        description="Get the current weather for a city.",
        inputSchema={
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                },
            },
            "required": ["city"],
        },
        outputSchema={
            "type": "object",
            "properties": {
                "temperature": {
                    "type": "number",
                },
            },
        },
    )

    second_tool = Tool(
        name="get_forecast",
        description="Get a multi-day weather forecast.",
        inputSchema={
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                },
                "days": {
                    "type": "integer",
                },
            },
        },
    )

    first_page = ListToolsResult(
        tools=[first_tool],
        next_cursor="cursor-2",
    )

    second_page = ListToolsResult(
        tools=[second_tool],
        next_cursor=None,
    )

    result = ApplicationInspectionResult(
        target=InspectionTargetSummary(
            display_name="Weather MCP",
            transport="stdio",
        ),
        inspection=MCPInspectionResult(
            server_description=ServerDescription(
                protocol_version="2025-06-18",
                server_info=None,
                server_capabilities=ServerCapabilities(),
                instructions=None,
            ),
            tools=CategoryInspection(
                status=InspectionStatus.SUCCESS,
                pages=(first_page, second_page),
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
        ),
    )

    report = render_report(result)

    assert "Tool: get_weather" in report
    assert "Title: Current Weather" in report
    assert "Description: Get the current weather for a city." in report
    assert '"city": {' in report
    assert '"required": [' in report
    assert "Output Schema:" in report
    assert '"temperature": {' in report

    assert "Tool: get_forecast" in report
    assert "Description: Get a multi-day weather forecast." in report
    assert '"days": {' in report

    assert report.index("Tool: get_weather") < report.index("Tool: get_forecast")

    assert result.inspection.tools.pages == (
        first_page,
        second_page,
    )
    
def test_render_report_distinguishes_successful_empty_tools_inventory() -> None:
    result = ApplicationInspectionResult(
        target=InspectionTargetSummary(
            display_name="Empty Tools MCP",
            transport="stdio",
        ),
        inspection=MCPInspectionResult(
            server_description=ServerDescription(
                protocol_version="2025-06-18",
                server_info=None,
                server_capabilities=ServerCapabilities(),
                instructions=None,
            ),
            tools=CategoryInspection(
                status=InspectionStatus.SUCCESS,
                pages=(
                    ListToolsResult(
                        tools=[],
                        next_cursor=None,
                    ),
                ),
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
        ),
    )

    report = render_report(result)

    assert "Tools" in report
    assert "Status: SUCCESS" in report
    assert "No tools reported." in report
    
def test_render_report_preserves_partial_tools_and_reports_failure() -> None:
    preserved_tool = Tool(
        name="get_weather",
        description="Get current weather.",
        inputSchema={
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                },
            },
        },
    )

    preserved_page = ListToolsResult(
        tools=[preserved_tool],
        next_cursor="cursor-2",
    )

    failure = RuntimeError("second tools page failed")

    result = ApplicationInspectionResult(
        target=InspectionTargetSummary(
            display_name="Partial Tools MCP",
            transport="stdio",
        ),
        inspection=MCPInspectionResult(
            server_description=ServerDescription(
                protocol_version="2025-06-18",
                server_info=None,
                server_capabilities=ServerCapabilities(),
                instructions=None,
            ),
            tools=CategoryInspection(
                status=InspectionStatus.PARTIAL,
                pages=(preserved_page,),
                failure=failure,
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
        ),
    )

    report = render_report(result)

    assert "Tools" in report
    assert "Status: PARTIAL" in report

    assert "Tool: get_weather" in report
    assert "Description: Get current weather." in report
    assert '"city": {' in report

    assert "Failure:" in report
    assert "RuntimeError: second tools page failed" in report

    assert result.inspection.tools.pages == (preserved_page,)
    assert result.inspection.tools.failure is failure
    
def test_render_report_reports_failed_tools_without_inventory() -> None:
    failure = RuntimeError("first tools page failed")

    result = ApplicationInspectionResult(
        target=InspectionTargetSummary(
            display_name="Failed Tools MCP",
            transport="stdio",
        ),
        inspection=MCPInspectionResult(
            server_description=ServerDescription(
                protocol_version="2025-06-18",
                server_info=None,
                server_capabilities=ServerCapabilities(),
                instructions=None,
            ),
            tools=CategoryInspection(
                status=InspectionStatus.FAILED,
                pages=(),
                failure=failure,
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
        ),
    )

    report = render_report(result)

    assert "Tools" in report
    assert "Status: FAILED" in report
    assert "Failure:" in report
    assert "RuntimeError: first tools page failed" in report

    assert "Tool:" not in report
    assert "No tools reported." not in report

    assert result.inspection.tools.pages == ()
    assert result.inspection.tools.failure is failure    
    
def test_render_report_includes_resources_from_all_successful_pages() -> None:
    first_resource = Resource(
        name="current-weather",
        title="Current Weather Data",
        uri="weather://current",
        description="Current observed weather.",
        mimeType="application/json",
        size=2048,
    )

    second_resource = Resource(
        name="forecast-data",
        uri="weather://forecast",
        description="Multi-day forecast data.",
    )

    first_page = ListResourcesResult(
        resources=[first_resource],
        next_cursor="cursor-2",
    )

    second_page = ListResourcesResult(
        resources=[second_resource],
        next_cursor=None,
    )

    result = ApplicationInspectionResult(
        target=InspectionTargetSummary(
            display_name="Weather MCP",
            transport="stdio",
        ),
        inspection=MCPInspectionResult(
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
                status=InspectionStatus.SUCCESS,
                pages=(first_page, second_page),
            ),
            resource_templates=CategoryInspection(
                status=InspectionStatus.NOT_ADVERTISED,
                pages=(),
            ),
            prompts=CategoryInspection(
                status=InspectionStatus.NOT_ADVERTISED,
                pages=(),
            ),
        ),
    )

    report = render_report(result)

    assert "Resource" in report
    assert "Name: current-weather" in report
    assert "Title: Current Weather Data" in report
    assert "URI: weather://current" in report
    assert "Description: Current observed weather." in report
    assert "MIME Type: application/json" in report
    assert "Size: 2048" in report

    assert "Name: forecast-data" in report
    assert "URI: weather://forecast" in report
    assert "Description: Multi-day forecast data." in report

    assert report.index("Name: current-weather") < report.index(
        "Name: forecast-data"
    )

    assert result.inspection.resources.pages == (
        first_page,
        second_page,
    )

def test_render_report_distinguishes_successful_empty_resource_inventory() -> None:
    result = ApplicationInspectionResult(
        target=InspectionTargetSummary(
            display_name="Empty Resources MCP",
            transport="stdio",
        ),
        inspection=MCPInspectionResult(
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
                status=InspectionStatus.SUCCESS,
                pages=(
                    ListResourcesResult(
                        resources=[],
                        next_cursor=None,
                    ),
                ),
            ),
            resource_templates=CategoryInspection(
                status=InspectionStatus.NOT_ADVERTISED,
                pages=(),
            ),
            prompts=CategoryInspection(
                status=InspectionStatus.NOT_ADVERTISED,
                pages=(),
            ),
        ),
    )

    report = render_report(result)

    assert "Resources" in report
    assert "Status: SUCCESS" in report
    assert "No resources reported." in report
    
def test_render_report_preserves_partial_resources_and_reports_failure() -> None:
    preserved_resource = Resource(
        name="current-weather",
        uri="weather://current",
        description="Current observed weather.",
        mimeType="application/json",
    )

    preserved_page = ListResourcesResult(
        resources=[preserved_resource],
        next_cursor="cursor-2",
    )

    failure = RuntimeError("second resources page failed")

    result = ApplicationInspectionResult(
        target=InspectionTargetSummary(
            display_name="Partial Resources MCP",
            transport="stdio",
        ),
        inspection=MCPInspectionResult(
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
                status=InspectionStatus.PARTIAL,
                pages=(preserved_page,),
                failure=failure,
            ),
            resource_templates=CategoryInspection(
                status=InspectionStatus.NOT_ADVERTISED,
                pages=(),
            ),
            prompts=CategoryInspection(
                status=InspectionStatus.NOT_ADVERTISED,
                pages=(),
            ),
        ),
    )

    report = render_report(result)

    assert "Resources" in report
    assert "Status: PARTIAL" in report

    assert "Name: current-weather" in report
    assert "URI: weather://current" in report
    assert "Description: Current observed weather." in report
    assert "MIME Type: application/json" in report

    assert "Failure:" in report
    assert "RuntimeError: second resources page failed" in report

    assert result.inspection.resources.pages == (preserved_page,)
    assert result.inspection.resources.failure is failure
    
def test_render_report_reports_failed_resources_without_inventory() -> None:
    failure = RuntimeError("first resources page failed")

    result = ApplicationInspectionResult(
        target=InspectionTargetSummary(
            display_name="Failed Resources MCP",
            transport="stdio",
        ),
        inspection=MCPInspectionResult(
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
                status=InspectionStatus.FAILED,
                pages=(),
                failure=failure,
            ),
            resource_templates=CategoryInspection(
                status=InspectionStatus.NOT_ADVERTISED,
                pages=(),
            ),
            prompts=CategoryInspection(
                status=InspectionStatus.NOT_ADVERTISED,
                pages=(),
            ),
        ),
    )

    report = render_report(result)

    assert "Resources" in report
    assert "Status: FAILED" in report
    assert "Failure:" in report
    assert "RuntimeError: first resources page failed" in report

    assert "\n  Resource\n" not in report
    assert "No resources reported." not in report

    assert result.inspection.resources.pages == ()
    assert result.inspection.resources.failure is failure   
    
def test_render_report_includes_resource_templates_from_all_successful_pages() -> None:
    first_template = ResourceTemplate(
        name="city-forecast",
        title="City Forecast",
        uriTemplate="weather://forecast/{city}",
        description="Forecast data for one city.",
        mimeType="application/json",
    )

    second_template = ResourceTemplate(
        name="station-observation",
        uriTemplate="weather://station/{station_id}",
        description="Observed weather for one station.",
    )

    first_page = ListResourceTemplatesResult(
        resourceTemplates=[first_template],
        next_cursor="cursor-2",
    )

    second_page = ListResourceTemplatesResult(
        resourceTemplates=[second_template],
        next_cursor=None,
    )

    result = ApplicationInspectionResult(
        target=InspectionTargetSummary(
            display_name="Weather MCP",
            transport="stdio",
        ),
        inspection=MCPInspectionResult(
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
                status=InspectionStatus.SUCCESS,
                pages=(first_page, second_page),
            ),
            prompts=CategoryInspection(
                status=InspectionStatus.NOT_ADVERTISED,
                pages=(),
            ),
        ),
    )

    report = render_report(result)

    assert "Resource Templates" in report
    assert "Status: SUCCESS" in report

    assert "Resource Template" in report
    assert "Name: city-forecast" in report
    assert "Title: City Forecast" in report
    assert "URI Template: weather://forecast/{city}" in report
    assert "Description: Forecast data for one city." in report
    assert "MIME Type: application/json" in report

    assert "Name: station-observation" in report
    assert "URI Template: weather://station/{station_id}" in report
    assert "Description: Observed weather for one station." in report

    assert report.index("Name: city-forecast") < report.index(
        "Name: station-observation"
    )

    assert result.inspection.resource_templates.pages == (
        first_page,
        second_page,
    )
    
def test_render_report_distinguishes_successful_empty_resource_template_inventory() -> None:
    result = ApplicationInspectionResult(
        target=InspectionTargetSummary(
            display_name="Empty Templates MCP",
            transport="stdio",
        ),
        inspection=MCPInspectionResult(
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
                status=InspectionStatus.SUCCESS,
                pages=(
                    ListResourceTemplatesResult(
                        resourceTemplates=[],
                        next_cursor=None,
                    ),
                ),
            ),
            prompts=CategoryInspection(
                status=InspectionStatus.NOT_ADVERTISED,
                pages=(),
            ),
        ),
    )

    report = render_report(result)

    assert "Resource Templates" in report
    assert "Status: SUCCESS" in report
    assert "No resource templates reported." in report    
    
def test_render_report_preserves_partial_resource_templates_and_reports_failure() -> None:
    preserved_template = ResourceTemplate(
        name="city-forecast",
        uriTemplate="weather://forecast/{city}",
        description="Forecast data for one city.",
        mimeType="application/json",
    )

    preserved_page = ListResourceTemplatesResult(
        resourceTemplates=[preserved_template],
        next_cursor="cursor-2",
    )

    failure = RuntimeError("second resource templates page failed")

    result = ApplicationInspectionResult(
        target=InspectionTargetSummary(
            display_name="Partial Templates MCP",
            transport="stdio",
        ),
        inspection=MCPInspectionResult(
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
                status=InspectionStatus.PARTIAL,
                pages=(preserved_page,),
                failure=failure,
            ),
            prompts=CategoryInspection(
                status=InspectionStatus.NOT_ADVERTISED,
                pages=(),
            ),
        ),
    )

    report = render_report(result)

    assert "Resource Templates" in report
    assert "Status: PARTIAL" in report

    assert "Name: city-forecast" in report
    assert "URI Template: weather://forecast/{city}" in report
    assert "Description: Forecast data for one city." in report
    assert "MIME Type: application/json" in report

    assert "Failure:" in report
    assert (
        "RuntimeError: second resource templates page failed"
        in report
    )

    assert "No resource templates reported." not in report

    assert result.inspection.resource_templates.pages == (
        preserved_page,
    )
    assert result.inspection.resource_templates.failure is failure

def test_render_report_reports_failed_resource_templates_without_inventory() -> None:
    failure = RuntimeError("first resource templates page failed")

    result = ApplicationInspectionResult(
        target=InspectionTargetSummary(
            display_name="Failed Templates MCP",
            transport="stdio",
        ),
        inspection=MCPInspectionResult(
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
                status=InspectionStatus.FAILED,
                pages=(),
                failure=failure,
            ),
            prompts=CategoryInspection(
                status=InspectionStatus.NOT_ADVERTISED,
                pages=(),
            ),
        ),
    )

    report = render_report(result)

    assert "Resource Templates" in report
    assert "Status: FAILED" in report
    assert "Failure:" in report
    assert (
        "RuntimeError: first resource templates page failed"
        in report
    )

    assert "\n  Resource Template\n" not in report
    assert "No resource templates reported." not in report

    assert result.inspection.resource_templates.pages == ()
    assert result.inspection.resource_templates.failure is failure
    
def test_render_report_includes_prompts_from_all_successful_pages() -> None:
    first_prompt = Prompt(
        name="weather-summary",
        title="Weather Summary",
        description="Generate a weather summary for a location.",
        arguments=[
            PromptArgument(
                name="location",
                title="Location",
                description="Location to summarize.",
                required=True,
            ),
            PromptArgument(
                name="units",
                description="Preferred measurement system.",
                required=False,
            ),
        ],
    )

    second_prompt = Prompt(
        name="server-status",
        description="Summarize current server status.",
    )

    first_page = ListPromptsResult(
        prompts=[first_prompt],
        next_cursor="cursor-2",
    )

    second_page = ListPromptsResult(
        prompts=[second_prompt],
        next_cursor=None,
    )

    result = ApplicationInspectionResult(
        target=InspectionTargetSummary(
            display_name="Weather MCP",
            transport="stdio",
        ),
        inspection=MCPInspectionResult(
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
                status=InspectionStatus.SUCCESS,
                pages=(first_page, second_page),
            ),
        ),
    )

    report = render_report(result)

    assert "Prompts" in report
    assert "Status: SUCCESS" in report

    assert "Prompt" in report
    assert "Name: weather-summary" in report
    assert "Title: Weather Summary" in report
    assert (
        "Description: Generate a weather summary for a location."
        in report
    )

    assert "Arguments:" in report

    assert "Name: location" in report
    assert "Title: Location" in report
    assert "Description: Location to summarize." in report
    assert "Required: yes" in report

    assert "Name: units" in report
    assert "Description: Preferred measurement system." in report
    assert "Required: no" in report

    assert "Name: server-status" in report
    assert "Description: Summarize current server status." in report

    assert report.index("Name: weather-summary") < report.index(
        "Name: server-status"
    )

    assert result.inspection.prompts.pages == (
        first_page,
        second_page,
    )
    
def test_render_report_distinguishes_successful_empty_prompt_inventory() -> None:
    result = ApplicationInspectionResult(
        target=InspectionTargetSummary(
            display_name="Empty Prompts MCP",
            transport="stdio",
        ),
        inspection=MCPInspectionResult(
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
                status=InspectionStatus.SUCCESS,
                pages=(
                    ListPromptsResult(
                        prompts=[],
                        next_cursor=None,
                    ),
                ),
            ),
        ),
    )

    report = render_report(result)

    assert "Prompts" in report
    assert "Status: SUCCESS" in report
    assert "No prompts reported." in report
    
def test_render_report_preserves_partial_prompts_and_reports_failure() -> None:
    preserved_prompt = Prompt(
        name="weather-summary",
        description="Generate a weather summary.",
        arguments=[
            PromptArgument(
                name="location",
                description="Location to summarize.",
                required=True,
            ),
        ],
    )

    preserved_page = ListPromptsResult(
        prompts=[preserved_prompt],
        next_cursor="cursor-2",
    )

    failure = RuntimeError("second prompts page failed")

    result = ApplicationInspectionResult(
        target=InspectionTargetSummary(
            display_name="Partial Prompts MCP",
            transport="stdio",
        ),
        inspection=MCPInspectionResult(
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
                status=InspectionStatus.PARTIAL,
                pages=(preserved_page,),
                failure=failure,
            ),
        ),
    )

    report = render_report(result)

    assert "Prompts" in report
    assert "Status: PARTIAL" in report

    assert "Name: weather-summary" in report
    assert "Description: Generate a weather summary." in report

    assert "Arguments:" in report
    assert "Name: location" in report
    assert "Description: Location to summarize." in report
    assert "Required: yes" in report

    assert "Failure:" in report
    assert "RuntimeError: second prompts page failed" in report

    assert "No prompts reported." not in report

    assert result.inspection.prompts.pages == (
        preserved_page,
    )
    assert result.inspection.prompts.failure is failure
    
def test_render_report_reports_failed_prompts_without_inventory() -> None:
    failure = RuntimeError("first prompts page failed")

    result = ApplicationInspectionResult(
        target=InspectionTargetSummary(
            display_name="Failed Prompts MCP",
            transport="stdio",
        ),
        inspection=MCPInspectionResult(
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
                status=InspectionStatus.FAILED,
                pages=(),
                failure=failure,
            ),
        ),
    )

    report = render_report(result)

    assert "Prompts" in report
    assert "Status: FAILED" in report
    assert "Failure:" in report
    assert "RuntimeError: first prompts page failed" in report

    assert "\n  Prompt\n" not in report
    assert "No prompts reported." not in report

    assert result.inspection.prompts.pages == ()
    assert result.inspection.prompts.failure is failure
    
    