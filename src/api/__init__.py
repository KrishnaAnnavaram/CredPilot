"""CredPilot's HTTP API.

The router and everything behind it. :mod:`src.web` mounts this alongside the
static page; a caller that wants the API without a browser UI mounts it alone.
"""

from src.api.routes import (
    AssessRequest,
    ChatRequest,
    ResumeRequest,
    get_graph,
    router,
)

__all__ = [
    "AssessRequest",
    "ChatRequest",
    "ResumeRequest",
    "get_graph",
    "router",
]
