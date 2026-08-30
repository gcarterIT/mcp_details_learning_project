# MCP Details Learning Project

# Part 1 Completion Note

**Part:** Part 1 — Architecture Foundation
**Status:** COMPLETE
**Completion Date:** 2026-08-30
**Next Part:** Part 2A — Minimal Project Skeleton and Profile Model First Milestone

---

## 1. Purpose of Part 1

Part 1 established the architectural foundation for the MCP Details Learning Project before production implementation begins.

The project is intended to become a general-purpose MCP inspection application that can connect to an explicitly configured MCP server and describe what that server exposes without executing its advertised capabilities.

The primary architectural principle established during Part 1 is:

> MCP Details performs non-executing capability inspection.

Normal inspection may discover and list MCP capabilities and their metadata, but it must not invoke the capabilities being advertised.

---

## 2. Project Goal

The initial application should be able to inspect an MCP server and report:

* server identity when available
* negotiated protocol information
* server capabilities
* server instructions
* tools
* static resources
* resource templates
* prompts
* descriptions
* tool schemas
* prompt arguments
* annotations and metadata
* pagination information and completeness
* relevant protocol/discovery evidence

The initial presentation target is terminal output.

The architecture should permit future presentation targets such as Markdown, JSON, notebooks, Streamlit, or other interfaces without requiring MCP discovery to be rewritten.

---

## 3. Strict Inspection Boundary

Normal MCP Details inspection may perform operations necessary to describe the server, including:

* connection and protocol negotiation
* server discovery or initialization as handled by the SDK
* list_tools()
* list_resources()
* list_resource_templates()
* list_prompts()
* pagination required to complete those inventories

Normal inspection must stop before capability execution.

It must not ordinarily perform:

* call_tool()
* read_resource()
* get_prompt()
* server-specific workflows
* capability execution merely to determine what a capability does

The important distinction is:

CAPABILITY INSPECTION != CAPABILITY EXECUTION

A more precise internal description is:

NON-EXECUTING CAPABILITY INSPECTION

---

## 4. MCP Python SDK Boundary

Part 1 determined that MCP Details will target MCP Python SDK 2.x.

The project will not initially attempt to support both SDK 1.x and SDK 2.x.

The high-level v2 Client is the primary MCP client abstraction.

The SDK is responsible for protocol-era negotiation, including modern server/discover behavior and fallback to legacy initialization where appropriate.

MCP Details should not recreate this protocol negotiation itself.

The old MCP Client Learning Project's MCPConnection class remains useful reference material but should not be copied unchanged into this project.

A new project-owned lifecycle wrapper should be introduced only if a concrete project-specific lifecycle responsibility emerges.

---

## 5. Transport Boundary

Initial supported transports are:

1. STDIO
2. Streamable HTTP

The architecture remains open to additional transports if genuine requirements arise.

Transport-specific mechanics must remain outside primitive inspection logic.

Conceptually:

Connection Profile
|
v
Connection / SDK Target Construction
|
v
SDK Client
|
v
Transport-Neutral Inspection

Once inspection receives a usable Client, primitive inspection should not need to know whether the connection originated through STDIO or Streamable HTTP.

---

## 6. Explicit Resolved Connection Profiles

Version 1 begins with an explicit resolved connection profile.

The intended workflow is:

Research MCP server
|
v
Determine actual connection requirements
|
v
Create explicit resolved connection profile
|
v
MCP Details connects and inspects

An arbitrary identifier such as:

weather-mcp/weather-mcp

must not be assumed to contain enough information to establish a connection.

Automatic resolution from registries, GitHub repositories, package names, vendor identifiers, or similar sources is deferred.

A future resolver may produce the same project-owned connection-profile model without changing the inspection subsystem.

---

## 7. Connection Profile Architecture

Connection profiles are project-owned configuration structures.

They are not serialized MCP SDK runtime objects.

Every profile should explicitly identify its transport.

Initial conceptual variants are:

* STDIO connection profile
* Streamable HTTP connection profile

The initial STDIO profile concept includes:

* display_name
* transport
* command
* args
* environment configuration
* optional cwd

The initial Streamable HTTP profile concept includes:

* display_name
* transport
* URL
* later, when required, safe header/authentication configuration

The project should expose only configuration required by project use cases rather than automatically mirroring every SDK constructor parameter.

---

## 8. Credential Boundary

Credentials should normally be referenced rather than embedded directly in connection profiles.

The initial preferred credential mechanism is an environment-variable reference.

Conceptually:

Profile
|
| credential reference only
v
Connection Construction
|
| resolve credential near runtime use
v
SDK Transport

Resolved secrets must not flow into ordinary inspection-result or presentation structures.

Connection profiles and safe inspection-target summaries are separate concepts.

A safe target summary may contain information such as:

* display name
* transport
* safe endpoint or command description

but must not indiscriminately expose credentials or secret-bearing configuration.

---

## 9. Server Description

After connection, MCP Details should preserve a common description of the server across protocol eras.

Conceptually this includes:

* protocol version
* server information when available
* server capabilities
* instructions
* underlying protocol discovery/initialization evidence where useful

Modern and legacy protocol paths may produce different underlying SDK evidence.

MCP Details should provide a common interpreted view while retaining richer protocol evidence where justified.

Server-reported identity is self-reported evidence.

It must remain distinct from the project/profile identity of the target being inspected.

---

## 10. Capability-Aware Inspection Policy

MCP Details should inspect only project-scope primitive categories advertised by the server.

It should not normally probe unadvertised capability-gated methods.

Conceptually:

Capability advertised?
|
+-- YES --> inspect category
|
+-- NO  --> record NOT_ADVERTISED and do not probe

This makes MCP Details an inspector of the server's advertised surface rather than a protocol-conformance probe.

A future explicit conformance-testing mode may be considered separately if ever required.

---

## 11. Primitive Inspection Scope

Version 1 deep inventory scope consists of:

* tools
* resources
* resource templates
* prompts

Resources require special attention because one resources capability governs both:

* resources/list
* resources/templates/list

Static resources and resource templates remain independent inventory operations even though they share the same advertised server capability.

Extensions and experimental capability structures should be preserved and reported where available, but Version 1 should not automatically invoke extension-specific operations.

---

## 12. Complete Inspection Definition

Complete inspection means preserving and reporting all metadata made available through permitted MCP discovery and initialization operations across all returned pages, without executing advertised capabilities or inventing absent information.

For every advertised project-scope primitive category:

1. issue the corresponding list operation
2. preserve the returned items
3. preserve relevant result/page metadata
4. follow every valid pagination cursor
5. continue until no next cursor remains

Retrieving only the first page when another cursor exists is incomplete inspection.

---

## 13. Pagination Contract

Pagination exhaustion is a correctness requirement.

Example:

Page 1 -> nextCursor
Page 2 -> nextCursor
Page 3 -> no nextCursor

Only after Page 3 is the category completely inspected.

If:

Page 1 succeeds
Page 2 succeeds
Page 3 fails

then MCP Details must:

* preserve items from Pages 1 and 2
* preserve relevant successful evidence
* record the failure
* mark the category PARTIAL

It must not discard useful partial evidence.

The exact internal page-evidence representation remains deferred until implementation demonstrates what is required to preserve SDK result metadata losslessly.

---

## 14. Category Inspection States

Part 1 established four conceptual category states:

NOT_ADVERTISED

The corresponding server capability was not advertised, so MCP Details did not probe it.

SUCCESS

The category was applicable and every required page was successfully retrieved.

SUCCESS may contain zero items.

PARTIAL

Useful category data was retrieved, but complete inspection could not be achieved.

FAILED

The category was advertised, but no successful complete or partial category inventory could be obtained.

A separate EMPTY status is not currently justified.

Instead:

status = SUCCESS
items = []

means the category was successfully inspected and contained zero advertised primitives.

---

## 15. Independent Category Failure

After successful connection and server-description retrieval, primitive categories should be inspected independently.

For example:

