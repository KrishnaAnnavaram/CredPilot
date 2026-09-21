"""The three mortgage knockout rules, across both policy versions.

``CRD-SCR-003`` (minimum representative score), ``AST-RSV-002`` (minimum
reserves) and ``AST-FTC-003`` (the funds-to-close sufficiency test) are all
``PASS_FAIL`` rules that can decline a file on their own — a file can clear its
DTI ceiling comfortably and still fail on a score floor.

Two of them changed shape at the 2026-07-01 boundary, and the interesting
property is that the engine holds **no** knowledge of which version exists. It
reads the parameters the retrieved rule publishes; a file dated before the
boundary retrieves v1.0 and is measured against v1.0's flatter requirements
because that is what came back, not because the code special-cases a date.
"""

from __future__ import annotations

import pytest

from src import rules
from src.rules import (
    Verdict,
    evaluate_mortgage_credit_score,
    evaluate_mortgage_funds_to_close,
    evaluate_mortgage_reserves,
)

# --------------------------------------------------------------------- fixtures


def _score_rule(version: str) -> dict:
    """CRD-SCR-003 as each version publishes it."""
    if version == "1.0":
        table = "| `min_representative_score_conventional` | 620 |\n"
    else:
        table = (
            "| `min_representative_score_ltv_at_or_below_90` | 620 |\n"
            "| `min_representative_score_ltv_above_90` | 640 |\n"
            "| `ltv_band_boundary` | 90% |\n"
        )
    return {
        "rule_id": "CRD-SCR-003",
        "citation": f"POL-CRD-001 v{version} rule CRD-SCR-003",
        "text": "### CRD-SCR-003\n\n| Parameter | Value |\n| --- | --- |\n" + table,
    }


def _reserve_rule(version: str) -> dict:
    base = (
        "| `min_months_primary_residence` | 0 |\n"
        "| `min_months_second_home` | 2 |\n"
        "| `min_months_investment` | 6 |\n"
    )
    additions = (
        "| `additional_months_ltv_above_90` | 2 |\n"
        "| `ltv_trigger` | 90% |\n"
        "| `additional_months_dti_above_43` | 2 |\n"
        "| `dti_trigger` | 43% |\n"
        "| `additions_cumulative` | yes |\n"
    )
    return {
        "rule_id": "AST-RSV-002",
        "citation": f"POL-AST-003 v{version} rule AST-RSV-002",
        "text": "### AST-RSV-002\n\n| Parameter | Value |\n| --- | --- |\n"
                + base + (additions if version == "2.0" else ""),
    }


FTC_RULE = {
    "rule_id": "AST-FTC-003",
    "citation": "POL-AST-002 v1.0 rule AST-FTC-003",
    "text": (
        "### AST-FTC-003 — Sufficiency test\n\n"
        "A shortfall is a deterministic arithmetic failure, not a judgement.\n\n"
        "| Parameter | Value |\n| --- | --- |\n"
        "| `test` | funds_to_close_available >= funds_to_close_required |\n"
    ),
}


def _calc(ltv=0.80, dti=0.35, reserves=6.0, available=100_000.0, required=80_000.0):
    return {
        "ratios": {"ltv": ltv, "back_end_dti": dti},
        "months_of_reserves": reserves,
        "amounts": {
            "funds_to_close_available": available,
            "funds_to_close_required": required,
        },
    }


# ============================================================ CRD-SCR-003


@pytest.mark.parametrize("score,expected", [(619, Verdict.FAIL), (620, Verdict.PASS),
                                            (742, Verdict.PASS)])
def test_the_flat_v1_floor(score, expected):
    packet = {"credit_summary": {"representative_score": str(score)}}
    result = evaluate_mortgage_credit_score(_calc(ltv=0.95), packet, [_score_rule("1.0")])[0]
    assert result.verdict == expected
    assert result.threshold == 620.0
    assert "every leverage level" in result.detail


def test_v2_graduates_the_floor_by_leverage():
    """The rule's own worked example: 630 at 95% passes under v1.0, fails under v2.0."""
    packet = {"credit_summary": {"representative_score": "630"}}
    high_leverage = _calc(ltv=0.95)

    v1 = evaluate_mortgage_credit_score(high_leverage, packet, [_score_rule("1.0")])[0]
    v2 = evaluate_mortgage_credit_score(high_leverage, packet, [_score_rule("2.0")])[0]

    assert v1.verdict == Verdict.PASS and v1.threshold == 620.0
    assert v2.verdict == Verdict.FAIL and v2.threshold == 640.0
    assert "above 90%" in v2.detail


def test_v2_leaves_the_lower_band_where_it_was():
    """660 at 95% passes under either version — the rule says so explicitly."""
    packet = {"credit_summary": {"representative_score": "660"}}
    for version in ("1.0", "2.0"):
        result = evaluate_mortgage_credit_score(
            _calc(ltv=0.95), packet, [_score_rule(version)]
        )[0]
        assert result.verdict == Verdict.PASS, version


def test_the_band_boundary_is_inclusive_at_or_below():
    """Exactly 90% takes the lower floor, as 'at or below 90 percent' says."""
    packet = {"credit_summary": {"representative_score": "625"}}
    at = evaluate_mortgage_credit_score(_calc(ltv=0.90), packet, [_score_rule("2.0")])[0]
    above = evaluate_mortgage_credit_score(_calc(ltv=0.9001), packet, [_score_rule("2.0")])[0]
    assert at.threshold == 620.0 and at.verdict == Verdict.PASS
    assert above.threshold == 640.0 and above.verdict == Verdict.FAIL


