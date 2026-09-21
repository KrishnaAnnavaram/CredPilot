"""The agentic-RAG tool's contract.

What this pins down: the tool performs real retrieval, it logs every call through
committed middleware, it returns a status the caller must branch on, and it never
hands back evidence it cannot cite.
"""

from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from src.domain import LendingProductDomain
from src.observability.tool_logging import read_log, summarize_result
from src.rag.models import PolicyRetrievalResult, RetrievalStatus
from src.tools import rag_tool

pytestmark = pytest.mark.integration


@pytest.fixture
def isolated_logs(tmp_path, monkeypatch):
    """Point the logging middleware at a temporary directory."""
    tool_log = tmp_path / "tool_calls.jsonl"
    action_log = tmp_path / "agent_actions.jsonl"
    monkeypatch.setattr("src.observability.tool_logging.TOOL_CALL_LOG", tool_log)
    monkeypatch.setattr("src.observability.tool_logging.AGENT_ACTION_LOG", action_log)
    return tool_log, action_log


# ------------------------------------------------------------------------- the surface


def test_the_tool_lives_where_the_checklist_says(repo_root):
    assert (repo_root / "src" / "tools" / "rag_tool.py").exists()


def test_the_tool_name_is_stable():
    assert rag_tool.TOOL_NAME == "retrieve_policy"


def test_the_description_tells_a_model_what_it_must_supply():
    description = rag_tool.TOOL_DESCRIPTION
    assert "MORTGAGE" in description and "EDUCATION_LOAN" in description
    assert "as_of_date" in description
    assert "PRODUCT_CLARIFICATION_REQUIRED" in description
    assert "citation" in description.lower()


def test_the_input_schema_rejects_unknown_arguments():
    with pytest.raises(Exception):
        rag_tool.RetrievePolicyInput(query="x", not_a_field=1)


def test_the_input_schema_requires_a_query():
    with pytest.raises(Exception):
        rag_tool.RetrievePolicyInput()


# ------------------------------------------------------- it really retrieves


def test_the_tool_does_not_return_a_hardcoded_answer():
    """Different questions must produce different evidence."""
    first = rag_tool.retrieve_policy_tool(
        query="What is the maximum back-end debt-to-income ratio?",
        application_id="APP-000056",
        as_of_date="2026-07-08",
    )
    second = rag_tool.retrieve_policy_tool(
        query="How many months of post-closing reserves are required?",
        application_id="APP-000056",
        as_of_date="2026-07-08",
    )
    assert {e.chunk_id for e in first.evidence} != {e.chunk_id for e in second.evidence}
    assert any(e.rule_id == "DTI-CONV-001" for e in first.evidence)
    assert any(e.policy_id == "POL-AST-003" for e in second.evidence)


def test_the_tool_source_contains_no_canned_answer(repo_root):
    """No hardcoded policy text, and no golden lookup, in the tool itself."""
    source = (repo_root / "src" / "tools" / "rag_tool.py").read_text(encoding="utf-8")
    assert "golden" not in source.lower().replace("golden set", "")
    assert "return hardcoded" not in source
    # It delegates to the real pipeline rather than reimplementing a shortcut.
    assert "retrieve_policy" in source
    assert "from src.rag.pipeline import" in source


def test_the_tool_runs_the_whole_pipeline_not_similarity_alone():
    """Evidence carries a lexical rank, a fusion score and a reranker score."""
    result = rag_tool.retrieve_policy_tool(
        query="What does DTI-CONV-001 say about compensating factors?",
        product_domain=LendingProductDomain.MORTGAGE,
        as_of_date="2026-07-08",
    )
    assert result.evidence
    top = result.evidence[0]
    assert top.fusion_score is not None
    assert top.reranker_score is not None
    assert top.dense_rank is not None or top.bm25_rank is not None
    assert any(e.bm25_rank is not None for e in result.evidence), "the lexical layer did not run"
    assert result.stage_latency_ms.keys() >= {"bm25", "dense", "fusion", "rerank", "citation"}


def test_the_tool_returns_the_typed_result_model():
    result = rag_tool.retrieve_policy_tool(
        query="Does this borrower require a cosigner?", application_id="APP-2026-00001"
    )
    assert isinstance(result, PolicyRetrievalResult)
    assert isinstance(result.status, RetrievalStatus)
    assert result.product_domain is LendingProductDomain.EDUCATION_LOAN


# ------------------------------------------------------------------------ status branch


def test_an_unresolvable_product_is_a_status_not_an_exception():
    result = rag_tool.retrieve_policy_tool(query="What is the DTI limit?")
    assert result.status is RetrievalStatus.PRODUCT_CLARIFICATION_REQUIRED
    assert result.evidence == []
    assert result.message


