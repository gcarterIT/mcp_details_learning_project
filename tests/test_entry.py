"""Tests for the MCP Details application-entry composition boundary."""
import subprocess
import sys

from pathlib import Path

import pytest

from mcp_details import entry
from mcp_details.profiles import (
    StdioConnectionProfile,
    StreamableHttpConnectionProfile,
)

@pytest.mark.anyio
async def test_streamable_http_entry_composes_profile_inspection_and_rendering(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Resolved HTTP entry values flow through inspection and rendering."""

    events: list[object] = []
    inspection_result = object()

    async def fake_inspect_streamable_http_profile(
        profile: StreamableHttpConnectionProfile,
    ) -> object:
        events.append(("inspect", profile))
        return inspection_result

    def fake_render_report(result: object) -> str:
        events.append(("render", result))
        return "EXPECTED REPORT"

    monkeypatch.setattr(
        entry,
        "inspect_streamable_http_profile",
        fake_inspect_streamable_http_profile,
    )
    monkeypatch.setattr(
        entry,
        "render_report",
        fake_render_report,
    )

    report = await entry.inspect_and_render_streamable_http(
        display_name="Demo Server",
        url="https://example.test/mcp",
    )

    assert report == "EXPECTED REPORT"

    assert len(events) == 2

    inspection_event = events[0]
    assert inspection_event[0] == "inspect"

    profile = inspection_event[1]
    assert isinstance(profile, StreamableHttpConnectionProfile)
    assert profile.display_name == "Demo Server"
    assert profile.url == "https://example.test/mcp"
    assert profile.transport == "streamable_http"

    assert events[1] == ("render", inspection_result)
    
@pytest.mark.anyio
async def test_stdio_entry_composes_profile_inspection_and_rendering(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Resolved STDIO entry values flow through inspection and rendering."""

    events: list[object] = []
    inspection_result = object()

    async def fake_inspect_stdio_profile(
        profile: StdioConnectionProfile,
    ) -> object:
        events.append(("inspect", profile))
        return inspection_result

    def fake_render_report(result: object) -> str:
        events.append(("render", result))
        return "EXPECTED REPORT"

    monkeypatch.setattr(
        entry,
        "inspect_stdio_profile",
        fake_inspect_stdio_profile,
    )
    monkeypatch.setattr(
        entry,
        "render_report",
        fake_render_report,
    )

    report = await entry.inspect_and_render_stdio(
        display_name="Demo Server",
        command="python",
        args=("server.py", "--readonly"),
        cwd=Path("C:/mcp/demo"),
    )

    assert report == "EXPECTED REPORT"

    assert len(events) == 2

    inspection_event = events[0]
    assert inspection_event[0] == "inspect"

    profile = inspection_event[1]
    assert isinstance(profile, StdioConnectionProfile)
    assert profile.display_name == "Demo Server"
    assert profile.command == "python"
    assert profile.args == ("server.py", "--readonly")
    assert profile.cwd == Path("C:/mcp/demo")
    assert profile.transport == "stdio"

    assert events[1] == ("render", inspection_result)  
    
def test_parse_arguments_parses_streamable_http_command() -> None:
    """Streamable HTTP command-line arguments preserve resolved values."""

    parsed = entry._parse_arguments(
        [
            "streamable-http",
            "--name",
            "Demo Server",
            "--url",
            "http://localhost:8000/mcp",
        ]
    )

    assert parsed.transport == "streamable-http"
    assert parsed.name == "Demo Server"
    assert parsed.url == "http://localhost:8000/mcp"
    
def test_parse_arguments_parses_stdio_command_with_server_arguments() -> None:
    """STDIO command-line parsing preserves target-server arguments in order."""

    parsed = entry._parse_arguments(
        [
            "stdio",
            "--name",
            "Demo Server",
            "--command",
            "python",
            "--cwd",
            r"C:\mcp\demo",
            "--",
            "server.py",
            "--mode",
            "readonly",
        ]
    )

    assert parsed.transport == "stdio"
    assert parsed.name == "Demo Server"
    assert parsed.command == "python"
    assert parsed.cwd == r"C:\mcp\demo"
    assert parsed.server_args == [
        "server.py",
        "--mode",
        "readonly",
    ]
    
@pytest.mark.anyio
async def test_run_parsed_arguments_routes_streamable_http_command(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Parsed HTTP arguments route to the HTTP entry operation."""

    calls: list[object] = []

    async def fake_inspect_and_render_streamable_http(
        display_name: str,
        url: str,
    ) -> str:
        calls.append((display_name, url))
        return "EXPECTED REPORT"

    monkeypatch.setattr(
        entry,
        "inspect_and_render_streamable_http",
        fake_inspect_and_render_streamable_http,
    )

    parsed = entry._parse_arguments(
        [
            "streamable-http",
            "--name",
            "Demo Server",
            "--url",
            "http://localhost:8000/mcp",
        ]
    )

    report = await entry._run_parsed_arguments(parsed)

    assert report == "EXPECTED REPORT"
    assert calls == [
        (
            "Demo Server",
            "http://localhost:8000/mcp",
        )
    ]
    
@pytest.mark.anyio
async def test_run_parsed_arguments_routes_stdio_command(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Parsed STDIO arguments adapt values and route to the STDIO entry operation."""

    calls: list[object] = []

    async def fake_inspect_and_render_stdio(
        display_name: str,
        command: str,
        args: tuple[str, ...] = (),
        cwd: Path | None = None,
    ) -> str:
        calls.append(
            (
                display_name,
                command,
                args,
                cwd,
            )
        )
        return "EXPECTED REPORT"

    monkeypatch.setattr(
        entry,
        "inspect_and_render_stdio",
        fake_inspect_and_render_stdio,
    )

    parsed = entry._parse_arguments(
        [
            "stdio",
            "--name",
            "Demo Server",
            "--command",
            "python",
            "--cwd",
            r"C:\mcp\demo",
            "--",
            "server.py",
            "--mode",
            "readonly",
        ]
    )

    report = await entry._run_parsed_arguments(parsed)

    assert report == "EXPECTED REPORT"
    assert calls == [
        (
            "Demo Server",
            "python",
            (
                "server.py",
                "--mode",
                "readonly",
            ),
            Path(r"C:\mcp\demo"),
        )
    ]
    
@pytest.mark.anyio
async def test_run_parsed_arguments_routes_minimal_stdio_command(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Minimal STDIO arguments preserve absent cwd and empty server arguments."""

    calls: list[object] = []

    async def fake_inspect_and_render_stdio(
        display_name: str,
        command: str,
        args: tuple[str, ...] = (),
        cwd: Path | None = None,
    ) -> str:
        calls.append(
            (
                display_name,
                command,
                args,
                cwd,
            )
        )
        return "EXPECTED REPORT"

    monkeypatch.setattr(
        entry,
        "inspect_and_render_stdio",
        fake_inspect_and_render_stdio,
    )

    parsed = entry._parse_arguments(
        [
            "stdio",
            "--name",
            "Demo Server",
            "--command",
            "python",
        ]
    )

    report = await entry._run_parsed_arguments(parsed)

    assert report == "EXPECTED REPORT"
    assert calls == [
        (
            "Demo Server",
            "python",
            (),
            None,
        )
    ]
    
def test_run_bridges_parsed_arguments_to_async_execution(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Synchronous entry execution parses argv and runs async command routing."""

    received: list[object] = []

    async def fake_run_parsed_arguments(
        parsed: object,
    ) -> str:
        received.append(parsed)
        return "EXPECTED REPORT"

    monkeypatch.setattr(
        entry,
        "_run_parsed_arguments",
        fake_run_parsed_arguments,
    )

    report = entry.run(
        [
            "streamable-http",
            "--name",
            "Demo Server",
            "--url",
            "http://localhost:8000/mcp",
        ]
    )

    assert report == "EXPECTED REPORT"

    assert len(received) == 1

    parsed = received[0]
    assert parsed.transport == "streamable-http"
    assert parsed.name == "Demo Server"
    assert parsed.url == "http://localhost:8000/mcp"
    
def test_main_writes_successful_report_to_stdout(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Successful terminal execution writes the rendered report to stdout."""

    received: list[object] = []

    def fake_run(argv: object) -> str:
        received.append(argv)
        return "EXPECTED REPORT"

    monkeypatch.setattr(
        entry,
        "run",
        fake_run,
    )

    argv = [
        "streamable-http",
        "--name",
        "Demo Server",
        "--url",
        "http://localhost:8000/mcp",
    ]

    entry.main(argv)

    captured = capsys.readouterr()

    assert received == [argv]
    assert captured.out == "EXPECTED REPORT\n"
    assert captured.err == ""
    
def test_python_module_entry_supports_help() -> None:
    """python -m mcp_details reaches the terminal argument parser."""

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "mcp_details",
            "--help",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    assert "usage:" in completed.stdout
    assert "stdio" in completed.stdout
    assert "streamable-http" in completed.stdout
    assert completed.stderr == ""

def test_main_propagates_runtime_failure_without_success_output(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Runtime failures propagate and do not produce a successful report."""

    def fake_run(argv: object) -> str:
        raise RuntimeError("EXPECTED FAILURE")

    monkeypatch.setattr(
        entry,
        "run",
        fake_run,
    )

    with pytest.raises(
        RuntimeError,
        match="EXPECTED FAILURE",
    ):
        entry.main(
            [
                "streamable-http",
                "--name",
                "Demo Server",
                "--url",
                "http://localhost:8000/mcp",
            ]
        )

    captured = capsys.readouterr()

    assert captured.out == ""
    assert captured.err == ""
    
def test_python_module_entry_reports_invalid_arguments_as_process_failure() -> None:
    """Invalid module invocation writes an error and exits unsuccessfully."""

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "mcp_details",
            "streamable-http",
            "--name",
            "Demo Server",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert completed.stdout == ""
    assert completed.stderr != ""