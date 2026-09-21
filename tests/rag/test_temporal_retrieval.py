"""Effective-date-aware retrieval.

The mortgage corpus publishes six policies at two versions each, all switching on
2026-07-01. Retrieving the wrong version silently flips an underwriting decision,
so version selection is tested as a hard requirement rather than a preference.

The boundary triple ``APP-000055`` / ``APP-000056`` / ``APP-000057`` is the case
the corpus was built around: the same 44% back-end ratio, three different
outcomes, determined entirely by which version governs and what the file
documents.
"""

from __future__ import annotations

from datetime import date

import pytest

from src.domain import LendingProductDomain
from src.rag.applicability import (
    ApplicabilityStatus,
    classify,
    evaluate_temporal,
    scope_affinity,
    select_effective_versions,
)
from src.rag.models import PolicyRetrievalRequest

pytestmark = pytest.mark.integration

#: Every mortgage policy published at two versions, with the v2.0 effective date.
VERSIONED_POLICIES = {
    "POL-DTI-001": "2026-07-01",
    "POL-CRD-001": "2026-07-01",
    "POL-AST-003": "2026-07-01",
    "POL-INC-004": "2026-07-01",
    "POL-JUMBO-001": "2026-07-01",
    "POL-VAL-001": "2026-07-01",
}

BEFORE = date(2026, 6, 25)
AFTER = date(2026, 7, 8)


# ------------------------------------------------------------------------- unit level


def test_effective_window_inclusion():
    meta = {"effective_date": "2026-07-01", "expiration_date": None}
    assert evaluate_temporal(meta, date(2026, 7, 1)).applicable, "the boundary day is inclusive"
    assert evaluate_temporal(meta, date(2026, 7, 2)).applicable
    decision = evaluate_temporal(meta, date(2026, 6, 30))
    assert decision.status is ApplicabilityStatus.NOT_YET_EFFECTIVE


def test_expiry_is_inclusive_and_open_ended_when_absent():
    expiring = {"effective_date": "2026-01-01", "expiration_date": "2026-06-30"}
    assert evaluate_temporal(expiring, date(2026, 6, 30)).applicable
    assert evaluate_temporal(expiring, date(2026, 7, 1)).status is ApplicabilityStatus.EXPIRED

    open_ended = {"effective_date": "2026-01-01", "expiration_date": None}
    assert evaluate_temporal(open_ended, date(2030, 1, 1)).applicable


def test_no_as_of_date_is_undetermined_not_a_failure():
    decision = evaluate_temporal({"effective_date": "2026-01-01"}, None)
    assert decision.status is ApplicabilityStatus.UNDETERMINED


def test_version_selection_picks_the_latest_eligible():
    metadatas = [
        {"policy_id": "POL-X", "policy_version": "1.0", "effective_date": "2026-01-01"},
        {"policy_id": "POL-X", "policy_version": "2.0", "effective_date": "2026-07-01"},
    ]
    assert select_effective_versions(metadatas, BEFORE)["POL-X"][0] == "1.0"
    assert select_effective_versions(metadatas, AFTER)["POL-X"][0] == "2.0"


def test_superseded_versions_are_classified_as_such():
    metadatas = [
        {"policy_id": "POL-X", "policy_version": "1.0", "effective_date": "2026-01-01"},
        {"policy_id": "POL-X", "policy_version": "2.0", "effective_date": "2026-07-01"},
    ]
    governing = select_effective_versions(metadatas, AFTER)
    assert classify(metadatas[0], as_of=AFTER, governing_versions=governing).status is (
        ApplicabilityStatus.SUPERSEDED
    )
    assert classify(metadatas[1], as_of=AFTER, governing_versions=governing).applicable


def test_version_ordering_is_numeric_not_lexical():
    metadatas = [
        {"policy_id": "P", "policy_version": "2.0", "effective_date": "2026-01-01"},
        {"policy_id": "P", "policy_version": "10.0", "effective_date": "2026-01-01"},
    ]
    assert select_effective_versions(metadatas, AFTER)["P"][0] == "10.0"


def test_scope_affinity_is_soft_and_bounded():
    meta = {
        "product_scope": "conventional_conforming|jumbo",
        "purpose_scope": "purchase",
        "occupancy_scope": "primary_residence",
    }
    full = scope_affinity(
        meta,
        {
            "product_family": "conventional_conforming",
            "loan_purpose": "purchase",
            "occupancy_type": "primary_residence",
        },
    )
    assert full == 1.0
    none = scope_affinity(meta, {"product_family": "usda"})
    assert none == 0.0
    # No context means no opinion, not a penalty.
    assert scope_affinity(meta, {}) == 0.0
    # Missing metadata is never a penalty either.
    assert scope_affinity({}, {"product_family": "usda"}) == 0.0


# --------------------------------------------------------------------- pipeline level


def _versions_of(result, policy_id: str) -> set[str]:
    return {e.policy_version for e in result.evidence if e.policy_id == policy_id}


