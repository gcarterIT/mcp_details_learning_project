# MCP Details Learning Project — Architectural Decision Ledger'

her## Part 1 Architectural Decision Ledger summary.

ID	Decision	Status
AD-001	Explicit resolved connection profiles; no automatic MCP-name resolver	Accept
AD-002	Capability inspection is separate from capability execution	Accept
AD-003	Ordinary inspection stops before call_tool, read_resource, get_prompt	Accept
AD-004	Old demo workflows will not be reused	Accept
AD-005	Old MCPConnection is reference material, not code to copy unchanged	Accept
AD-006	Transport mechanics must be separated from MCP session/inspection logic	Accept
AD-007	STDIO first; Streamable HTTP later	Accept
AD-008	Discovery logic must be presentation-independent	Accept
AD-009	Complete inventory means following pagination until exhausted	Accept
AD-010	Preserve raw JSON Schema and server-supplied metadata; do not invent missing information	Accept
AD-011	A project-owned aggregate inspection result is justified	Accept conceptually; exact model deferred
AD-012	Do not duplicate every SDK MCP model into project-owned DTOs yet	Accept
AD-013	Connection profile is project-owned configuration, not merely serialized SDK objects	Accept
AD-014	SDK version for new project requires explicit review because v2 is now stable	Unresolved intentionally


## AD-001 — Require Explicit Resolved Connection Profiles

**Status:** Accepted
**Part:** Part 1 — Initial Architecture and Reuse Review
**Date:** 2026-08-23

### Question

Should MCP Details automatically resolve an arbitrary MCP identifier, such as:

```text
weather-mcp/weather-mcp
```

into the information required to connect to the MCP server?

Or should MCP Details initially require explicit, already-resolved connection information?

### Evidence

An arbitrary MCP identifier does not necessarily contain sufficient information to establish an MCP connection.

Such an identifier could represent:

* a GitHub repository,
* an MCP registry identifier,
* a package,
* a vendor-specific server name,
* or an informal human-readable label.

Establishing an MCP connection may require additional information such as:

```text
transport type
command or executable
command-line arguments
environment-variable requirements
working directory
Streamable HTTP URL
HTTP headers
authentication information
```

Researching or resolving an MCP server therefore represents a different responsibility from inspecting an already-connectable MCP server.

The project context establishes the intended separation as:

```text
MCP DISCOVERY / RESEARCH
        ≠
MCP CONNECTION
```

and proposes the initial flow:

```text
MCP research / resolution
        │
        ▼
explicit connection profile
        │
        ▼
MCP Details inspector
```

### Decision

Version 1 of MCP Details will **not automatically resolve arbitrary MCP identifiers into connection information**.

The user will first research the MCP server and determine the information required to connect to it.

That resolved information will then be supplied to MCP Details through an explicit connection profile.

Therefore, the responsibility boundary is:

```text
OUTSIDE MCP DETAILS
===================

Find an MCP server
        │
        ▼
Research authoritative documentation
        │
        ▼
Determine how to connect
        │
        ▼
Create resolved connection profile


INSIDE MCP DETAILS
==================

Receive resolved connection profile
        │
        ▼
Connect
        │
        ▼
Initialize
        │
        ▼
Inspect advertised MCP capabilities
        │
        ▼
Produce inspection information
```

### Contract Created / Protected

The MCP Details inspection subsystem begins with **resolved connection configuration**.

It does not require an arbitrary server name, repository name, registry identifier, or package identifier to be independently resolvable.

Conceptually:

```text
Resolved Connection Profile
        │
        ▼
MCP Details
```

rather than:

```text
Arbitrary MCP Identifier
        │
        ▼
MCP Details
        │
        ▼
discover/install/resolve/connect
```

The connection profile will eventually contain the transport-specific information necessary to establish either an STDIO or Streamable HTTP connection.

The exact profile model and file format remain separate architectural decisions.

### Alternatives Deliberately Deferred

The following capabilities are **not rejected permanently**, but are outside the initial project boundary:

* automatic MCP Registry resolution,
* automatic GitHub repository inspection,
* automatic package discovery,
* automatic package installation,
* vendor-specific server resolution,
* converting human-readable MCP names into connection profiles,
* automatic credential discovery,
* a general MCP server resolver subsystem.

A future project phase may introduce a separate resolution subsystem if a demonstrated requirement justifies it.

Conceptually, such a future architecture could become:

```text
MCP Identifier
        │
        ▼
Resolver
        │
        ▼
Resolved Connection Profile
        │
        ▼
MCP Details Inspector
```

The important architectural constraint is that such a resolver should remain distinct from the MCP inspection responsibility.

## 8/25/26 update
## --------------
AD-014	SDK version for new project requires explicit review because v2 is now stable - Accepted: target MCP Python SDK 2.x


## 8/27/26 5:00 pm update
## ----------------------

AD-015 — Use the v2 Client as the primary MCP client boundary

Decision

MCP Details will use the documented high-level v2 Client as its normal MCP interaction boundary.

Contract

Inspection code should not recreate protocol-era negotiation or manually center itself around ClientSession.initialize().

Deferred

Low-level ClientSession use where the high-level API is insufficient.

AD-016 — Delegate modern/legacy negotiation to the SDK

Decision

Use the default automatic protocol negotiation behavior unless a concrete future requirement demands otherwise.

Conceptually:

MCP Details
      ↓
Client(mode="auto")
      ↓
SDK handles discover/fallback

Deferred

Forcing legacy mode, pinning a protocol version, project-owned negotiation logic.

AD-017 — Do not copy or immediately replace MCPConnection

Decision

The old class remains architectural reference material.

