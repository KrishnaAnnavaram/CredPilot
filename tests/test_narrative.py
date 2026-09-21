"""The written rationale, and the check that it did not make anything up.

The narrative is the only place a language model speaks, and it speaks after the
decision exists. So the failure mode it has to be guarded against is not "the
model decides wrongly" — it cannot decide at all — but "the model narrates a
figure or a citation that is not in its evidence".

:func:`~src.narrative.verify_narrative` is that guard, and it asks no model
anything. These tests are mostly about it, because a grounding check that passes
everything is worse than none: it reports 1.00 and means nothing.

That was not hypothetical. The figure pattern originally matched percentages and
money amounts only, so on a real narrative sentence carrying five figures —
`9466.67`, `3976.0`, `0.42`, `0.3101`, `43 percent` — it checked one. Bare
decimals are how the model actually quotes a computed figure.
"""

from __future__ import annotations

import pytest

from src.narrative import (
    NarrativeResult,
    _deterministic_summary,
    _FIGURE,
    draft_rationale,
    generation_enabled,
    verify_narrative,
)

CITATION = "POL-DTI-001 v2.0 rule DTI-CONV-001"
EVIDENCE = [
    {
        "rule_id": "DTI-CONV-001",
        "citation": CITATION,
        "text": (
            "Back-end debt-to-income must not exceed 43%. The ceiling extends to 45% "
            "where at least two compensating factors are documented.\n"
            "| Parameter | Value |\n| `max_back_end_dti` | 43% |\n"
        ),
    }
]
CALCULATIONS = {
    "ratios": {"back_end_dti": 0.4400, "front_end_dti": 0.3101, "ltv": 0.80},
    "amounts": {
        "qualifying_monthly_income": 8858.33,
        "total_monthly_obligations": 3897.67,
        "verified_liquid_assets": 167719.08,
    },
    "formula_version": "mortgage-affordability-2.1",
}

FAITHFUL = (
    f"Under [{CITATION}] the back-end ceiling is 43 percent. Qualifying monthly income "
    f"of 8858.33 against total monthly obligations of 3897.67 gives a back_end_dti of "
    f"0.44, with front_end_dti at 0.3101 and verified liquid assets of 167719.08."
)


# ============================================================ what gets checked


def test_the_pattern_catches_every_shape_a_figure_is_written_in():
    """Percentages, money, and — above all — bare decimals."""
    text = "income 9466.67, obligations 3976.0, dti 0.42, front 0.3101, ceiling 43 percent, $1,850.00"
    matched = _FIGURE.findall(text)
    for figure in ("9466.67", "3976.0", "0.42", "0.3101", "43 percent"):
        assert figure in matched, f"{figure} went unchecked"
    assert any("1,850" in m for m in matched)


@pytest.mark.parametrize("text", [
    "a term of 360 months",
    "self-employed since 2019",
    "per POL-DTI-001 v2.0 rule DTI-CONV-001",
    "underwritten on 2026-07-08",
    "a household of 4",
])
def test_the_pattern_ignores_numbers_that_are_not_figures(text):
    """Years, terms, versions, dates and counts are not quoted measurements.

    A check that flagged `2019` as an unsupported figure is a check nobody would
    keep switched on.
    """
    assert _FIGURE.findall(text) == []


# ================================================================= faithfulness


def test_a_faithful_narrative_passes():
    used, bad_citations, bad_figures = verify_narrative(FAITHFUL, EVIDENCE, CALCULATIONS)
    assert CITATION in used
    assert bad_citations == []
    assert bad_figures == []


def test_a_figure_that_came_from_nowhere_is_caught():
    text = FAITHFUL + " Reserves stood at 12345.67 months."
    _, _, bad_figures = verify_narrative(text, EVIDENCE, CALCULATIONS)
    assert "12345.67" in bad_figures


