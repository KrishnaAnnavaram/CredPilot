"""The extended rule families: every threshold comes out of the retrieved rule.

The families in :mod:`src.rule_families` were added because 33 of 75 mortgage
and 17 of 20 education golden cases turned on a rule the engine never compared
against anything. Adding them is only an improvement if they obey the same three
rules as the families that were already there, and each is checked here:

* **a missing rule is INDETERMINATE, never a pass and never a fail.** Absence of
  evidence is not permission (``GEN-ELG-005``). An evaluator that quietly passed
  when its rule failed to retrieve would turn a retrieval regression into an
  approval;
* **the threshold is read from the evidence**, so moving the number in the
  policy moves the verdict with no code change;
* **a family that does not apply says NOT_APPLICABLE**, because an evaluator
  that returns nothing is indistinguishable from one that was never written.

Every test builds its evidence by hand. No index, no retrieval, no model — so a
failure here is a failure in the rule logic and nothing else.
"""

from __future__ import annotations

import pytest

from src.domain import LendingProductDomain
from src.rules import Verdict, evaluate, summarize
from src.rule_families.education_ext import (
    evaluate_education_cosigner,
    evaluate_education_international,
    evaluate_education_risk_grade,
    evaluate_education_underwriting,
)
from src.rule_families.mortgage_ext import (
    evaluate_asset_source,
    evaluate_credit_events,
    evaluate_delinquency,
    evaluate_documentation,
    evaluate_employment_continuity,
    evaluate_general_eligibility,
    evaluate_jumbo,
    evaluate_valuation,
)


def rule(rule_id: str, text: str, citation: str | None = None) -> dict:
    """One evidence chunk, spelled the way the retriever spells them."""
    return {
        "rule_id": rule_id,
        "policy_id": citation.split()[0] if citation else "POL-TEST-001",
        "policy_version": "1.0",
        "citation": citation or f"POL-TEST-001 v1.0 rule {rule_id}",
        "text": text,
        "citation_resolves": True,
    }


def by_measure(evaluations, measure):
    return next((e for e in evaluations if e.measure == measure), None)


# ======================================================== the shared contract


MORTGAGE_EVALUATORS = (
    ("DOC-REQ-001", evaluate_documentation, "document_completeness"),
    ("EMP-CNT-001", evaluate_employment_continuity, "employment_history_months"),
    ("AST-SRC-002", evaluate_asset_source, "unsourced_large_deposits"),
    ("CRD-DLQ-001", evaluate_delinquency, "housing_delinquency"),
    ("GEN-ELG-003", evaluate_general_eligibility, "programme_loan_limit"),
    ("VAL-APR-003", evaluate_valuation, "valuation_age_days"),
)


@pytest.mark.parametrize("rule_id,evaluator,measure", MORTGAGE_EVALUATORS)
def test_a_missing_rule_is_indeterminate_never_a_pass(rule_id, evaluator, measure):
    """Absence of evidence is not permission (POL-GEN-001 GEN-ELG-005).

    This is the property that makes the coverage extension safe: a retrieval
    regression shows up as a referral, not as an approval nobody checked.
    """
    packet = {
        "application_date": "2026-07-08",
        "product_family": "conventional_conforming",
        "loan_purpose": "purchase",
        "credit_accounts": [{"account_type": "auto_loan", "lates_30d_24m": "0"}],
        "supplied_documents": [{"document_type": "paystub", "document_date": "2026-07-01"}],
    }
    evaluations = evaluator({"ratios": {}, "amounts": {}}, packet, [])
    found = by_measure(evaluations, measure)
    assert found is not None, f"{measure} produced no evaluation at all"
    assert found.verdict == Verdict.INDETERMINATE, (
        f"{rule_id} was absent and {measure} returned {found.verdict}"
    )
    assert "not retrieved" in found.detail


