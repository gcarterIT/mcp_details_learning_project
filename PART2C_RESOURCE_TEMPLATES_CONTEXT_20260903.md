# MCP Details Learning Project — Part 2C Resource Templates Continuation Context

**Date:** 2026-09-03
**Project:** MCP Details Learning Project
**Project root:** `C:\AI_Projects\mcp_details_learning_project`

---

## 1. Purpose of This Context File

This file is the handoff context for continuing Part 2C of the MCP Details Learning Project in a new ChatGPT conversation.

Part 2C is **not complete**.

The project has completed the server-description, capability-policy, tools-inspection, static-resources-inspection, and shared-pagination milestones.

The next milestone is:

**Part 2C.9 — Resource Templates Inspection Boundary Review**

Do not redesign or reimplement the completed boundaries unless concrete evidence requires a change.

---

# 2. Project Goal

MCP Details is a general-purpose, strictly read-only MCP inspection application.

The application should allow a user to research an MCP server, prepare an explicit connection profile, connect to that server, and inspect the server's advertised descriptive/discovery information.

Initial transports:

* STDIO
* Streamable HTTP

The architecture should remain open to additional transports later.

The eventual inspection report should include, where advertised and available:

* server identity
* initialization/negotiation metadata
* negotiated protocol information
* server capabilities
* server instructions
* tools
* static resources
* resource templates
* prompts
* descriptions
* tool parameter/schema information
* prompt argument information

The application is strictly discovery/read-only.

Allowed inspection operations include:

* negotiated server metadata
* `list_tools()`
* `list_resources()`
* `list_resource_templates()`
* `list_prompts()`

The inspection application must not perform execution/materialization operations such as:

* `call_tool()`
* `read_resource()`
* `get_prompt()`

---

# 3. Development Contract

Continue using the established development method:

* architecture before implementation
* explain why before code
* professor/software-architect teaching style
* extremely small, highly testable milestones
* preserve behavior exactly unless a milestone intentionally changes it
* compile after every implementation
* run focused tests after every implementation
* run the full regression suite after every milestone
* stop after every checkpoint
* separate architectural decisions from implementation
* avoid speculative abstractions
* prefer project-owned policy over unnecessary SDK wrappers
* do not generalize until concrete duplication demonstrates the need

---

# 4. SDK Boundary

The project targets the MCP Python SDK v2 high-level `Client` abstraction.

The high-level connected `Client` is the primary MCP interaction boundary.

MCP Details does not center its architecture around the older low-level `ClientSession.initialize()` workflow.

The SDK owns:

* transport mechanics
* protocol negotiation
* JSON-RPC/wire behavior
* MCP semantic models
* individual SDK list operations

MCP Details owns:

* inspection policy
* capability-aware discovery decisions
* completeness policy
* pagination exhaustion
* category state
* partial evidence preservation
* failure evidence
* result aggregation
* presentation

Inspection receives an already-connected high-level `Client` and must remain transport-neutral.

---

# 5. Important Architectural Decisions Already Established

The Architectural Decision Ledger is authoritative.

Relevant decisions include:

## AD-015

Use the documented high-level v2 `Client` as the primary SDK interaction boundary.

## AD-016

The SDK owns modern/legacy protocol negotiation.

## AD-017

Do not create a custom connection wrapper unless a project-owned responsibility later justifies one.

## AD-018

Common server-description properties include:

* `protocol_version`
* `server_info`
* `server_capabilities`
* `instructions`

## AD-019

Preserve raw SDK discovery/initialization evidence where useful.

## AD-020

Respect advertised server capabilities.

Do not ordinarily probe categories the server did not advertise.

## AD-021

Complete inventory requires exhausting pagination until `next_cursor is None`.

## AD-022

Preserve partial inspection results when later pagination fails.

## AD-023

Primitive inspection categories fail independently.

## AD-024

Distinguish:

* `NOT_ADVERTISED`
* `SUCCESS`
* `PARTIAL`
* `FAILED`

Do not introduce an `EMPTY` status.

An advertised category that successfully returns zero items is still `SUCCESS`.

## AD-025

Preserve lossless SDK/protocol evidence before presentation normalization.

## AD-026

The eventual aggregate result will be project-owned `MCPInspectionResult`.

It has not yet been implemented.

## AD-027

