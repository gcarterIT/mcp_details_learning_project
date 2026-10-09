# MCP Details Learning Project — Part 2H Context

**Project:** MCP Details Learning Project  
**Next Part:** Part 2H — Post-Connection-Configuration Remaining-Territory Review  
**Context Date:** 2026-10-07  
**Previous Part:** Part 2G — Resolved Connection Configuration Expansion  
**Previous Part Status:** COMPLETE

---

# 1. Purpose of This Context File

This file is the authoritative starting context for Part 2H of the MCP Details Learning Project.

Part 2G is complete.

Part 2H must begin with an architectural remaining-territory review.

Do not assume that Part 2H requires another implementation feature.

Do not select OAuth, persistent configuration, automatic server discovery, packaging, additional transports, richer HTTP configuration, or any other deferred feature merely because it is available to implement.

First compare the original MCP Details project goals with the architecture and behavior that now exist.

The review must determine whether another genuine architectural gap remains and whether additional implementation is justified.

---

# 2. Project Purpose

The MCP Details Learning Project is a general-purpose, strictly read-only MCP inspection application.

Its purpose is to allow a user to research an MCP server, obtain explicit connection information, configure the application to connect to that server, and produce a detailed terminal report describing what the server advertises through MCP discovery operations.

The project is also a learning application for understanding:

- MCP connection architecture;
- MCP initialization;
- server metadata and capabilities;
- MCP discovery primitives;
- pagination;
- transport boundaries;
- application composition;
- presentation boundaries;
- runtime connection configuration.

The application is not intended to be an MCP workflow executor.

---

# 3. Core Inspection Policy

The application remains:

