"""Representative STDIO MCP server for manual presentation acceptance testing."""

import anyio

from mcp import types
from mcp.server.lowlevel.server import Server, ServerRequestContext
from mcp.server.stdio import stdio_server


async def list_tools(
    context: ServerRequestContext[dict[str, object]],
    params: types.PaginatedRequestParams | None,
) -> types.ListToolsResult:
    """Return representative tools for the presentation demo."""
    return types.ListToolsResult(
        tools=[
            types.Tool(
                name="add_numbers",
                title="Add Numbers",
                description=(
                    "Add two integer values for the MCP Details "
                    "presentation demo."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "a": {
                            "type": "integer",
                        },
                        "b": {
                            "type": "integer",
                        },
                    },
                    "required": ["a", "b"],
                },
            ),
        ],
    )


async def list_resources(
    context: ServerRequestContext[dict[str, object]],
    params: types.PaginatedRequestParams | None,
) -> types.ListResourcesResult:
    """Return representative resources for the presentation demo."""
    return types.ListResourcesResult(
        resources=[
            types.Resource(
                name="demo_readme",
                title="Demo README",
                uri="demo://readme",
                description=(
                    "README resource for the MCP Details "
                    "presentation demo."
                ),
                mime_type="text/plain",
            ),
        ],
    )


async def list_resource_templates(
    context: ServerRequestContext[dict[str, object]],
    params: types.PaginatedRequestParams | None,
) -> types.ListResourceTemplatesResult:
    """Return representative resource templates for the presentation demo."""
    return types.ListResourceTemplatesResult(
        resource_templates=[
            types.ResourceTemplate(
                name="demo_user",
                title="Demo User",
                uri_template="demo://users/{user_id}",
                description=(
                    "User resource template for the MCP Details "
                    "presentation demo."
                ),
                mime_type="application/json",
            ),
        ],
    )


async def list_prompts(
    context: ServerRequestContext[dict[str, object]],
    params: types.PaginatedRequestParams | None,
) -> types.ListPromptsResult:
    """Return representative prompts for the presentation demo."""
    return types.ListPromptsResult(
        prompts=[
            types.Prompt(
                name="summarize_text",
                title="Summarize Text",
                description=(
                    "Summarize supplied text for the MCP Details "
                    "presentation demo."
                ),
                arguments=[
                    types.PromptArgument(
                        name="text",
                        description="Text to summarize.",
                        required=True,
                    ),
                    types.PromptArgument(
                        name="style",
                        description="Optional summary style.",
                        required=False,
                    ),
                ],
            ),
        ],
    )


async def main() -> None:
    """Run the representative MCP server over STDIO."""
    server: Server[dict[str, object]] = Server(
        "mcp-details-presentation-demo",
        version="1.0.0",
        title="MCP Details Presentation Demo",
        description=(
            "Representative MCP server used for manual "
            "presentation acceptance testing."
        ),
        instructions=(
            "Inspect this server without executing its primitives."
        ),
        on_list_tools=list_tools,
        on_list_resources=list_resources,
        on_list_resource_templates=list_resource_templates,
        on_list_prompts=list_prompts,
    )

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    anyio.run(main)