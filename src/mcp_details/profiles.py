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
    transport: Literal["stdio"] = field(default="stdio", init=False)

    def __post_init__(self) -> None:
        """Validate the minimal structural requirements of a STDIO profile."""
        if not self.display_name.strip():
            raise ValueError("display_name must not be blank")

        if not self.command.strip():
            raise ValueError("command must not be blank")
            
@dataclass(frozen=True)
class StreamableHttpConnectionProfile:
    """Project-owned configuration describing a Streamable HTTP MCP connection."""

    display_name: str
    url: str
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