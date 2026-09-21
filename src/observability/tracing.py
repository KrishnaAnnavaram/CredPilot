"""Arize Phoenix / OpenTelemetry instrumentation for the CredPilot run path.

The tracer is *called*, not merely imported: every retrieval stage opens a span
through :func:`span`, so a committed trace export shows the real shape of a run —
which stages ran, how long each took, how many candidates survived each filter.

Two design rules the rest of the code depends on:

* **No sensitive applicant text ever becomes a span attribute.** Attributes carry
  identifiers, counts, latencies and policy/rule ids. Query text is truncated and
  redacted before it is recorded; applicant documents are never recorded at all.
* **Tracing never breaks retrieval.** If Phoenix or the OTLP exporter is
  unavailable the span helpers degrade to no-ops and retrieval continues.
"""

from __future__ import annotations

import contextlib
import os
import threading
from typing import Any, Iterator, Mapping

from src.guardrails.redaction import redact_text

_LOCK = threading.Lock()
_TRACER: Any = None
_TRACER_PROVIDER: Any = None
_INITIALIZED = False

#: Span names used across the retrieval path. Kept in one place so the trace
#: export, the failure analysis and the tests all refer to the same strings.
SPAN_RAG_RETRIEVE = "rag.retrieve"
SPAN_DOMAIN_RESOLVE = "domain.resolve"
SPAN_METADATA_FILTER = "metadata.filter"
SPAN_BM25_SEARCH = "bm25.search"
SPAN_EMBEDDING_QUERY = "embedding.query"
SPAN_CHROMA_SEARCH = "chroma.search"
SPAN_RRF_FUSION = "rrf.fusion"
SPAN_RERANKER_RUN = "reranker.run"
SPAN_TEMPORAL_VALIDATE = "temporal.validate"
SPAN_CITATION_VALIDATE = "citation.validate"
SPAN_RAG_RESULT = "rag.result"

PROJECT_NAME = os.environ.get("PHOENIX_PROJECT_NAME", "credpilot")

#: Attribute values longer than this are truncated before export.
_MAX_ATTR_CHARS = 512

#: Tracing is opt-in. Phoenix's exporter targets a local collector, and wiring it
#: up implicitly means every ``retrieve_policy`` call in a test or a benchmark
#: spends its time retrying a connection to a collector nobody started. Callers
#: that want traces call :func:`configure_tracing`; setting ``CREDPILOT_TRACING=1``
#: turns it on for a whole process.
_TRACING_ENV_FLAG = "CREDPILOT_TRACING"


def tracing_requested() -> bool:
    return os.environ.get(_TRACING_ENV_FLAG, "").strip().lower() in ("1", "true", "yes", "on")


def configure_tracing(
    *,
    project_name: str = PROJECT_NAME,
    endpoint: str | None = None,
    force: bool = False,
) -> Any:
    """Wire the Phoenix/OpenInference tracer into this process.

    Returns the tracer, or ``None`` when tracing could not be configured. Safe to
    call more than once; subsequent calls reuse the configured provider unless
    ``force`` is set.
    """
    global _TRACER, _TRACER_PROVIDER, _INITIALIZED

    with _LOCK:
        if _INITIALIZED and not force:
            return _TRACER
        _INITIALIZED = True
        try:
            from phoenix.otel import register

            _TRACER_PROVIDER = register(
                project_name=project_name,
                endpoint=endpoint or os.environ.get("PHOENIX_COLLECTOR_ENDPOINT"),
                auto_instrument=False,
                batch=True,
                set_global_tracer_provider=True,
            )
            _TRACER = _TRACER_PROVIDER.get_tracer("credpilot.rag")
        except Exception:  # noqa: BLE001 - observability must never break retrieval
            try:
                from opentelemetry import trace as _trace

                _TRACER = _trace.get_tracer("credpilot.rag")
            except Exception:  # noqa: BLE001
                _TRACER = None
        return _TRACER


def get_tracer() -> Any:
    """The configured tracer.

    Returns ``None`` — and every span becomes a no-op — unless tracing was
    explicitly configured or ``CREDPILOT_TRACING`` is set.
    """
    if not _INITIALIZED:
        if not tracing_requested():
            return None
        return configure_tracing()
    return _TRACER


def flush_traces(timeout_millis: int = 10_000) -> bool:
    """Force-flush pending spans. Returns whether a provider was available."""
    provider = _TRACER_PROVIDER
    if provider is None:
        return False
    try:
        provider.force_flush(timeout_millis)
        return True
    except Exception:  # noqa: BLE001
        return False


def safe_attributes(attrs: Mapping[str, Any]) -> dict[str, Any]:
    """Coerce attributes to OTel-safe scalars, redacting and truncating strings.

    Applicant-identifying values are redacted here as a last line of defence, so
    a caller that forgets cannot leak through the trace export.
    """
    out: dict[str, Any] = {}
    for key, value in attrs.items():
        if value is None:
            continue
        if isinstance(value, bool) or isinstance(value, (int, float)):
            out[key] = value
        elif isinstance(value, (list, tuple, set)):
            joined = ",".join(str(v) for v in list(value)[:40])
            out[key] = redact_text(joined)[:_MAX_ATTR_CHARS]
        else:
            out[key] = redact_text(str(value))[:_MAX_ATTR_CHARS]
    return out


@contextlib.contextmanager
def span(name: str, **attributes: Any) -> Iterator[Any]:
    """Open a span, degrading to a no-op when no tracer is configured."""
    tracer = get_tracer()
    if tracer is None:
        yield _NullSpan()
        return
    with tracer.start_as_current_span(name) as otel_span:
        for key, value in safe_attributes(attributes).items():
            otel_span.set_attribute(key, value)
        yield _SpanHandle(otel_span)


class _NullSpan:
    def set(self, **attributes: Any) -> None:  # pragma: no cover - trivial
        return None

    @property
    def ids(self) -> tuple[str | None, str | None]:
        return None, None


class _SpanHandle:
    """Thin wrapper so callers add attributes without importing OpenTelemetry."""

    def __init__(self, otel_span: Any):
        self._span = otel_span

    def set(self, **attributes: Any) -> None:
        for key, value in safe_attributes(attributes).items():
            self._span.set_attribute(key, value)

    @property
    def ids(self) -> tuple[str | None, str | None]:
        """``(trace_id, span_id)`` as 32/16-char hex, for evidence citations."""
        try:
            ctx = self._span.get_span_context()
            return f"{ctx.trace_id:032x}", f"{ctx.span_id:016x}"
        except Exception:  # noqa: BLE001
            return None, None


def current_ids() -> tuple[str | None, str | None]:
    """``(trace_id, span_id)`` of the active span, or ``(None, None)``."""
    try:
        from opentelemetry import trace as _trace

        ctx = _trace.get_current_span().get_span_context()
        if not ctx.is_valid:
            return None, None
        return f"{ctx.trace_id:032x}", f"{ctx.span_id:016x}"
    except Exception:  # noqa: BLE001
        return None, None