No new project-owned connection wrapper will be introduced until a project responsibility exists that the SDK Client does not already own.

AD-018 — Use common server-description properties across protocol eras

Decision

The project should conceptually collect:

protocol_version
server_info
server_capabilities
instructions

regardless of whether those facts originated through modern discovery or legacy initialization.

Deferred

Exact project-owned result model.

AD-019 — Preserve underlying protocol discovery evidence when justified

Decision

Because MCP Details exists to inspect servers in detail, the eventual inspection result should be capable of retaining the raw SDK discovery/initialization result where useful rather than reducing everything to four convenience properties.

Deferred

Exact representation and serialization policy.

## 8/27/26 10:00 pm update
## -----------------------


AD-020 — Respect Advertised Server Capabilities

Decision

MCP Details will issue primitive-list operations only for project-scope capability categories advertised by the server.

It will not deliberately probe unadvertised capability-gated methods during ordinary inspection.

Contract

advertised
    ↓
inspect

not advertised
    ↓
record unsupported/not advertised

Deferred

Protocol-conformance probing mode.

AD-021 — Complete Inventory Requires Pagination Exhaustion

Decision

A primitive inventory is complete only after every returned pagination cursor has been followed until no further cursor remains.

Contract

One successful first page does not constitute complete inspection when nextCursor is present.

AD-022 — Preserve Partial Inspection Results

Decision

If retrieval succeeds for some pages and later fails, previously collected information is retained and the category is marked incomplete/partial.

Contract

Partial evidence must not be represented as a complete inventory or discarded unnecessarily.

AD-023 — Primitive Categories Fail Independently

Decision

After successful connection/server description, failure inspecting one primitive category does not prevent inspection or reporting of other categories.

Contract

tools failure
    ≠
entire report failure
AD-024 — Distinguish Unsupported, Empty, Partial, and Failed

Decision

The inspection architecture must semantically distinguish:

not advertised
successful but empty
successful and populated
partial
failed

Deferred

Exact Python representation.

AD-025 — Preserve Lossless SDK/Protocol Evidence Before Presentation Normalization

Decision

Raw descriptive structures, JSON schemas, metadata, extensions, and relevant list-result metadata must not be discarded merely because the initial terminal renderer does not interpret them.

Contract

Presentation may derive simplified views, but should not define or restrict the stored inspection information.

## 8/28/26 5:00 pm update
## ----------------------

AD-026 — Introduce a Project-Owned Aggregate Inspection Result

Decision

MCP Details will eventually expose one project-owned aggregate representing the outcome of inspecting one MCP server.

Contract

The aggregate must carry both server-description information and independent primitive-category inspection results.

Deferred

Exact Python class and serialization mechanism.

AD-027 — Do Not Clone MCP SDK Semantic Models Initially

Decision

Project-owned result structures will retain documented SDK semantic models such as Tool, Resource, ResourceTemplate, Prompt, ServerCapabilities, and server identity objects rather than copying every field into parallel DTOs.

Contract

The project owns composition and inspection state; the SDK continues to own MCP semantic representation.

Deferred

Project-specific semantic copies only if a concrete portability/versioning/serialization requirement later justifies them.

AD-028 — Represent Primitive Inspection Through a Shared Category Result Concept

Decision

Tools, resources, resource templates, and prompts share one conceptual category-inspection structure.

Each category carries:

inspection status
collected SDK objects
completeness/failure evidence

Contract

A collection alone is insufficient to represent inspection truth.

Deferred

Exact generic Python implementation.

AD-029 — Keep Inspection State Separate From Inventory Size

Decision

SUCCESS represents successful inspection regardless of whether zero or many primitives were returned.

Therefore:

SUCCESS + zero items

is distinct from:

NOT_ADVERTISED

No separate EMPTY inspection status is currently justified.

AD-030 — Separate Target Identity From Server-Reported Identity

Decision

Project/profile information identifying what the user intended to inspect must remain distinct from server_info supplied by the MCP server.

Contract

Neither source of identity silently replaces the other.

Sensitive connection information must not be copied indiscriminately into inspection output.

AD-031 — Presentation Must Consume Structured Inspection Results

Decision

Terminal output will consume the project-owned structured inspection result.

Discovery/inspection logic will not make terminal formatting part of its semantic contract.

Contract

Future renderers should be able to consume the same inspection result without repeating MCP discovery.

## 8/28/26 10:00 pm update
## -----------------------
AD-032 — Use Project-Owned Resolved Connection Profiles

Decision

MCP Details will accept project-owned resolved connection profiles rather than treating SDK transport configuration objects as its public configuration boundary.

Contract

Profiles describe project-level connection intent and are translated into SDK runtime configuration.

AD-033 — Make Transport an Explicit Profile Discriminator

Decision

Every resolved connection profile explicitly identifies its transport.

Initially supported transports:

stdio
streamable_http

Contract

Transport-specific field validation follows from the declared transport rather than inferred combinations of optional fields.

AD-034 — Keep STDIO and Streamable HTTP Configuration Structurally Separate

Decision

STDIO and Streamable HTTP use distinct profile variants rather than one large structure containing every possible transport field.

Contract

STDIO-specific settings cannot accidentally masquerade as HTTP settings and vice versa.

AD-035 — Keep the Initial STDIO Profile Minimal

Decision

The initial STDIO profile concept includes:

display_name
transport
command
args
environment configuration
optional cwd

SDK-specific encoding controls remain deferred unless a real server requires them.

AD-036 — Prefer Runtime Credential References Over Embedded Secrets

Decision

Credentials should normally be represented by references—initially environment-variable references—rather than literal secret values stored in project profiles.

