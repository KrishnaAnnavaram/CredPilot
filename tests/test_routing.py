"""Routing-logic tests (REQ-094).

*"asserts conditional edges route the right worker for given states"*

Routing in CredPilot carries more weight than usual, because one of the routes
decides **which body of lending law applies**. A mortgage file routed to the
education branch would be assessed against cosigner rules and school
certification; the answer would be confidently wrong and every citation in it
would resolve. So these tests check the edge functions directly against
hand-built states — no retrieval, no models, no index — and then check the
compiled graph agrees.

Since the Supervisor was introduced the graph carries two kinds of request
through the same edges: an application packet and a conversational turn. Both
are covered here, and so is the property the topology exists to guarantee — that
**no edge connects a mortgage node to an education node**, so no sequence of
routing decisions can send a file to the wrong corpus.
"""

from __future__ import annotations

import uuid

import pytest

from src.domain import LendingProductDomain
from src.graph import (
    build_graph,
    conversation_state,
    initial_state,
    route_after_clarification,
    route_after_domain,
    route_after_narrative,
    route_after_recommendation,
    route_after_retrieval,
    route_after_supervisor,
)
from src.supervisor import Route


# ------------------------------------------------------------------ edge functions


@pytest.mark.parametrize(
    "route,expected",
    [
        (Route.GENERAL.value, "general_response"),
        (Route.CLARIFY.value, "clarification"),
        (Route.MORTGAGE.value, "mortgage_agent"),
        (Route.EDUCATION_LOAN.value, "education_agent"),
        (Route.HUMAN_REVIEW.value, "human_review"),
        (Route.OUT_OF_SCOPE.value, "safe_response"),
    ],
)
def test_each_supervisor_route_has_its_own_target(route, expected):
    """Six routes, six destinations, no overlap."""
    assert route_after_supervisor({"route": route}) == expected


def test_an_unrecognized_route_asks_rather_than_guesses():
    """The safe default is a question, not a product."""
    assert route_after_supervisor({}) == "clarification"
    assert route_after_supervisor({"route": "nonsense"}) == "clarification"


def test_a_halted_run_goes_to_a_human_whatever_it_was_routed_to():
    assert route_after_supervisor({"route": Route.MORTGAGE.value, "halted": True}) \
        == "human_review"


def test_an_unresolved_product_routes_to_human_review():
    """A file whose product cannot be established is escalated, never guessed."""
    assert route_after_domain({"route": "human_review"}) == "human_review"


def test_a_resolved_product_routes_to_its_own_retrieval_node():
    assert route_after_domain({"loan_domain": "MORTGAGE"}) == "mortgage_policy_retrieval"
    assert route_after_domain({"loan_domain": "EDUCATION_LOAN"}) \
        == "education_policy_retrieval"


def test_retrieval_with_no_evidence_routes_to_human_review():
    """No policy evidence means no basis to assess, so a human takes it."""
    assert route_after_retrieval({"route": "human_review"}) == "human_review"


def test_retrieval_with_evidence_routes_to_its_own_eligibility_node():
    assert route_after_retrieval({"loan_domain": "MORTGAGE"}) == "mortgage_eligibility"
    assert route_after_retrieval({"loan_domain": "EDUCATION_LOAN"}) \
        == "education_eligibility"


def test_a_policy_question_skips_the_assessment_nodes():
    """There is no application to assess, so eligibility has nothing to decide."""
    from src.graph import MODE_POLICY_QUESTION

    assert route_after_retrieval(
        {"loan_domain": "MORTGAGE", "workflow_mode": MODE_POLICY_QUESTION}
    ) == "final_response"


def test_a_clarified_thread_goes_back_to_the_supervisor():
    """The answer is re-routed with the original question, not acted on alone."""
    assert route_after_clarification({}) == "supervisor"
    assert route_after_clarification({"halted": True}) == "human_review"


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


def test_a_clean_file_goes_straight_to_the_response():
    assert route_after_narrative({"requires_human_review": False}) == "final_response"
    assert route_after_narrative({}) == "final_response"


