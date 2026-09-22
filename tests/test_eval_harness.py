"""The evaluation harness itself, and the ways it could quietly lie.

An evaluation is only worth what its harness is worth. Three failure modes here
produce numbers that look fine and are not:

* **replay** — a stable checkpoint thread makes the second run resume the first
  one's final state instead of re-running, so the report describes code that has
  since changed;
* **pooling** — averaging 75 mortgage cases with 20 education ones produces a
  mortgage score with a rounding error attached;
* **an inverted metric** — DeepEval 4.x reports hallucination as 1.0-is-good, so
  publishing the raw score under the name "hallucination rate" states the
  opposite of the truth.

Each is covered below. None was hypothetical: the first was observed as a
13-second case returning in 0.2 with no retrieval performed.
"""

from __future__ import annotations

import json

import pytest

from eval.agent.dataset import (
    APPROVE,
    APPROVE_WITH_CONDITIONS,
    DECLINE,
    EXPRESSIBLE_FAMILIES,
    REFER,
    load_cases,
    load_education_cases,
    load_mortgage_cases,
    outcome_family,
)
from eval.agent.run_agent_eval import CaseOutcome, macro_average, summarize
from src.domain import LendingProductDomain


# ============================================================== outcome families


@pytest.mark.parametrize("recorded,family", [
    ("APPROVE", APPROVE),
    ("APPROVE_RECOMMENDATION", APPROVE),
    ("DECLINE", DECLINE),
    ("DECLINE_RECOMMENDATION", DECLINE),
    ("REFER", REFER),
    ("REFER_MANUAL", REFER),
    ("REFER_RECOMMENDATION", REFER),
    ("MANUAL_REVIEW_REQUIRED", REFER),
    ("PENDING_HUMAN_REVIEW", REFER),
    ("SUSPENDED_INCOMPLETE", REFER),
    ("APPROVE_WITH_CONDITIONS", APPROVE_WITH_CONDITIONS),
])
def test_every_recorded_spelling_maps_to_one_family(recorded, family):
    """The two golden sources spell the same outcome differently."""
    assert outcome_family(recorded) == family


def test_conditional_approval_is_not_folded_into_approval():
    """Scoring it as APPROVE would credit an answer the system cannot give.

    `recommendation_node` emits approve, refer or decline and nothing else. Six
    golden cases expect `APPROVE_WITH_CONDITIONS`; they stay their own class and
    are counted, not absorbed.
    """
    assert APPROVE_WITH_CONDITIONS not in EXPRESSIBLE_FAMILIES
    assert outcome_family("APPROVE_WITH_CONDITIONS") != APPROVE


def test_an_unknown_spelling_is_none_rather_than_a_guess():
    assert outcome_family("SOMETHING_NEW") is None
    assert outcome_family(None) is None
    assert outcome_family("") is None


# ===================================================================== the cases


def test_both_products_load_with_expectations():
    mortgage, education = load_mortgage_cases(), load_education_cases()
    assert len(mortgage) == 75
    assert len(education) == 20
    assert all(c.expected_outcome for c in mortgage), "a mortgage case has no expected outcome"
    assert all(c.expected_outcome for c in education), "an education case has no expected outcome"


def test_every_case_points_at_a_packet_that_exists():
    missing = [c.case_id for c in load_cases() if not c.packet_path.exists()]
    assert not missing, missing


def test_the_limit_is_per_product_not_overall():
    """A flat limit would leave a 'both products' run that was mostly mortgage."""
    cases = load_cases(limit_per_product=4)
    by_product = {}
    for case in cases:
        by_product.setdefault(case.product, []).append(case)
    assert len(by_product[LendingProductDomain.MORTGAGE]) == 4
    assert len(by_product[LendingProductDomain.EDUCATION_LOAN]) == 4


def test_mortgage_expectations_come_from_the_recommendation_stage():
    """Not the later credit_decision row, which records a human's own conclusion.

    Scoring against that would penalise the copilot for failing to predict a
    judgement made after it ran.
    """
    from eval.agent.dataset import _mortgage_expectations

    expectations = _mortgage_expectations()
    assert len(expectations) == 75, "one row per application, from one stage only"


# ================================================================ no golden leak


def test_the_dataset_module_is_not_importable_from_runtime_code(repo_root):
    """`src/` must never reach the golden sets."""
    import re

    offenders = []
    for path in (repo_root / "src").rglob("*.py"):
        text = path.read_text(encoding="utf-8", errors="replace")
        if re.search(r"^\s*(from|import)\s+eval\b", text, re.MULTILINE):
            offenders.append(str(path.relative_to(repo_root)))
    assert not offenders, f"runtime modules importing evaluation code: {offenders}"


# ==================================================================== aggregation


def _outcome(product, expected, actual, **kwargs):
    from eval.agent.dataset import AgentCase
    from pathlib import Path

    case = AgentCase(
        case_id=f"C-{expected}-{actual}",
        product=product,
        application_id="APP-X",
        packet_path=Path("nowhere.json"),
        question="?",
        expected_outcome=expected,
    )
    result = CaseOutcome(case=case, outcome=actual)
    for key, value in kwargs.items():
        setattr(result, key, value)
    return result


