"""Tracing is wired into the run path, and carries nothing it should not.

REQ-077 requires the tracer to be *called*, not merely imported. These tests
capture spans from a real retrieval and check their shape, their attributes and
what those attributes do not contain.
"""

from __future__ import annotations

import json

import pytest

from src.domain import LendingProductDomain
from src.guardrails.redaction import find_sensitive
from src.observability import tracing as tr
from src.rag.models import PolicyRetrievalRequest

pytestmark = [pytest.mark.integration, pytest.mark.slow]

#: Every stage that must appear in a traced retrieval.
EXPECTED_SPANS = {
    tr.SPAN_RAG_RETRIEVE,
    tr.SPAN_METADATA_FILTER,
    tr.SPAN_BM25_SEARCH,
    tr.SPAN_EMBEDDING_QUERY,
    tr.SPAN_CHROMA_SEARCH,
    tr.SPAN_RRF_FUSION,
    tr.SPAN_RERANKER_RUN,
    tr.SPAN_TEMPORAL_VALIDATE,
    tr.SPAN_CITATION_VALIDATE,
    tr.SPAN_RAG_RESULT,
}


class _Recorder:
    """Collects finished spans in-process."""

    def __init__(self):
        self.spans = []

    def export(self, spans):
        from opentelemetry.sdk.trace.export import SpanExportResult

        self.spans.extend(spans)
        return SpanExportResult.SUCCESS

    def shutdown(self):
        return None

    def force_flush(self, timeout_millis=30_000):
        return True


@pytest.fixture
def recorded(monkeypatch):
    """Install a recording tracer for the duration of one test."""
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor

    recorder = _Recorder()
    provider = TracerProvider(resource=Resource.create({"service.name": "credpilot-test"}))
    provider.add_span_processor(SimpleSpanProcessor(recorder))

    monkeypatch.setattr(tr, "_TRACER", provider.get_tracer("credpilot.rag"))
    monkeypatch.setattr(tr, "_TRACER_PROVIDER", provider)
    monkeypatch.setattr(tr, "_INITIALIZED", True)
    yield recorder


def _names(recorder) -> set[str]:
    return {s.name for s in recorder.spans}


def _attrs(recorder, name) -> dict:
    span = next(s for s in recorder.spans if s.name == name)
    return dict(span.attributes or {})


# ------------------------------------------------------------------- spans are emitted


def test_a_retrieval_emits_every_stage_span(retriever, recorded):
    retriever.retrieve(
        PolicyRetrievalRequest(
            product_domain=LendingProductDomain.MORTGAGE,
            query_text="What is the maximum back-end debt-to-income ratio?",
            application_id="APP-000056",
            as_of_date="2026-07-08",
        )
    )
    missing = EXPECTED_SPANS - _names(recorded)
    assert not missing, f"stages ran untraced: {sorted(missing)}"


def test_spans_carry_latency(retriever, recorded):
    retriever.retrieve(
        PolicyRetrievalRequest(
            product_domain=LendingProductDomain.EDUCATION_LOAN,
            query_text="Does this borrower require a cosigner?",
            as_of_date="2026-08-01",
        )
    )
    for span in recorded.spans:
        assert span.end_time is not None, f"{span.name} never ended"
        assert span.end_time >= span.start_time


def test_spans_nest_under_the_root(retriever, recorded):
    """A trace, not a flat list of unrelated spans."""
    retriever.retrieve(
        PolicyRetrievalRequest(
            product_domain=LendingProductDomain.MORTGAGE,
            query_text="How many months of reserves are required?",
            as_of_date="2026-08-12",
        )
    )
    root = next(s for s in recorded.spans if s.name == tr.SPAN_RAG_RETRIEVE)
    trace_ids = {s.get_span_context().trace_id for s in recorded.spans}
    assert len(trace_ids) == 1, "the retrieval produced more than one trace"
    assert root.get_span_context().trace_id in trace_ids

    children = [s for s in recorded.spans if s.name in EXPECTED_SPANS - {tr.SPAN_RAG_RETRIEVE}]
    assert children
    assert all(s.parent is not None for s in children)