```text
DISCOVERY / INSPECTION ONLY

It may connect to an MCP server, initialize the MCP protocol, inspect initialization metadata, and perform discovery/list operations.

It must not normally:

call tools
read arbitrary resource contents
invoke/render prompts for workflow execution
perform MCP-specific workflows
modify remote state

The application stops at the inspection boundary.

This policy remains a foundational project constraint.

4. Explicit Connection Information Remains the Starting Point

The application does not treat an arbitrary MCP name, repository identifier, package name, or registry identifier as sufficient connection information.

The current conceptual workflow remains:

User researches an MCP server
        │
        ▼
obtains explicit connection information
        │
        ▼
constructs/configures a resolved connection profile
        │
        ▼
MCP Details
        │
        ▼
connects
        │
        ▼
initializes MCP
        │
        ▼
inspects
        │
        ▼
renders report

Research/resolution and connection remain separate concerns.

Automatic arbitrary MCP server discovery/resolution has not been implemented.

5. Current Environment

The authoritative Part 2H starting environment is:

Python:                    3.12.7
MCP Python SDK:            2.1.1
pytest:                    9.1.1
anyio:                     4.14.2
Operating environment:     Windows / PowerShell

Project root:

C:\AI_Projects\mcp_details_learning_project
6. Supported Transports

The application currently supports:

STDIO
Streamable HTTP

The architecture remains open to additional transports without introducing a generic transport registry prematurely.

Transport-specific connection configuration is kept separate.

Inspection becomes transport-neutral after an MCP SDK Client has been constructed and connected.

7. Part 2A — Minimal Skeleton and STDIO Profile

Part 2A established the initial project structure and explicit STDIO connection profile.

The profile boundary established the principle that MCP Details owns its own connection-profile representation rather than exposing SDK runtime objects as application configuration.

The initial STDIO profile represented:

display name;
command;
arguments;
optional working directory;
explicit STDIO transport identity.

Arguments are stored as an immutable tuple.

Profile validation rejects structurally invalid required fields such as blank display names or commands.

8. Part 2B — STDIO Connection Boundary

Part 2B established the connection boundary for STDIO.

The project-owned STDIO profile is translated into MCP SDK StdioServerParameters.

Conceptually:

StdioConnectionProfile
        │
        ▼
build_stdio_server_parameters()
        │
        ▼
StdioServerParameters
        │
        ▼
MCP SDK
        │
        ▼
STDIO subprocess

Real SDK integration established that MCP Details could launch and connect to a real MCP STDIO subprocess.

9. Part 2C — Transport-Neutral Inspection

Part 2C established the central inspection architecture.

Inspection operates on an already-connected MCP SDK v2 Client.

The major result structures include:

ServerDescription
InspectionStatus
CategoryInspection[T]
MCPInspectionResult

Inspection statuses distinguish:

NOT_ADVERTISED
SUCCESS
PARTIAL
FAILED

The application inspects:

server initialization metadata;
protocol version;
server capabilities;
instructions;
tools;
resources;
resource templates;
prompts.

Primitive discovery honors server-advertised capabilities.

Pagination is exhausted completely.

If a later page fails after earlier pages succeeded, the application preserves the earlier evidence and reports a partial result rather than discarding successful data.

Primitive categories fail independently.

Raw SDK/protocol semantic evidence is preserved rather than unnecessarily cloned into project-specific semantic models.

Inspection remains transport-neutral.

10. Part 2D.1 — Application Composition

Part 2D.1 established the application composition boundary.

The application composes:

connection profile
        │
        ▼
transport-specific Client construction
        │
        ▼
Client lifecycle
        │
        ▼
transport-neutral inspection
        │
        ▼
ApplicationInspectionResult

ApplicationInspectionResult combines:

InspectionTargetSummary
+
MCPInspectionResult

The target summary contains safe configured-target identity information such as:

display name;
transport.

Raw connection profiles and runtime-sensitive values do not flow into the inspection result.

11. Part 2D.2 — Presentation Boundary

Part 2D.2 established a pure presentation boundary:

ApplicationInspectionResult
        │
        ▼
render_report()
        │
        ▼
str

The renderer does not own SDK lifecycle or connection behavior.

The terminal report includes:

configured target;
server identity/version;
protocol version;
capabilities;
instructions;
tools;
resources;
resource templates;
prompts;
pagination evidence;
partial/failure evidence;
nested task capabilities;
experimental/extension capabilities.

Manual presentation review discovered a duplicate Tools-section defect.

That defect was corrected and protected with a regression test.

12. Part 2E — Streamable HTTP

Part 2E added Streamable HTTP as the second supported transport.

The minimal Streamable HTTP profile initially represented:

display_name
url
transport = streamable_http

For the minimal unauthenticated path, application composition uses:

Client(profile.url)

directly.

The application did not introduce a generic transport factory, strategy hierarchy, registry, or dispatcher.

The shared application lifecycle begins only after transport-specific Client construction.

Real Streamable HTTP integration evidence was established.

13. Part 2F — Application Entry Boundary

Part 2F established terminal application entry.

The application supports:

python -m mcp_details

with explicit transport subcommands.

Conceptually:

PowerShell
        │
        ▼
python -m mcp_details
        │
        ▼
argument parsing
        │
        ▼
transport-specific profile construction
        │
        ▼
application composition
        │
        ▼
inspection
        │
        ▼
render_report()
        │
        ▼
stdout

The entry boundary owns:

argparse configuration;
terminal syntax;
transport selection;
CLI-to-profile translation;
application routing;
the outer synchronous-to-asynchronous execution bridge;
stdout output.

Lower application layers remain asynchronous.

One outer asyncio.run(...) bridge converts the synchronous process-entry environment into the asynchronous application execution model.

Runtime exceptions continue to propagate rather than being hidden by a premature generalized error taxonomy.

Part 2F completed with:

96 tests passed
0 failures

and real terminal acceptance for both supported transports.

14. Part 2G — Resolved Connection Configuration Expansion

Part 2G began with a post-entry architectural review rather than immediately selecting another feature.

That review determined that the core inspection architecture was substantially complete but identified an important remaining connection gap:

realistic MCP servers may require runtime-sensitive connection configuration that the minimal profiles could not express.

Part 2G therefore expanded resolved connection configuration for both supported transports while preserving the established profile, connection, application, inspection, and presentation boundaries.

15. Part 2G STDIO Environment References

StdioConnectionProfile now includes:

environment_variables: tuple[str, ...] = ()

The profile stores environment-variable names only.

It does not store resolved environment-variable values.

Blank environment-variable names are rejected structurally.

Declared references use same-name forwarding.

Example:

profile declares:

MCP_DETAILS_TEST_VALUE

        │
        ▼

connection resolves:

os.environ["MCP_DETAILS_TEST_VALUE"]

        │
        ▼

StdioServerParameters.env:

{
    "MCP_DETAILS_TEST_VALUE": "<runtime value>"
}

All declared references are required.

A missing reference fails connection construction.

An environment variable that exists with an empty-string value is still considered present.

16. STDIO SDK Environment Ownership

Investigation of MCP Python SDK 2.1.1 established that the SDK constructs the subprocess environment from its safe default environment plus explicitly supplied StdioServerParameters.env values.

MCP Details therefore does not duplicate SDK environment merging.

When no additional environment references are configured:

StdioServerParameters.env is None

The SDK retains ownership of its safe-default environment behavior.

When references are configured, MCP Details supplies only the explicitly resolved additional variables.

17. STDIO CLI Environment Contract

STDIO terminal syntax supports repeatable:

--env NAME

Example:

$env:MCP_DETAILS_TEST_VALUE = "manual-acceptance-value"

python -m mcp_details stdio `
    --name "Manual STDIO Demo" `
    --command python `
    --env MCP_DETAILS_TEST_VALUE `
    -- `
    tests\support\minimal_stdio_server.py

