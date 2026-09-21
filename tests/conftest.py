"""Shared pytest fixtures.

The retriever, the embedding model and the cross-encoder are expensive to build
and immutable once built, so they are session-scoped. Everything they touch is
read-only: no test mutates an index, and any test that needs to would build its
own in a temporary directory.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# The suite makes no model call. Every graph test would otherwise reach the
# narrative node and call Gemini — six minutes for one module, a key required to
# run `pytest`, and assertions about routing and rule application made to depend
# on a hosted service that has nothing to do with them.
#
# Set before any src import so the graph never sees it on. Tests that mean to
# exercise generation set it back themselves; the end-to-end evaluation runs
# outside pytest and is unaffected.
os.environ.setdefault("CREDPILOT_NARRATIVE", "off")

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.config import get_config  # noqa: E402
from src.domain import LendingProductDomain  # noqa: E402


@pytest.fixture(scope="session")
def config():
    return get_config()


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def indexes_built(config) -> bool:
    """Whether the indexes exist. Tests needing them skip when they do not."""
    return config.manifest_path.exists() and config.vectorstore_path.exists()


@pytest.fixture(scope="session")
def retriever(config, indexes_built):
    if not indexes_built:
        pytest.skip("indexes not built; run 'python scripts/build_policy_indexes.py'")
    from src.rag.pipeline import PolicyRetriever

    return PolicyRetriever(config)


@pytest.fixture(scope="session")
def mortgage_chunks(config):
    from src.rag.parsers import get_parser

    parser = get_parser("mortgage", max_chars=config.chunking.max_chars)
    chunks, docs = parser.parse_corpus(config.products["mortgage"].corpus_root)
    return chunks, docs


@pytest.fixture(scope="session")
def education_chunks(config):
    from src.rag.parsers import get_parser

    parser = get_parser("education", max_chars=config.chunking.max_chars)
    chunks, docs = parser.parse_corpus(config.products["education"].corpus_root)
    return chunks, docs


@pytest.fixture(scope="session")
def citation_resolver(config):
    from src.rag.citations import CitationResolver

    return CitationResolver(config)


@pytest.fixture(params=list(LendingProductDomain), ids=lambda d: d.value)
def each_domain(request) -> LendingProductDomain:
    """Parameterizes a test over both lending products.

    Used wherever a property must hold for the whole system rather than for
    mortgage alone — which is most of them.
    """
    return request.param
