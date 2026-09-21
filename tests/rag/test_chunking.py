"""Chunking keeps a rule whole, and splits only when it genuinely must."""

from __future__ import annotations

from src.rag.models import ChunkKind
from src.rag.parsers import get_parser


def test_rules_are_not_split_at_the_configured_size(config, mortgage_chunks, education_chunks):
    """No rule in either corpus needs secondary splitting at 4200 characters.

    This is worth asserting rather than assuming: if a future policy grows past
    the limit the test fails and the split path gets exercised deliberately
    instead of appearing unnoticed in production retrieval.
    """
    for chunks, _ in (mortgage_chunks, education_chunks):
        split = [c for c in chunks if c.part_count > 1]
        assert not split, f"{len(split)} chunk(s) were split: {[c.chunk_id for c in split][:3]}"


def test_oversized_sections_split_at_paragraph_boundaries(tmp_path):
    """When a rule does exceed the limit, the split keeps whole paragraphs."""
    paragraph = ("Sentence with enough substance to matter. " * 12).strip()
    body = "\n\n".join(f"{paragraph} Paragraph {n}." for n in range(1, 9))
    doc = tmp_path / "POL-BIG-001_x_v1.0.md"
    doc.write_text(
        "---\npolicy_id: POL-BIG-001\ntitle: Big\nversion: 1.0\n"
        "rule_ids:\n  - BIG-001\n---\n\n"
        "# Big\n\n## 1. Purpose\n\nA purpose statement.\n\n"
        f"## 4. Rules\n\n### BIG-001 — A very long rule\n\n{body}\n",
        encoding="utf-8",
    )
    parser = get_parser("mortgage", max_chars=900, overlap_chars=100)
    chunks = parser.chunk_document(parser.parse_document(doc))
    parts = [c for c in chunks if c.rule_id == "BIG-001"]

    assert len(parts) > 1, "an oversized rule should split"
    assert all(c.part_count == len(parts) for c in parts)
    assert [c.part_index for c in parts] == list(range(len(parts)))
    # Every part after the first repeats the parent heading, so a retrieved
    # fragment still says which rule it belongs to.
    for part in parts[1:]:
        assert "BIG-001" in part.text
    # Paragraphs stay intact across the split.
    for part in parts:
        assert "Sentence with enough substance to matter." in part.text


def test_split_parts_have_distinct_stable_ids(tmp_path):
    body = "\n\n".join(f"{'Long paragraph text. ' * 30}n={n}" for n in range(6))
    doc = tmp_path / "POL-BIG-002_x_v1.0.md"
    doc.write_text(
        "---\npolicy_id: POL-BIG-002\ntitle: Big\nversion: 1.0\n"
        "rule_ids:\n  - BIG-002\n---\n\n# Big\n\n## 1. Purpose\n\nPurpose.\n\n"
        f"## 4. Rules\n\n### BIG-002 — Long\n\n{body}\n",
        encoding="utf-8",
    )
    parser = get_parser("mortgage", max_chars=800)
    ids = [c.chunk_id for c in parser.chunk_document(parser.parse_document(doc))]
    assert len(ids) == len(set(ids))
    assert ids == [c.chunk_id for c in parser.chunk_document(parser.parse_document(doc))]


def test_embedding_text_carries_the_identifiers(mortgage_chunks, education_chunks):
    """Policy id, rule id and titles are embedded and lexically indexed.

    A query naming ``DTI-CONV-001`` must not depend on the semantics of that
    rule's prose to find it.
    """
    chunks, _ = mortgage_chunks
    rule = next(c for c in chunks if c.rule_id == "DTI-CONV-001" and c.policy_version == "2.0")
    text = rule.embedding_text()
    assert "POL-DTI-001" in text
    assert "DTI-CONV-001" in text
    assert "version 2.0" in text
    assert rule.rule_title in text

    edu_chunks, _ = education_chunks
    edu_rule = next(c for c in edu_chunks if c.rule_id == "EDU-INTL-004")
    edu_text = edu_rule.embedding_text()
    assert "POL-012" in edu_text
    assert "EDU-INTL-004" in edu_text


def test_chroma_metadata_is_all_scalars(mortgage_chunks, education_chunks):
    """Chroma stores str/int/float/bool only; lists must be flattened."""
    for chunks, _ in (mortgage_chunks, education_chunks):
        for chunk in chunks[:50]:
            for key, value in chunk.chroma_metadata().items():
                assert isinstance(value, (str, int, float, bool)), f"{key} is {type(value)}"
                assert value is not None


def test_overview_chunks_exist_for_every_document(mortgage_chunks):
    chunks, docs = mortgage_chunks
    overviews = {c.source_path for c in chunks if c.chunk_kind is ChunkKind.OVERVIEW}
    assert overviews == {d.source_path for d in docs}


def test_every_chunk_has_provenance(mortgage_chunks, education_chunks):
    for chunks, _ in (mortgage_chunks, education_chunks):
        for chunk in chunks:
            assert chunk.source_path
            assert len(chunk.source_sha256) == 64
            assert chunk.policy_id
            assert chunk.citation
