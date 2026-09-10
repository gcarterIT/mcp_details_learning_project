# MCP Details Learning Project — Part 2D Context

## Context Purpose

This file is the authoritative transition context from completed Part 2C inspection architecture into Part 2D application-composition review.

Part 2D must begin from the architecture documented here and must not redesign completed Part 2C boundaries without concrete new evidence.

---

# 1. Project Goal

MCP Details is a general-purpose, strictly read-only MCP inspection application.

The intended workflow is:

1. research an MCP server,
2. prepare explicit connection information,
3. connect to the server,
4. inspect its discoverable MCP surface,
5. present that information clearly.

Initial transports are:

* STDIO
* Streamable HTTP

The architecture must remain open to additional transports later.

Ordinary inspection must remain strictly read-only.

The application may discover/list:

* server initialization/description information
* tools
* static resources
* resource templates
* prompts
* descriptions
* schemas
* prompt arguments
* server capabilities

It must not execute tools, read resource contents, materialize templates, or render/get prompts as part of ordinary inspection.

---

# 2. Development Contract

Continue using the established project method:

* architecture before implementation
* professor/software-architect teaching style
* extremely small, highly testable milestones
* preserve established behavior exactly
* compile after every implementation milestone
* run focused regression tests
* run the full regression suite after every milestone
* stop at checkpoints
* distinguish architectural decisions from implementation choices
* avoid speculative abstractions
* do not redesign completed boundaries without concrete evidence

---

# 3. Completed Part 2A — Minimal Project Skeleton and STDIO Profile

The minimal package skeleton is established.

The project-owned STDIO profile boundary is represented by `StdioConnectionProfile`.

Its essential contract includes:

```text
name
args: tuple[str, ...]
cwd: optional
transport fixed to STDIO
```

Arguments use an immutable tuple at the project boundary even when the SDK ultimately requires another representation.

---

# 4. Completed Part 2B — STDIO Connection Boundary

A real end-to-end STDIO path has been proven.

Conceptually:

```text
StdioConnectionProfile
        ↓
build STDIO SDK connection parameters
        ↓
high-level MCP SDK Client
        ↓
real subprocess
        ↓
MCP negotiation
        ↓
connected Client
```

The connection boundary owns transport-specific connection concerns.

Inspection does not.

The project remains intended to add Streamable HTTP later without redesigning transport-neutral inspection.

---

# 5. Completed Part 2C — Inspection Boundary

Part 2C is architecturally complete.

The inspection boundary accepts an already-connected high-level MCP SDK `Client`.

It does not accept a STDIO profile or otherwise depend on the transport used to create the client.

The final conceptual API is:

```text
already-connected Client
        ↓
inspect_mcp()
        ↓
MCPInspectionResult
```

---

# 6. Server Description

`ServerDescription` is the project-owned server-description result.

Its current authoritative fields are:

```python
protocol_version: str
server_info: Implementation | None
server_capabilities: ServerCapabilities
instructions: str | None
```

The project does not clone MCP SDK semantic models merely to avoid SDK types.

The project owns project-specific inspection semantics while the SDK continues to own its protocol-semantic result models.

---

# 7. Primitive Inspection Categories

The explicit primitive operations are:

```python
inspect_tools(client)
inspect_resources(client)
inspect_resource_templates(client)
inspect_prompts(client)
```

These remain distinct semantic operations.

There is no generic public `inspect_category()` dispatcher or registry.

Resources and resource templates share the server's resources capability advertisement but remain independent inspection categories.

---

# 8. Capability Policy

Ordinary inspection respects advertised MCP server capabilities.

A category that is not advertised is not listed and is represented as:

```python
CategoryInspection(
    status=InspectionStatus.NOT_ADVERTISED,
    pages=(),
    failure=None,
)
```

Capability advertisement and inspection success/failure are separate truths.

A failed list request does not imply the server failed to advertise that capability.

---

# 9. Category Inspection State

`CategoryInspection[PageT]` is the project-owned result model for one primitive category.

Supported statuses are:

