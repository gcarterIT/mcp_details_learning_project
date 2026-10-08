MCP Details Learning Project — Part 2G Context
Purpose of This Context

This file provides the authoritative transition context from the completed Part 2F Application Entry Boundary into Part 2G.

Part 2G should begin with a post-entry remaining-territory architectural review.

Do not assume that the next step is implementation.

The first objective is to compare the original MCP Details project goals against the architecture and behavior that now exist, identify meaningful remaining gaps, and determine the smallest justified next architectural milestone.

Project

MCP Details Learning Project

Project root:

C:\AI_Projects\mcp_details_learning_project

The project is separate from the earlier MCP Client Learning Project.

Environment

Verified project environment:

Python 3.12.7
MCP Python SDK 2.1.1
pytest 9.1.1
anyio 4.14.2

Primary development shell:

Windows PowerShell
Project Goal

MCP Details is intended to be a general-purpose, strictly read-only MCP inspection application.

A user first researches an MCP server and obtains explicit connection information.

The application then connects to that server through a supported transport and reports MCP discovery/inspection information.

The project does not attempt to infer connection information from an arbitrary server identifier.

Read-Only Policy

The application is strictly inspection/discovery oriented.

It may inspect:

server identity and version;
negotiated protocol version;
server capabilities;
server instructions;
tools;
resources;
resource templates;
prompts;
descriptions;
tool input schemas;
prompt argument information;
pagination;
experimental/extension capabilities.

It must not perform MCP workflows.

In particular, the project does not use inspection as justification to:

execute tools;
read resources for workflow purposes;
materialize resource templates;
execute/get prompts for workflow purposes;
perform arbitrary MCP actions.
Supported Transports

The currently supported transports are:

STDIO
Streamable HTTP

The architecture remains open to additional transports if future requirements justify them.

Architectural Pipeline

The completed architecture is conceptually:

explicit user invocation
        |
        v
application entry boundary
        |
        v
explicit concrete connection profile
        |
        v
transport-specific MCP SDK Client construction
        |
        v
shared Client lifecycle
        |
        v
transport-neutral read-only inspection
        |
        v
structured project-owned results
        |
        v
pure terminal presentation
        |
        v
stdout
Completed Work
Part 1 — Architecture Foundation

Completed.

Major principles established included:

research/discovery of connection information is separate from MCP protocol connection;
arbitrary MCP identifiers are not assumed to contain sufficient connection information;
connection profiles are explicit and project-owned;
inspection remains strictly read-only;
transport mechanics are separated from transport-neutral MCP inspection;
terminal presentation is initially sufficient but the architecture should remain adaptable.
Part 2A — Minimal Skeleton and STDIO Profile

Implemented the initial project structure and:

StdioConnectionProfile

Important profile fields:

display_name
command
args
cwd
transport = "stdio"

STDIO arguments use an immutable tuple at the project configuration boundary.

Structural validation rejects blank required values.

Part 2B — STDIO Connection Boundary

Implemented translation from:

StdioConnectionProfile

to MCP SDK:

StdioServerParameters

Real STDIO subprocess connection and MCP negotiation were verified.

Part 2C — Transport-Neutral Inspection

Implemented the transport-neutral inspection boundary.

Important result types include:

ServerDescription
InspectionStatus
CategoryInspection[T]
MCPInspectionResult

Inspection statuses include:

NOT_ADVERTISED
SUCCESS
PARTIAL
FAILED

The inspection architecture:

respects server-advertised capabilities;
exhausts paginated primitive inventories;
preserves successfully retrieved pages if a later page fails;
keeps primitive-category failures independent;
preserves MCP SDK semantic models rather than unnecessarily cloning them;
distinguishes unsupported/unadvertised categories from successful empty inventories;
remains strictly read-only.

A shared private pagination helper supports tools, resources, resource templates, and prompts.

Part 2D.1 — Application Composition

Implemented application-level composition.

Important operations include:

inspect_stdio_profile(...)
inspect_streamable_http_profile(...)

Application composition returns:

ApplicationInspectionResult

Configured target identity remains separate from server-reported identity through:

InspectionTargetSummary

The safe target summary intentionally avoids preserving sensitive connection details in inspection results.

Part 2D.2 — Terminal Presentation Boundary

Implemented:

ApplicationInspectionResult
        ->
render_report()
        ->
str

Presentation remains pure.

It does not reconnect to MCP servers or own SDK lifecycle.

The report covers:

configured target;
server identity;
protocol version;
server capabilities;
instructions;
tools;
resources;
resource templates;
prompts;
pagination-derived inventory;
partial and failed inspection evidence;
nested task capabilities;
experimental/extension capabilities.