def test_macro_averaging_gives_each_product_equal_weight():
    """The property the whole averaging choice exists for.

    Mortgage is perfect over 10 cases, education fails all 2. A pooled mean would
    read 0.83 and hide it; the macro mean reads 0.50 and does not.
    """
    mortgage = [
        _outcome(LendingProductDomain.MORTGAGE, APPROVE, APPROVE) for _ in range(10)
    ]
    education = [
        _outcome(LendingProductDomain.EDUCATION_LOAN, APPROVE, DECLINE) for _ in range(2)
    ]

    per_product = {
        "MORTGAGE": summarize(mortgage),
        "EDUCATION_LOAN": summarize(education),
    }
    assert per_product["MORTGAGE"]["outcome_accuracy"] == 1.0
    assert per_product["EDUCATION_LOAN"]["outcome_accuracy"] == 0.0

    macro = macro_average(per_product)
    assert macro["outcome_accuracy"] == 0.5, "a pooled mean would have read 0.83"
    assert macro["cases"] == 12, "counts sum rather than average"


def test_inexpressible_cases_are_excluded_from_accuracy_but_still_counted():
    results = [
        _outcome(LendingProductDomain.MORTGAGE, APPROVE, APPROVE),
        _outcome(LendingProductDomain.MORTGAGE, APPROVE_WITH_CONDITIONS, APPROVE),
    ]
    summary = summarize(results)
    assert summary["outcome_accuracy"] == 1.0, "the expressible case was correct"
    assert summary["outcome_accuracy_all_cases"] == 0.5, "and the other one still counts"
    assert summary["cases_with_inexpressible_expectation"] == 1


def test_directional_agreement_is_softer_than_exact_match():
    """A conditional approval is an approval in direction, if not in kind."""
    result = _outcome(LendingProductDomain.MORTGAGE, APPROVE_WITH_CONDITIONS, APPROVE)
    assert result.outcome_correct is False
    assert result.direction_correct is True


def test_a_decline_scored_against_an_approval_is_wrong_in_both_senses():
    result = _outcome(LendingProductDomain.MORTGAGE, APPROVE, DECLINE)
    assert result.outcome_correct is False
    assert result.direction_correct is False


def test_an_errored_case_is_excluded_from_quality_but_counted_as_an_error():
    ok = _outcome(LendingProductDomain.MORTGAGE, APPROVE, APPROVE)
    broken = _outcome(LendingProductDomain.MORTGAGE, APPROVE, None, error="boom")
    summary = summarize([ok, broken])
    assert summary["cases"] == 2
    assert summary["completed"] == 1
    assert summary["errors"] == 1
    assert summary["outcome_accuracy"] == 1.0, "a crashed run must not score as a miss"


def test_summarize_reports_none_rather_than_zero_when_nothing_was_measured():
    """Zero and 'not measured' are different claims."""
    summary = summarize([])
    assert summary["outcome_accuracy"] is None
    assert summary["judge_faithfulness"] is None
    assert summary["cases"] == 0


# ================================================== the hallucination direction


@pytest.mark.parametrize("score,rate", [(1.0, 0.0), (0.0, 1.0), (0.75, 0.25), (0.5, 0.5)])
def test_the_hallucination_rate_inverts_deepevals_score(score, rate):
    """DeepEval 4.x scores hallucination 1.0-is-grounded.

    Publishing the raw score as a "hallucination rate" would state the opposite
    of the truth — a perfectly grounded run would read as fully hallucinated.
    """
    from eval.agent.run_agent_eval import hallucination_rate_from

    assert hallucination_rate_from(score) == rate


def test_a_grounded_run_reports_a_zero_hallucination_rate():
    """The direction that matters, stated on its own so it cannot be misread."""
    from eval.agent.run_agent_eval import hallucination_rate_from

    perfectly_grounded_score = 1.0
    assert hallucination_rate_from(perfectly_grounded_score) == 0.0


def test_a_case_with_no_narrative_is_not_judged():
    """Scoring the deterministic fallback would measure the fallback."""
    from eval.agent.run_agent_eval import judge_case

    result = CaseOutcome(case=load_mortgage_cases()[0], narrative="", evidence_texts=[])
    scores = judge_case(result, judge=None)
    assert scores["judged"] is False


def test_an_errored_case_is_not_judged():
    from eval.agent.run_agent_eval import judge_case

    result = CaseOutcome(
        case=load_mortgage_cases()[0], narrative="text", evidence_texts=["x"], error="boom"
    )
    assert judge_case(result, judge=None)["judged"] is False


# ================================================================ report shape


def test_the_case_record_round_trips_through_json():
    """It is committed as JSONL, so it has to serialize."""
    result = _outcome(LendingProductDomain.MORTGAGE, APPROVE, APPROVE)
    payload = json.loads(json.dumps(result.as_dict(), default=str))
    assert payload["expected_outcome"] == APPROVE
    assert payload["actual_outcome"] == APPROVE
    assert payload["outcome_correct"] is True


