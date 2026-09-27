# Part 2E Completion Note — Streamable HTTP Transport Support

## Status

Part 2E is complete.

The MCP Details application now supports both initial project transports:

- STDIO
- Streamable HTTP

The Streamable HTTP path has been implemented through the existing application
architecture and verified with both focused composition tests and a real
end-to-end SDK integration test.

Final regression baseline:

- 84 tests passed
- 0 tests failed

---

## Part 2E Objective

The objective of Part 2E was to add the project's second originally planned
transport, Streamable HTTP, without weakening or prematurely generalizing the
architecture established during Parts 2A through 2D.

The completed architecture demonstrates that the existing inspection, result,
and presentation boundaries remain transport-neutral after introducing a
second genuinely different transport.

---

## Completed Profile Model

A project-owned Streamable HTTP profile was added:

```python
@dataclass(frozen=True)
class StreamableHttpConnectionProfile:
    """Project-owned configuration describing a Streamable HTTP MCP connection."""

    display_name: str
    url: str
    transport: Literal["streamable_http"] = field(
        default="streamable_http",
        init=False,
    )

    def __post_init__(self) -> None:
        if not self.display_name.strip():
            raise ValueError("display_name must not be blank")
        if not self.url.strip():
            raise ValueError("url must not be blank")

The initial profile intentionally contains only:

display_name
url
fixed transport="streamable_http"

Validation remains structural rather than attempting to establish runtime
connection validity.

Advanced HTTP concerns were intentionally deferred.

Installed SDK Contract Verification

The installed MCP Python SDK version remains:

MCP SDK 2.1.1

Installed-environment introspection confirmed that the high-level SDK Client
accepts a URL string directly as a server target.

Therefore the minimal Streamable HTTP connection path is:

StreamableHttpConnectionProfile
        ↓
profile.url
        ↓
Client(profile.url)

No project-owned HTTP target builder was introduced because the required
translation would currently be only:

str → str

The SDK already owns Streamable HTTP transport construction, MCP negotiation,
and connection mechanics for this case.

Application Composition

A Streamable HTTP application entry point was added:

async def inspect_streamable_http_profile(
    profile: StreamableHttpConnectionProfile,
) -> ApplicationInspectionResult:

The transport-specific application entry point:

constructs a safe InspectionTargetSummary;
constructs the SDK Client from profile.url; and
delegates the common connected-client lifecycle to the shared private
application helper.

After both STDIO and Streamable HTTP paths existed, demonstrated lifecycle
duplication justified extracting:

async def _inspect_client(
    client: Client,
    target: InspectionTargetSummary,
) -> ApplicationInspectionResult:

The helper owns the common sequence:

already-constructed Client
        ↓
enter Client context
        ↓
inspect_mcp(client)
        ↓
exit Client context
        ↓
ApplicationInspectionResult

The helper does not accept connection profiles and does not dispatch on
transport type.

Transport-specific behavior remains outside the helper.

Final Application Architecture

The resulting two-transport application composition is:

StdioConnectionProfile
        ↓
build_stdio_server_parameters()
        ↓
Client(parameters)
        │
        │
        ├───────────────┐
                        ▼
                 _inspect_client()
                        ▲
        ├───────────────┘
        │
Client(profile.url)
        ↑
StreamableHttpConnectionProfile

After Client construction, both transports use the same lifecycle,
transport-neutral inspection boundary, result model, and presentation
boundary.

Intentional Transport Asymmetry

STDIO and Streamable HTTP connection construction remain intentionally
asymmetric.

STDIO requires meaningful project-to-SDK translation:

StdioConnectionProfile
        ↓
build_stdio_server_parameters()
        ↓
StdioServerParameters
        ↓
Client

Minimal Streamable HTTP does not:

StreamableHttpConnectionProfile
        ↓
profile.url
        ↓
Client

No artificial HTTP builder was added merely to make the two diagrams
symmetrical.

Architecture continues to reflect actual responsibilities rather than visual
symmetry.

Safe Target Summary

Operational connection profiles do not flow into the result or presentation
boundaries.

Instead, application composition derives:

InspectionTargetSummary
    display_name
    transport

This preserves the configured target identity needed for reporting while
excluding operational connection information such as:

STDIO command
STDIO arguments
working directory
HTTP URL
future credentials or authentication configuration

The target summary does not drive MCP inspection. It is carried alongside the
inspection result for safe application reporting.

Configured target identity remains distinct from server-reported identity.

Inspection Boundary Validation

No Streamable HTTP-specific changes were required in inspect_mcp().

The inspection boundary continues to consume an already-connected SDK
Client.

This means the same inspection implementation now works across:

STDIO
Streamable HTTP

The addition of the second transport therefore provides concrete evidence
that the inspection boundary is genuinely transport-neutral.

Results and Presentation

No transport-specific redesign was required for:

MCPInspectionResult
ApplicationInspectionResult
render_report()

Presentation continues to consume structured application results rather than
connection profiles or SDK transport objects.

The presentation layer therefore does not need access to operational
connection configuration.

Streamable HTTP Composition Tests

Focused application tests protect the Streamable HTTP composition contract.

The success-path test verifies:

the profile URL is passed to the SDK Client;
the Client is entered before inspection;
inspection occurs while the Client is connected;
the Client exits after inspection;
the safe target summary is preserved; and
the inspection result is preserved.

The failure-path test verifies:

inspection failures propagate; and
the Client context is still exited when inspection raises.
Real Streamable HTTP Integration Proof

A real integration fixture was added:

tests/support/minimal_streamable_http_server.py

The fixture uses the MCP SDK 2.1.1 high-level MCPServer API and:

run_streamable_http_async()

to expose a real Streamable HTTP MCP endpoint through Uvicorn.

The integration test:

selects an available localhost port;
launches the MCP server in a separate subprocess;
waits until the TCP endpoint is ready;
creates a real StreamableHttpConnectionProfile;
invokes the production inspect_streamable_http_profile() path;
establishes a real SDK Streamable HTTP connection;
performs real MCP initialization/negotiation;
executes the real transport-neutral inspection path;
verifies the server-reported identity and application target identity; and
terminates the server subprocess safely.

This establishes the complete path:

StreamableHttpConnectionProfile
        ↓
inspect_streamable_http_profile()
        ↓
real SDK Client
        ↓
real Streamable HTTP
        ↓
real MCPServer
        ↓
real MCP negotiation
        ↓
inspect_mcp()
        ↓
MCPInspectionResult
        ↓
ApplicationInspectionResult

STDIO and Streamable HTTP now both have real SDK integration evidence.

Architectural Decisions Added
AD-049 — Use the SDK Client URL Contract Directly for Minimal Streamable HTTP

For the initial unauthenticated Streamable HTTP path, the resolved URL is
passed directly to the SDK Client.

No project-owned HTTP target builder, connection wrapper, factory, registry,
or transport strategy is introduced while there is no meaningful additional
connection-construction responsibility.

AD-050 — Share Application Lifecycle Only After Transport-Specific Client Construction

Transport-specific application entry points remain responsible for
constructing their respective SDK Clients.

Only after Client construction does execution converge on the shared private
application lifecycle helper.

This preserves explicit transport-specific construction while keeping the
connected-client lifecycle and inspection path transport-neutral.

Architecture Deliberately Not Introduced

Part 2E does not introduce:

a base connection-profile hierarchy;
a generic connection factory;
a connection registry;
transport strategy objects;
a project-owned MCP connection façade;
a generic transport dispatcher;
an HTTP target builder with no meaningful translation responsibility;
a credential framework;
a profile persistence format; or
support for every SDK transport.

These remain unjustified by current project requirements.

Deferred Streamable HTTP Territory

Part 2E closes the initial resolved, unauthenticated Streamable HTTP path.

It does not claim complete support for every possible HTTP MCP deployment.

The following remain intentionally deferred until concrete requirements arise:

authentication;
OAuth;
API keys;
custom HTTP headers;
credential references and resolution;
custom HTTP clients;
timeout configuration;
TLS customization;
proxy configuration; and
other advanced HTTP connection policies.

The installed SDK exposes lower-level HTTP construction facilities that can be
used later if such requirements justify additional connection-layer behavior.

Additional Transports

The project remains architecturally open to additional transports.

However, SDK support for another transport does not by itself make that
transport a project requirement.

SSE and other transports remain outside the initial project scope.

The two explicitly selected initial transports are now implemented:

STDIO
Streamable HTTP
Read-Only Policy

Part 2E preserves the project's strict inspection-only policy.

The transport work did not introduce workflow execution such as:

tool invocation;
resource reading;
resource-template materialization; or
prompt execution/retrieval beyond discovery.

MCP Details remains a discovery and inspection application.

Final Verification

Part 2E closure included:

python -m compileall src\mcp_details tests
python -m pytest tests\test_profiles.py -v
python -m pytest tests\test_application.py -v
python -m pytest -v

All final verification commands completed successfully.

The application suite contains:

6 passed

The final project regression baseline is:

84 passed
0 failed
Part 2E Closure Statement

Part 2E adds the project's second initial transport, Streamable HTTP, through
a project-owned explicit connection profile and application-composition path
using the MCP Python SDK 2.1.1 Client URL contract.

Both STDIO and Streamable HTTP are protected by real SDK integration tests.

Inspection, result modeling, and presentation remain transport-neutral.

Advanced HTTP authentication/configuration, additional transports, generic
profile dispatch, profile persistence, and user-facing profile-input/CLI
concerns are intentionally deferred.

Part 2E is complete.