"""The MCP client CredPilot's host owns.

One class, :class:`CredPilotMCPClient`, which:

* launches the CredPilot MCP server as a subprocess over stdio and initializes a
  session against it;
* **discovers** what the server offers rather than assuming — tools, resources
  and prompts are listed and recorded, and a host that needs a capability the
  server did not advertise fails at connect time with a readable message rather
  than at call time with a protocol error;
* calls tools, reads resources and fetches prompts under a **deadline** with
  **bounded retries** (:mod:`src.resilience`);
* answers the server's **elicitation** and **sampling** requests, and declares
  its **roots**;
* checks **protocol compatibility** and records the negotiated version;
* opens a **Phoenix span** per call and writes the **tool log** entry.

Every failure mode is a value, not a traceback. A graph node calling this has to
produce a state update whatever happened, so :meth:`call_tool` returns an
:class:`MCPCallResult` whose ``ok`` says which it was. The node then degrades —
refer the file, say retrieval was unavailable — instead of dying with a
``ConnectionError`` inside a checkpoint.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, AsyncIterator, Mapping, Sequence

from src.observability.tool_logging import (
    TRANSPORT_MCP,
    log_mcp_exchange,
    log_tool_call,
)
from src.observability.tracing import (
    SPAN_KIND_TOOL,
    SPAN_MCP_CONNECT,
    SPAN_MCP_PROMPT,
    SPAN_MCP_RESOURCE,
    SPAN_MCP_TOOL,
    span,
)
from src.resilience import (
    DependencyUnavailable,
    NonRetryableError,
    RetryPolicy,
    ToolFailure,
    run_async,
    safe_call,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SERVER_SCRIPT = REPO_ROOT / "mcp_server" / "server.py"

#: Connecting launches a subprocess that loads two sentence-transformer models
#: before it answers, so the connect deadline is generous and the per-call one
#: is not. One attempt: a server that failed to start will fail to start again,
#: and a second 120-second wait for the same answer helps nobody.
CONNECT_POLICY = RetryPolicy(max_attempts=1, timeout_seconds=180.0)

#: Per-call policy. Retrieval over two indexes with a cross-encoder rerank is
#: seconds, not milliseconds, so 60 is a deadline rather than a target.
CALL_POLICY = RetryPolicy(max_attempts=3, timeout_seconds=60.0, backoff_seconds=0.5)

#: Reads are cheap and idempotent, so they get a tighter deadline.
READ_POLICY = RetryPolicy(max_attempts=3, timeout_seconds=20.0, backoff_seconds=0.25)

#: Directories this client declares as roots. The same allowlist the server
#: enforces — declared here so a reader can see the host is not asking for
#: anything wider than the server would grant.
CLIENT_ROOTS: tuple[str, ...] = (
    "synthetic_data/mortgage/policy_corpus",
    "synthetic_data/education/policy_corpus",
    "data/vectorstore",
    "config",
)

#: MCP protocol revisions this client has been tested against.
#:
#: A server negotiating something else is recorded and **allowed** — the
#: protocol is backwards compatible within a major line, and refusing an
#: unknown-but-newer revision would break a working connection over a version
#: string. The note goes in the capability record and the transcript, so a
#: compatibility problem is diagnosable rather than mysterious.
#:
#: ``2025-11-25`` is what the pinned SDK actually negotiates and what
#: ``tests/test_mcp_capabilities.py`` exercises; the earlier three are listed
#: because a client is not only ever pointed at its own server.
KNOWN_PROTOCOL_VERSIONS: tuple[str, ...] = (
    "2024-11-05", "2025-03-26", "2025-06-18", "2025-11-25",
)


class MCPUnavailable(RuntimeError):
    """The server could not be reached or did not offer what the host needs."""


@dataclass
class MCPCapabilities:
    """What the server said it offers, discovered at connect time."""

    tools: dict[str, str] = field(default_factory=dict)
    resources: dict[str, str] = field(default_factory=dict)
    prompts: dict[str, str] = field(default_factory=dict)
    protocol_version: str | None = None
    server_name: str | None = None
    server_version: str | None = None
    server_capabilities: dict[str, Any] = field(default_factory=dict)
    discovery_errors: list[str] = field(default_factory=list)

    @property
    def tool_names(self) -> list[str]:
        return sorted(self.tools)

    @property
    def resource_uris(self) -> list[str]:
        return sorted(self.resources)

    @property
    def prompt_names(self) -> list[str]:
        return sorted(self.prompts)

    @property
    def protocol_known(self) -> bool:
        return self.protocol_version in KNOWN_PROTOCOL_VERSIONS

    def require(self, *tools: str) -> None:
        """Fail now, with a list, rather than at the first missing call."""
        missing = [t for t in tools if t not in self.tools]
        if missing:
            raise MCPUnavailable(
                f"the MCP server does not offer {', '.join(sorted(missing))}. "
                f"It offers: {', '.join(self.tool_names) or '(nothing)'}"
            )

    def as_dict(self) -> dict[str, Any]:
        return {
            "server_name": self.server_name,
            "server_version": self.server_version,
            "protocol_version": self.protocol_version,
            "protocol_recognised": self.protocol_known,
            "tool_count": len(self.tools),
            "resource_count": len(self.resources),
            "prompt_count": len(self.prompts),
            "tools": self.tool_names,
            "resources": self.resource_uris,
            "prompts": self.prompt_names,
            "server_capabilities": self.server_capabilities,
            **({"discovery_errors": self.discovery_errors} if self.discovery_errors else {}),
        }


@dataclass
class MCPCallResult:
    """The outcome of one MCP call — success or failure, never an exception."""

    ok: bool
    operation: str
    payload: Any = None
    error_type: str | None = None
    message: str | None = None
    latency_ms: float = 0.0
    attempts: int = 1
    trace_id: str | None = None
    span_id: str | None = None

    def unwrap(self, default: Any = None) -> Any:
        """The payload on success, ``default`` otherwise."""
        return self.payload if self.ok else default

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "operation": self.operation,
            "latency_ms": round(self.latency_ms, 1),
            "attempts": self.attempts,
            **({"error_type": self.error_type} if self.error_type else {}),
            **({"message": self.message} if self.message else {}),
            **({"trace_id": self.trace_id} if self.trace_id else {}),
            **({"span_id": self.span_id} if self.span_id else {}),
        }


def server_parameters(python: str | None = None):
    """Stdio parameters for launching the CredPilot MCP server."""
    from mcp import StdioServerParameters

    # The child inherits the parent's environment so a committed `.env` and the
    # model cache are visible, minus anything that would make it print to the
    # protocol channel.
    env = dict(os.environ)
    env.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
    env.setdefault("TQDM_DISABLE", "1")
    env.setdefault("TRANSFORMERS_VERBOSITY", "error")

    return StdioServerParameters(
        command=python or sys.executable,
        args=[str(SERVER_SCRIPT)],
        cwd=str(REPO_ROOT),
        env=env,
    )


class CredPilotMCPClient:
    """One connected MCP session, with discovery, resilience and tracing.

    Use it as an async context manager::

        async with CredPilotMCPClient() as client:
            result = await client.call_tool("retrieve_policy", {...})

    or from synchronous code through :func:`open_client`.
    """

    def __init__(
        self,
        *,
        python: str | None = None,
        call_policy: RetryPolicy | None = None,
        connect_policy: RetryPolicy | None = None,
        roots: Sequence[str] = CLIENT_ROOTS,
        agent: str = "mcp_host",
    ):
        self.python = python
        self.call_policy = call_policy or CALL_POLICY
        self.connect_policy = connect_policy or CONNECT_POLICY
        self.roots = tuple(roots)
        self.agent = agent
        self.capabilities = MCPCapabilities()
        self.session: Any = None
        self._stack: contextlib.AsyncExitStack | None = None
        #: Elicitation requests the server made and how this client answered.
        #: Recorded because an elicitation is a question put to a person, and a
        #: client that answered one on its own must leave a trace of doing so.
        self.elicitations: list[dict[str, Any]] = []
        self.sampling_requests: list[dict[str, Any]] = []
        #: Supplied by the host to answer elicitations. When absent, this client
        #: declines rather than inventing an answer.
        self.elicitation_responder: Any = None

    # -- lifecycle ------------------------------------------------------------

    async def __aenter__(self) -> "CredPilotMCPClient":
        await self.connect()
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.close()

    async def connect(self) -> MCPCapabilities:
        """Launch the server, initialize the session, and discover the surface."""
        from mcp import ClientSession
        from mcp.client.stdio import stdio_client

        started = time.perf_counter()
        with span(
            SPAN_MCP_CONNECT, span_kind=SPAN_KIND_TOOL, agent=self.agent,
            transport="stdio", server_script=SERVER_SCRIPT.name,
        ) as sp:
            self._stack = contextlib.AsyncExitStack()
            try:
                read, write = await asyncio.wait_for(
                    self._stack.enter_async_context(stdio_client(server_parameters(self.python))),
                    timeout=self.connect_policy.timeout_seconds,
                )
                self.session = await self._stack.enter_async_context(
                    ClientSession(
                        read,
                        write,
                        sampling_callback=self._on_sampling,
                        elicitation_callback=self._on_elicitation,
                        list_roots_callback=self._on_list_roots,
                    )
                )
                init = await asyncio.wait_for(
                    self.session.initialize(),
                    timeout=self.connect_policy.timeout_seconds,
                )
            except asyncio.TimeoutError as exc:
                await self.close()
                raise DependencyUnavailable(
                    f"the CredPilot MCP server did not initialize within "
                    f"{self.connect_policy.timeout_seconds:g}s",
                    operation="mcp.connect", cause=exc,
                ) from exc
            except Exception as exc:  # noqa: BLE001 - reported as unavailability
                await self.close()
                raise DependencyUnavailable(
                    f"could not start or initialize the CredPilot MCP server: "
                    f"{type(exc).__name__}: {exc}",
                    operation="mcp.connect", cause=exc,
                ) from exc

            self.capabilities = await self._discover(init)
            sp.set(
                tool_count=len(self.capabilities.tools),
                resource_count=len(self.capabilities.resources),
                prompt_count=len(self.capabilities.prompts),
                protocol_version=self.capabilities.protocol_version or "",
                protocol_recognised=self.capabilities.protocol_known,
                latency_ms=round((time.perf_counter() - started) * 1000, 1),
            )

        log_mcp_exchange(
            direction="client",
            method="initialize",
            payload=self.capabilities.as_dict(),
        )
        return self.capabilities

    async def close(self) -> None:
        """Close the session and reap the subprocess. Never raises."""
        stack, self._stack = self._stack, None
        self.session = None
        if stack is None:
            return
        try:
            await stack.aclose()
        except Exception:  # noqa: BLE001 - a shutdown error must not mask a result
            pass

    # -- discovery ------------------------------------------------------------

    async def _discover(self, init: Any) -> MCPCapabilities:
        """List what the server offers. A partial surface is recorded, not fatal."""
        caps = MCPCapabilities()

        info = getattr(init, "serverInfo", None)
        caps.server_name = str(getattr(info, "name", "") or "") or None
        caps.server_version = str(getattr(info, "version", "") or "") or None
        caps.protocol_version = str(getattr(init, "protocolVersion", "") or "") or None
        server_caps = getattr(init, "capabilities", None)
        if server_caps is not None:
            try:
                caps.server_capabilities = json.loads(server_caps.model_dump_json())
            except Exception:  # noqa: BLE001
                caps.server_capabilities = {}

        try:
            listed = await asyncio.wait_for(self.session.list_tools(), timeout=30)
            caps.tools = {
                t.name: (getattr(t, "description", "") or "")[:300] for t in listed.tools
            }
        except Exception as exc:  # noqa: BLE001
            caps.discovery_errors.append(f"tools/list: {type(exc).__name__}: {exc}")

        try:
            listed = await asyncio.wait_for(self.session.list_resources(), timeout=30)
            caps.resources = {
                str(r.uri): (getattr(r, "description", "") or "")[:300]
                for r in listed.resources
            }
        except Exception as exc:  # noqa: BLE001
            caps.discovery_errors.append(f"resources/list: {type(exc).__name__}: {exc}")

        try:
            listed = await asyncio.wait_for(self.session.list_prompts(), timeout=30)
            caps.prompts = {
                p.name: (getattr(p, "description", "") or "")[:300] for p in listed.prompts
            }
        except Exception as exc:  # noqa: BLE001
            caps.discovery_errors.append(f"prompts/list: {type(exc).__name__}: {exc}")

        return caps

    # -- calls ----------------------------------------------------------------

    async def call_tool(
        self,
        name: str,
        arguments: Mapping[str, Any] | None = None,
        *,
        policy: RetryPolicy | None = None,
    ) -> MCPCallResult:
        """Call one MCP tool under a deadline, with bounded retries.

        A tool the server never advertised is a :class:`NonRetryableError`
        immediately: three round trips to be told "unknown tool" three times is
        not resilience, it is latency.
        """
        arguments = dict(arguments or {})
        operation = f"mcp.tool:{name}"
        started = time.perf_counter()

        if self.session is None:
            return self._failed(operation, "NotConnected",
                                "no MCP session; call connect() first", started)
        if self.capabilities.tools and name not in self.capabilities.tools:
            return self._failed(
                operation, "UnknownTool",
                f"the server did not advertise {name!r}; it offers "
                f"{', '.join(self.capabilities.tool_names)}",
                started,
            )

        with span(
            SPAN_MCP_TOOL, span_kind=SPAN_KIND_TOOL, tool=name, agent=self.agent,
            argument_keys=sorted(arguments),
        ) as sp:
            trace_id, span_id = sp.ids

            async def once() -> Any:
                raw = await self.session.call_tool(name, arguments)
                return self._decode(name, raw)

            outcome = await safe_call(operation, once, policy=policy or self.call_policy)
            latency = (time.perf_counter() - started) * 1000

            if isinstance(outcome, ToolFailure):
                sp.set(status="ERROR", error_type=outcome.error_type,
                       attempts=outcome.attempts, latency_ms=round(latency, 1))
                log_tool_call(
                    tool_name=name, agent=self.agent, args=arguments,
                    result=None, latency_ms=latency, status="ERROR",
                    transport=TRANSPORT_MCP,
                    error=f"{outcome.error_type}: {outcome.message}",
                )
                return MCPCallResult(
                    ok=False, operation=operation, error_type=outcome.error_type,
                    message=outcome.message, latency_ms=latency,
                    attempts=outcome.attempts, trace_id=trace_id, span_id=span_id,
                )

            sp.set(status="OK", latency_ms=round(latency, 1))
            log_tool_call(
                tool_name=name, agent=self.agent, args=arguments,
                result=outcome, latency_ms=latency, status="OK",
                transport=TRANSPORT_MCP,
            )
            return MCPCallResult(
                ok=True, operation=operation, payload=outcome, latency_ms=latency,
                trace_id=trace_id, span_id=span_id,
            )

    async def read_resource(self, uri: str) -> MCPCallResult:
        """Read one MCP resource, decoding JSON where the server sent it."""
        operation = f"mcp.resource:{uri}"
        started = time.perf_counter()

        if self.session is None:
            return self._failed(operation, "NotConnected", "no MCP session", started)
        if self.capabilities.resources and uri not in self.capabilities.resources:
            return self._failed(
                operation, "UnknownResource",
                f"the server did not advertise {uri!r}", started,
            )

        with span(SPAN_MCP_RESOURCE, span_kind=SPAN_KIND_TOOL, uri=uri,
                  agent=self.agent) as sp:
            trace_id, span_id = sp.ids

            async def once() -> Any:
                from pydantic import AnyUrl

                raw = await self.session.read_resource(AnyUrl(uri))
                return self._decode_resource(uri, raw)

            outcome = await safe_call(operation, once, policy=READ_POLICY)
            latency = (time.perf_counter() - started) * 1000

            if isinstance(outcome, ToolFailure):
                sp.set(status="ERROR", error_type=outcome.error_type)
                return MCPCallResult(
                    ok=False, operation=operation, error_type=outcome.error_type,
                    message=outcome.message, latency_ms=latency,
                    attempts=outcome.attempts, trace_id=trace_id, span_id=span_id,
                )
            sp.set(status="OK", latency_ms=round(latency, 1))
            return MCPCallResult(ok=True, operation=operation, payload=outcome,
                                 latency_ms=latency, trace_id=trace_id, span_id=span_id)

    async def get_prompt(
        self, name: str, arguments: Mapping[str, Any] | None = None
    ) -> MCPCallResult:
        """Fetch one MCP prompt template, rendered with its arguments."""
        operation = f"mcp.prompt:{name}"
        started = time.perf_counter()

        if self.session is None:
            return self._failed(operation, "NotConnected", "no MCP session", started)
        if self.capabilities.prompts and name not in self.capabilities.prompts:
            return self._failed(
                operation, "UnknownPrompt",
                f"the server did not advertise a prompt named {name!r}; it offers "
                f"{', '.join(self.capabilities.prompt_names)}",
                started,
            )

        with span(SPAN_MCP_PROMPT, span_kind=SPAN_KIND_TOOL, prompt=name,
                  agent=self.agent) as sp:
            trace_id, span_id = sp.ids

            async def once() -> Any:
                result = await self.session.get_prompt(name, dict(arguments or {}))
                return {
                    "description": getattr(result, "description", None),
                    "messages": [
                        {
                            "role": str(getattr(m, "role", "user")),
                            "text": str(getattr(getattr(m, "content", None), "text", "") or ""),
                        }
                        for m in (getattr(result, "messages", None) or [])
                    ],
                }

            outcome = await safe_call(operation, once, policy=READ_POLICY)
            latency = (time.perf_counter() - started) * 1000

            if isinstance(outcome, ToolFailure):
                sp.set(status="ERROR", error_type=outcome.error_type)
                return MCPCallResult(
                    ok=False, operation=operation, error_type=outcome.error_type,
                    message=outcome.message, latency_ms=latency,
                    attempts=outcome.attempts, trace_id=trace_id, span_id=span_id,
                )
            sp.set(status="OK", message_count=len(outcome.get("messages", [])))
            return MCPCallResult(ok=True, operation=operation, payload=outcome,
                                 latency_ms=latency, trace_id=trace_id, span_id=span_id)

    # -- decoding -------------------------------------------------------------

    def _decode(self, name: str, raw: Any) -> Any:
        """Turn a ``CallToolResult`` into a plain Python value.

        A server error comes back as ``isError`` with the message in the content,
        not as an exception, so it is raised here — as a
        :class:`NonRetryableError`, because a tool that rejected its arguments
        will reject them again.
        """
        if getattr(raw, "isError", False):
            raise NonRetryableError(
                f"{name} refused: {_text_of(raw)[:400]}", operation=f"mcp.tool:{name}"
            )

        structured = getattr(raw, "structuredContent", None)
        if isinstance(structured, dict):
            # FastMCP wraps a non-dict return in {"result": ...}.
            return structured.get("result", structured)

        text = _text_of(raw)
        if not text:
            raise NonRetryableError(
                f"{name} returned no content", operation=f"mcp.tool:{name}"
            )
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text

    def _decode_resource(self, uri: str, raw: Any) -> Any:
        contents = getattr(raw, "contents", None) or []
        if not contents:
            raise NonRetryableError(f"{uri} returned no content",
                                    operation=f"mcp.resource:{uri}")
        text = str(getattr(contents[0], "text", "") or "")
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text

    def _failed(self, operation: str, error_type: str, message: str,
                started: float) -> MCPCallResult:
        return MCPCallResult(
            ok=False, operation=operation, error_type=error_type, message=message,
            latency_ms=(time.perf_counter() - started) * 1000,
        )

    # -- server-initiated requests --------------------------------------------

    async def _on_elicitation(self, context: Any, params: Any) -> Any:
        """Answer an elicitation request from the server.

        The host supplies an ``elicitation_responder`` when it has a person or a
        stored fact that can answer. With none, this **declines** — a client that
        invented an answer to "which lending product is this?" would be doing
        exactly what elicitation exists to avoid.
        """
        from mcp.types import ElicitResult

        message = str(getattr(params, "message", "") or "")
        schema = getattr(params, "requestedSchema", None)
        record = {
            "message": message[:400],
            "requested_fields": sorted((schema or {}).get("properties", {}))
            if isinstance(schema, dict) else [],
        }

        responder = self.elicitation_responder
        if responder is None:
            record["action"] = "decline"
            record["reason"] = "the host supplied no responder; nothing is assumed"
            self.elicitations.append(record)
            log_mcp_exchange(direction="client", method="elicitation/create", payload=record)
            return ElicitResult(action="decline")

        try:
            answer = responder(message, schema)
            if asyncio.iscoroutine(answer):
                answer = await answer
        except Exception as exc:  # noqa: BLE001
            record["action"] = "decline"
            record["reason"] = f"the responder failed: {type(exc).__name__}"
            self.elicitations.append(record)
            log_mcp_exchange(direction="client", method="elicitation/create", payload=record)
            return ElicitResult(action="decline")

        if not answer:
            record["action"] = "decline"
            record["reason"] = "the responder had no answer"
            self.elicitations.append(record)
            log_mcp_exchange(direction="client", method="elicitation/create", payload=record)
            return ElicitResult(action="decline")

        record["action"] = "accept"
        record["answered_fields"] = sorted(answer)
        self.elicitations.append(record)
        log_mcp_exchange(direction="client", method="elicitation/create", payload=record)
        return ElicitResult(action="accept", content=dict(answer))

    async def _on_sampling(self, context: Any, params: Any) -> Any:
        """Serve a sampling request — through Gemini, or not at all.

        This is the compatibility path. CredPilot answers with the provider it is
        required to use and names it in the response, so a server can see which
        model actually replied and refuse it if it must. With no key, the request
        is declined rather than answered by something else.
        """
        from mcp.types import CreateMessageResult, ErrorData, TextContent
        from mcp.shared.exceptions import McpError

        from src import llm

        prompt_parts: list[str] = []
        for message in getattr(params, "messages", None) or []:
            content = getattr(message, "content", None)
            text = str(getattr(content, "text", "") or "")
            if text:
                prompt_parts.append(text)
        prompt = "\n\n".join(prompt_parts)
        system = str(getattr(params, "systemPrompt", "") or "")
        record = {"prompt_chars": len(prompt), "has_system_prompt": bool(system)}

        status = llm.probe()
        if not status.available:
            record["served"] = False
            record["reason"] = f"Gemini unavailable: {status.reason[:160]}"
            self.sampling_requests.append(record)
            log_mcp_exchange(direction="client", method="sampling/createMessage",
                             payload=record)
            raise McpError(
                ErrorData(
                    code=-32603,
                    message=(
                        "CredPilot's host serves sampling through Google Gemini only, "
                        f"and it is unreachable ({status.reason[:120]}). The request "
                        f"is declined rather than served by another provider."
                    ),
                )
            )

        try:
            model = llm.chat_model(status.model, temperature=0.0)
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    model.invoke, f"{system}\n\n{prompt}".strip() if system else prompt
                ),
                timeout=60,
            )
            text = llm.message_text(response)
        except Exception as exc:  # noqa: BLE001
            record["served"] = False
            record["reason"] = f"{type(exc).__name__}: {str(exc)[:160]}"
            self.sampling_requests.append(record)
            log_mcp_exchange(direction="client", method="sampling/createMessage",
                             payload=record)
            raise McpError(
                ErrorData(code=-32603, message=f"sampling failed: {type(exc).__name__}")
            ) from exc

        record["served"] = True
        record["model"] = status.model
        record["response_chars"] = len(text)
        self.sampling_requests.append(record)
        log_mcp_exchange(direction="client", method="sampling/createMessage", payload=record)

        return CreateMessageResult(
            role="assistant",
            content=TextContent(type="text", text=text),
            model=status.model or "gemini",
            stopReason="endTurn",
        )

    async def _on_list_roots(self, context: Any) -> Any:
        """Declare this host's roots: a fixed allowlist of committed directories."""
        from mcp.types import ListRootsResult, Root
        from pydantic import FileUrl

        roots = []
        for relative in self.roots:
            path = REPO_ROOT / relative
            if not path.exists():
                continue
            roots.append(Root(uri=FileUrl(path.resolve().as_uri()), name=relative))
        log_mcp_exchange(
            direction="client", method="roots/list",
            payload={"declared": [r.name for r in roots]},
        )
        return ListRootsResult(roots=roots)