@pytest.mark.slow
@pytest.mark.parametrize("policy_id", sorted(VERSIONED_POLICIES))
def test_before_the_boundary_returns_v1(retriever, policy_id):
    """Every versioned mortgage policy resolves to v1.0 before 2026-07-01."""
    request = PolicyRetrievalRequest(
        product_domain=LendingProductDomain.MORTGAGE,
        query_text=f"What does policy {policy_id} require?",
        as_of_date=BEFORE,
        top_k=8,
    )
    versions = _versions_of(retriever.retrieve(request), policy_id)
    assert versions, f"{policy_id} was not retrieved at all"
    assert versions == {"1.0"}, f"{policy_id} returned {versions} before the boundary"


@pytest.mark.slow
@pytest.mark.parametrize("policy_id", sorted(VERSIONED_POLICIES))
def test_after_the_boundary_returns_v2(retriever, policy_id):
    request = PolicyRetrievalRequest(
        product_domain=LendingProductDomain.MORTGAGE,
        query_text=f"What does policy {policy_id} require?",
        as_of_date=AFTER,
        top_k=8,
    )
    versions = _versions_of(retriever.retrieve(request), policy_id)
    assert versions, f"{policy_id} was not retrieved at all"
    assert versions == {"2.0"}, f"{policy_id} returned {versions} after the boundary"


@pytest.mark.slow
def test_no_superseded_version_ever_appears(retriever):
    """A single retrieval never mixes two versions of the same policy."""
    for as_of in (BEFORE, AFTER):
        request = PolicyRetrievalRequest(
            product_domain=LendingProductDomain.MORTGAGE,
            query_text="What affordability, credit, reserve and valuation rules apply?",
            as_of_date=as_of,
            top_k=15,
        )
        result = retriever.retrieve(request)
        seen: dict[str, set[str]] = {}
        for item in result.evidence:
            seen.setdefault(item.policy_id, set()).add(item.policy_version)
        mixed = {p: v for p, v in seen.items() if len(v) > 1}
        assert not mixed, f"as of {as_of}: two versions returned for {mixed}"


@pytest.mark.slow
def test_the_boundary_pair_retrieves_different_dti_ceilings(retriever):
    """The case the corpus was built around: same question, two answers."""
    query = "What is the maximum back-end debt-to-income ratio for a conventional loan?"

    before = retriever.retrieve(
        PolicyRetrievalRequest(
            product_domain=LendingProductDomain.MORTGAGE,
            query_text=query,
            application_id="APP-000055",
            as_of_date=BEFORE,
            top_k=6,
        )
    )
    after = retriever.retrieve(
        PolicyRetrievalRequest(
            product_domain=LendingProductDomain.MORTGAGE,
            query_text=query,
            application_id="APP-000056",
            as_of_date=AFTER,
            top_k=6,
        )
    )

    before_rule = next(e for e in before.evidence if e.rule_id == "DTI-CONV-001")
    after_rule = next(e for e in after.evidence if e.rule_id == "DTI-CONV-001")

    assert before_rule.policy_version == "1.0"
    assert before_rule.citation == "POL-DTI-001 v1.0 rule DTI-CONV-001"
    assert "45" in before_rule.text

    assert after_rule.policy_version == "2.0"
    assert after_rule.citation == "POL-DTI-001 v2.0 rule DTI-CONV-001"
    assert "43%" in after_rule.text
    assert "max_back_end_dti_with_factors" in after_rule.text


@pytest.mark.slow
def test_a_date_before_any_policy_yields_no_applicable_policy(retriever):
    """Retrieval says so rather than falling back to the newest document."""
    result = retriever.retrieve(
        PolicyRetrievalRequest(
            product_domain=LendingProductDomain.MORTGAGE,
            query_text="What is the maximum debt-to-income ratio?",
            as_of_date=date(2020, 1, 1),
        )
    )
    assert result.status.value == "NO_APPLICABLE_POLICY"
    assert result.evidence == []


@pytest.mark.slow
def test_education_effective_dates_are_honoured(retriever):
    """The education corpus publishes effective dates; they are applied."""
    result = retriever.retrieve(
        PolicyRetrievalRequest(
            product_domain=LendingProductDomain.EDUCATION_LOAN,
            query_text="What underwriting criteria apply to an undergraduate applicant?",
            as_of_date=date(2026, 8, 1),
            top_k=6,
        )
    )
    assert result.evidence
    for item in result.evidence:
        assert item.effective_date is not None
        assert item.effective_date <= date(2026, 8, 1)


@pytest.mark.slow
def test_education_before_its_first_policy_returns_nothing(retriever):
    """No education policy is in force in 2024; retrieval must not invent one."""
    result = retriever.retrieve(
        PolicyRetrievalRequest(
            product_domain=LendingProductDomain.EDUCATION_LOAN,
            query_text="Does this borrower require a cosigner?",
            as_of_date=date(2024, 1, 1),
        )
    )
    assert result.status.value == "NO_APPLICABLE_POLICY"
    assert result.evidence == []


def test_education_has_a_single_version_per_policy(education_chunks):
    """Documented limitation: there is no version to select between.

    The temporal machinery is applied to education all the same, so the corpus
    can gain versions later without the retriever changing.
    """
    chunks, _ = education_chunks
    by_policy: dict[str, set[str]] = {}
    for chunk in chunks:
        by_policy.setdefault(chunk.policy_id, set()).add(chunk.policy_version)
    multi = {p: v for p, v in by_policy.items() if len(v) > 1}
    assert not multi, f"education now has versioned policies: {multi}"