# -------------------------------------------------------------------- useful attributes


def test_the_root_span_identifies_the_request(retriever, recorded):
    retriever.retrieve(
        PolicyRetrievalRequest(
            product_domain=LendingProductDomain.MORTGAGE,
            query_text="What is the maximum back-end debt-to-income ratio?",
            application_id="APP-000056",
            as_of_date="2026-07-08",
            top_k=6,
        )
    )
    attrs = _attrs(recorded, tr.SPAN_RAG_RETRIEVE)
    assert attrs["product_domain"] == "MORTGAGE"
    assert attrs["application_id"] == "APP-000056"
    assert attrs["as_of_date"] == "2026-07-08"
    assert attrs["top_k"] == 6
    assert attrs["status"] == "FOUND"
    assert attrs["evidence_count"] > 0


def test_the_result_span_records_what_came_back(retriever, recorded):
    retriever.retrieve(
        PolicyRetrievalRequest(
            product_domain=LendingProductDomain.MORTGAGE,
            query_text="What is the maximum back-end debt-to-income ratio?",
            as_of_date="2026-07-08",
        )
    )
    attrs = _attrs(recorded, tr.SPAN_RAG_RESULT)
    assert "DTI-CONV-001" in attrs["rule_ids"]
    assert "POL-DTI-001" in attrs["policy_ids"]
    assert "2.0" in attrs["policy_versions"]
    assert "POL-DTI-001 v2.0 rule DTI-CONV-001" in attrs["citations"]
    assert attrs["latency_ms"] > 0


def test_candidate_counts_are_traced_at_each_stage(retriever, recorded):
    """A trace should show where candidates were gained and lost."""
    retriever.retrieve(
        PolicyRetrievalRequest(
            product_domain=LendingProductDomain.MORTGAGE,
            query_text="What documentation is required?",
            as_of_date="2026-08-12",
        )
    )
    assert _attrs(recorded, tr.SPAN_METADATA_FILTER)["catalogue_size"] > 0
    assert _attrs(recorded, tr.SPAN_BM25_SEARCH)["hits"] >= 0
    assert _attrs(recorded, tr.SPAN_CHROMA_SEARCH)["hits"] > 0
    assert _attrs(recorded, tr.SPAN_RRF_FUSION)["fused_candidates"] > 0
    assert _attrs(recorded, tr.SPAN_RERANKER_RUN)["kept"] > 0
    assert "kept" in _attrs(recorded, tr.SPAN_TEMPORAL_VALIDATE)


def test_the_filter_span_shows_the_temporal_narrowing(retriever, recorded):
    retriever.retrieve(
        PolicyRetrievalRequest(
            product_domain=LendingProductDomain.MORTGAGE,
            query_text="What affordability ceiling applies?",
            as_of_date="2026-06-25",
        )
    )
    attrs = _attrs(recorded, tr.SPAN_METADATA_FILTER)
    assert attrs["allowed"] < attrs["catalogue_size"], (
        "the effective-date filter removed nothing, so it is not being applied"
    )
    assert attrs["governing_policies"] > 0


# --------------------------------------------------------- attributes stay safe


def test_no_span_attribute_carries_an_identifier(retriever, recorded, repo_root):
    """Drive tracing with an adversarial packet full of identifiers."""
    from src.domain import load_application

    packet = load_application(
        repo_root / "synthetic_data/mortgage/applications/APP-000067.json"
    )
    retriever.retrieve(
        PolicyRetrievalRequest(
            product_domain=LendingProductDomain.MORTGAGE,
            query_text=packet["untrusted_applicant_text"]["content"],
            application_id="APP-000067",
            as_of_date="2026-08-12",
        )
    )
    payload = json.dumps(
        [{"name": s.name, "attributes": dict(s.attributes or {})} for s in recorded.spans],
        default=str,
    )
    assert not find_sensitive(payload), find_sensitive(payload)