Contract

Credential resolution occurs near connection construction and resolved secret values must not flow into ordinary inspection-result or presentation objects.

AD-037 — Keep Profile Validation Separate From Connection Validation

Decision

Profile validation checks structural correctness.

Runtime connection behavior determines operational validity.

Contract

A structurally valid profile may still fail to connect; that is not a profile-schema failure.

AD-038 — Separate Connection Profiles From Safe Inspection Target Summaries

Decision

MCPInspectionResult should not retain the raw connection profile indiscriminately.

A safe target summary will represent the inspected target without exposing secrets or unnecessary sensitive connection configuration.

AD-039 — Keep Profile Semantics Independent From File Format

Decision

The profile's conceptual model will be established independently of JSON, YAML, TOML, or another persistence format.

Contract

Future profile loaders translate external representation into the same validated project-owned profile semantics.

## 8/30/26 12:00 am update
## -----------------------

AD-040 — Separate Profile, Connection, Inspection, Result, Presentation, and Composition Responsibilities

Decision

MCP Details will maintain distinct ownership for:

profile semantics
connection construction
inspection policy
inspection result representation
presentation
application composition

Contract

No module should absorb another responsibility merely for convenience.

AD-041 — Keep Profile Models Independent of MCP SDK Runtime Objects

Decision

profiles will represent project-owned configuration and will not require MCP SDK transport objects as its semantic model.

Contract

SDK translation occurs in the connection boundary.

AD-042 — Let Connection Own Profile-to-SDK Translation

Decision

The connection layer owns translating validated profiles into appropriate MCP SDK transport/client construction.

It may resolve runtime credential references as part of this responsibility.

AD-043 — Make Inspection Transport-Neutral After Connection

Decision

The inspection subsystem operates on an already-connected SDK Client and does not require STDIO- or HTTP-specific profile details.

Contract

Primitive inspection logic must not branch based on transport.

AD-044 — Keep Inspection Independent From Presentation

Decision

Inspection returns structured project-owned results and does not perform normal terminal rendering.

Contract

Renderers consume MCPInspectionResult; they do not execute MCP discovery operations.

AD-045 — Permit Direct MCP SDK Dependencies Where Semantically Appropriate

Decision

The project will not introduce a generic SDK façade merely to prevent direct use of documented SDK client APIs or semantic types.

Contract

connection, inspection, and result typing may depend directly on appropriate public SDK interfaces.

Deferred

A project-owned SDK compatibility façade unless a concrete compatibility requirement appears.

AD-046 — Do Not Introduce Capability-Specific Workflow Modules

Decision

Version 1 will not create tool/resource/template/prompt workflow modules because MCP Details performs metadata inspection rather than capability execution.

Contract

The primitive categories remain under the shared inspection responsibility unless distinct behavior later justifies extraction.

AD-047 — Keep Composition as the Top-Level Dependency Assembly Boundary

Decision

A thin application composition root will sequence:

profile
connection
inspection
rendering

without owning transport mechanics, inspection policy, or presentation details.
.

## 9/3/26 12:00 am update
## ----------------------

## AD-048 — Shared Private Pagination Mechanics for Inspection Categories

### Context

Complete tools inspection and static resources inspection now demonstrate the same pagination and failure-classification mechanics:

- make the initial list request without a cursor argument
- preserve each successful SDK result page
- continue while `next_cursor is not None`
- pass continuation cursors back unchanged
- return `SUCCESS` when pagination completes
- return `FAILED` when the first request fails
- return `PARTIAL` when a later request fails
- preserve the original exception object

However, capability gating and SDK method selection remain category-specific.

### Decision

Extract the repeated pagination and failure-classification mechanics into a private helper within the inspection module.

Keep the semantic inspection operations explicit:

- `inspect_tools()`
- `inspect_resources()`

The private helper will receive the appropriate SDK list callable rather than an `InspectionCategory`.

`NOT_ADVERTISED` remains the responsibility of the category-specific inspection functions and is not handled by the pagination helper.

The helper is an internal implementation mechanism and is not part of the public MCP Details inspection API.

### Consequences

- Tools and resources retain clear semantic entry points.
- Capability policy remains explicit and category-specific.
- Shared pagination behavior has one implementation.
- Existing tools and resources tests protect the helper indirectly.
- No separate pagination module, pagination class hierarchy, generic category dispatcher, or public paginator API is introduced.
- Future categories may reuse the helper only if their concrete SDK behavior satisfies the same pagination contract.



## 9/5/26 10:00 pm update
## -----------------------

## AD-026 — Extension

Aggregate Inspection Preserves Established Evidence Directly

MCPInspectionResult stores ServerDescription plus the four independent
CategoryInspection results directly. It does not flatten SDK result pages
or duplicate primitive inspection state.


Aggregate Status Is Not Stored Initially

MCPInspectionResult does not contain an independently stored overall status.
Any future aggregate summary state should preferably be derived from the
authoritative primitive-category results.


Complete Inspection Owns Primitive Failure Isolation

After server description is available, a FAILED or PARTIAL primitive
inspection result does not suppress inspection of the remaining primitive
categories.


Initial Complete Inspection Is Sequential

Complete inspection initially invokes primitive inspection operations
sequentially. Exact primitive invocation order is not a public contract.
Concurrency may be reconsidered only if demonstrated need and Client/server
behavior justify it.


Server-Description Failure Is Not Normalized Into Category State

Unexpected failure while obtaining required server-description evidence
propagates rather than producing a synthetic primitive-category or aggregate
failure result.


Aggregate Result and Orchestration Remain in Existing Modules