@pytest.mark.parametrize("rule_id,evaluator,measure", MORTGAGE_EVALUATORS)
def test_no_evaluator_invents_a_breach_from_a_missing_rule(rule_id, evaluator, measure):
    evaluations = evaluator({"ratios": {}, "amounts": {}}, {}, [])
    assert not [e for e in evaluations if e.verdict == Verdict.FAIL]


# ================================================================== DOC-REQ


DOC_REQ_001 = rule(
    "DOC-REQ-001",
    "Every application requires a completed application form, identity evidence, "
    "a credit report, income evidence, asset evidence, and a valuation.\n"
    "| Parameter | Value |\n| --- | --- |\n"
    "| `baseline` | application, identity, credit report, income evidence, asset "
    "evidence, valuation |\n| `purchase_additional` | executed purchase contract |\n",
    "POL-DOC-001 v1.0 rule DOC-REQ-001",
)

DOC_REQ_002 = rule(
    "DOC-REQ-002",
    "Measured to the note date.\n"
    "| Parameter | Value |\n| --- | --- |\n"
    "| `paystub_days` | 30 |\n| `asset_statement_days` | 60 |\n"
    "| `employment_verification_days` | 60 |\n| `tax_return_days` | 120 |\n",
    "POL-DOC-001 v1.0 rule DOC-REQ-002",
)

FULL_DOCUMENT_SET = [
    {"document_type": "loan_application_summary", "document_date": "2026-07-01"},
    {"document_type": "identity_verification_summary", "document_date": "2026-07-01"},
    {"document_type": "credit_report_summary", "document_date": "2026-07-01"},
    {"document_type": "paystub", "document_date": "2026-07-01"},
    {"document_type": "bank_statement", "document_date": "2026-06-20"},
    {"document_type": "appraisal_report", "document_date": "2026-06-14"},
    {"document_type": "purchase_agreement", "document_date": "2026-06-12"},
]


def test_a_complete_and_fresh_document_set_passes():
    packet = {
        "application_date": "2026-07-08",
        "loan_purpose": "purchase",
        "supplied_documents": FULL_DOCUMENT_SET,
    }
    evaluations = evaluate_documentation({}, packet, [DOC_REQ_001, DOC_REQ_002])
    assert by_measure(evaluations, "document_completeness").verdict == Verdict.PASS
    assert by_measure(evaluations, "document_freshness").verdict == Verdict.PASS


def test_an_incomplete_file_is_suspended_never_declined():
    """DOC-REQ-004: the difference matters to the borrower.

    A borrower can supply a document. They cannot un-decline a file.
    """
    packet = {
        "application_date": "2026-07-08",
        "loan_purpose": "purchase",
        "supplied_documents": [d for d in FULL_DOCUMENT_SET
                               if d["document_type"] != "appraisal_report"],
    }
    evaluations = evaluate_documentation({}, packet, [DOC_REQ_001, DOC_REQ_002])
    completeness = by_measure(evaluations, "document_completeness")
    assert completeness.verdict == Verdict.INDETERMINATE
    assert completeness.verdict != Verdict.FAIL
    assert "valuation" in completeness.factors
    assert "SUSPENDED_INCOMPLETE" in completeness.detail


def test_a_stale_document_raises_a_refresh_rather_than_a_failure():
    packet = {
        "application_date": "2026-07-08",
        "loan_purpose": "purchase",
        "supplied_documents": [
            *[d for d in FULL_DOCUMENT_SET if d["document_type"] != "paystub"],
            # 38 days old against a 30-day window.
            {"document_type": "paystub", "document_date": "2026-05-31"},
        ],
    }
    evaluations = evaluate_documentation({}, packet, [DOC_REQ_001, DOC_REQ_002])
    freshness = by_measure(evaluations, "document_freshness")
    assert freshness.verdict == Verdict.INDETERMINATE
    assert "paystub" in freshness.detail


