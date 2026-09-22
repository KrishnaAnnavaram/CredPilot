"""Machine-generated tool-invocation and audit logging.

Every tool call the agent makes is written to ``logs/tool_calls.jsonl`` by this
middleware, and every consequential action to ``logs/agent_actions.jsonl``. Both
files are produced by running code — nothing here is ever hand-written, which is
the point: a log a team could have typed is not evidence.

Both writers redact before they write. Arguments and results pass through
:func:`~src.guardrails.redaction.redact_structure` with Presidio enabled, so an
applicant identifier cannot reach disk in plaintext even if a caller forgets.
"""

from __future__ import annotations

import json
import os
import threading
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterator, Mapping

from src.config import REPO_ROOT
from src.guardrails.redaction import redact_structure, redact_text
from src.observability.tracing import current_ids

LOG_DIR = Path(os.environ.get("CREDPILOT_LOG_DIR", REPO_ROOT / "logs"))
TOOL_CALL_LOG = LOG_DIR / "tool_calls.jsonl"
AGENT_ACTION_LOG = LOG_DIR / "agent_actions.jsonl"
MCP_TRANSCRIPT_LOG = LOG_DIR / "mcp_transcript.jsonl"

_WRITE_LOCK = threading.Lock()

#: Result fields worth summarizing. A whole evidence list would bloat the log and
#: put policy prose in it; identifiers and counts reconcile with the trace.
_MAX_SUMMARY_ITEMS = 12


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def _append(path: Path, record: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=False, sort_keys=True, default=str)
    with _WRITE_LOCK:
        with path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")


def sanitize_args(args: Mapping[str, Any]) -> dict[str, Any]:
    """Redact tool arguments for logging."""
    return redact_structure(dict(args), use_presidio=True)


def summarize_result(result: Any) -> dict[str, Any]:
    """Reduce a tool result to a loggable summary.

    Policy text is deliberately excluded — the citation and chunk id resolve back
    to the committed source, so the log stays small and free of prose.
    """
    if result is None:
        return {"type": "null"}

    # PolicyRetrievalResult and anything shaped like it
    status = getattr(result, "status", None)
    evidence = getattr(result, "evidence", None)
    if status is not None and evidence is not None:
        return {
            "type": "PolicyRetrievalResult",
            "status": getattr(status, "value", str(status)),
            "product_domain": getattr(
                getattr(result, "product_domain", None), "value", None
            ),
            "evidence_count": len(evidence),
            "citations": [e.citation for e in evidence][:_MAX_SUMMARY_ITEMS],
            "policy_ids": sorted({e.policy_id for e in evidence})[:_MAX_SUMMARY_ITEMS],
            "rule_ids": [e.rule_id for e in evidence if e.rule_id][:_MAX_SUMMARY_ITEMS],
            "all_citations_resolve": all(e.citation_resolves for e in evidence),
        }

    if isinstance(result, Mapping):
        return {"type": "mapping", "keys": sorted(result)[:_MAX_SUMMARY_ITEMS]}
    if isinstance(result, (list, tuple)):
        return {"type": "sequence", "length": len(result)}
    return {"type": type(result).__name__, "repr": redact_text(str(result))[:300]}


#: How a tool was reached. Carried as its own field rather than baked into the
#: name.
#:
#: The name was briefly prefixed — ``mcp:retrieve_policy`` — so a 40 ms MCP
#: round trip could be told apart from a 1.4 s in-process retrieval in the
#: latency data. That broke the AC-07 reconciliation: the requirement is that
#: *"tool names reconcile with the agent/MCP code"*, and no source file contains
#: the string ``mcp:retrieve_policy``. The name of a tool is its name wherever
#: it is called from; how it was reached is a different fact about the call, and
#: it belongs in a different field.
TRANSPORT_IN_PROCESS = "in_process"
TRANSPORT_MCP = "mcp"


