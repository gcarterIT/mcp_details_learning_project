
"""Structured inspection result models for MCP Details."""

from dataclasses import dataclass
from enum import Enum
from typing import Generic, TypeVar

from mcp.types import Implementation, ServerCapabilities


PageT = TypeVar("PageT")

@dataclass(frozen=True)
class ServerDescription:
    """Negotiated descriptive information about an MCP server."""

    protocol_version: str
    server_info: Implementation | None
    server_capabilities: ServerCapabilities
    instructions: str | None


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


from mcp.types import (
    ListPromptsResult,
    ListResourcesResult,
    ListResourceTemplatesResult,
    ListToolsResult,
)

@dataclass(frozen=True)
class MCPInspectionResult:
    server_description: ServerDescription
    tools: CategoryInspection[ListToolsResult]
    resources: CategoryInspection[ListResourcesResult]
    resource_templates: CategoryInspection[ListResourceTemplatesResult]
    prompts: CategoryInspection[ListPromptsResult]

@dataclass(frozen=True)
class InspectionTargetSummary:
    """Safe project-owned identity for the target being inspected."""

    display_name: str
    transport: str


@dataclass(frozen=True)
class ApplicationInspectionResult:
    """Complete application result for one inspected MCP target."""

    target: InspectionTargetSummary
    inspection: MCPInspectionResult