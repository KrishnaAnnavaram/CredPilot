#!/usr/bin/env python
"""Check that headline metrics quoted in docs/ match the committed measurements.

    python scripts/check_published_figures.py

A document that quotes ``rule_recall@5 = 0.9709`` while
``eval/results/retrieval_eval.json`` says ``0.9514`` is worse than a document
with no number in it: the reader has no way to tell which one is stale. This
reads the committed result files and reports any quoted headline metric that no
longer matches.

**What it checks.** A line that names a headline metric *and* carries a
four-decimal figure. That deliberately excludes figures which are not headline
metrics — a DTI ratio of 0.4400 from a worked example, a delta of +0.0314
computed between two rows, a per-product figure inside an ablation table. Those
are checked by the scripts that generate them.

**Historical figures.** A line ending in ``<!-- was -->`` is a deliberate
before/after record and is skipped: the failure analysis quotes what a metric
*used to be*, and that must not be rewritten when the metric moves.

Exits non-zero when a quoted headline metric is stale.
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

RESULTS = REPO_ROOT / "eval" / "results" / "retrieval_eval.json"
INTEGRITY = REPO_ROOT / "data" / "vectorstore" / "index_integrity.json"

WATCHED_DOCUMENTS = (
    "README.md",
    "docs/rag/README.md",
    "docs/rag/REQUIREMENTS_MAPPING.md",
)

EVAL_REPORT = REPO_ROOT / "reports" / "eval_report.json"

#: ``key in eval_report.json macro`` -> the label it is published as.
#:
#: The end-to-end figures. They live in a different file from the retrieval ones
#: and are re-derived the same way, because a headline number nobody re-derives is
#: a number that drifts the first time the code moves.
END_TO_END_HEADLINE = {
    "outcome_accuracy": "outcome_accuracy",
    "directional_agreement": "directional_agreement",
    "citation_recall": "citation_recall",
    "judge_faithfulness": "judge_faithfulness",
    "judge_answer_relevancy": "judge_answer_relevancy",
}

#: ``key in retrieval_eval.json authored macro`` -> the label it is published as.
HEADLINE = {
    "macro_policy_recall@5": "policy_recall@5",
    "macro_rule_recall@5": "rule_recall@5",
    "macro_policy_recall@3": "policy_recall@3",
    "macro_rule_recall@3": "rule_recall@3",
    "macro_rule_mrr@10": "rule_mrr@10",
    "macro_policy_mrr@10": "policy_mrr@10",
    "macro_version_accuracy": "version_accuracy",
}

_FIGURE = re.compile(r"\b(\d\.\d{4})\b")
_HISTORICAL = re.compile(r"<!--\s*was\s*-->\s*$")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    from src.console import use_utf8_stdio

    use_utf8_stdio()

    if not RESULTS.exists():
        print(f"no results at {RESULTS.relative_to(REPO_ROOT)}; run the evaluation first")
        return 1

    macro = json.loads(RESULTS.read_text(encoding="utf-8"))["authored"]["macro"]
    measured = {
        label: round(float(macro[key]), 4) for key, label in HEADLINE.items() if key in macro
    }

    if INTEGRITY.exists():
        metrics = json.loads(INTEGRITY.read_text(encoding="utf-8"))["metrics"]
        measured["citation_validity"] = round(float(metrics["citation_validity"]), 4)
        measured["cross_product_contamination"] = round(
            float(metrics["cross_product_contamination_rate"]), 4
        )

    # The end-to-end figures, re-derived the same way. Absent before the agent
    # evaluation has been run, which is why this is conditional rather than
    # required — a clean checkout with no key still checks everything else.
    if EVAL_REPORT.exists():
        end_to_end = json.loads(EVAL_REPORT.read_text(encoding="utf-8"))["macro"]
        for key, label in END_TO_END_HEADLINE.items():
            value = end_to_end.get(key)
            if isinstance(value, (int, float)):
                measured[label] = round(float(value), 4)

    print("Measured (from committed results)")
    for label, value in sorted(measured.items()):
        print(f"  {label:<32} {value:.4f}")
    print()

    stale: list[str] = []
    checked = 0
    for relative in WATCHED_DOCUMENTS:
        path = REPO_ROOT / relative
        if not path.exists():
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if _HISTORICAL.search(line):
                continue
            for label, expected in measured.items():
                if label not in line:
                    continue
                figures = {float(f) for f in _FIGURE.findall(line)}
                if not figures:
                    continue
                checked += 1
                if not any(abs(f - expected) < 5e-5 for f in figures):
                    stale.append(
                        f"{relative}:{number}: {label} quoted as "
                        f"{sorted(figures)} — measured {expected:.4f}"
                    )

    if stale:
        print("STALE FIGURES")
        for entry in stale:
            print(f"  {entry}")
        print()
        print("Re-run 'python scripts/regenerate_evidence.py', then update the document.")
        return 1

    if not args.quiet:
        print(f"{checked} quoted headline metric(s) checked; all match the measurements.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