Tools      SUCCESS
Resources  FAILED
Prompts    SUCCESS

must not cause the successful tools and prompts information to be discarded.

One category failure should not automatically abort all remaining primitive inspection.

Top-level connection/server-description failure is different because primitive inspection cannot begin without a usable connection.

---

## 16. Overall Inspection State

Conceptually, the overall inspection may be:

SUCCESS

All applicable advertised categories were completely inspected.

PARTIAL

Connection and server-description retrieval succeeded, but one or more advertised categories were partial or failed.

FAILED

Connection or server-description failure prevented meaningful primitive inspection.

Where practical, overall state should be derived from authoritative stored facts rather than independently stored as redundant state.

This follows the general design principle:

Derived truths should preferably be computed from authoritative stored facts rather than independently stored when practical.

---

## 17. Lossless Evidence Before Presentation

MCP Details is an inspection application.

Therefore information returned by the server should not be discarded merely because the first terminal renderer does not understand or display every field.

Preferred information flow:

SERVER / SDK RESPONSE
|
v
LOSSLESS SEMANTIC REPRESENTATION
|
v
OPTIONAL INTERPRETATION
|
v
TERMINAL PRESENTATION

Important examples include:

* tool schemas
* annotations
* server metadata
* experimental fields
* extensions
* cache/result metadata
* protocol-specific discovery evidence

The application must not invent information that the server did not provide.

---

## 18. Structured Inspection Result Boundary

Part 1 established that MCP Details should eventually expose one project-owned aggregate inspection result.

Conceptually:

MCPInspectionResult
|
+-- target summary
|
+-- server description
|
+-- tools
|     `-- CategoryInspection[Tool]
|
+-- resources |     `-- CategoryInspection[Resource]
|
+-- resource templates
|     `-- CategoryInspection[ResourceTemplate]
|
`-- prompts
`-- CategoryInspection[Prompt]

The exact Python implementation remains deferred.

---

## 19. DTO Ownership Principle

The project should model its own inspection concepts without unnecessarily cloning the MCP SDK's semantic type system.

The key rule is:

MCP SDK owns MCP semantics.

MCP Details owns inspection semantics.

Therefore project-owned structures may contain documented SDK semantic objects such as:

* Tool
* Resource
* ResourceTemplate
* Prompt
* ServerCapabilities
* server identity objects
* DiscoverResult
* InitializeResult

The project should not initially create parallel ToolDTO, ResourceDTO, PromptDTO, and similar copies merely for architectural symmetry.

A project-owned copy should be introduced only if a concrete portability, compatibility, serialization, or semantic requirement later justifies it.

---

## 20. Category Inspection Result Concept

A shared conceptual CategoryInspection[T] is justified because tools, resources, resource templates, and prompts share the same inspection-state behavior.

Conceptually it needs to express:

* inspection status
* collected SDK semantic objects
* completeness/pagination evidence
* failure diagnostic where applicable

The exact generic Python implementation remains deferred.

Redundant booleans such as:

* advertised
* attempted
* successful
* partial
* complete

should be avoided if one authoritative status can express the state without contradiction.

---

## 21. Presentation Boundary

Inspection and presentation must remain separate.

Inspection:

MCP Client
|
v
MCPInspectionResult

Presentation:

MCPInspectionResult
|
v
Terminal Renderer

The renderer may read SDK semantic objects contained in the result.

It must not perform MCP discovery operations itself.

This allows future presentation targets to consume the same inspection result without reconnecting to the MCP server.

---

## 22. Initial Module Responsibility Map

Part 1 established the following conceptual module responsibilities:

### profiles.py

Owns project connection-profile semantics, structural profile validation, credential-reference configuration, and safe target-summary projection.

It should not depend on MCP SDK runtime configuration objects.

### connection.py

Owns translation from validated project profiles to MCP SDK connection targets.

It may:

* construct STDIO SDK parameters
* construct STDIO transport
* construct simple or advanced Streamable HTTP transport
* resolve credential references near runtime use
* participate in SDK Client construction/lifecycle

It should not perform primitive inspection.

### results.py

Owns project inspection-result semantics such as:

* ServerDescription
* CategoryInspection[T]
* MCPInspectionResult
* InspectionTargetSummary as appropriate

It may use public MCP SDK semantic types.

It must not depend upward on inspection or rendering.

### inspection.py

Owns MCP Details inspection policy:

* server-description collection
* capability-aware primitive inspection
* pagination
* partial-result preservation
* category failure independence
* strict non-execution boundary

It operates on an already-usable MCP SDK Client.

It should not depend on transport-specific profile details or terminal presentation.

### rendering.py

Owns human-facing terminal presentation.

It consumes structured inspection results.

It performs no MCP discovery operations.

### app.py / composition root

Owns application sequencing:

profile
|
v
validation
|
v
connection
|
v
inspection
|
v
rendering

It should remain shallow and should not absorb subsystem implementation details.

Exact filenames remain subject to evidence during implementation.

---

## 23. Dependency Direction

The intended dependency direction is approximately:

app
|
+--> profiles
|
+--> connection
|      |
|      +--> profiles
|      `--> MCP SDK
 |
 +--> inspection  |      |  |      +--> results  |      `--> MCP SDK
|
`--> rendering
        |
        `--> results

results
|
`--> MCP SDK semantic types where justified