@pytest.mark.parametrize(
    "state,expected",
    [
        ({"requires_human_review": True, "route": "done"}, "human_review"),
        ({"requires_human_review": False, "route": "human_review"}, "final_response"),
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
        assert {"intake", "input_guardrails", "supervisor"} <= nodes
        assert {"general_response", "clarification", "safe_response"} <= nodes
        assert {"final_response", "output_guardrails", "human_review", "narrative"} <= nodes
        for product in ("mortgage", "education"):
            assert {
                f"{product}_agent",
                f"{product}_policy_retrieval",
                f"{product}_eligibility",
                f"{product}_risk",
                f"{product}_recommendation",
            } <= nodes, product

        edges = {(e.source, e.target) for e in drawn.edges}
        assert ("intake", "input_guardrails") in edges
        assert ("input_guardrails", "supervisor") in edges
        assert ("supervisor", "mortgage_agent") in edges
        assert ("supervisor", "education_agent") in edges
        assert ("supervisor", "general_response") in edges
        assert ("supervisor", "clarification") in edges
        assert ("supervisor", "safe_response") in edges
        assert ("clarification", "supervisor") in edges
        assert ("narrative", "human_review") in edges
        assert ("final_response", "output_guardrails") in edges
        for product in ("mortgage", "education"):
            assert (f"{product}_agent", f"{product}_policy_retrieval") in edges
            assert (f"{product}_policy_retrieval", f"{product}_eligibility") in edges
            assert (f"{product}_eligibility", f"{product}_risk") in edges
            assert (f"{product}_risk", f"{product}_recommendation") in edges
            assert (f"{product}_recommendation", "narrative") in edges
    finally:
        if context is not None:
            context.__exit__(None, None, None)


def test_no_edge_crosses_between_the_two_products(indexes_built, tmp_path):
    """Product isolation is a property of the topology, not of a condition.

    A shared worker node guarded by ``if domain is MORTGAGE`` is only as good as
    that condition staying correct. Two chains that share no node cannot be got
    wrong: there is no sequence of routing decisions that reaches education
    retrieval from a mortgage node, because no such edge exists.
    """
    if not indexes_built:
        pytest.skip("indexes not built")
    graph, context = build_graph(checkpoint_path=tmp_path / "isolation.sqlite")
    try:
        edges = {(e.source, e.target) for e in graph.get_graph().edges}
        crossings = [
            (source, target)
            for source, target in edges
            if ("mortgage" in source and "education" in target)
            or ("education" in source and "mortgage" in target)
        ]
        assert crossings == [], f"an edge crosses products: {crossings}"
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
            ["intake", "input_guardrails", "supervisor", "mortgage_agent",
             "mortgage_policy_retrieval", "mortgage_eligibility", "mortgage_risk"],
        ),
        (
            "synthetic_data/education/applications/APP-2026-00001.json",
            "EDUCATION_LOAN",
            ["intake", "input_guardrails", "supervisor", "education_agent",
             "education_policy_retrieval", "education_eligibility", "education_risk"],
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
        # It ended through the response path, not by falling off an edge.
        assert result["steps"][-1] == "output_guardrails"
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
        # human_review sits before the response is assembled, so the reviewer
        # gets the figures and the rationale rather than a bare referral.
        assert "human_review" in result["steps"]
        assert result["steps"].index("human_review") < result["steps"].index("final_response")
        assert "human review" in result["final_response"]["text"].lower()
    finally:
        if context is not None:
            context.__exit__(None, None, None)


@pytest.mark.slow
@pytest.mark.integration
def test_an_adversarial_file_is_routed_for_review(indexes_built, tmp_path, repo_root):
    """Applicant text that tries to steer the system escalates it instead.

    The file is still assessed. Refusing to underwrite a file because a hostile
    letter of explanation was attached to it would let the attacker stop the
    applicant's file from being read at all — so the attack changes where the
    result goes, not whether there is one.
    """
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
        assert result["recommendation"]["outcome"]
    finally:
        if context is not None:
            context.__exit__(None, None, None)


# ------------------------------------------------- the conversational path


@pytest.mark.integration
def test_a_greeting_never_reaches_retrieval(indexes_built, tmp_path):
    """The requirement, asserted on the path actually taken.

    ``general_response`` has no edge to any retrieval node, so this cannot be
    satisfied by a greeting that retrieves quickly — the nodes it visited are
    the evidence.
    """
    if not indexes_built:
        pytest.skip("indexes not built")
    graph, context = build_graph(checkpoint_path=tmp_path / "greet.sqlite")
    try:
        for greeting in ("hi", "hello", "thanks", "goodbye", "who are you"):
            result = graph.invoke(
                conversation_state(greeting),
                config={"configurable": {"thread_id": f"g-{uuid.uuid4().hex[:8]}"}},
            )
            steps = result["steps"]
            assert not any("retrieval" in step for step in steps), (greeting, steps)
            assert not result.get("policy_evidence"), greeting
            assert result["supervisor"]["route"] == Route.GENERAL.value, greeting
            assert result["answer"]
    finally:
        if context is not None:
            context.__exit__(None, None, None)


@pytest.mark.integration
def test_an_out_of_scope_request_is_refused_without_retrieval(indexes_built, tmp_path):
    if not indexes_built:
        pytest.skip("indexes not built")
    graph, context = build_graph(checkpoint_path=tmp_path / "oos.sqlite")
    try:
        result = graph.invoke(
            conversation_state("what is the weather in Paris tomorrow"),
            config={"configurable": {"thread_id": f"oos-{uuid.uuid4().hex[:8]}"}},
        )
        assert result["supervisor"]["route"] == Route.OUT_OF_SCOPE.value
        assert "safe_response" in result["steps"]
        assert not result.get("policy_evidence")
        assert not result["final_response"]["citations"]
    finally:
        if context is not None:
            context.__exit__(None, None, None)


def test_the_documented_node_count_matches_the_compiled_graph(tmp_path):
    """A figure in the README is a claim like any other.

    Both the README and the requirements mapping quoted 18 nodes while the
    graph compiled 20 — the two product chains had grown a node each and
    nobody re-counted. Asserting it here means the next person to add a node
    is told to update the prose rather than discovering the drift later.
    """
    import re
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[1]
    graph, context = build_graph(checkpoint_path=tmp_path / "nodecount.sqlite")
    try:
        nodes = {n for n in graph.get_graph().nodes if not n.startswith("__")}
    finally:
        if context is not None:
            context.__exit__(None, None, None)

    quoted = []
    for relative in ("README.md", "docs/rag/REQUIREMENTS_MAPPING.md"):
        text = (repo_root / relative).read_text(encoding="utf-8")
        for match in re.finditer(r"(\d+) nodes", text):
            quoted.append((relative, int(match.group(1))))

    assert quoted, "neither document states a node count any more"
    for relative, count in quoted:
        assert count == len(nodes), (
            f"{relative} says {count} nodes; the compiled graph has {len(nodes)}: "
            f"{sorted(nodes)}"
        )
