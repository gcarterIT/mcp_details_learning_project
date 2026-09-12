"""Human-readable presentation of MCP inspection results."""

import json

from mcp.types import (
    ListPromptsResult,
    ListResourceTemplatesResult,
    ListResourcesResult,
    ListToolsResult,
)

from mcp_details.results import (
    ApplicationInspectionResult,
    CategoryInspection,
    InspectionStatus,
)


def _append_schema(
    lines: list[str],
    label: str,
    schema: dict,
) -> None:
    """Append one JSON schema in readable indented form."""

    lines.append(f"    {label}:")

    rendered_schema = json.dumps(
        schema,
        indent=2,
    )

    lines.extend(
        f"      {line}"
        for line in rendered_schema.splitlines()
    )


def _render_tools(
    tools: CategoryInspection[ListToolsResult],
) -> list[str]:
    """Render preserved tool inspection evidence."""

    lines = [
        "Tools",
        f"  Status: {tools.status.name}",
    ]

    tool_count = 0

    for page in tools.pages:
        for tool in page.tools:
            tool_count += 1

            lines.extend(
                [
                    "",
                    f"  Tool: {tool.name}",
                ]
            )

            if tool.title is not None:
                lines.append(f"    Title: {tool.title}")

            if tool.description is not None:
                lines.append(
                    f"    Description: {tool.description}"
                )

            _append_schema(
                lines,
                "Input Schema",
                tool.input_schema,
            )

            if tool.output_schema is not None:
                _append_schema(
                    lines,
                    "Output Schema",
                    tool.output_schema,
                )

    _append_inventory_outcome(
        lines,
        status=tools.status,
        item_count=tool_count,
        empty_message="  No tools reported.",
        failure=tools.failure,
    )

    return lines



def _render_resources(
    resources: CategoryInspection[ListResourcesResult],
) -> list[str]:
    """Render preserved static-resource inspection evidence."""

    lines = [
        "Resources",
        f"  Status: {resources.status.name}",
    ]

    resource_count = 0

    for page in resources.pages:
        for resource in page.resources:
            resource_count += 1

            lines.extend(
                [
                    "",
                    "  Resource",
                    f"    Name: {resource.name}",
                ]
            )

            if resource.title is not None:
                lines.append(
                    f"    Title: {resource.title}"
                )

            lines.append(
                f"    URI: {resource.uri}"
            )

            if resource.description is not None:
                lines.append(
                    f"    Description: {resource.description}"
                )

            if resource.mime_type is not None:
                lines.append(
                    f"    MIME Type: {resource.mime_type}"
                )

            if resource.size is not None:
                lines.append(
                    f"    Size: {resource.size}"
                )

    _append_inventory_outcome(
        lines,
        status=resources.status,
        item_count=resource_count,
        empty_message="  No resources reported.",
        failure=resources.failure,
    )

    return lines 


def render_report(result: ApplicationInspectionResult) -> str:
    """Render one application inspection result as human-readable text."""

    target = result.target
    inspection = result.inspection
    server = inspection.server_description

    if server.server_info is None:
        server_identity = "Not reported"
    else:
        server_identity = (
            f"{server.server_info.name} "
            f"{server.server_info.version}"
        )

    lines = [
        "MCP Inspection Report",
        "",
        "Configured Target",
        f"  Name: {target.display_name}",
        f"  Transport: {target.transport}",
        "",
        "Server",
        f"  Identity: {server_identity}",
        f"  Protocol Version: {server.protocol_version}",
        "",
    ]

    lines.extend(_render_tools(inspection.tools))

    lines.append("")

    lines.extend(
        _render_resources(inspection.resources)
    )

    lines.append("")

    lines.extend(
        _render_resource_templates(
            inspection.resource_templates
        )
    )

    lines.append("")

    lines.extend(
        _render_prompts(
            inspection.prompts
        )
    )
    return "\n".join(lines)
    
def _append_failure(
    lines: list[str],
    failure: Exception,
) -> None:
    """Append one human-readable failure description."""

    lines.extend(
        [
            "  Failure:",
            f"    {type(failure).__name__}: {failure}",
        ]
    )
    
def _append_inventory_outcome(
    lines: list[str],
    *,
    status: InspectionStatus,
    item_count: int,
    empty_message: str,
    failure: Exception | None,
) -> None:
    """Append shared inventory outcome details."""

    if status is InspectionStatus.SUCCESS and item_count == 0:
        lines.append(empty_message)

    if failure is not None:
        _append_failure(
            lines,
            failure,
        )
        
def _render_resource_templates(
    resource_templates: CategoryInspection[
        ListResourceTemplatesResult
    ],
) -> list[str]:
    """Render preserved resource-template inspection evidence."""

    lines = [
        "Resource Templates",
        f"  Status: {resource_templates.status.name}",
    ]

    template_count = 0

    for page in resource_templates.pages:
        for template in page.resource_templates:
            template_count += 1

            lines.extend(
                [
                    "",
                    "  Resource Template",
                    f"    Name: {template.name}",
                ]
            )

            if template.title is not None:
                lines.append(
                    f"    Title: {template.title}"
                )

            lines.append(
                f"    URI Template: {template.uri_template}"
            )

            if template.description is not None:
                lines.append(
                    f"    Description: {template.description}"
                )

            if template.mime_type is not None:
                lines.append(
                    f"    MIME Type: {template.mime_type}"
                )

    _append_inventory_outcome(
        lines,
        status=resource_templates.status,
        item_count=template_count,
        empty_message="  No resource templates reported.",
        failure=resource_templates.failure,
    )

    return lines
    
def _render_prompts(
    prompts: CategoryInspection[ListPromptsResult],
) -> list[str]:
    """Render preserved prompt inspection evidence."""

    lines = [
        "Prompts",
        f"  Status: {prompts.status.name}",
    ]

    prompt_count = 0

    for page in prompts.pages:
        for prompt in page.prompts:
            prompt_count += 1

            lines.extend(
                [
                    "",
                    "  Prompt",
                    f"    Name: {prompt.name}",
                ]
            )

            if prompt.title is not None:
                lines.append(
                    f"    Title: {prompt.title}"
                )

            if prompt.description is not None:
                lines.append(
                    f"    Description: {prompt.description}"
                )

            if prompt.arguments:
                lines.append("    Arguments:")

                for argument in prompt.arguments:
                    lines.extend(
                        [
                            "      Argument",
                            f"        Name: {argument.name}",
                        ]
                    )

                    if argument.title is not None:
                        lines.append(
                            f"        Title: {argument.title}"
                        )

                    if argument.description is not None:
                        lines.append(
                            f"        Description: {argument.description}"
                        )

                    if argument.required is True:
                        lines.append(
                            "        Required: yes"
                        )
                    elif argument.required is False:
                        lines.append(
                            "        Required: no"
                        )

    _append_inventory_outcome(
        lines,
        status=prompts.status,
        item_count=prompt_count,
        empty_message="  No prompts reported.",
        failure=prompts.failure,
    )

    return lines
    
    
    