def test_a_quietly_altered_figure_is_caught():
    """The dangerous one: a plausible number in place of the real one."""
    tampered = FAITHFUL.replace("0.44", "0.39")
    _, _, bad_figures = verify_narrative(tampered, EVIDENCE, CALCULATIONS)
    assert "0.39" in bad_figures


def test_an_invented_threshold_is_caught():
    tampered = FAITHFUL.replace("43 percent", "55 percent")
    _, _, bad_figures = verify_narrative(tampered, EVIDENCE, CALCULATIONS)
    assert "55 percent" in bad_figures


def test_the_same_figure_in_a_different_scale_is_the_same_claim():
    """0.44 and 44% are one number written two ways, not two claims."""
    text = f"Under [{CITATION}] the computed ratio is 44 percent."
    _, _, bad_figures = verify_narrative(text, EVIDENCE, CALCULATIONS)
    assert bad_figures == []


def test_trailing_zeros_are_not_a_discrepancy():
    text = f"Under [{CITATION}] the ratio is 0.4400 and leverage is 0.80."
    _, _, bad_figures = verify_narrative(text, EVIDENCE, CALCULATIONS)
    assert bad_figures == []


def test_a_threshold_stated_by_the_evidence_may_be_repeated():
    """45% appears only in the policy text, not in the computed figures."""
    text = f"[{CITATION}] extends the ceiling to 45 percent on two factors."
    _, _, bad_figures = verify_narrative(text, EVIDENCE, CALCULATIONS)
    assert bad_figures == []


# ==================================================================== citations


def test_a_citation_outside_the_evidence_is_caught():
    text = "This file is governed by POL-DTI-001 v9.9 rule DTI-CONV-999."
    _, bad_citations, _ = verify_narrative(text, EVIDENCE, CALCULATIONS)
    assert bad_citations


def test_a_citation_written_without_its_version_still_resolves():
    """A spelling difference is not an invented citation."""
    text = "Under POL-DTI-001 rule DTI-CONV-001 the ceiling applies."
    used, bad_citations, _ = verify_narrative(text, EVIDENCE, CALCULATIONS)
    assert used and not bad_citations


# ====================================================================== result


def test_faithfulness_requires_both_halves():
    assert NarrativeResult(text="x", model="m", available=True).is_faithful
    assert not NarrativeResult(
        text="x", model="m", available=True, unsupported_citations=["POL-X"]
    ).is_faithful
    assert not NarrativeResult(
        text="x", model="m", available=True, unsupported_figures=["99.99"]
    ).is_faithful


def test_the_result_serializes_for_the_checkpoint():
    import json

    result = NarrativeResult(text="x", model="m", available=True, usage={"input_tokens": 1})
    assert json.loads(json.dumps(result.as_dict()))["is_faithful"] is True


# ============================================================ degradation


def test_generation_is_disabled_in_the_suite():
    """conftest sets it, so no test makes a model call."""
    assert generation_enabled() is False


def test_a_disabled_narrative_still_produces_a_usable_rationale():
    """A recommendation without prose is still a recommendation.

    An outage must not block a file, so the node degrades to a deterministic
    summary and says so rather than failing.
    """
    state = {
        "application_id": "APP-000057",
        "loan_domain": "MORTGAGE",
        "as_of_date": "2026-07-08",
        "policy_evidence": EVIDENCE,
        "calculations": CALCULATIONS,
        "eligibility": {"status": "ELIGIBLE", "evaluations": [], "breaches": [],
                        "indeterminate": []},
        "risk": {"level": "LOW", "flags": []},
        "recommendation": {"outcome": "APPROVE_RECOMMENDATION"},
    }
    result = draft_rationale(state)

    assert result.available is False
    assert result.model is None
    assert "CREDPILOT_NARRATIVE" in (result.note or "")
    assert "APP-000057" in result.text
    assert "APPROVE_RECOMMENDATION" in result.text


