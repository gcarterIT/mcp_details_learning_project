# Part 2E — Streamable HTTP Transport Architectural Review

We are continuing my MCP Details Learning Project.

Part 2D is complete.

The application currently supports complete strictly read-only MCP
inspection through STDIO, including:

- explicit STDIO connection profiles;
- MCP SDK v2 Client connection;
- real STDIO subprocess connection and MCP negotiation;
- transport-neutral inspection;
- capability-aware tools, resources, resource-template, and prompt
  discovery;
- pagination exhaustion and partial-result preservation;
- structured application results;
- complete terminal presentation;
- real end-to-end STDIO manual acceptance.

Part 2D.2C.5 manual acceptance also discovered and corrected a duplicate
Tools-section presentation-composition defect. The core presentation
composition test now protects exactly one top-level section for each
primitive category.

The final baseline entering this chat is:

- Python 3.12.7
- MCP Python SDK 2.1.1
- pytest 9.1.1
- anyio 4.14.2
- 23 presentation tests passing
- 74 total project tests passing
- 0 failures
- terminal presentation boundary formally closed
- real STDIO manual acceptance complete

Please use the following project artifacts as the authoritative context
for this conversation:

- `MCP_DETAILS_PROJECT_CONTEXT.md`, if available
- `ARCHITECTURAL_DECISION_LEDGER.md`
- `Part_2D.2C_Completion_Note.md`
- `PART2E_CONTEXT_20260916.md`

We are now beginning:

**Part 2E — Streamable HTTP Transport Architectural Review**

The purpose of Part 2E is not merely to add HTTP connectivity.

Streamable HTTP is the project's second concrete transport, so this is
the correct point to determine—based on evidence rather than
speculation—which parts of the existing profile, connection, and
application-composition architecture are genuinely transport-neutral and
which should remain transport-specific.

Before proposing any production code:

1. Review the attached/current project context and architectural
   decisions.

2. Review the actual current profile, connection, and application
   composition architecture that I provide.

3. Establish the authoritative MCP Python SDK 2.1.1 Streamable HTTP
   Client API and lifecycle contract. Do not assume the SDK shape from
   an earlier MCP SDK version.

4. Compare the concrete Streamable HTTP requirements with the completed
   STDIO path.

5. Identify which existing boundaries can remain unchanged.

6. Determine whether any shared profile, connection, or application
   abstraction is now justified by the existence of the second concrete
   transport.

7. Do not introduce a generic ConnectionProfile hierarchy, transport
   registry, factory framework, strategy pattern, lifecycle abstraction,
   or generic dispatcher unless the comparison demonstrates a concrete
   need.

8. Preserve the closed transport-neutral inspection, structured-result,
   and presentation boundaries unless Streamable HTTP reveals a real
   contradiction.

9. Pay particular attention to HTTP-specific connection information,
   authentication, headers, credentials, and the boundary between
   connection configuration and presentation-safe target identity.

10. Recommend the smallest safe first Part 2E milestone.

Continue using our established development method:

- architecture before implementation;
- professor/software-architect style;
- explain why before code;
- extremely small, highly testable milestones;
- preserve behavior exactly;
- compile after every implementation;
- focused tests after implementation;
- full regression after each completed milestone;
- stop after every checkpoint;
- separate architectural decisions from implementation;
- distinguish high-value contracts from low-value edge cases;
- avoid speculative abstractions.

Do not begin coding until the initial Part 2E architectural and SDK
contract review is complete.