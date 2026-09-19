# Part 2E Context — Streamable HTTP Transport Architectural Review

## Project

MCP Details Learning Project

Project root:

`C:\AI_Projects\mcp_details_learning_project`

## Current Date

2026-09-16

## Current Project Status

Parts 1 through 2D are complete.

The current application supports complete strictly read-only inspection
of an MCP server through the STDIO transport and renders the resulting
structured evidence as a human-readable terminal report.

The STDIO path has been verified through:

- unit tests;
- integration tests;
- a real MCP STDIO subprocess;
- real MCP negotiation;
- real capability-aware inspection;
- real primitive inventory discovery;
- manual end-to-end terminal acceptance testing.

Final regression baseline entering Part 2E:

- 23 presentation tests passing;
- 74 total project tests passing;
- 0 failures.

## Project Goal

Build a general-purpose, strictly read-only MCP inspection application.

The intended initial transport scope is:

1. STDIO;
2. Streamable HTTP.

The architecture should remain open to additional transports later, but
additional transport abstractions must not be introduced speculatively.

## Read-Only Policy

The application may perform MCP negotiation and discovery/list
operations required for inspection.

It must not:

- execute tools;
- read resource contents;
- materialize resource templates;
- execute/use prompts.

The purpose of the application is inspection and discovery, not MCP
workflow execution.

## Environment

Current confirmed environment:

- Python 3.12.7;
- pytest 9.1.1;
- anyio 4.14.2;
- MCP Python SDK 2.1.1;
- Windows development environment;
- project virtual environment `.venv`.

## Current Architecture

The current dependency direction is conceptually:

