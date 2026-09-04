# MCP Details Learning Project
# Part 2C Context — Inspection Boundary Architectural Review

**Context date:** 2026-08-30  
**Previous milestone:** Part 2B — Minimal STDIO Connection Boundary  
**Regression baseline:** 15 passing tests

---

## 1. Project purpose

MCP Details is a learning project for building a general-purpose,
strictly non-executing MCP inspection application.

The intended user workflow is:

```text
research/configure MCP server
        ↓
explicit connection profile
        ↓
connect through supported transport
        ↓
inspect server metadata and discoverable capabilities
        ↓
produce structured inspection result
        ↓
present result

The application is not intended to execute the functionality exposed by the
server.

## 2. Strict non-execution policy

MCP Details may inspect discoverable MCP metadata and capability declarations.

It must not perform operations that execute server functionality or retrieve
capability content merely for demonstration.

Explicitly prohibited application operations include:

call_tool()
read_resource()
get_prompt()

The intended discovery scope includes:

server initialization / negotiated metadata
server name/version
protocol information
server capabilities
list_tools()
list_resources()
list_resource_templates()
list_prompts()

The distinction is:

discover what exists
        YES

execute/use what exists
        NO
## 3. Part 1 architecture foundation

Part 1 established the following architectural direction:

use MCP Python SDK 2.x,
architect around the high-level v2 Client,
let the SDK own protocol negotiation,
support STDIO and Streamable HTTP initially,
remain open to additional transports later,
use explicit project-owned connection profiles,
translate profiles to SDK runtime configuration at the connection boundary,
keep inspection transport-neutral after connection,
perform capability-aware discovery,
perform pagination-complete discovery,
preserve partial evidence when practical,
keep structured inspection results separate from presentation,
keep the composition root thin,
avoid capability-specific workflow modules,
avoid speculative abstractions.

## 4. Important architectural decisions from Part 1

Relevant decisions include:

AD-032

Use project-owned resolved connection profiles and translate them into SDK
runtime configuration.

AD-033

Connection profiles have explicit transport identity.

AD-034

STDIO and Streamable HTTP use structurally distinct profile variants.

AD-035

The conceptual STDIO profile includes:

display name,
transport,
command,
arguments,
environment configuration,
optional working directory.

SDK-specific controls are deferred unless needed.

AD-036

Credentials should be represented through references rather than embedded
secrets.

Initial credential references may resolve through environment variables.

Resolution should occur near connection construction.

Secrets must not leak into inspection results or presentation.

AD-037

Structural profile validity and runtime connection validity are distinct.

AD-038

Raw connection profiles and safe inspection-target summaries are distinct.

AD-039

Profile semantics are independent of JSON/YAML/TOML serialization format.

AD-040

Profile, connection, inspection, result, presentation, and composition are
distinct responsibilities.

AD-041

Project connection profiles remain independent of MCP SDK runtime objects.

AD-042

The connection layer owns profile-to-SDK translation and may eventually own
credential resolution.

AD-043

Inspection is transport-neutral after connection.

AD-044

Inspection is independent of presentation.

AD-045

Direct MCP SDK dependencies are allowed where semantically appropriate.

AD-046

Do not create capability-specific workflow modules.

AD-047

Keep the composition root thin.

## 5. Part 2A completed work

Part 2A established the minimal project skeleton.

Current production package:

src/
└── mcp_details/
    ├── __init__.py
    ├── profiles.py
    └── connection.py

The project uses a src-layout package.

pyproject.toml defines:

distribution name: mcp-details
Python package:    mcp_details

The project currently declares:

dependencies = [
    "mcp==2.1.1",
]

and:

[project.optional-dependencies]
test = [
    "pytest",
]

## 6. Current STDIO profile

src/mcp_details/profiles.py currently contains:

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

The model is deliberately immutable.

Arguments use a tuple because the profile represents stable project-owned
connection intent rather than mutable SDK runtime configuration.

Environment configuration and credential references remain deferred.

## 7. Current connection boundary

src/mcp_details/connection.py currently contains:

"""MCP SDK connection-target construction for MCP Details."""

from mcp import StdioServerParameters

from mcp_details.profiles import StdioConnectionProfile


def build_stdio_server_parameters(
    profile: StdioConnectionProfile,
) -> StdioServerParameters:
    """Translate a project-owned STDIO profile into MCP SDK parameters."""
    return StdioServerParameters(
        command=profile.command,
        args=list(profile.args),
        cwd=profile.cwd,
    )

Its responsibility is intentionally narrow:

StdioConnectionProfile
        ↓
build_stdio_server_parameters()
        ↓
StdioServerParameters

No Client builder or custom lifecycle wrapper currently exists.

## 8. Part 2B Client/lifecycle conclusion

The MCP Python SDK v2 high-level Client already owns the runtime connection
lifecycle needed by the current project.

The proven path is:

StdioServerParameters
        ↓
Client(parameters)
        ↓
async with client
        ↓
STDIO subprocess
        ↓
MCP negotiation
        ↓
connected Client

MCP Details currently does not need:

MCPConnection
ConnectionManager
build_stdio_client()
open_connection()
manual stdio_client()
manual ClientSession
manual initialize()

These abstractions should not be added unless a future project-owned policy
creates a real need.

## 9. Real STDIO integration proof

Part 2B added:

tests/
└── support/
    └── minimal_stdio_server.py

and:

tests/test_stdio_connection.py

The integration test proves:

StdioConnectionProfile
        ↓
production translation function
        ↓
StdioServerParameters
        ↓
high-level Client
        ↓
real subprocess
        ↓
real STDIO
        ↓
real MCP negotiation
        ↓
known connected server

The test verifies connection-level negotiated evidence such as:

server_info
protocol_version
server_capabilities

The integration test does not perform capability discovery.

## 10. Current test architecture

Current tests:

tests/
├── support/
│   └── minimal_stdio_server.py
├── test_package_import.py
├── test_profiles.py
├── test_connection.py
└── test_stdio_connection.py

Current full regression baseline:

15 passing tests

## 11. Important boundary entering Part 2C

Part 2C should begin conceptually from:

ALREADY CONNECTED
high-level MCP Client
        ↓
?????????
        ↓
structured inspection evidence

Part 2C should not redesign the STDIO profile or connection lifecycle unless
the inspection review exposes a genuine architectural problem.

Inspection should not establish its own connection.

Inspection should not care whether the connected Client originated from:

STDIO
Streamable HTTP
future transport

The transport boundary should already have disappeared by the time inspection
begins.

## 12. Part 2C primary architectural question

Determine:

Given an already-connected high-level MCP Client, what is the smallest,
correct, transport-neutral inspection boundary for MCP Details?

Architecture must be reviewed before implementation.

## 13. Inspection scope to review

The eventual inspection scope includes:

negotiated server metadata
server identity/version
protocol information
server capabilities

tools
resources
resource templates
prompts

Part 2C should determine which of these belong in the first milestone rather
than implementing everything immediately.

## 14. Capability-aware discovery requirement

Inspection should not blindly assume every server exposes every capability.

Part 2C must determine:

how negotiated capabilities affect discovery,
whether capability declarations are authoritative enough to skip unsupported
list operations,
how optional capability absence should be represented,
whether capability-aware policy belongs in inspection rather than connection.

Do not implement a policy until the current SDK v2 behavior and types have
been reviewed.

## 15. Pagination-complete discovery requirement

Part 1 established that discovery should be pagination-complete.

Part 2C must review the current MCP Python SDK v2 pagination model before
implementation.

Questions include:

whether high-level Client list operations automatically aggregate pages,
whether cursors remain visible to callers,
whether MCP Details must explicitly iterate,
where pagination policy belongs,
what termination conditions should be protected.

Do not assume behavior from the previous MCP Client Learning Project or MCP
SDK v1.x.

## 16. Partial evidence requirement

Part 1 established the preference to preserve authoritative evidence already
obtained when later inspection operations fail.

Conceptually:

connection succeeds

server metadata captured

tools discovery succeeds

resources discovery fails

prompts discovery succeeds

MCP Details should eventually consider whether the successful evidence should
remain available rather than being discarded because one discovery operation
failed.

Part 2C should review this requirement before deciding the first result model.

## 17. Result-model boundary

Inspection behavior and presentation must remain separate.

Avoid designs where inspection directly prints output.

Conceptually:

connected Client
        ↓
inspection
        ↓
structured result
        ↓
presentation

Part 2C should determine the smallest useful project-owned result/DTO needed
for the first inspection milestone.

Do not build the complete final InspectionResult prematurely.

Derived truths should preferably be computed from authoritative stored facts
rather than independently stored when practical.

## 18. Strict non-execution boundary

The inspection subsystem must never evolve into demo workflows resembling the
previous MCP Client Learning Project.

Do not create modules such as:

tool_workflow.py
resource_workflow.py
prompt_workflow.py

MCP Details is an inspector, not a capability-execution demonstration client.

Allowed discovery operations may include:

list_tools()
list_resources()
list_resource_templates()
list_prompts()

Prohibited operations include:

call_tool()
read_resource()
get_prompt()

This distinction should be explicit in the architecture.

## 19. Connection failures remain deferred

Part 2B intentionally did not define project-owned connection failure
semantics.

Possible future representations include:

project-owned exceptions,
structured failure DTOs,
inspection-result failure fields,
composition-level handling,
or a combination.

Do not freeze incidental SDK exception types into the MCP Details contract
without first determining what failure distinctions the application actually
needs.

The Part 2C inspection/result review may provide useful information for this
future decision.

## 20. Other intentionally deferred connection territory

The following remain outside the immediate Part 2C inspection review unless
they become directly relevant:

Streamable HTTP profile implementation
environment configuration
credential references/resolution
connection failure normalization
generic connection dispatcher
custom lifecycle wrapper
configuration file parsing
presentation formatting
CLI/application entrypoint

## 21. Teaching contract

Continue using the established learning-project method:

architecture before implementation,
professor/software-architect style,
explain why before code,
extremely small milestones,
preserve intended behavior,
compile after implementation changes,
focused tests after each milestone,
full regression after each milestone,
stop after every checkpoint,
separate architectural decisions from implementation,
avoid speculative abstractions,
do not copy old MCP SDK v1.x architecture into the v2 project.
## 22. Recommended Part 2C starting sequence

Begin with an architectural review rather than implementation.

Recommended sequence:

Part 2C.1
Current high-level Client inspection API review

        ↓

Part 2C.2
Transport-neutral inspection responsibility review

        ↓

Part 2C.3
Capability-aware discovery policy review

        ↓

Part 2C.4
Pagination-completeness review

        ↓

Part 2C.5
Smallest structured inspection-result boundary

        ↓

Part 2C.A
First implementation milestone

The exact sequence may be revised if current MCP SDK 2.1.1 behavior suggests a
better decomposition.

## 23. Starting instruction for Part 2C

Do not begin by implementing all four discovery operations.

First inspect the current MCP Python SDK 2.1.1 high-level Client API and
determine:

what negotiated metadata is directly available,
what discovery operations exist,
how capability declarations relate to those operations,
how pagination works,
what data types the SDK returns,
what information MCP Details should preserve in project-owned results,
what the smallest high-value first inspection milestone should be.

Architecture review must precede production code.