```text
NOT_ADVERTISED
SUCCESS
PARTIAL
FAILED
```

Semantics:

```text
NOT_ADVERTISED
    capability not advertised

SUCCESS
    inspection completed successfully
    zero inventory items is still success

PARTIAL
    at least one page succeeded
    a later page failed
    successful pages and original exception preserved

FAILED
    first request failed
    no successful pages
    original exception preserved
```

There is intentionally no `EMPTY` status.

---

# 10. SDK Page Preservation

Primitive inspection preserves complete MCP SDK result pages:

```python
CategoryInspection[ListToolsResult]
CategoryInspection[ListResourcesResult]
CategoryInspection[ListResourceTemplatesResult]
CategoryInspection[ListPromptsResult]
```

The inspection layer does not flatten these to primitive item tuples.

This preserves authoritative SDK evidence, page boundaries, pagination metadata, future SDK fields, and partial results.

Presentation may derive flattened views later if useful.

---

# 11. Shared Pagination Mechanics

The four primitive inspectors share a private pagination helper.

Its responsibility is limited to:

* first request
* exact opaque cursor continuation
* page preservation
* termination
* SUCCESS/PARTIAL/FAILED classification
* original exception preservation

It does not own:

* capability gating
* semantic category selection
* SDK method selection
* connection
* server description
* aggregate composition
* presentation

The helper remains private.

---

# 12. Read-Only Inspection Contract

The inspection subsystem may perform discovery/list operations.

It must not perform ordinary inspection by:

```text
call_tool()
read_resource()
get_prompt()
materializing a resource template
```

This is a central project policy.

---

# 13. Aggregate Inspection Result

Part 2C introduced:

```python
MCPInspectionResult
```

Its final shape is:

```text
MCPInspectionResult
├── server_description: ServerDescription
├── tools: CategoryInspection[ListToolsResult]
├── resources: CategoryInspection[ListResourcesResult]
├── resource_templates: CategoryInspection[ListResourceTemplatesResult]
└── prompts: CategoryInspection[ListPromptsResult]
```

The aggregate preserves the established results directly.

It does not store a separately maintained overall status.

Any future aggregate summary state should preferably be derived from authoritative category evidence.

---

# 14. Complete Inspection Orchestration

Part 2C introduced:

```python
async def inspect_mcp(client: Client) -> MCPInspectionResult
```

It coordinates:

```text
inspect_server_description()
inspect_tools()
inspect_resources()
inspect_resource_templates()
inspect_prompts()
```

and returns one `MCPInspectionResult`.

The initial implementation is sequential.

The exact category invocation order is not a public architectural contract.

Concurrency is not currently justified.

---

# 15. Primitive Failure Isolation

After server-description evidence is available, primitive categories fail independently.

Example valid aggregate:

```text
tools               FAILED
resources           SUCCESS
resource_templates  SUCCESS
prompts              SUCCESS
```

A failed or partial primitive category must not suppress inspection of later categories.

Resources and resource templates remain independent even though they share capability advertisement.

Expected primitive list failures are normalized by the primitive inspectors into `CategoryInspection`.

`inspect_mcp()` does not blanket-catch unexpected programming defects.

---

# 16. Server-Description Failure

The project does not currently define a structured failure wrapper for server description.

Unexpected failure to establish required server-description evidence from an already-connected client propagates normally.

Do not introduce a `ServerDescriptionInspection` or aggregate failure abstraction without concrete evidence that such a boundary is needed.

---

# 17. Current Module Responsibilities

The key production modules remain:

```text
src/mcp_details/
    __init__.py
    profiles.py
    connection.py
    results.py
    inspection.py
```

Responsibilities:

### `profiles.py`

Project-owned explicit connection-profile semantics.

### `connection.py`

Transport-specific connection construction/lifecycle boundary.

### `results.py`

Project-owned structured inspection results:

* `ServerDescription`
* `InspectionStatus`
* `CategoryInspection`
* `MCPInspectionResult`

### `inspection.py`

Transport-neutral read-only inspection over an already-connected SDK Client:

* server description
* capability gating
* primitive discovery
* pagination
* aggregate inspection orchestration

Do not create extra service/orchestration modules without a distinct responsibility.

---

# 18. Architectural Decisions Relevant to Part 2D

Existing decisions include:

* use explicit connection profiles,
* use the high-level MCP SDK Client boundary,
* keep connection and inspection separate,
* preserve authoritative evidence,
* respect advertised capabilities,
* exhaust pagination,
* preserve partial results,
* keep primitive categories failure-independent,
* distinguish NOT_ADVERTISED/SUCCESS/PARTIAL/FAILED,
* retain SDK semantic result models where appropriate,
* separate target identity from server-reported identity,
* make presentation consume structured inspection results,
* introduce a project-owned aggregate inspection result,
* do not independently store aggregate status,
* keep complete inspection sequential initially,
* keep orchestration in existing inspection modules.

Part 2D must build on these decisions rather than revisiting them without new evidence.

---

# 19. Current Regression State

Part 2C closed only after:

```powershell
python -m compileall src\mcp_details tests
python -m pytest tests\test_results.py -v
python -m pytest tests\test_inspection.py -v
python -m pytest -v
```

all passed.

The exact test count from the user's local final regression run is authoritative.

---

# 20. Part 2D Architectural Problem

Part 2C answered:

> Given an already-connected MCP SDK Client, how should MCP Details inspect the server?

Part 2D should answer:

> How should the application compose an explicit connection target/profile, connection lifetime, transport-neutral inspection, and structured result into one useful application-level operation?

Current separate boundaries are:

```text
ConnectionProfile
      ↓
connection boundary
      ↓
connected Client
```

and:

```text
connected Client
      ↓
inspect_mcp()
      ↓
MCPInspectionResult
```

Part 2D should determine the smallest correct composition between them.

---

# 21. Questions Part 2D Must Review Before Coding

Before proposing production code, review:

1. Whether a project-owned complete application operation is now justified.

2. Whether that operation should accept a connection profile directly.

3. Whether it should own the connection lifetime.

4. Whether application composition should remain transport-neutral or dispatch through transport-specific connection builders.

5. How STDIO composition should coexist with future Streamable HTTP support.

6. Whether the result consumed by presentation should be exactly `MCPInspectionResult` or a higher application-level result.

7. Whether target/profile identity belongs in an application-level result rather than `MCPInspectionResult`.

8. How target identity should remain distinct from server-reported `server_info`.

9. Whether connection failures should propagate or receive project-owned structured result state.

10. Whether inspection failures already represented by `CategoryInspection` require any additional application-level handling.

11. Whether the application needs a dedicated composition module or whether existing modules remain sufficient.

12. Whether connection-profile dispatch requires a generic abstraction now or should remain explicit.

13. What exact lifecycle shape is correct for:

```text
profile
  ↓
open connection
  ↓
inspect
  ↓
close connection
```

14. What presentation should receive after application composition is complete.

15. Which contracts are genuinely high-value enough to protect with regression tests.

16. What new architectural decisions should be recorded.

17. What the smallest safe first implementation milestone should be.

---

# 22. Constraints for Part 2D

Do not:

* redesign `CategoryInspection`,
* redesign primitive inspectors,
* redesign pagination,
* flatten SDK result pages,
* introduce concurrency without evidence,
* mix presentation into connection or inspection,
* execute tools,
* read resource contents,
* render/get prompts,
* materialize resource templates,
* add speculative service classes,
* prematurely implement Streamable HTTP merely because future transport support matters.

Part 2D should remain a controlled composition review.

---

# 23. Recommended Part 2D Starting Point

The likely conceptual territory is:

```text
explicit ConnectionProfile
          │
          ▼
application composition
          │
          ├── establish connection
          │
          ├── own connection lifetime
          │
          ├── call inspect_mcp()
          │
          └── preserve target + inspection evidence appropriately
          │
          ▼
structured application result
          │
          ▼
future presentation
```

This diagram is a hypothesis to review, not a pre-approved implementation.

No production code should be written until the Part 2D application-composition boundary review is complete.
