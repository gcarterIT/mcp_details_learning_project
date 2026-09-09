# MCP Details Learning Project
# Part 2C Continuation Context
# Aggregate Inspection Result and Orchestration Boundary

Date: 2026-09-04

## Purpose of this context file

This file is the authoritative continuation context for the next conversation
in the MCP Details Learning Project.

The project has completed the primitive inspection architecture through
Part 2C.10B.

The next milestone is:

**Part 2C.11 — Aggregate Inspection Result and Orchestration Boundary Review**

Do not redesign or reopen completed primitive inspection boundaries unless new
evidence demonstrates a concrete architectural problem.

Before proposing aggregate implementation code, review the architecture
described here and determine the smallest correct aggregate inspection and
orchestration boundary.

---

# 1. Project identity

Project name:

**MCP Details Learning Project**

Repository root:

```text
C:\AI_Projects\mcp_details_learning_project

The project is separate from the earlier MCP Client Learning Project.

Its purpose is to build a general-purpose application that inspects MCP servers
without executing their advertised capabilities.

The application is intentionally:

discovery-focused
inspection-focused
strictly read-only during ordinary inspection
transport-neutral above the connection boundary
based on the high-level MCP Python SDK v2 Client abstraction
2. Primary project goal

Given an explicit MCP connection profile, MCP Details should connect to the
server and produce structured inspection evidence describing the server and
everything it advertises.

The intended complete inspection includes:

server identity
initialization / negotiated server metadata exposed by the high-level Client
protocol information
server capabilities
server instructions
all tools
all static resources
all resource templates
all prompts
descriptions
tool schemas / parameter information
resource metadata
resource-template metadata
prompt arguments
pagination evidence where relevant
category-level success / partial / failure information

The initial presentation target is terminal output, but inspection architecture
must remain independent of terminal, notebook, Streamlit, or future
presentation layers.

3. Strict read-only policy

Ordinary MCP Details inspection may perform discovery/list operations such as:

list_tools()
list_resources()
list_resource_templates()
list_prompts()

Ordinary inspection must not perform:

call_tool()
read_resource()
get_prompt()

It must also avoid other execution/materialization behavior unless a future
explicitly separate feature introduces such behavior.

The project inspects what a server advertises.

It does not exercise the advertised behavior.

Conceptually:

DISCOVERY / INSPECTION
        |
        v
structured evidence
        X
        |
        v
execution / materialization

The X is intentional.

4. Transport architecture

Initial transports:

STDIO
Streamable HTTP

The architecture must remain open to additional transports later.

An explicit connection profile supplies the information required to connect.

A generic string such as:

weather-mcp/weather-mcp

is not assumed to contain sufficient connection information.

The connection boundary translates project-owned connection profile data into
the MCP SDK's connection mechanism.

The inspection boundary receives an already-connected high-level MCP SDK v2
Client and must not know whether that Client came from STDIO, Streamable HTTP,
or a future transport.

5. SDK boundary

The project targets the MCP Python SDK v2 architecture.

Primary interaction boundary:

mcp.Client

The project intentionally uses the documented high-level Client rather than
centering the application on the lower-level ClientSession API.

The SDK owns:

transport mechanics
protocol negotiation
JSON-RPC mechanics
wire messages
serialization / deserialization
SDK semantic models
list operation result models
connection mechanics

MCP Details owns:

inspection policy
capability-aware discovery
pagination exhaustion policy
category inspection state
partial-evidence preservation
failure evidence
aggregation
presentation policy

Do not create custom copies of SDK semantic types without a concrete reason.

SDK models such as:

Tool
Resource
ResourceTemplate
Prompt
ListToolsResult
ListResourcesResult
ListResourceTemplatesResult
ListPromptsResult
ServerCapabilities

are legitimate evidence types at the inspection boundary.

6. Completed connection architecture

Part 2A established the minimal package skeleton and initial explicit STDIO
connection profile.

Part 2B established the minimal STDIO connection path from:

StdioConnectionProfile
        |
        v
SDK STDIO server parameters
        |
        v
high-level MCP SDK Client
        |
        v
real STDIO subprocess
        |
        v
MCP negotiation
        |
        v
connected Client

The STDIO path was proven with a real minimal subprocess test server.

Inspection does not own this connection lifecycle.

7. Current production modules

The project currently includes production files conceptually including:

src/mcp_details/__init__.py
src/mcp_details/profiles.py
src/mcp_details/connection.py
src/mcp_details/results.py
src/mcp_details/inspection.py

The architecture should remain shallow unless a genuinely independent
responsibility justifies another module.

Do not create modules merely to reduce file length.

8. Server-description inspection

Part 2C.1 established server-description inspection.

Conceptual operation:

inspect_server_description(client)

The resulting project-owned ServerDescription preserves authoritative evidence
from the already-connected high-level Client, including:

protocol version
server information / identity
server capabilities
server instructions

The server description is distinct from primitive category inspection.

9. Inspection categories

The project currently defines:

class InspectionCategory(Enum):
    TOOLS = "tools"
    RESOURCES = "resources"
    RESOURCE_TEMPLATES = "resource_templates"
    PROMPTS = "prompts"

These categories represent semantic inspection categories, not merely SDK
method names.

The capability mapping is:

TOOLS
    -> ServerCapabilities.tools

RESOURCES
    -> ServerCapabilities.resources

RESOURCE_TEMPLATES
    -> ServerCapabilities.resources

PROMPTS
    -> ServerCapabilities.prompts

Static resources and resource templates are intentionally distinct inspection
categories even though they share the same advertised resources capability.

Do not collapse them into a single resource-family inspection result.

Shared capability advertisement does not imply shared inspection fate.

For example, this must remain representable:

RESOURCES              SUCCESS
RESOURCE_TEMPLATES     FAILED

and also:

RESOURCES              FAILED
RESOURCE_TEMPLATES     SUCCESS
10. Capability-aware discovery policy

Ordinary inspection respects advertised server capabilities.

If a category is not advertised, MCP Details does not deliberately probe its
list operation.

Example:

ServerCapabilities.prompts is None
        |
        v
do not call list_prompts()
        |
        v
NOT_ADVERTISED

Absence of advertisement is not a failure.

It is inspection evidence.

11. Category result model

The current shared category result model is conceptually:

class InspectionStatus(Enum):
    NOT_ADVERTISED = "not_advertised"
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"

and:

@dataclass(frozen=True)
class CategoryInspection(Generic[PageT]):
    status: InspectionStatus
    pages: tuple[PageT, ...]
    failure: Exception | None = None

Semantics:

NOT_ADVERTISED
status = NOT_ADVERTISED
pages = ()
failure = None

The category was not advertised and was not probed.

SUCCESS
status = SUCCESS
pages = one or more successfully obtained SDK result pages
failure = None

SUCCESS describes inspection completion.

It does not describe inventory size.

A successfully listed category containing zero items is still SUCCESS.

There is intentionally no EMPTY status.

PARTIAL
status = PARTIAL
pages = one or more successfully obtained SDK pages
failure = original exception

At least one page succeeded but later pagination failed.

Successfully obtained evidence must be preserved.

FAILED
status = FAILED
pages = ()
failure = original exception

The first attempt failed before any page was obtained.

The original exception is retained rather than replaced by a project-owned
generic exception.

12. Evidence preservation policy

The project preserves complete SDK result pages.

Examples:

CategoryInspection[ListToolsResult]
CategoryInspection[ListResourcesResult]
CategoryInspection[ListResourceTemplatesResult]
CategoryInspection[ListPromptsResult]

The authoritative inspection result should not immediately flatten these into:

list[Tool]
list[Resource]
list[ResourceTemplate]
list[Prompt]

Flattened inventories may later be derived for presentation.

Preserving SDK pages retains:

original semantic result objects
pagination boundaries
result metadata
future SDK fields
stronger diagnostic evidence

Derived views should preferably be computed from authoritative stored evidence
rather than independently stored when practical.

13. Shared pagination mechanics

Part 2C.8C extracted a private shared pagination helper after genuine
duplication had been demonstrated.

Conceptually:

class PaginatedPage(Protocol):
    next_cursor: str | None

and:

async def _inspect_paginated_pages(
    list_pages: Callable[..., Awaitable[PageT]],
) -> CategoryInspection[PageT]:
    ...

The helper owns:

first request without cursor
continuation request with exact cursor
opaque cursor propagation
preservation of successfully obtained SDK pages
looping until next_cursor is None
SUCCESS classification
PARTIAL classification
FAILED classification
preservation of the original exception

The helper does NOT own:

capability gating
InspectionCategory selection
SDK method selection
NOT_ADVERTISED
transport
connection
server-description inspection
aggregate composition
presentation

The helper remains private.

Do not make it a public pagination API.

Do not move it into a pagination module without new evidence that pagination is
an independent application responsibility.

Direct private-helper tests are not currently required.

Its contracts are protected indirectly through semantic inspection tests.

14. Completed tools inspection

Conceptual operation:

async def inspect_tools(
    client: Client,
) -> CategoryInspection[ListToolsResult]:
    ...

It:

checks the tools capability
returns NOT_ADVERTISED when tools are not advertised
otherwise delegates client.list_tools to the private pagination helper
preserves complete ListToolsResult pages
returns SUCCESS after complete pagination
returns PARTIAL after later-page failure
returns FAILED after first-page failure
never calls tools

call_tool() remains outside inspection.

15. Completed static-resources inspection

Conceptual operation:

async def inspect_resources(
    client: Client,
) -> CategoryInspection[ListResourcesResult]:
    ...

It:

checks the resources capability using the RESOURCES semantic category
returns NOT_ADVERTISED when resources are not advertised
delegates client.list_resources to the pagination helper
preserves complete ListResourcesResult pages
supports SUCCESS / PARTIAL / FAILED
does not read resource contents

read_resource() remains outside ordinary inspection.

16. Completed resource-template inspection

Conceptual operation:

async def inspect_resource_templates(
    client: Client,
) -> CategoryInspection[ListResourceTemplatesResult]:
    ...

It:

uses the RESOURCE_TEMPLATES semantic category
shares ServerCapabilities.resources advertisement with static resources
remains an independent inspection operation
delegates client.list_resource_templates to the pagination helper
preserves SDK ListResourceTemplatesResult pages
treats successful zero-template results as SUCCESS
preserves partial evidence and original exceptions
does not materialize template URIs
does not read instantiated resources

Part 2C.9B concluded that no resource-family abstraction is justified.

17. Completed prompts inspection

Conceptual operation:

async def inspect_prompts(
    client: Client,
) -> CategoryInspection[ListPromptsResult]:
    ...

It:

checks ServerCapabilities.prompts
returns NOT_ADVERTISED without probing when prompts are unadvertised
delegates client.list_prompts to the pagination helper
preserves ListPromptsResult SDK pages
exhausts pagination
returns SUCCESS for complete listings even when zero prompts are returned
returns PARTIAL after later-page failure
returns FAILED after first-page failure
preserves the original exception

Prompt metadata and arguments are discoverable through list_prompts().

Ordinary inspection must not proceed to:

get_prompt()

Prompt rendering/materialization is outside the inspection boundary.

Likewise, interactive completion behavior does not belong in ordinary primitive
inspection.

18. Primitive category architecture is now closed

The completed primitive architecture is:

                  high-level MCP v2 Client
                           |
                           v
                       inspection.py
                           |
              +------------+------------+
              |                         |
              v                         v
     server description         primitive categories
                                         |
                   +----------+----------+----------+
                   |          |          |          |
                   v          v          v          v
                 tools    resources  templates   prompts
                   |          |          |          |
                   +----------+----------+----------+
                              |
                              v
                  _inspect_paginated_pages()
                              |
                              v
                    CategoryInspection[T]

No further primitive-category generalization is currently justified.

The explicit semantic operations should remain:

inspect_tools()
inspect_resources()
inspect_resource_templates()
inspect_prompts()

Do not replace them with a generic inspect_category() dispatcher merely to
remove small amounts of repetition.

The semantic layer should remain explicit.

The pagination layer should remain generic only with respect to pagination
mechanics.

19. Primitive failure independence

Primitive categories must fail independently.

A future complete inspection must be able to preserve results such as:

TOOLS                  SUCCESS
RESOURCES              PARTIAL
RESOURCE_TEMPLATES     FAILED
PROMPTS                SUCCESS

One category failure must not automatically discard successful evidence from
other categories.

Likewise, failure in one category must not automatically prevent later
categories from being inspected.

The primitive functions themselves currently remain independent.

The next aggregate/orchestration boundary is where this policy must receive
direct implementation protection.

20. Current architectural decisions that should remain stable

The following architectural principles are already established and should not
be reopened without concrete new evidence:

high-level MCP SDK v2 Client is the primary semantic client boundary
inspection receives an already-connected Client
inspection remains transport-neutral
SDK owns protocol and transport mechanics
MCP Details owns inspection policy and completeness
server capabilities govern ordinary category probing
complete inventories require exhausting pagination
pagination cursors are opaque and must be propagated unchanged
successful partial pages survive later failure
primitive categories fail independently
SDK semantic result pages are preserved
zero-item successful listings are SUCCESS
static resources and templates remain independent categories
ordinary inspection remains strictly discovery/read-only
private pagination mechanics remain private
no generic category-dispatch framework is justified
no project-owned copies of Tool / Resource / ResourceTemplate / Prompt are
justified at this time
presentation remains downstream of structured inspection results
21. Current regression checkpoint

The repository has passed:

python -m compileall src\mcp_details tests

the focused inspection test suite, and the complete regression suite after
resource-template and prompt inspection implementation.

The exact pytest output from the repository should remain authoritative.

The expected full-suite baseline after the five prompt inspection tests was
approximately:

42 passing tests

Do not assume the numeric baseline if the repository output shows otherwise.

The important point is that all compile, focused inspection, and full regression
checks passed before beginning Part 2C.11.

22. No aggregate inspection has been implemented yet

There is currently no project-owned aggregate orchestration operation that
owns the complete inspection sequence.

Conceptually, callers still have separate operations such as:

inspect_server_description(client)

await inspect_tools(client)

await inspect_resources(client)

await inspect_resource_templates(client)

await inspect_prompts(client)

The next architectural milestone must determine how these become one coherent
server-inspection operation.

Do not implement aggregate orchestration before that review is complete.

23. Next milestone

Proceed with:

Part 2C.11 — Aggregate Inspection Result and Orchestration Boundary Review

The review should begin from the already-completed primitive architecture and
answer the following questions before any production code is proposed.

23.1 Aggregate result responsibility

Determine whether the previously anticipated project-owned aggregate result,
conceptually named:

MCPInspectionResult

is now justified.

Determine exactly what evidence it should contain.

A likely starting hypothesis is:

server_description

tools:
    CategoryInspection[ListToolsResult]

resources:
    CategoryInspection[ListResourcesResult]

resource_templates:
    CategoryInspection[ListResourceTemplatesResult]

prompts:
    CategoryInspection[ListPromptsResult]

This is only a starting hypothesis.

Review it architecturally before implementing it.

23.2 Preserve category result semantics

Do not flatten category results merely because they are being aggregated.

The aggregate should preserve:

NOT_ADVERTISED
SUCCESS
PARTIAL
FAILED
SDK pages
original category failure evidence

Determine whether additional aggregate-level information is actually required.

23.3 Aggregate status

Determine whether MCPInspectionResult needs an overall status.

Do not add one automatically.

Questions include:

Is an overall SUCCESS / FAILED status meaningful when categories can fail
independently?
Would an aggregate status hide useful nuance?
Can overall health be derived from category results instead?
Is there any orchestration failure that cannot be represented by the category
results themselves?

Prefer derived truths over independently stored duplicate truths where
practical.

23.4 Orchestration operation

Determine the appropriate semantic operation for complete inspection.

A conceptual candidate might be:

async def inspect_mcp(client: Client) -> MCPInspectionResult:
    ...

or another clearly named operation.

Do not select the name or signature merely by intuition.

Review responsibility and API shape first.

23.5 Sequential versus concurrent orchestration

Determine whether primitive category inspection should initially run:

sequentially

or:

concurrently

Do not assume concurrency is better.

Review:

high-level Client concurrency guarantees
server behavior
category isolation
deterministic behavior
simplicity
diagnostic clarity
performance relevance
testing complexity
learning-project goals

Prefer the smallest understandable safe architecture unless concrete evidence
justifies concurrency.

23.6 Failure isolation

The aggregate orchestrator must not treat primitive failure as permission to
discard or skip unrelated evidence.

Review explicit cases such as:

tools FAILED
resources SUCCESS
resource templates SUCCESS
prompts SUCCESS

and:

tools SUCCESS
resources FAILED
resource templates SUCCESS
prompts FAILED

Determine exactly which component owns the rule that all eligible categories
should still be attempted.

This will likely require direct aggregate/orchestration regression tests once
the boundary is implemented.

23.7 Server-description failure semantics

Review whether inspect_server_description() can fail under the established
already-connected Client contract.

Determine whether server-description collection requires separate failure
representation or whether its evidence is guaranteed to be available after
connection.

Do not invent failure machinery without evidence.

23.8 Capability consistency

The aggregate should use the same authoritative server capabilities already
available from the connected Client.

Do not independently infer capability support from whether list operations
succeed.

A list failure does not mean the capability was unadvertised.

Capability advertisement and inspection outcome remain separate truths.

23.9 Ordering

Determine whether category invocation order is architecturally meaningful.

A possible deterministic sequence is:

server description
tools
resources
resource templates
prompts

but review whether this is policy or merely implementation convenience.

If order is not semantically meaningful, avoid exposing it as a contract
unnecessarily.

23.10 Presentation boundary

The aggregate result should remain structured evidence.

Do not mix terminal rendering, Rich output, notebooks, Streamlit, formatting,
or report-generation logic into aggregate orchestration.

Presentation should consume the aggregate result downstream.

23.11 Exception policy

Determine whether unexpected orchestration-level exceptions need a distinct
representation.

Do not automatically wrap all exceptions.

Primitive list-operation exceptions are already represented within
CategoryInspection.

Review whether any additional failure class is genuinely possible at the
aggregate composition layer.

23.12 Module location

Determine whether aggregate result and orchestration responsibilities belong
in the existing:

results.py
inspection.py

or whether a genuinely separate module is justified.

Prefer existing cohesive modules unless a distinct responsibility requires a
new boundary.

Do not create an orchestrator.py, service.py, or similar module solely
because aggregation sounds important.

24. Questions Part 2C.11 should explicitly answer

Before implementation, answer:

Is MCPInspectionResult now justified?
What exact fields should it contain?
Should it preserve the four CategoryInspection result objects directly?
Does it need an aggregate status?
If an aggregate status is proposed, is it stored or derived?
What should the complete-inspection operation be responsible for?
Should server-description inspection be part of that operation?
Should primitive categories be inspected sequentially or concurrently?
What evidence supports that choice?
How do we guarantee that one primitive failure does not suppress the
remaining categories?
Does the orchestrator need its own exception model?
Does server-description retrieval need failure representation?
Is invocation order part of the contract?
Should aggregation remain in inspection.py and results.py?
Is any new abstraction actually necessary beyond MCPInspectionResult and
one orchestration operation?
Which contracts are high-value enough to protect directly with tests?
What is the smallest safe first implementation milestone after the review?
25. Important constraints for the next conversation

Do not:

redesign completed primitive category functions without evidence
collapse resources and resource templates
modify CategoryInspection merely to support aggregation
flatten SDK evidence prematurely
add an overall aggregate status merely for symmetry
add generic category dispatch
add a category registry
add retries
add execution or materialization
call tools
read resources
render prompts
mix presentation into orchestration
introduce concurrency without reviewing Client/server implications
create new modules merely for organizational preference
begin implementation before Part 2C.11 architectural review is complete
26. Teaching and development contract

Continue using the established project method:

architecture before implementation
explain why before code
professor/software-architect teaching style
extremely small milestones
preserve existing behavior exactly
compile after every implementation
run focused tests after every implementation
run the full regression suite after every milestone
stop after every checkpoint
separate architectural decisions from implementation
distinguish high-value contracts from low-value edge cases
avoid speculative abstractions
do not build the complete application at once

For architectural reviews:

review existing production responsibilities first
identify the smallest new responsibility
determine the correct dependency direction
determine what evidence is authoritative
determine failure semantics before implementation
recommend the smallest safe implementation milestone
stop before code
27. Starting architectural position for Part 2C.11

The most likely architectural direction, subject to review, is:

already-connected Client
        |
        v
complete inspection operation
        |
        +--> inspect_server_description()
        |
        +--> inspect_tools()
        |
        +--> inspect_resources()
        |
        +--> inspect_resource_templates()
        |
        +--> inspect_prompts()
        |
        v
MCPInspectionResult

where the aggregate preserves each primitive CategoryInspection directly.

However:

Do not treat this sketch as a decided implementation.

Part 2C.11 must review:

aggregate result shape
failure isolation
aggregate status
sequencing
concurrency
orchestration exception behavior
module ownership
high-value test contracts

before any production code is proposed.

28. Desired end state of Part 2C.11

Part 2C.11 should end with:

a precise aggregate-result responsibility
a precise orchestration responsibility
a decision on sequential versus concurrent primitive inspection
explicit failure-isolation semantics
a decision on whether aggregate status exists
a decision on orchestration-level exceptions
confirmation of module ownership
identification of genuinely new architectural decisions, if any
a very small first implementation milestone

Then stop before implementation.

The likely implementation milestone after architectural approval should remain
small enough to compile and test independently.

29. Current architectural boundary

At the start of the new conversation, assume:

CONNECTION BOUNDARY       COMPLETE FOR MINIMAL STDIO PATH

SERVER DESCRIPTION        COMPLETE

CAPABILITY POLICY         COMPLETE

CATEGORY RESULT MODEL     COMPLETE

TOOLS INSPECTION          COMPLETE

RESOURCES INSPECTION      COMPLETE

RESOURCE TEMPLATES        COMPLETE

PROMPTS INSPECTION        COMPLETE

SHARED PAGINATION         COMPLETE AND PRIVATE

PRIMITIVE INSPECTION      ARCHITECTURALLY CLOSED

AGGREGATE INSPECTION      NOT YET DESIGNED

PRESENTATION              NOT YET THE CURRENT FOCUS

Proceed from this boundary.

Do not reopen earlier layers without concrete evidence.


---

# 5. Exact first prompt for the new chat

Use this as the first message in the new conversation:

```text
# Part 2C.11 — Aggregate Inspection Result and Orchestration Boundary Review

