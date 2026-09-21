"""Tool-contract tests (REQ-096).

*"asserts each tool's input/output schema + one error path"*

Every tool CredPilot exposes — in process and over MCP — is checked here for
three things: it accepts what it says it accepts, it returns what it says it
returns, and it fails in a way a caller can handle rather than in a way that
takes the run down.

The error path matters more than the happy path. A retrieval tool that raises on
an unknown product, or returns an empty list when it means "I could not tell
which product this is", produces an underwriting decision made on no evidence.
"""

from __future__ import annotations

import json

import pytest

from src.domain import LendingProductDomain
from src.rag.models import PolicyRetrievalResult, RetrievalStatus
from src.tools import rag_tool

pytestmark = pytest.mark.integration


# ========================================================================== schema


def test_the_input_schema_is_declared():
    schema = rag_tool.RetrievePolicyInput.model_json_schema()
    assert schema["required"] == ["query"]
    for field in (
        "query",
        "product_domain",
        "application_id",
        "as_of_date",
        "product_family",
        "loan_purpose",
        "occupancy_type",
        "product_code",
        "top_k",
    ):
        assert field in schema["properties"], field
    # Every optional field is documented, or a model cannot use it correctly.
    for name, spec in schema["properties"].items():
        assert spec.get("description"), f"{name} has no description"


def test_the_input_schema_rejects_an_unknown_field():
    with pytest.raises(Exception):
        rag_tool.RetrievePolicyInput(query="x", collection="credpilot_all_policies")


def test_the_input_schema_requires_a_query():
    with pytest.raises(Exception):
        rag_tool.RetrievePolicyInput()


def test_the_output_schema_is_typed():
    fields = PolicyRetrievalResult.model_fields
    for field in ("status", "product_domain", "evidence", "message", "latency_ms"):
        assert field in fields, field


@pytest.mark.slow
def test_the_output_shape_matches_the_contract():
    payload = rag_tool.retrieve_policy_json(
        query="What is the maximum back-end debt-to-income ratio?",
        application_id="APP-000056",
        as_of_date="2026-07-08",
        top_k=3,
    )
    assert set(payload) >= {
        "status",
        "product_domain",
        "as_of_date",
        "evidence",
        "evidence_count",
        "latency_ms",
    }
    assert payload["status"] in {s.value for s in RetrievalStatus}
    assert payload["product_domain"] in {d.value for d in LendingProductDomain}
    assert payload["evidence_count"] == len(payload["evidence"])

    for item in payload["evidence"]:
        for field in ("rank", "citation", "citation_resolves", "policy_id", "text"):
            assert field in item, field
        assert isinstance(item["citation_resolves"], bool)
        assert isinstance(item["rank"], int)

    # It crosses the MCP boundary, so it must survive a JSON round trip.
    assert json.loads(json.dumps(payload)) == payload


# ===================================================================== error paths


@pytest.mark.slow
def test_an_unresolvable_product_is_a_status_not_an_exception():
    """The caller must be able to branch, not catch."""
    result = rag_tool.retrieve_policy_tool(query="What is the DTI limit?")
    assert result.status is RetrievalStatus.PRODUCT_CLARIFICATION_REQUIRED
    assert result.evidence == []
    assert result.message and "PRODUCT_CLARIFICATION_REQUIRED" in result.message


@pytest.mark.slow
def test_no_applicable_policy_is_distinguishable_from_an_empty_answer():
    """"Nothing applies" and "I do not know which product" are different."""
    nothing_applies = rag_tool.retrieve_policy_tool(
        query="What is the maximum debt-to-income ratio?",
        product_domain="MORTGAGE",
        as_of_date="2019-01-01",
    )
    assert nothing_applies.status is RetrievalStatus.NO_APPLICABLE_POLICY
    assert nothing_applies.evidence == []

    cannot_tell = rag_tool.retrieve_policy_tool(query="What is the DTI limit?")
    assert cannot_tell.status is RetrievalStatus.PRODUCT_CLARIFICATION_REQUIRED
    assert nothing_applies.status is not cannot_tell.status


