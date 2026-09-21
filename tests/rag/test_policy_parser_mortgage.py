"""The mortgage parser reproduces the corpus exactly."""

from __future__ import annotations

import pytest

from src.domain import LendingProductDomain
from src.rag.models import ChunkKind
from src.rag.parsers import PolicyParseError, get_parser
from src.rag.parsers.base import coerce_str_list, parse_front_matter
from src.domain import read_text_tolerant


def test_every_corpus_document_parses(config, mortgage_chunks):
    chunks, docs = mortgage_chunks
    parser = get_parser("mortgage")
    files = parser.corpus_files(config.products["mortgage"].corpus_root)
    assert len(docs) == len(files), "a policy document failed to parse"
    assert len(files) > 0


def test_every_declared_rule_becomes_a_chunk(config, mortgage_chunks):
    """Front matter declares the rules; the body must contain all of them.

    The parser raises on a mismatch, so this test also proves the corpus is
    internally consistent — a rule declared but never written, or written but
    never declared, would fail the build rather than be silently dropped.
    """
    chunks, docs = mortgage_chunks
    for doc in docs:
        declared = set(coerce_str_list(doc.front_matter.get("rule_ids")))
        produced = {
            c.rule_id
            for c in chunks
            if c.source_path == doc.source_path and c.chunk_kind is ChunkKind.RULE
        }
        assert produced == declared, f"{doc.source_path}: {declared ^ produced}"


def test_chunk_ids_are_unique_and_deterministic(config, mortgage_chunks):
    chunks, _ = mortgage_chunks
    ids = [c.chunk_id for c in chunks]
    assert len(ids) == len(set(ids))

    parser = get_parser("mortgage", max_chars=config.chunking.max_chars)
    again, _ = parser.parse_corpus(config.products["mortgage"].corpus_root)
    assert [c.chunk_id for c in again] == ids, "chunk ids are not stable across runs"


def test_chunk_id_shape(mortgage_chunks):
    chunks, _ = mortgage_chunks
    rule_chunk = next(c for c in chunks if c.rule_id == "DTI-CONV-001" and c.policy_version == "2.0")
    assert rule_chunk.chunk_id == "MORTGAGE__POL-DTI-001__v2.0__DTI-CONV-001__000"


def test_rule_metadata_is_captured(mortgage_chunks):
    """A rule carries its own source category, severity and outcome."""
    chunks, _ = mortgage_chunks
    rule = next(c for c in chunks if c.rule_id == "DTI-CONV-001" and c.policy_version == "2.0")
    assert rule.product_domain is LendingProductDomain.MORTGAGE
    assert rule.policy_id == "POL-DTI-001"
    assert rule.rule_title.startswith("Maximum back-end debt-to-income")
    assert rule.severity == "HARD_FAIL"
    assert rule.outcome_type == "PASS_FAIL"
    assert rule.source_category == "SYNTHETIC_INTERNAL_POLICY"
    assert rule.policy_family == "affordability-dti"
    assert rule.effective_date.isoformat() == "2026-07-01"
    assert rule.expiration_date is None
    assert "conventional_conforming" in rule.product_scope


def test_rule_body_keeps_its_threshold_table(mortgage_chunks):
    """A rule and the number it sets must never be split apart."""
    chunks, _ = mortgage_chunks
    rule = next(c for c in chunks if c.rule_id == "DTI-CONV-001" and c.policy_version == "2.0")
    assert "`max_back_end_dti`" in rule.text
    assert "43%" in rule.text
    assert "`max_back_end_dti_with_factors`" in rule.text
    assert "`min_compensating_factors`" in rule.text


def test_both_versions_of_a_versioned_policy_are_parsed(mortgage_chunks):
    chunks, _ = mortgage_chunks
    versions = {
        c.policy_version for c in chunks if c.policy_id == "POL-DTI-001"
    }
    assert versions == {"1.0", "2.0"}


def test_v1_and_v2_of_a_rule_are_distinct_chunks(mortgage_chunks):
    chunks, _ = mortgage_chunks
    v1 = next(c for c in chunks if c.rule_id == "DTI-CONV-001" and c.policy_version == "1.0")
    v2 = next(c for c in chunks if c.rule_id == "DTI-CONV-001" and c.policy_version == "2.0")
    assert v1.chunk_id != v2.chunk_id
    assert v1.text != v2.text
    assert v1.effective_date < v2.effective_date


def test_no_source_content_is_dropped(config):
    """Every substantive line of every document appears in some chunk.

    A chunking scheme that quietly loses a paragraph loses whatever rule that
    paragraph stated, so coverage is asserted rather than assumed.
    """
    parser = get_parser("mortgage", max_chars=config.chunking.max_chars)
    uncovered: list[str] = []
    for path in parser.corpus_files(config.products["mortgage"].corpus_root):
        parsed = parser.parse_document(path)
        blob = "\n".join(c.text for c in parser.chunk_document(parsed))
        _, body, _ = parse_front_matter(read_text_tolerant(path), str(path))
        for line in body.splitlines():
            stripped = line.strip()
            if len(stripped) < 12 or stripped[0] in "#|>-":
                continue
            if stripped not in blob:
                uncovered.append(f"{path.name}: {stripped[:90]}")
    assert not uncovered, f"{len(uncovered)} uncovered lines, e.g. {uncovered[:3]}"


def test_parser_rejects_a_document_without_front_matter(tmp_path):
    bad = tmp_path / "POL-BAD-001_x_v1.0.md"
    bad.write_text("# No front matter\n\n## 1. Purpose\n\nNothing.\n", encoding="utf-8")
    with pytest.raises(PolicyParseError, match="no YAML front matter"):
        get_parser("mortgage").parse_document(bad)


def test_parser_rejects_a_declared_rule_that_is_missing_from_the_body(tmp_path):
    """A rule declared but never written must fail the build, not vanish."""
    doc = tmp_path / "POL-BAD-002_x_v1.0.md"
    doc.write_text(
        "---\n"
        "policy_id: POL-BAD-002\n"
        "title: Broken\n"
        "version: 1.0\n"
        "rule_ids:\n  - BAD-001\n  - BAD-002\n"
        "---\n\n"
        "# Broken\n\n## 1. Purpose\n\nA purpose statement long enough to keep.\n\n"
        "## 4. Rules\n\n### BAD-001 — Only one rule is actually written here\n\n"
        "This rule exists and has a body long enough to survive the minimum.\n",
        encoding="utf-8",
    )
    with pytest.raises(PolicyParseError, match="BAD-002"):
        get_parser("mortgage").parse_document(doc)