We are continuing my MCP Details Learning Project.

The primitive inspection boundary through Part 2C.10B is complete.

Please use the attached project context files as the authoritative basis for
this conversation, especially:

- MCP_DETAILS_PROJECT_CONTEXT.md
- ARCHITECTURAL_DECISION_LEDGER.md
- Part_1_Completion_Note.md
- Part_2B_Completion_Note.md
- PART2C_AGGREGATE_INSPECTION_CONTEXT_20260904.md

The current architecture already supports transport-neutral inspection of an
already-connected high-level MCP SDK v2 Client for:

- server description
- tools
- static resources
- resource templates
- prompts

The four primitive list categories use explicit semantic inspection functions
and share a private pagination helper.

Primitive category inspection is now architecturally closed.

We are now beginning:

**Part 2C.11 — Aggregate Inspection Result and Orchestration Boundary Review**

Before proposing any production code:

1. Review the completed architecture through Part 2C.10B.

2. Confirm whether the previously anticipated project-owned aggregate result,
   conceptually named `MCPInspectionResult`, is now justified.

3. Determine the smallest correct responsibility for that aggregate result.

4. Determine exactly which authoritative evidence it should contain.

5. Review whether it should directly preserve:

   - `ServerDescription`
   - `CategoryInspection[ListToolsResult]`
   - `CategoryInspection[ListResourcesResult]`
   - `CategoryInspection[ListResourceTemplatesResult]`
   - `CategoryInspection[ListPromptsResult]`

