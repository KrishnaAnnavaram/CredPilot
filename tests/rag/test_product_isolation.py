"""Product isolation: the property the whole architecture exists to guarantee.

Mortgage queries must return zero education policies and education queries zero
mortgage policies — not because a filter was applied correctly but because the
two bodies of knowledge never share an index. These tests check the guarantee at
every level it is claimed at: the collections, the routing, and the retrieved
evidence.
"""

from __future__ import annotations

import pytest

from src.domain import (
    LendingProductDomain,
    ProductResolutionError,
    domain_from_application_id,
    domain_from_packet,
    resolve_product_domain,
)
from src.rag.models import RetrievalStatus
from src.rag.pipeline import retrieve_policy
from src.rag.vectorstore import FORBIDDEN_COLLECTION_NAMES, PolicyVectorStore

pytestmark = pytest.mark.integration


# ---------------------------------------------------------------------------- routing


@pytest.mark.parametrize(
    "application_id,expected",
    [
        ("APP-000001", LendingProductDomain.MORTGAGE),
        ("APP-000056", LendingProductDomain.MORTGAGE),
        ("APP-000075", LendingProductDomain.MORTGAGE),
        ("APP-2026-00001", LendingProductDomain.EDUCATION_LOAN),
        ("APP-2026-00037", LendingProductDomain.EDUCATION_LOAN),
        ("APP-2026-00200", LendingProductDomain.EDUCATION_LOAN),
    ],
)
def test_application_id_shape_resolves_the_product(application_id, expected):
    assert domain_from_application_id(application_id) is expected
    assert resolve_product_domain(application_id=application_id) is expected


@pytest.mark.parametrize(
    "application_id", ["", "APP-1", "APP-12345", "LOAN-000001", "APP-20260-0001", "banana"]
)
def test_unknown_id_shapes_do_not_resolve(application_id):
    assert domain_from_application_id(application_id) is None


def test_every_committed_application_id_routes_correctly(repo_root):
    """Routing accuracy over the whole corpus, not a sample.

    ``index.json`` is the mortgage corpus's own manifest, not an application, so
    it is excluded by the ``APP-*`` glob rather than by name.
    """
    mortgage = sorted((repo_root / "synthetic_data/mortgage/applications").glob("APP-*.json"))
    education = sorted((repo_root / "synthetic_data/education/applications").glob("APP-*.json"))
    assert len(mortgage) == 75 and len(education) == 200

    for path in mortgage:
        assert domain_from_application_id(path.stem) is LendingProductDomain.MORTGAGE, path.stem
    for path in education:
        assert (
            domain_from_application_id(path.stem) is LendingProductDomain.EDUCATION_LOAN
        ), path.stem


def test_packet_shape_resolves_the_product():
    mortgage_packet = {
        "subject_property": {},
        "borrowers": [],
        "product_family": "conventional_conforming",
    }
    education_packet = {"school": {}, "borrower": {}, "product_code": "UG"}
    assert domain_from_packet(mortgage_packet) is LendingProductDomain.MORTGAGE
    assert domain_from_packet(education_packet) is LendingProductDomain.EDUCATION_LOAN


def test_ambiguous_input_raises_rather_than_guessing():
    with pytest.raises(ProductResolutionError, match="PRODUCT_CLARIFICATION_REQUIRED"):
        resolve_product_domain(application_id="UNKNOWN-1")
    with pytest.raises(ProductResolutionError):
        resolve_product_domain()


def test_graph_state_supplies_the_domain():
    state = {"loan_domain": "EDUCATION_LOAN", "application_id": "APP-2026-00001"}
    assert resolve_product_domain(graph_state=state) is LendingProductDomain.EDUCATION_LOAN


def test_explicit_domain_wins_over_the_identifier():
    """An operator override is authoritative; the id is only a fallback signal."""
    resolved = resolve_product_domain(
        explicit_domain="EDUCATION_LOAN", application_id="APP-000056"
    )
    assert resolved is LendingProductDomain.EDUCATION_LOAN


# ------------------------------------------------------------------------ collections


def test_each_product_has_its_own_collection(config):
    collections = [p.collection for p in config.products.values()]
    assert len(set(collections)) == len(collections)
    assert "credpilot_mortgage_policies" in collections
    assert "credpilot_education_policies" in collections