```text
profiles
   ↓
connection
   ↓
application composition
   ↓
inspection
   ↓
structured results
   ↓
presentation

For the completed STDIO path:

StdioConnectionProfile
        ↓
build_stdio_server_parameters()
        ↓
MCP SDK Client
        ↓
real STDIO connection / MCP negotiation
        ↓
inspect_mcp()
        ↓
MCPInspectionResult
        ↓
ApplicationInspectionResult
        ↓
render_report()
        ↓
str
Current Major Modules

The package currently contains:

src/mcp_details/__init__.py;
src/mcp_details/profiles.py;
src/mcp_details/connection.py;
src/mcp_details/inspection.py;
src/mcp_details/results.py;
src/mcp_details/application.py;
src/mcp_details/presentation.py.

There is currently no requirement to introduce a CLI or __main__.py.

Connection Profile Boundary

The currently implemented concrete profile is:

StdioConnectionProfile

Its established minimal contract includes:

display_name;
command;
immutable args: tuple[str, ...];
optional cwd;
fixed STDIO transport identity.

Profiles represent explicit user-supplied connection configuration.

Do not assume that an MCP server name or repository identifier alone is
sufficient connection information.

Connection Boundary

The current STDIO connection helper translates project-owned profile
configuration into MCP SDK connection parameters.

Conceptually:

StdioConnectionProfile
        ↓
build_stdio_server_parameters()
        ↓
StdioServerParameters

The MCP SDK owns transport mechanics.

The project should not reproduce SDK transport implementation details.

Application Composition Boundary

The completed STDIO application operation is:

inspect_stdio_profile(profile) -> ApplicationInspectionResult

Its responsibility is to:

create the configured-target summary;
translate the STDIO profile;
construct the SDK Client;
own the Client lifetime scope;
invoke the transport-neutral inspection boundary;
return the application-level result.

The application owns Client lifetime scope.

The MCP SDK owns lifecycle mechanics.

Inspection Boundary

inspect_mcp() operates on an already-connected MCP SDK v2 Client.

It is transport-neutral.

The inspection boundary must not know whether the Client was connected
through STDIO or Streamable HTTP.

Inspection currently covers:

server description;
tools;
static resources;
resource templates;
prompts.

Primitive inspection respects advertised capabilities.

Complete inventory inspection exhausts pagination.

Partial pagination failures preserve successfully retrieved pages.

Primitive categories fail independently.

Structured Results

Current important project-owned result models include:

ServerDescription

Retains:

protocol version;
server info;
server capabilities;
instructions.
InspectionStatus

Values:

NOT_ADVERTISED;
SUCCESS;
PARTIAL;
FAILED.
CategoryInspection[T]

Retains:

status;
immutable pages;
optional failure.
MCPInspectionResult

Aggregates:

server description;
tools;
resources;
resource templates;
prompts.
InspectionTargetSummary

Retains presentation-safe configured-target identity:

display name;
transport.

It intentionally does not retain:

command;
args;
cwd;
raw profile;
SDK Client;
credentials.
ApplicationInspectionResult

Combines:

configured target summary;
MCP inspection result.

There is intentionally no aggregate overall inspection status.

Presentation Boundary

Part 2D.2 is formally closed.

The presentation contract is:

ApplicationInspectionResult -> render_report() -> str

Presentation:

does not reconnect;
does not inspect;
does not own Client lifecycle;
does not perform pagination;
does not execute MCP operations;
does not depend on transport mechanics.

All retained server-description evidence and all four primitive
inventories are currently represented in the terminal report.

Primitive renderers remain explicit and SDK-shape-aware.

Server Capability Presentation

Known MCP SDK 2.1.1 capability structures currently rendered include:

logging;
prompts;
resources;
tools;
completions;
tasks;
experimental;
extensions.

Capability advertisement and primitive inspection status remain
independent authoritative evidence.

Optional boolean capability details preserve True, False, and
None.

Open experimental and extension structures are preserved as JSON
without application-level semantic interpretation.

Manual End-to-End STDIO Acceptance

Part 2D.2C.5 added manual test-support components:

tests/support/presentation_demo_stdio_server.py;
tests/support/run_presentation_demo.py.

These are test/support infrastructure, not production application
interfaces.

The manual runner exercises:

StdioConnectionProfile
        ↓
inspect_stdio_profile()
        ↓
real SDK Client
        ↓
real STDIO subprocess
        ↓
MCP negotiation
        ↓
inspect_mcp()
        ↓
ApplicationInspectionResult
        ↓
render_report()
        ↓
terminal

The representative server exposes:

server identity/version;
instructions;
tools;
resources;
resource templates;
prompts and prompt arguments.

No tool execution, resource read, template materialization, or prompt
execution occurs.

Manual Acceptance Finding

The initial real acceptance run exposed a duplicate Tools section even
though the existing 74-test project regression baseline was green.

Diagnostic evidence established that the inspection result contained
exactly one tools page and one representative tool.

The defect was localized to render_report(), which accidentally
composed _render_tools(inspection.tools) twice.

The existing core report test protected category presence but not
top-level composition cardinality.

The existing composition test was strengthened to require exactly one
top-level section for each primitive category:

Tools;
Resources;
Resource Templates;
Prompts.

The strengthened test failed before the fix, proving that it detected
the observed defect.

The duplicate composition call was removed.

After correction:

focused composition test passed;
all 23 presentation tests passed;
real STDIO acceptance report was correct;
all 74 project tests passed.

This is the authoritative regression baseline entering Part 2E.

Important Existing Architectural Principles

Continue preserving these principles:

Architecture before implementation.
Explicit connection profiles.
Project-owned DTOs where they provide a meaningful project boundary.
Do not clone MCP SDK semantic models without a concrete need.
Derived truths should preferably be computed from authoritative
stored facts rather than independently stored.
Inspection of an already-connected Client remains transport-neutral.
Respect server-advertised capabilities.
Exhaust pagination for complete inventory inspection.
Preserve partial results on later-page failure.
Primitive categories fail independently.
Distinguish unsupported, empty, populated, partial, and failed
inspection states.
Configured target identity and server-reported identity are separate
authoritative facts.
Application composition owns Client lifetime scope while the SDK
owns lifecycle mechanics.
Presentation consumes structured results and remains downstream of
inspection.
Primitive presentation renderers remain explicit and SDK-shape-aware.
Introduce shared abstractions only after genuinely shared semantics
have been demonstrated.
Top-level presentation composition is a behavioral contract, not
merely a presence check.
Manual acceptance evidence can reveal boundary-level defects not
exposed by isolated automated tests.
Part 2E Objective

Begin the architectural review for the second concrete transport:

Streamable HTTP

The purpose of Part 2E is not merely to make HTTP connectivity work.

The second transport provides the first concrete evidence needed to
review whether the existing profile, connection, and application
composition boundaries should remain transport-specific or gain a
carefully justified shared abstraction.

The architecture must not be generalized before examining the actual
MCP SDK 2.1.1 Streamable HTTP API and comparing its requirements with
the completed STDIO path.

Questions Part 2E Must Answer

Before implementation, determine:

What is the authoritative MCP SDK 2.1.1 API for connecting a
high-level Client through Streamable HTTP?
What connection information must a project-owned Streamable HTTP
profile retain?
Which fields are genuinely transport-specific?
Does the existing connection boundary require generalization?
Does application composition require a common transport-neutral
operation, or should concrete operations remain explicit?
Which parts of the current STDIO lifecycle are actually common
Client semantics versus STDIO-specific mechanics?
Can inspect_mcp() remain completely unchanged?
Can all existing structured-result and presentation boundaries remain
unchanged?
How should credentials, headers, authentication configuration, or
other potentially sensitive HTTP connection information be kept out
of presentation-safe target summaries?
What is the smallest safe Streamable HTTP milestone that can be
implemented and tested without speculative abstraction?
Constraints for Part 2E

Do not begin by inventing:

a generic ConnectionProfile hierarchy;
a transport registry;
a connection factory framework;
a strategy pattern;
a transport plugin architecture;
a generic lifecycle manager;
a generic application dispatcher.

First inspect the actual second transport.

Only introduce common abstractions when comparison of STDIO and
Streamable HTTP demonstrates a real shared contract.

Do not redesign the closed inspection, result, or presentation
boundaries unless Streamable HTTP reveals a concrete contradiction.

Development Method

Continue the established teaching and implementation contract:

architecture before implementation;
professor/software-architect style;
explain why before code;
extremely small, highly testable milestones;
preserve behavior exactly;
compile after every implementation;
run focused tests after each implementation;
run the full regression suite after each completed milestone;
stop after every checkpoint;
separate architectural decisions from implementation;
distinguish high-value contracts from low-value implementation
details;
avoid speculative abstractions.
Entry Baseline for Part 2E

Part 2E begins with:

STDIO transport complete;
application composition complete for STDIO;
transport-neutral inspection complete;
structured result boundary complete;
terminal presentation complete and formally closed;
manual real STDIO acceptance complete;
74 total tests passing;
0 failures.

The first Part 2E activity should be architectural and SDK-contract
review only.

Do not write production Streamable HTTP code until that review is
complete.