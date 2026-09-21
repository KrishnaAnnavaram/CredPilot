"""The rule engine reads its thresholds from retrieved policy, never from code.

This is what makes retrieval load-bearing rather than decorative: change the
policy the retriever returns and the verdict changes with it; remove it and the
engine reports INDETERMINATE rather than falling back to a number in the source.
"""

from __future__ import annotations

import pytest

from src import rules
from src.domain import LendingProductDomain


def _as_evidence(chunks) -> list[dict]:
    return [
        {
            "rule_id": c.rule_id,
            "policy_id": c.policy_id,
            "policy_version": c.policy_version,
            "citation": c.citation,
            "text": c.text,
        }
        for c in chunks
    ]


@pytest.fixture(scope="module")
def mortgage_evidence(mortgage_chunks):
    chunks, _ = mortgage_chunks

    def for_version(version: str) -> list[dict]:
        return _as_evidence(
            c for c in chunks if c.policy_id == "POL-DTI-001" and c.policy_version == version
        )

    return for_version


@pytest.fixture(scope="module")
def education_evidence(education_chunks):
    chunks, _ = education_chunks
    return _as_evidence(chunks)


def _calc(dti: float, **extra) -> dict:
    calculations = {"ratios": {"back_end_dti": dti}, "amounts": {}, "months_of_reserves": 0.0}
    calculations.update(extra)
    return calculations


# ------------------------------------------------------------------ parameter reading


def test_parameters_come_from_the_cited_chunk(mortgage_evidence):
    """v1.0 and v2.0 publish different numbers under the same rule id."""
    v1 = rules.parameters_of(rules.find_rule(mortgage_evidence("1.0"), "DTI-CONV-001"))
    v2 = rules.parameters_of(rules.find_rule(mortgage_evidence("2.0"), "DTI-CONV-001"))

    assert v1["max_back_end_dti"] == pytest.approx(0.45)
    assert "max_back_end_dti_with_factors" not in v1, "v1.0 publishes no extension"

    assert v2["max_back_end_dti"] == pytest.approx(0.43)
    assert v2["max_back_end_dti_with_factors"] == pytest.approx(0.45)
    assert v2["min_compensating_factors"] == 2


def test_mixed_version_evidence_is_refused(mortgage_evidence):
    """Merging two versions would return v1.0's ceiling under v2.0's citation.

    Retrieval's temporal filter makes this unreachable in practice. The engine
    refuses it anyway rather than silently answering with the wrong number.
    """
    mixed = mortgage_evidence("1.0") + mortgage_evidence("2.0")
    with pytest.raises(rules.MixedVersionEvidenceError, match="multiple versions"):
        rules.extract_parameters(mixed)
    with pytest.raises(rules.MixedVersionEvidenceError):
        rules.evaluate(LendingProductDomain.MORTGAGE, {"ratios": {}}, {}, mixed)


def test_single_version_evidence_is_accepted(mortgage_evidence):
    rules.assert_single_version(mortgage_evidence("2.0"))
    params = rules.extract_parameters(mortgage_evidence("2.0"))
    assert params["DTI-CONV-001"]["max_back_end_dti"] == pytest.approx(0.43)


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("43%", 0.43),
        ("45%", 0.45),
        ("2", 2.0),
        ("$800", 800.0),
        ("1,200", 1200.0),
        ("yes", True),
        ("no", False),
        ("120 days", "120 days"),
    ],
)
def test_parameter_values_are_coerced(raw, expected):
    assert rules.parse_value(raw) == expected


def test_education_ceilings_are_read_per_product(education_evidence):
    ceilings = rules.extract_product_ceilings(education_evidence, "EDU-INC-003")
    assert ceilings == {"UG": 0.45, "GR": 0.43, "SP": 0.45, "INTL": 0.40, "REFI": 0.45}


def test_education_residual_floor_is_read(education_evidence):
    rule = rules.find_rule(education_evidence, "EDU-INC-004")
    assert rules._residual_floor(rule["text"]) == pytest.approx(800.0)


# ----------------------------------------------------------------------------- verdicts


def test_the_same_ratio_decides_differently_by_version(mortgage_evidence):
    """44% passes under v1.0 and breaches under v2.0. Nothing else changes."""
    packet = {"product_family": "conventional_conforming", "loan_purpose": "purchase"}

    v1 = rules.summarize(
        rules.evaluate(
            LendingProductDomain.MORTGAGE, _calc(0.44), packet, mortgage_evidence("1.0")
        )
    )
    v2 = rules.summarize(
        rules.evaluate(
            LendingProductDomain.MORTGAGE, _calc(0.44), packet, mortgage_evidence("2.0")
        )
    )

    assert v1["status"] == "ELIGIBLE"
    assert v2["status"] == "INELIGIBLE"
    assert v2["breaches"][0]["threshold"] == pytest.approx(0.43)
    assert v2["breaches"][0]["citation"] == "POL-DTI-001 v2.0 rule DTI-CONV-001"


def test_missing_evidence_is_indeterminate_not_a_pass():
    """Absence is never permission (POL-GEN-001 GEN-ELG-005)."""
    summary = rules.summarize(
        rules.evaluate(LendingProductDomain.MORTGAGE, _calc(0.44), {}, [])
    )
    assert summary["status"] == "INDETERMINATE"
    assert summary["breaches"] == []
    assert "not retrieved" in summary["indeterminate"][0]["detail"]