MCPInspectionResult belongs in results.py and inspect_mcp() belongs in
inspection.py. No additional orchestration/service module is justified yet.

## 9/8/26 8:33 pm update
## ---------------------

## AD-032 — Aggregate Inspection Preserves Established Evidence Directly

**Status:** Accepted

**Decision**

`MCPInspectionResult` is the project-owned aggregate result for one complete MCP inspection.

It directly preserves:

- `ServerDescription`
- `CategoryInspection[ListToolsResult]`
- `CategoryInspection[ListResourcesResult]`
- `CategoryInspection[ListResourceTemplatesResult]`
- `CategoryInspection[ListPromptsResult]`

The aggregate does not flatten SDK result pages, replace the primitive category results with alternate representations, or duplicate primitive inspection state.

**Rationale**

The primitive inspection boundary already preserves authoritative project state and SDK semantic evidence. The aggregate should compose those established results rather than reinterpret them.

This preserves:

- independent category status,
- successful and partial page evidence,
- original failures,
- SDK semantic result objects,
- pagination evidence,
- future SDK fields.

Presentation-specific flattening or normalization remains downstream.

---

## AD-033 — Aggregate Inspection Status Is Not Stored Initially

**Status:** Accepted

**Decision**

`MCPInspectionResult` does not initially store an independent overall inspection status such as `SUCCESS`, `PARTIAL`, or `FAILED`.

Any future overall summary state should preferably be derived from the authoritative primitive-category results when a concrete consumer requires it.

**Rationale**

The category results already contain the authoritative inspection states.

Storing an additional aggregate status would duplicate derived truth and could allow contradictory state such as an aggregate marked successful while one primitive category is failed.

This follows the project principle that derived truths should preferably be computed from authoritative stored facts rather than independently stored.

---

## AD-034 — Complete Inspection Orchestration Owns Primitive Failure Isolation

**Status:** Accepted

**Decision**

`inspect_mcp(client)` coordinates complete inspection of an already-connected MCP SDK `Client`.

After server-description evidence is successfully established, a `FAILED` or `PARTIAL` result from one primitive category does not suppress inspection of the remaining primitive categories.

Primitive inspection functions remain responsible for converting expected list-operation failures into `CategoryInspection` state.

The aggregate orchestrator preserves those results and continues.

**Rationale**

Tools, resources, resource templates, and prompts are independently useful inspection categories.

Failure of one category must not discard discoverable evidence from another category.

The orchestrator does not introduce a second exception-normalization layer or blanket-catch programming errors.

---

## AD-035 — Initial Complete Inspection Is Sequential

**Status:** Accepted

**Decision**

The initial implementation of `inspect_mcp(client)` invokes the established inspection operations sequentially.

The current implementation is conceptually:

1. inspect server description,
2. inspect tools,
3. inspect resources,
4. inspect resource templates,
5. inspect prompts,
6. construct `MCPInspectionResult`.

The exact primitive-category invocation order is not a public architectural contract.

Concurrency may be reconsidered later only if a demonstrated performance need and sufficient MCP SDK/server behavior evidence justify it.

**Rationale**

Sequential orchestration is the smallest understandable implementation and avoids introducing unsupported assumptions about:

- concurrent use of one MCP `Client`,
- server request concurrency,
- cancellation behavior,
- concurrent failure aggregation,
- nondeterministic diagnostics.

No demonstrated requirement currently justifies that complexity.

---

## AD-036 — Server-Description Failure Is Not Normalized Into Primitive Category State

**Status:** Accepted

**Decision**

Unexpected failure while establishing the required `ServerDescription` for a supposedly already-connected client propagates normally.

The project does not currently introduce:

- `ServerDescriptionInspection`,
- a synthetic aggregate failure object,
- synthetic `FAILED` primitive results for categories that were never meaningfully inspected.

**Rationale**

Server-description evidence and primitive list operations have different semantics.

Primitive categories represent independently attempted discovery operations and therefore have structured inspection state.

Server description is currently obtained from the negotiated state of an already-connected client.

No concrete failure case currently justifies introducing another result-state abstraction.

---

## AD-037 — Aggregate Result and Orchestration Remain in Existing Inspection Modules

**Status:** Accepted

**Decision**

`MCPInspectionResult` remains in:

`src/mcp_details/results.py`

and complete inspection orchestration remains in:

`src/mcp_details/inspection.py`

through:

`inspect_mcp(client)`.

No separate `orchestrator.py`, `service.py`, `aggregate.py`, registry, dispatcher, or inspection-service class is introduced.

**Rationale**

The existing modules already have clear responsibilities:

- `results.py` owns project-owned inspection result semantics.
- `inspection.py` owns inspection policy over an already-connected client.

A new module or service object would currently add indirection without introducing a distinct responsibility.

## 9/10/26 6:13 pm update
## ---------------------

## Decision — Application-Level Result Composes Safe Target Identity with Inspection Evidence

### Status

Accepted — Part 2D.1A

### Decision

The application-level result will compose a safe project-owned target summary
with the existing aggregate inspection result.

The current structure is conceptually:

```text
ApplicationInspectionResult
├── target: InspectionTargetSummary
└── inspection: MCPInspectionResult

InspectionTargetSummary currently contains:

configured display name
transport identity

It deliberately does not retain the raw connection profile, command,
arguments, working directory, live SDK Client, connection state, or future
credential material.

Rationale

Downstream consumers such as presentation need to know which configured target
was inspected, but they do not need connection mechanics.

Keeping a safe target summary prevents unnecessary propagation of runtime and
potentially sensitive configuration while preserving useful project-owned
identity.

The existing MCPInspectionResult remains authoritative inspection evidence
and is composed directly rather than flattened or reconstructed.

Consequences
Presentation can consume configured target identity safely.
Raw profiles do not need to flow into presentation.
The application result does not retain a live connection.
Inspection evidence remains structurally identical to the Part 2C result.
Future target-summary fields should be added only when downstream consumers
have a demonstrated need.
Decision — Configured Target Identity and Server-Reported Identity Remain Distinct
Status

Accepted — Part 2D.1A; verified end-to-end in Part 2D.1C-A

Decision

Project-configured target identity and MCP server-reported identity are
separate authoritative facts and will not be silently merged.

Configured identity is represented by:

ApplicationInspectionResult.target

Server-reported identity is represented by:

ApplicationInspectionResult
    .inspection
    .server_description
    .server_info

A mismatch between these identities is not automatically considered an error.

Rationale

The configured display name describes the target as known to the project or
user.

The negotiated server identity describes what the connected MCP server reports
about itself.

These facts originate from different authorities and may legitimately differ.

Consequences
Presentation should preserve and clearly distinguish both identities.
Server identity must not overwrite configured identity.
Configured identity must not be treated as negotiated server evidence.
Future identity comparison or mismatch policy, if required, should be a
separate explicit architectural decision.
Decision — Application Composition Owns Connection Lifetime Scope, Not Lifecycle Mechanics
Status

Accepted — Part 2D.1B

Decision

The application composition boundary determines the scope during which the MCP
connection must remain active.

The MCP SDK high-level Client remains responsible for the actual mechanics of
connection establishment, MCP negotiation, and cleanup.

The conceptual pattern is:

construct Client
      ↓
async with Client
      ↓
inspect_mcp(client)
      ↓
leave Client context
      ↓
return structured result
Rationale

Application policy must determine when inspection occurs relative to connection
lifetime.

Reimplementing transport startup, shutdown, ClientSession, or cleanup logic
would duplicate responsibilities already provided by the SDK.

Consequences
application.py owns the lifetime scope.
SDK Client owns lifecycle mechanics.
No custom connection manager is currently justified.
No manual ClientSession or manual initialization is introduced.
Returned application results do not depend on an active connection.
Decision — Unexpected Inspection Exceptions Propagate After Deterministic Client Cleanup
Status

Accepted — Part 2D.1B

Decision

If an unexpected exception escapes inspect_mcp() while the SDK Client
context is active, the Client context is allowed to exit and perform cleanup,
after which the original exception propagates unchanged.

The application layer does not currently normalize that exception into an
application status or custom exception.

Rationale

Part 2C already represents expected primitive inspection failures using
CategoryInspection statuses and preserved failure evidence.

Unexpected orchestration/programming failures are semantically different and
should not be silently converted into the same result model without a concrete
requirement.

The SDK async context manager already provides the appropriate cleanup
mechanism.

Consequences
Primitive FAILED and PARTIAL states remain structured inspection
evidence.
Unexpected inspection exceptions remain exceptional.
The original exception object is preserved.
Client cleanup occurs before propagation.
A future application exception policy requires a separate architectural
review.
Decision — Connection Failures Remain Propagating Failures
Status

Accepted / Deferred for further normalization — Part 2D.1B

Decision

Connection construction, connection establishment, and MCP negotiation
failures are currently allowed to propagate.

No project-owned connection-failure DTO, application-wide failure status, or
custom connection exception hierarchy is introduced at this stage.

Rationale

The project does not yet have a demonstrated requirement for normalized
connection failure results.

Introducing such a model during initial application composition would create
new semantics without sufficient evidence.

Consequences
inspect_stdio_profile() returns an ApplicationInspectionResult only when
application composition reaches a successful structured inspection result.
Connection failures remain exceptions.
Presentation of successfully returned inspection results can proceed
independently of a future connection-failure UX policy.
Connection-failure normalization remains available for later architectural
review if concrete application requirements justify it.
Decision — Keep the First Application Operation STDIO-Specific
Status

Accepted — Part 2D.1B

Decision

The first application-level operation is explicitly STDIO-specific:

inspect_stdio_profile(
    profile: StdioConnectionProfile,
) -> ApplicationInspectionResult

The project will not yet introduce a generic inspect_profile() dispatcher,
transport registry, connection factory, profile union, or transport strategy
hierarchy.

Rationale

STDIO is currently the only implemented project-owned transport profile.

A generic multi-transport abstraction would therefore be based on anticipated
rather than observed commonality.

Streamable HTTP will provide the second concrete transport case from which a
justified common abstraction can later be derived.

Consequences
Current code remains explicit and easy to understand.
STDIO-specific translation remains in the connection boundary.
Transport-neutral inspection remains reusable.
Generic transport composition is deferred until another real transport
exists.
Decision — Protect the Application Boundary with One Real STDIO Integration Proof
Status

Accepted and verified — Part 2D.1C / Part 2D.1C-A

Decision

The project will maintain one real application-level STDIO integration proof
that invokes inspect_stdio_profile() directly using the existing minimal
STDIO MCP test server.

The test proves the complete path:

StdioConnectionProfile
        ↓
application composition
        ↓
real SDK parameter translation
        ↓
real SDK Client
        ↓
real STDIO subprocess
        ↓
real MCP negotiation
        ↓
transport-neutral inspection
        ↓
ApplicationInspectionResult
Rationale

Part 2B already proves the real STDIO connection boundary, and focused
Part 2D.1B tests protect composition and lifecycle semantics.

One application-level integration test provides valuable seam evidence that
all real components compose correctly without duplicating the exhaustive
lower-level test suites.

Consequences
The real application operation has end-to-end evidence.
The existing minimal STDIO test server is reused.
No separate integration framework is introduced.
Additional real STDIO application tests are not currently justified unless
a new architectural contract appears.
The integration proof does not duplicate pagination, capability-gating, or
primitive failure tests already owned by Part 2C.

## 9/12/26 7:37 pm update
## ----------------------

### AD-041 — Keep Primitive Presentation Renderers Explicit and SDK-Shape-Aware

**Decision**

Presentation maintains separate explicit renderers for Tools, Resources,
Resource Templates, and Prompts.

Shared presentation abstractions are introduced only where semantics are
genuinely identical across primitive categories.

The common inventory-outcome behavior for successful-empty inventories and
retained failures is shared through a small private helper. Primitive page
traversal and item formatting remain explicit within each primitive renderer.

Prompt arguments remain nested Prompt evidence rather than becoming a separate
primitive presentation category.

Presentation may iterate across retained pagination pages and present their
items as one human-readable inventory, but the authoritative paginated SDK
results remain unchanged in the inspection result.

**Rationale**

Although all primitive renderers contain superficially similar page/item loops,
their protocol semantics and displayed fields differ materially:

- Tools render input/output schemas.
- Resources render concrete URIs and optional size.
- Resource Templates render URI templates and have no resource size.
- Prompts render nested Prompt arguments and preserve the three-state
  `required` field without coercing an unspecified value to false.

A generic primitive renderer or generic pagination abstraction would therefore
replace clear SDK-aware code with callbacks, selectors, or configuration
without providing meaningful semantic reuse.

**Consequences**

- Primitive renderers remain straightforward to read and test.
- Shared inventory outcome semantics remain consistent across all four
  categories.
- SDK/protocol distinctions remain visible in presentation code.
- Future abstraction remains possible if additional presentation surfaces or
  repeated semantic responsibilities provide concrete evidence for it.
  
## 9/15/26 9:14 pm update
## ---------------------

## AD-042 — Render Server Capabilities as Independent Authoritative Evidence

**Status:** Accepted

### Decision

Server capabilities are preserved and rendered as authoritative MCP SDK semantic evidence independently from primitive inspection statuses.

Known capability structures are rendered explicitly according to their SDK semantics:

- presence-only capabilities are reported as advertised;
- optional boolean details preserve the distinction between `True`, `False`, and `None`;
- nested capability structures preserve their meaningful hierarchy;
- open `experimental` and `extensions` mappings are rendered as structured JSON without application-level semantic interpretation.

Capability advertisement is not inferred from primitive inspection outcomes, and primitive inspection outcomes are not inferred from capability advertisement.

The presentation layer does not manufacture an aggregate inspection status from either source.

### Rationale

Server capability advertisement and application-observed inspection results represent different authoritative facts.

For example, a server may advertise tools support while a subsequent tools inspection fails. Both facts must remain visible rather than being collapsed into a single derived state.

Explicit rendering also preserves the MCP SDK's semantic structure without introducing speculative capability DTOs, reflection-based rendering, or application-specific interpretations of open extension data.

### Consequences

- `ServerCapabilities` remains authoritative SDK semantic evidence.
- Primitive `CategoryInspection` status remains authoritative application inspection evidence.
- Capability and inspection evidence may legitimately differ.
- Known capability structures are rendered explicitly.
- Open experimental and extension data is preserved without interpretation.
- No separate capability DTO is introduced.
- No generic reflection-based capability renderer is introduced.
- No aggregate inspection status is introduced.
- Future capability support should be added only when justified by concrete SDK or application requirements.

## 9/16/26 6:36 pm update
## ----------------------

## 6. Architectural Decision Ledger addition

I recommend **one new durable decision** from the manual acceptance work. It is distinct from AD-042 and captures a principle we actually learned through evidence.

If AD-042 is currently your latest decision, number this **AD-043**:

```markdown
## AD-043 — Protect Top-Level Presentation Composition as a Behavioral Contract

