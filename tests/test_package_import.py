"""Tests for the basic MCP Details package boundary."""


def test_mcp_details_package_can_be_imported() -> None:
    """The installed project must expose the mcp_details Python package."""
    import mcp_details

    assert mcp_details is not None