Arguments before -- belong to MCP Details.

Arguments after -- remain opaque arguments for the target STDIO server.

18. Streamable HTTP Header Environment References

Part 2G introduced:

HttpHeaderEnvironmentReference

representing:

HTTP header name
        ←
environment-variable name

StreamableHttpConnectionProfile now includes:

header_references: tuple[HttpHeaderEnvironmentReference, ...] = ()

The profile stores names/references only.

It does not store resolved header values.

Both the HTTP header name and environment-variable name must be nonblank.

19. Streamable HTTP Runtime Resolution

For profiles containing header references, the connection boundary resolves the required environment variables and constructs the configured HTTP path.

Conceptually:

StreamableHttpConnectionProfile
        │
        │ header ← environment reference
        ▼
configured_streamable_http_transport()
        │
        │ runtime environment lookup
        ▼
resolved HTTP headers
        │
        ▼
create_mcp_http_client(headers=...)
        │
        ▼
streamable_http_client(
    profile.url,
    http_client=http_client,
)
        │
        ▼
Client(transport)

All configured references are required.

A missing referenced environment variable fails connection construction.

The environment-variable value is treated as the complete HTTP-header value.

MCP Details does not prepend authentication schemes or otherwise transform the value.

20. Simple vs. Configured Streamable HTTP Paths

Part 2G deliberately preserved the existing minimal HTTP path.

When no header references are configured:

StreamableHttpConnectionProfile
        │
        ▼
Client(profile.url)

When header references are configured:

StreamableHttpConnectionProfile
        │
        ▼
configured_streamable_http_transport()
        │
        ▼
configured HTTP client
        │
        ▼
Streamable HTTP transport
        │
        ▼
Client(transport)

The richer mechanism is introduced only when required.

21. Streamable HTTP CLI Header Contract

The Streamable HTTP terminal command supports repeatable:

--header-env HEADER ENV_VAR

Example:

$env:MCP_AUTHORIZATION = "Bearer abc123"