**Status:** Accepted

### Context

During Part 2D.2C.5 manual end-to-end STDIO acceptance testing, the
terminal report rendered the complete Tools section twice.

The structured inspection result contained exactly one tools page and
one representative tool, proving that the duplication did not originate
from the MCP server, transport, pagination, inspection, or structured
result boundary.

Source review showed that `render_report()` accidentally composed
`_render_tools(inspection.tools)` twice.

The existing automated presentation tests verified that expected
category evidence was present, but presence assertions did not detect
duplicate top-level composition.

### Decision

Top-level report composition is treated as a behavioral presentation
contract.

For each authoritative primitive category currently represented by
`ApplicationInspectionResult`, `render_report()` must compose exactly one
top-level category section:

- Tools;
- Resources;
- Resource Templates;
- Prompts.

Tests should protect this observable report behavior rather than private
implementation details such as the number of times a particular private
renderer function is invoked.

### Rationale

A report may contain all required evidence and still be behaviorally
incorrect if that evidence is accidentally composed multiple times.

Testing only for presence is therefore insufficient at the application
report-composition boundary.

Protecting the public rendered result preserves implementation freedom
while detecting duplication or omission of authoritative category
sections.

### Consequences

- Core report-composition tests protect both presence and single
  composition of primitive-category sections.
- Tests do not mock or count calls to private renderer functions merely
  to enforce this behavior.
- Primitive renderer implementations remain independent of the
  top-level composition contract.
- Duplicate category composition is treated as a presentation defect.
- No generic renderer framework or additional presentation abstraction
  is required.
- Manual end-to-end acceptance remains valuable as complementary
  evidence to automated unit and integration tests.
  
## 9/19/26 4:19 pm update
## ----------------------
  
