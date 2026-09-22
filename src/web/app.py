"""The CredPilot FastAPI application.

One graph, reached over HTTP. Every endpoint here builds the same state the CLI
builds and invokes the same compiled graph, so the web path and the scored path
cannot drift: there is no second router, no second rule engine and no second
prompt.

Endpoints
---------
``POST /api/chat``
    One conversational turn. Streams progress over Server-Sent Events so a
    fifteen-second assessment shows what it is doing rather than spinning.
``POST /api/chat/resume``
    Answer a clarification and resume the suspended thread.
``POST /api/assess``
    Submit an application for assessment, by committed id or by uploaded packet.
``GET  /api/applications``
    The committed sample applications, so the page has something to submit.
``GET  /api/thread/{thread_id}``
    The evidence view for one run: route, agents, tool calls, citations, timing.
``GET  /api/health``
    Whether the indexes, the model and the MCP server are reachable.

What the API never returns: chain of thought, secrets, or unmasked applicant
identifiers. The graph's own output guardrail redacts before anything reaches a
response, and :func:`_public` drops the internal state the page has no business
seeing — the raw packet above all, which carries the applicant's address and
masked identifiers and is not needed to render an answer.
"""

from __future__ import annotations

import asyncio
import json
import queue
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Mapping

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from src.config import REPO_ROOT

STATIC_DIR = Path(__file__).resolve().parent / "static"

#: One compiled graph for the process, built lazily on the first request.
#: Building it loads two sentence-transformer models, which is several seconds
#: nobody should pay at import time — including the test collector.
_GRAPH: Any = None
_GRAPH_CONTEXT: Any = None
_GRAPH_LOCK = threading.Lock()

#: Runs the page can ask about afterwards. Bounded: this is a demonstration
#: surface, not a datastore, and the checkpointer already holds the durable
#: record of every thread.
_RUNS: dict[str, dict[str, Any]] = {}
_MAX_RUNS = 200


def get_graph():
    """The compiled graph, built once per process."""
    global _GRAPH, _GRAPH_CONTEXT
    with _GRAPH_LOCK:
        if _GRAPH is None:
            from src.graph import build_graph

            _GRAPH, _GRAPH_CONTEXT = build_graph()
        return _GRAPH


# ======================================================================================
# Request and response shapes
# ======================================================================================


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    thread_id: str | None = None
    #: Pin the product when the caller already knows it. Omit it and the
    #: Supervisor works it out or asks.
    loan_domain: str | None = None


class ResumeRequest(BaseModel):
    thread_id: str
    answer: str = Field(min_length=1, max_length=2000)


class AssessRequest(BaseModel):
    application_id: str | None = None
    packet: dict[str, Any] | None = None
    as_of_date: str | None = None
    thread_id: str | None = None