Do not clone SDK semantic models unnecessarily.

The SDK continues to own semantic objects such as:

* Tool
* Resource
* ResourceTemplate
* Prompt
* ServerCapabilities
* server identity models

MCP Details owns inspection state and composition.

## AD-028

Use the shared conceptual `CategoryInspection[T]` result model for primitive inspection categories.

## AD-029

`SUCCESS` is independent of item count.

`SUCCESS` with zero items is distinct from `NOT_ADVERTISED`.

## AD-030

Profile/target identity is distinct from server-reported identity.

## AD-031

Presentation consumes structured inspection results and performs no discovery.

## AD-040 through AD-047

Maintain responsibility separation among:

* profiles
* connection
* inspection
* results
* presentation
* composition

Profiles remain independent of SDK runtime objects.

Connection owns profile-to-SDK translation.

Inspection is transport-neutral after connection.

Inspection is independent of presentation.

Direct SDK dependencies are acceptable where appropriate.

Do not create a generic SDK façade without a concrete need.

Do not introduce capability-specific workflow modules.

Composition should remain shallow.

## AD-048 — Shared Private Pagination Mechanics for Inspection Categories

Complete tools and static resources inspection demonstrated genuine duplication of pagination and failure-classification mechanics.

The repeated mechanics are extracted into a private helper inside the inspection module.

Category-specific semantic operations remain explicit:

* `inspect_tools()`
* `inspect_resources()`

Capability gating remains category-specific.

The private pagination helper receives the appropriate SDK list callable rather than an `InspectionCategory`.

`NOT_ADVERTISED` remains outside the pagination helper because it is a capability-policy outcome rather than a pagination outcome.

The helper remains private and is not a public MCP Details inspection API.

No separate pagination module, pagination class hierarchy, generic category dispatcher, or public paginator API has been introduced.

Future inspection categories may reuse the helper only if their concrete SDK behavior satisfies the same pagination contract.

---

# 6. Completed Part 2A Boundary

Part 2A established the minimal package skeleton and first project-owned connection profile.

The STDIO profile boundary is implemented and tested.

The profile uses project-owned configuration data and does not expose SDK runtime connection objects.

---

# 7. Completed Part 2B Boundary

Part 2B established the minimal STDIO connection path.

The proven end-to-end path is conceptually:

```text
StdioConnectionProfile
        ↓
build_stdio_server_parameters()
        ↓
StdioServerParameters
        ↓
high-level MCP SDK Client
        ↓
real STDIO subprocess
        ↓
MCP negotiation
        ↓
connected Client
```

No custom lifecycle wrapper or manual `ClientSession.initialize()` architecture was introduced.

At Part 2B closure the regression baseline was 15 passing tests.

---

# 8. Part 2C.1 — Server Description Inspection — Complete

Implemented a project-owned:

```python
ServerDescription
```

and:

```python
inspect_server_description(client)
```

The function captures negotiated descriptive information from an already-connected high-level SDK `Client`.

It preserves:

* protocol version
* server info
* server capabilities
* instructions

It does not:

* connect
* negotiate
* inspect transport
* perform primitive discovery
* execute tools/resources/prompts

---

# 9. Part 2C.2 — Capability-Aware Inspection Policy — Complete

Implemented:

```python
class InspectionCategory(Enum):
    TOOLS = "tools"
    RESOURCES = "resources"
    RESOURCE_TEMPLATES = "resource_templates"
    PROMPTS = "prompts"
```

and:

```python
is_category_advertised(
    capabilities,
    category,
)
```

Current capability mapping:

```text
TOOLS
    ↓
ServerCapabilities.tools


RESOURCES
    ↓
ServerCapabilities.resources


RESOURCE_TEMPLATES
    ↓
ServerCapabilities.resources


PROMPTS
    ↓
ServerCapabilities.prompts
```

A particularly important established fact is:

**Static resources and resource templates are separate inspection categories but share the same advertised resources capability.**

---

# 10. Tools Inspection Boundary — Complete

The tools boundary progressed through first-page inspection, pagination, partial-failure preservation, closure review, and cleanup.

The obsolete first-page-only helper was removed.

The intended semantic production operation is now:

```python
async def inspect_tools(
    client: Client,
) -> CategoryInspection[ListToolsResult]:
    ...
```