def test_no_span_attribute_carries_policy_prose(retriever, recorded):
    """Spans carry identifiers and counts, not the evidence text."""
    retriever.retrieve(
        PolicyRetrievalRequest(
            product_domain=LendingProductDomain.MORTGAGE,
            query_text="What is the maximum back-end debt-to-income ratio?",
            as_of_date="2026-07-08",
        )
    )
    payload = json.dumps(
        [dict(s.attributes or {}) for s in recorded.spans], default=str
    )
    assert "Back-end debt-to-income must not exceed" not in payload


def test_attribute_values_are_truncated():
    attrs = tr.safe_attributes({"long": "x" * 5000})
    assert len(attrs["long"]) <= 512


def test_attribute_coercion_keeps_types():
    attrs = tr.safe_attributes(
        {"n": 5, "f": 1.5, "b": True, "s": "text", "seq": ["a", "b"], "none": None}
    )
    assert attrs["n"] == 5 and attrs["f"] == 1.5 and attrs["b"] is True
    assert attrs["s"] == "text"
    assert attrs["seq"] == "a,b"
    assert "none" not in attrs


def test_attributes_are_redacted_as_a_last_resort():
    attrs = tr.safe_attributes({"note": "SSN 123-45-6789"})
    assert "123-45-6789" not in attrs["note"]


# ------------------------------------------------------------------- degradation


def test_tracing_is_off_by_default(monkeypatch):
    """No collector is contacted unless tracing was asked for."""
    monkeypatch.delenv("CREDPILOT_TRACING", raising=False)
    monkeypatch.setattr(tr, "_INITIALIZED", False)
    monkeypatch.setattr(tr, "_TRACER", None)
    assert tr.get_tracer() is None
    assert not tr.tracing_requested()


def test_spans_degrade_to_no_ops_without_a_tracer(monkeypatch):
    """Retrieval must never break because observability is unavailable."""
    monkeypatch.setattr(tr, "_INITIALIZED", True)
    monkeypatch.setattr(tr, "_TRACER", None)
    with tr.span("x", a=1) as handle:
        handle.set(b=2)
        assert handle.ids == (None, None)


def test_retrieval_works_with_tracing_disabled(retriever, monkeypatch):
    monkeypatch.setattr(tr, "_INITIALIZED", True)
    monkeypatch.setattr(tr, "_TRACER", None)
    result = retriever.retrieve(
        PolicyRetrievalRequest(
            product_domain=LendingProductDomain.MORTGAGE,
            query_text="What is the maximum back-end debt-to-income ratio?",
            as_of_date="2026-07-08",
        )
    )
    assert result.evidence


# --------------------------------------------------------------- committed export


def test_the_committed_trace_export_is_usable(repo_root):
    """REQ-078: ≥1 full run, spans across agents and tools, latencies present."""
    export = repo_root / "traces" / "phoenix_spans.jsonl"
    if not export.exists():
        pytest.skip("run 'python scripts/export_traces.py' first")

    spans = [json.loads(line) for line in export.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert spans, "the export is empty"

    names = {s["name"] for s in spans}
    assert EXPECTED_SPANS <= names, f"missing {sorted(EXPECTED_SPANS - names)}"

    assert all(s.get("latency_ms") is not None for s in spans), "latencies are missing"
    assert len({s["trace_id"] for s in spans}) >= 1

    domains = {
        s["attributes"].get("product_domain")
        for s in spans
        if s.get("attributes", {}).get("product_domain")
    }
    assert domains >= {"MORTGAGE", "EDUCATION_LOAN"}, (
        f"the export covers only {domains}; both products must be traced"
    )

    payload = export.read_text(encoding="utf-8")
    assert not find_sensitive(payload)
