# MCP Details Learning Project — Part 2F Context

**Date:** 2026-09-19

## Current Project Status

Parts 1 through 2E are complete.

Part 2E added and closed the project's second initial transport:

- STDIO
- Streamable HTTP

The final regression baseline at Part 2E closure is:

```text
84 passed
0 failed

Python compilation and all focused/final verification commands also pass.

Project Goal

MCP Details is a general-purpose, strictly read-only MCP inspection
application.

A user researches an MCP server, supplies explicit connection information,
connects through a supported transport, and receives a detailed inspection
report describing the MCP server without executing its capabilities.

The initial transports are:

STDIO
Streamable HTTP

The architecture should remain open to additional transports when concrete
requirements justify them.

The application remains strictly discovery/inspection oriented.

It must not become an MCP workflow/execution client.

Development Method

Continue using the established teaching and implementation contract:

Architecture before implementation.
Explain architectural reasoning before proposing code.
Use extremely small, highly testable milestones.
Preserve existing behavior unless a deliberate architectural change is
explicitly approved.
Compile after every implementation milestone.
Run focused tests after each implementation milestone.
Run the full regression suite after each completed milestone.
Stop after every checkpoint.
Separate architectural decisions from implementation details.
Distinguish high-value contracts from low-value implementation details.
Avoid speculative abstractions.
Inspect the actual repository and installed SDK rather than assuming APIs
or project structure.
Prefer the installed MCP SDK 2.1.1 behavior as authoritative for this
project.
Environment

Current environment:

Python 3.12.7
MCP Python SDK 2.1.1
pytest 9.1.1
anyio 4.14.2
Windows development environment
project virtual environment: .venv

Project root:

C:\AI_Projects\mcp_details_learning_project
Major Closed Architectural Boundaries
Profiles

Project-owned explicit connection profiles are used instead of exposing SDK
runtime objects as configuration.

STDIO

StdioConnectionProfile contains:

display_name
command
immutable args
optional cwd
fixed transport="stdio"
Streamable HTTP

StreamableHttpConnectionProfile contains:

display_name
url
fixed transport="streamable_http"

Profile validation is structural.

Runtime connection validity is a separate concern.

Profiles are independent of any future persistence format.

Connection Boundary

STDIO requires meaningful translation:

StdioConnectionProfile
        ↓
build_stdio_server_parameters()
        ↓
StdioServerParameters
        ↓
Client

Minimal Streamable HTTP uses the SDK 2.1.1 URL contract directly:

StreamableHttpConnectionProfile
        ↓
profile.url
        ↓
Client(profile.url)

No HTTP builder was introduced because str -> str would not own meaningful
project behavior.

The asymmetry is intentional.

No generic connection manager, connection factory, transport registry, or
project-owned MCP connection façade currently exists.

Application Composition

The application exposes transport-specific composition functions:

inspect_stdio_profile(...)
inspect_streamable_http_profile(...)

Each transport-specific function:

creates a safe InspectionTargetSummary;
performs transport-specific Client construction; and
delegates the shared connected-client lifecycle.

A private helper now owns the common lifecycle:

async def _inspect_client(
    client: Client,
    target: InspectionTargetSummary,
) -> ApplicationInspectionResult:

Conceptually:

transport-specific profile
        ↓
transport-specific Client construction
        ↓
_inspect_client()
        ↓
enter Client
        ↓
inspect_mcp()
        ↓
exit Client
        ↓
ApplicationInspectionResult

The shared helper does not accept profiles and does not dispatch on transport.

Safe Target Summary

Operational connection profiles do not flow into the result or presentation
layers.

Instead, application composition creates:

InspectionTargetSummary
    display_name
    transport

This represents safe configured-target identity for reporting.

It is not used to establish the connection or drive inspection.

The full profile may contain operational or eventually sensitive connection
information and therefore should not automatically flow into result or
presentation boundaries.

Configured target identity remains distinct from server-reported identity.

Inspection Boundary

Inspection remains transport-neutral.

The central contract remains conceptually:

inspect_mcp(client)

The Client is already connected when inspection begins.

Inspection does not know whether the Client was connected through:

STDIO
Streamable HTTP
any future transport

The addition of Streamable HTTP required no transport-specific redesign of
the inspection subsystem.

Inspection supports:

server description;
tools;
static resources;
resource templates; and
prompts.

It respects advertised server capabilities, exhausts pagination, preserves
partial results, and keeps category failures independent.

Result Model

Important project-owned result types include:

ServerDescription
InspectionStatus
CategoryInspection[T]
MCPInspectionResult
InspectionTargetSummary
ApplicationInspectionResult

InspectionStatus distinguishes:

NOT_ADVERTISED
SUCCESS
PARTIAL
FAILED

SDK semantic models are intentionally preserved where they are legitimate
public semantic dependencies.

The project does not clone SDK models merely to eliminate SDK type exposure.

Presentation Boundary

Presentation remains pure:

ApplicationInspectionResult
        ↓
render_report()
        ↓
str

Presentation must not:

connect;
reconnect;
inspect;
paginate;
own SDK lifecycle;
execute MCP operations; or
understand transport mechanics.

The terminal report covers:

configured target identity;
server identity and negotiated information;
server capabilities;
tools;
resources;
resource templates;
prompts;
nested task capabilities;
experimental capabilities; and
extension capabilities.

Experimental and extension evidence is preserved/rendered without speculative
semantic interpretation.

Strict Read-Only Policy

MCP Details is an inspection application.

It does not execute discovered capabilities.

The inspection path must not introduce operations such as:

call_tool()
read_resource()
resource-template materialization
workflow execution

The distinction between discovery and execution is a foundational project
boundary.

Real Integration Evidence

Both initial transports now have real SDK integration evidence.

STDIO

The existing integration fixture uses:

tests/support/minimal_stdio_server.py

and proves:

StdioConnectionProfile
        ↓
real SDK Client
        ↓
real STDIO subprocess
        ↓
real MCP negotiation
        ↓
inspect_mcp()
        ↓
ApplicationInspectionResult
Streamable HTTP

Part 2E added:

tests/support/minimal_streamable_http_server.py

The server uses MCP SDK 2.1.1 MCPServer and
run_streamable_http_async().

The real integration test proves:

StreamableHttpConnectionProfile
        ↓
inspect_streamable_http_profile()
        ↓
real SDK Client
        ↓
real Streamable HTTP
        ↓
real MCPServer/Uvicorn
        ↓
real MCP negotiation
        ↓
inspect_mcp()
        ↓
ApplicationInspectionResult

The HTTP integration test dynamically selects an available localhost port,
waits for server readiness, and terminates the server subprocess safely.

Part 2E Test Baseline

At Part 2E closure:

tests/test_application.py
6 passed

Full suite:

84 passed
0 failed

The final closure verification commands were:

python -m compileall src\mcp_details tests
python -m pytest tests\test_profiles.py -v
python -m pytest tests\test_application.py -v
python -m pytest -v

All passed.

Part 2E Architectural Decisions

The Architectural Decision Ledger has been updated through AD-050.

Important recent decisions include:

AD-049 — Use the SDK Client URL Contract Directly for Minimal Streamable HTTP

For the initial unauthenticated HTTP path, pass the resolved URL directly to
the SDK Client.

Do not introduce an HTTP target builder, connection wrapper, factory,
registry, or strategy while no meaningful additional construction behavior
exists.

AD-050 — Share Application Lifecycle Only After Transport-Specific Client Construction

Transport-specific entry points construct their respective SDK Clients.

Only after Client construction does execution converge on the private shared
application lifecycle helper.

This keeps transport-specific construction explicit while preserving
transport-neutral inspection.

Deferred Territory

Part 2E intentionally does not implement:

HTTP authentication;
OAuth;
API keys;
custom HTTP headers;
credential resolution;
custom HTTP clients;
timeout configuration;
TLS customization;
proxy configuration;
SSE;
additional transports;
a generic connection factory;
a generic profile hierarchy;
a generic transport dispatcher;
profile persistence; or
a user-facing CLI/profile-input mechanism.

These are not defects in Part 2E.

They should be introduced only when a concrete project requirement justifies
them.

Why the Next Review Is Likely an Application-Entry Review

The internal pipeline now exists:

explicit profile
        ↓
transport-specific connection construction
        ↓
SDK Client
        ↓
inspection
        ↓
structured results
        ↓
presentation

However, the larger application goal is that a user can research an MCP,
provide explicit connection information, run MCP Details, and receive the
report.

Therefore the next major architectural question is likely:

How should a real user invoke the completed inspection pipeline and provide
the resolved target configuration?

Possible territory may include:

application entry point;
terminal invocation;
user input;
profile selection/construction;
transport selection;
sequencing inspection and presentation; and
application-level failure reporting.

Do not assume that all of these belong in the next milestone.

Do not begin by designing a large CLI framework.

First inspect the actual current repository and determine what application
entry/composition mechanisms already exist.

Part 2F Starting Objective

Begin Part 2F with an architectural review rather than implementation.

The first objective is:

Review the complete MCP Details architecture after Part 2E and determine
whether the application-entry/user-invocation boundary is the correct next
subsystem.

Before proposing production code:

Review the actual repository structure.
Review the current public/application entry points.
Identify whether any terminal/CLI entry mechanism already exists.
Reconstruct the current complete data/control flow.
Identify the remaining gap between the existing Python composition API and
a user-operable MCP Details application.
Separate user-input concerns from profile, connection, inspection, result,
and presentation responsibilities.
Determine the smallest useful next milestone.
Do not introduce a CLI framework, generic profile dispatcher, persistence
model, or configuration format until a concrete need is demonstrated.

Part 2E is closed and should not be redesigned unless Part 2F discovers a
genuine architectural contradiction.