def test_no_applicable_policy_is_reported_rather_than_faked():
    result = rag_tool.retrieve_policy_tool(
        query="What is the maximum debt-to-income ratio?",
        product_domain="MORTGAGE",
        as_of_date="2019-01-01",
    )
    assert result.status is RetrievalStatus.NO_APPLICABLE_POLICY
    assert result.evidence == []
    assert result.citations == []


def test_every_returned_citation_resolves():
    for query, application_id in (
        ("What are the leverage limits?", "APP-000056"),
        ("What school certification is required?", "APP-2026-00024"),
    ):
        result = rag_tool.retrieve_policy_tool(query=query, application_id=application_id)
        assert result.evidence
        assert all(e.citation_resolves for e in result.evidence)


# ----------------------------------------------------------------------------- logging


def test_a_call_writes_a_tool_log_record(isolated_logs):
    tool_log, action_log = isolated_logs
    rag_tool.retrieve_policy_tool(
        query="What is the maximum back-end debt-to-income ratio?",
        application_id="APP-000056",
        as_of_date="2026-07-08",
        agent="test_agent",
    )

    records = read_log(tool_log)
    assert len(records) == 1
    record = records[0]
    for field in (
        "timestamp", "agent", "tool_name", "args", "result", "latency_ms", "status",
    ):
        assert field in record, field
    assert record["tool_name"] == "retrieve_policy"
    assert record["agent"] == "test_agent"
    assert record["status"] == "OK"
    assert record["latency_ms"] > 0
    assert record["product_domain"] == "MORTGAGE"
    assert record["result"]["citations"]
    assert record["result"]["all_citations_resolve"] is True


def test_a_call_writes_an_audit_record(isolated_logs):
    tool_log, action_log = isolated_logs
    rag_tool.retrieve_policy_tool(
        query="Does this borrower require a cosigner?",
        application_id="APP-2026-00001",
        agent="test_agent",
    )
    records = read_log(action_log)
    assert len(records) == 1
    record = records[0]
    for field in ("timestamp", "actor", "action", "tool", "decision"):
        assert field in record, field
    assert record["action"] == "policy_retrieval"
    assert record["product_domain"] == "EDUCATION_LOAN"
    assert record["detail"]["citations"]


def test_the_log_carries_no_policy_prose(isolated_logs):
    """Identifiers and counts reconcile with the trace; prose does not belong."""
    tool_log, _ = isolated_logs
    rag_tool.retrieve_policy_tool(
        query="What is the maximum back-end debt-to-income ratio?",
        application_id="APP-000056",
        as_of_date="2026-07-08",
    )
    text = tool_log.read_text(encoding="utf-8")
    assert "Back-end debt-to-income must not exceed" not in text
    assert "DTI-CONV-001" in text, "the rule id should still reconcile with the code"


def test_a_failing_call_is_logged_as_an_error(isolated_logs, monkeypatch):
    tool_log, _ = isolated_logs

    def boom(**kwargs):
        raise RuntimeError("index unavailable")

    monkeypatch.setattr(rag_tool, "retrieve_policy", boom)
    with pytest.raises(RuntimeError):
        rag_tool.retrieve_policy_tool(query="x", product_domain="MORTGAGE")

    records = read_log(tool_log)
    assert records[-1]["status"] == "ERROR"
    assert "index unavailable" in records[-1]["error"]


def test_the_result_summary_never_carries_evidence_text():
    result = rag_tool.retrieve_policy_tool(
        query="What are the reserve requirements?",
        application_id="APP-000056",
        as_of_date="2026-07-08",
    )
    summary = summarize_result(result)
    assert summary["type"] == "PolicyRetrievalResult"
    assert "text" not in json.dumps(summary)
    assert summary["evidence_count"] == len(result.evidence)


# ------------------------------------------------------------------- serialized output


def test_the_json_payload_hides_ranking_internals():
    """What an agent needs is evidence and citations, not fusion scores."""
    payload = rag_tool.retrieve_policy_json(
        query="What is the maximum back-end debt-to-income ratio?",
        application_id="APP-000056",
        as_of_date="2026-07-08",
    )
    assert payload["status"] == "FOUND"
    assert payload["evidence"]
    item = payload["evidence"][0]
    assert {"citation", "citation_resolves", "policy_id", "rule_id", "text"} <= set(item)
    for internal in ("fusion_score", "reranker_score", "dense_rank", "bm25_rank", "chunk_id"):
        assert internal not in item
    # It must survive a JSON round trip, since it crosses the MCP boundary.
    assert json.loads(json.dumps(payload)) == payload


