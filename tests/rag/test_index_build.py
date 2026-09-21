"""The built indexes match the committed corpora.

These tests read the live indexes and the live corpus and compare them. They are
the executable form of the claim the build script prints.
"""

from __future__ import annotations

import pytest

from src.domain import LendingProductDomain
from src.rag.corpus_registry import load_registry
from src.rag.indexer import load_manifest
from src.rag.integrity import validate_indexes
from src.rag.lexical import BM25Index
from src.rag.models import sha256_file
from src.rag.parsers import get_parser
from src.rag.vectorstore import PolicyVectorStore

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def integrity(config, indexes_built):
    if not indexes_built:
        pytest.skip("indexes not built; run 'python scripts/build_policy_indexes.py'")
    return validate_indexes(config)


def test_all_integrity_checks_pass(integrity):
    failures = [f"{c.name}: {c.detail}" for c in integrity.failures]
    assert not failures, failures


def test_source_document_counts_match(config, integrity):
    """Source file count equals indexed source count, per product."""
    for key, metrics in integrity.metrics["products"].items():
        parser = get_parser(config.products[key].parser)
        on_disk = len(parser.corpus_files(config.products[key].corpus_root))
        assert metrics["source_document_count"] == on_disk
        assert metrics["indexed_source_count"] == on_disk, f"{key}: a document was skipped"


def test_every_declared_rule_is_indexed(integrity):
    for key, metrics in integrity.metrics["products"].items():
        assert metrics["indexed_rule_count"] == metrics["declared_rule_count"], (
            f"{key}: {metrics['declared_rule_count'] - metrics['indexed_rule_count']} "
            f"declared rule(s) are missing from the index"
        )


def test_cross_product_contamination_is_zero(integrity):
    assert integrity.metrics["cross_product_contamination_rate"] == 0.0


def test_every_indexed_citation_resolves(integrity):
    assert integrity.metrics["citation_validity"] == 1.0


def test_no_stale_source_hashes(integrity):
    for key, metrics in integrity.metrics["products"].items():
        assert metrics["stale_documents"] == 0, f"{key}: the corpus changed since the build"


def test_manifest_records_the_build(config, indexes_built):
    if not indexes_built:
        pytest.skip("indexes not built")
    manifest = load_manifest(config)
    assert manifest["schema_version"] >= 2
    assert manifest["embedding"]["model"] == config.embedding.model
    assert manifest["embedding"]["dimension"] > 0
    assert manifest["embedding"]["distance_metric"] == "cosine"
    assert set(manifest["products"]) == set(config.products)

    for key, product in manifest["products"].items():
        assert product["source_document_count"] > 0
        assert product["chunk_count"] >= product["source_document_count"]
        assert product["collection_name"] == config.products[key].collection
        for document in product["documents"]:
            assert len(document["source_sha256"]) == 64
            assert document["chunk_ids"]


def test_manifest_hashes_match_the_files_on_disk(config, indexes_built, repo_root):
    if not indexes_built:
        pytest.skip("indexes not built")
    manifest = load_manifest(config)
    for product in manifest["products"].values():
        for document in product["documents"]:
            path = repo_root / document["source_path"]
            assert path.exists(), document["source_path"]
            assert sha256_file(str(path)) == document["source_sha256"]


def test_corpus_registry_matches_the_corpus(config, indexes_built, repo_root):
    """``data/policy_corpus/`` registers every committed policy document."""
    if not indexes_built:
        pytest.skip("indexes not built")
    registry = load_registry()
    for key, product in registry["products"].items():
        parser = get_parser(config.products[key].parser)
        on_disk = parser.corpus_files(config.products[key].corpus_root)
        assert product["document_count"] == len(on_disk)
        for document in product["documents"]:
            path = repo_root / document["source_path"]
            assert path.exists()
            assert sha256_file(str(path)) == document["source_sha256"]


def test_lexical_and_vector_indexes_agree(config, each_domain, indexes_built):
    if not indexes_built:
        pytest.skip("indexes not built")
    lexical = BM25Index.load(BM25Index.path_for(config, each_domain))
    store = PolicyVectorStore(config, each_domain)
    assert set(lexical.chunk_ids) == {r["chunk_id"] for r in store.get_all()}


def test_a_rebuild_reproduces_the_same_chunk_ids(config):
    """Same corpus plus same code yields the same ids, run after run."""
    for key in config.products:
        parser = get_parser(
            config.products[key].parser, max_chars=config.chunking.max_chars
        )
        first, _ = parser.parse_corpus(config.products[key].corpus_root)
        second, _ = parser.parse_corpus(config.products[key].corpus_root)
        assert [c.chunk_id for c in first] == [c.chunk_id for c in second]
        assert [c.source_sha256 for c in first] == [c.source_sha256 for c in second]
