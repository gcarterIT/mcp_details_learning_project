# MCP Details Learning Project — Initial Context

**Project:** MCP Details Learning Project
**Status:** New Project — Initial Architecture Review
**Parent Learning Project:** MCP Client Learning Project
**Starting Date:** 2026-08-22

---

# 1. Project Purpose

The MCP Details Learning Project will reuse lessons and selected code from the completed **MCP Client Learning Project** to build a new, general-purpose, read-only MCP inspection application.

The application should allow a user to research an MCP server available on the internet, configure a connection to that server, and produce a detailed report describing the server and everything it advertises through MCP discovery operations.

The application is intended primarily as a learning tool for understanding the structure and capabilities of arbitrary MCP servers.

The project should proceed slowly, beginning with the smallest useful implementation and adding capabilities only after their architecture is understood.

---

# 2. Primary Goal

Build an application that can inspect arbitrary MCP servers using:

```text
STDIO
+
Streamable HTTP
```

The architecture should initially support these two transports while avoiding unnecessary coupling that would make an additional transport impossible to add later.

The application should be strictly:

```text
DISCOVERY / INSPECTION ONLY
```

It should not normally:

```text
call tools
read arbitrary resource contents
render/invoke prompts
perform MCP-specific workflows
modify remote state
```

Its responsibility is to discover and describe what an MCP server exposes.

---

# 3. Intended User Experience

Conceptually:

```text
User researches an MCP
        │
        ▼
obtains connection information
        │
        ▼
creates/selects connection profile
        │
        ▼
MCP Details application
        │
        ▼
connect
        │
        ▼
initialize
        │
        ▼
inspect server metadata/capabilities
        │
        ▼
list MCP primitives
        │
        ├── tools
        ├── resources
        ├── resource templates
        └── prompts
        │
        ▼
normalize inspection data
        │
        ▼
produce detailed terminal report
```

Example user intent:

```text
"I found weather-mcp/weather-mcp
and want to know exactly what this MCP exposes."
```

The first versions of the application should NOT assume that an arbitrary identifier such as:

```text
weather-mcp/weather-mcp
```

contains enough information to connect to the server.

It may represent:

* a GitHub repository,
* an MCP registry identifier,
* a package,
* a vendor-specific server name,
* or an informal human-readable label.

Instead, the initial architecture should separate:

```text
MCP DISCOVERY / RESEARCH
        ≠
MCP CONNECTION
```

---

# 4. Initial Connection-Profile Model

Version 1 should use an explicit connection profile after the server has been researched.

Conceptually:

```text
MCPServerProfile
│
├── display_name
├── source/reference
├── transport
│
├── STDIO configuration
│      ├── command
│      ├── args
│      ├── environment references
│      └── optional working directory
│
└── Streamable HTTP configuration
       ├── URL
       ├── headers if required
       └── authentication references if required
```

Exact models and fields must NOT be implemented until the architecture has been reviewed.

Secrets should not be embedded unnecessarily in stored profiles or generated reports.

A future phase may investigate automatic resolution from:

```text
registry identifier
GitHub repository
package identifier
vendor URL
```

into a usable connection profile.

That resolver is NOT required for the first implementation.

---

# 5. MCP Information to Inspect

The application should capture as much descriptive MCP information as the connected server and MCP SDK make available.

At minimum, investigate and report information obtained from:

```text
ClientSession.initialize()

ClientSession.list_tools()

ClientSession.list_resources()

ClientSession.list_resource_templates()

ClientSession.list_prompts()
```

The inspection should include initialization/server information where available, including:

```text
server name
server version
protocol version
server capabilities
other relevant initialization metadata
```

The exact fields must be determined from the installed MCP SDK models rather than assumed.

---

# 6. Tool Inspection Requirements

For every advertised tool, the report should attempt to display all server-supplied descriptive information.

Conceptually:

```text
TOOL
│
├── name
├── title, if supplied
├── description
├── input schema
│      ├── parameter names
│      ├── descriptions
│      ├── types
│      ├── required / optional status
│      ├── defaults
│      ├── enums
│      ├── nested objects
│      ├── arrays/items
│      └── constraints
│
├── output schema, if supplied
├── annotations/metadata, if supplied
└── any other relevant MCP-defined fields
```

The application should report what the server actually supplies.

It should not invent missing descriptions or schema information.

---

# 7. Resource Inspection Requirements

The application must treat these as distinct MCP capability categories:

```text
STATIC RESOURCES
        ≠
RESOURCE TEMPLATES
```

For static resources, capture all relevant metadata supplied by the server, such as:

```text
URI
name
title
description
MIME type
size/metadata if available
other MCP-defined fields
```

For resource templates, capture descriptive and URI-template information, including arguments or related metadata where available.

The application should inspect resource metadata only.

Reading the actual resource contents is outside the normal read-only discovery scope unless a future explicit requirement justifies it.

---

# 8. Prompt Inspection Requirements

For every advertised prompt, capture all descriptive information supplied by the server.

Conceptually:

```text
PROMPT
│
├── name
├── title, if supplied
├── description
├── arguments
│      ├── argument name
│      ├── description
│      └── required / optional status
└── other relevant MCP-defined metadata
```

The application should list prompt definitions.

It should not call `get_prompt()` merely to test or execute the prompt during ordinary server inspection unless a later architectural review establishes that prompt rendering is necessary to satisfy the project's inspection goal.

---

# 9. Strict Read-Only Boundary

The normal inspection flow should stop at metadata/discovery operations.

Conceptually:

```text
initialize
    │
    ├── inspect initialization metadata
    ├── list_tools
    ├── list_resources
    ├── list_resource_templates
    └── list_prompts
             │
             ▼
            STOP
```

The project should deliberately avoid demo-specific workflows of the kind used in the MCP Client Learning Project.

Because arbitrary MCP servers will be inspected, the application cannot assume the semantic meaning or safe invocation requirements of their tools, resources, or prompts.

This separation is intentional:

```text
CAPABILITY INSPECTION
        ≠
CAPABILITY EXECUTION
```

---

# 10. Initial Output

The first presentation target is:

```text
TERMINAL
```

The terminal report should eventually be neat, hierarchical, and easy to read.

Conceptually:

```text
============================================================
MCP SERVER REPORT
============================================================

Server
------
Name:
Version:
Protocol:
Transport:

Server Capabilities
-------------------
...

Tools (N)
---------
Tool 1
  Name:
  Description:

  Parameters:
    location
      Type:
      Required:
      Description:

...

Static Resources (N)
--------------------
...

Resource Templates (N)
----------------------
...

Prompts (N)
-----------
...

============================================================
```

Presentation architecture should avoid unnecessarily coupling discovery logic directly to terminal printing.

The code should eventually permit additional presentation targets such as:

```text
Terminal
Notebook
Streamlit
Markdown / structured report
```

without redesigning the MCP inspection core.

Do NOT build those additional interfaces initially.

---

# 11. Important Architecture Principle for Reporting

Prefer this conceptual separation:

```text
MCP SDK RESULTS
      │
      ▼
INSPECTION / NORMALIZATION
      │
      ▼
STRUCTURED PROJECT-OWNED REPORT MODEL
      │
      ▼
FORMATTER / RENDERER
      │
      ▼
TERMINAL
```

However, unlike the previous MCP Client Learning Project, whether a project-owned normalized report model or DTO layer is justified should be reviewed rather than assumed.

This new project has a stronger potential requirement for normalized data because the same inspection results may eventually feed multiple presentation interfaces.

Do not implement such a model until its architectural value is demonstrated.

---

# 12. Lessons Carried Forward from MCP Client Learning Project

The completed MCP Client Learning Project established several architectural lessons that should be used as starting evidence.

## 12.1 Application Execution and Reusable API Are Different

The completed project established:

```text
application execution interface
        ≠
reusable Python public API
```

Do not accidentally conflate these concepts in the new project.

A public reusable API for MCP Details should be considered only after the internal architecture becomes stable enough to justify one.

---

## 12.2 Connection Lifecycle Has Genuine Architectural Ownership

The previous project established `MCPConnection` as a project-owned lifecycle abstraction.

Its conceptual STDIO lifecycle was:

```text
open STDIO transport
        ↓
create ClientSession
        ↓
enter ClientSession context
        ↓
initialize
        ↓
expose initialized session
        ↓
cleanly close lifecycle
```

The reusable public import in the completed project became:

```python
from mcp_client import MCPConnection
```

This code and its tests are useful source material.

However, the new project must NOT simply copy the class unchanged without review because `MCPConnection` was intentionally designed around STDIO, while MCP Details requires:

```text
STDIO
+
Streamable HTTP
```

The first architecture review should determine:

```text
Which lifecycle responsibilities are transport-neutral?

Which responsibilities belong to an STDIO transport adapter?

Which responsibilities belong to a Streamable HTTP transport adapter?
```

