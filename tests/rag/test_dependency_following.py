"""The agent follows the rules its own evidence depends on.

A rule that says "at least two compensating factors from DTI-CONV-003" cannot be
applied without DTI-CONV-003. Retrieving the first and not the second used to
produce a confident, wrong answer: the engine reported "0 of 2 factors
documented" when the truth was that it had never seen what counts as a factor,
and a file that should have been approved was declined.

Two defences, tested here:

* the Policy Retrieval Agent issues a follow-up retrieval for every rule its
  evidence references but does not hold — retrieval-in-the-loop in the literal
  sense, the first answer raising the next question;
* the rule engine refuses to evaluate an extension whose defining rule is absent,
  reporting INDETERMINATE rather than a negative result (GEN-ELG-005).
"""

from __future__ import annotations

import uuid

import pytest

from src import rules
from src.domain import LendingProductDomain
from src.graph import (
    MAX_DEPENDENCY_FOLLOWS,
    build_graph,
    initial_state,
    referenced_rules,
    state_evidence,
)

pytestmark = [pytest.mark.integration, pytest.mark.slow]


# --------------------------------------------------------------- reference detection


def test_a_referenced_rule_is_detected():
    evidence = [
        {
            "rule_id": "DTI-CONV-001",
            "text": "extends to 45 percent where at least two compensating factors "
                    "from DTI-CONV-003 are documented",
        }
    ]
    assert referenced_rules(evidence) == ["DTI-CONV-003"]


def test_a_rule_already_held_is_not_refetched():
    evidence = [
        {"rule_id": "DTI-CONV-001", "text": "see DTI-CONV-003"},
        {"rule_id": "DTI-CONV-003", "text": "the recognised compensating factors"},
    ]
    assert referenced_rules(evidence) == []


def test_a_self_reference_is_not_a_dependency():
    assert referenced_rules([{"rule_id": "DTI-CONV-003", "text": "DTI-CONV-003 applies"}]) == []


def test_a_policy_id_is_not_a_rule():
    """`POL-AST-003` matches the same shape but names a document, not a rule."""
    evidence = [{"rule_id": "X-Y-001", "text": "See also POL-AST-003 and CRD-SCR-003."}]
    assert referenced_rules(evidence) == ["CRD-SCR-003"]


def test_education_references_are_detected():
    evidence = [{"rule_id": "EDU-UW-001", "text": "cosigner required per EDU-COS-001"}]
    assert referenced_rules(evidence) == ["EDU-COS-001"]


def test_references_are_deduplicated_and_ordered():
    evidence = [
        {"rule_id": "A-B-001", "text": "see CRD-SCR-003 and DTI-CONV-003"},
        {"rule_id": "A-B-002", "text": "see DTI-CONV-003 again"},
    ]
    assert referenced_rules(evidence) == ["CRD-SCR-003", "DTI-CONV-003"]


def test_the_reference_pattern_does_not_match_prose():
    for text in (
        "The borrower has a DTI of 44 percent.",
        "See section 4 of the policy.",
        "A 720 credit score is required.",
        "Reserves of 6 months, at LTV above 80%.",
    ):
        assert referenced_rules([{"rule_id": "X-Y-001", "text": text}]) == [], text


# ------------------------------------------------------------ the rule engine refuses


def test_the_extension_cannot_be_evaluated_without_its_defining_rule(mortgage_chunks):
    """DTI-CONV-001 alone is not enough to decide a file at 44%.

    Without DTI-CONV-003 the engine does not know what counts as a compensating
    factor. Reporting FAIL would decline a file because retrieval missed a rule.
    """
    chunks, _ = mortgage_chunks
    only_the_ceiling = [
        {
            "rule_id": c.rule_id,
            "policy_id": c.policy_id,
            "policy_version": c.policy_version,
            "citation": c.citation,
            "text": c.text,
        }
        for c in chunks
        if c.rule_id == "DTI-CONV-001" and c.policy_version == "2.0"
    ]
    assert len(only_the_ceiling) == 1

    evaluations = rules.evaluate(
        LendingProductDomain.MORTGAGE,
        {"ratios": {"back_end_dti": 0.44}, "amounts": {}, "months_of_reserves": 61.1},
        {"product_family": "conventional_conforming", "loan_purpose": "purchase"},
        only_the_ceiling,
    )
    summary = rules.summarize(evaluations)

    assert summary["status"] == "INDETERMINATE"
    assert summary["breaches"] == [], "a missing rule must never produce a breach"
    assert "DTI-CONV-003" in evaluations[0].detail
    assert "not retrieved" in evaluations[0].detail