def test_the_freshness_window_comes_from_the_rule_not_the_code():
    """Move the number in the policy and the verdict moves with it."""
    packet = {
        "application_date": "2026-07-08",
        "loan_purpose": "purchase",
        "supplied_documents": [
            *[d for d in FULL_DOCUMENT_SET if d["document_type"] != "paystub"],
            {"document_type": "paystub", "document_date": "2026-05-31"},
        ],
    }
    generous = rule(
        "DOC-REQ-002",
        "| Parameter | Value |\n| --- | --- |\n| `paystub_days` | 90 |\n",
        "POL-DOC-001 v1.0 rule DOC-REQ-002",
    )
    evaluations = evaluate_documentation({}, packet, [DOC_REQ_001, generous])
    assert by_measure(evaluations, "document_freshness").verdict == Verdict.PASS


# ================================================================== EMP-CNT


EMP_CNT_001 = rule(
    "EMP-CNT-001",
    "A 24-month employment history is required.\n"
    "| Parameter | Value |\n| --- | --- |\n"
    "| `required_history_months` | 24 |\n| `shortfall_treatment` | refer, not fail |\n",
    "POL-EMP-002 v1.0 rule EMP-CNT-001",
)


def test_a_two_year_history_passes():
    packet = {
        "application_date": "2026-07-08",
        "employment": [{"declared_start_date": "2022-01-08", "is_current": True}],
    }
    evaluations = evaluate_employment_continuity({}, packet, [EMP_CNT_001])
    history = by_measure(evaluations, "employment_history_months")
    assert history.verdict == Verdict.PASS
    assert history.observed >= 24


def test_a_short_history_refers_and_does_not_fail():
    """EMP-CNT-001 says so in as many words: refer, not fail."""
    packet = {
        "application_date": "2026-07-08",
        "employment": [{"declared_start_date": "2025-06-01", "is_current": True}],
    }
    evaluations = evaluate_employment_continuity({}, packet, [EMP_CNT_001])
    history = by_measure(evaluations, "employment_history_months")
    assert history.verdict == Verdict.INDETERMINATE
    assert history.verdict != Verdict.FAIL
    assert summarize(evaluations)["breaches"] == []


def test_overlapping_employment_is_counted_once():
    """A second job started before the first ended is not double history.

    Summing the spans would turn 14 months into 26 and pass a file that should
    have been referred.
    """
    packet = {
        "application_date": "2026-07-08",
        "employment": [
            {"declared_start_date": "2025-05-08", "end_date": "2026-02-01"},
            {"declared_start_date": "2025-09-01", "is_current": True},
        ],
    }
    evaluations = evaluate_employment_continuity({}, packet, [EMP_CNT_001])
    history = by_measure(evaluations, "employment_history_months")
    # May 2025 to July 2026 inclusive is 15 months, not 9 + 11.
    assert history.observed == pytest.approx(15.0)


# ================================================================== CRD-EVT


CRD_EVT_001 = rule(
    "CRD-EVT-001",
    "| Parameter | Value |\n| --- | --- |\n"
    "| `chapter_7_bankruptcy_months` | 48 |\n| `foreclosure_months` | 84 |\n"
    "| `short_sale_months` | 48 |\n",
    "POL-CRD-002 v1.0 rule CRD-EVT-001",
)


def test_a_file_with_no_credit_event_is_not_applicable():
    """Not a pass by luck — a statement that the family does not apply."""
    evaluations = evaluate_credit_events({}, {"credit_events": []}, [CRD_EVT_001])
    assert evaluations[0].verdict == Verdict.NOT_APPLICABLE


def test_a_seasoned_bankruptcy_passes():
    packet = {
        "application_date": "2026-07-08",
        "credit_events": [{"event_type": "chapter_7_bankruptcy",
                           "anchor_date": "2021-06-12", "status": "resolved"}],
    }
    evaluations = evaluate_credit_events({}, packet, [CRD_EVT_001])
    seasoning = by_measure(evaluations, "seasoning_chapter_7_bankruptcy")
    assert seasoning.verdict == Verdict.PASS
    assert seasoning.threshold == 48
    assert seasoning.observed >= 48


