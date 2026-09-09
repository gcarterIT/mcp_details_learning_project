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