def test_a_missing_score_is_indeterminate_not_a_fail():
    result = evaluate_mortgage_credit_score(_calc(), {}, [_score_rule("2.0")])[0]
    assert result.verdict == Verdict.INDETERMINATE
    assert "no representative score" in result.detail


def test_missing_leverage_does_not_default_to_the_generous_band():
    """The floor depends on a figure that is absent, so the engine says so.

    Assuming the lower band would be the generous direction on a knockout rule,
    which is the direction that lets a file through on a number nobody computed.
    """
    packet = {"credit_summary": {"representative_score": "625"}}
    result = evaluate_mortgage_credit_score(
        {"ratios": {}}, packet, [_score_rule("2.0")]
    )[0]
    assert result.verdict == Verdict.INDETERMINATE
    assert "leverage could not be computed" in result.detail


def test_an_unretrieved_score_rule_is_indeterminate():
    packet = {"credit_summary": {"representative_score": "500"}}
    result = evaluate_mortgage_credit_score(_calc(), packet, [])[0]
    assert result.verdict == Verdict.INDETERMINATE
    assert "not retrieved" in result.detail


# ============================================================ AST-RSV-002


def test_a_primary_residence_needs_no_reserves_under_v1():
    packet = {"occupancy_type": "primary_residence"}
    result = evaluate_mortgage_reserves(
        _calc(ltv=0.95, dti=0.44, reserves=0.0), packet, [_reserve_rule("1.0")]
    )[0]
    assert result.threshold == 0.0
    assert result.verdict == Verdict.PASS


def test_v2_adds_months_for_leverage_and_affordability_cumulatively():
    """The rule's own example: 95% leverage and 44% DTI needs four months."""
    packet = {"occupancy_type": "primary_residence"}
    calculations = _calc(ltv=0.95, dti=0.44, reserves=3.0)

    v1 = evaluate_mortgage_reserves(calculations, packet, [_reserve_rule("1.0")])[0]
    v2 = evaluate_mortgage_reserves(calculations, packet, [_reserve_rule("2.0")])[0]

    assert v1.threshold == 0.0 and v1.verdict == Verdict.PASS
    assert v2.threshold == 4.0 and v2.verdict == Verdict.FAIL
    assert "+2 for leverage" in v2.detail
    assert "+2 for back-end DTI" in v2.detail
    assert v2.baseline_threshold == 0.0, "the occupancy base should still be visible"


@pytest.mark.parametrize("occupancy,expected", [
    ("primary_residence", 0.0), ("second_home", 2.0), ("investment", 6.0),
])
def test_the_occupancy_base(occupancy, expected):
    result = evaluate_mortgage_reserves(
        _calc(ltv=0.80, dti=0.30), {"occupancy_type": occupancy}, [_reserve_rule("2.0")]
    )[0]
    assert result.threshold == expected


def test_an_unknown_occupancy_is_indeterminate():
    result = evaluate_mortgage_reserves(
        _calc(), {"occupancy_type": "houseboat"}, [_reserve_rule("2.0")]
    )[0]
    assert result.verdict == Verdict.INDETERMINATE


# ============================================================ AST-FTC-003


def test_sufficient_funds_pass():
    result = evaluate_mortgage_funds_to_close(
        _calc(available=100_000.0, required=80_000.0), [FTC_RULE]
    )[0]
    assert result.verdict == Verdict.PASS
    assert "shortfall" not in result.detail


def test_a_shortfall_fails_and_names_the_gap():
    result = evaluate_mortgage_funds_to_close(
        _calc(available=59_350.80, required=82_431.66), [FTC_RULE]
    )[0]
    assert result.verdict == Verdict.FAIL
    assert "shortfall 23,080.86" in result.detail


def test_exactly_enough_passes():
    """'at least the required funds' — equality is sufficiency."""
    result = evaluate_mortgage_funds_to_close(
        _calc(available=80_000.0, required=80_000.0), [FTC_RULE]
    )[0]
    assert result.verdict == Verdict.PASS


def test_no_compensating_factor_cures_a_shortfall():
    """The rule is explicit that this one is arithmetic, not judgement.

    There is no extension branch to exercise, so the test is that a file with
    every compensating factor imaginable still fails on the arithmetic.
    """
    calculations = _calc(available=10.0, required=80_000.0, reserves=999.0)
    result = evaluate_mortgage_funds_to_close(calculations, [FTC_RULE])[0]
    assert result.verdict == Verdict.FAIL


def test_uncomputable_funds_are_indeterminate():
    result = evaluate_mortgage_funds_to_close({"amounts": {}}, [FTC_RULE])[0]
    assert result.verdict == Verdict.INDETERMINATE


# ============================================================ together


def test_a_file_can_clear_its_dti_and_still_be_declined():
    """The property the knockouts exist for."""
    packet = {
        "occupancy_type": "primary_residence",
        "credit_summary": {"representative_score": "598"},
    }
    evaluations = [
        *evaluate_mortgage_credit_score(_calc(dti=0.28), packet, [_score_rule("2.0")]),
        *evaluate_mortgage_reserves(_calc(dti=0.28), packet, [_reserve_rule("2.0")]),
        *evaluate_mortgage_funds_to_close(_calc(dti=0.28), [FTC_RULE]),
    ]
    summary = rules.summarize(evaluations)
    assert summary["status"] == "INELIGIBLE"
    assert summary["breaches"][0]["measure"] == "representative_score"
