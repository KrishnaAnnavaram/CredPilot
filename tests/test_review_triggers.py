"""Mandatory human-review triggers — ``POL-UWR-001`` UWR-HRV-001.

The rule calls itself mandatory: *"a file matching any trigger reaches a human
regardless of how the rest of the file looks."* These tests hold that line, and
in particular hold the two places it is easy to lose:

* an **eligible** file with a clean risk screen still gets referred when a
  trigger matches — referral is not a kind of failure;
* the band comes from the **retrieved rule**, so a version boundary that moved it
  would move the behaviour with it.
"""

from __future__ import annotations

import pytest

from src.domain import LendingProductDomain
from src.review_triggers import (
    DEFAULT_BORDERLINE_BAND_PCT_POINTS,
    UNEVALUABLE_TRIGGERS,
    evaluate_review_triggers,
)

MORTGAGE = LendingProductDomain.MORTGAGE

#: A retrieved UWR-HRV-001 chunk, with the parameter table the real one carries.
RULE_CHUNK = {
    "rule_id": "UWR-HRV-001",
    "citation": "POL-UWR-001 v1.0 rule UWR-HRV-001",
    "text": (
        "### UWR-HRV-001 - Mandatory human-review triggers\n\n"
        "A file reaches a human underwriter whenever any of the following is "
        "present: a decline recommendation; a jumbo or otherwise high-value "
        "exposure; self-employment income; an affordability result within two "
        "percentage points of its limit; or an application where a security "
        "event was raised.\n\n"
        "| Parameter | Value |\n"
        "| --- | --- |\n"
        "| `borderline_band_pct_points` | 2 |\n"
    ),
}


def _eligibility(status="ELIGIBLE", observed=None, threshold=None, baseline=None):
    evaluations = []
    if observed is not None:
        evaluations.append({
            "measure": "back_end_dti",
            "verdict": "PASS",
            "observed": observed,
            "threshold": threshold,
            "baseline_threshold": baseline,
            "comparator": "<=",
        })
    return {"status": status, "evaluations": evaluations, "breaches": [], "indeterminate": []}


def _run(packet=None, eligibility=None, risk=None, evidence=None, **kwargs):
    return evaluate_review_triggers(
        MORTGAGE,
        {},
        packet or {},
        evidence if evidence is not None else [RULE_CHUNK],
        eligibility or _eligibility(),
        risk or {"level": "LOW", "flags": []},
        **kwargs,
    )


# ------------------------------------------------------------------ the band


def test_the_band_comes_from_the_retrieved_rule():
    """A threshold living in Python is one no version boundary could move."""
    assessment = _run()
    assert assessment.band_pct_points == 2.0
    assert assessment.band_from_policy is True
    assert assessment.rule_citation == "POL-UWR-001 v1.0 rule UWR-HRV-001"


def test_a_missing_rule_falls_back_and_says_so():
    """The fallback is used, and the result records that it was assumed."""
    assessment = _run(evidence=[])
    assert assessment.band_pct_points == DEFAULT_BORDERLINE_BAND_PCT_POINTS
    assert assessment.band_from_policy is False
    assert "not retrieved" in assessment.rule_citation


def test_a_moved_band_moves_the_behaviour():
    """The whole point of reading it from policy."""
    tighter = dict(RULE_CHUNK)
    tighter["text"] = RULE_CHUNK["text"].replace(
        "| `borderline_band_pct_points` | 2 |", "| `borderline_band_pct_points` | 0.5 |"
    )
    # 42% against a 43% limit is 1 point clear: inside a 2-point band, outside 0.5.
    eligibility = _eligibility(observed=0.42, threshold=0.43, baseline=0.43)

    assert _run(eligibility=eligibility).required is True
    assert _run(eligibility=eligibility, evidence=[tighter]).required is False


# -------------------------------------------------------- borderline affordability


def test_a_file_approaching_its_limit_is_referred():
    assessment = _run(eligibility=_eligibility(observed=0.42, threshold=0.43, baseline=0.43))
    assert assessment.required is True
    assert [t.name for t in assessment.triggers] == ["borderline_affordability"]
    assert "42.00%" in assessment.triggers[0].detail
    assert "43.00%" in assessment.triggers[0].detail


def test_a_comfortable_file_is_not_referred():
    assessment = _run(eligibility=_eligibility(observed=0.31, threshold=0.43, baseline=0.43))
    assert assessment.required is False
    assert assessment.triggers == []