### AD-049 — Use the SDK Client URL Contract Directly for Minimal Streamable HTTP

**Decision**

For the initial unauthenticated Streamable HTTP path, MCP Details passes the
resolved profile URL directly to the MCP SDK `Client`.

No project-owned Streamable HTTP target builder, connection wrapper, factory,
registry, or transport strategy is introduced while the required translation
remains only:

`profile.url -> Client(profile.url)`

The application layer constructs the transport-specific SDK client and then
delegates the shared connected-client lifecycle to the private application
composition helper.

**Rationale**

The installed MCP Python SDK 2.1.1 already accepts a URL string as a supported
`Client` server target and owns Streamable HTTP transport construction,
protocol negotiation, and connection lifecycle mechanics.

A project-owned abstraction that merely converts a string to the same string
would not own meaningful project behavior.

STDIO remains intentionally asymmetric because its project-owned profile must
be translated into `StdioServerParameters`.

A real Streamable HTTP integration test verifies the complete path through a
real SDK client, real HTTP transport, real MCP negotiation, and real MCP
server.

**Consequences**

- `connection.py` does not require a Streamable HTTP builder for the minimal
  path.
- `inspect_streamable_http_profile()` may construct `Client(profile.url)`
  directly.
- Shared client lifecycle and inspection composition remain transport-neutral
  after Client construction.
- Future HTTP requirements such as authentication, headers, credential
  resolution, TLS configuration, or custom HTTP-client behavior may justify
  introducing additional connection-layer construction when those
  requirements actually exist.
- Transport symmetry is not itself a reason to introduce an abstraction.

### AD-050 — Share Application Lifecycle Only After Transport-Specific Client Construction

**Decision**

Transport-specific application entry points remain responsible for constructing
an MCP SDK `Client` from their respective project-owned connection profiles.

After Client construction, the common connected-client lifecycle is delegated
to a private application helper that:

1. enters the SDK Client context,
2. invokes transport-neutral MCP inspection,
3. exits the Client context, and
4. assembles the `ApplicationInspectionResult`.

The shared helper accepts an already-constructed SDK Client and a safe
`InspectionTargetSummary`; it does not accept or dispatch on connection
profiles.

**Rationale**

STDIO and Streamable HTTP require different connection construction:

- STDIO requires translation to `StdioServerParameters`.
- Minimal Streamable HTTP can pass its URL directly to the SDK `Client`.

Their behavior becomes genuinely identical only after Client construction.

Sharing the lifecycle at that point removes demonstrated duplication without
introducing a generic profile hierarchy, connection factory, transport
dispatcher, or transport-aware inspection boundary.

**Consequences**

- Transport-specific connection construction remains explicit.
- Client lifecycle ownership is centralized at the application layer.
- `inspect_mcp()` remains transport-neutral.
- Adding another transport does not automatically require a generic transport
  framework.
- A broader dispatch abstraction should be introduced only if a concrete
  caller later needs to operate on an unknown profile variant.

## 9/26/26 4:19 pm update
## ----------------------

AD-051 — Keep the executable entry boundary separate from application composition

Decision

The user/process-facing entry boundary will live above the existing application composition boundary. __main__.py and entry.py may handle process invocation, command-line interpretation, synchronous execution bridging, and terminal delivery, while application.py remains independent of CLI/process concerns.

Rationale

The application boundary already provides reusable Python operations returning structured ApplicationInspectionResult values. Mixing argument parsing, sys.argv, stdout, or process semantics into that layer would couple reusable application behavior to one particular interface.

The resulting direction remains:

process / terminal
       │
       ▼
entry
       │
       ▼
application
       │
       ▼
inspection

Consequences

application.py remains reusable outside a terminal application.
presentation.py remains independent of stdout.
Future interfaces can reuse the existing application boundary.
__main__.py remains a thin Python module-entry adapter.

AD-052 — Use explicit transport-specific terminal commands and existing concrete profiles

Decision

The initial terminal interface will expose the supported transports explicitly as:

stdio
streamable-http

Parsed values are adapted directly into the existing:

StdioConnectionProfile
StreamableHttpConnectionProfile

No additional generic CLI configuration DTO, transport hierarchy, registry, or dispatcher is introduced.

Rationale

The two supported transports have materially different connection semantics.

STDIO requires process configuration:

command
args
cwd

Streamable HTTP requires:

url

The concrete profile types already represent these differences and remain the authoritative project-owned configuration models.

Consequences

Transport selection is visible and understandable.
Profile validation is not duplicated in the entry layer.
STDIO and Streamable HTTP can evolve independently.
A generalized transport dispatcher remains deferred until additional transports or duplication justify one.

AD-053 — Place one synchronous-to-asynchronous bridge at the outer execution boundary

Decision

The terminal-facing execution path remains synchronous at its outer boundary and enters the asynchronous MCP application through a single:

asyncio.run(...)

bridge in entry.py.

Asynchronous behavior continues naturally below that bridge.

Rationale

MCP Client lifecycle and inspection operations are asynchronous, while a conventional terminal invocation begins as a synchronous Python process.

Keeping the bridge near the process boundary avoids spreading event-loop management throughout application and inspection code.

Conceptually:

SYNCHRONOUS

python -m mcp_details
        │
      main()
        │
       run()
        │
   asyncio.run(...)
════════╪══════════════
        │
ASYNCHRONOUS
        │
_run_parsed_arguments()
        │
inspect_*()
        │
async with Client(...)
        │
await inspect_mcp(...)

Consequences

Event-loop ownership has a clear location.
Application and inspection APIs remain naturally asynchronous.
Lower layers do not create their own event loops.
Other asynchronous Python consumers can continue using the async APIs directly without passing through run().

