"""The graph actually uses the retriever, and uses it correctly.

Agentic-RAG means retrieval-in-the-loop: the Policy Retrieval Agent decides which
policy questions a file raises and issues one targeted retrieval per question.
These tests check that the graph does that for both products, that the product is
resolved before any retrieval happens, and that the decision the graph reaches is
the one the retrieved policy supports.
"""

from __future__ import annotations

import uuid

import pytest

from src.domain import LendingProductDomain
from src.graph import (
    EDUCATION_QUESTIONS,
    MAX_DEPENDENCY_FOLLOWS,
    MORTGAGE_QUESTIONS,
    build_graph,
    initial_state,
    plan_policy_questions,
    state_evidence,
)

pytestmark = [pytest.mark.integration, pytest.mark.slow]


@pytest.fixture(scope="module")
def graph(indexes_built, tmp_path_factory):
    if not indexes_built:
        pytest.skip("indexes not built")
    checkpoint = tmp_path_factory.mktemp("checkpoints") / "test.sqlite"
    compiled, context = build_graph(checkpoint_path=checkpoint)
    yield compiled
    if context is not None:
        context.__exit__(None, None, None)


def run(graph, path, **kwargs):
    state = initial_state(path, **kwargs)
    thread = f"{state['application_id']}-{uuid.uuid4().hex[:8]}"
    return graph.invoke(state, config={"configurable": {"thread_id": thread}})


# ------------------------------------------------------------------- question planning


def test_questions_are_planned_from_the_file_not_fixed():
    """A cash-out jumbo asks more questions than a plain salaried purchase."""
    plain = plan_policy_questions(
        LendingProductDomain.MORTGAGE,
        {"loan_purpose": "purchase", "product_family": "conventional_conforming"},
    )
    complex_file = plan_policy_questions(
        LendingProductDomain.MORTGAGE,
        {
            "loan_purpose": "cash_out_refinance",
            "product_family": "jumbo",
            "declared_income": [{"income_type": "self_employed"}],
            "untrusted_applicant_text": {"content": "x"},
        },
    )
    assert len(plain) == len(MORTGAGE_QUESTIONS)
    assert len(complex_file) > len(plain)
    topics = {q["topic"] for q in complex_file}
    assert {"cash_out", "jumbo", "income_self_employed", "security"} <= topics


def test_education_questions_adapt_to_the_product():
    base = plan_policy_questions(LendingProductDomain.EDUCATION_LOAN, {"product_code": "UG"})
    international = plan_policy_questions(
        LendingProductDomain.EDUCATION_LOAN, {"product_code": "INTL"}
    )
    refinance = plan_policy_questions(
        LendingProductDomain.EDUCATION_LOAN, {"product_code": "REFI"}
    )
    assert len(base) == len(EDUCATION_QUESTIONS)
    assert "international" in {q["topic"] for q in international}
    assert "refinance" in {q["topic"] for q in refinance}


def test_the_two_products_ask_different_questions():
    mortgage = {q["topic"] for q in MORTGAGE_QUESTIONS}
    education = {q["topic"] for q in EDUCATION_QUESTIONS}
    assert mortgage != education
    assert "leverage" in mortgage and "leverage" not in education
    assert "cosigner" in education and "cosigner" not in mortgage


# --------------------------------------------------------------------------- the graph


def test_the_graph_declares_a_supervisor_and_at_least_three_workers(graph):
    nodes = set(graph.get_graph().nodes)
    assert "supervisor" in nodes
    workers = {"policy_retrieval", "eligibility", "risk", "recommendation"}
    assert workers <= nodes
    assert "domain_router" in nodes


def test_a_mortgage_application_runs_end_to_end(graph, repo_root):
    result = run(graph, repo_root / "synthetic_data/mortgage/applications/APP-000001.json")

    assert result["loan_domain"] == "MORTGAGE"
    assert result["steps"][:4] == [
        "supervisor",
        "domain_router",
        "policy_retrieval",
        "eligibility",
    ]
    evidence = state_evidence(result)
    assert evidence, "the graph reached a decision with no policy evidence"
    assert all(e["citation_resolves"] for e in evidence)
    assert all(e["product_domain"] == "MORTGAGE" for e in evidence)
    assert result["recommendation"]["outcome"]