def create_app() -> FastAPI:
    app = FastAPI(
        title="CredPilot",
        description=(
            "Loan origination and underwriting copilot. Mortgage and private "
            "education lending, kept strictly separate."
        ),
        version="1.0.0",
    )

    # -- pages -----------------------------------------------------------------

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    # -- health ----------------------------------------------------------------

    @app.get("/api/health")
    def health() -> dict[str, Any]:
        """What is reachable. Nothing here blocks on the MCP subprocess."""
        from src import llm
        from src.rag.indexer import load_manifest

        indexes: dict[str, Any]
        try:
            manifest = load_manifest()
            indexes = {
                "built": True,
                "embedding_model": manifest.get("embedding_model"),
                "products": sorted((manifest.get("products") or {}).keys()),
            }
        except Exception as exc:  # noqa: BLE001 - a health check reports, never raises
            indexes = {"built": False, "reason": f"{type(exc).__name__}: {exc}"}

        status = llm.probe()
        return {
            "ok": bool(indexes.get("built")),
            "indexes": indexes,
            "model": {
                "provider": "google-gemini",
                "available": status.available,
                "model": status.model,
                "reason": status.reason if not status.available else None,
                "role": "narrative rationale only; no retrieval, arithmetic, "
                        "threshold or verdict comes from a model",
            },
            "mcp": {
                "note": "probe with GET /api/mcp; it launches the server subprocess "
                        "and takes a few seconds",
            },
            "generated_at_utc": _now(),
        }

    @app.get("/api/mcp")
    async def mcp_status() -> dict[str, Any]:
        """Connect to the MCP server and report the surface it advertises."""
        from src.mcp_host import open_client

        try:
            async with open_client() as client:
                return {"available": True, **client.capabilities.as_dict()}
        except Exception as exc:  # noqa: BLE001
            return {"available": False, "reason": f"{type(exc).__name__}: {str(exc)[:300]}"}

    # -- sample applications ---------------------------------------------------

    @app.get("/api/applications")
    def applications(limit: int = 24) -> dict[str, Any]:
        """Committed sample applications, so the page has something to submit."""
        return {"products": _sample_applications(limit)}

    # -- chat ------------------------------------------------------------------

    @app.post("/api/chat")
    async def chat(request: ChatRequest) -> StreamingResponse:
        from src.graph import conversation_state

        thread_id = request.thread_id or f"web-{uuid.uuid4().hex[:12]}"
        state = conversation_state(
            request.message,
            session_id=thread_id,
            loan_domain=request.loan_domain,
        )
        return _stream(state, thread_id, kind="chat")

    @app.post("/api/chat/resume")
    async def resume(request: ResumeRequest) -> StreamingResponse:
        from langgraph.types import Command

        return _stream(Command(resume=request.answer), request.thread_id, kind="resume")

    # -- assessment ------------------------------------------------------------

    @app.post("/api/assess")
    async def assess(request: AssessRequest) -> StreamingResponse:
        from src.application_context import strip_embedded_outcomes
        from src.graph import initial_state

        thread_id = request.thread_id or f"web-{uuid.uuid4().hex[:12]}"

        if request.application_id:
            path = _application_path(request.application_id)
            if path is None:
                raise HTTPException(
                    404,
                    f"no committed application {request.application_id!r}. "
                    f"GET /api/applications lists what is available.",
                )
            state = initial_state(
                path, as_of_date=request.as_of_date, session_id=thread_id
            )
        elif request.packet:
            packet = strip_embedded_outcomes(request.packet)
            state = _state_from_packet(packet, request.as_of_date, thread_id)
        else:
            raise HTTPException(400, "pass application_id or packet")

        return _stream(state, thread_id, kind="assess")

    # -- evidence view ---------------------------------------------------------

    @app.get("/api/thread/{thread_id}")
    def thread(thread_id: str) -> dict[str, Any]:
        """The debug/evidence view for one run.

        Route, agents executed, tool calls, citations and timing — the things a
        reviewer needs to check the answer against. Never chain of thought: the
        model writes prose after the decision exists, and there is no reasoning
        trace to show because none of the reasoning was the model's.
        """
        run = _RUNS.get(thread_id)
        if run is None:
            raise HTTPException(404, f"no run on thread {thread_id!r} in this process")
        return run

    return app


# ======================================================================================
# Streaming
# ======================================================================================

#: What each node is doing, in words a person reading a progress line can use.
_NODE_LABELS = {
    "intake": "Receiving the request",
    "input_guardrails": "Screening the input",
    "supervisor": "Understanding and routing",
    "general_response": "Answering",
    "clarification": "Asking for clarification",
    "safe_response": "Answering within scope",
    "mortgage_agent": "Mortgage specialist picking it up",
    "education_agent": "Education specialist picking it up",
    "mortgage_policy_retrieval": "Retrieving mortgage policy",
    "education_policy_retrieval": "Retrieving education-loan policy",
    "mortgage_eligibility": "Computing affordability and applying the rules",
    "education_eligibility": "Computing capacity and applying the rules",
    "mortgage_risk": "Screening risk",
    "education_risk": "Screening risk",
    "mortgage_recommendation": "Forming the recommendation",
    "education_recommendation": "Forming the recommendation",
    "narrative": "Writing the rationale",
    "human_review": "Routing to a human reviewer",
    "final_response": "Assembling the answer",
    "output_guardrails": "Checking what leaves",
}


