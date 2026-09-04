
"""Structured inspection result models for MCP Details."""

from dataclasses import dataclass
from enum import Enum
from typing import Generic, TypeVar

from mcp.types import Implementation, ServerCapabilities


PageT = TypeVar("PageT")


class InspectionStatus(Enum):
    """Completion state for one MCP inspection category."""

    NOT_ADVERTISED = "not_advertised"
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


@dataclass(frozen=True)
class CategoryInspection(Generic[PageT]):
    """Structured evidence captured while inspecting one MCP category."""

    status: InspectionStatus
    pages: tuple[PageT, ...]
    failure: Exception | None = None


@dataclass(frozen=True)
class ServerDescription:
    """Negotiated descriptive information about an MCP server."""

    protocol_version: str
    server_info: Implementation | None
    server_capabilities: ServerCapabilities
    instructions: str | None