def test_with_both_rules_the_extension_is_evaluated(mortgage_chunks):
    """The same file, with the dependency present, decides properly."""
    chunks, _ = mortgage_chunks
    both = [
        {
            "rule_id": c.rule_id,
            "policy_id": c.policy_id,
            "policy_version": c.policy_version,
            "citation": c.citation,
            "text": c.text,
        }
        for c in chunks
        if c.rule_id in ("DTI-CONV-001", "DTI-CONV-003") and c.policy_version == "2.0"
    ]
    assert len(both) == 2

    evaluations = rules.evaluate(
        LendingProductDomain.MORTGAGE,
        {"ratios": {"back_end_dti": 0.44, "ltv": 0.72}, "amounts": {}, "months_of_reserves": 61.1},
        {
            "product_family": "conventional_conforming",
            "loan_purpose": "purchase",
            "credit_summary": {"score_1": "732", "score_2": "744", "score_3": "750"},
        },
        both,
    )
    assert rules.summarize(evaluations)["status"] == "ELIGIBLE"
    assert evaluations[0].threshold == pytest.approx(0.45)
    assert len(evaluations[0].factors) >= 2


# ----------------------------------------------------------------- end to end


@pytest.fixture(scope="module")
def graph(indexes_built, tmp_path_factory):
    if not indexes_built:
        pytest.skip("indexes not built")
    compiled, context = build_graph(
        checkpoint_path=tmp_path_factory.mktemp("deps") / "checkpoints.sqlite"
    )
    yield compiled
    if context is not None:
        context.__exit__(None, None, None)


def _run(graph, repo_root, application_id):
    state = initial_state(
        repo_root / f"synthetic_data/mortgage/applications/{application_id}.json"
    )
    return graph.invoke(
        state,
        config={"configurable": {"thread_id": f"{application_id}-{uuid.uuid4().hex[:8]}"}},
    )


def test_the_graph_follows_dependencies(graph, repo_root):
    result = _run(graph, repo_root, "APP-000057")

    followed = [s for s in result["retrieval_statuses"] if s.startswith("dependency:")]
    assert followed, "no dependency retrieval was issued"
    assert len(result["policy_dependencies"]) <= MAX_DEPENDENCY_FOLLOWS

    held = {e["rule_id"] for e in state_evidence(result) if e["rule_id"]}
    assert "DTI-CONV-003" in held, "the dependency was not actually retrieved"


def test_dependency_following_is_bounded(graph, repo_root):
    """One round, capped — not a walk of the whole corpus."""
    result = _run(graph, repo_root, "APP-000056")
    followed = [s for s in result["retrieval_statuses"] if s.startswith("dependency:")]
    assert len(followed) <= MAX_DEPENDENCY_FOLLOWS

    # Every dependency retrieval stays inside the product.
    for item in state_evidence(result):
        assert item["product_domain"] == "MORTGAGE"


def test_the_extension_now_decides_APP_000057_correctly(graph, repo_root):
    """The regression this machinery exists to prevent.

    ``APP-000057`` documents three compensating factors and must be approved. It
    was being declined because DTI-CONV-003 was not retrieved and the engine
    concluded — wrongly — that no factors were documented.
    """
    result = _run(graph, repo_root, "APP-000057")
    evaluation = result["eligibility"]["evaluations"][0]

    assert result["calculations"]["ratios"]["back_end_dti"] == pytest.approx(0.44)
    assert evaluation["threshold"] == pytest.approx(0.45)
    assert len(evaluation["compensating_factors"]) >= 2
    assert result["eligibility"]["status"] == "ELIGIBLE"
    assert result["recommendation"]["outcome"] == "APPROVE_RECOMMENDATION"


def test_APP_000056_still_declines(graph, repo_root):
    """The fix must not turn a correct decline into an approval.

    ``APP-000056`` is the same 44% ratio with too few documented factors, so the
    extension is unavailable and the 43% ceiling governs.
    """
    result = _run(graph, repo_root, "APP-000056")
    evaluation = result["eligibility"]["evaluations"][0]

    assert evaluation["threshold"] == pytest.approx(0.43)
    assert len(evaluation["compensating_factors"]) < 2
    assert result["eligibility"]["status"] == "INELIGIBLE"
    assert result["recommendation"]["outcome"] == "DECLINE_RECOMMENDATION"
    assert result["requires_human_review"] is True
