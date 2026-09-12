# MCP Details Learning Project
# Part 2D.2 Context — Presentation Boundary Architectural Review

Date: 2026-09-10

## Purpose

This file provides the authoritative transition context from completed
Part 2D.1 application composition work into Part 2D.2 presentation
architecture.

Part 2D.1 is complete.

The next focus is:

# Part 2D.2 — Presentation Boundary Architectural Review

Do not begin presentation implementation until the presentation architecture
has been reviewed.

---

## 1. Project Goal

MCP Details is a general-purpose, strictly read-only MCP inspection
application.

The user researches an MCP server and provides an explicit connection profile.

The application should eventually report:

- configured target identity
- server-reported identity
- protocol version
- server initialization metadata
- server capabilities
- server instructions
- every advertised tool
- every advertised static resource
- every advertised resource template
- every advertised prompt
- descriptions
- tool parameter/input schema information
- prompt argument information
- primitive-category inspection status
- preserved partial evidence when inspection fails after one or more pages
- useful failure information

Initial transports:

- STDIO
- Streamable HTTP later

Architecture should remain open to additional transports without introducing
speculative transport abstractions before they are justified.

Initial presentation target:

- terminal

Future presentation possibilities may include:

- notebook
- Streamlit
- exported reports

Presentation architecture should therefore avoid unnecessary coupling to a
single output mechanism where practical.

---

## 2. Development Method

Continue the established development contract:

- architecture before implementation
- professor/software-architect teaching style
- extremely small, highly testable milestones
- preserve behavior exactly
- compile after every implementation
- run focused tests after each implementation
- run the complete regression suite after each milestone
- stop after every checkpoint
- separate architectural decisions from implementation details
- do not invent abstractions without evidence
- inspect the actual repository before proposing code that depends on its
  current contents

---

## 3. Completed Profile Boundary

Current project-owned STDIO profile:

```python
@dataclass(frozen=True)
class StdioConnectionProfile:
    display_name: str
    command: str
    args: tuple[str, ...] = ()
    cwd: Path | None = None
    transport: Literal["stdio"] = field(default="stdio", init=False)

Responsibilities:

represent project-owned STDIO connection intent
remain independent of MCP SDK runtime objects
distinguish structural profile validity from runtime connection validity

The profile should not be passed directly into presentation.

4. Completed Connection Boundary

Current connection translation operation:

def build_stdio_server_parameters(
    profile: StdioConnectionProfile,
) -> StdioServerParameters:
    ...

Path:

StdioConnectionProfile
        ↓
build_stdio_server_parameters()
        ↓
StdioServerParameters

connection.py owns transport-specific profile-to-SDK translation.

The MCP SDK high-level Client owns actual transport lifecycle mechanics.

Presentation must not depend on this boundary.

5. Completed Inspection Boundary

The central aggregate inspection operation is:

async def inspect_mcp(client: Client) -> MCPInspectionResult:
    ...

It accepts an already-connected high-level MCP SDK Client.

It remains transport-neutral.

Current primitive categories:

tools
resources
resource templates
prompts

Current category statuses:

NOT_ADVERTISED
SUCCESS
PARTIAL
FAILED

Semantics:

NOT_ADVERTISED

The relevant server capability was absent.

pages = ()
failure = None
SUCCESS

Inspection completed successfully.

An empty successful inventory is still SUCCESS.

PARTIAL

One or more complete pages were successfully retrieved, followed by a failure.

The successfully retrieved pages are preserved.

The original exception is preserved.

FAILED

The first request failed before any page was successfully retrieved.

pages = ()
failure = original exception
6. Pagination Evidence Model

Primitive inspection preserves complete MCP SDK result pages rather than
flattening them.

Examples include:

ListToolsResult
ListResourcesResult
ListResourceTemplatesResult
ListPromptsResult

A category result conceptually contains:

CategoryInspection
├── status
├── pages: tuple[complete SDK result pages, ...]
└── failure

Presentation must therefore decide how to render useful human-readable
information from these pages without requiring the inspection/result layer to
flatten or duplicate them.

Do not change the result model merely to make terminal formatting easier
unless an architectural review demonstrates a genuine result-model problem.

7. Completed Aggregate Inspection Result

Current structure:

MCPInspectionResult
├── server_description
├── tools
├── resources
├── resource_templates
└── prompts

server_description preserves:

protocol version
server information
server capabilities
instructions

No aggregate overall status is stored.

Any overall summary should preferably be derived from authoritative category
facts rather than stored independently unless a concrete requirement proves
otherwise.

8. Completed Application Result Boundary

Part 2D.1 introduced:

@dataclass(frozen=True)
class InspectionTargetSummary:
    display_name: str
    transport: str

and:

@dataclass(frozen=True)
class ApplicationInspectionResult:
    target: InspectionTargetSummary
    inspection: MCPInspectionResult

InspectionTargetSummary intentionally does not expose:

command
args
cwd
raw connection profile
live Client
connection state
future credentials

This is the safe project-owned identity intended for downstream consumers.

9. Configured Identity vs Server Identity

The application preserves two distinct identities.

Configured/project identity
ApplicationInspectionResult.target

Contains:

display name
transport
Server-reported identity
ApplicationInspectionResult
    .inspection
    .server_description
    .server_info

These are separate facts.

A mismatch is not automatically an error.

Presentation should make the distinction understandable rather than silently
merging the two identities.

10. Completed Application Composition Boundary

Part 2D.1 introduced:

async def inspect_stdio_profile(
    profile: StdioConnectionProfile,
) -> ApplicationInspectionResult:
    ...

The complete STDIO application path is:

StdioConnectionProfile
        ↓
derive InspectionTargetSummary
        ↓
build_stdio_server_parameters()
        ↓
construct MCP SDK Client
        ↓
enter Client async context
        ↓
inspect_mcp(client)
        ↓
MCPInspectionResult
        ↓
exit Client async context
        ↓
ApplicationInspectionResult

The connection is closed before the operation returns.

No live Client is retained by the returned result.

11. Lifecycle Responsibility

The established distinction is:

application.py owns:

    WHEN the connection must be alive


MCP SDK Client owns:

    HOW the connection is opened, negotiated, and cleaned up

Presentation should have no connection-lifecycle responsibility.

By the time presentation receives an ApplicationInspectionResult, the MCP
connection should already be closed.

12. Failure Policy at Part 2D.1 Closure

Primitive inspection failures are represented by CategoryInspection.

Unexpected inspection/orchestration exceptions propagate.

If unexpected inspection raises while the Client is active:

inspection raises
      ↓
Client context exits
      ↓
cleanup occurs
      ↓
same exception propagates

Connection failures currently propagate.

There is no:

application-wide status DTO
connection status DTO
generic failure wrapper
custom application exception hierarchy

Presentation architecture should initially focus on presenting successfully
returned ApplicationInspectionResult values, including represented
NOT_ADVERTISED/PARTIAL/FAILED primitive-category states.

Do not silently redesign connection-failure handling as part of presentation
work.

13. Real Application Integration Proof

Part 2D.1 added one real end-to-end STDIO application integration proof using:

tests/support/minimal_stdio_server.py

The test proves:

real profile
   ↓
real application operation
   ↓
real SDK parameter translation
   ↓
real SDK Client
   ↓
real STDIO subprocess
   ↓
real MCP negotiation
   ↓
real inspect_mcp()
   ↓
real ApplicationInspectionResult

The integration proof required no production-code changes.

The STDIO application composition path should therefore be considered closed.

14. Current Production Modules

At the start of Part 2D.2:

src/mcp_details/
    __init__.py
    profiles.py
    connection.py
    results.py
    inspection.py
    application.py

No presentation module has yet been established.

15. Current Responsibility Map
profiles.py
    project-owned connection configuration

connection.py
    transport-specific profile → SDK parameter translation

inspection.py
    transport-neutral read-only inspection

results.py
    structured project-owned inspection/application results

application.py
    application composition and connection lifetime scope

presentation
    NOT YET DESIGNED
	
16. Read-Only Policy

The application remains strictly read-only for ordinary inspection.

Allowed ordinary inspection behavior:

initialization/negotiation
capability discovery
list tools
list resources
list resource templates
list prompts

Ordinary inspection must not:

execute tools
read resource contents
materialize resource templates
execute/get prompts

Presentation must consume existing evidence only.

Presentation must never trigger additional MCP operations.

17. Part 2D.2 Central Question

The primary architectural question is:

Given an ApplicationInspectionResult, what is the smallest presentation
architecture that can render a complete, useful terminal inspection report
without coupling presentation back into profiles, connection, SDK lifecycle,
or inspection policy?

18. Questions for Part 2D.2 Review

Before implementation, review at least the following.

18.1 Presentation input boundary

Should presentation consume:

ApplicationInspectionResult

as its primary input?

Determine whether there is any legitimate reason for presentation to receive:

raw profiles
SDK Client
SDK connection parameters
transport objects

The current expectation is that it should not.

18.2 Rendering vs printing

Determine whether the first presentation boundary should:

render_report(result) -> str

or directly perform terminal output:

print_report(result) -> None

or use another minimal design.

Consider:

testability
future notebook use
future Streamlit use
future file/export use
separation of rendering from terminal I/O

Do not introduce a complex renderer framework without evidence.

18.3 Report structure

Determine the smallest useful terminal report organization.

Potential sections include:

configured target
server identity
protocol
server capabilities
instructions
tools
resources
resource templates
prompts

Do not treat this list as a predetermined implementation.

18.4 Category status rendering

Determine how presentation should distinguish:

NOT_ADVERTISED
SUCCESS with zero items
SUCCESS with items
PARTIAL with preserved pages and failure
FAILED with no successful pages

These states must not be collapsed into misleading equivalents.

For example:

NOT_ADVERTISED

is semantically different from:

SUCCESS with zero tools
18.5 Preserved pagination

Determine how terminal presentation should consume complete SDK result pages.

The result boundary currently preserves pages because they are authoritative
inspection evidence.

Presentation may iterate across pages for display purposes, but should not
force the result model itself to flatten them merely for formatting
convenience.

18.6 Failure presentation

Determine how preserved exceptions should be represented to a human.

Questions include:

exception type?
exception message?
both?
whether raw exception repr is appropriate?
how PARTIAL differs visually from FAILED?

Do not discard preserved failure evidence.

18.7 Server capabilities

Determine how server capabilities should be rendered without creating
presentation-owned interpretations that contradict the authoritative SDK
capability data.

18.8 Schemas and arguments

Determine how to present:

tool input schemas
resource metadata
resource-template metadata
prompt arguments

The goal is useful inspection, not merely object repr output.

18.9 Future presentation surfaces

Terminal is the first target.

The architecture should remain reasonably usable later for:

notebook
Streamlit
exported reports

However, do not create a generic presentation framework merely to anticipate
those possibilities.

18.10 Presentation contracts vs formatting choices

Clearly distinguish high-value semantic presentation contracts from
low-value formatting details.

Potential high-value contracts include:

all authoritative inspection evidence remains representable
NOT_ADVERTISED is distinguishable from empty SUCCESS
PARTIAL preserves both successful evidence and failure information
configured and server-reported identities remain distinct
presentation performs no MCP operations

Potential low-value details include:

exact whitespace
decorative separators
exact indentation
colors
exact heading punctuation

These should be reviewed rather than assumed.

19. Constraints for Part 2D.2

Do not begin by adding:

renderer class hierarchy
plugin system
output-format registry
generic visitor framework
terminal UI framework
Rich dependency usage merely because it is available
notebook adapter
Streamlit adapter
export subsystem
JSON/YAML serialization layer

First determine the smallest correct presentation boundary.

20. Expected Part 2D.2 Process

Recommended sequence:

Review current result models and application result boundary.
Define presentation responsibility.
Define presentation input.
Decide rendering vs direct output.
Define minimum semantic report structure.
Review category-status presentation semantics.
Review page/item rendering requirements.
Review failure presentation.
Separate architectural contracts from cosmetic formatting.
Propose the smallest safe implementation milestone.
Stop for approval before coding.

21. Regression State

All Part 2D.1 final verification checks passed.

The exact test count from the user's local repository is authoritative.

The project should begin Part 2D.2 from this clean regression baseline.

22. Part 2D.2 Entry Condition

Part 2D.2 should begin with architecture review only.

Do not propose production implementation until the presentation boundary has
been reviewed and the smallest first milestone has been approved.