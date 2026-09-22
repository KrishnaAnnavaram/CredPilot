"""The output guardrail, on its own.

`validate_response` used to be a private function inside `src/graph.py`, which
meant the only way to exercise the output guardrail was to build a graph and
run an application through it. These tests are the reason it moved: each of
the three checks, and the repair decision, asserted directly.

No model is called here and none is needed — the faithfulness verdict is made
where the narrative is made, and this reads it.
"""

from __future__ import annotations

from src.guardrails.validation import (
    CONTRADICTION_TERMS,
    policy_allows_publication,
    validate_response,
)

RESOLVING = [{"citation": "POL-DTI-001 v2.0 rule DTI-CONV-001", "citation_resolves": True}]
FAITHFUL = {"available": True, "is_faithful": True, "text": "The file was referred."}


def _verdict(**over):
    recommendation = over.pop("recommendation", {"outcome": "REFER_RECOMMENDATION"})
    narrative = {**FAITHFUL, **over.pop("narrative", {})}
    evidence = over.pop("evidence", RESOLVING)
    return validate_response({}, recommendation, narrative, evidence)


def test_a_clean_response_passes():
    verdict = _verdict()
    assert verdict["passed"] is True
    assert verdict["failures"] == []
    assert policy_allows_publication(verdict) is True
    assert verdict["fallback_to_deterministic"] is False


def test_an_unresolved_citation_fails_and_is_not_repairable_by_substitution():
    """A citation that does not resolve is a retrieval problem.

    Swapping in different prose would leave the gap and hide it, so the
    response fails validation *without* `fallback_to_deterministic`.
    """
    verdict = _verdict(
        evidence=[{"citation": "POL-GHOST-001 v1.0 rule NOPE-001", "citation_resolves": False}]
    )
    assert verdict["passed"] is False
    assert verdict["citations_resolve"] is False
    assert "do not resolve" in verdict["failures"][0]
    assert verdict["fallback_to_deterministic"] is False, (
        "substituting prose would hide a retrieval failure"
    )


def test_unfaithful_prose_fails_and_is_repairable():
    verdict = _verdict(
        narrative={
            "is_faithful": False,
            "unsupported_citations": ["POL-DTI-001 v9.9 rule MADE-UP-001"],
            "unsupported_figures": [0.99],
        }
    )
    assert verdict["passed"] is False
    assert verdict["narrative_faithful"] is False
    assert verdict["fallback_to_deterministic"] is True
    assert "MADE-UP-001" in verdict["failures"][0]


def test_prose_that_contradicts_the_decision_fails():
    """The most dangerous output this system can produce.

    A rationale that says "approved" under a decline reads as authoritative
    and is wrong in the direction a borrower would act on.
    """
    verdict = _verdict(
        recommendation={"outcome": "DECLINE_RECOMMENDATION"},
        narrative={"text": "Good news — the application was approved."},
    )
    assert verdict["passed"] is False
    assert verdict["decision_consistent"] is False
    assert verdict["fallback_to_deterministic"] is True


def test_the_word_appears_but_the_decision_agrees_with_it():
    """Guard the guard: the check must not fire on the correct sentence."""
    verdict = _verdict(
        recommendation={"outcome": "DECLINE_RECOMMENDATION"},
        narrative={"text": "The application was declined for the reasons below."},
    )
    assert verdict["passed"] is True, verdict["failures"]
    assert verdict["decision_consistent"] is True


def test_an_unavailable_narrative_is_not_scanned_for_contradictions():
    """The deterministic fallback is generated from the decision itself.

    Scanning it would be scanning our own template, and a template that named
    the outcome would fail against itself.
    """
    verdict = _verdict(
        recommendation={"outcome": "DECLINE_RECOMMENDATION"},
        narrative={"available": False, "text": "approved" * 3},
    )
    assert verdict["decision_consistent"] is True
    assert verdict["passed"] is True


def test_every_outcome_the_system_can_emit_has_contradiction_terms():
    """A new outcome with no terms would be silently unchecked."""
    from src.graph import _CONTRADICTION_TERMS  # the alias graph.py re-exports

    assert _CONTRADICTION_TERMS is CONTRADICTION_TERMS
    for outcome in ("APPROVE_RECOMMENDATION", "REFER_RECOMMENDATION", "DECLINE_RECOMMENDATION"):
        assert CONTRADICTION_TERMS.get(outcome), f"{outcome} has no contradiction terms"


def test_failures_accumulate_rather_than_short_circuiting():
    """A reviewer needs every reason, not the first one."""
    verdict = _verdict(
        recommendation={"outcome": "DECLINE_RECOMMENDATION"},
        narrative={"is_faithful": False, "text": "the application was approved"},
        evidence=[{"citation": "POL-GHOST-001", "citation_resolves": False}],
    )
    assert len(verdict["failures"]) == 3, verdict["failures"]
    assert policy_allows_publication(verdict) is False

    # Guardrails-AI reached the same conclusion on two of them. Its agreement is
    # recorded, but not re-listed: a reviewer counting reasons should see three
    # problems here, not five.
    assert set(verdict["guardrails"]["failed_validators"]) == {
        "NoUnresolvedCitation", "DecisionConsistent",
    }
    assert not [f for f in verdict["failures"] if f.startswith("guardrails-ai:")]


def test_a_pii_leak_on_the_way_out_is_caught_only_by_the_library_layer():
    """The one output check with no counterpart in this module.

    Citation resolution and decision consistency are checked twice on purpose.
    This is not: nothing above scans the published prose for a sensitive value,
    so if the Guardrails-AI layer stopped running, this failure would disappear
    silently rather than loudly.
    """
    verdict = _verdict(
        recommendation={"outcome": "APPROVE_RECOMMENDATION"},
        narrative={"is_faithful": True,
                   "text": f"Approved. We will write to the card {'4' + '1' * 15}."},
        evidence=[],
    )
    assert policy_allows_publication(verdict) is False
    assert [f for f in verdict["failures"] if f.startswith("guardrails-ai:")], (
        verdict["failures"]
    )
    assert "NoSensitiveValue" in verdict["guardrails"]["failed_validators"]