Tools inspection protects:

* capability-aware discovery
* no probing when tools are unadvertised
* first request without a cursor argument
* complete pagination
* exact continuation cursor propagation
* completion only when `next_cursor is None`
* successful empty inventory as `SUCCESS`
* preservation of SDK result page objects
* `NOT_ADVERTISED`
* `SUCCESS`
* `PARTIAL`
* `FAILED`
* first-request failure
* later-page failure
* original exception preservation
* transport neutrality
* strict non-execution

---

# 11. Static Resources Inspection Boundary — Complete

Implemented:

```python
async def inspect_resources(
    client: Client,
) -> CategoryInspection[ListResourcesResult]:
    ...
```

Static resources use the same established category inspection semantics as tools.

Resources inspection protects:

* resources capability gating
* no probing when resources are unadvertised
* `list_resources()` discovery only
* complete pagination
* exact continuation cursor propagation
* SDK `ListResourcesResult` page preservation
* successful empty resource inventory as `SUCCESS`
* `NOT_ADVERTISED`
* `SUCCESS`
* `PARTIAL`
* `FAILED`
* first-request failure
* later-page partial failure
* original exception preservation

`read_resource()` is outside the MCP Details inspection boundary.

---

# 12. Shared Result Model

The project currently uses a project-owned generic category result model conceptually equivalent to:

```python
class InspectionStatus(Enum):
    NOT_ADVERTISED = "not_advertised"
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
```

and:

```python
@dataclass(frozen=True)
class CategoryInspection(Generic[PageT]):
    status: InspectionStatus
    pages: tuple[PageT, ...]
    failure: Exception | None = None
```

Important semantics:

```text
NOT_ADVERTISED
    pages = ()
    failure = None


SUCCESS
    one or more successfully obtained SDK pages
    failure = None


PARTIAL
    one or more successfully obtained SDK pages
    failure = original exception


FAILED
    pages = ()
    failure = original exception
```

No `EMPTY` state exists.

---

# 13. Shared Private Pagination Helper

Part 2C.8B compared the completed tools and static resources implementations.

The duplication was judged sufficient to earn a narrow private abstraction.

Part 2C.8C extracted the shared pagination mechanics.

The inspection module now contains a minimal structural page contract conceptually equivalent to:

```python
class PaginatedPage(Protocol):
    next_cursor: str | None
```

with:

```python
PageT = TypeVar("PageT", bound=PaginatedPage)
```

and a private helper conceptually equivalent to:

```python
async def _inspect_paginated_pages(
    list_pages: Callable[..., Awaitable[PageT]],
) -> CategoryInspection[PageT]:
    ...
```

The helper owns:

* first-page request
* continuation requests
* exact cursor propagation
* page preservation
* cursor exhaustion
* `SUCCESS`
* `PARTIAL`
* `FAILED`
* original exception preservation

The helper does **not** own:

* capability gating
* `NOT_ADVERTISED`
* category selection
* SDK method selection
* connection
* transport
* presentation

`inspect_tools()` and `inspect_resources()` remain explicit semantic operations and delegate only their pagination mechanics to the helper.

The helper is private.

It is tested indirectly through the tools and resources production operations rather than through direct private-helper tests.

---

# 14. Current Conceptual Inspection Architecture

```text
                  already-connected Client
                           │
             ┌─────────────┴──────────────┐
             │                            │
             ▼                            ▼
inspect_server_description()       primitive inspection
                                          │
                            ┌─────────────┴─────────────┐
                            │                           │
                            ▼                           ▼
                    inspect_tools()             inspect_resources()
                            │                           │
                            │ category policy           │ category policy
                            │                           │
                            └────────────┬──────────────┘
                                         ▼
                              _inspect_paginated_pages()
                                         │
                                         ▼
                               CategoryInspection[T]
```

Resource templates and prompts have not yet been implemented.

The aggregate `MCPInspectionResult` has not yet been implemented.

Presentation and composition remain deferred.

---

# 15. Current Regression Baseline

After successful completion of Part 2C.8C:

```text
32 tests passing
```

The user reported that all of the following checks passed:

```powershell
python -m compileall src\mcp_details tests

python -m pytest tests\test_inspection.py -v

python -m pytest -v
```

The focused inspection suite was approximately 17 passing tests.