def _text_of(raw: Any) -> str:
    """Concatenate the text blocks of a tool or resource result."""
    parts: list[str] = []
    for block in getattr(raw, "content", None) or []:
        text = getattr(block, "text", None)
        if text:
            parts.append(str(text))
    return "\n".join(parts)


@contextlib.asynccontextmanager
async def open_client(**kwargs: Any) -> AsyncIterator[CredPilotMCPClient]:
    """Open a connected client as an async context manager."""
    client = CredPilotMCPClient(**kwargs)
    try:
        await client.connect()
        yield client
    finally:
        await client.close()


def mcp_available(timeout: float = 180.0) -> dict[str, Any]:
    """Probe the server from synchronous code. Never raises.

    Returns the discovered surface, or ``{"available": False, "reason": ...}``.
    Used by the web app's health endpoint and by the CLI's ``mcp`` command.
    """

    async def probe() -> dict[str, Any]:
        try:
            async with open_client() as client:
                return {"available": True, **client.capabilities.as_dict()}
        except Exception as exc:  # noqa: BLE001 - a probe reports, never raises
            return {"available": False, "reason": f"{type(exc).__name__}: {str(exc)[:300]}"}

    try:
        return run_async(probe(), timeout=timeout)
    except Exception as exc:  # noqa: BLE001
        return {"available": False, "reason": f"{type(exc).__name__}: {str(exc)[:300]}"}


def call_tool_sync(
    name: str, arguments: Mapping[str, Any] | None = None, *, timeout: float = 240.0
) -> MCPCallResult:
    """One-shot: connect, call one tool, disconnect. For the CLI and tests.

    Paying the server's start-up cost per call is wrong for a graph node, which
    holds a session open instead — see :mod:`src.mcp_host.pool`.
    """

    async def once() -> MCPCallResult:
        async with open_client() as client:
            return await client.call_tool(name, arguments)

    try:
        return run_async(once(), timeout=timeout)
    except Exception as exc:  # noqa: BLE001
        return MCPCallResult(
            ok=False, operation=f"mcp.tool:{name}",
            error_type=type(exc).__name__, message=str(exc)[:300],
        )


__all__ = [
    "CALL_POLICY",
    "CLIENT_ROOTS",
    "CONNECT_POLICY",
    "CredPilotMCPClient",
    "KNOWN_PROTOCOL_VERSIONS",
    "MCPCallResult",
    "MCPCapabilities",
    "MCPUnavailable",
    "READ_POLICY",
    "SERVER_SCRIPT",
    "call_tool_sync",
    "mcp_available",
    "open_client",
    "server_parameters",
]
