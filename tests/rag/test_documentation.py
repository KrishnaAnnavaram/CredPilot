"""The documents say what the measurements say.

The Evidence-in-Repo and Citation-Resolves rules (REQ-029, REQ-030) are about
documents matching reality. A document quoting a metric that no result file
contains, or a link pointing at a file that does not exist, fails both — and
neither is visible by reading the document.

These tests run the same checks as ``scripts/check_published_figures.py`` and
``scripts/verify_doc_tables.py``, so drift fails the suite rather than shipping.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys

import pytest

DOCS = (
    "README.md",
    "docs/rag/README.md",
    "docs/rag/ARCHITECTURE.md",
    "docs/rag/REQUIREMENTS_MAPPING.md",
    "docs/rag/TEMPORAL_RETRIEVAL.md",
    "docs/rag/RETRIEVAL_ABLATION.md",
    "docs/rag/FAILURE_ANALYSIS.md",
    "docs/rag/DATA_QUALITY_FINDINGS.md",
    "docs/rag/RUNBOOK.md",
)

_MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)#]+?)(?:#[^)]*)?\)")


def test_every_expected_document_exists(repo_root):
    missing = [d for d in DOCS if not (repo_root / d).exists()]
    assert not missing, missing


@pytest.mark.parametrize("document", DOCS)
def test_relative_links_resolve(repo_root, document):
    """A link to a file that does not exist is an unresolvable citation."""
    path = repo_root / document
    if not path.exists():
        pytest.skip(f"{document} not written yet")

    broken = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        for target in _MARKDOWN_LINK.findall(line):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                broken.append(f"{document}:{number}: {target}")
    assert not broken, broken


#: The one document whose subject *is* broken citations. Excluded from the
#: resolve-everything check below, and checked the other way round instead.
DATA_QUALITY_DOC = "docs/rag/DATA_QUALITY_FINDINGS.md"


@pytest.mark.parametrize("document", [d for d in DOCS if d != DATA_QUALITY_DOC])
def test_documents_cite_no_unresolvable_policy(repo_root, citation_resolver, document):
    """Every policy citation printed in a document resolves to a source file."""
    path = repo_root / document
    if not path.exists():
        pytest.skip(f"{document} not written yet")

    pattern = re.compile(
        r"\bPOL-[A-Z]+-\d{3}(?:\s+v\d\.\d)?(?:\s+rule\s+[A-Z0-9-]+)?"
        r"|\bPOL-\d{3}\s+EDU-[A-Z]+-\d+"
    )
    unresolved = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        for citation in pattern.findall(line):
            citation = citation.strip()
            # A bare policy id with no version is a reference, not a citation.
            if not re.search(r"\sv\d\.\d|\sEDU-", citation):
                continue
            if not citation_resolver.citation_exists(citation):
                unresolved.append(f"{document}:{number}: {citation}")
    assert not unresolved, unresolved


def test_the_data_quality_findings_are_still_true(repo_root, citation_resolver):
    """The broken citations that document names must still be broken.

    Checked the opposite way round from every other document: if the education
    golden set is ever fixed upstream, this fails and the finding gets retired
    rather than lingering as a stale complaint about data that is now correct.
    """
    from eval.retrieval.dataset import load_education_golden_cases

    findings = (repo_root / DATA_QUALITY_DOC).read_text(encoding="utf-8")

    load_education_golden_cases()
    from eval.retrieval.dataset import UNRESOLVABLE_EDUCATION_RULES

    assert UNRESOLVABLE_EDUCATION_RULES, (
        "the education golden set no longer cites nonexistent rules; retire finding F-1"
    )
    for rule_id in UNRESOLVABLE_EDUCATION_RULES:
        assert rule_id in findings, f"{rule_id} is broken but undocumented"
        assert not citation_resolver.citation_exists(f"POL-002 {rule_id}")

    # And the mis-paired citations the document names.
    for citation, actual_policy in (
        ("POL-005 EDU-RG-001", "POL-003"),
        ("POL-010 EDU-INTL-001", "POL-012"),
    ):
        assert citation in findings
        assert not citation_resolver.citation_exists(citation), (
            f"{citation} now resolves; retire that part of finding F-1"
        )
        rule_id = citation.split()[1]
        assert citation_resolver.citation_exists(f"{actual_policy} {rule_id}")


def test_the_non_utf8_finding_is_still_true(repo_root):
    """The five cp1252 application packets named in F-2 are still cp1252."""
    findings = (repo_root / DATA_QUALITY_DOC).read_text(encoding="utf-8")
    still_broken = []
    for name in (
        "APP-2026-00023",
        "APP-2026-00030",
        "APP-2026-00085",
        "APP-2026-00097",
        "APP-2026-00177",
    ):
        assert name in findings, f"{name} is not named in the finding"
        path = repo_root / f"synthetic_data/education/applications/{name}.json"
        try:
            path.read_bytes().decode("utf-8")
        except UnicodeDecodeError:
            still_broken.append(name)
    assert len(still_broken) == 5, (
        f"only {len(still_broken)} of 5 packets are still non-UTF-8; update finding F-2"
    )

    # And the tolerant loader handles all of them.
    from src.domain import load_application

    for name in still_broken:
        packet = load_application(
            repo_root / f"synthetic_data/education/applications/{name}.json"
        )
        assert packet["application_id"] == name


def test_published_headline_figures_match_the_measurements(repo_root):
    """`scripts/check_published_figures.py`, as a test."""
    results = repo_root / "eval" / "results" / "retrieval_eval.json"
    if not results.exists():
        pytest.skip("no evaluation results; run eval/retrieval/run_retrieval_eval.py")

    completed = subprocess.run(
        [sys.executable, "scripts/check_published_figures.py", "--quiet"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_transcribed_tables_match_the_result_files(repo_root):
    """`scripts/verify_doc_tables.py`, as a test."""
    if not (repo_root / "eval" / "results" / "retrieval_ablation.json").exists():
        pytest.skip("no ablation results; run eval/retrieval/ablation.py")

    completed = subprocess.run(
        [sys.executable, "scripts/verify_doc_tables.py", "--quiet"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_the_requirements_mapping_covers_the_mandatory_requirements(repo_root):
    """Every retrieval-bearing requirement id appears in the mapping."""
    mapping = (repo_root / "docs" / "rag" / "REQUIREMENTS_MAPPING.md").read_text(
        encoding="utf-8"
    )
    for requirement in (
        "REQ-029",  # Evidence-in-Repo
        "REQ-030",  # Citation-Resolves
        "REQ-031",  # Synthetic-Data / PII
        "REQ-032",  # Open-source & Gemini-only
        "REQ-033",  # Reproducibility
        "REQ-035",  # Python 3.11+ / LangGraph
        "REQ-036",  # Gemini only
        "REQ-037",  # MCP
        "REQ-039",  # Chroma or FAISS + Sentence-Transformers
        "REQ-044",  # AC-01 current policy + citation
        "REQ-049",  # AC-06 untrusted input
        "REQ-050",  # AC-07 tool log
        "REQ-076",  # agentic-RAG tool
        "REQ-077",  # Phoenix instrumentation
    ):
        assert requirement in mapping, f"{requirement} is not mapped"


def test_the_requirements_mapping_separates_requirements_from_decisions(repo_root):
    """A design choice must not be presented as a mandate."""
    mapping = (repo_root / "docs" / "rag" / "REQUIREMENTS_MAPPING.md").read_text(
        encoding="utf-8"
    )
    assert "Architecture decisions (not requirements)" in mapping
    for decision in ("BM25", "Reciprocal rank fusion", "cross-encoder"):
        assert decision.lower() in mapping.lower()
    # The stack requirement is quoted verbatim, so nobody has to take it on trust.
    assert "Chroma or FAISS + Sentence-Transformers (local)" in mapping


def test_deviations_are_declared(repo_root):
    mapping = (repo_root / "docs" / "rag" / "REQUIREMENTS_MAPPING.md").read_text(
        encoding="utf-8"
    )
    assert "## 4. Deviations" in mapping
    assert "data/policy_corpus/" in mapping


def test_the_index_manifest_agrees_with_the_documented_counts(repo_root, config):
    """The counts documents quote are the counts the build recorded."""
    manifest_path = config.manifest_path
    if not manifest_path.exists():
        pytest.skip("indexes not built")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    readme = (repo_root / "docs" / "rag" / "README.md").read_text(encoding="utf-8")
    for key, product in manifest["products"].items():
        assert str(product["source_document_count"]) in readme, (
            f"{key} document count {product['source_document_count']} is not in the README"
        )
        assert str(product["chunk_count"]) in readme, (
            f"{key} chunk count {product['chunk_count']} is not in the README"
        )
