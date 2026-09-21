"""Runtime code never reads the answers.

An evaluation is only worth running if the system under test could not have seen
the answer. Three boundaries are enforced here:

1. No runtime module imports or reads either product's ``golden_set/``.
2. No golden content reaches the index, a chunk, a prompt or a log.
3. No runtime module reads a structured table holding an outcome — the computed
   ratios, the rule evaluations, the eligibility results, the decisions.

Only ``eval/`` may read the golden sets, and it does so through
``eval/retrieval/dataset.py``.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

import pytest

from src.application_context import OUTCOME_TABLES, OutcomeAccessError, rows_for

#: Every tree that runs in production. ``eval/`` and ``tests/`` are excluded by
#: design: evaluation is exactly the code that is allowed to know the answer.
RUNTIME_TREES = ("src", "mcp_server", "scripts")

_GOLDEN_MARKERS = ("golden_set", "expected_results", "evaluation_cases", "expected_outputs")


def _runtime_files(repo_root: Path) -> list[Path]:
    files: list[Path] = []
    for tree in RUNTIME_TREES:
        root = repo_root / tree
        if root.exists():
            files.extend(
                p for p in root.rglob("*.py") if "__pycache__" not in p.parts
            )
    return sorted(files)


def test_runtime_trees_are_not_empty(repo_root):
    """Guard the guard: an empty file list would make every check below vacuous."""
    files = _runtime_files(repo_root)
    assert len(files) >= 15, f"only {len(files)} runtime modules found"


@pytest.mark.parametrize("marker", _GOLDEN_MARKERS)
def test_no_runtime_module_mentions_a_golden_path(repo_root, marker):
    offenders = []
    for path in _runtime_files(repo_root):
        text = path.read_text(encoding="utf-8")
        for number, line in enumerate(text.splitlines(), start=1):
            if marker not in line:
                continue
            stripped = line.strip()
            # A comment or docstring line saying the code must *not* read the
            # golden set is the opposite of a violation.
            if stripped.startswith("#") or _is_prose(text, number):
                continue
            offenders.append(f"{path.relative_to(repo_root)}:{number}: {stripped[:100]}")
    assert not offenders, offenders


def _is_prose(text: str, line_number: int) -> bool:
    """True when the line sits inside a module, class or function docstring."""
    try:
        tree = ast.parse(text)
    except SyntaxError:  # pragma: no cover
        return False
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        doc = ast.get_docstring(node, clean=False)
        if not doc:
            continue
        body = node.body[0]
        start = getattr(body, "lineno", 0)
        end = getattr(body, "end_lineno", start)
        if start <= line_number <= end:
            return True
    return False


def test_no_runtime_module_imports_the_eval_package(repo_root):
    """Runtime must not reach into evaluation code, which does read the answers."""
    offenders = []
    for path in _runtime_files(repo_root):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:  # pragma: no cover
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            else:
                continue
            for name in names:
                if name == "eval" or name.startswith("eval."):
                    offenders.append(f"{path.relative_to(repo_root)}:{node.lineno}: {name}")
    assert not offenders, offenders


def test_golden_directories_exist_and_are_outside_the_corpus_roots(repo_root, config):
    """The thing being guarded is really there, and really separate."""
    for key, product in config.products.items():
        golden = repo_root / "synthetic_data" / key / "golden_set"
        assert golden.exists(), f"{key} golden set is missing"
        assert not str(golden).startswith(str(product.corpus_root)), (
            f"{key} golden set sits inside the policy corpus root"
        )


def test_no_golden_content_is_indexed(config, indexes_built, repo_root):
    """No indexed chunk originates from, or quotes, the golden set."""
    if not indexes_built:
        pytest.skip("indexes not built")
    from src.rag.vectorstore import PolicyVectorStore
    from src.domain import LendingProductDomain

    for domain in LendingProductDomain:
        store = PolicyVectorStore(config, domain)
        for record in store.get_all(include_documents=True):
            source = record["metadata"].get("source_path", "")
            assert "golden" not in source, f"{record['chunk_id']} came from {source}"
            document = record.get("document") or ""
            assert "expected_decision" not in document
            assert "expected_recommendation" not in document


def test_no_golden_case_id_appears_in_the_index(config, indexes_built):
    """A golden case id in retrievable text would be a direct answer leak."""
    if not indexes_built:
        pytest.skip("indexes not built")
    from src.rag.vectorstore import PolicyVectorStore
    from src.domain import LendingProductDomain

    pattern = re.compile(r"\b(?:CASE-APP-\d{6}|GOLD-\d{2})\b")
    for domain in LendingProductDomain:
        store = PolicyVectorStore(config, domain)
        for record in store.get_all(include_documents=True):
            hit = pattern.search(record.get("document") or "")
            assert not hit, f"{record['chunk_id']} contains golden case id {hit.group(0)}"


def test_retrieved_evidence_carries_no_expected_outcome(retriever):
    """The evidence model has no field an expected answer could ride in on."""
    from src.domain import LendingProductDomain
    from src.rag.models import PolicyEvidence, PolicyRetrievalRequest

    forbidden = {
        "expected_decision",
        "expected_recommendation",
        "expected_eligibility",
        "expected_risk_level",
        "expected_citations",
        "scenario_id",
        "case_id",
        "golden",
    }
    assert not (set(PolicyEvidence.model_fields) & forbidden)

    result = retriever.retrieve(
        PolicyRetrievalRequest(
            product_domain=LendingProductDomain.MORTGAGE,
            query_text="What is the maximum back-end debt-to-income ratio?",
            as_of_date="2026-07-08",
        )
    )
    payload = json.dumps([e.model_dump(mode="json") for e in result.evidence])
    for marker in ("expected_decision", "expected_recommendation", "CASE-APP-", "GOLD-"):
        assert marker not in payload


def test_logs_carry_no_golden_content(repo_root):
    """Nothing the system wrote quotes an expected answer."""
    log_dir = repo_root / "logs"
    if not log_dir.exists():
        pytest.skip("no logs written yet")
    offenders = []
    for path in log_dir.glob("*.jsonl"):
        text = path.read_text(encoding="utf-8")
        for marker in ("expected_decision", "expected_recommendation", "CASE-APP-", "golden_set"):
            if marker in text:
                offenders.append(f"{path.name}: {marker}")
    assert not offenders, offenders


# --------------------------------------------------- outcome tables are off limits too


@pytest.mark.parametrize("table", sorted(OUTCOME_TABLES))
def test_outcome_tables_cannot_be_read(table):
    with pytest.raises(OutcomeAccessError, match="outcomes, not inputs"):
        rows_for(table, "APP-000056")


def test_input_tables_can_be_read():
    """The boundary lets inputs through, or it would not be a boundary."""
    assert rows_for("properties", "APP-000056")
    assert rows_for("loans", "APP-000056")
    assert rows_for("liabilities", "APP-000056")


def test_the_outcome_table_list_covers_the_answers(repo_root):
    """Every structured table is classified as an input or an outcome."""
    from src.application_context import INPUT_TABLES

    structured = repo_root / "synthetic_data" / "mortgage" / "structured"
    on_disk = {p.stem for p in structured.glob("*.csv")}
    classified = INPUT_TABLES | OUTCOME_TABLES
    unclassified = on_disk - classified
    assert not unclassified, f"unclassified structured tables: {sorted(unclassified)}"
    assert not (INPUT_TABLES & OUTCOME_TABLES)


def test_the_graph_never_reads_an_outcome_table(repo_root):
    """The enrichment path touches inputs only."""
    from src.application_context import build_underwriting_input

    packet = build_underwriting_input(
        repo_root / "synthetic_data/mortgage/applications/APP-000056.json"
    )
    payload = json.dumps(packet, default=str)
    for marker in ("eligibility_result", "rule_evaluation", "decision_reason", "risk_flag"):
        assert marker not in payload
    # And it did bring the inputs it is supposed to bring.
    assert packet["property_costs"]["annual_property_tax"]
    assert packet["verified_liabilities"]