Important forbidden or undesirable dependency directions include:

* profiles -> connection
* profiles -> inspection
* results -> inspection
* results -> rendering
* inspection -> rendering
* rendering -> connection
* connection -> rendering

Application composition is the expected place where multiple subsystem dependencies meet.

---

## 24. Deliberately Deferred Abstractions

Part 1 deliberately does not introduce:

* automatic MCP identifier resolution
* registry resolution
* GitHub resolution
* package installation
* dual MCP Python SDK v1/v2 support
* project-owned protocol negotiation
* replacement MCPConnection wrapper
* generalized SDK facade
* transport plugin framework
* tool/resource/prompt workflow subsystem
* generalized pagination framework
* standalone validation subsystem
* large exception hierarchy
* complete serialization architecture
* JSON/YAML/TOML profile format decision
* caching subsystem
* protocol-conformance scoring
* capability execution
* resource content reading
* prompt rendering
* tool invocation

These should be introduced only when a concrete requirement justifies them.

---

## 25. Architectural Decision Ledger

The project should maintain one continuously updated root-level:

ARCHITECTURAL_DECISION_LEDGER.md

Part 1 established or recommended the following decisions:

AD-001 — Require Explicit Resolved Connection Profiles

AD-002 — Separate Capability Inspection From Capability Execution

AD-003 — Stop Ordinary Inspection Before call_tool/read_resource/get_prompt

AD-004 — Do Not Reuse Old Demo Workflows

AD-005 — Treat Old MCPConnection as Reference Rather Than Copying It

AD-006 — Separate Transport Mechanics From Session/Inspection Policy

AD-007 — Support STDIO First and Streamable HTTP as the Second Initial Transport

AD-008 — Keep Discovery/Inspection Presentation-Independent

AD-009 — Require Pagination Exhaustion for Complete Inventory

AD-010 — Preserve Raw Schemas and Metadata Without Inventing Information

AD-011 — Use a Project-Owned Aggregate Inspection Result

AD-012 — Do Not Duplicate Every SDK Semantic Type Into Project DTOs

AD-013 — Make Connection Profiles Project-Owned Configuration

AD-014 — Target MCP Python SDK 2.x

AD-015 — Use the v2 Client as the Primary MCP Client Boundary

AD-016 — Delegate Modern/Legacy Protocol Negotiation to the SDK

AD-017 — Do Not Immediately Replace the Old MCPConnection Wrapper

AD-018 — Use Common Server-Description Properties Across Protocol Eras

AD-019 — Preserve Underlying Protocol Discovery Evidence Where Justified

AD-020 — Respect Advertised Server Capabilities

AD-021 — Complete Inventory Requires Pagination Exhaustion

AD-022 — Preserve Partial Inspection Results

AD-023 — Primitive Categories Fail Independently

