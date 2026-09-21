#!/usr/bin/env python
"""Verify the transcribed tables in the benchmark and ablation documents.

    python scripts/verify_doc_tables.py

``check_published_figures.py`` checks metrics quoted by name in prose. This
checks the other failure mode: a table transcribed from JSON by hand, where a
digit gets dropped or a subtraction is done wrong. It re-derives every row and
every delta from the result files and compares against what the document says.

It found one real error on its first run — the ablation document claimed fusion
added ``+0.0345`` policy recall where the measured figure was ``+0.0207``.

Exits non-zero on any mismatch.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

TOLERANCE = 5e-5

#: (document, result file, how to pull comparable rows out of the result)
ABLATION_DOC = REPO_ROOT / "docs" / "rag" / "RETRIEVAL_ABLATION.md"
ABLATION_JSON = REPO_ROOT / "eval" / "results" / "retrieval_ablation.json"
SWEEP_JSON = REPO_ROOT / "eval" / "results" / "pipeline_sweep.json"
RERANKER_DOC = REPO_ROOT / "docs" / "rag" / "RERANKER_BENCHMARK.md"
RERANKER_JSON = REPO_ROOT / "eval" / "results" / "reranker_benchmark.json"
EMBEDDING_DOC = REPO_ROOT / "docs" / "rag" / "EMBEDDING_BENCHMARK.md"
EMBEDDING_JSON = REPO_ROOT / "eval" / "results" / "embedding_benchmark.json"

_ROW = re.compile(r"^\s*\|(.+)\|\s*$")
_FIGURE = re.compile(r"(-?\d\.\d{4})")

#: Prose uses a typographic minus (U+2212) and en dash; the regex wants ASCII.
_MINUS = str.maketrans({"−": "-", "–": "-"})


def figures(text: str) -> list[str]:
    """Every four-decimal figure in a line, with typographic minuses normalized."""
    return _FIGURE.findall(text.translate(_MINUS))


def row_cells(line: str) -> list[str] | None:
    match = _ROW.match(line)
    if not match:
        return None
    return [cell.strip() for cell in match.group(1).split("|")]


def check_ablation() -> list[str]:
    """Each configuration row, and each incremental delta, against the JSON."""
    if not (ABLATION_DOC.exists() and ABLATION_JSON.exists()):
        return []
    data = json.loads(ABLATION_JSON.read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in data["configurations"]}
    deltas = {(d["from"], d["to"]): d for d in data.get("deltas", [])}

    problems: list[str] = []
    for number, line in enumerate(ABLATION_DOC.read_text(encoding="utf-8").splitlines(), 1):
        cells = row_cells(line)
        if not cells:
            continue

        # Configuration rows: | **A** | BM25 only | 0.8616 | ...
        config_id = re.fullmatch(r"\*{0,2}([A-F])\*{0,2}", cells[0] or "")
        if config_id and config_id.group(1) in by_id:
            macro = by_id[config_id.group(1)]["macro"]
            expected = {
                round(float(v), 4)
                for k, v in macro.items()
                if k.startswith("macro_") and isinstance(v, (int, float))
            }
            for figure in figures(line):
                if not any(abs(float(figure) - e) < TOLERANCE for e in expected):
                    problems.append(
                        f"RETRIEVAL_ABLATION.md:{number}: row {config_id.group(1)} "
                        f"quotes {figure}, which is not a measured macro metric"
                    )
            continue

        # Delta rows: | A → B  dense instead of lexical | +0.0582 | ...
        arrow = re.match(r"\*{0,2}([A-F])\s*(?:→|->)\s*([A-F])\b", cells[0] or "")
        if arrow:
            key = (arrow.group(1), arrow.group(2))
            if key not in deltas:
                continue
            measured = {
                round(float(v), 4) for v in deltas[key]["delta"].values()
            }
            for figure in figures(line):
                if not any(abs(float(figure) - m) < TOLERANCE for m in measured):
                    problems.append(
                        f"RETRIEVAL_ABLATION.md:{number}: delta {key[0]}→{key[1]} "
                        f"quotes {figure}, measured deltas are {sorted(measured)}"
                    )
    return problems


def check_sweep_table() -> list[str]:
    """The funnel-width table, wherever it appears."""
    if not SWEEP_JSON.exists():
        return []
    data = json.loads(SWEEP_JSON.read_text(encoding="utf-8"))
    by_funnel = {
        (c["dense_top_k"], c["lexical_top_k"], c["fusion_top_k"], c["rerank_top_k"]): c
        for c in data["configurations"]
    }

    problems: list[str] = []
    for doc in (ABLATION_DOC, REPO_ROOT / "docs" / "failure-analysis.md"):
        if not doc.exists():
            continue
        for number, line in enumerate(doc.read_text(encoding="utf-8").splitlines(), 1):
            cells = row_cells(line)
            if not cells or len(cells) < 5:
                continue
            try:
                funnel = tuple(int(re.sub(r"\D", "", c)) for c in cells[:4])
            except ValueError:
                continue
            row = by_funnel.get(funnel)
            if row is None:
                continue
            expected = {
                round(float(v), 4)
                for v in row["macro"].values()
                if isinstance(v, (int, float))
            }
            for figure in figures("|".join(cells[4:])):
                if not any(abs(float(figure) - e) < TOLERANCE for e in expected):
                    problems.append(
                        f"{doc.name}:{number}: funnel {funnel} quotes {figure}, "
                        f"which is not a measured macro metric for that row"
                    )
    return problems


def check_benchmark(doc: Path, results: Path, key: str) -> list[str]:
    """A benchmark document's per-candidate rows."""
    if not (doc.exists() and results.exists()):
        return []
    data = json.loads(results.read_text(encoding="utf-8"))
    by_model = {
        (c.get(key) or "(none)"): c for c in data["candidates"] if "error" not in c
    }

    problems: list[str] = []
    for number, line in enumerate(doc.read_text(encoding="utf-8").splitlines(), 1):
        cells = row_cells(line)
        if not cells:
            continue
        label = re.sub(r"[`*]", "", cells[0]).strip()
        candidate = next(
            (c for name, c in by_model.items() if name and name in label), None
        )
        if candidate is None:
            continue
        expected = {
            round(float(v), 4)
            for v in candidate["macro"].values()
            if isinstance(v, (int, float))
        }
        for metrics in candidate["per_product"].values():
            expected |= {
                round(float(v), 4) for v in metrics.values() if isinstance(v, (int, float))
            }
        for figure in figures("|".join(cells[1:])):
            if not any(abs(float(figure) - e) < TOLERANCE for e in expected):
                problems.append(
                    f"{doc.name}:{number}: {label} quotes {figure}, "
                    f"which is not a measured metric for that candidate"
                )
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    from src.console import use_utf8_stdio

    use_utf8_stdio()

    problems = (
        check_ablation()
        + check_sweep_table()
        + check_benchmark(RERANKER_DOC, RERANKER_JSON, "model")
        + check_benchmark(EMBEDDING_DOC, EMBEDDING_JSON, "model")
    )

    if problems:
        print("TABLE MISMATCHES")
        for problem in problems:
            print(f"  {problem}")
        print()
        print(f"{len(problems)} figure(s) in the documents do not match the result files.")
        return 1

    if not args.quiet:
        print("Every transcribed table figure matches its result file.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