python -m mcp_details streamable-http `
    --name "Authenticated MCP" `
    --url "https://example.com/mcp" `
    --header-env Authorization MCP_AUTHORIZATION

The CLI carries references only.

It does not resolve runtime values.

Resolution remains a connection-boundary responsibility.

22. Configured HTTP Lifecycle Ownership

For configured Streamable HTTP connections:

connection boundary
        │
        ├── resolves references
        ├── creates configured HTTP client
        ├── owns HTTP-client context
        └── yields Streamable HTTP transport
                    │
                    ▼
application composition
        │
        ├── creates MCP Client
        ├── owns MCP Client lifecycle
        └── invokes transport-neutral inspection

This preserves the established separation between connection construction and application composition.

23. Real Configured Streamable HTTP Verification

Part 2G added:

tests/support/header_required_streamable_http_server.py

This real MCP Streamable HTTP test server requires:

X-MCP-Details-Test: expected-test-value

A control request without the required header returned:

401 Unauthorized

proving that the server genuinely enforced the test condition.

The real MCP Details terminal path then succeeded using:

$env:MCP_DETAILS_HTTP_TEST_VALUE = "expected-test-value"

python -m mcp_details streamable-http `
    --name "Configured HTTP Demo" `
    --url "http://127.0.0.1:8765/mcp" `
    --header-env X-MCP-Details-Test MCP_DETAILS_HTTP_TEST_VALUE

The successful path proved:

PowerShell environment
        │
        ▼
CLI reference
        │
        ▼
HTTP header environment reference
        │
        ▼
Streamable HTTP profile
        │
        ▼
connection-time resolution
        │
        ▼
configured HTTP client
        │
        ▼
real HTTP header
        │
        ▼
real MCP server
        │
        ▼
MCP initialization
        │
        ▼
inspection
        │
        ▼
terminal report

A permanent real-server integration test now protects this path.

24. Current Profile Concepts

The current profile concepts are approximately:

StdioConnectionProfile
├── display_name
├── command
├── args
├── cwd
├── environment_variables
└── transport = "stdio"


HttpHeaderEnvironmentReference
├── header_name
└── environment_variable


StreamableHttpConnectionProfile
├── display_name
├── url
├── header_references
└── transport = "streamable_http"

Profiles remain immutable project-owned configuration structures.

Runtime-sensitive values are not stored in them.

25. Current Architectural Flow

The current high-level application architecture is:

Terminal / Entry Boundary
        │
        ▼
Resolved Connection Profile
        │
        ▼
Transport-Specific Connection Construction
        │
        │
        ├── STDIO parameters
        │
        └── Streamable HTTP transport/client configuration
        │
        ▼
MCP SDK Client
        │
        ▼
Transport-Neutral Inspection
        │
        ▼
MCPInspectionResult
        │
        ▼
ApplicationInspectionResult
        │
        ▼
Pure Presentation Boundary
        │
        ▼
Terminal Report

Runtime-sensitive values stop at the connection boundary and do not flow into inspection or presentation results.

26. Architectural Decision Ledger

The Architectural Decision Ledger is current through AD-056.

Important established decisions include:

explicit resolved connection profiles rather than automatic arbitrary-name resolution;
inspection rather than execution;
stop before tool execution/resource-content retrieval/prompt execution;
transport mechanics separate from inspection;
SDK v2 Client as the primary connected-client boundary;
SDK-owned protocol negotiation;
advertised-capability gating;
complete pagination;
partial-result preservation;
independent primitive-category failure handling;
lossless SDK/protocol evidence preservation;
safe configured-target summary;
presentation independent of SDK lifecycle;
direct SDK URL Client construction for minimal Streamable HTTP;
shared application lifecycle only after transport-specific Client construction;
separate application entry boundary;
explicit terminal subcommands mapped to concrete profiles;
one outer synchronous-to-asynchronous execution bridge;
simple process failure semantics;
runtime-referenced additional STDIO environment requirements;
runtime-referenced additional Streamable HTTP headers.

Part 2G added:

AD-055
Represent Additional STDIO Environment Requirements
as Runtime References

AD-056
Represent Additional Streamable HTTP Headers
as Runtime Environment References