def log_tool_call(
    *,
    tool_name: str,
    agent: str,
    args: Mapping[str, Any],
    result: Any,
    latency_ms: float,
    status: str,
    product_domain: str | None = None,
    error: str | None = None,
    transport: str = TRANSPORT_IN_PROCESS,
    path: Path | None = None,
) -> dict[str, Any]:
    """Append one tool-invocation record and return it."""
    trace_id, span_id = current_ids()
    record: dict[str, Any] = {
        "timestamp": _now(),
        "call_id": str(uuid.uuid4()),
        "agent": agent,
        "tool_name": tool_name,
        "transport": transport,
        "product_domain": product_domain,
        "args": sanitize_args(args),
        "result": summarize_result(result),
        "latency_ms": round(float(latency_ms), 2),
        "status": status,
        "trace_id": trace_id,
        "span_id": span_id,
    }
    if error:
        record["error"] = redact_text(error)[:500]
    _append(path or TOOL_CALL_LOG, record)
    return record


def log_agent_action(
    *,
    actor: str,
    action: str,
    decision: str,
    tool: str | None = None,
    application_id: str | None = None,
    product_domain: str | None = None,
    detail: Mapping[str, Any] | None = None,
    path: Path | None = None,
) -> dict[str, Any]:
    """Append one audit-trail record for a consequential action."""
    trace_id, span_id = current_ids()
    record = {
        "timestamp": _now(),
        "event_id": str(uuid.uuid4()),
        "actor": actor,
        "action": action,
        "tool": tool,
        "decision": decision,
        "application_id": application_id,
        "product_domain": product_domain,
        "detail": redact_structure(dict(detail or {}), use_presidio=True),
        "trace_id": trace_id,
        "span_id": span_id,
    }
    _append(path or AGENT_ACTION_LOG, record)
    return record


def log_mcp_exchange(
    *,
    direction: str,
    method: str,
    payload: Mapping[str, Any],
    path: Path | None = None,
) -> dict[str, Any]:
    """Append one MCP request/response record to the committed transcript."""
    record = {
        "timestamp": _now(),
        "direction": direction,
        "method": method,
        "payload": redact_structure(dict(payload), use_presidio=True),
    }
    _append(path or MCP_TRANSCRIPT_LOG, record)
    return record


@contextmanager
def tool_call(
    tool_name: str,
    *,
    agent: str,
    args: Mapping[str, Any],
    product_domain: str | None = None,
) -> Iterator[dict[str, Any]]:
    """Time a tool call and log it, whether it succeeds or raises.

    Usage::

        with tool_call("retrieve_policy", agent="policy_retrieval", args=kwargs) as call:
            result = do_work()
            call["result"] = result
    """
    box: dict[str, Any] = {"result": None}
    started = time.perf_counter()
    try:
        yield box
    except Exception as exc:  # noqa: BLE001 - re-raised after logging
        log_tool_call(
            tool_name=tool_name,
            agent=agent,
            args=args,
            result=None,
            latency_ms=(time.perf_counter() - started) * 1000,
            status="ERROR",
            product_domain=product_domain,
            error=f"{type(exc).__name__}: {exc}",
        )
        raise
    else:
        result = box.get("result")
        log_tool_call(
            tool_name=tool_name,
            agent=agent,
            args=args,
            result=result,
            latency_ms=(time.perf_counter() - started) * 1000,
            status="OK",
            product_domain=product_domain
            or getattr(getattr(result, "product_domain", None), "value", None),
        )


def logged_tool(tool_name: str, agent: str) -> Callable:
    """Decorator form of :func:`tool_call` for plain functions."""

    def decorator(fn: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            with tool_call(tool_name, agent=agent, args=kwargs) as call:
                call["result"] = fn(*args, **kwargs)
                return call["result"]

        wrapper.__name__ = fn.__name__
        wrapper.__doc__ = fn.__doc__
        wrapper.__wrapped__ = fn
        return wrapper

    return decorator


def read_log(path: Path) -> list[dict[str, Any]]:
    """Read a JSONL log back, skipping blank lines."""
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