def test_an_unseasoned_foreclosure_fails():
    """Date arithmetic with no judgement in it, so a hard fail is right."""
    packet = {
        "application_date": "2026-07-08",
        "credit_events": [{"event_type": "foreclosure", "anchor_date": "2024-01-01"}],
    }
    evaluations = evaluate_credit_events({}, packet, [CRD_EVT_001])
    seasoning = by_measure(evaluations, "seasoning_foreclosure")
    assert seasoning.verdict == Verdict.FAIL
    assert seasoning.threshold == 84
    assert "extenuating circumstances" in seasoning.detail


def test_seasoning_is_recomputed_from_the_anchor_not_read_off_the_file():
    """A figure computed at some other moment is not the one that governs."""
    packet = {
        "application_date": "2026-07-08",
        "credit_events": [{
            "event_type": "chapter_7_bankruptcy",
            "anchor_date": "2026-01-01",
            "seasoning_months": "999",   # stale, and wrong
        }],
    }
    evaluations = evaluate_credit_events({}, packet, [CRD_EVT_001])
    seasoning = by_measure(evaluations, "seasoning_chapter_7_bankruptcy")
    assert seasoning.observed == 6.0
    assert seasoning.verdict == Verdict.FAIL


# ================================================================== GEN-ELG


GEN_ELG_003 = rule(
    "GEN-ELG-003",
    "| Parameter | Value |\n| --- | --- |\n"
    "| `conforming_baseline_one_unit_2026` | 832,750 |\n"
    "| `high_cost_ceiling_one_unit_2026` | 1,249,125 |\n",
    "POL-GEN-001 v1.0 rule GEN-ELG-003",
)


def test_a_conforming_loan_within_the_limit_passes():
    packet = {
        "product_family": "conventional_conforming",
        "property_costs": {"note_amount": "432400.00"},
    }
    evaluations = evaluate_general_eligibility({}, packet, [GEN_ELG_003])
    assert by_measure(evaluations, "programme_loan_limit").verdict == Verdict.PASS


def test_a_jumbo_loan_is_not_failed_by_the_conforming_limit():
    """"A loan above the conforming limit is not ineligible — it is simply not
    conforming." Failing it would decline every jumbo file in the book."""
    packet = {
        "product_family": "jumbo",
        "property_costs": {"note_amount": "1500000.00"},
    }
    evaluations = evaluate_general_eligibility({}, packet, [GEN_ELG_003])
    limit = by_measure(evaluations, "programme_loan_limit")
    assert limit.verdict == Verdict.NOT_APPLICABLE
    assert limit.verdict != Verdict.FAIL


def test_a_conforming_loan_over_the_ceiling_fails():
    packet = {
        "product_family": "conventional_conforming",
        "property_costs": {"note_amount": "1400000.00"},
    }
    evaluations = evaluate_general_eligibility({}, packet, [GEN_ELG_003])
    assert by_measure(evaluations, "programme_loan_limit").verdict == Verdict.FAIL


# ================================================================== JMB-ELG


def test_the_jumbo_overlay_does_not_touch_a_conforming_file():
    """Its 720 floor and 75% cap are not conforming policy."""
    evaluations = evaluate_jumbo(
        {"ratios": {"ltv": 0.92}},
        {"product_family": "conventional_conforming",
         "credit_summary": {"representative_score": "640"}},
        [],
    )
    assert all(e.verdict == Verdict.NOT_APPLICABLE for e in evaluations)


def test_the_jumbo_overlay_applies_its_tighter_bars():
    jmb = rule(
        "JMB-ELG-002",
        "| Parameter | Value |\n| --- | --- |\n"
        "| `max_ltv_primary_residence` | 75% |\n| `min_representative_score` | 720 |\n",
        "POL-JUMBO-001 v2.0 rule JMB-ELG-002",
    )
    evaluations = evaluate_jumbo(
        {"ratios": {"ltv": 0.80}},
        {"product_family": "jumbo", "occupancy_type": "primary_residence",
         "credit_summary": {"representative_score": "700"}},
        [jmb],
    )
    assert by_measure(evaluations, "jumbo_ltv").verdict == Verdict.FAIL
    assert by_measure(evaluations, "jumbo_representative_score").verdict == Verdict.FAIL


