"""CredPilot as an MCP **host**.

The MCP specification separates three roles, and CredPilot occupies the first:

``host``
    The application. It owns the Supervisor, the two specialist agents, the
    Final Response Agent, the Gemini integration, memory, checkpointing, the UI
    and the observability stack. It decides what to ask for and what to do with
    the answer.
``client``
    The protocol-speaking component the host owns, one per server. It connects,
    discovers what the server offers, calls tools, reads resources, fetches
    prompts, answers elicitation and sampling requests and declares roots. It is
    :mod:`src.mcp_host.client`.
``server``
    ``mcp_server/``, a separate process reached over stdio. It exposes
    capabilities; it does not know who is calling or why.

Keeping the client inside ``src/`` rather than beside the server is the point.
The server must be independently runnable by anything that speaks MCP, and code
that imports the server module to "call a tool" has proved nothing about the
server working as a server.
"""

from src.mcp_host.client import (
    CredPilotMCPClient,
    MCPCapabilities,
    MCPCallResult,
    mcp_available,
    open_client,
)

__all__ = [
    "CredPilotMCPClient",
    "MCPCallResult",
    "MCPCapabilities",
    "mcp_available",
    "open_client",
]