def test_the_tighter_of_the_applied_and_baseline_limits_governs():
    """A file clearing only on a discretionary extension is near a policy edge.

    At 42% with the ceiling extended to 45% on compensating factors, the applied
    threshold makes the file look three points clear. Against the 43% the
    programme actually sets it is one point under, which is what the trigger is
    for.
    """
    assessment = _run(eligibility=_eligibility(observed=0.42, threshold=0.45, baseline=0.43))
    assert assessment.required is True
    trigger = assessment.triggers[0]
    assert trigger.threshold == 0.43
    assert "after extension" in trigger.detail, "the applied ceiling should still be disclosed"


def test_a_breach_is_not_a_borderline_trigger():
    """Over the limit is a decline, which is a different trigger entirely."""
    eligibility = _eligibility(status="INELIGIBLE", observed=0.48, threshold=0.45, baseline=0.43)
    assessment = _run(eligibility=eligibility)
    names = [t.name for t in assessment.triggers]
    assert "decline" in names
    assert "borderline_affordability" not in names


# ------------------------------------------------------------- the other triggers


@pytest.mark.parametrize(
    "packet,expected",
    [
        ({"product_family": "jumbo"}, "high_value_exposure"),
        ({"declared_income": [{"income_type": "self_employed"}]}, "self_employment"),
        (
            {"occupancy_type": "primary_residence",
             "subject_property": {"occupancy_intent": "investment"}},
            "occupancy_contradiction",
        ),
        ({"fraud_screening": {"kyc_status": "REVIEW"}}, "identity_not_clean"),
        ({"fraud_screening": {"kyc_status": "PASS", "ofac_hit": True}},
         "fraud_or_document_integrity"),
    ],
)
def test_each_packet_trigger_refers_the_file(packet, expected):
    assessment = _run(packet=packet)
    assert expected in [t.name for t in assessment.triggers]
    assert assessment.required is True


def test_a_security_event_refers_the_file():
    assessment = _run(security_findings=["instruction_override"])
    assert "security_event" in [t.name for t in assessment.triggers]


def test_indeterminate_evidence_refers_the_file():
    """Absent evidence refers; it never declines (GEN-ELG-005)."""
    assessment = _run(eligibility=_eligibility(status="INDETERMINATE"))
    assert "unresolved_evidence" in [t.name for t in assessment.triggers]


def test_a_clean_file_is_not_referred():
    """The rule must not refer everything, or it routes nothing."""
    assessment = _run(
        packet={"product_family": "conventional_conforming",
                "declared_income": [{"income_type": "salaried"}],
                "occupancy_type": "primary_residence",
                "subject_property": {"occupancy_intent": "primary_residence"}},
        eligibility=_eligibility(observed=0.28, threshold=0.43, baseline=0.43),
    )
    assert assessment.required is False


# ------------------------------------------------------------------ honesty


def test_unevaluable_triggers_are_named_rather_than_passed_silently():
    """A trigger nobody checked is not a trigger that did not fire."""
    payload = _run().as_dict()
    assert set(payload["unevaluable_triggers"]) == set(UNEVALUABLE_TRIGGERS)
    assert "not the same as their having passed" in payload["unevaluable_note"]


def test_an_eligible_low_risk_file_can_still_be_referred():
    """The property the whole rule exists for.

    Referral is not a downgrade of eligibility: the file passed every threshold,
    the risk screen is clean, and it still reaches a human.
    """
    eligibility = _eligibility(status="ELIGIBLE", observed=0.42, threshold=0.43, baseline=0.43)
    assessment = _run(eligibility=eligibility, risk={"level": "LOW", "flags": []})
    assert eligibility["status"] == "ELIGIBLE"
    assert assessment.required is True


# ---------------------------------------- triggers read from the structured inputs


def test_an_unsourced_large_deposit_refers_the_file():
    """UWR-HRV-001 names it, and `asset_transactions` carries the flag.

    This was on the "unevaluable" list until the data was checked properly. The
    table was on the INPUT allowlist the whole time.
    """
    packet = {
        "asset_transactions": [
            {"amount": "45000.00", "transaction_date": "2026-07-02",
             "source_status": "UNSOURCED", "large_deposit_flag": True},
        ]
    }
    assessment = _run(packet=packet)
    assert "unsourced_large_deposit" in [t.name for t in assessment.triggers]
    assert "45000.00" in assessment.triggers[0].detail


