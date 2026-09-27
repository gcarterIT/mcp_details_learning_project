import asyncio

from app import inspect_server


def run() -> str:
    """Bridge synchronous execution into async application work."""

    report = asyncio.run(inspect_server())

    return report


def main() -> None:
    """Synchronous application entry."""

    print("Application starting")

    report = run()

    print(report)

    print("Application finished")


if __name__ == "__main__":
    main()