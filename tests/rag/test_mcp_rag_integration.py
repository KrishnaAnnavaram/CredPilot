"""Real MCP consumption of the retrieval tool.

The server is launched as a subprocess over stdio and its tools are loaded
through ``langchain-mcp-adapters`` — the integration the stack requires, and the
only one that proves the server works as a server rather than as an import.

Each test opens its own session and does all of its work inside a single
coroutine. The stdio transport is built on anyio task groups, which must be
entered and exited from the same task; a session held open across separate
``run_until_complete`` calls deadlocks instead of failing, which is how this file
was first written and why it is now written this way.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

import pytest

pytestmark = [pytest.mark.integration, pytest.mark.slow]


def unwrap(payload: Any) -> Any:
    """MCP tool output arrives as JSON text, or as a list of content blocks."""
    if isinstance(payload, str):
        return json.loads(payload)
    if isinstance(payload, dict) and "text" not in payload:
        return payload
    if isinstance(payload, list):
        for part in payload:
            if isinstance(part, str):
                return json.loads(part)
            text = part.get("text") if isinstance(part, dict) else getattr(part, "text", None)
            if text:
                return json.loads(text)
    raise AssertionError(f"could not unwrap MCP payload: {payload!r}")


def with_surface(body):
    """Run ``body(surface)`` inside one session, on one task."""
    from mcp_server.client import load_surface, open_session

    async def runner():
        async with open_session() as session:
            surface = await load_surface(session)
            return await body(surface)

    return asyncio.run(runner())


def tool_named(surface, name):
    return next(t for t in surface.tools if t.name == name)


async def call(surface, name, arguments):
    return unwrap(await tool_named(surface, name).ainvoke(arguments))


@pytest.fixture(autouse=True)
def _require_indexes(indexes_built):
    if not indexes_built:
        pytest.skip("indexes not built; run 'python scripts/build_policy_indexes.py'")


# ------------------------------------------------------------------------- the surface


def test_the_server_exposes_the_required_surface():
    """At least two tools and one resource, with the expected names."""

    async def body(surface):
        from src.tools.rag_tool import TOOL_NAME

        assert len(surface.tools) >= 2, surface.tool_names
        assert len(surface.resources) >= 1, surface.resource_uris
        assert set(surface.tool_names) >= {
            "retrieve_policy",
            "resolve_citation",
            "list_policy_rules",
        }
        assert set(surface.resource_uris) >= {
            "credpilot://policies/mortgage",
            "credpilot://policies/education",
        }
        # Tool names reconcile with the code that implements them.
        assert TOOL_NAME in surface.tool_names
        return True

    assert with_surface(body)


# ---------------------------------------------------------------------------- retrieval


def test_retrieval_over_mcp_serves_both_products_in_isolation():
    """Both products retrieve, and neither can reach the other's corpus."""

    async def body(surface):
        mortgage = await call(
            surface,
            "retrieve_policy",
            {
                "query": "What is the maximum back-end debt-to-income ratio?",
                "application_id": "APP-000056",
                "as_of_date": "2026-07-08",
                "top_k": 5,
            },
        )
        assert mortgage["status"] == "FOUND"
        assert mortgage["product_domain"] == "MORTGAGE"
        assert any(e["rule_id"] == "DTI-CONV-001" for e in mortgage["evidence"])
        assert all(e["citation_resolves"] for e in mortgage["evidence"])
        assert all(
            e["source_path"].startswith("synthetic_data/mortgage/") for e in mortgage["evidence"]
        )

        education = await call(
            surface,
            "retrieve_policy",
            {
                "query": "Does this borrower require a cosigner?",
                "application_id": "APP-2026-00001",
                "as_of_date": "2026-08-01",
                "top_k": 5,
            },
        )
        assert education["status"] == "FOUND"
        assert education["product_domain"] == "EDUCATION_LOAN"
        assert all(e["citation_resolves"] for e in education["evidence"])
        assert all(
            e["source_path"].startswith("synthetic_data/education/")
            for e in education["evidence"]
        )

        # Bait each product with the other's vocabulary.
        baited_mortgage = await call(
            surface,
            "retrieve_policy",
            {
                "query": "What cost of attendance and cosigner rules apply to an undergraduate?",
                "product_domain": "MORTGAGE",
                "as_of_date": "2026-08-12",
            },
        )
        assert all(
            e["source_path"].startswith("synthetic_data/mortgage/")
            for e in baited_mortgage["evidence"]
        )

        baited_education = await call(
            surface,
            "retrieve_policy",
            {
                "query": "What is the maximum loan-to-value on a cash-out refinance?",
                "product_domain": "EDUCATION_LOAN",
                "as_of_date": "2026-08-01",
            },
        )
        assert all(
            e["source_path"].startswith("synthetic_data/education/")
            for e in baited_education["evidence"]
        )
        return True

    assert with_surface(body)


