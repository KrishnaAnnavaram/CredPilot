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

#: Node, agent and model spans opened by the graph rather than by retrieval.
SPAN_INTAKE = "graph.intake"
SPAN_INPUT_GUARDRAILS = "guardrails.input"
SPAN_SUPERVISOR = "supervisor.route"
SPAN_CLARIFICATION = "supervisor.clarify"
SPAN_MORTGAGE_AGENT = "agent.mortgage"
SPAN_EDUCATION_AGENT = "agent.education"
SPAN_ELIGIBILITY = "agent.eligibility"
SPAN_RISK = "agent.risk"
SPAN_RECOMMENDATION = "agent.recommendation"
SPAN_NARRATIVE = "llm.narrative"
SPAN_FINAL_RESPONSE = "agent.final_response"
SPAN_OUTPUT_GUARDRAILS = "guardrails.output"
SPAN_HUMAN_REVIEW = "agent.human_review"
SPAN_MCP_CONNECT = "mcp.connect"
SPAN_MCP_TOOL = "mcp.tool"
SPAN_MCP_RESOURCE = "mcp.resource"
SPAN_MCP_PROMPT = "mcp.prompt"

#: Every span declares which of four kinds of work it represents. AC-09 asks for
#: latency split into *thinking*, *acting* and *tool* time, and that split cannot
#: be recovered from span names alone once new nodes are added — so it is an
#: attribute the producer sets, and ``scripts/build_golden_signals.py`` reads it
#: rather than pattern-matching names it does not control.
#:
#:   THINKING   a language-model call. Billed, variable, and the tail of every
#:              assessment.
#:   ACTING     a graph node doing deterministic work: routing, calculation,
#:              rule evaluation, assembling a response.
#:   TOOL       a call that crosses a tool boundary — the agentic-RAG tool, an
#:              MCP tool, a resource read.
#:   RETRIEVAL  a stage inside the retrieval pipeline. A subset of tool work,
#:              reported separately because it is where the latency actually is.
SPAN_KIND_THINKING = "THINKING"
SPAN_KIND_ACTING = "ACTING"
SPAN_KIND_TOOL = "TOOL"
SPAN_KIND_RETRIEVAL = "RETRIEVAL"

SPAN_KIND_ATTRIBUTE = "credpilot.span_kind"

#: Default kind per span name, applied when a caller does not pass ``span_kind``.
#: Retrieval-stage spans predate the attribute and are classified here rather
#: than by editing eleven call sites that are already correct.
_DEFAULT_SPAN_KINDS: dict[str, str] = {
    SPAN_RAG_RETRIEVE: SPAN_KIND_TOOL,
    SPAN_RAG_RESULT: SPAN_KIND_TOOL,
    SPAN_DOMAIN_RESOLVE: SPAN_KIND_ACTING,
    SPAN_METADATA_FILTER: SPAN_KIND_RETRIEVAL,
    SPAN_BM25_SEARCH: SPAN_KIND_RETRIEVAL,
    SPAN_EMBEDDING_QUERY: SPAN_KIND_RETRIEVAL,
    SPAN_CHROMA_SEARCH: SPAN_KIND_RETRIEVAL,
    SPAN_RRF_FUSION: SPAN_KIND_RETRIEVAL,
    SPAN_RERANKER_RUN: SPAN_KIND_RETRIEVAL,
    SPAN_TEMPORAL_VALIDATE: SPAN_KIND_RETRIEVAL,
    SPAN_CITATION_VALIDATE: SPAN_KIND_RETRIEVAL,
    SPAN_INTAKE: SPAN_KIND_ACTING,
    SPAN_INPUT_GUARDRAILS: SPAN_KIND_ACTING,
    SPAN_SUPERVISOR: SPAN_KIND_ACTING,
    SPAN_CLARIFICATION: SPAN_KIND_ACTING,
    SPAN_MORTGAGE_AGENT: SPAN_KIND_ACTING,
    SPAN_EDUCATION_AGENT: SPAN_KIND_ACTING,
    SPAN_ELIGIBILITY: SPAN_KIND_ACTING,
    SPAN_RISK: SPAN_KIND_ACTING,
    SPAN_RECOMMENDATION: SPAN_KIND_ACTING,
    SPAN_NARRATIVE: SPAN_KIND_THINKING,
    "supervisor.classify": SPAN_KIND_THINKING,
    SPAN_FINAL_RESPONSE: SPAN_KIND_ACTING,
    SPAN_OUTPUT_GUARDRAILS: SPAN_KIND_ACTING,
    SPAN_HUMAN_REVIEW: SPAN_KIND_ACTING,
    SPAN_MCP_CONNECT: SPAN_KIND_TOOL,
    SPAN_MCP_TOOL: SPAN_KIND_TOOL,
    SPAN_MCP_RESOURCE: SPAN_KIND_TOOL,
    SPAN_MCP_PROMPT: SPAN_KIND_TOOL,
}


