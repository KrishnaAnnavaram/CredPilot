"""Routing-logic tests (REQ-094).

*"asserts conditional edges route the right worker for given states"*

Routing in CredPilot carries more weight than usual, because one of the routes
decides **which body of lending law applies**. A mortgage file routed to the
education branch would be assessed against cosigner rules and school
certification; the answer would be confidently wrong and every citation in it
would resolve. So these tests check the edge functions directly against
hand-built states — no retrieval, no models, no index — and then check the
compiled graph agrees.
"""

from __future__ import annotations

import uuid

import pytest

from src.domain import LendingProductDomain
from src.graph import (
    build_graph,
    initial_state,
    route_after_domain,
    route_after_narrative,
    route_after_recommendation,
    route_after_retrieval,
    route_after_supervisor,
)


# ------------------------------------------------------------------ edge functions


def test_supervisor_always_routes_to_the_domain_router():
    """Product resolution happens before anything reads a corpus."""
    for state in ({}, {"route": "anything"}, {"requires_human_review": True}):
        assert route_after_supervisor(state) == "domain_router"


def test_an_unresolved_product_routes_to_human_review():
    """A file whose product cannot be established is escalated, never guessed."""
    assert route_after_domain({"route": "human_review"}) == "human_review"


def test_a_resolved_product_routes_to_policy_retrieval():
    assert route_after_domain({"route": "policy_retrieval"}) == "policy_retrieval"
    assert route_after_domain({"loan_domain": "MORTGAGE"}) == "policy_retrieval"


def test_retrieval_with_no_evidence_routes_to_human_review():
    """No policy evidence means no basis to assess, so a human takes it."""
    assert route_after_retrieval({"route": "human_review"}) == "human_review"


def test_retrieval_with_evidence_routes_to_eligibility():
    assert route_after_retrieval({"route": "eligibility"}) == "eligibility"


def test_every_decided_file_gets_a_rationale_including_a_referred_one():
    """The reviewer picking up a referred file needs the reasoning most.

    So the narrative sits between the recommendation and the handoff rather than
    being skipped when a human is going to look anyway.
    """
    assert route_after_recommendation({"requires_human_review": True}) == "narrative"
    assert route_after_recommendation({"requires_human_review": False}) == "narrative"
    assert route_after_recommendation({}) == "narrative"


def test_a_halted_run_skips_the_rationale():
    """There is nothing to narrate: the run stopped before reaching a decision."""
    assert route_after_recommendation({"halted": True}) == "human_review"


def test_a_file_needing_review_routes_there_after_the_rationale():
    assert route_after_narrative({"requires_human_review": True}) == "human_review"


def test_a_clean_file_ends():
    assert route_after_narrative({"requires_human_review": False}) == "__end__"
    assert route_after_narrative({}) == "__end__"


@pytest.mark.parametrize(
    "state,expected",
    [
        ({"requires_human_review": True, "route": "done"}, "human_review"),
        ({"requires_human_review": False, "route": "human_review"}, "__end__"),
    ],
)
def test_the_review_flag_governs_the_final_edge_not_the_route_field(state, expected):
    """Two fields could disagree; the flag is the one that decides."""
    assert route_after_narrative(state) == expected


# ------------------------------------------------------------- the compiled graph


def test_the_graph_declares_the_expected_nodes_and_edges(indexes_built, tmp_path):
    if not indexes_built:
        pytest.skip("indexes not built")
    graph, context = build_graph(checkpoint_path=tmp_path / "routing.sqlite")
    try:
        drawn = graph.get_graph()
        nodes = set(drawn.nodes)
        assert {"supervisor", "domain_router", "policy_retrieval"} <= nodes
        assert {"eligibility", "risk", "recommendation", "narrative", "human_review"} <= nodes

        edges = {(e.source, e.target) for e in drawn.edges}
        assert ("supervisor", "domain_router") in edges
        assert ("domain_router", "policy_retrieval") in edges
        assert ("domain_router", "human_review") in edges
        assert ("policy_retrieval", "eligibility") in edges
        assert ("policy_retrieval", "human_review") in edges
        assert ("eligibility", "risk") in edges
        assert ("risk", "recommendation") in edges
        assert ("recommendation", "narrative") in edges
        assert ("narrative", "human_review") in edges
    finally:
        if context is not None:
            context.__exit__(None, None, None)


