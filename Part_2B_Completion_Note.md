# MCP Details Learning Project
# Part 2B Completion Note — Minimal STDIO Connection Boundary

**Completion date:** 2026-08-30  
**Status:** COMPLETE — minimal STDIO connection boundary closed  
**Regression baseline:** 15 passing tests

---

## 1. Part 2B objective

Part 2B established the first real MCP connection boundary for MCP Details.

The objective was deliberately narrow:

1. declare the MCP Python SDK dependency,
2. translate the project-owned STDIO connection profile into SDK runtime
   configuration,
3. determine whether MCP Details needs its own Client construction or
   connection-lifecycle abstraction,
4. prove a real STDIO MCP connection,
5. stop before beginning capability inspection.

Part 2B did not attempt to build the complete connection subsystem.

---

## 2. Starting architecture

Part 2A established the initial project skeleton and the first project-owned
connection profile:

```text
StdioConnectionProfile
    display_name
    transport = "stdio"
    command
    args
    cwd
	
	
The profile is:

project-owned,
immutable,
independent of MCP SDK runtime objects,
structurally validated,
intentionally minimal.

Part 2B began from this boundary.


## 3. MCP SDK dependency

The project now declares:

dependencies = [
    "mcp==2.1.1",
]

The SDK is pinned exactly because this learning project prioritizes
reproducibility and controlled architectural evolution.

The CLI extra was not added because MCP Details currently needs the client and
runtime APIs rather than MCP CLI tooling.

The test dependency remains separate:

[project.optional-dependencies]
test = [
    "pytest",
]

## 4. Connection translation boundary

The production connection boundary is currently intentionally small.

src/mcp_details/connection.py owns translation from the project profile to
the MCP SDK runtime connection parameters.

The current contract is:

StdioConnectionProfile
        ↓
build_stdio_server_parameters()
        ↓
StdioServerParameters

The implementation translates:

profile.command
    ↓
parameters.command

profile.args: tuple[str, ...]
    ↓
list(profile.args)
    ↓
parameters.args

profile.cwd
    ↓
parameters.cwd

The following profile fields are deliberately not translated:

display_name
transport

display_name is project-owned human-facing metadata.

transport identifies the project profile variant rather than an SDK
parameter that needs to be copied into StdioServerParameters.

## 5. Project model versus SDK model

The profile intentionally stores arguments as:

tuple[str, ...]

rather than:

list[str]

because the project profile is immutable connection intent.

A frozen dataclass containing a mutable list would still allow mutation of
the list contents.

The SDK runtime object expects a list, so the connection boundary adapts:

project model
tuple[str, ...]
        ↓
connection adapter
list(profile.args)
        ↓
SDK runtime model
list[str]

The project model is therefore not distorted merely to mirror an external
SDK representation.

## 6. Translation contract tests

tests/test_connection.py protects the following contracts:

translation returns StdioServerParameters,
minimal profile command is preserved,
default arguments become an empty SDK list,
default cwd remains None,
configured arguments are translated from tuple to list,
configured cwd is preserved.

These tests do not launch a subprocess.

They protect only the deterministic project-to-SDK translation boundary.

## 7. Client construction ownership review

Part 2B reviewed whether MCP Details should introduce a helper such as:

build_stdio_client(profile)

or a wrapper such as:

open_connection(profile)

No such abstraction was justified.

The current high-level SDK already supports:

StdioServerParameters
        ↓
Client(parameters)
        ↓
async with client

No additional MCP Details connection policy currently exists between those
steps.

Therefore adding another wrapper would hide an SDK constructor without adding
meaningful project semantics.

The composition layer may construct the high-level SDK Client directly when
wiring the application together.

## 8. Lifecycle ownership review

MCP Details does not currently own a custom connection lifecycle.

The MCP Python SDK high-level Client already owns the relevant runtime
behavior:

Client(parameters)
        ↓
async context entry
        ↓
STDIO subprocess launch
        ↓
MCP communication
        ↓
protocol negotiation
        ↓
connected Client
        ↓
async context exit
        ↓
transport/process cleanup

Therefore MCP Details did not introduce:

MCPConnection
ConnectionManager
open_connection()
stdio_client()
ClientSession
manual initialize()

The previous MCP Client Learning Project required more explicit lifecycle
machinery because it used a lower-level SDK architecture.

That architecture was not copied into MCP Details because MCP Python SDK v2
already provides the higher-level Client abstraction needed here.

## 9. Inspection boundary direction

Part 2B confirmed that future inspection behavior should receive an already
connected high-level SDK Client.

Conceptually:

STDIO profile
      ↓
connection setup
      ↓
connected Client
      ↓
inspection

Future inspection code should not receive:

StdioConnectionProfile

for the purpose of establishing its own connection.

It should also not receive:

StdioServerParameters

and recreate the connection lifecycle.

This preserves the intended separation:

connection
    establishes MCP relationship

inspection
    examines the connected server

It also supports the future transport-neutral architecture:

STDIO ───────────────┐
                     │
                     ▼
               connected Client
                     │
                     ▼
                 inspection
                     ▲
                     │
Streamable HTTP ─────┘

## 10. Real STDIO connection proof

Part 2B added one real integration test.

A minimal project-controlled MCP server exists only under test support:

tests/
└── support/
    └── minimal_stdio_server.py

This server:

uses the real MCP SDK,
communicates through real STDIO,
has a known server identity,
contains no application business logic,
does not need tools, resources, resource templates, or prompts.

The integration test uses:

StdioConnectionProfile
        ↓
build_stdio_server_parameters()
        ↓
StdioServerParameters
        ↓
Client(parameters)
        ↓
real subprocess
        ↓
real STDIO
        ↓
real MCP negotiation

The subprocess is launched with:

sys.executable

so the server runs using the same Python environment that is running pytest.

The server path is resolved relative to the integration test rather than
depending on the shell's current working directory.

## 11. Connection evidence protected

The integration test confirms:

the real STDIO subprocess can launch,
the high-level SDK Client can enter successfully,
MCP negotiation completes,
server information becomes available,
the expected server identity is observed,
negotiated protocol information is available,
server capability metadata is available,
the Client context exits successfully.

The test deliberately does not perform capability discovery.

It makes no calls to:

list_tools()
list_resources()
list_resource_templates()
list_prompts()

It also makes none of the operations forbidden by the project's strict
non-execution policy:

call_tool()
read_resource()
get_prompt()

## 12. Test architecture

The current regression suite is divided into four useful layers:

tests/test_package_import.py
    package boundary

tests/test_profiles.py
    project-owned profile contract

tests/test_connection.py
    profile → SDK translation contract

tests/test_stdio_connection.py
    real STDIO integration contract

Current full regression baseline:

15 passed

## 13. Connection failure semantics

Connection failures are real but project-owned failure semantics have not yet
been defined.

Possible underlying failures include:

executable not found,
server script not found,
subprocess startup failure,
server crash,
invalid MCP traffic,
negotiation failure,
unexpected connection termination.

MCP Details currently does not define whether these should become:

raw SDK/process exceptions,
project-owned connection exceptions,
structured failure DTOs,
result-model failure fields,
composition-level failures,
or some combination.

Tests were deliberately not added that would freeze incidental SDK exception
types into the project contract.

Failure semantics are considered important future territory, but their correct
shape depends partly on the upcoming inspection and result architecture.

## 14. Deferred connection concerns

The following remain intentionally deferred:

Environment configuration

The initial STDIO profile does not yet own environment-variable configuration.

Credential references

Part 1 established the architectural direction that credentials should use
references and be resolved near connection construction, but no credential
model or resolution mechanism has been implemented.

Failure normalization

No project-owned connection exception hierarchy or failure DTO has been
introduced.

Streamable HTTP

The first concrete connection path is STDIO only.

Streamable HTTP remains a future connection-profile and translation milestone.

Generic transport dispatcher

No generic:

build_connection_target(profile)

or transport switch has been introduced because only one concrete transport
profile currently exists.

Custom lifecycle abstraction

No connection wrapper has been introduced because the high-level SDK Client
already provides sufficient lifecycle behavior for the current requirements.

## 15. Architectural conclusions

The minimal STDIO connection boundary is complete.

The project currently needs only a thin adapter between project-owned
connection intent and the SDK's runtime connection configuration.

Current dependency direction:

profiles.py
    │
    └── standard library


connection.py
    │
    ├── profiles.py
    └── MCP Python SDK


composition — future
    │
    ├── connection translation
    ├── SDK Client lifecycle
    └── inspection

The project has not created a connection framework merely because an external
SDK exists.

Additional abstractions should be introduced only when project-owned policy
requires them.

## 16. Part 2B closure status
Project-owned STDIO profile               COMPLETE
Profile structural validation             COMPLETE
MCP SDK 2.1.1 dependency                  COMPLETE
Profile → SDK translation                 COMPLETE
Translation contract tests                COMPLETE
Real STDIO subprocess proof               COMPLETE
Real MCP negotiation proof                COMPLETE
Known server identity proof               COMPLETE
SDK lifecycle proof                       COMPLETE

Custom Client builder                     NOT NEEDED
Custom lifecycle wrapper                  NOT NEEDED
Manual ClientSession                      NOT NEEDED
Manual initialize                         NOT NEEDED
Low-level stdio_client                     NOT NEEDED

Environment configuration                 DEFERRED
Credential references                     DEFERRED
Connection failure normalization          DEFERRED
Streamable HTTP                           FUTURE

Regression baseline                       15 PASS

Part 2B status: CLOSED FOR THE MINIMAL STDIO CONNECTION BOUNDARY.

## 17. Recommended next territory

Proceed to:

Part 2C — Inspection Boundary Architectural Review

The next architectural question is no longer:

How does MCP Details connect to an MCP server?

It becomes:

Given an already-connected high-level MCP Client, how should MCP Details
safely, completely, and transport-neutrally inspect the server?

Part 2C should review architecture before implementation.