def test_a_combined_collection_is_refused(config):
    """Guard against a mixed index being created by accident."""
    assert FORBIDDEN_COLLECTION_NAMES
    import dataclasses

    product = dataclasses.replace(
        config.products["mortgage"], collection="credpilot_all_policies"
    )
    mixed = dataclasses.replace(config, products={**config.products, "mortgage": product})
    with pytest.raises(ValueError, match="would mix lending products"):
        PolicyVectorStore(mixed, LendingProductDomain.MORTGAGE)


def test_a_store_refuses_to_write_another_products_chunks(config, indexes_built, education_chunks):
    if not indexes_built:
        pytest.skip("indexes not built")
    import numpy as np

    chunks = education_chunks[0][:2]
    store = PolicyVectorStore(config, LendingProductDomain.MORTGAGE)
    with pytest.raises(ValueError, match="another product"):
        store.add_chunks(chunks, np.zeros((2, config.embedding.dimension), dtype="float32"))


def test_collections_share_no_policy_id(config, indexes_built):
    if not indexes_built:
        pytest.skip("indexes not built")
    ids = {}
    for domain in LendingProductDomain:
        store = PolicyVectorStore(config, domain)
        ids[domain] = {r["metadata"]["policy_id"] for r in store.get_all()}
    overlap = ids[LendingProductDomain.MORTGAGE] & ids[LendingProductDomain.EDUCATION_LOAN]
    assert not overlap, f"policy ids in both collections: {sorted(overlap)}"


def test_every_chunk_in_a_collection_belongs_to_it(config, indexes_built, each_domain):
    if not indexes_built:
        pytest.skip("indexes not built")
    store = PolicyVectorStore(config, each_domain)
    for record in store.get_all():
        meta = record["metadata"]
        assert meta["product_domain"] == each_domain.value
        assert record["chunk_id"].startswith(each_domain.chunk_prefix + "__")
        assert each_domain.corpus_key in meta["source_path"]


# ------------------------------------------------------------------- retrieved evidence

#: Queries phrased so that the *other* product's vocabulary is the obvious match.
#: If isolation were only a filter, these are the queries that would leak.
_CROSS_PRODUCT_BAIT = [
    (
        LendingProductDomain.MORTGAGE,
        "Does this student borrower need a cosigner for their undergraduate loan?",
    ),
    (
        LendingProductDomain.MORTGAGE,
        "What cost of attendance and school certification rules apply to an F-1 visa holder?",
    ),
    (LendingProductDomain.MORTGAGE, "What is the risk grade and pricing matrix for REFI?"),
    (
        LendingProductDomain.EDUCATION_LOAN,
        "What is the maximum loan-to-value on a cash-out refinance of a primary residence?",
    ),
    (
        LendingProductDomain.EDUCATION_LOAN,
        "How many months of post-closing reserves does a jumbo mortgage need?",
    ),
    (
        LendingProductDomain.EDUCATION_LOAN,
        "Which appraisal and occupancy rules govern this property?",
    ),
]


@pytest.mark.slow
@pytest.mark.parametrize(
    "domain,query", _CROSS_PRODUCT_BAIT, ids=[f"{d.value}-{i}" for i, (d, _) in enumerate(_CROSS_PRODUCT_BAIT)]
)
def test_cross_product_queries_return_no_foreign_policy(retriever, domain, query):
    result = retrieve_policy(
        query=query, product_domain=domain, as_of_date="2026-08-12", retriever=retriever
    )
    foreign_prefix = (
        "EDUCATION__" if domain is LendingProductDomain.MORTGAGE else "MORTGAGE__"
    )
    assert result.product_domain is domain
    leaked = [e.chunk_id for e in result.evidence if e.chunk_id.startswith(foreign_prefix)]
    assert not leaked, f"{domain.value} query returned foreign evidence: {leaked}"

    expected_root = f"synthetic_data/{domain.corpus_key}/policy_corpus/"
    for item in result.evidence:
        assert item.source_path.startswith(expected_root)
        assert item.product_domain is domain


@pytest.mark.slow
def test_an_unresolvable_product_returns_clarification_not_a_search(retriever):
    """Ambiguity escalates; it never becomes a search of both corpora."""
    result = retrieve_policy(
        query="What is the maximum debt-to-income ratio?", retriever=retriever
    )
    assert result.status is RetrievalStatus.PRODUCT_CLARIFICATION_REQUIRED
    assert result.evidence == []
    assert "PRODUCT_CLARIFICATION_REQUIRED" in (result.message or "")