Do not introduce a new architectural decision merely to document an implementation detail.

27. Final Part 2G Verification Baseline

Part 2G closed with:

Compile verification:
  PASS

Automated regression:
  120 passed
  0 failures

Manual STDIO environment forwarding:
  PASS

Streamable HTTP missing-header control:
  401 Unauthorized as expected

Configured-header Streamable HTTP inspection:
  PASS

Real ordinary Streamable HTTP integration:
  PASS

Real header-required Streamable HTTP integration:
  PASS

The final automated suite includes profile, connection, application, entry, inspection, presentation, STDIO integration, ordinary Streamable HTTP integration, and configured-header Streamable HTTP integration coverage.

28. Part 2G Repository Closure

Part 2G was committed as:

Commit:
  27c4c8e

Summary:
  Add runtime-referenced STDIO and HTTP connection configuration

Branch:
  main

Remote:
  origin/main synchronized

Tag:
  part-2g-complete

Working tree:
  clean

Part 2G is fully closed.

29. Part 2G Documentation

The repository preserves different documentation roles.

MCP_DETAILS_PROJECT_CONTEXT.md is the original project-definition document.

Historical PART*_CONTEXT_*.md files preserve the starting state of individual project phases.

Historical Part_*_Completion_Note.md files preserve completed milestone records.

PART2G_CONTEXT_20260926.md remains the historical starting context for Part 2G.

Part_2G_Completion_Note.md records the completed Part 2G implementation and verification state.

Supporting Part 2G learning/architecture documentation is stored under:

docs/

including STDIO and Streamable HTTP environment-reference flow material.

30. Intentionally Deferred Territory

The following territory remains intentionally deferred.

STDIO Configuration
literal environment values in profiles;
optional environment references;
environment-variable renaming;
.env loading;
full process-environment inheritance;
generalized secret-provider integration.
Streamable HTTP Configuration
literal HTTP-header values;
optional header references;
automatic Bearer construction;
authentication-specific transformations;
OAuth authorization flows;
token refresh;
generalized SDK authentication-provider integration;
TLS configuration;
client certificates;
proxy configuration;
configurable HTTP timeouts;
arbitrary HTTP-client injection.
Cross-Transport / Product-Level Territory
persistent connection-profile/configuration files;
credential stores;
cloud secret-manager integration;
automatic MCP server discovery/resolution;
generic transport registry;
additional transports;
alternate presentation surfaces;
installed console command/package distribution;
richer process-level error translation.

These are candidate future territories.

They are not automatically incomplete requirements.

31. Important Distinction for Part 2H

Part 2H must distinguish:

genuine architectural gap
        ≠
feature that could be added
        ≠
usability improvement
        ≠
packaging concern
        ≠
deployment concern
        ≠
optional enhancement

A capability should not be selected merely because it is common in production applications.

The review should ask whether the capability is required by the original purpose and success definition of the MCP Details Learning Project.

32. Part 2H Starting Question

The primary Part 2H question is:

Given the original MCP Details project goals and the architecture now completed through Part 2G, does a meaningful architectural gap remain that justifies another implementation part?

This question must be answered before selecting implementation work.

33. Required Part 2H Review

Part 2H should begin by comparing the original project definition against the current application.

The review should determine:

which original requirements are fully satisfied;
which original requirements remain incomplete;
which remaining items are genuine architectural gaps;
which items are usability improvements;
which items are packaging or deployment concerns;
which items are optional enhancements;
which intentionally deferred areas should remain deferred;
whether the application has reached a natural completion boundary for the original project goal;
whether another implementation part is justified;
if another implementation part is justified, which subsystem should become the next focus;
the smallest safe first milestone for that subsystem.

Do not implement anything until this review is complete.

34. Candidate Areas to Evaluate — Not Preselected Work

The review may consider:

persistent connection profiles
richer authentication / OAuth
credential management
HTTP TLS/proxy/timeout configuration
automatic MCP server discovery/resolution
additional transports
packaging / installed command
richer process-level error handling
alternate presentation surfaces