def test_the_deterministic_summary_names_every_breach_with_its_threshold():
    state = {
        "application_id": "APP-000056",
        "loan_domain": "MORTGAGE",
        "as_of_date": "2026-07-08",
        "calculations": CALCULATIONS,
        "eligibility": {
            "status": "INELIGIBLE",
            "breaches": [{"measure": "back_end_dti", "observed": 0.44, "threshold": 0.43,
                          "citation": CITATION}],
            "indeterminate": [],
        },
        "risk": {"level": "ELEVATED", "flags": []},
        "recommendation": {"outcome": "DECLINE_RECOMMENDATION"},
        "requires_human_review": True,
        "human_review_reasons": ["a decline is always routed to a human (DEC-REC-002)"],
    }
    summary = _deterministic_summary(state)

    assert "back_end_dti" in summary
    assert "0.43" in summary
    assert CITATION in summary
    assert "DEC-REC-002" in summary


# ======================================= every figure the prompt actually supplies


EVALUATIONS = [
    {"measure": "representative_score", "observed": 742.0, "threshold": 620.0,
     "baseline_threshold": 620.0, "comparator": ">="},
    {"measure": "months_of_reserves", "observed": 4.7833, "threshold": 2.0,
     "baseline_threshold": 0.0, "comparator": ">="},
]
CALCULATIONS_WITH_TOP_LEVEL = {**CALCULATIONS, "months_of_reserves": 4.7833}


def test_a_figure_from_the_rule_evaluations_is_supported():
    """The representative score and every policy floor arrive only this way.

    `draft_rationale` passes the rule evaluations to the model under
    `application_facts.rule_evaluations`, so a narrative quoting 742 against a
    620 floor is quoting what it was handed.
    """
    text = f"Under [{CITATION}] the representative score of 742.0 clears the floor of 620.0."
    _, _, bad_figures = verify_narrative(
        text, EVIDENCE, CALCULATIONS_WITH_TOP_LEVEL, EVALUATIONS
    )
    assert bad_figures == []


def test_a_figure_published_outside_ratios_and_amounts_is_supported():
    """`months_of_reserves` sits at the top level of the calculations dict."""
    text = f"Under [{CITATION}] the file holds 4.7833 months of reserves."
    _, _, bad_figures = verify_narrative(
        text, EVIDENCE, CALCULATIONS_WITH_TOP_LEVEL, EVALUATIONS
    )
    assert bad_figures == []


def test_omitting_those_sources_is_what_produced_the_false_accusations():
    """Guards the regression directly.

    The first judged run reported 0.648 deterministic faithfulness against the
    judge's 0.984, and the entire gap was this: the check flagged the model for
    quoting figures the system had computed and supplied. A grounding check that
    cries wolf buries the real cases.
    """
    text = f"Under [{CITATION}] the score of 742.0 clears 620.0 with 4.7833 months."

    without = verify_narrative(text, EVIDENCE, CALCULATIONS)[2]
    with_them = verify_narrative(text, EVIDENCE, CALCULATIONS_WITH_TOP_LEVEL, EVALUATIONS)[2]

    assert without, "the fixture should reproduce the old false positives"
    assert with_them == []


def test_an_invented_figure_survives_the_wider_supported_set():
    """Widening it must not turn the check off."""
    text = f"Under [{CITATION}] the score of 742.0 clears 620.0. Reserves were 99.99 months."
    _, _, bad_figures = verify_narrative(
        text, EVIDENCE, CALCULATIONS_WITH_TOP_LEVEL, EVALUATIONS
    )
    assert bad_figures == ["99.99"]


# ================================================ signs, versions and real misses


SIGNED = {
    "ratios": {},
    "amounts": {
        # Funds to close is signed: a borrower taking cash out is owed money.
        "funds_to_close_required": -43441.36,
        "funds_to_close_surplus": -23080.86,
    },
    "formula_version": "mortgage-affordability-2.1",
}