AD-024 — Distinguish Unsupported, Empty, Partial, and Failed Semantics

AD-025 — Preserve Lossless SDK/Protocol Evidence Before Presentation Normalization

AD-026 — Introduce a Project-Owned Aggregate Inspection Result

AD-027 — Do Not Clone MCP SDK Semantic Models Initially

AD-028 — Represent Primitive Inspection Through a Shared Category Result Concept

AD-029 — Keep Inspection State Separate From Inventory Size

AD-030 — Separate Target Identity From Server-Reported Identity

AD-031 — Presentation Must Consume Structured Inspection Results

AD-032 — Use Project-Owned Resolved Connection Profiles

AD-033 — Make Transport an Explicit Profile Discriminator

AD-034 — Keep STDIO and Streamable HTTP Configuration Structurally Separate

AD-035 — Keep the Initial STDIO Profile Minimal

AD-036 — Prefer Runtime Credential References Over Embedded Secrets

AD-037 — Keep Profile Validation Separate From Connection Validation

AD-038 — Separate Connection Profiles From Safe Inspection Target Summaries

AD-039 — Keep Profile Semantics Independent From File Format

AD-040 — Separate Profile, Connection, Inspection, Result, Presentation, and Composition Responsibilities

AD-041 — Keep Profile Models Independent of MCP SDK Runtime Objects

AD-042 — Let Connection Own Profile-to-SDK Translation

AD-043 — Make Inspection Transport-Neutral After Connection

AD-044 — Keep Inspection Independent From Presentation

AD-045 — Permit Direct MCP SDK Dependencies Where Semantically Appropriate

AD-046 — Do Not Introduce Capability-Specific Workflow Modules

AD-047 — Keep Composition as the Top-Level Dependency Assembly Boundary

The ledger remains the authoritative record of why these architectural decisions were made and which alternatives were deliberately deferred.

---

## 26. Part 1 Closure Assessment

Part 1 is architecturally complete enough to begin implementation.

The following major questions have been resolved:

* SDK version boundary
* high-level MCP Client boundary
* protocol negotiation ownership
* transport boundary
* inspection/execution boundary
* capability-aware discovery policy
* pagination completeness
* partial failure semantics
* category independence
* structured inspection-result boundary
* SDK semantic-type ownership
* connection-profile boundary
* credential-handling boundary
* target/server identity distinction
* presentation boundary
* module responsibilities
* dependency direction

No further broad architectural review is required before beginning the first implementation milestone.

Architecture should continue to be reviewed locally as concrete implementation evidence emerges.

---

## 27. Next Part

Proceed to:

# Part 2A — Minimal Project Skeleton and Profile Model First Milestone

The first implementation should be intentionally small.

The initial target is only the lowest project-owned input boundary:

Connection Profile
|
v
Minimal STDIO Profile Model

The first milestone should establish only the minimum required project structure and STDIO profile semantics, likely including:

* display_name
* explicit STDIO transport identity
* command
* args
* optional cwd

Do not implement the entire connection subsystem.

Do not connect to an MCP server yet.

Do not implement Streamable HTTP yet unless the architectural review of the concrete profile implementation demonstrates that a shared discriminator must be represented immediately.

Do not implement inspection.

Do not implement rendering.

Do not introduce speculative profile-file serialization.

---

## 28. Teaching and Implementation Contract for Part 2

Continue using the established project method:

1. architecture before implementation
2. professor/software-architect teaching style
3. extremely small milestones
4. explain the responsibility and contract before code
5. implement only one small architectural increment
6. compile immediately
7. run focused tests
8. run the full regression suite
9. stop at every checkpoint
10. separate architectural decisions from implementation details
11. preserve behavior and architectural boundaries
12. do not introduce abstractions merely for future possibilities

The implementation sequence should remain:

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
STOP / CHECKPOINT

---

## 29. Final Part 1 Status

PART 1 — ARCHITECTURE FOUNDATION

STATUS: COMPLETE

The MCP Details Learning Project is ready to transition from broad architectural definition to controlled incremental implementation.