def test_zero_income_is_indeterminate_not_zero_or_infinite(mortgage_evidence):
    """POL-DTI-001 DTI-CALC-001 is explicit about this."""
    summary = rules.summarize(
        rules.evaluate(
            LendingProductDomain.MORTGAGE,
            {"ratios": {}, "amounts": {}},
            {},
            mortgage_evidence("2.0"),
        )
    )
    assert summary["status"] == "INDETERMINATE"


def test_the_extension_needs_the_minimum_number_of_factors(mortgage_evidence):
    """One documented factor is not enough; the rule requires two."""
    packet = {"product_family": "conventional_conforming", "loan_purpose": "purchase"}
    calculations = _calc(0.44, ratios={"back_end_dti": 0.44, "ltv": 0.72}, months_of_reserves=1.0)
    summary = rules.summarize(
        rules.evaluate(
            LendingProductDomain.MORTGAGE, calculations, packet, mortgage_evidence("2.0")
        )
    )
    assert summary["status"] == "INELIGIBLE"
    assert "1 of 2 required factors" in summary["breaches"][0]["detail"]


def test_the_extension_applies_with_enough_factors(mortgage_evidence):
    packet = {
        "product_family": "conventional_conforming",
        "loan_purpose": "purchase",
        "credit_summary": {"score_1": "732", "score_2": "744", "score_3": "750"},
    }
    calculations = _calc(
        0.44, ratios={"back_end_dti": 0.44, "ltv": 0.72}, months_of_reserves=61.1
    )
    evaluations = rules.evaluate(
        LendingProductDomain.MORTGAGE, calculations, packet, mortgage_evidence("2.0")
    )
    assert rules.summarize(evaluations)["status"] == "ELIGIBLE"
    assert evaluations[0].threshold == pytest.approx(0.45)
    assert len(evaluations[0].factors) >= 2
    joined = " ".join(evaluations[0].factors)
    assert "reserves" in joined and "credit score" in joined and "loan-to-value" in joined


@pytest.mark.parametrize(
    "packet",
    [
        {"product_family": "jumbo", "loan_purpose": "purchase"},
        {"product_family": "conventional_conforming", "loan_purpose": "cash_out_refinance"},
    ],
    ids=["jumbo", "cash-out"],
)
def test_the_extension_is_unavailable_on_an_excluded_product(mortgage_evidence, packet):
    """DTI-CONV-003 excludes cash-out refinances and the jumbo overlay."""
    calculations = _calc(
        0.44, ratios={"back_end_dti": 0.44, "ltv": 0.72}, months_of_reserves=61.1
    )
    evaluations = rules.evaluate(
        LendingProductDomain.MORTGAGE, calculations, packet, mortgage_evidence("2.0")
    )
    assert evaluations[0].verdict == rules.Verdict.FAIL
    assert evaluations[0].threshold == pytest.approx(0.43)
    assert "not available" in evaluations[0].detail


def test_an_undocumented_factor_does_not_count(mortgage_evidence):
    """A factor asserted but not evidenced is not a factor (DTI-CONV-003)."""
    packet = {"product_family": "conventional_conforming", "loan_purpose": "purchase"}
    calculations = _calc(0.44, months_of_reserves=None)
    evaluations = rules.evaluate(
        LendingProductDomain.MORTGAGE, calculations, packet, mortgage_evidence("2.0")
    )
    assert evaluations[0].factors == []
    assert evaluations[0].verdict == rules.Verdict.FAIL


# -------------------------------------------------------------------------- education


@pytest.mark.parametrize(
    "product,dti,expected",
    [
        ("GR", 0.42, "PASS"),
        ("GR", 0.44, "FAIL"),
        ("UG", 0.44, "PASS"),
        ("INTL", 0.42, "FAIL"),
        ("INTL", 0.39, "PASS"),
    ],
)
def test_education_ceilings_are_applied_per_product(education_evidence, product, dti, expected):
    """GR is 43%, UG and SP 45%, INTL 40% — the same ratio decides differently."""
    calculations = {
        "ratios": {"education_dti": dti},
        "amounts": {"residual_income_monthly": 2000.0},
    }
    evaluations = rules.evaluate(
        LendingProductDomain.EDUCATION_LOAN,
        calculations,
        {"product_code": product},
        education_evidence,
    )
    dti_evaluation = next(e for e in evaluations if e.rule_id == "EDU-INC-003")
    assert dti_evaluation.verdict == expected


def test_education_residual_income_floor_is_applied(education_evidence):
    calculations = {
        "ratios": {"education_dti": 0.20},
        "amounts": {"residual_income_monthly": 500.0},
    }
    evaluations = rules.evaluate(
        LendingProductDomain.EDUCATION_LOAN,
        calculations,
        {"product_code": "REFI"},
        education_evidence,
    )
    residual = next(e for e in evaluations if e.rule_id == "EDU-INC-004")
    assert residual.verdict == rules.Verdict.FAIL
    assert residual.threshold == pytest.approx(800.0)
    assert "hard knockout" in residual.detail


def test_education_unknown_product_is_indeterminate(education_evidence):
    evaluations = rules.evaluate(
        LendingProductDomain.EDUCATION_LOAN,
        {"ratios": {"education_dti": 0.30}, "amounts": {}},
        {"product_code": "UNKNOWN"},
        education_evidence,
    )
    assert evaluations[0].verdict == rules.Verdict.INDETERMINATE