def test_an_unknown_product_domain_raises_with_a_usable_message():
    with pytest.raises(ValueError, match="unknown lending product domain"):
        LendingProductDomain.from_any("CAR_LOAN")


def test_a_blank_query_is_rejected_at_the_schema():
    from src.rag.models import PolicyRetrievalRequest

    with pytest.raises(Exception):
        PolicyRetrievalRequest(product_domain=LendingProductDomain.MORTGAGE, query_text="   ")


@pytest.mark.slow
def test_a_failing_tool_call_is_logged_and_re_raised(tmp_path, monkeypatch):
    """An error must reach the caller *and* the tool log."""
    from src.observability.tool_logging import read_log

    tool_log = tmp_path / "tool_calls.jsonl"
    monkeypatch.setattr("src.observability.tool_logging.TOOL_CALL_LOG", tool_log)

    def boom(**kwargs):
        raise RuntimeError("index unavailable")

    monkeypatch.setattr(rag_tool, "retrieve_policy", boom)
    with pytest.raises(RuntimeError, match="index unavailable"):
        rag_tool.retrieve_policy_tool(query="x", product_domain="MORTGAGE")

    records = read_log(tool_log)
    assert records and records[-1]["status"] == "ERROR"
    assert "index unavailable" in records[-1]["error"]
    assert records[-1]["tool_name"] == rag_tool.TOOL_NAME


# ================================================================ the other tools


def test_resolve_citation_contract():
    from src.config import get_config
    from src.rag.citations import CitationResolver

    resolver = CitationResolver(get_config())

    resolves, reason = resolver.resolve("POL-DTI-001 v2.0 rule DTI-CONV-001")
    assert resolves is True and reason.startswith("resolves to synthetic_data/")

    resolves, reason = resolver.resolve("POL-DTI-001 v2.0 rule DTI-FAKE-999")
    assert resolves is False and "does not appear" in reason

    # An unparseable citation is a clean False, not an exception.
    resolves, reason = resolver.resolve("not a citation at all")
    assert resolves is False and "grammar" in reason


def test_list_policy_rules_contract():
    summary = rag_tool.policy_corpus_summary()
    assert set(summary["products"]) == {"mortgage", "education"}
    for product in summary["products"].values():
        assert product["document_count"] > 0
        assert product["declared_rule_count"] > 0
        for policy in product["policies"]:
            assert policy["policy_id"]
            assert isinstance(policy["rule_ids"], list)
    assert summary["embedding_model"] and summary["reranker_model"]


def test_the_langchain_tool_exposes_the_declared_schema():
    tool = rag_tool.build_langchain_tool()
    assert tool.name == rag_tool.TOOL_NAME
    assert tool.args_schema is rag_tool.RetrievePolicyInput
    assert "MORTGAGE" in tool.description and "EDUCATION_LOAN" in tool.description


def test_tool_names_reconcile_between_code_and_mcp_server(repo_root):
    """REQ-050: the names in the log must match the names in the code."""
    server = (repo_root / "mcp_server" / "server.py").read_text(encoding="utf-8")
    assert f'name="{rag_tool.TOOL_NAME}"' in server
    for name in ("resolve_citation", "list_policy_rules"):
        assert f'name="{name}"' in server


@pytest.mark.slow
def test_logged_tool_names_reconcile_with_the_code(repo_root):
    from src.observability.tool_logging import read_log

    records = read_log(repo_root / "logs" / "tool_calls.jsonl")
    if not records:
        pytest.skip("no tool log written yet")
    logged = {r["tool_name"] for r in records}
    known = {rag_tool.TOOL_NAME, "resolve_citation", "list_policy_rules"}
    assert logged <= known, f"log contains unknown tools: {logged - known}"