def test_a_sourced_large_deposit_does_not_refer_the_file():
    """The flag alone is not the trigger; being unsourced is."""
    packet = {
        "asset_transactions": [
            {"amount": "45000.00", "source_status": "SOURCED", "large_deposit_flag": True},
        ]
    }
    assert _run(packet=packet).required is False


def test_a_conflicting_verification_refers_the_file():
    packet = {"verification_results": [
        {"category": "income", "result": "CONFLICT", "provider": "SYNTH-VERIFY"},
    ]}
    assessment = _run(packet=packet)
    assert "unresolved_evidence_conflict" in [t.name for t in assessment.triggers]
    assert "income" in assessment.triggers[0].detail


def test_a_flood_zone_code_is_not_read_as_a_verification_status():
    """`verifications.result` is polymorphic.

    For `flood_determination` it holds a FEMA zone code — `X` for minimal hazard,
    `AE` for a special flood hazard area — not a pass/fail status. Reading those
    as statuses would refer files on the strength of a zone letter.
    """
    for zone in ("X", "AE", "A", "VE"):
        packet = {"verification_results": [
            {"category": "flood_determination", "result": zone, "provider": "SYNTH-VERIFY"},
        ]}
        assert _run(packet=packet).required is False, f"zone {zone} triggered a referral"


def test_a_clean_verification_set_does_not_refer_the_file():
    packet = {"verification_results": [
        {"category": c, "result": "VERIFIED"} for c in ("identity", "employment", "income", "assets")
    ] + [{"category": "flood_determination", "result": "X"}]}
    assert _run(packet=packet).required is False


def test_the_unevaluable_list_holds_only_triggers_with_no_data_anywhere():
    """It shrank from five to three once the structured tables were checked.

    Publishing a false "we could not check this" tells a reviewer a control was
    impossible when it was merely unwritten.
    """
    payload = _run().as_dict()
    assert set(payload["unevaluable_triggers"]) == {
        "automated underwriting refer or caution result",
        "requested policy exception",
        "valuation or collateral finding",
    }
    assert "unsourced large deposit" not in payload["unevaluable_triggers"]
    assert "unresolved conflict between evidence sources" not in payload["unevaluable_triggers"]


# ------------------------------------------------ the band does not cross products


def test_education_does_not_inherit_the_mortgage_borderline_band():
    """A threshold written for one product must not govern another.

    `UWR-HRV-001` sets two percentage points for mortgage. `EDU-GOV-002` defines
    the four permitted education outcomes and states its referral criterion
    qualitatively, with no band. Falling back to mortgage's number would produce
    an education referral citing an education rule for a mortgage threshold —
    exactly the cross-product bleed separate collections exist to prevent.
    """
    education_rule = {
        "rule_id": "EDU-GOV-002",
        "citation": "POL-001 EDU-GOV-002",
        "text": "**EDU-GOV-002 -- Permitted Decision Outcomes.** APPROVE, "
                "APPROVE_WITH_CONDITIONS, REFER, DECLINE.",
    }
    # A file one point under its limit — squarely inside mortgage's 2-point band.
    eligibility = _eligibility(observed=0.44, threshold=0.45, baseline=0.45)

    assessment = evaluate_review_triggers(
        LendingProductDomain.EDUCATION_LOAN,
        {},
        {},
        [education_rule],
        eligibility,
        {"level": "LOW", "flags": []},
    )

    assert "borderline_affordability" not in [t.name for t in assessment.triggers]
    assert assessment.band_from_policy is False
    assert assessment.band_pct_points is None, "no band should be claimed at all"
    assert any("publish no borderline band" in t for t in assessment.unevaluable), (
        "the trigger should be reported unevaluable, not silently skipped"
    )


def test_mortgage_still_falls_back_when_its_own_rule_is_missing():
    """The fallback survives for the product the number was written for.

    A mortgage file whose routing rule failed to retrieve still gets the tighter,
    safer treatment rather than none — and the result records that the band was
    assumed.
    """
    eligibility = _eligibility(observed=0.44, threshold=0.45, baseline=0.45)
    assessment = _run(eligibility=eligibility, evidence=[])

    assert "borderline_affordability" in [t.name for t in assessment.triggers]
    assert assessment.band_from_policy is False
    assert assessment.band_pct_points == DEFAULT_BORDERLINE_BAND_PCT_POINTS
