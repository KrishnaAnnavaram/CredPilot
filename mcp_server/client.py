"""Consuming CredPilot's MCP server through ``langchain-mcp-adapters``.

The agent side does not import ``mcp_server.server`` — it launches the server as
a subprocess over stdio and loads its tools and resources through the adapters,
which is the integration the stack requires and the only one that proves the
server actually works as a server.
"""

from __future__ import annotations

import contextlib
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, AsyncIterator

REPO_ROOT = Path(__file__).resolve().parents[1]
SERVER_SCRIPT = REPO_ROOT / "mcp_server" / "server.py"


def server_parameters(python: str | None = None):
    """Stdio parameters for launching the CredPilot MCP server."""
    from mcp import StdioServerParameters

    return StdioServerParameters(
        command=python or sys.executable,
        args=[str(SERVER_SCRIPT)],
        cwd=str(REPO_ROOT),
        env=None,
    )


@dataclass
class MCPSurface:
    """What the server exposed, once loaded through the adapters."""

    tools: list[Any] = field(default_factory=list)
    resources: list[Any] = field(default_factory=list)

    @property
    def tool_names(self) -> list[str]:
        return [t.name for t in self.tools]

    @property
    def resource_uris(self) -> list[str]:
        out = []
        for r in self.resources:
            uri = getattr(r, "metadata", {}).get("uri") if hasattr(r, "metadata") else None
            out.append(str(uri) if uri else str(getattr(r, "uri", r)))
        return out


@contextlib.asynccontextmanager
async def open_session(python: str | None = None) -> AsyncIterator[Any]:
    """Open an initialized MCP client session against the CredPilot server."""
    from mcp import ClientSession
    from mcp.client.stdio import stdio_client

    async with stdio_client(server_parameters(python)) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


async def load_surface(session: Any) -> MCPSurface:
    """Load the server's tools and resources as LangChain objects."""
    from langchain_mcp_adapters.resources import load_mcp_resources
    from langchain_mcp_adapters.tools import load_mcp_tools

    tools = await load_mcp_tools(session)
    try:
        resources = await load_mcp_resources(session)
    except Exception:  # noqa: BLE001 - resources are optional to the tool path
        resources = []
    return MCPSurface(tools=list(tools), resources=list(resources))


async def load_mcp_policy_tools(python: str | None = None) -> tuple[Any, MCPSurface]:
    """Open a session and load the surface, returning both.

    The caller owns the session's lifetime; use :func:`open_session` directly when
    a context manager is more convenient.
    """
    ctx = open_session(python)
    session = await ctx.__aenter__()
    surface = await load_surface(session)
    return ctx, surface