# ================================================================== VAL-APR


def test_the_lower_of_contract_and_appraised_value_governs():
    val = rule(
        "VAL-APR-002",
        "| Parameter | Value |\n| --- | --- |\n"
        "| `value_used` | lower of contract price and appraised value |\n"
        "| `upward_adjustment_permitted` | no |\n",
        "POL-VAL-001 v2.0 rule VAL-APR-002",
    )
    packet = {
        "subject_property": {"purchase_price": "470000.00"},
        "property_costs": {"appraised_value": "450000.00",
                           "value_used_for_ltv": "450000.00"},
    }
    evaluations = evaluate_valuation({}, packet, [val])
    assert by_measure(evaluations, "value_used_for_ltv").verdict == Verdict.PASS

    packet["property_costs"]["value_used_for_ltv"] = "470000.00"
    evaluations = evaluate_valuation({}, packet, [val])
    assert by_measure(evaluations, "value_used_for_ltv").verdict == Verdict.FAIL


def test_a_valuation_inside_the_update_window_is_curable_not_fatal():
    val = rule(
        "VAL-APR-003",
        "| Parameter | Value |\n| --- | --- |\n"
        "| `max_age_days` | 120 |\n| `update_window_days` | 240 |\n",
        "POL-VAL-001 v2.0 rule VAL-APR-003",
    )
    packet = {
        "application_date": "2026-07-08",
        "supplied_documents": [
            {"document_type": "appraisal_report", "document_date": "2026-01-15"},
        ],
    }
    evaluations = evaluate_valuation({}, packet, [val])
    age = by_measure(evaluations, "valuation_age_days")
    assert age.verdict == Verdict.INDETERMINATE   # 174 days: curable by an update
    assert "update window" in age.detail

    packet["supplied_documents"][0]["document_date"] = "2025-06-01"
    evaluations = evaluate_valuation({}, packet, [val])
    assert by_measure(evaluations, "valuation_age_days").verdict == Verdict.FAIL


# ================================================================== EDU-UW


EDU_UW_001 = rule(
    "EDU-UW-001",
    "| Parameter | Requirement |\n|---|---|\n"
    "| Minimum loan amount | $1,000 per academic year |\n"
    "| Maximum loan amount | $75,000 per academic year |\n"
    "| Cosigner requirement | Required if borrower FICO < 700 or borrower has a "
    "THIN file |\n",
    "POL-002 EDU-UW-001",
)


def test_the_education_product_selects_its_own_underwriting_rule():
    """A GR file judged against UG's criteria is judged against the wrong cap."""
    packet = {"product_code": "GR", "requested_amount": 90000}
    evaluations = evaluate_education_underwriting({}, packet, [EDU_UW_001])
    # EDU-UW-002 governs GR, and it was not supplied.
    assert all(e.verdict == Verdict.INDETERMINATE for e in evaluations)
    assert "EDU-UW-002" in evaluations[0].rule_id


def test_a_loan_above_the_product_cap_fails():
    packet = {"product_code": "UG", "requested_amount": 90000,
              "credit_bureau": [{"subject_type": "borrower", "fico_score": 720,
                                 "file_status": "ESTABLISHED"}]}
    evaluations = evaluate_education_underwriting({}, packet, [EDU_UW_001])
    amount = by_measure(evaluations, "requested_amount")
    assert amount.verdict == Verdict.FAIL
    assert amount.threshold == 75000


def test_a_thin_file_needs_a_cosigner_and_having_one_passes():
    packet = {
        "product_code": "UG", "requested_amount": 13000, "has_cosigner": True,
        "credit_bureau": [{"subject_type": "borrower", "fico_score": 683,
                           "file_status": "THIN"}],
    }
    evaluations = evaluate_education_underwriting({}, packet, [EDU_UW_001])
    required = by_measure(evaluations, "cosigner_required")
    assert required.verdict == Verdict.PASS
    assert "THIN" in required.detail

    packet["has_cosigner"] = False
    evaluations = evaluate_education_underwriting({}, packet, [EDU_UW_001])
    assert by_measure(evaluations, "cosigner_required").verdict == Verdict.FAIL


