"""Loading the retrieval evaluation sets.

Two kinds of case feed the evaluation:

* **Hand-authored policy questions** (``eval/retrieval/<product>/queries.jsonl``)
  phrased the way an underwriter would ask them, with rule-level ground truth
  taken from the committed corpus.
* **Golden-derived application cases**, built from each product's golden set.
  These carry only policy-level ground truth, because the golden set records
  which policies govern an application rather than which chunk answers a
  question.

Golden files are read **here and nowhere else in the codebase**. Runtime modules
must never touch them; ``tests/rag/test_no_golden_leakage.py`` enforces that.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

from src.config import REPO_ROOT
from src.domain import LendingProductDomain, read_text_tolerant

EVAL_ROOT = REPO_ROOT / "eval" / "retrieval"

#: The golden directories. Referenced only from evaluation code.
GOLDEN_SETS = {
    LendingProductDomain.MORTGAGE: REPO_ROOT / "synthetic_data" / "mortgage" / "golden_set",
    LendingProductDomain.EDUCATION_LOAN: REPO_ROOT / "synthetic_data" / "education" / "golden_set",
}


@dataclass
class EvalCase:
    """One retrieval evaluation case."""

    query_id: str
    product_domain: LendingProductDomain
    query: str
    category: str = "general"
    as_of_date: str | None = None
    application_id: str | None = None
    expected_rule_ids: list[str] = field(default_factory=list)
    expected_policy_ids: list[str] = field(default_factory=list)
    expected_policy_versions: dict[str, str] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    source: str = "authored"

    @classmethod
    def from_json(cls, payload: dict[str, Any], source: str = "authored") -> "EvalCase":
        return cls(
            query_id=payload["query_id"],
            product_domain=LendingProductDomain.from_any(payload["product_domain"]),
            query=payload["query"],
            category=payload.get("category", "general"),
            as_of_date=payload.get("as_of_date"),
            application_id=payload.get("application_id"),
            expected_rule_ids=list(payload.get("expected_rule_ids") or []),
            expected_policy_ids=list(payload.get("expected_policy_ids") or []),
            expected_policy_versions=dict(payload.get("expected_policy_versions") or {}),
            context=dict(payload.get("context") or {}),
            tags=list(payload.get("tags") or []),
            source=source,
        )


def _read_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    for line in read_text_tolerant(path).splitlines():
        line = line.strip()
        if line:
            yield json.loads(line)


def load_authored_cases(domain: LendingProductDomain) -> list[EvalCase]:
    """Load the hand-authored query set for one product."""
    path = EVAL_ROOT / domain.corpus_key / "queries.jsonl"
    if not path.exists():
        return []
    return [EvalCase.from_json(row, source="authored") for row in _read_jsonl(path)]


def load_mortgage_golden_cases(limit: int | None = None) -> list[EvalCase]:
    """Derive policy-level cases from the mortgage golden set.

    The golden set records, per application, which policies and which versions
    governed it. That is exactly the ground truth for "which policy applies to
    this application?", so each golden case becomes one retrieval case scored at
    policy and version level.
    """
    root = GOLDEN_SETS[LendingProductDomain.MORTGAGE]
    cases_path = root / "evaluation_cases.jsonl"
    expected_path = root / "expected_results.jsonl"
    if not (cases_path.exists() and expected_path.exists()):
        return []

    expected = {row["application_id"]: row for row in _read_jsonl(expected_path)}
    out: list[EvalCase] = []
    for row in _read_jsonl(cases_path):
        app_id = row["application_id"]
        exp = expected.get(app_id)
        if not exp:
            continue
        versions = {
            v["policy_id"]: v["version"] for v in exp.get("applicable_policy_versions", [])
        }
        out.append(
            EvalCase(
                query_id=f"GOLD-MTG-{app_id}",
                product_domain=LendingProductDomain.MORTGAGE,
                query=row["question"],
                category="golden-application",
                as_of_date=row.get("as_of_date"),
                application_id=app_id,
                # Rule-level truth exists here too, but a single retrieval call
                # answering one broad question is not expected to surface all ~20
                # rules that govern a whole file; only policy-level recall is
                # scored, and rule ids are kept for the failure analysis.
                expected_rule_ids=[],
                expected_policy_ids=list(exp.get("applicable_policy_ids", [])),
                expected_policy_versions=versions,
                context={},
                tags=list(row.get("features_being_tested") or []),
                source="golden",
            )
        )
        if limit and len(out) >= limit:
            break
    return out


#: Golden citations that name a rule id absent from the committed corpus. They
#: are counted, reported and excluded from ground truth — no retriever can find a
#: rule that was never written. See ``docs/rag/DATA_QUALITY_FINDINGS.md``.
UNRESOLVABLE_EDUCATION_RULES: dict[str, int] = {}


def load_education_golden_cases(limit: int | None = None) -> list[EvalCase]:
    """Derive policy-level cases from the education golden set.

    The education golden set cites ``POL-002 EDU-UW-001`` pairs, and 21 of its 59
    citations are defective:

    * **12** pair a real rule with the wrong policy document — ``POL-005
      EDU-RG-001`` in GOLD-01, when ``EDU-RG-001`` lives in ``POL-003``. The rule
      id is the reliable half, so the policy is resolved from the corpus rather
      than trusted from the citation string.
    * **9** name a rule id that appears nowhere in the corpus — ``EDU-CERT-001``,
      ``EDU-AGG-001``, ``EDU-REFI-001``, ``EDU-FRAUD-001``. These are dropped
      from ground truth and recorded in :data:`UNRESOLVABLE_EDUCATION_RULES`,
      because scoring a retriever against a rule that does not exist measures the
      corpus, not the retriever.

    Both are data defects in the committed golden set, not retrieval failures.
    They are handled here rather than quietly absorbed into the metrics.
    """
    root = GOLDEN_SETS[LendingProductDomain.EDUCATION_LOAN]
    path = root / "evaluation_cases.jsonl"
    if not path.exists():
        return []

    rule_to_policy = _education_rule_index()
    UNRESOLVABLE_EDUCATION_RULES.clear()
    out: list[EvalCase] = []
    for row in _read_jsonl(path):
        rules: list[str] = []
        policies: list[str] = []
        for citation in row.get("expected_policy_citations") or []:
            parts = str(citation).split()
            rule = next((p for p in parts if p.startswith("EDU-")), None)
            if rule:
                resolved = rule_to_policy.get(rule)
                if resolved is None:
                    UNRESOLVABLE_EDUCATION_RULES[rule] = (
                        UNRESOLVABLE_EDUCATION_RULES.get(rule, 0) + 1
                    )
                    continue
                rules.append(rule)
                policies.append(resolved)
            else:
                policies.extend(p for p in parts if p.startswith("POL-"))
        out.append(
            EvalCase(
                query_id=f"GOLD-EDU-{row['case_id']}",
                product_domain=LendingProductDomain.EDUCATION_LOAN,
                query=_education_question(row),
                category="golden-application",
                as_of_date="2026-08-01",
                application_id=row.get("input_application_id"),
                expected_rule_ids=sorted(set(rules)),
                expected_policy_ids=sorted(set(policies)),
                expected_policy_versions={},
                context={"product_code": row.get("product_code")},
                tags=[row.get("product_code", ""), row.get("difficulty", "")],
                source="golden",
            )
        )
        if limit and len(out) >= limit:
            break
    return out


def _education_question(row: dict[str, Any]) -> str:
    """Turn a golden case into the policy question an underwriter would ask.

    Only the product and the case's own summary are used — never the expected
    decision, grade, reason codes or rationale, which would leak the answer into
    the query.
    """
    product = row.get("product_code", "")
    summary = str(row.get("input_summary", "")).split(".")[0]
    return (
        f"Which lending policies govern this {product} education loan application? {summary}."
    ).strip()


def _education_rule_index() -> dict[str, str]:
    """Map every education rule id to the policy document that declares it."""
    from src.config import get_config
    from src.rag.parsers import get_parser
    from src.rag.parsers.base import coerce_str_list, parse_front_matter

    config = get_config()
    product = config.products["education"]
    parser = get_parser("education")
    index: dict[str, str] = {}
    for path in parser.corpus_files(product.corpus_root):
        text = read_text_tolerant(path)
        fm, _, _ = parse_front_matter(text, str(path))
        policy_id = str(fm.get("policy_id", ""))
        for rule in coerce_str_list(fm.get("rule_ids")):
            index[rule] = policy_id
    return index


def load_cases(
    domain: LendingProductDomain,
    *,
    include_authored: bool = True,
    include_golden: bool = True,
    golden_limit: int | None = None,
) -> list[EvalCase]:
    """Load every evaluation case for one product."""
    cases: list[EvalCase] = []
    if include_authored:
        cases.extend(load_authored_cases(domain))
    if include_golden:
        if domain is LendingProductDomain.MORTGAGE:
            cases.extend(load_mortgage_golden_cases(golden_limit))
        else:
            cases.extend(load_education_golden_cases(golden_limit))
    return cases


def load_all_cases(**kwargs) -> dict[LendingProductDomain, list[EvalCase]]:
    return {domain: load_cases(domain, **kwargs) for domain in LendingProductDomain}