def test_compound_determining_rule_ids_are_split_on_both_separators():
    """`determining_rule_ids` uses ';' and '|', sometimes in the same file.

    A row reading "AST-FTC-003|AST-RSV-002|AST-SRC-001" records three rules that
    decided together. Splitting on one separator leaves it as a single nonsense
    identifier, which silently understates citation recall and miscounts rule
    coverage — both quietly, because a wrong identifier still looks like an
    identifier.
    """
    from eval.agent.dataset import _mortgage_expectations

    expectations = _mortgage_expectations()
    all_ids = {rule for entry in expectations.values() for rule in entry["rule_ids"]}

    assert all_ids, "no determining rules were parsed at all"
    for rule_id in all_ids:
        assert "|" not in rule_id, f"unsplit compound value: {rule_id}"
        assert ";" not in rule_id, f"unsplit compound value: {rule_id}"


def test_rule_coverage_reports_the_ceiling_for_both_products():
    """The number that makes `outcome_accuracy` interpretable.

    Reported per product, because the gap is not the same size on each: the
    mortgage engine now evaluates fourteen rule families and the education
    engine seven, and education's golden citations lean on families the
    mortgage set never touches. A coverage figure that averaged the two, or
    covered only mortgage, would hide exactly the asymmetry it exists to show.

    Education's figure is **zero**, and that is the answer rather than a broken
    check: every family its golden citations name is implemented. So this no
    longer asserts a non-zero count — that would force the measurement to
    under-report in order to stay green. It asserts the counter is live
    instead, by withdrawing a family and requiring it to reappear as a gap.
    """
    from eval.agent import dataset as dataset_module
    from eval.agent.dataset import IMPLEMENTED_RULE_FAMILIES, rule_coverage
    from src.domain import LendingProductDomain as D

    coverage = rule_coverage()
    assert set(coverage) >= {"MORTGAGE", "EDUCATION_LOAN"}

    for key, product in (("MORTGAGE", D.MORTGAGE), ("EDUCATION_LOAN", D.EDUCATION_LOAN)):
        entry = coverage[key]
        affected = entry["cases_needing_an_unimplemented_family"]
        assert entry["cases"] > 0, f"{key}: no cases loaded, so nothing was measured"
        assert 0 <= affected <= entry["cases"], f"{key}: {affected} of {entry['cases']}"
        assert entry["share_affected"] == pytest.approx(affected / entry["cases"], abs=0.001)

        gaps = set(entry["unimplemented_families_by_case_count"])
        assert not (gaps & set(IMPLEMENTED_RULE_FAMILIES[product])), (
            f"{key}: a family is listed as both implemented and missing"
        )
        for family in gaps:
            assert "|" not in family and ";" not in family, f"{key}: unsplit family {family}"


@pytest.mark.parametrize(
    "key,product,withdrawn",
    # Families the golden citations actually name. EDU-INC and EDU-GOV are
    # implemented but never cited, so withdrawing either would change nothing
    # and the guard would be vacuous.
    [("MORTGAGE", "MORTGAGE", "DTI-CONV"), ("EDUCATION_LOAN", "EDUCATION_LOAN", "EDU-UW")],
)
def test_the_coverage_counter_notices_a_family_that_is_not_implemented(
    key, product, withdrawn, monkeypatch
):
    """Guard the guard, now that zero is a legitimate answer for one product.

    Withdraw one implemented family and the cases that cite it must be counted
    as uncovered. A counter that reports zero because it is broken fails here;
    one that reports zero because the work is done passes.
    """
    from eval.agent import dataset as dataset_module
    from src.domain import LendingProductDomain as D

    domain = getattr(D, product)
    reduced = {
        prod: {k: v for k, v in families.items() if k != withdrawn}
        if prod is domain
        else families
        for prod, families in dataset_module.IMPLEMENTED_RULE_FAMILIES.items()
    }
    monkeypatch.setattr(dataset_module, "IMPLEMENTED_RULE_FAMILIES", reduced)

    entry = dataset_module.rule_coverage()[key]
    assert entry["cases_needing_an_unimplemented_family"] > 0, (
        f"{key}: withdrawing {withdrawn} changed nothing, so the counter is not reading "
        "the implemented set"
    )
    assert withdrawn in entry["unimplemented_families_by_case_count"], (
        f"{key}: {withdrawn} was withdrawn but is not reported as a gap"
    )


def test_nonexistent_education_citations_are_counted_not_charged_as_gaps():
    """9 of 59 education golden citations name rules that were never written.

    "Not implemented" and "does not exist in the corpus" are different problems,
    and only the first is ours. They are counted separately so neither hides the
    other.
    """
    from eval.agent.dataset import rule_coverage

    education = rule_coverage()["EDUCATION_LOAN"]
    assert education["citations_naming_a_nonexistent_rule"] == 9
    gaps = set(education["unimplemented_families_by_case_count"])
    assert not (gaps & {"EDU-CERT", "EDU-REFI", "EDU-AGG", "EDU-FRAUD"})
