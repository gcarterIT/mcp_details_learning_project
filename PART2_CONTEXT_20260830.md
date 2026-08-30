# MCP Details Learning Project

# Part 2 Context

**Context Date:** 2026-08-30
**Previous Part:** Part 1 — Architecture Foundation
**Previous Part Status:** COMPLETE
**Current Part:** Part 2 — Initial Implementation
**First Milestone:** Part 2A — Minimal Project Skeleton and Profile Model First Milestone

---

# 1. Purpose of This File

This file provides the authoritative starting context for Part 2 of the MCP Details Learning Project.

Part 1 completed the broad architectural review.

Part 2 begins controlled implementation.

The architecture should not be redesigned casually during implementation. However, concrete implementation evidence may reveal that a previously deferred detail requires an architectural decision.

When that occurs:

1. stop implementation
2. identify the architectural question
3. review evidence
4. make the smallest necessary decision
5. record it in the Architectural Decision Ledger
6. resume implementation

---

# 2. Project Goal

Build a general-purpose MCP inspection application that can connect to explicitly configured MCP servers and describe what they expose without executing their advertised capabilities.

The application should eventually inspect and report:

* server identity when available
* negotiated protocol information
* server capabilities
* server instructions
* tools
* resources
* resource templates
* prompts
* descriptions
* tool schemas
* prompt arguments
* annotations
* metadata
* pagination completeness
* relevant discovery/initialization evidence

Initial presentation is terminal output.

Future presentation may include JSON, Markdown, notebooks, Streamlit, or other interfaces.

---

# 3. Fundamental Safety and Scope Boundary

The project performs:

NON-EXECUTING CAPABILITY INSPECTION

Normal inspection may perform:

* MCP connection/protocol negotiation
* server discovery/initialization as handled by the SDK
* list_tools()
* list_resources()
* list_resource_templates()
* list_prompts()
* pagination necessary to complete those inventories

Normal inspection must not perform:

* call_tool()
* read_resource()
* get_prompt()
* server-specific execution workflows

Core principle:

CAPABILITY INSPECTION != CAPABILITY EXECUTION

---

# 4. SDK Boundary

Target:

MCP Python SDK 2.x

Do not attempt dual SDK 1.x and 2.x support.

Primary client abstraction:

MCP SDK v2 Client

The SDK owns:

* transport mechanics
* connection lifecycle mechanics
* modern server/discover behavior
* legacy initialization fallback
* protocol-era negotiation
* wire requests
* protocol parsing
* ClientSession internals

The project owns:

* connection profiles
* profile validation
* profile-to-SDK translation
* inspection policy
* inspection completeness
* partial-failure semantics
* structured inspection result
* presentation

Do not recreate SDK protocol negotiation.

Do not copy the previous project's MCPConnection unchanged.

Introduce a project-owned lifecycle wrapper only if a concrete project-specific lifecycle responsibility emerges.

---

# 5. Initial Transport Scope

Initial transports:

1. STDIO
2. Streamable HTTP

Architecture should remain open to additional transports only when a real requirement appears.

Transport-specific mechanics belong in the connection boundary.

Primitive inspection must remain transport-neutral after it receives a usable Client.

---

# 6. Explicit Resolved Connection Profiles

Version 1 begins from explicit resolved connection configuration.

Intended workflow:

Research server
|
v
Determine actual connection requirements
|
v
Create resolved connection profile
|
v
MCP Details
|
v
Connect
|
v
Inspect

Do not assume that an arbitrary identifier such as:

weather-mcp/weather-mcp

is enough information to establish a connection.

Automatic registry, GitHub, package, vendor, or identifier resolution is deferred.

---

# 7. Connection Profile Boundary

Connection profiles are project-owned.

They are not serialized MCP SDK runtime objects.

Profiles explicitly identify transport.

Conceptual variants:

StdioConnectionProfile

StreamableHTTPConnectionProfile

Initial STDIO profile concept:

* display_name
* transport = stdio
* command
* args
* environment configuration
* optional cwd

Initial Streamable HTTP concept:

* display_name
* transport = streamable_http
* URL
* authentication/header configuration when concrete requirements demand it

Do not expose every MCP SDK constructor option merely because it exists.

---

# 8. Credential Boundary

Prefer credential references rather than embedded secrets.

Initial preferred secret mechanism:

environment-variable references

Resolve credentials near connection construction.

