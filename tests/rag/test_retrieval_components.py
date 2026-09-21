"""The retrieval components: BM25, dense search, RRF and the reranker.

Each layer is tested on its own so that a regression points at the layer that
caused it rather than at "retrieval got worse".
"""

from __future__ import annotations

import pytest

from src.domain import LendingProductDomain
from src.rag.expansion import expand_query, extract_identifiers, normalize_query
from src.rag.fusion import fuse, reciprocal_rank_fusion
from src.rag.lexical import BM25Index, LexicalHit, tokenize

# ---------------------------------------------------------------------------- tokenizer


def test_identifiers_survive_tokenization():
    """Splitting ``DTI-CONV-001`` on the hyphen would scatter the exact token."""
    tokens = tokenize("What does DTI-CONV-001 in POL-DTI-001 say?")
    assert "dti-conv-001" in tokens
    assert "pol-dti-001" in tokens
    # The parts are emitted too, so a query spelling it either way still matches.
    assert "dti" in tokens and "conv" in tokens and "001" in tokens


def test_education_identifiers_survive_tokenization():
    tokens = tokenize("EDU-INTL-004 and the I-94 record")
    assert "edu-intl-004" in tokens
    assert "i-94" in tokens


def test_stopwords_are_removed_but_policy_vocabulary_is_not():
    tokens = tokenize("What is the income and credit value of the reserves?")
    assert "the" not in tokens and "is" not in tokens
    for keeper in ("income", "credit", "value", "reserves"):
        assert keeper in tokens


# --------------------------------------------------------------------------------- BM25


@pytest.fixture(scope="module")
def mortgage_bm25(config, indexes_built):
    if not indexes_built:
        pytest.skip("indexes not built")
    return BM25Index.load(BM25Index.path_for(config, LendingProductDomain.MORTGAGE))


@pytest.fixture(scope="module")
def education_bm25(config, indexes_built):
    if not indexes_built:
        pytest.skip("indexes not built")
    return BM25Index.load(BM25Index.path_for(config, LendingProductDomain.EDUCATION_LOAN))


@pytest.mark.parametrize(
    "rule_id",
    ["DTI-CONV-001", "AST-RSV-002", "SEC-INJ-001", "CONV-PUR-002", "VAL-APR-003"],
)
def test_bm25_finds_a_mortgage_rule_by_its_exact_id(mortgage_bm25, rule_id):
    """Exact-id lookup must not depend on the embedding."""
    hits = mortgage_bm25.search(rule_id, top_k=5)
    assert hits, f"BM25 found nothing for {rule_id}"
    assert any(h.metadata.get("rule_id") == rule_id for h in hits[:3])


@pytest.mark.parametrize(
    "rule_id", ["EDU-UW-002", "EDU-COS-004", "EDU-INTL-004", "EDU-INC-003"]
)
def test_bm25_finds_an_education_rule_by_its_exact_id(education_bm25, rule_id):
    hits = education_bm25.search(rule_id, top_k=5)
    assert hits
    assert any(h.metadata.get("rule_id") == rule_id for h in hits[:3])


@pytest.mark.parametrize("term", ["HCLTV", "PITIA", "reserves", "cash to close", "occupancy"])
def test_bm25_finds_mortgage_domain_vocabulary(mortgage_bm25, term):
    assert mortgage_bm25.search(term, top_k=5)


@pytest.mark.parametrize(
    "term", ["cost of attendance", "cosigner", "Tier A", "SEVIS", "OPT", "risk grade"]
)
def test_bm25_finds_education_domain_vocabulary(education_bm25, term):
    assert education_bm25.search(term, top_k=5)


def test_bm25_honours_an_allow_list(mortgage_bm25):
    unrestricted = mortgage_bm25.search("debt-to-income", top_k=10)
    assert len(unrestricted) > 1
    allowed = {unrestricted[1].chunk_id}
    restricted = mortgage_bm25.search("debt-to-income", top_k=10, allowed_ids=allowed)
    assert {h.chunk_id for h in restricted} == allowed


def test_bm25_ranks_are_dense_and_ordered(mortgage_bm25):
    hits = mortgage_bm25.search("maximum debt-to-income ratio", top_k=8)
    assert [h.rank for h in hits] == list(range(1, len(hits) + 1))
    assert all(a.score >= b.score for a, b in zip(hits, hits[1:]))


def test_bm25_returns_nothing_for_an_out_of_vocabulary_query(mortgage_bm25):
    assert mortgage_bm25.search("zzzzqqqxyw", top_k=5) == []


def test_bm25_index_round_trips(tmp_path, mortgage_bm25):
    path = tmp_path / "bm25.json"
    mortgage_bm25.save(path)
    reloaded = BM25Index.load(path)
    assert reloaded.chunk_ids == mortgage_bm25.chunk_ids
    assert reloaded.domain is mortgage_bm25.domain
    assert [h.chunk_id for h in reloaded.search("reserves", top_k=5)] == [
        h.chunk_id for h in mortgage_bm25.search("reserves", top_k=5)
    ]


def test_bm25_index_save_is_byte_stable(tmp_path, mortgage_bm25):
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    mortgage_bm25.save(a)
    mortgage_bm25.save(b)
    assert a.read_bytes() == b.read_bytes()


# ---------------------------------------------------------------------------------- RRF