Reuse behavior and tested ideas where appropriate.

Do not preserve old structure merely because it already exists.

---

## 12.3 MCP SDK Semantic Types Are Legitimate Dependencies

The completed project determined that using public MCP SDK semantic types is acceptable.

Examples included:

```text
ClientSession
InitializeResult
StdioServerParameters
```

The project should not introduce project-owned wrappers merely to hide legitimate public SDK concepts.

For the new project, this decision should remain the default unless multi-transport or report-normalization requirements provide a genuine reason for another abstraction.

---

## 12.4 Discovery Is Different from Initialization Capability Negotiation

The previous project distinguished:

```text
protocol initialization / negotiated server capabilities
        ≠
application capability inventory
```

The new application needs BOTH.

It should inspect:

```text
InitializeResult / server capability information
```

and separately perform:

```text
list_tools()
list_resources()
list_resource_templates()
list_prompts()
```

The two information sources should not be conceptually merged merely because both describe the server.

---

## 12.5 Discovery Must Be Reconsidered

The previous project's `discover_capabilities()` function:

* called the four discovery/list operations,
* performed presentation,
* returned a four-position tuple.

That implementation was appropriate to the old demo application but was intentionally NOT promoted to its reusable public API.

The new MCP Details project has different requirements.

Its discovery architecture should therefore be reviewed from first principles rather than copied unchanged.

In particular, the new application needs:

```text
more complete metadata
schema inspection
initialization metadata
transport-neutral behavior
clean report generation
future multiple renderers
```

This may justify a richer discovery/result architecture.

---

## 12.6 Old Demo Workflows Should NOT Be Carried Forward

Do not copy these as core new-project architecture:

```text
tool_workflow.py
static_resource_workflow.py
resource_template_workflow.py
prompt_workflow.py
```

They were deliberately demo/application-specific.

The new project does not know the semantics of arbitrary servers and should remain discovery-only.

---

## 12.7 Formatting Lessons Are Useful

The old project separated presentation helpers into `formatters.py`.

That principle remains valuable.

The new project will have substantially more detailed reporting requirements, so presentation should remain separate from connection and discovery behavior.

Do not let terminal formatting become part of the MCP protocol/discovery layer.

---

## 12.8 Validation Lessons Are Useful

The old project separated semantic validation from presentation.

The new project may need validation for:

```text
connection profiles
transport-specific configuration
returned metadata
schema normalization
report assumptions
```

But validation should be introduced only when a concrete contract exists.

---

## 12.9 Package and Import Lessons Should Be Preserved

The previous project learned to:

* use package-aware imports,
* avoid bare sibling-import ambiguity,
* support intentional application entry points,
* distinguish internal modules from curated public API.

The new project should begin with proper package architecture rather than repeating the earlier import-cleanup phase.

---

## 12.10 Tests Should Protect Architecture, Not Coverage Numbers

Carry forward this rule:

```text
test important contracts
        ≠
test everything because it exists
```

Do not add tests merely to increase coverage.

Each test should protect a behavior or architectural boundary important enough that an accidental change should be detected.

---

# 13. Useful Source Material from the Completed Project

The following completed-project files/concepts may be useful references when beginning MCP Details:

```text
src/mcp_client/connection.py
tests/test_connection.py

src/mcp_client/discovery.py
tests/test_discovery.py

src/mcp_client/formatters.py
src/mcp_client/validation.py

src/mcp_client/client.py

src/mcp_client/__init__.py
src/mcp_client/__main__.py

tests/test_package_interface.py
tests/test_public_api_integration.py

configs/demo_stdio.json
configs/demo_http.json

requirements.txt
pyproject.toml

Part_11_Completion_Note.md
Part_12_Completion_Note.md
Part_13_Completion_Note.md
README.md
```

Do not assume these should all be copied.

They are architectural reference material.

---

# 14. Recommended Starting Architecture Question

Before copying production code, answer:

```text
What is the smallest transport-neutral architecture
that can:

1. connect to one known STDIO MCP server,
2. initialize it,
3. collect initialization metadata,
4. list all four MCP primitive categories,
5. preserve complete descriptive metadata,
6. and return data independently of terminal presentation?
```

Only after this is understood should Streamable HTTP be added.

Although supporting both transports is a project requirement, implementing both simultaneously in the first milestone would introduce unnecessary debugging dimensions.

Recommended progression:

