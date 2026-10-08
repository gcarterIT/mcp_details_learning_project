"""Connection profile models for MCP Details."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


@dataclass(frozen=True)
class StdioConnectionProfile:
    """Project-owned configuration describing a STDIO MCP connection."""

    display_name: str
    command: str
    args: tuple[str, ...] = ()
    cwd: Path | None = None
    environment_variables: tuple[str, ...] = ()
    transport: Literal["stdio"] = field(default="stdio", init=False)

    def __post_init__(self) -> None:
        """Validate the minimal structural requirements of a STDIO profile."""
        if not self.display_name.strip():
            raise ValueError("display_name must not be blank")

        if not self.command.strip():
            raise ValueError("command must not be blank")

        if any(not name.strip() for name in self.environment_variables):
            raise ValueError("environment variable names must not be blank")

@dataclass(frozen=True)
class HttpHeaderEnvironmentReference:
    """Reference an HTTP header value through a runtime environment variable."""

    header_name: str
    environment_variable: str

    def __post_init__(self) -> None:
        """Validate the structural requirements of an HTTP header reference."""
        if not self.header_name.strip():
            raise ValueError("header_name must not be blank")

        if not self.environment_variable.strip():
            raise ValueError("environment_variable must not be blank")

@dataclass(frozen=True)
class StreamableHttpConnectionProfile:
    """Project-owned configuration describing a Streamable HTTP MCP connection."""

    display_name: str
    url: str
    header_references: tuple[HttpHeaderEnvironmentReference, ...] = ()
    transport: Literal["streamable_http"] = field(
        default="streamable_http",
        init=False,
    )

    def __post_init__(self) -> None:
        """Validate the minimal structural requirements of a Streamable HTTP profile."""
        if not self.display_name.strip():
            raise ValueError("display_name must not be blank")

        if not self.url.strip():
            raise ValueError("url must not be blank")
            
def test_streamable_http_profile_defaults_header_references_to_empty_tuple() -> None:
    profile = StreamableHttpConnectionProfile(
        display_name="Remote Demo MCP",
        url="http://localhost:8000/mcp",
    )

    assert profile.header_references == ()            