# --------------------------------------------------- routing to the right product


@pytest.mark.parametrize(
    "application,expected",
    [
        ("synthetic_data/mortgage/applications/APP-000001.json", "MORTGAGE"),
        ("synthetic_data/mortgage/applications/APP-000056.json", "MORTGAGE"),
        ("synthetic_data/education/applications/APP-2026-00001.json", "EDUCATION_LOAN"),
        ("synthetic_data/education/applications/APP-2026-00037.json", "EDUCATION_LOAN"),
    ],
)
def test_an_application_routes_to_its_own_product(repo_root, application, expected):
    """Checked on the packet itself, before any graph or index is involved."""
    from src.domain import resolve_product_domain
    from src.application_context import build_underwriting_input

    packet = build_underwriting_input(repo_root / application)
    resolved = resolve_product_domain(
        application_id=packet.get("application_id"), packet=packet
    )
    assert resolved is LendingProductDomain.from_any(expected)


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.parametrize(
    "application,expected_domain,expected_worker_path",
    [
        (
            "synthetic_data/mortgage/applications/APP-000001.json",
            "MORTGAGE",
            ["supervisor", "domain_router", "policy_retrieval", "eligibility", "risk"],
        ),
        (
            "synthetic_data/education/applications/APP-2026-00001.json",
            "EDUCATION_LOAN",
            ["supervisor", "domain_router", "policy_retrieval", "eligibility", "risk"],
        ),
    ],
)
def test_the_graph_visits_the_right_workers_in_order(
    indexes_built, tmp_path, repo_root, application, expected_domain, expected_worker_path
):
    if not indexes_built:
        pytest.skip("indexes not built")
    graph, context = build_graph(checkpoint_path=tmp_path / "routing2.sqlite")
    try:
        result = graph.invoke(
            initial_state(repo_root / application),
            config={"configurable": {"thread_id": f"route-{uuid.uuid4().hex[:8]}"}},
        )
        assert result["loan_domain"] == expected_domain
        assert result["steps"][: len(expected_worker_path)] == expected_worker_path
        # And the evidence it gathered belongs to that product only.
        assert {e["product_domain"] for e in result["policy_evidence"]} == {expected_domain}
    finally:
        if context is not None:
            context.__exit__(None, None, None)


@pytest.mark.slow
@pytest.mark.integration
def test_a_decline_is_routed_to_a_human(indexes_built, tmp_path, repo_root):
    """POL-DEC-001 DEC-REC-002: never auto-decided."""
    if not indexes_built:
        pytest.skip("indexes not built")
    graph, context = build_graph(checkpoint_path=tmp_path / "routing3.sqlite")
    try:
        result = graph.invoke(
            initial_state(repo_root / "synthetic_data/mortgage/applications/APP-000056.json"),
            config={"configurable": {"thread_id": f"decline-{uuid.uuid4().hex[:8]}"}},
        )
        assert result["recommendation"]["outcome"] == "DECLINE_RECOMMENDATION"
        assert result["requires_human_review"] is True
        assert result["steps"][-1] == "human_review"
    finally:
        if context is not None:
            context.__exit__(None, None, None)


@pytest.mark.slow
@pytest.mark.integration
def test_an_adversarial_file_is_routed_for_review(indexes_built, tmp_path, repo_root):
    """Applicant text that tries to steer the system escalates it instead."""
    if not indexes_built:
        pytest.skip("indexes not built")
    graph, context = build_graph(checkpoint_path=tmp_path / "routing4.sqlite")
    try:
        result = graph.invoke(
            initial_state(repo_root / "synthetic_data/mortgage/applications/APP-000065.json"),
            config={"configurable": {"thread_id": f"adv-{uuid.uuid4().hex[:8]}"}},
        )
        assert result["security_findings"]
        assert result["requires_human_review"] is True
        assert "human_review" in result["steps"]
        # It was still assessed — the attack did not move the product or the date.
        assert result["loan_domain"] == "MORTGAGE"
        assert result["policy_evidence"]
    finally:
        if context is not None:
            context.__exit__(None, None, None)