```text
Architecture review
        ↓
minimal STDIO inspector
        ↓
complete metadata inspection
        ↓
structured reporting
        ↓
Streamable HTTP transport
        ↓
transport-neutral connection interface
        ↓
arbitrary external MCP profiles
        ↓
terminal reporting improvements
        ↓
future UI/report targets
```

The exact order may change if architectural review provides better evidence.

---

# 15. MCP Research and Connection Strategy

For the first project versions, treat researching a server and connecting to it as separate activities.

Suggested workflow:

```text
find MCP server
        ↓
research authoritative server documentation
        ↓
determine:
    transport
    command/package OR URL
    required arguments
    required environment variables
    authentication
        ↓
create explicit connection profile
        ↓
inspect with MCP Details
```

Potential research sources include:

```text
Official MCP Registry
server maintainer documentation
official GitHub repository
vendor documentation
package documentation
```

Do not assume a repository identifier alone is executable connection information.

Automatic server-name resolution may become a later subsystem if there is a demonstrated need.

---

# 16. Development / Teaching Contract

Continue the development method proven in the MCP Client Learning Project.

## Architecture First

Before implementation:

1. identify the responsibility,
2. identify the architectural boundary,
3. identify the contract,
4. distinguish project policy from MCP SDK behavior,
5. determine the smallest implementation.

## Extremely Small Milestones

Prefer:

```text
one architectural decision
        ↓
one small implementation
        ↓
compile
        ↓
focused test
        ↓
complete regression
        ↓
STOP
```

Avoid implementing multiple architectural dimensions simultaneously.

## Preserve Known-Good Behavior

When code is reused from the completed project:

```text
understand existing contract
        ↓
copy only what is justified
        ↓
verify behavior
        ↓
modify incrementally
```

## Stop at Checkpoints

After every milestone:

* explain what changed,
* explain why,
* compile,
* run the relevant test,
* run regression when implementation changed,
* stop for review before proceeding.

## No Speculative Abstractions

Do not introduce:

* generic transport factories,
* DTO hierarchies,
* registries,
* plugin systems,
* repository resolvers,
* generic renderer frameworks,

until a demonstrated requirement makes the abstraction useful.

---

# 17. Process Improvement — Architectural Decision Ledger

For this project, maintain a lightweight decision ledger.

For important decisions record:

```text
Question
    ↓
Evidence
    ↓
Decision
    ↓
Contract created/protected
    ↓
Alternatives deliberately deferred
```

Example:

```text
Question:
Should arbitrary MCP names automatically resolve to connection details?

Evidence:
Different servers may publish different launch/remote connection information.

Decision:
Version 1 requires an explicit connection profile.

Protected Contract:
Inspection receives resolved connection configuration.

Deferred:
Registry/repository automatic resolver.
```

This should reduce context loss during a long multi-chat project and make it clear which decisions are settled versus still open.

---

# 18. Initial Scope Constraints

Do NOT begin the project by implementing:

```text
automatic MCP registry resolution
automatic GitHub installation
tool execution
resource-content retrieval
prompt execution/rendering
Notebook UI
Streamlit UI
generic plugin architecture
production publishing
generic workflow abstraction
```

Begin with the smallest architecture that proves correct inspection of one known MCP server.

---

# 19. Initial Success Definition

The earliest meaningful success state should be approximately:

```text
known MCP server
        │
        ▼
known connection profile
        │
        ▼
connect successfully
        │
        ▼
initialize successfully
        │
        ▼
capture server initialization information
        │
        ├── list_tools()
        ├── list_resources()
        ├── list_resource_templates()
        └── list_prompts()
        │
        ▼
return complete inspection information
        │
        ▼
render basic terminal report
```

The first implementation does NOT need attractive final formatting.

Correct architectural separation comes before presentation polish.

---

# 20. First Conversation Objective

Begin the new project with:

# Part 1 — Initial Architecture and Reuse Review

Before implementing anything:

1. review the completed MCP Client Learning Project architecture that is relevant to MCP Details,
2. distinguish reusable ideas from demo-specific code,
3. inspect the current MCP Python SDK interfaces needed for STDIO and Streamable HTTP,
4. design the smallest transport-neutral conceptual architecture,
5. decide what, if anything, should initially be copied from `MCPConnection`,
6. define the first explicit MCP connection-profile contract,
7. define what “complete MCP details” means according to actual SDK models,
8. propose the smallest safe first implementation milestone.

Do not write production code until this architectural review is complete.
