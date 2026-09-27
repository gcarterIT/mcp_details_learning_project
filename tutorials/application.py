from inspection import inspect_server


async def inspect_profile(server_name: str) -> dict[str, str]:
    """Application-level asynchronous composition."""

    result = await inspect_server(server_name)

    return result