Manual acceptance during Part 2D discovered a duplicate Tools section defect.

The defect was fixed and protected by a composition test.

Part 2E — Streamable HTTP Transport

Added:

StreamableHttpConnectionProfile

Important fields:

display_name
url
transport = "streamable_http"

For the current minimal unauthenticated Streamable HTTP contract, application composition uses the MCP Python SDK v2 Client URL contract directly:

Client(profile.url)

No unnecessary project-owned HTTP transport wrapper, factory, strategy hierarchy, or generic transport abstraction was introduced.

STDIO and Streamable HTTP construct their Clients differently but share the connected Client lifecycle after construction.

Both transports have real MCP integration evidence.

Part 2E closed with:

84 tests passed
0 failures
Part 2F — Application Entry Boundary

Part 2F is complete.

Its purpose was to provide a user/process-facing execution boundary without contaminating the existing application, inspection, result, or presentation layers with command-line/process concerns.

The initial executable interface is:

python -m mcp_details ...
Entry Architecture

Part 2F introduced:

src/mcp_details/entry.py
src/mcp_details/__main__.py

The resulting execution path is:

PowerShell
        |
        v
python -m mcp_details
        |
        v
__main__.py
        |
        v
entry.py
        |
        +-- command-line parsing
        +-- explicit transport selection
        +-- CLI values -> concrete connection profile
        +-- synchronous -> asynchronous execution bridge
        +-- successful report -> stdout
        |
        v
application.py
        |
        v
inspection.py
        |
        v
structured results
        |
        v
presentation.py
        |
        v
terminal report
Terminal Commands
Streamable HTTP
python -m mcp_details streamable-http --name NAME --url URL
STDIO
python -m mcp_details stdio --name NAME --command COMMAND [--cwd PATH] [-- SERVER_ARG ...]

The -- delimiter establishes the ownership boundary between MCP Details arguments and opaque ordered arguments belonging to the target STDIO server.

Entry Boundary Responsibilities

entry.py owns:

argparse-based command parsing;
explicit transport selection;
CLI-to-profile adaptation;
routing to existing transport-specific application operations;
the synchronous-to-asynchronous bridge;
successful stdout delivery.

It does not own MCP transport implementation or MCP inspection semantics.

Concrete Profiles Remain Authoritative

CLI values are adapted directly into:

StdioConnectionProfile
StreamableHttpConnectionProfile

No additional generic CLI configuration DTO was introduced.

No generic profile hierarchy was introduced.

No generic transport registry or dispatcher was introduced.

Synchronous-to-Asynchronous Bridge

The terminal-facing process begins synchronously.

MCP Client lifecycle and inspection remain asynchronous.

Part 2F established one outer bridge:

asyncio.run(...)

Conceptually:

SYNCHRONOUS

python -m mcp_details
        |
        v
main()
        |
        v
run()
        |
        v
asyncio.run(...)

---------------- boundary ----------------

ASYNCHRONOUS

_run_parsed_arguments()
        |
        v
inspect_and_render_...()
        |
        v
inspect_*_profile()
        |
        v
async with Client(...)
        |
        v
await inspect_mcp(...)

Lower application and inspection layers do not own event-loop creation.

Failure Semantics

Part 2F intentionally keeps initial process-failure semantics simple.

Invalid command syntax

Owned by:

argparse

Invalid syntax produces a nonzero process outcome.

Runtime failure before a valid result exists

Runtime exceptions currently propagate.

No broad:

except Exception

translation policy was added.

Friendly project-owned runtime error presentation remains deferred until a meaningful exception taxonomy exists.

Inspection category failure

Statuses such as:

PARTIAL
FAILED
NOT_ADVERTISED

inside a valid inspection result remain inspection evidence.

They do not automatically mean that application execution itself failed.

A valid result continues through report rendering.

Part 2F Manual Acceptance
STDIO

Real terminal invocation was successfully verified using:

python -m mcp_details stdio --name "Manual STDIO Demo" --command python -- tests/support/minimal_stdio_server.py

The real path successfully covered:

terminal
-> module entry
-> parsing
-> STDIO profile
-> SDK Client
-> subprocess MCP server
-> MCP negotiation
-> inspection
-> presentation
-> stdout

The report correctly distinguished configured target identity from server-reported identity.

The minimal STDIO server did not advertise the primitive capabilities, and those categories were correctly represented as:

NOT_ADVERTISED
Streamable HTTP

A real local Streamable HTTP MCP server was started and the application was successfully invoked using:

python -m mcp_details streamable-http --name "Manual HTTP Demo" --url "http://127.0.0.1:8765/mcp"

The complete real path succeeded:

terminal
-> module entry
-> parsing
-> HTTP profile
-> synchronous/asynchronous bridge
-> SDK Client(URL)
-> real Streamable HTTP connection
-> MCP negotiation
-> inspection
-> presentation
-> stdout

The report correctly distinguished configured target identity from server-reported identity.

The HTTP server advertised tools, resources, and prompts.

The empty inventories were correctly represented as:

SUCCESS

rather than:

NOT_ADVERTISED

This provided end-to-end confirmation of the inspection status semantics through the user-facing application boundary.

Final Part 2F Verification Baseline

Final compile command:

python -m compileall src\mcp_details tests

Result:

PASS

Final full regression command:

python -m pytest -v

Result:

96 passed in 5.99s
0 failures

The suite includes 12 application-entry tests.

Real manual terminal acceptance:

STDIO              PASS
Streamable HTTP    PASS
Architectural Decision Ledger

The project Architectural Decision Ledger already contained the decisions established through Parts 1–2E.

Part 2F added:

AD-051

Executable entry remains separate from application composition.

AD-052

Terminal transport selection maps directly to existing concrete connection profiles.

AD-053

The synchronous-to-asynchronous bridge belongs at the outer execution boundary.

AD-054

Runtime exceptions propagate until a meaningful project-owned failure taxonomy justifies explicit translation.

Important Existing Architectural Principles

The following principles remain in force:

explicit resolved connection profiles;
no automatic server resolver without a justified requirement;
inspection is separate from execution;
no tool execution or workflow behavior;
transport mechanics remain separate from transport-neutral inspection;
presentation remains independent;
pagination is exhausted;
raw schema and protocol metadata are preserved;
MCP SDK v2 Client remains the primary connection/session abstraction;
protocol negotiation is delegated to the SDK;
advertised capabilities control primitive inspection;
partial pagination evidence is preserved;
primitive-category failures remain independent;
project-owned configuration is separate from SDK runtime models;
configured target identity remains separate from server-reported identity;
profiles remain independent of file format;
direct SDK dependencies are acceptable where they are already the correct semantic abstraction;
application composition remains top-level assembly rather than protocol implementation;
Streamable HTTP currently uses the SDK's direct URL Client contract;
transport-specific Client construction occurs before the shared connected lifecycle;
executable entry remains separate from reusable application composition;
CLI transport selection maps directly to concrete profiles;
one outer synchronous-to-asynchronous bridge owns event-loop startup;
runtime exception translation remains deferred until justified.
Intentionally Deferred Territory

The following were explicitly not required to complete Part 2F:

friendly project-owned runtime error presentation;
richer process exit-code taxonomy;
installed mcp-details console command;
persistent connection-profile/configuration files;
authenticated Streamable HTTP configuration;
automatic MCP server discovery/resolution;
generic transport registry or dispatcher;
additional transports;
alternate presentation surfaces.

These items are possibilities, not automatically the next implementation tasks.

Part 2G Starting Position

Part 2G should begin as:

Part 2G — Post-Entry Remaining-Territory Architectural Review

Do not select a deferred feature merely because it is available to implement.

First compare the original MCP Details project goals with the architecture that now exists.

Determine:

which original requirements are fully satisfied;
which original requirements remain incomplete;
which remaining items are genuine architectural gaps;
which items are usability, packaging, deployment, or optional enhancement concerns;
which previously deferred areas now have sufficient evidence to justify work;
which areas should remain deferred;
whether the current application represents a natural completion boundary for the original project goal;
which subsystem, if any, should become the primary focus of the next implementation part;
the smallest safe first milestone for that subsystem.

Architecture review must precede implementation.

Teaching / Development Contract

Continue using the established project working style:

architecture before implementation;
professor / senior-software-architect teaching style;
beginner-friendly explanations without sacrificing technical depth;
extremely small, highly testable milestones;
preserve behavior unless a change is explicitly approved;
avoid speculative abstractions;
distinguish architectural decisions from implementation details;
compile after every implementation change;
run focused tests after implementation;
run the full regression suite after completed milestones;
stop at checkpoints;
explain why each abstraction exists before introducing it.

Do not begin coding Part 2G until the architectural review identifies and justifies the next implementation territory.

Authoritative Starting Baseline for Part 2G
Python:                    3.12.7
MCP Python SDK:            2.1.1
pytest:                    9.1.1
anyio:                     4.14.2

Supported transports:
  STDIO
  Streamable HTTP

Terminal entry:
  python -m mcp_details

Final automated baseline:
  96 passed
  0 failures

Manual terminal acceptance:
  STDIO                    PASS
  Streamable HTTP          PASS

Part 2F:
  COMPLETE

Architectural decisions:
  through AD-054 recorded