Do not propagate resolved secret values into:

* inspection DTOs
* terminal rendering
* JSON/Markdown reports
* ordinary logging
* Git-managed example profiles

Raw connection profiles and safe target summaries are separate concepts.

---

# 9. Capability-Aware Inspection Policy

After successful connection, inspect only project-scope primitive categories advertised by the server.

Do not probe unadvertised capability-gated methods during normal inspection.

Conceptually:

advertised
|
+-- yes --> inspect
|
`-- no --> NOT_ADVERTISED

Resources capability governs both:

* resources/list
* resources/templates/list

These remain separate inventory operations and may independently succeed or fail.

---

# 10. Complete Inspection Contract

A category is complete only when every pagination cursor has been exhausted.

Example:

Page 1 -> nextCursor
Page 2 -> nextCursor
Page 3 -> no cursor

Only after Page 3 is the inventory complete.

If a later page fails:

* preserve earlier items
* preserve relevant successful evidence
* record the failure
* mark category PARTIAL

Never discard partial evidence merely because complete inspection failed.

---

# 11. Category Inspection States

Conceptual states:

NOT_ADVERTISED

SUCCESS

PARTIAL

FAILED

Important distinction:

SUCCESS + zero items

means:

the category was advertised/applicable, inspection succeeded, and the inventory was empty.

It is not equivalent to NOT_ADVERTISED.

Do not introduce a separate EMPTY state unless later evidence demonstrates a need.

---

# 12. Independent Failure Policy

After connection and server-description retrieval succeed, primitive categories fail independently.

Example:

Tools               SUCCESS
Resources           FAILED
Resource Templates  SUCCESS
Prompts              SUCCESS

The resource failure must not erase successful information from the other categories.

Top-level connection/server-description failure is different because primitive inspection cannot meaningfully begin.

---

# 13. Structured Result Boundary

The project should eventually own one aggregate inspection result.

Conceptually:

MCPInspectionResult
|
+-- safe target summary
+-- server description
+-- tools
+-- resources
+-- resource templates
`-- prompts

Each primitive category conceptually uses:

CategoryInspection[T]

with:

* status
* collected SDK semantic objects
* completeness/pagination evidence
* diagnostic when necessary

Exact implementation is deferred until the corresponding milestone.

---

# 14. SDK Type Ownership

Do not create a second MCP type system.

Use documented MCP SDK semantic objects where appropriate, including:

* Tool
* Resource
* ResourceTemplate
* Prompt
* ServerCapabilities
* server identity objects
* DiscoverResult
* InitializeResult

Project-owned DTOs should represent MCP Details concepts such as:

* inspection aggregation
* category state
* completeness
* diagnostics
* safe target identity

Key principle:

SDK owns MCP semantics.

MCP Details owns inspection semantics.

---

# 15. Derived Truth Principle

Avoid independently storing information that can be reliably and cheaply derived from authoritative stored facts.

Examples:

items = [A, B, C]

derive:

item_count = 3

rather than storing both independently.

Similarly, overall inspection state should preferably be derived from component inspection states when practical.

This reduces contradictory state.

---

# 16. Presentation Boundary

Inspection returns structured results.

Presentation consumes structured results.

Correct:

MCP Client
|
v
Inspection
|
v
MCPInspectionResult
|
v
Terminal Renderer

Incorrect:

Terminal Renderer
|
v
list_tools()

Renderers may inspect fields of SDK semantic objects contained in results.

Renderers must not make MCP discovery requests.

---

# 17. Module Responsibility Map

The current conceptual module map is:

src/
`-- mcp_details/
    |
    +-- __init__.py
    +-- __main__.py          later when needed
    +-- app.py               composition
    +-- profiles.py          profile semantics
    +-- connection.py        profile -> SDK connection
    +-- inspection.py        inspection policy
    +-- results.py           structured inspection results
    `-- rendering.py         terminal presentation

Do not create every module immediately merely because it appears in the architecture.

Create modules only as implementation milestones require them.

---

# 18. Dependency Direction

Intended dependencies:

connection.py
-> profiles.py
-> MCP SDK transport/client APIs

inspection.py
-> results.py
-> MCP SDK client APIs

results.py
-> MCP SDK semantic types where justified

rendering.py
-> results.py

app.py
-> project modules required for composition

Undesirable directions:

profiles -> connection
profiles -> inspection
results -> inspection
results -> rendering
inspection -> rendering
rendering -> connection
connection -> rendering

