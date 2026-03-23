import argparse
import asyncio
import os
from pathlib import Path

from fastmcp import Client
from fastmcp.client.transports import StdioTransport


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def build_transport_env(env_path: Path) -> dict[str, str]:
    env = os.environ.copy()
    for key, value in parse_env_file(env_path).items():
        if key not in env:
            env[key] = value
    env["MCP_TRANSPORT"] = "stdio"
    env.setdefault("FASTMCP_SHOW_SERVER_BANNER", "0")
    return env


async def run_smoke_test(env_path: Path, username: str | None) -> None:
    root = Path(__file__).resolve().parent
    launcher = root / "run_codex_stdio.sh"
    if not launcher.exists():
        raise RuntimeError("Missing run_codex_stdio.sh.")

    transport = StdioTransport(
        command=str(launcher),
        args=[],
        env=build_transport_env(env_path),
    )
    client = Client(transport)

    async with client:
        tools = await client.list_tools()
        print(f"Connected. Loaded {len(tools)} tools.")
        for tool in tools:
            print(f"- {tool.name}")

        if username:
            result = await client.call_tool(
                "getUsersByUsername",
                {"username": username},
            )
            print("\ngetUsersByUsername result:")
            print(result.data)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke test the X MCP server.")
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Environment file to load before launching the server.",
    )
    parser.add_argument(
        "--username",
        help="Optional X username to look up after listing tools.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    env_path = Path(args.env_file).resolve()
    asyncio.run(run_smoke_test(env_path, args.username))


if __name__ == "__main__":
    main()