def test_temporal_selection_and_clarification_hold_over_mcp():
    """Version selection survives the boundary, and ambiguity still escalates."""

    async def body(surface):
        query = "What is the maximum back-end debt-to-income ratio?"
        before = await call(
            surface,
            "retrieve_policy",
            {"query": query, "product_domain": "MORTGAGE", "as_of_date": "2026-06-25"},
        )
        after = await call(
            surface,
            "retrieve_policy",
            {"query": query, "product_domain": "MORTGAGE", "as_of_date": "2026-07-08"},
        )
        before_rule = next(e for e in before["evidence"] if e["rule_id"] == "DTI-CONV-001")
        after_rule = next(e for e in after["evidence"] if e["rule_id"] == "DTI-CONV-001")
        assert before_rule["policy_version"] == "1.0"
        assert after_rule["policy_version"] == "2.0"
        assert before_rule["citation"] == "POL-DTI-001 v1.0 rule DTI-CONV-001"
        assert after_rule["citation"] == "POL-DTI-001 v2.0 rule DTI-CONV-001"

        ambiguous = await call(surface, "retrieve_policy", {"query": "What is the DTI limit?"})
        assert ambiguous["status"] == "PRODUCT_CLARIFICATION_REQUIRED"
        assert ambiguous["evidence"] == []
        return True

    assert with_surface(body)


# --------------------------------------------------------------------- the other tools


def test_the_supporting_tools_work_over_mcp():
    """Citation resolution and rule enumeration, across the boundary."""

    async def body(surface):
        good = await call(
            surface, "resolve_citation", {"citation": "POL-DTI-001 v2.0 rule DTI-CONV-001"}
        )
        assert good["resolves"] is True
        assert good["product_domain"] == "MORTGAGE"
        assert good["reason"].startswith("resolves to synthetic_data/")

        bad = await call(
            surface, "resolve_citation", {"citation": "POL-DTI-001 v2.0 rule DTI-FAKE-999"}
        )
        assert bad["resolves"] is False
        assert "does not appear" in bad["reason"]

        one = await call(
            surface,
            "list_policy_rules",
            {"product_domain": "EDUCATION_LOAN", "policy_id": "POL-004"},
        )
        assert one["policy_count"] == 1
        assert {"EDU-COS-001", "EDU-COS-004"} <= set(one["policies"][0]["rule_ids"])

        whole = await call(surface, "list_policy_rules", {"product_domain": "MORTGAGE"})
        assert whole["policy_count"] == 42
        assert whole["rule_count"] == 203
        return True

    assert with_surface(body)


# --------------------------------------------------------------------------- transcript


def test_the_mcp_transcript_is_machine_generated(repo_root):
    """The committed tool-call transcript is written by the server, not by hand."""
    from src.observability.tool_logging import read_log

    transcript = repo_root / "logs" / "mcp_transcript.jsonl"
    before = len(read_log(transcript))

    async def body(surface):
        await call(surface, "resolve_citation", {"citation": "POL-002 EDU-UW-001"})
        return True

    assert with_surface(body)

    records = read_log(transcript)
    assert len(records) > before, "the server wrote no new transcript records"
    for record in records:
        assert record["direction"] in ("request", "response")
        assert "timestamp" in record and "method" in record
    assert any(r["method"].startswith("tools/call:") for r in records)