def test_a_magnitude_of_a_signed_figure_is_the_same_claim():
    """"Receives 43,441.36" and "a shortfall of 23,080.86" quote real values.

    The system stores both as negatives. Flagging the prose for dropping the sign
    would accuse the model of inventing its own inputs.
    """
    text = "The borrower receives 43441.36 at closing; elsewhere a shortfall of 23080.86 arises."
    _, _, bad_figures = verify_narrative(text, [], SIGNED)
    assert bad_figures == []


def test_a_formula_version_is_not_a_quoted_figure():
    """`mortgage-affordability-2.1` is an identifier, like `v2.0` before it."""
    assert _FIGURE.findall("computed under formula mortgage-affordability-2.1") == []
    assert _FIGURE.findall("screened under risk-screen-1.0") == []


def test_a_negative_number_in_prose_is_still_read_as_a_figure():
    """Excluding versions must not exclude genuine negatives."""
    assert _FIGURE.findall("required was -43,441.36") == ["43,441.36"]


def test_a_figure_the_prompt_never_carried_is_still_caught():
    """A figure absent from every source stays flagged.

    16733.33 is used here precisely because it looked invented and was not: in
    APP-000040 it is the unsourced deposit amount, which reaches the prompt
    through a human-review reason. Checking only the amounts dict made it look
    like a fabrication. Against a fixture that genuinely never supplies it, the
    check still catches it — which is the property being pinned, and the reason
    to widen against the real sources rather than until a number looks good.
    """
    _, _, bad_figures = verify_narrative("Reserves stood at 16733.33.", [], SIGNED)
    assert bad_figures == ["16733.33"]


# ===================================== generous about given, strict about claimed


VERSIONED = {
    "ratios": {"back_end_dti": 0.42},
    "amounts": {},
    "formula_version": "mortgage-affordability-2.1",
}
REVIEW_REASONS = [
    "back_end_dti 42.00% is within 2.00 percentage points of its 43.00% limit "
    "(POL-UWR-001 v1.0 rule UWR-HRV-001)"
]


def test_a_figure_from_a_human_review_reason_is_supported():
    """The review reasons go into the prompt as application facts.

    `UWR-HRV-001`'s band reaches the model only this way — "within 2.00
    percentage points" — so a narrative repeating 2.00 is repeating its input.
    """
    text = "The file sits within 2.00 percentage points of its limit."
    _, _, bad = verify_narrative(text, [], VERSIONED, (), REVIEW_REASONS)
    assert bad == []


def test_the_formula_version_is_supported_as_well_as_unmatched():
    """Belt and braces, and they guard different things.

    The pattern no longer reads `mortgage-affordability-2.1` as a quoted `2.1`,
    and the supported set admits the number anyway because COMPUTED_FACTS carried
    it. Either alone would be enough; both together mean a rewording of the prose
    cannot resurrect the false positive.
    """
    assert _FIGURE.findall("under mortgage-affordability-2.1") == []
    _, _, bad = verify_narrative("Computed under formula version 2.1.", [], VERSIONED)
    assert bad == []


def test_the_supplied_side_is_looser_than_the_asserting_side():
    """The asymmetry, stated directly.

    Anything numeric we put in the prompt is fair for the model to repeat; not
    every number in the prose is a quoted measurement. Being strict on both sides
    produces false accusations; being loose on both lets real ones through.
    """
    from src.narrative import _SUPPLIED_NUMBER

    identifier = "mortgage-affordability-2.1"
    assert _SUPPLIED_NUMBER.findall(identifier), "supplied side should see the number"
    assert not _FIGURE.findall(identifier), "asserting side should not"


def test_widening_the_supplied_side_does_not_admit_an_unsupplied_figure():
    """The guard on every widening in this module.

    The review reasons here mention a band, not a deposit, so the figure has no
    source and stays flagged.
    """
    _, _, bad = verify_narrative("Reserves stood at 16733.33.", [], VERSIONED, (), REVIEW_REASONS)
    assert bad == ["16733.33"]