The full suite baseline is 32 passing tests.

Treat the actual repository/test output as authoritative if it differs.

---

# 16. Current Repository Areas Relevant to Part 2C

Relevant production files include:

```text
src/
└── mcp_details/
    ├── __init__.py
    ├── profiles.py
    ├── connection.py
    ├── inspection.py
    └── results.py
```

Relevant tests include:

```text
tests/
├── support/
│   └── minimal_stdio_server.py
├── test_package_import.py
├── test_profiles.py
├── test_connection.py
├── test_stdio_connection.py
└── test_inspection.py
```

Do not assume this listing is exhaustive if the actual repository differs.

Review the actual files provided in the new conversation before proposing implementation changes.

---

# 17. Next Milestone

The next milestone is:

# Part 2C.9 — Resource Templates Inspection Boundary Review

This should begin as an architectural review, not implementation.

The central architectural question is:

> How should MCP Details inspect resource templates as an independent primitive category when resource templates and static resources are both gated by the same advertised `ServerCapabilities.resources` capability?

Important questions to review include:

1. Confirm the exact high-level SDK v2 `Client.list_resource_templates()` contract.

2. Confirm the exact SDK result type and pagination contract.

3. Determine whether the existing private `_inspect_paginated_pages()` helper is directly appropriate.

4. Confirm that resource templates remain independently classified from static resources.

5. Confirm behavior when the shared resources capability is absent.

6. Confirm behavior when static resources succeed but resource templates fail.

7. Confirm behavior when static resources fail but resource templates succeed.

8. Preserve `SUCCESS` with zero resource templates as distinct from `NOT_ADVERTISED`.

9. Preserve SDK `ListResourceTemplatesResult` pages rather than prematurely flattening them.

10. Maintain strict non-execution/read-only policy.

11. Do not call `read_resource()` as part of resource-template inspection.

12. Determine the smallest safe implementation milestone only after the architectural review.

---

# 18. Expected Likely Semantic Operation

Do not implement this merely because it appears here; first verify the SDK contract and architecture.

The likely semantic operation is:

```python
async def inspect_resource_templates(
    client: Client,
) -> CategoryInspection[ListResourceTemplatesResult]:
    ...
```

The likely architecture is:

```text
inspect_resource_templates()
        │
        ├── check InspectionCategory.RESOURCE_TEMPLATES
        │
        │       ↓
        │   ServerCapabilities.resources
        │
        └── if advertised:
                client.list_resource_templates
                        │
                        ▼
              _inspect_paginated_pages()
```

This must be confirmed during Part 2C.9 rather than assumed.

---

# 19. Important Constraint for Part 2C.9

Do not collapse:

```text
RESOURCES
RESOURCE_TEMPLATES
```

into one category merely because both are gated by:

```text
ServerCapabilities.resources
```

The current architecture intentionally distinguishes:

```text
advertised capability
```

from:

```text
individual inspection result
```

Therefore it must remain possible to represent situations such as:

```text
RESOURCES
    SUCCESS

RESOURCE_TEMPLATES
    FAILED
```

or:

```text
RESOURCES
    FAILED

RESOURCE_TEMPLATES
    SUCCESS
```

provided the shared resources capability was advertised and the SDK operations behave independently.

---

# 20. Do Not Yet Implement

Until Part 2C.9 architecture is reviewed, do not add:

* resource-template inspection implementation
* prompt inspection
* aggregate `MCPInspectionResult`
* rendering
* composition
* generic category dispatcher
* public pagination API
* new SDK façade
* transport-specific inspection
* execution/materialization operations
* exception normalization hierarchy
* retries
* speculative DTOs for SDK resource-template models

---

# 21. Required New-Chat Behavior

At the beginning of the new conversation:

1. Review this context file.
2. Review the current `ARCHITECTURAL_DECISION_LEDGER.md`.
3. Review the actual current `inspection.py`.
4. Review the actual current `results.py`.
5. Review the relevant current inspection tests.
6. Treat the 32-test passing state as the current regression baseline unless repository evidence shows otherwise.
7. Do not begin coding immediately.
8. Perform Part 2C.9 as an architectural review first.
9. Stop at the architectural checkpoint before implementation.

The immediate next task is:

**Part 2C.9 — Resource Templates Inspection Boundary Review**
