"""Every citation resolves to a committed artifact, or it is not evidence."""

from __future__ import annotations

import pytest

from src.domain import LendingProductDomain
from src.rag.citations import citation_exists, parse_citation
from src.rag.models import PolicyRetrievalRequest, build_citation

pytestmark = pytest.mark.integration


# ------------------------------------------------------------------------ construction


def test_mortgage_citation_matches_the_golden_convention():
    """``POL-DTI-001 v2.0 rule DTI-CONV-001`` — the form the golden set uses."""
    assert (
        build_citation(
            product_domain=LendingProductDomain.MORTGAGE,
            policy_id="POL-DTI-001",
            policy_version="2.0",
            rule_id="DTI-CONV-001",
        )
        == "POL-DTI-001 v2.0 rule DTI-CONV-001"
    )


def test_education_citation_matches_its_own_convention():
    """``POL-002 EDU-UW-001`` — the education corpus is single-version."""
    assert (
        build_citation(
            product_domain=LendingProductDomain.EDUCATION_LOAN,
            policy_id="POL-002",
            policy_version="1.0",
            rule_id="EDU-UW-001",
        )
        == "POL-002 EDU-UW-001"
    )


def test_a_rule_id_is_never_invented():
    """A chunk with no rule cites its section, or the document alone."""
    section = build_citation(
        product_domain=LendingProductDomain.MORTGAGE,
        policy_id="POL-AST-001",
        policy_version="1.0",
        section_number="5",
    )
    assert section == "POL-AST-001 v1.0 section 5"
    document = build_citation(
        product_domain=LendingProductDomain.MORTGAGE,
        policy_id="POL-AST-001",
        policy_version="1.0",
    )
    assert document == "POL-AST-001 v1.0"
    assert "rule" not in document


# ----------------------------------------------------------------------------- parsing


@pytest.mark.parametrize(
    "citation,domain,policy_id,version,rule_id",
    [
        ("POL-DTI-001 v2.0 rule DTI-CONV-001", LendingProductDomain.MORTGAGE, "POL-DTI-001", "2.0", "DTI-CONV-001"),
        ("POL-AST-003 v1.0 rule AST-RSV-002", LendingProductDomain.MORTGAGE, "POL-AST-003", "1.0", "AST-RSV-002"),
        ("POL-GEN-001 v1.0", LendingProductDomain.MORTGAGE, "POL-GEN-001", "1.0", None),
        ("POL-002 EDU-UW-001", LendingProductDomain.EDUCATION_LOAN, "POL-002", None, "EDU-UW-001"),
        ("POL-012 EDU-INTL-004", LendingProductDomain.EDUCATION_LOAN, "POL-012", None, "EDU-INTL-004"),
        ("POL-009", LendingProductDomain.EDUCATION_LOAN, "POL-009", None, None),
    ],
)
def test_parsing_both_conventions(citation, domain, policy_id, version, rule_id):
    parsed = parse_citation(citation)
    assert parsed is not None, citation
    assert parsed.product_domain is domain
    assert parsed.policy_id == policy_id
    assert parsed.policy_version == version
    assert parsed.rule_id == rule_id


@pytest.mark.parametrize("citation", ["", "nonsense", "see the policy", "POL-", "rule DTI-CONV-001"])
def test_unparseable_citations_are_rejected(citation):
    assert parse_citation(citation) is None
    assert not citation_exists(citation)


# -------------------------------------------------------------------------- resolution


@pytest.mark.parametrize(
    "citation",
    [
        "POL-DTI-001 v1.0 rule DTI-CONV-001",
        "POL-DTI-001 v2.0 rule DTI-CONV-001",
        "POL-SEC-001 v1.0 rule SEC-INJ-001",
        "POL-VAL-001 v2.0 rule VAL-APR-005",
        "POL-002 EDU-UW-001",
        "POL-004 EDU-COS-004",
        "POL-012 EDU-INTL-009",
    ],
)
def test_real_citations_resolve(citation_resolver, citation):
    resolves, reason = citation_resolver.resolve(citation)
    assert resolves, reason


@pytest.mark.parametrize(
    "citation,because",
    [
        ("POL-DTI-001 v9.9 rule DTI-CONV-001", "no such version"),
        ("POL-ZZZ-999 v1.0 rule X-001", "no such policy"),
        ("POL-DTI-001 v2.0 rule DTI-FAKE-999", "no such rule"),
        ("POL-002 EDU-FAKE-001", "no such education rule"),
        ("POL-999 EDU-UW-001", "no such education policy"),
        # DTI-CONV-003 exists only in v2.0; citing it against v1.0 must fail.
        ("POL-DTI-001 v1.0 rule DTI-CONV-003", "rule absent from that version"),
    ],
)
def test_fabricated_citations_do_not_resolve(citation_resolver, citation, because):
    resolves, reason = citation_resolver.resolve(citation)
    assert not resolves, f"{citation} resolved although {because}: {reason}"


def test_resolution_reports_a_repo_relative_path(citation_resolver):
    """A resolution recorded in a log means the same on every checkout."""
    _, reason = citation_resolver.resolve("POL-DTI-001 v2.0 rule DTI-CONV-001")
    assert reason.startswith("resolves to synthetic_data/")
    assert ":" not in reason.split("resolves to ")[1]


def test_every_chunk_in_the_corpus_has_a_resolvable_citation(
    citation_resolver, mortgage_chunks, education_chunks
):
    """Citation validity of 1.00, measured over the whole corpus."""
    unresolved = []
    for chunks, _ in (mortgage_chunks, education_chunks):
        for chunk in chunks:
            if not citation_resolver.citation_exists(chunk.citation):
                unresolved.append(f"{chunk.chunk_id} -> {chunk.citation}")
    assert not unresolved, unresolved[:5]


@pytest.mark.slow
def test_retrieval_only_returns_resolvable_citations(retriever, each_domain):
    """A citation that does not resolve is dropped before it becomes evidence."""
    queries = {
        LendingProductDomain.MORTGAGE: [
            "What is the maximum back-end debt-to-income ratio?",
            "How many months of reserves are required?",
            "Which documents are required?",
        ],
        LendingProductDomain.EDUCATION_LOAN: [
            "Does this borrower require a cosigner?",
            "Which school certification rule applies?",
            "What is the maximum DTI by product?",
        ],
    }
    for query in queries[each_domain]:
        result = retriever.retrieve(
            PolicyRetrievalRequest(
                product_domain=each_domain, query_text=query, as_of_date="2026-08-01"
            )
        )
        assert result.evidence, query
        for item in result.evidence:
            assert item.citation_resolves, f"{query}: {item.citation}"
            assert citation_exists(item.citation)


@pytest.mark.slow
def test_a_citation_names_the_version_it_came_from(retriever):
    """Citation and evidence must agree about the version, or the audit is broken."""
    result = retriever.retrieve(
        PolicyRetrievalRequest(
            product_domain=LendingProductDomain.MORTGAGE,
            query_text="What affordability and reserve rules apply?",
            as_of_date="2026-06-25",
            top_k=10,
        )
    )
    for item in result.evidence:
        parsed = parse_citation(item.citation)
        assert parsed is not None
        assert parsed.policy_id == item.policy_id
        assert parsed.policy_version == item.policy_version
        if parsed.rule_id:
            assert parsed.rule_id == item.rule_id