def _stream(payload: Any, thread_id: str, *, kind: str) -> StreamingResponse:
    """Invoke the graph on a worker thread and stream node progress as SSE.

    LangGraph's ``stream`` is synchronous and the retrieval stack underneath it
    is CPU-bound local work, so it runs on a thread rather than blocking the
    event loop. Events cross back on a queue.
    """
    events: queue.Queue = queue.Queue()

    def run() -> None:
        started = datetime.now(timezone.utc)
        final: dict[str, Any] = {}
        try:
            graph = get_graph()
            config = {"configurable": {"thread_id": thread_id}}
            for update in graph.stream(payload, config=config, stream_mode="updates"):
                for node, delta in (update or {}).items():
                    if node == "__interrupt__":
                        continue
                    events.put({
                        "event": "node",
                        "node": node,
                        "label": _NODE_LABELS.get(node, node),
                        "at": _now(),
                    })
                    if isinstance(delta, Mapping):
                        final.update(
                            {k: v for k, v in delta.items() if k in _CARRIED_KEYS}
                        )
            snapshot = graph.get_state(config)
            state = dict(snapshot.values or {})
            interrupt = _interrupt_of(snapshot)
            record = _public(state, thread_id, started, kind, interrupt)
            _remember(thread_id, record)
            events.put({"event": "result", **record})
        except Exception as exc:  # noqa: BLE001 - the client gets an error event
            events.put({
                "event": "error",
                "error_type": type(exc).__name__,
                "message": str(exc)[:400],
                "thread_id": thread_id,
            })
        finally:
            events.put(None)

    threading.Thread(target=run, daemon=True).start()

    async def generator() -> Any:
        loop = asyncio.get_running_loop()
        while True:
            item = await loop.run_in_executor(None, events.get)
            if item is None:
                break
            yield f"data: {json.dumps(item, default=str)}\n\n"

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


#: State keys worth carrying out of the stream. Everything else is either
#: internal or already on the final snapshot.
_CARRIED_KEYS = frozenset({
    "supervisor", "loan_domain", "route", "final_response", "answer",
    "requires_human_review", "clarification_question",
})


def _interrupt_of(snapshot: Any) -> dict[str, Any] | None:
    """The clarification a suspended thread is waiting on, if any."""
    for task in getattr(snapshot, "tasks", None) or []:
        for item in getattr(task, "interrupts", None) or []:
            value = getattr(item, "value", None)
            if isinstance(value, Mapping) and value.get("kind") == "clarification":
                return dict(value)
    return None


def _public(
    state: Mapping[str, Any],
    thread_id: str,
    started: datetime,
    kind: str,
    interrupt: dict[str, Any] | None,
) -> dict[str, Any]:
    """The part of the state a client may see.

    An allowlist, not a denylist. ``application_packet`` alone carries the
    applicant's address, employer and masked identifiers, none of which the page
    needs to render an answer — and a denylist would ship it the first time
    somebody added a key and forgot.
    """
    response = dict(state.get("final_response") or {})
    supervisor = dict(state.get("supervisor") or {})
    elapsed = (datetime.now(timezone.utc) - started).total_seconds()

    return {
        "thread_id": thread_id,
        "kind": kind,
        "awaiting_clarification": interrupt is not None,
        "clarification": interrupt,
        "answer": state.get("answer") or response.get("text") or "",
        "route": supervisor.get("route"),
        "routing_reason": supervisor.get("routing_reason"),
        "intent": supervisor.get("intent"),
        "confidence": supervisor.get("confidence"),
        "decided_by": supervisor.get("decided_by"),
        "loan_domain": state.get("loan_domain"),
        "application_id": state.get("application_id") or None,
        "as_of_date": state.get("as_of_date"),
        "outcome": response.get("outcome"),
        "eligibility": response.get("eligibility"),
        "risk_level": response.get("risk_level"),
        "requires_human_review": bool(state.get("requires_human_review")),
        "human_review_reasons": list(state.get("human_review_reasons") or []),
        "citations": list(response.get("citations") or []),
        "figures": response.get("figures") or {},
        "breaches": response.get("breaches") or [],
        "missing_evidence": response.get("missing_evidence") or [],
        "validation": response.get("validation") or {},
        "security_findings": sorted(set(state.get("security_findings") or [])),
        "output_guardrail": state.get("output_guardrail") or {},
        "evidence_count": response.get("evidence_count", 0),
        "retrieval_invoked": bool(response.get("retrieval_invoked")),
        "degradations": response.get("degradations") or [],
        # -- the debug/evidence view ------------------------------------------
        "agents_executed": list(state.get("steps") or []),
        "retrieval_statuses": list(state.get("retrieval_statuses") or []),
        "policy_questions": [
            q.get("topic") for q in (state.get("policy_questions") or [])
        ],
        "required_rules_fetched": list(state.get("required_rules_fetched") or []),
        "policy_dependencies": list(state.get("policy_dependencies") or []),
        "steps_taken": int(state.get("steps_taken") or 0),
        "step_budget": int(state.get("step_budget") or 0),
        "halted": bool(state.get("halted")),
        "elapsed_seconds": round(elapsed, 2),
        "narrative_model": (state.get("narrative") or {}).get("model"),
        "narrative_faithful": (state.get("narrative") or {}).get("is_faithful"),
        "generated_at_utc": _now(),
    }