def span_kind_for(name: str, explicit: str | None = None) -> str:
    """The kind attribute a span carries. Explicit wins; otherwise by name."""
    if explicit:
        return str(explicit)
    return _DEFAULT_SPAN_KINDS.get(name, SPAN_KIND_ACTING)

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



def _random_id_generator_base():
    """The SDK's own generator, imported lazily so tracing stays optional."""
    from opentelemetry.sdk.trace.id_generator import RandomIdGenerator

    return RandomIdGenerator


class UnambiguousIdGenerator(_random_id_generator_base()):
    """Random OTel ids, with the all-decimal ones rejected.

    A span id is 16 hex characters and a trace id is 32. Roughly one in 1,800
    span ids comes out with no a-f character in it, and a 16-digit run
    beginning with 4 is a valid Visa shape — so a committed trace export
    randomly acquires a string that every payment-card scanner reports as an
    unmasked account number. Two turned up in one 1,119-span export.

    NFR-05 says no committed artifact carries an account-number-shaped string.
    An identifier that satisfies that by luck does not satisfy it. The
    alternative — exempting the shape wherever it might appear — weakens the
    scan that exists to catch a real leak, and has to be re-done for every new
    artifact format. This fixes it once, where the id is made.

    The cost is 1/16 of the id space for a span id (those with no a-f
    character), which is a rounding error against 2^64, and none of the
    properties that matter: the ids stay uniformly random over the remaining
    space, stay 64- and 128-bit, and stay valid OpenTelemetry ids. Rejection
    sampling, not munging — a mangled id would no longer be random.

    A subclass rather than a wrapper because the SDK calls more of the
    interface than the two generate methods: `start_span` asks
    `is_trace_id_random()`, and a duck-typed class raised AttributeError on
    the first span.
    """

    #: Drawn again rather than edited. In practice the first draw succeeds
    #: ~99.94% of the time; the bound only exists so a broken RNG cannot hang.
    MAX_DRAWS = 64

    @staticmethod
    def _is_ambiguous(value: int, width: int) -> bool:
        """Whether the hex rendering is all decimal digits, hence card-shaped."""
        return all(c in "0123456789" for c in format(value, f"0{width}x"))

    def generate_span_id(self) -> int:
        for _ in range(self.MAX_DRAWS):
            value = super().generate_span_id()
            if not self._is_ambiguous(value, 16):
                return value
        return value  # pragma: no cover - a broken RNG; a valid id still beats none

    def generate_trace_id(self) -> int:
        for _ in range(self.MAX_DRAWS):
            value = super().generate_trace_id()
            if not self._is_ambiguous(value, 32):
                return value
        return value  # pragma: no cover



def unambiguous_id_generator() -> "UnambiguousIdGenerator":
    """The id generator every CredPilot tracer provider should be built with.

    A function rather than a module-level instance so each provider gets its
    own, and so there is one name to call from anywhere a provider is
    constructed. There are two such places — the OTLP exporter in
    :func:`configure_tracing` and the in-process recorder in
    `scripts/export_traces.py` — and the second is the one whose ids reach a
    committed artifact.
    """
    return UnambiguousIdGenerator()


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
            # Before the tracer is built: `get_tracer` captures the
            # provider's id generator at construction, so swapping it
            # afterwards would have no effect.
            try:
                _TRACER_PROVIDER.id_generator = unambiguous_id_generator()
            except Exception:  # noqa: BLE001 - never break tracing over this
                pass
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
def span(name: str, *, span_kind: str | None = None, **attributes: Any) -> Iterator[Any]:
    """Open a span, degrading to a no-op when no tracer is configured.

    Every span carries a ``credpilot.span_kind`` attribute — THINKING, ACTING,
    TOOL or RETRIEVAL — so the golden-signals report can split latency the way
    AC-09 asks for it without pattern-matching span names. ``span_kind`` is
    inferred from the name when the caller does not pass one.
    """
    tracer = get_tracer()
    if tracer is None:
        yield _NullSpan()
        return
    with tracer.start_as_current_span(name) as otel_span:
        otel_span.set_attribute(SPAN_KIND_ATTRIBUTE, span_kind_for(name, span_kind))
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
