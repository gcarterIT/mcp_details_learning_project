# MCP Details Learning Project — Part 1 Initial Architecture and Reuse Review

We are beginning a new learning project titled:

**MCP Details Learning Project**

Please use the attached:

* `MCP_DETAILS_PROJECT_CONTEXT.md`

as the authoritative starting context.

The new project builds on architectural lessons and selected code from my completed **MCP Client Learning Project**, but it is a separate project with different requirements.

## Goal

Build a general-purpose, strictly read-only MCP inspection application.

The application should eventually support:

```text
STDIO
+
Streamable HTTP
```

while keeping the architecture reasonably open to additional transports if a genuine future requirement appears.

I want to be able to research an MCP available on the internet, determine how to connect to it, give that connection information to this application, and receive a detailed report describing everything the MCP advertises.

For example, if I discover a weather MCP, I want the application to tell me in detail:

* server identity and initialization metadata,
* negotiated/protocol information,
* server capabilities,
* every tool,
* every static resource,
* every resource template,
* every prompt,
* all supplied descriptions,
* all supplied tool parameter/schema information,
* all supplied prompt argument information,
* and other relevant MCP-defined descriptive metadata.

The application should NOT normally:

* call discovered tools,
* read arbitrary resource contents,
* render/invoke prompts,
* or contain server-specific workflows.

The central distinction is:

```text
CAPABILITY INSPECTION
        ≠
CAPABILITY EXECUTION
```

## Initial Connection Strategy

Do not assume that a string such as:

```text
weather-mcp/weather-mcp
```

is sufficient connection information.

For the initial project, assume that I first research the server and create an explicit connection profile containing the information required to connect through STDIO or Streamable HTTP.

Automatic registry/GitHub/package resolution may be considered later, but it is not an initial requirement.

Before implementation, review whether this is the correct boundary.

## Part 1 — Initial Architecture and Reuse Review

Before proposing any production implementation:

1. Review the relevant architecture from the completed MCP Client Learning Project.

2. Identify which existing concepts/code are genuinely useful to this new project, especially:

   * connection lifecycle architecture,
   * `MCPConnection`,
   * Discovery,
   * formatting,
   * validation,
   * package architecture,
   * SDK-boundary decisions,
   * public-API lessons,
   * integration-testing lessons.

3. Clearly identify what should NOT be copied, particularly the old demo-specific workflow architecture.

4. Review whether the old `MCPConnection` abstraction should:

   * be reused unchanged,
   * be adapted,
   * be decomposed,
   * or merely serve as reference material.

   Remember that the old abstraction was deliberately STDIO-oriented while this project requires both STDIO and Streamable HTTP.

5. Review the current installed MCP Python SDK APIs relevant to:

   * STDIO client transport,
   * Streamable HTTP client transport,
   * `ClientSession`,
   * initialization,
   * `InitializeResult`,
   * server information,
   * server capabilities,
   * `list_tools()`,
   * `list_resources()`,
   * `list_resource_templates()`,
   * `list_prompts()`.

6. Inspect the actual SDK result/model structures needed to answer:

```text
What information can an MCP server
actually provide about itself?
```

Do not guess fields from memory when the installed SDK can establish the contract.

7. Define what **complete MCP inspection information** should mean for this project.

For tools, investigate all available descriptive/schema fields, including where available:

```text
name
title
description
input schema
output schema
parameter names
parameter descriptions
types
required/optional
defaults
enums
nested structures
constraints
annotations
metadata
```

For resources, investigate both:

```text
static resources
resource templates
```

and all available descriptive metadata.

For prompts, investigate all available prompt and argument metadata.

For initialization, investigate server identity, version, protocol/capability information, and other relevant fields.

8. Review the proposed connection-profile boundary:

```text
MCP research/resolution
        │
        ▼
explicit connection profile
        │
        ▼
MCP Details inspector
```

Determine the smallest sensible profile needed for:

```text
STDIO
```

and:

```text
Streamable HTTP
```

Do not build an automatic registry/repository resolver yet.

9. Design the conceptual architecture before writing code.

Consider a flow such as:

```text
Connection Profile
        │
        ▼
Transport-specific connection
        │
        ▼
ClientSession
        │
        ▼
Initialization Inspection
        +
Primitive Discovery
        │
        ▼
Inspection / Normalization
        │
        ▼
Structured Inspection Result
        │
        ▼
Terminal Renderer
```

But do not adopt this architecture merely because it looks clean. Determine which boundaries are genuinely justified.

10. Consider future presentation requirements:

```text
Terminal initially

possibly later:
Notebook
Streamlit
Markdown/report output
```

The first implementation should remain terminal-only, but discovery logic should not become unnecessarily bound to terminal printing.

11. Determine whether a project-owned normalized inspection/report model is justified.

The previous project deliberately avoided unnecessary DTOs.

This project may have a stronger reason for structured project-owned inspection data because:

* multiple MCP result types need to be combined,
* schemas need detailed presentation,
* and future renderers may consume the same inspection data.

Review this architecturally rather than assuming either answer.

12. Identify the smallest safe first implementation milestone.

Prefer beginning with **one known STDIO MCP server** rather than implementing STDIO and Streamable HTTP simultaneously.

The first milestone should prove only the minimum architecture necessary before expanding it.

13. Clearly distinguish throughout the review:

```text
PROJECT-OWNED POLICY
        versus
MCP SDK SEMANTIC API
        versus
TRANSPORT-SPECIFIC MECHANICS
        versus
PRESENTATION
```

14. Identify what should be carried forward as an architectural decision and what should remain deliberately unresolved.

## Development Method

Continue the teaching/development method from the MCP Client Learning Project:

* architecture before implementation,
* professor/software-architect explanations,
* extremely small milestones,
* one architectural dimension at a time,
* compile after implementation changes,
* focused test after each contract change,
* full regression after implementation milestones,
* stop after every checkpoint,
* preserve known-good behavior,
* do not add tests merely for coverage,
* do not refactor merely for symmetry,
* do not introduce abstractions merely because they might be useful later.

Additionally, maintain an **Architectural Decision Ledger** for important decisions:

```text
Question
    ↓
Evidence
    ↓
Decision
    ↓
Contract created/protected
    ↓
Alternatives deferred
```

This will be a long learning project, so favor correctness and understanding over speed.

Begin with the **Part 1 architectural review only**.

**Do not write production code yet.**
