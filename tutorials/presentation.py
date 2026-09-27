def render_report(result: dict[str, str]) -> str:
    """Convert structured inspection data into terminal text."""

    return (
        "MCP Inspection Report\n"
        f"Server: {result['server']}\n"
        f"Tools: {result['tools']}"
    )