6. Determine whether an aggregate-level inspection status is genuinely needed.

7. If an aggregate status is considered, distinguish stored authoritative
   state from state that can be derived from the individual category results.

8. Determine the correct responsibility and API shape for a complete
   inspection orchestration operation over an already-connected Client.

9. Determine whether `inspect_server_description()` belongs inside that
   complete orchestration operation.

10. Review whether primitive category inspection should initially execute
    sequentially or concurrently.

11. Do not assume concurrency is preferable. Review high-level Client behavior,
    server implications, failure isolation, determinism, testing complexity,
    diagnostic clarity, and the learning-project goal before deciding.

12. Define the exact failure-isolation contract.

    In particular, determine how the architecture guarantees that:

    - tools failure does not suppress resources
    - resources failure does not suppress resource templates
    - resource-template failure does not suppress prompts
    - successful and partial evidence from every attempted category survives

13. Review whether there are any genuine orchestration-level exceptions that
    cannot already be represented by the primitive `CategoryInspection`
    results.

14. Review whether server-description retrieval needs its own failure
    representation under the already-connected Client contract.

15. Determine whether invocation order is part of the architectural contract
    or merely an implementation detail.

16. Confirm that aggregation remains presentation-independent.

17. Review whether the aggregate result belongs in `results.py` and the
    orchestration operation belongs in `inspection.py`, or whether a genuinely
    new module responsibility has emerged.

18. Do not introduce a new module merely for organizational preference.

19. Identify which aggregate/orchestration contracts are genuinely high-value
    enough to protect directly with regression tests.

20. Identify any genuinely new architectural decision that should be recorded
    in `ARCHITECTURAL_DECISION_LEDGER.md`.

21. Recommend the smallest safe first implementation milestone.

Continue using the established teaching contract:

- architecture before implementation
- professor/software-architect style
- explain why before code
- extremely small, highly testable milestones
- preserve behavior exactly
- compile after every implementation
- run focused tests after every implementation
- run the full regression suite after every milestone
- stop after every checkpoint
- separate architectural decisions from implementation
- distinguish high-value architectural contracts from low-value edge cases
- avoid speculative abstractions

Do not begin coding until the Part 2C.11 architectural review is complete.

Do not redesign the completed primitive inspection functions, shared pagination
helper, capability policy, or CategoryInspection model unless concrete new
evidence demonstrates a real problem.

This checkpoint is especially well suited to a new chat because the conceptual handoff is now clean:

Part 2C.1–2C.10
Primitive inspection
        │
        │ COMPLETE
        ▼
Part 2C.11
Aggregate result + orchestration