Inspection should not require transport-specific profile details after connection.

---

# 19. Deliberately Deferred Architecture

Do not introduce without concrete evidence:

* automatic MCP server resolver
* registry integration
* GitHub resolution
* package installation
* SDK v1 compatibility
* project-owned protocol negotiation
* replacement MCPConnection wrapper
* SDK facade merely to hide the SDK
* transport plugin framework
* workflow subsystem
* generalized pagination framework
* standalone generic validation subsystem
* large exception hierarchy
* caching subsystem
* protocol-conformance testing
* capability execution
* profile-file serialization decision
* JSON/YAML/TOML commitment
* full persistence architecture

---

# 20. Architectural Decision Ledger

Maintain:

ARCHITECTURAL_DECISION_LEDGER.md

as the continuously updated project decision record.

Part 1 established AD-001 through AD-047.

When Part 2 discovers a genuinely architectural question:

Question
|
v
Evidence
|
v
Decision
|
v
Contract Created/Protected
|
v
Alternatives Deferred

Then add the next AD entry.

Do not create ledger entries for ordinary implementation details.

---

# 21. Part 2 Teaching Contract

Continue the established method:

* architecture before implementation
* professor/software-architect style
* explain why before coding
* extremely small milestones
* preserve established boundaries
* compile after every implementation
* run focused tests
* run full regression after every milestone
* stop after every checkpoint
* distinguish architecture from implementation
* avoid speculative abstraction
* use implementation evidence to refine deferred details

Implementation rhythm:

ONE ARCHITECTURAL DECISION
|
v
ONE SMALL IMPLEMENTATION
|
v
COMPILE
|
v
FOCUSED TEST
|
v
FULL REGRESSION
|
v
STOP

---

# 22. Part 2A Objective

Part 2A is:

# Minimal Project Skeleton and Profile Model First Milestone

Do not attempt the complete application.

The purpose of Part 2A is to establish the first concrete project-owned boundary:

Connection Profile

Specifically, begin with the smallest useful STDIO profile model.

Likely initial semantic fields:

* display_name
* explicit STDIO transport identity
* command
* args
* optional cwd

Environment/credential configuration is architecturally expected but should be introduced in a later small milestone rather than bundled into the first implementation unless concrete code structure proves it must be present immediately.

---

# 23. Part 2A Initial Non-Goals

Do not initially implement:

* actual MCP connection
* StdioServerParameters translation
* stdio_client()
* Client()
* Streamable HTTP
* server inspection
* list_tools()
* list_resources()
* list_resource_templates()
* list_prompts()
* pagination
* result DTOs
* terminal rendering
* profile-file loading
* credential resolution
* automatic server research/resolution

Part 2A should establish the bottom-most project-owned configuration boundary first.

---

# 24. Recommended First Part 2A Review

Before writing the first production code:

1. inspect the actual current project directory
2. inspect pyproject.toml if present
3. inspect requirements/dependency declarations if present
4. determine whether a src/mcp_details package already exists
5. determine whether tests already exist
6. identify the smallest filesystem/package change required
7. confirm the exact first STDIO profile contract
8. only then propose the first implementation

Do not invent the current repository state.

Ask for or inspect concrete project files before changing them.

---

# 25. Expected First Implementation Rhythm

The likely first implementation should be approximately:

Part 2A.1
Review repository/package baseline
|
STOP

Part 2A.2
Establish minimal package skeleton if required
|
compile/import check
|
regression
|
STOP

Part 2A.3
Introduce smallest STDIO profile model
|
compile
|
focused tests
|
regression
|
STOP

The exact subdivision should be decided from the actual repository state rather than assumed in advance.

---

# 26. Authoritative Context Files for the New Chat

Use these as the primary project context:

* MCP_DETAILS_PROJECT_CONTEXT.md
* Part_1_Completion_Note.md
* PART2_CONTEXT_20260830.md
* ARCHITECTURAL_DECISION_LEDGER.md, if created/updated

Part 1 architectural decisions should be treated as established unless new implementation evidence creates a concrete reason to revisit one.

---

# 27. Current Project Status

PART 1 — ARCHITECTURE FOUNDATION

COMPLETE

PART 2 — INITIAL IMPLEMENTATION

READY TO BEGIN

NEXT:

Part 2A — Minimal Project Skeleton and Profile Model First Milestone