def test_an_education_application_runs_end_to_end(graph, repo_root):
    result = run(graph, repo_root / "synthetic_data/education/applications/APP-2026-00001.json")

    assert result["loan_domain"] == "EDUCATION_LOAN"
    evidence = state_evidence(result)
    assert evidence
    assert all(e["product_domain"] == "EDUCATION_LOAN" for e in evidence)
    assert all(e["citation_resolves"] for e in evidence)
    assert result["calculations"]["product_domain"] == "EDUCATION_LOAN"


def test_the_graph_retrieves_once_per_planned_question(graph, repo_root):
    """Every planned question is asked, and nothing else is asked speculatively.

    The statuses also carry ``dependency:<RULE>:<STATUS>`` entries from the
    second pass, which follows the rules the first pass's evidence references —
    see test_dependency_following.py. Those are separated out here rather than
    folded into the planned set, so this test still fails if a planned question
    is skipped.
    """
    result = run(graph, repo_root / "synthetic_data/education/applications/APP-2026-00002.json")

    planned = {q["topic"] for q in result["policy_questions"]}
    statuses = result["retrieval_statuses"]
    dependency = [s for s in statuses if s.startswith("dependency:")]
    asked = {s.split(":")[0] for s in statuses if not s.startswith("dependency:")}

    assert asked == planned
    assert all(s.endswith(":FOUND") for s in statuses if not s.startswith("dependency:"))
    # Dependency follows are extra, bounded, and also succeed.
    assert all(s.endswith(":FOUND") for s in dependency)
    assert len(dependency) <= MAX_DEPENDENCY_FOLLOWS


def test_evidence_never_mixes_products(graph, repo_root):
    for path, expected in (
        ("synthetic_data/mortgage/applications/APP-000056.json", "MORTGAGE"),
        ("synthetic_data/education/applications/APP-2026-00037.json", "EDUCATION_LOAN"),
    ):
        result = run(graph, repo_root / path)
        evidence = state_evidence(result)
        assert {e["product_domain"] for e in evidence} == {expected}
        corpus = "mortgage" if expected == "MORTGAGE" else "education"
        assert all(f"/{corpus}/" in e["source_path"] for e in evidence)


# ------------------------------------------------------- the boundary triple, end to end


@pytest.mark.parametrize(
    "application_id,as_of,version,eligibility,outcome",
    [
        ("APP-000055", "2026-06-25", "1.0", "ELIGIBLE", "REFER_RECOMMENDATION"),
        ("APP-000056", "2026-07-08", "2.0", "INELIGIBLE", "DECLINE_RECOMMENDATION"),
        ("APP-000057", "2026-07-08", "2.0", "ELIGIBLE", "APPROVE_RECOMMENDATION"),
    ],
)
def test_the_same_ratio_decides_three_ways(
    graph, repo_root, application_id, as_of, version, eligibility, outcome
):
    """44% back-end DTI, three files, three different outcomes.

    The ratio is identical in all three. What differs is which policy version
    retrieval returned for the file's as-of date, and what the file documents.

    The pair worth reading closely is 55 and 57, because both sit at 44% under a
    45% ceiling and they do not land in the same place:

    * **APP-000055** (v1.0) — 45% *is* the programme limit, so 44% is one point
      short of it. ``UWR-HRV-001`` makes an affordability result within two
      percentage points of its limit a mandatory human-review trigger, so the
      file is eligible and still referred. Eligible and referred are not in
      tension; referral is a routing decision, not a verdict.
    * **APP-000057** (v2.0) — the programme limit is 43% and 45% is an extension
      earned on two documented compensating factors. The borderline test reads
      the tighter of the two, so this file is measured against 43% — which it is
      already past, not approaching — and no trigger fires.

    A file that clears only on a concession is nearer a policy edge than its
    applied threshold suggests; a file clearing the programme limit by a point is
    genuinely borderline. The two are different situations and get different
    answers.
    """
    result = run(graph, repo_root / f"synthetic_data/mortgage/applications/{application_id}.json")

    assert result["as_of_date"] == as_of
    assert result["calculations"]["ratios"]["back_end_dti"] == pytest.approx(0.44)

    dti_evidence = [
        e for e in state_evidence(result) if e["rule_id"] == "DTI-CONV-001"
    ]
    assert dti_evidence, f"{application_id}: DTI-CONV-001 was not retrieved"
    assert {e["policy_version"] for e in dti_evidence} == {version}

    assert result["eligibility"]["status"] == eligibility
    assert result["recommendation"]["outcome"] == outcome