def _remember(thread_id: str, record: Mapping[str, Any]) -> None:
    _RUNS[thread_id] = dict(record)
    while len(_RUNS) > _MAX_RUNS:
        _RUNS.pop(next(iter(_RUNS)))


# ======================================================================================
# Helpers
# ======================================================================================


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _application_path(application_id: str) -> Path | None:
    from src.domain import domain_from_application_id

    domain = domain_from_application_id(application_id)
    if domain is None:
        return None
    path = (
        REPO_ROOT / "synthetic_data" / domain.corpus_key / "applications"
        / f"{application_id}.json"
    )
    return path if path.exists() else None


def _state_from_packet(
    packet: Mapping[str, Any], as_of_date: str | None, thread_id: str
) -> dict[str, Any]:
    """Initial state for an uploaded packet.

    Delegates to the graph so an uploaded packet starts from exactly the state a
    committed one does. The two used to be separate copies of the same dict,
    which is how an uploaded packet with no as-of date reached the rule engine
    by a path the CLI could not take (F-20).
    """
    from src.graph import packet_state

    return dict(packet_state(packet, as_of_date=as_of_date, session_id=thread_id))


#: Applications worth putting at the top of the list.
#:
#: Ordering by filename put APP-000001 to APP-000012 in front of everything,
#: which is the least interesting dozen in the corpus — twelve conventional
#: conforming purchases that all approve. These are the cases that show the
#: system doing something: the boundary triple (one ratio, three outcomes,
#: decided by which policy version governed), an adversarial packet, and one
#: education file per product family.
FEATURED_APPLICATIONS: dict[str, tuple[str, ...]] = {
    "mortgage": ("APP-000055", "APP-000056", "APP-000057", "APP-000065"),
    "education": ("APP-2026-00001", "APP-2026-00002", "APP-2026-00009",
                  "APP-2026-00016", "APP-2026-00017"),
}


def _sample_applications(limit: int) -> dict[str, list[dict[str, Any]]]:
    """A short list of committed applications per product, for the page."""
    from src.domain import load_application

    out: dict[str, list[dict[str, Any]]] = {}
    for product in ("mortgage", "education"):
        root = REPO_ROOT / "synthetic_data" / product / "applications"
        if not root.exists():
            out[product] = []
            continue

        featured = [
            root / f"{application_id}.json"
            for application_id in FEATURED_APPLICATIONS.get(product, ())
            if (root / f"{application_id}.json").exists()
        ]
        rest = [p for p in sorted(root.glob("*.json")) if p not in featured]
        rows: list[dict[str, Any]] = []
        for path in (featured + rest)[:limit]:
            try:
                packet = load_application(path)
            except Exception:  # noqa: BLE001 - a malformed sample is skipped
                continue
            rows.append({
                "application_id": packet.get("application_id"),
                "product": product,
                "as_of_date": (
                    packet.get("underwriting_as_of_date")
                    or packet.get("application_date")
                    or str(packet.get("submitted_at", ""))[:10]
                ),
                "summary": _summarize(product, packet),
            })
        out[product] = rows
    return out


def _summarize(product: str, packet: Mapping[str, Any]) -> str:
    """A one-line description, with no applicant identifier in it."""
    if product == "mortgage":
        loan = packet.get("requested_loan") or {}
        amount = loan.get("base_loan_amount")
        return (
            f"{str(packet.get('product_family', '')).replace('_', ' ')} "
            f"{str(packet.get('loan_purpose', '')).replace('_', ' ')}"
            + (f", ${float(amount):,.0f}" if amount else "")
        ).strip()
    amount = packet.get("requested_amount")
    return (
        f"{packet.get('product_code', '')} "
        f"{str(packet.get('loan_purpose', '')).replace('_', ' ')}"
        + (f", ${float(amount):,.0f}" if amount else "")
    ).strip()


app = create_app()


def main() -> int:
    """Run the development server."""
    import argparse

    import uvicorn

    parser = argparse.ArgumentParser(description="Run the CredPilot web application")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()

    print(f"CredPilot  ->  http://{args.host}:{args.port}")
    uvicorn.run(
        "src.web.app:app" if args.reload else app,
        host=args.host, port=args.port, reload=args.reload,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