def test_the_langchain_tool_exposes_the_same_contract():
    tool = rag_tool.build_langchain_tool()
    assert tool.name == "retrieve_policy"
    assert tool.args_schema is rag_tool.RetrievePolicyInput
    payload = tool.invoke(
        {
            "query": "What is the maximum back-end debt-to-income ratio?",
            "application_id": "APP-000056",
            "as_of_date": "2026-07-08",
            "top_k": 3,
        }
    )
    assert payload["status"] == "FOUND"
    assert all(e["citation_resolves"] for e in payload["evidence"])


def test_the_corpus_summary_describes_both_products():
    summary = rag_tool.policy_corpus_summary()
    assert set(summary["products"]) == {"mortgage", "education"}
    for product in summary["products"].values():
        assert product["document_count"] > 0
        assert product["policies"]
    assert summary["embedding_model"]


# ------------------------------------------------------- degradation is not silent


@pytest.mark.slow
def test_an_unresolvable_citation_is_replaced_not_dropped(retriever, monkeypatch):
    """A bad citation must shorten nothing — the next good candidate fills in.

    Citation validity is 1.0 over the committed corpus, so this path needs a
    forced failure to exercise. Without the slack the pipeline keeps after
    deduplication, one unresolvable citation would quietly return five results
    where six were asked for, and nothing would say so.
    """
    from src.domain import LendingProductDomain
    from src.rag.models import PolicyRetrievalRequest

    request = PolicyRetrievalRequest(
        product_domain=LendingProductDomain.MORTGAGE,
        query_text="How is income qualified for a self-employed borrower?",
        as_of_date="2026-08-12",
        top_k=5,
    )

    baseline = retriever.retrieve(request)
    assert len(baseline.evidence) == 5, "the query needs a pool deeper than top_k"
    doomed = baseline.evidence[0].citation

    real_resolve = retriever._citations.resolve

    def resolve(citation: str):
        if citation == doomed:
            return False, "forced failure for the test"
        return real_resolve(citation)

    monkeypatch.setattr(retriever._citations, "resolve", resolve)

    degraded = retriever.retrieve(request)
    citations = [e.citation for e in degraded.evidence]

    assert doomed not in citations, "the unresolvable citation was returned anyway"
    assert len(degraded.evidence) == 5, "the result shrank instead of backfilling"
    assert all(e.citation_resolves for e in degraded.evidence)
    assert [e.final_rank for e in degraded.evidence] == [1, 2, 3, 4, 5]


@pytest.mark.slow
def test_a_large_top_k_is_not_capped_by_the_configured_funnel(retriever, config):
    """Every stage width is a floor of top_k, not a cap.

    The configured funnel is tuned for the default top_k of 6. Asking for 15 used
    to return 4: `fusion_top_k` of 12 and an overview budget of 2 both truncated
    the result, and nothing in the response said so. What may legitimately
    shorten a result is deduplication running out of *distinct* (policy, rule)
    units — a different thing, and visible in the candidate counts.
    """
    from src.domain import LendingProductDomain
    from src.rag.models import PolicyRetrievalRequest

    result = retriever.retrieve(
        PolicyRetrievalRequest(
            product_domain=LendingProductDomain.MORTGAGE,
            query_text="Which policies govern this application?",
            as_of_date="2026-08-12",
            top_k=15,
        )
    )

    # Every stage carried at least the requested number of candidates, even
    # though two of the configured widths are narrower than that.
    assert config.retrieval.fusion_top_k < 15, "this test assumes the tuned funnel"
    assert config.retrieval.rerank_top_k < 15
    assert result.dense_candidates >= 15
    assert result.fused_candidates >= 15
    assert result.reranked_candidates >= 15

    # And far more evidence comes back than the old cap allowed.
    assert len(result.evidence) >= 10
    assert [e.final_rank for e in result.evidence] == list(
        range(1, len(result.evidence) + 1)
    )
    # Deduplication still holds: one chunk per rule.
    units = [(e.policy_id, e.policy_version, e.rule_id or e.section_number) for e in result.evidence]
    assert len(units) == len(set(units))


@pytest.mark.slow
def test_the_default_top_k_is_unaffected_by_the_width_floors(retriever, config):
    """The measured funnel still governs at the default size."""
    from src.domain import LendingProductDomain
    from src.rag.models import PolicyRetrievalRequest

    result = retriever.retrieve(
        PolicyRetrievalRequest(
            product_domain=LendingProductDomain.MORTGAGE,
            query_text="What is the maximum back-end debt-to-income ratio?",
            as_of_date="2026-07-08",
        )
    )
    assert result.dense_candidates <= config.retrieval.dense_top_k
    assert result.fused_candidates <= config.retrieval.fusion_top_k
    assert result.reranked_candidates <= config.retrieval.rerank_top_k
    assert len(result.evidence) == config.retrieval.final_top_k