# ================================================================== EDU-RG


EDU_RG_001 = rule(
    "EDU-RG-001",
    "| Grade | FICO Minimum | DTI Maximum | Fixed Rate (Base) |\n|---|---|---|---|\n"
    "| A1 | 780 | 25% | 4.99% |\n| A2 | 760 | 30% | 5.49% |\n"
    "| A3 | 740 | 35% | 5.99% |\n| B1 | 720 | 38% | 6.49% |\n"
    "| B2 | 700 | 40% | 6.99% |\n| C2 | 650 | 44% | 8.49% |\n"
    "| C3 | 640 | 45% | 8.99% |\n| D3 | 580 | 50% | 11.99% |\n"
    "| E1 | 560 | -- | DECLINE |\n| E3 | < 540 | -- | DECLINE |\n",
    "POL-003 EDU-RG-001",
)


def test_the_worse_of_fico_and_dti_governs_the_grade():
    """"if the FICO qualifies for one band but the DTI qualifies for a lower
    band, the lower (worse) band governs." Getting this backwards grades most
    thin files a band or two better than policy allows."""
    packet = {"credit_bureau": [{"subject_type": "borrower", "fico_score": 780}]}
    evaluations = evaluate_education_risk_grade(
        {"ratios": {"education_dti": 0.44}}, packet, [EDU_RG_001]
    )
    grade = by_measure(evaluations, "risk_grade")
    assert "grade:C2" in grade.factors, grade.detail
    assert grade.verdict == Verdict.PASS


def test_an_e_band_score_is_an_automatic_decline():
    packet = {"credit_bureau": [{"subject_type": "borrower", "fico_score": 520}]}
    evaluations = evaluate_education_risk_grade(
        {"ratios": {"education_dti": 0.20}}, packet, [EDU_RG_001]
    )
    grade = by_measure(evaluations, "risk_grade")
    assert grade.verdict == Verdict.FAIL
    assert "no cosigner cure" in grade.detail


def test_the_stronger_profile_grades_the_file_when_a_cosigner_is_present():
    packet = {
        "has_cosigner": True,
        "credit_bureau": [
            {"subject_type": "borrower", "fico_score": 610},
            {"subject_type": "cosigner", "fico_score": 760},
        ],
    }
    evaluations = evaluate_education_risk_grade(
        {"ratios": {"education_dti": 0.28}}, packet, [EDU_RG_001]
    )
    grade = by_measure(evaluations, "risk_grade")
    assert "graded_on:cosigner" in grade.factors
    assert grade.observed == 760


# ================================================================= EDU-COS


EDU_COS_001 = rule(
    "EDU-COS-001",
    "| Criterion | Requirement |\n|---|---|\n"
    "| Citizenship / residency | Must be a US citizen (US_CITIZEN) or lawful "
    "permanent resident (PERM_RESIDENT). |\n"
    "| Minimum age | 21 years old at the time of application |\n"
    "| FICO score | Minimum 650 |\n"
    "| OFAC / sanctions | A match is a knockout with no exception. |\n",
    "POL-004 EDU-COS-001",
)


def test_no_cosigner_is_not_a_cosigner_failure():
    """Whether one was *required* is EDU-UW's question, answered separately.

    Failing this for every solo graduate borrower would decline most of the GR
    book for the absence of something it does not need.
    """
    evaluations = evaluate_education_cosigner({}, {"product_code": "GR"}, [EDU_COS_001])
    assert evaluations[0].verdict == Verdict.NOT_APPLICABLE