def test_a_decline_is_always_routed_to_a_human(graph, repo_root):
    """POL-DEC-001 DEC-REC-002: never auto-decided."""
    result = run(graph, repo_root / "synthetic_data/mortgage/applications/APP-000056.json")
    assert result["recommendation"]["outcome"] == "DECLINE_RECOMMENDATION"
    assert result["requires_human_review"] is True
    assert any("DEC-REC-002" in r for r in result["human_review_reasons"])
    assert "human_review" in result["steps"]


def test_the_breach_names_the_threshold_it_failed(graph, repo_root):
    """AC-02: every breach is reported with the threshold it failed and its citation."""
    result = run(graph, repo_root / "synthetic_data/mortgage/applications/APP-000056.json")
    breaches = result["eligibility"]["breaches"]
    assert breaches, "a file at 44% against a 43% ceiling must report a breach"

    by_measure = {b["measure"]: b for b in breaches}
    breach = by_measure["back_end_dti"]
    assert breach["observed"] == pytest.approx(0.44)
    assert breach["threshold"] == pytest.approx(0.43)
    assert breach["citation"] == "POL-DTI-001 v2.0 rule DTI-CONV-001"
    assert breach["rule_id"] == "DTI-CONV-001"

    # Every breach, not just the first, carries what a reviewer needs to check it.
    for measure, item in by_measure.items():
        assert item["citation"], f"{measure} breached with no citation"
        assert item["threshold"] is not None, f"{measure} breached with no threshold"
        assert item["rule_id"], f"{measure} breached with no rule id"


def test_a_second_rule_can_breach_on_the_same_file(graph, repo_root):
    """Breaches compound, and each is reported on its own terms.

    APP-000056 fails its DTI ceiling at 44%. That same 44% also trips the v2.0
    reserve rule, which adds two months of required reserves above a 43%
    back-end DTI — so one ratio breaches two rules, for two different reasons,
    and the file reports both rather than stopping at the first.
    """
    result = run(graph, repo_root / "synthetic_data/mortgage/applications/APP-000056.json")
    measures = {b["measure"] for b in result["eligibility"]["breaches"]}
    assert "back_end_dti" in measures
    assert "months_of_reserves" in measures

    reserves = next(
        b for b in result["eligibility"]["breaches"] if b["measure"] == "months_of_reserves"
    )
    assert reserves["rule_id"] == "AST-RSV-002"
    assert reserves["baseline_threshold"] == pytest.approx(0.0), (
        "the occupancy base should still be visible beneath the risk-based addition"
    )
    assert reserves["threshold"] > reserves["baseline_threshold"]
    assert "back-end DTI" in reserves["detail"]


def test_the_extension_names_each_compensating_factor(graph, repo_root):
    """DTI-CONV-003: a factor must be documented and named, not asserted."""
    result = run(graph, repo_root / "synthetic_data/mortgage/applications/APP-000057.json")
    evaluation = result["eligibility"]["evaluations"][0]
    assert evaluation["threshold"] == pytest.approx(0.45)
    assert len(evaluation["compensating_factors"]) >= 2
    joined = " ".join(evaluation["compensating_factors"])
    assert "reserves" in joined and "credit score" in joined
    assert "DTI-CONV-003" in evaluation["detail"]