This list is not a roadmap.

No item on the list has been approved as Part 2H implementation work.

The review may conclude that none of them is required for completion of the original project.

35. Natural Completion Boundary Question

Part 2H should explicitly consider whether the current application already satisfies the original success definition.

The current application can:

known MCP server
        │
        ▼
explicit connection profile
        │
        ▼
runtime-sensitive connection requirements
        │
        ▼
STDIO or Streamable HTTP connection
        │
        ▼
MCP initialization
        │
        ▼
server metadata and capabilities
        │
        ├── tools
        ├── resources
        ├── resource templates
        └── prompts
        │
        ▼
complete pagination / failure evidence
        │
        ▼
structured inspection result
        │
        ▼
terminal report

This is very close to, and may fully satisfy, the original stated application goal.

Part 2H must evaluate that conclusion explicitly rather than assuming continued implementation.

36. Development and Teaching Contract

Continue using the established working style:

architecture before implementation;
professor / senior-software-architect teaching style;
beginner-friendly explanations without sacrificing technical depth;
explain why an abstraction exists before introducing it;
extremely small, highly testable milestones;
preserve existing behavior unless a change is explicitly approved;
avoid speculative abstractions;
distinguish architectural decisions from implementation details;
inspect actual SDK behavior before relying on assumptions;
compile after every implementation change;
run focused tests after implementation;
run the full regression suite before milestone closure;
stop at checkpoints;
do not invent repository state or code that has not been shown;
preserve the strict read-only inspection policy.

Do not begin implementation merely because Part 2H has started.

37. Authoritative Starting Baseline for Part 2H
Project:
  MCP Details Learning Project

Previous part:
  Part 2G — Resolved Connection Configuration Expansion

Part 2G status:
  COMPLETE

Python:
  3.12.7

MCP Python SDK:
  2.1.1

pytest:
  9.1.1

anyio:
  4.14.2

Supported transports:
  STDIO
  Streamable HTTP

STDIO runtime environment references:
  SUPPORTED

Streamable HTTP header environment references:
  SUPPORTED

Terminal entry:
  python -m mcp_details

Inspection policy:
  strictly read-only discovery / inspection

Final automated baseline:
  120 passed
  0 failures

Manual acceptance:
  STDIO environment forwarding             PASS
  Streamable HTTP missing-header control   PASS
  Streamable HTTP configured-header flow   PASS

Architectural Decision Ledger:
  current through AD-056

Part 2G Git commit:
  27c4c8e

Part 2G Git tag:
  part-2g-complete

Repository:
  main synchronized with origin/main
  working tree clean
38. Required First Action in Part 2H

Begin:

Part 2H — Post-Connection-Configuration Remaining-Territory Review

Do not write production code.

First review the original project goals against the completed architecture through Part 2G.

Produce a requirements/status matrix that classifies each important original goal as:

SATISFIED
PARTIALLY SATISFIED
UNSATISFIED
INTENTIONALLY DEFERRED / OUT OF CORE SCOPE

For every item that is not fully satisfied, explain whether it represents:

a genuine architectural gap
a usability concern
a packaging/deployment concern
an optional enhancement
or intentionally deferred territory

Then determine whether another implementation part is justified.

If implementation is justified, identify the smallest architecturally coherent next subsystem and propose the smallest safe first milestone.

If implementation is not justified, recommend project-level closure or the appropriate next learning phase.

Stop for approval before implementing anything.


## Why this is the right transition file

Notice that it does **not** say:

```text
Part 2H = OAuth

or:

Part 2H = persistent profiles

Instead:

Part 2G completed
        │
        ▼
re-establish authoritative baseline
        │
        ▼
compare original requirements
with actual completed system
        │
        ▼
determine remaining territory
        │
        ├── genuine gap → justify implementation
        │
        └── no core gap → consider project closure

That keeps us faithful to the architecture-first method that has worked well throughout this project.