def test_an_ineligible_cosigner_fails_on_the_criterion_it_breaks():
    packet = {
        "has_cosigner": True,
        "cosigner": {"citizenship_status": "F1_VISA", "dob": "1996-01-01",
                     "cosigner_notice_acknowledged": True},
        "credit_bureau": [{"subject_type": "cosigner", "fico_score": 700,
                           "bankruptcy_flag": False}],
        "submitted_at": "2026-07-11",
    }
    evaluations = evaluate_education_cosigner({}, packet, [EDU_COS_001])
    assert by_measure(evaluations, "cosigner_citizenship").verdict == Verdict.FAIL
    assert by_measure(evaluations, "cosigner_age").verdict == Verdict.PASS
    assert by_measure(evaluations, "cosigner_fico").verdict == Verdict.PASS


def test_the_cosigner_fico_floor_comes_from_the_rule():
    packet = {
        "has_cosigner": True,
        "cosigner": {"citizenship_status": "US_CITIZEN", "dob": "1970-01-01"},
        "credit_bureau": [{"subject_type": "cosigner", "fico_score": 630}],
        "submitted_at": "2026-07-11",
    }
    evaluations = evaluate_education_cosigner({}, packet, [EDU_COS_001])
    fico = by_measure(evaluations, "cosigner_fico")
    assert fico.verdict == Verdict.FAIL
    assert fico.threshold == 650


# ================================================================ EDU-INTL


def test_the_international_family_does_not_apply_to_a_domestic_file():
    evaluations = evaluate_education_international({}, {"product_code": "UG"}, [])
    assert evaluations[0].verdict == Verdict.NOT_APPLICABLE


def test_an_ineligible_visa_fails():
    visa = rule(
        "EDU-INTL-001",
        "Only F-1 and J-1 visa holders are eligible for the INTL loan product.",
        "POL-012 EDU-INTL-001",
    )
    packet = {"product_code": "INTL", "international_details": {"visa_type": "H-1B"}}
    evaluations = evaluate_education_international({}, packet, [visa])
    assert by_measure(evaluations, "visa_eligibility").verdict == Verdict.FAIL


def test_an_unverifiable_i94_refers_rather_than_declining():
    """EDU-INTL-003 says REFER_MANUAL. Refusing an applicant for a CBP outage
    would be the system's failure charged to them."""
    i94 = rule(
        "EDU-INTL-003",
        "If the I-94 cannot be verified the application is assigned a disposition "
        "of REFER_MANUAL.",
        "POL-012 EDU-INTL-003",
    )
    packet = {"product_code": "INTL",
              "international_details": {"visa_type": "F-1", "i94_verified": False}}
    evaluations = evaluate_education_international({}, packet, [i94])
    verification = by_measure(evaluations, "i94_verification")
    assert verification.verdict == Verdict.INDETERMINATE
    assert verification.verdict != Verdict.FAIL


def test_the_no_cosigner_pathway_requires_all_four_conditions():
    pathway = rule(
        "EDU-INTL-004",
        "International students may apply without a U.S.-based cosigner only if all "
        "of the following are satisfied: Tier A or Tier B school, OPT eligibility, "
        "and at least **12** months of post-study work authorization remaining.",
        "POL-012 EDU-INTL-004",
    )
    packet = {
        "product_code": "INTL",
        "international_details": {"visa_type": "F-1", "opt_eligible": True,
                                  "post_study_work_months": 36},
        "school": {"school_risk_tier": "A"},
    }
    evaluations = evaluate_education_international({}, packet, [pathway])
    assert by_measure(evaluations, "no_cosigner_pathway").verdict == Verdict.PASS

    packet["school"]["school_risk_tier"] = "C"
    evaluations = evaluate_education_international({}, packet, [pathway])
    pathway_result = by_measure(evaluations, "no_cosigner_pathway")
    assert pathway_result.verdict == Verdict.FAIL
    assert "Tier C" in pathway_result.detail


# =============================================== the borderline-band regression