def test_thresholds_come_from_retrieval_not_from_code(repo_root):
    """Remove the retrieved rule and the engine reports INDETERMINATE.

    This is the test that proves retrieval is load-bearing: with no policy in
    hand the system does not fall back to a hardcoded 43%, and it does not treat
    the absence as permission (GEN-ELG-005).
    """
    from src import rules
    from src.calculations import mortgage_affordability
    from src.application_context import build_underwriting_input

    packet = build_underwriting_input(
        repo_root / "synthetic_data/mortgage/applications/APP-000056.json"
    )
    calculations = mortgage_affordability(packet)

    evaluations = rules.evaluate(LendingProductDomain.MORTGAGE, calculations, packet, [])
    summary = rules.summarize(evaluations)
    assert summary["status"] == "INDETERMINATE"
    assert summary["breaches"] == []
    assert "not retrieved" in summary["indeterminate"][0]["detail"]


def test_a_changed_ceiling_changes_the_verdict(repo_root):
    """The threshold really is read out of the evidence, not baked in."""
    from src import rules
    from src.application_context import build_underwriting_input
    from src.calculations import mortgage_affordability

    packet = build_underwriting_input(
        repo_root / "synthetic_data/mortgage/applications/APP-000056.json"
    )
    calculations = mortgage_affordability(packet)

    permissive = [
        {
            "rule_id": "DTI-CONV-001",
            "citation": "POL-TEST-001 v1.0 rule DTI-CONV-001",
            "text": "| `max_back_end_dti` | 50% |",
        }
    ]
    # Scoped to the affordability rule: this evidence holds DTI-CONV-001 alone,
    # so a whole-file summary would be INDETERMINATE on the three knockouts that
    # were never retrieved — true, and not what this test is about.
    assert rules.summarize(
        rules.evaluate_mortgage_affordability(calculations, packet, permissive)
    )["status"] == "ELIGIBLE"

    strict = [
        {
            "rule_id": "DTI-CONV-001",
            "citation": "POL-TEST-001 v1.0 rule DTI-CONV-001",
            "text": "| `max_back_end_dti` | 30% |",
        }
    ]
    assert rules.summarize(
        rules.evaluate_mortgage_affordability(calculations, packet, strict)
    )["status"] == "INELIGIBLE"


# ------------------------------------------------------------------------- state shape


def test_the_state_carries_the_product_domain_and_the_evidence(graph, repo_root):
    result = run(graph, repo_root / "synthetic_data/mortgage/applications/APP-000001.json")
    assert result["loan_domain"] in {d.value for d in LendingProductDomain}
    assert isinstance(result["policy_evidence"], list)
    assert isinstance(result["policy_evidence"][0], dict), (
        "evidence must be checkpoint-safe plain data"
    )


def test_the_state_survives_the_checkpointer(graph, repo_root):
    """A checkpoint that cannot be read back is not a durable record."""
    import json

    state = initial_state(repo_root / "synthetic_data/education/applications/APP-2026-00001.json")
    thread = f"ckpt-{uuid.uuid4().hex[:8]}"
    config = {"configurable": {"thread_id": thread}}
    graph.invoke(state, config=config)

    restored = graph.get_state(config)
    assert restored.values["loan_domain"] == "EDUCATION_LOAN"
    assert restored.values["policy_evidence"]
    json.dumps(restored.values["policy_evidence"])


def test_untrusted_text_is_quarantined_before_routing(graph, repo_root):
    result = run(graph, repo_root / "synthetic_data/mortgage/applications/APP-000065.json")
    envelope = result["untrusted_applicant_text"]
    assert envelope["trust_class"] == "customer_evidence"
    assert envelope["injection_findings"]
    assert result["security_findings"]
    assert result["requires_human_review"] is True
    # It still got underwritten — the attack did not move the product or the date.
    assert result["loan_domain"] == "MORTGAGE"
    assert state_evidence(result)