AD-054 — Preserve simple process-failure semantics until a meaningful exception taxonomy exists

Decision

The initial application-entry boundary will distinguish successful report production from process failure without introducing broad runtime exception translation or a detailed exit-code taxonomy.

Argument syntax failures remain owned by argparse. Ordinary runtime exceptions that prevent creation of a valid report propagate to the Python process. Structured category-level inspection failures contained within an ApplicationInspectionResult remain valid report content rather than process failures.

Rationale

The project does not yet have a sufficiently developed application-specific exception taxonomy to reliably distinguish expected connection/configuration failures from SDK failures and programming defects.

A broad:

except Exception:

at the entry boundary could hide useful diagnostic information and incorrectly collapse fundamentally different failures into one artificial category.

Consequences

The initial semantics are:

valid report
    → stdout
    → successful execution

invalid CLI syntax
    → argparse diagnostic
    → nonzero execution

runtime exception before valid result
    → exception propagates
    → nonzero execution

category FAILED/PARTIAL inside valid result
    → rendered report
    → successful application execution

Friendlier runtime error presentation and richer exit-code semantics remain explicitly deferred.
  
## 10/4/26 4:19 pm update
## ----------------------

AD-055 — Represent Additional STDIO Environment Requirements as Runtime References

Decision:
MCP Details represents additional STDIO subprocess environment requirements as
same-name references to variables in the MCP Details process environment.

StdioConnectionProfile stores environment-variable names only, using
environment_variables: tuple[str, ...]. It does not store resolved environment
values.

The terminal entry boundary exposes these references through repeatable
--env NAME options. Values after the STDIO "--" separator remain opaque target
server arguments and are not interpreted as MCP Details options.

Environment-variable references are resolved at the connection-construction
boundary. Each declared reference is required. If a declared variable is absent
from the MCP Details process environment, connection construction fails.

When no environment-variable references are configured,
StdioServerParameters.env remains None, preserving the previous behavior.

When references are configured, MCP Details passes only the explicitly resolved
name/value pairs through StdioServerParameters.env. MCP Details does not copy or
merge the complete parent process environment. Final composition with the SDK's
safe default environment remains the MCP SDK's responsibility.

Rationale:
This keeps resolved runtime values out of project-owned connection profiles,
keeps secret/value resolution close to connection construction, preserves the
SDK's environment-management semantics, and adds the minimum configuration
needed for real STDIO MCP servers that require application-specific environment
variables.

Deferred:
- literal environment values in profiles
- source-to-target environment-variable renaming
- optional environment-variable references
- automatic full parent-environment inheritance
- .env-file loading
- generalized secret-provider abstractions
- cloud secret managers
- persistent secret storage
- HTTP authentication and headers

## 10/7/26 9:38 pm update
## ----------------------

AD-056 — Represent Additional Streamable HTTP Headers as Runtime Environment References

Decision

Streamable HTTP connection profiles may declare additional HTTP-header requirements using explicit mappings from HTTP header names to environment-variable names.

The profile stores only the header name and the environment-variable reference. It does not store the resolved header value.

At connection construction time, MCP Details resolves each referenced environment variable from the current process environment and supplies the resulting header mapping to an MCP SDK HTTP client.

All declared header references are required. If a referenced environment variable is absent, connection construction fails.

The environment-variable value is treated as the complete HTTP header value. MCP Details does not transform, prefix, parse, or otherwise interpret it. For example, an Authorization header requiring a Bearer value may reference an environment variable whose value is already "Bearer <token>".

When a Streamable HTTP profile contains no header references, MCP Details preserves the existing minimal direct-URL Client path. The configured HTTP-client/transport path is used only when additional headers are required.

Rationale

This preserves the distinction between connection configuration and runtime secret material. Profiles can describe how a connection obtains required HTTP headers without embedding credential values in project-owned configuration objects.

Resolving values at the connection boundary keeps runtime credentials out of inspection results and presentation while allowing the connection layer to construct the SDK objects that actually require those values.

Treating the environment value as the complete header value keeps the mechanism generic. MCP Details does not need authentication-scheme-specific behavior such as automatically constructing Bearer tokens.

Preserving the direct URL path for profiles without additional headers avoids unnecessary connection machinery for the minimal Streamable HTTP case and preserves the architecture established in AD-049.

Consequences

- StreamableHttpConnectionProfile may contain zero or more HttpHeaderEnvironmentReference values.
- Each reference identifies an HTTP header name and an environment-variable name.
- Resolved header values are not stored in the profile.
- Missing referenced environment variables cause connection-construction failure.
- MCP Details supplies only the explicitly configured additional headers.
- The MCP SDK remains responsible for MCP protocol-specific HTTP headers and transport behavior.
- Header values may contain credentials without those credentials being embedded in the profile or CLI arguments.
- The CLI exposes repeatable --header-env HEADER ENV_VAR configuration.
- Profiles without header references continue to use the direct Client(profile.url) path.
- Profiles with header references use the configured HTTP-client/Streamable-HTTP transport path.
- HTTP-client lifetime for the configured path is owned by the connection-construction context; MCP Client lifetime remains owned by the application composition boundary.

Deferred

The following remain outside this decision:

- literal header values stored directly in profiles
- automatic Bearer-prefix construction
- authentication-scheme-specific transformations
- OAuth flows and token refresh
- generalized SDK authentication-provider abstractions
- .env-file loading
- persistent credential storage
- operating-system or cloud secret-manager integration
- optional header references
- duplicate-header policy beyond current mapping semantics
- configurable TLS, proxies, timeouts, and arbitrary HTTP-client injection