def test_a_non_ratio_measure_never_trips_the_borderline_band():
    """UWR-HRV-001's band is in percentage points and means nothing otherwise.

    A freshness evaluation reporting 0 days over a 0-day allowance read as
    "within 2 percentage points of its limit" and referred every clean file.
    Every measure now declares a unit, and the trigger table skips what is not
    a ratio.
    """
    from src.review_triggers import evaluate_review_triggers

    packet = {
        "application_date": "2026-07-08",
        "loan_purpose": "purchase",
        "supplied_documents": FULL_DOCUMENT_SET,
        "product_family": "conventional_conforming",
    }
    evaluations = evaluate_documentation({}, packet, [DOC_REQ_001, DOC_REQ_002])
    eligibility = summarize(evaluations)

    uwr = rule(
        "UWR-HRV-001",
        "| Parameter | Value |\n| --- | --- |\n| `borderline_band_pct_points` | 2.0 |\n",
        "POL-UWR-001 v1.0 rule UWR-HRV-001",
    )
    review = evaluate_review_triggers(
        LendingProductDomain.MORTGAGE, {"ratios": {}}, packet, [uwr], eligibility,
        {"level": "LOW", "flags": []},
    )
    borderline = [t for t in review.as_dict()["triggers"]
                  if t["trigger"] == "borderline_affordability"]
    assert borderline == [], f"a non-ratio measure tripped the band: {borderline}"


def test_every_evaluation_declares_a_unit():
    """The field only protects anything if nothing forgets to set it."""
    packet = {
        "application_date": "2026-07-08",
        "loan_purpose": "purchase",
        "product_family": "conventional_conforming",
        "supplied_documents": FULL_DOCUMENT_SET,
        "property_costs": {"note_amount": "432400.00", "appraised_value": "479400.00",
                           "value_used_for_ltv": "470000.00"},
        "subject_property": {"purchase_price": "470000.00"},
        "credit_accounts": [{"account_type": "auto_loan", "lates_30d_24m": "0"}],
        "credit_events": [],
        "asset_transactions": [],
        "employment": [{"declared_start_date": "2022-01-08", "is_current": True}],
    }
    evaluations = evaluate(
        LendingProductDomain.MORTGAGE,
        {"ratios": {"back_end_dti": 0.30, "ltv": 0.92},
         "amounts": {"qualifying_monthly_income": 8000.0}},
        packet,
        [DOC_REQ_001, DOC_REQ_002, EMP_CNT_001, CRD_EVT_001, GEN_ELG_003],
    )
    assert evaluations
    for evaluation in evaluations:
        assert evaluation.unit, f"{evaluation.measure} declares no unit"
        assert evaluation.as_dict()["unit"] == evaluation.unit


def test_the_required_rule_list_matches_what_the_engine_evaluates():
    """A rule the engine needs that retrieval never fetches keeps reporting
    INDETERMINATE; a rule fetched that nothing evaluates is wasted retrieval."""
    from src.graph import REQUIRED_RULES

    mortgage = set(REQUIRED_RULES["MORTGAGE"])
    education = set(REQUIRED_RULES["EDUCATION_LOAN"])

    # Every family the extended evaluators reference by id must be fetchable.
    for rule_id in ("DOC-REQ-001", "DOC-REQ-002", "EMP-CNT-001", "CRD-EVT-001",
                    "CRD-DLQ-001", "CRD-DLQ-002", "AST-SRC-002", "VAL-APR-002",
                    "VAL-APR-003", "GEN-ELG-003", "GEN-ELG-006"):
        assert rule_id in mortgage, f"{rule_id} is evaluated but never fetched"

    for rule_id in ("EDU-UW-001", "EDU-COS-001", "EDU-COS-002", "EDU-RG-001",
                    "EDU-INTL-001", "EDU-INTL-003", "EDU-INTL-004"):
        assert rule_id in education, f"{rule_id} is evaluated but never fetched"

    # And the two products' lists do not bleed into each other.
    assert not any(r.startswith("EDU-") for r in mortgage)
    assert all(r.startswith("EDU-") for r in education)
