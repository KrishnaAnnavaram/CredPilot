"""The education parser reproduces its corpus exactly — and differently.

The education documents are laid out differently from the mortgage ones: lighter
front matter, two spellings of the product-scope key, rules marked inline in bold
rather than by their own heading, and sections that carry no rule at all. These
tests pin the differences rather than assuming the two corpora are symmetrical.
"""

from __future__ import annotations

import pytest

from src.domain import LendingProductDomain, read_text_tolerant
from src.rag.models import ChunkKind
from src.rag.parsers import PolicyParseError, get_parser
from src.rag.parsers.base import coerce_str_list, parse_front_matter


def test_every_corpus_document_parses(config, education_chunks):
    chunks, docs = education_chunks
    parser = get_parser("education")
    files = parser.corpus_files(config.products["education"].corpus_root)
    assert len(docs) == len(files)
    assert len(files) > 0


def test_every_declared_rule_becomes_a_chunk(education_chunks):
    chunks, docs = education_chunks
    for doc in docs:
        declared = set(coerce_str_list(doc.front_matter.get("rule_ids")))
        produced = {
            c.rule_id
            for c in chunks
            if c.source_path == doc.source_path and c.chunk_kind is ChunkKind.RULE
        }
        assert produced == declared, f"{doc.source_path}: {declared ^ produced}"


def test_inline_bold_rule_markers_are_found(education_chunks):
    """POL-001 runs the rule body on from the marker on the same line.

    An earlier version of the marker pattern anchored to the end of the line and
    silently found no rules in that document at all.
    """
    chunks, _ = education_chunks
    gov = next(c for c in chunks if c.rule_id == "EDU-GOV-001")
    assert gov.policy_id == "POL-001"
    assert gov.rule_title == "Policy Scope and Applicability"
    assert "Every credit decision" in gov.text


def test_both_dash_conventions_are_handled(education_chunks):
    """POL-001..006 mark rules with ``--``; POL-007..012 use an em dash."""
    chunks, _ = education_chunks
    double_hyphen = next(c for c in chunks if c.rule_id == "EDU-UW-001")
    em_dash = next(c for c in chunks if c.rule_id == "EDU-EXC-001")
    assert double_hyphen.rule_title == "Undergraduate Underwriting Criteria"
    assert em_dash.rule_title == "Documentation Standard"


def test_both_product_scope_spellings_are_read(education_chunks):
    """``product_scope`` in POL-001..006, ``products`` in POL-007..012."""
    chunks, _ = education_chunks
    by_scope = next(c for c in chunks if c.policy_id == "POL-002")
    by_products = next(c for c in chunks if c.policy_id == "POL-008")
    assert set(by_scope.product_scope) == {"UG", "GR", "SP", "INTL", "REFI"}
    assert set(by_products.product_scope) == {"UG", "GR", "SP", "INTL", "REFI"}


def test_sections_without_a_rule_still_become_chunks(education_chunks):
    """Content with no rule id must not be dropped for lacking one."""
    chunks, _ = education_chunks
    sections = [c for c in chunks if c.chunk_kind is ChunkKind.SECTION]
    assert sections, "no section-level chunks were produced"
    titles = {c.section_title for c in sections}
    assert "Cross-Product Rules" in titles
    assert all(c.rule_id is None for c in sections)


def test_no_rule_ids_are_invented(config, education_chunks):
    """Every rule id a chunk claims appears verbatim in its source document."""
    chunks, _ = education_chunks
    sources = {
        doc.source_path: read_text_tolerant(config.products["education"].corpus_root.parent.parent.parent / doc.source_path)
        for doc in education_chunks[1]
    }
    for chunk in chunks:
        if chunk.rule_id:
            assert chunk.rule_id in sources[chunk.source_path], (
                f"{chunk.chunk_id} claims a rule id absent from its source"
            )


def test_education_has_no_fabricated_temporal_metadata(education_chunks):
    """The corpus publishes no expiry or supersession; none is invented."""
    chunks, _ = education_chunks
    assert all(c.expiration_date is None for c in chunks)
    assert all(c.supersedes is None for c in chunks)
    assert all(c.superseded_by is None for c in chunks)
    # Effective dates, which the corpus does publish, are kept.
    assert all(c.effective_date is not None for c in chunks)


def test_education_has_no_fabricated_mortgage_metadata(education_chunks):
    """Mortgage-only fields stay empty rather than being filled for symmetry."""
    chunks, _ = education_chunks
    assert all(c.occupancy_scope == [] for c in chunks)
    assert all(c.purpose_scope == [] for c in chunks)
    assert all(c.policy_family is None for c in chunks)


def test_chunk_ids_are_unique_and_deterministic(config, education_chunks):
    chunks, _ = education_chunks
    ids = [c.chunk_id for c in chunks]
    assert len(ids) == len(set(ids))

    parser = get_parser("education", max_chars=config.chunking.max_chars)
    again, _ = parser.parse_corpus(config.products["education"].corpus_root)
    assert [c.chunk_id for c in again] == ids


def test_chunk_id_shape(education_chunks):
    chunks, _ = education_chunks
    rule = next(c for c in chunks if c.rule_id == "EDU-UW-001")
    assert rule.chunk_id == "EDUCATION__POL-002__v1.0__EDU-UW-001__000"


def test_rule_keeps_its_parameter_table(education_chunks):
    """EDU-INC-003's product/ceiling matrix must travel with the rule."""
    chunks, _ = education_chunks
    rule = next(c for c in chunks if c.rule_id == "EDU-INC-003")
    for product in ("UG", "GR", "SP", "INTL", "REFI"):
        assert f"| {product} |" in rule.text
    assert "45%" in rule.text and "43%" in rule.text and "40%" in rule.text


def test_no_source_content_is_dropped(config):
    parser = get_parser("education", max_chars=config.chunking.max_chars)
    uncovered: list[str] = []
    for path in parser.corpus_files(config.products["education"].corpus_root):
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


def test_parser_rejects_an_undeclared_rule_in_the_body(tmp_path):
    doc = tmp_path / "POL-999_x.md"
    doc.write_text(
        "---\npolicy_id: POL-999\ntitle: Broken\nversion: 1.0\n"
        "rule_ids: [EDU-XX-001]\n---\n\n"
        "# POL-999 -- Broken\n\n## 1. Purpose\n\nA purpose long enough to survive.\n\n"
        "## 2. Rules\n\n**EDU-XX-001 -- First.** Body text long enough to survive.\n\n"
        "**EDU-XX-002 -- Undeclared.** Body text long enough to survive.\n",
        encoding="utf-8",
    )
    with pytest.raises(PolicyParseError, match="EDU-XX-002"):
        get_parser("education").parse_document(doc)


def test_parser_is_selected_by_domain():
    assert get_parser(LendingProductDomain.MORTGAGE).product_domain is LendingProductDomain.MORTGAGE
    assert (
        get_parser(LendingProductDomain.EDUCATION_LOAN).product_domain
        is LendingProductDomain.EDUCATION_LOAN
    )