def test_rrf_formula():
    """RRF(d) = sum_i w_i / (k + rank_i(d)), ranks 1-based."""
    scores = reciprocal_rank_fusion([["a", "b"], ["b", "a"]], k=60)
    assert scores["a"] == pytest.approx(1 / 61 + 1 / 62)
    assert scores["b"] == pytest.approx(1 / 61 + 1 / 62)


def test_rrf_rewards_appearing_in_both_lists():
    """A document both layers found beats one only the top of one list found."""
    scores = reciprocal_rank_fusion([["top", "both"], ["other", "both"]], k=60)
    assert scores["both"] > scores["top"]
    assert scores["both"] > scores["other"]


def test_rrf_respects_rank_order_within_a_list():
    scores = reciprocal_rank_fusion([["first", "second", "third"]], k=60)
    assert scores["first"] > scores["second"] > scores["third"]


def test_rrf_weights_shift_the_balance():
    dense_heavy = reciprocal_rank_fusion([["a"], ["b"]], k=60, weights=[2.0, 1.0])
    assert dense_heavy["a"] > dense_heavy["b"]
    lexical_heavy = reciprocal_rank_fusion([["a"], ["b"]], k=60, weights=[1.0, 2.0])
    assert lexical_heavy["b"] > lexical_heavy["a"]


def test_rrf_k_damps_the_head_of_a_list():
    """A larger k flattens the advantage of rank 1 over rank 2."""
    small = reciprocal_rank_fusion([["a", "b"]], k=1)
    large = reciprocal_rank_fusion([["a", "b"]], k=1000)
    assert (small["a"] / small["b"]) > (large["a"] / large["b"])


def test_rrf_rejects_a_non_positive_k():
    with pytest.raises(ValueError, match="rrf_k must be positive"):
        reciprocal_rank_fusion([["a"]], k=0)


def test_rrf_rejects_mismatched_weights():
    with pytest.raises(ValueError, match="same length"):
        reciprocal_rank_fusion([["a"], ["b"]], weights=[1.0])


def test_fuse_is_deterministic_and_records_provenance():
    dense = [
        {"chunk_id": "x", "metadata": {"policy_id": "P1"}, "document": "doc x",
         "distance": 0.1, "score": 0.9, "rank": 1},
        {"chunk_id": "y", "metadata": {"policy_id": "P2"}, "document": "doc y",
         "distance": 0.3, "score": 0.7, "rank": 2},
    ]
    lexical = [
        LexicalHit(chunk_id="y", score=8.0, rank=1, metadata={"policy_id": "P2"}),
        LexicalHit(chunk_id="z", score=3.0, rank=2, metadata={"policy_id": "P3"}),
    ]
    fused = fuse(dense, lexical, k=60)
    by_id = {c.chunk_id: c for c in fused}

    assert by_id["y"].dense_rank == 2 and by_id["y"].bm25_rank == 1
    assert by_id["y"].sources == ["dense", "bm25"]
    assert by_id["x"].sources == ["dense"]
    assert by_id["z"].sources == ["bm25"]
    # y is in both lists, so it wins.
    assert fused[0].chunk_id == "y"
    assert [c.rank for c in fused] == list(range(1, len(fused) + 1))
    assert [c.chunk_id for c in fuse(dense, lexical, k=60)] == [c.chunk_id for c in fused]


def test_fuse_breaks_ties_on_chunk_id():
    dense = [{"chunk_id": "b", "metadata": {}, "document": "", "distance": 0, "score": 1, "rank": 1}]
    lexical = [LexicalHit(chunk_id="a", score=1.0, rank=1, metadata={})]
    fused = fuse(dense, lexical, k=60)
    assert [c.chunk_id for c in fused] == ["a", "b"]


# --------------------------------------------------------------------- query expansion


def test_expansion_adds_domain_synonyms_and_keeps_the_original():
    expanded, added = expand_query("What is the DTI limit?", LendingProductDomain.MORTGAGE)
    assert expanded.startswith("What is the DTI limit?")
    assert "debt-to-income" in added


def test_expansion_is_product_specific():
    _, mortgage_added = expand_query("cost of attendance", LendingProductDomain.MORTGAGE)
    _, education_added = expand_query("cost of attendance", LendingProductDomain.EDUCATION_LOAN)
    assert "coa" in education_added
    assert "coa" not in mortgage_added


def test_expansion_is_deterministic():
    first = expand_query("LTV and DTI on a cash-out", LendingProductDomain.MORTGAGE)
    second = expand_query("LTV and DTI on a cash-out", LendingProductDomain.MORTGAGE)
    assert first == second


def test_expansion_can_be_disabled():
    expanded, added = expand_query("DTI", LendingProductDomain.MORTGAGE, enabled=False)
    assert expanded == "DTI"
    assert added == []


def test_expansion_does_not_fire_on_a_substring():
    """``dti`` inside another word must not trigger the synonym."""
    _, added = expand_query("editing the document", LendingProductDomain.MORTGAGE)
    assert "debt-to-income" not in added


def test_identifier_extraction():
    assert extract_identifiers("What does DTI-CONV-001 say?") == ["DTI-CONV-001"]
    assert "POL-DTI-001" in extract_identifiers("Show me POL-DTI-001 rule DTI-CONV-001")
    assert "EDU-UW-002" in extract_identifiers("what is EDU-UW-002")
    assert extract_identifiers("no identifiers here") == []


def test_normalize_collapses_whitespace():
    assert normalize_query("  a \n b\tc  ") == "a b c"
