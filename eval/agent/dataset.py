"""Loading the end-to-end agent evaluation cases.

The two products record their ground truth in completely different places, and
the difference is not cosmetic:

* **Education** keeps it inside ``golden_set/evaluation_cases.jsonl`` — 20
  hand-written cases carrying ``expected_decision``, ``expected_risk_grade``,
  ``expected_policy_citations`` and a ``must_not_do`` list.
* **Mortgage** keeps none of it in the golden file. Its 75 cases name an
  application and a question; the expected answer lives in the structured
  outcome tables (``decisions.csv``, ``eligibility_results.csv``,
  ``decision_reasons.csv``) that :mod:`src.application_context` forbids runtime
  code from opening.

Both are read **here and in the other evaluation modules only**. Nothing under
``src/`` may import this file, and ``tests/rag/test_no_golden_leakage.py``
checks that it does not.
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

from src.config import REPO_ROOT
from src.domain import LendingProductDomain

GOLDEN_SETS = {
    LendingProductDomain.MORTGAGE: REPO_ROOT / "synthetic_data" / "mortgage" / "golden_set",
    LendingProductDomain.EDUCATION_LOAN: REPO_ROOT / "synthetic_data" / "education" / "golden_set",
}
MORTGAGE_STRUCTURED = REPO_ROOT / "synthetic_data" / "mortgage" / "structured"
EDUCATION_APPLICATIONS = REPO_ROOT / "synthetic_data" / "education" / "applications"

#: The outcome families a recommendation can fall into.
#:
#: ``APPROVE_WITH_CONDITIONS`` is listed because the golden sets use it — six
#: cases across the two products — and deliberately *not* produced by
#: :func:`src.graph.recommendation_node`, which emits approve, refer or decline
#: and nothing else. Folding it into APPROVE would score the system correct for
#: an answer it is structurally incapable of giving, so it stays its own class
#: and the report names how many cases it covers. See ``expressible``.
APPROVE = "APPROVE"
APPROVE_WITH_CONDITIONS = "APPROVE_WITH_CONDITIONS"
REFER = "REFER"
DECLINE = "DECLINE"

#: Every spelling the two golden sources use, mapped to one family.
_OUTCOME_FAMILY = {
    "APPROVE": APPROVE,
    "APPROVE_RECOMMENDATION": APPROVE,
    "APPROVE_WITH_CONDITIONS": APPROVE_WITH_CONDITIONS,
    "DECLINE": DECLINE,
    "DECLINE_RECOMMENDATION": DECLINE,
    "REFER": REFER,
    "REFER_MANUAL": REFER,
    "REFER_RECOMMENDATION": REFER,
    "MANUAL_REVIEW_REQUIRED": REFER,
    "PENDING_HUMAN_REVIEW": REFER,
    "SUSPENDED_INCOMPLETE": REFER,
}

#: What the system is able to emit at all.
EXPRESSIBLE_FAMILIES = frozenset({APPROVE, REFER, DECLINE})

#: Approve-with-conditions is an approval in direction even though it is not the
#: same recommendation, so directional agreement can still be scored for it.
_DIRECTION = {
    APPROVE: "POSITIVE",
    APPROVE_WITH_CONDITIONS: "POSITIVE",
    REFER: "NEUTRAL",
    DECLINE: "NEGATIVE",
}


def outcome_family(value: str | None) -> str | None:
    """Normalize any recorded outcome spelling to one family."""
    if not value:
        return None
    return _OUTCOME_FAMILY.get(str(value).strip().upper())


def direction_of(family: str | None) -> str | None:
    return _DIRECTION.get(family) if family else None


@dataclass
class AgentCase:
    """One end-to-end case: an application, and what should come back."""

    case_id: str
    product: LendingProductDomain
    application_id: str
    packet_path: Path
    question: str
    as_of_date: str | None = None
    expected_outcome: str | None = None
    expected_eligibility: str | None = None
    expected_risk_level: str | None = None
    expected_requires_human_review: bool | None = None
    expected_citations: list[str] = field(default_factory=list)
    expected_rule_ids: list[str] = field(default_factory=list)
    must_not_do: list[str] = field(default_factory=list)
    features: list[str] = field(default_factory=list)
    security_test_type: str | None = None
    difficulty: str | None = None
    title: str | None = None

    @property
    def expressible(self) -> bool:
        """Whether the system can produce this expected outcome at all."""
        return self.expected_outcome in EXPRESSIBLE_FAMILIES

    @property
    def expected_direction(self) -> str | None:
        return direction_of(self.expected_outcome)

    def as_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "product": self.product.value,
            "application_id": self.application_id,
            "as_of_date": self.as_of_date,
            "expected_outcome": self.expected_outcome,
            "expected_eligibility": self.expected_eligibility,
            "expected_risk_level": self.expected_risk_level,
            "expected_requires_human_review": self.expected_requires_human_review,
            "expected_citations": self.expected_citations,
            "expected_rule_ids": self.expected_rule_ids,
            "expressible": self.expressible,
            "difficulty": self.difficulty,
            "security_test_type": self.security_test_type,
            "title": self.title,
        }


# ================================================================== mortgage


def _read_csv(name: str) -> list[dict[str, str]]:
    path = MORTGAGE_STRUCTURED / f"{name}.csv"
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _mortgage_expectations() -> dict[str, dict[str, Any]]:
    """Expected outcome, eligibility, risk and citations, keyed by application.

    Only the ``underwriting_recommendation`` stage is used. ``decisions.csv``
    also holds a later ``credit_decision`` row for many files, recording what a
    human concluded afterwards — a different question from the one the copilot is
    asked, and scoring against it would penalise the system for failing to
    predict a human's subsequent judgement.
    """
    expectations: dict[str, dict[str, Any]] = {}

    for row in _read_csv("decisions"):
        if row.get("decision_stage") != "underwriting_recommendation":
            continue
        expectations[row["application_id"]] = {
            "outcome": outcome_family(row.get("result")),
            "raw_outcome": row.get("result"),
            "eligibility": (row.get("eligibility_result") or "").strip() or None,
            "risk_level": (row.get("risk_level") or "").strip() or None,
            "requires_human_review": str(row.get("requires_human_review", "")).lower() == "true",
            "citations": [],
            "rule_ids": [],
        }

    for row in _read_csv("eligibility_results"):
        entry = expectations.get(row["application_id"])
        if entry is None:
            continue
        # The column uses both separators: "CRD-SCR-003" alone, but also
        # "AST-FTC-003|AST-RSV-002|AST-SRC-001" where several rules decided
        # together. Splitting on only one leaves compound values as a single
        # nonsense identifier.
        raw = row.get("determining_rule_ids") or ""
        ids = [r.strip() for r in re.split(r"[;|]", raw) if r.strip()]
        entry["rule_ids"].extend(i for i in ids if i not in entry["rule_ids"])

    for row in _read_csv("decision_reasons"):
        entry = expectations.get(row["application_id"])
        if entry is None:
            continue
        rule_id = (row.get("rule_id") or "").strip()
        policy_id = (row.get("policy_id") or "").strip()
        version = (row.get("policy_version") or "").strip()
        if rule_id and rule_id not in entry["rule_ids"]:
            entry["rule_ids"].append(rule_id)
        if rule_id and policy_id:
            citation = (
                f"{policy_id} v{version} rule {rule_id}" if version
                else f"{policy_id} rule {rule_id}"
            )
            if citation not in entry["citations"]:
                entry["citations"].append(citation)

    return expectations


def load_mortgage_cases() -> list[AgentCase]:
    path = GOLDEN_SETS[LendingProductDomain.MORTGAGE] / "evaluation_cases.jsonl"
    expectations = _mortgage_expectations()
    cases: list[AgentCase] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        expected = expectations.get(row["application_id"], {})
        cases.append(
            AgentCase(
                case_id=row["case_id"],
                product=LendingProductDomain.MORTGAGE,
                application_id=row["application_id"],
                packet_path=REPO_ROOT / row["input_packet"],
                question=row["question"],
                as_of_date=row.get("as_of_date"),
                expected_outcome=expected.get("outcome"),
                expected_eligibility=expected.get("eligibility"),
                expected_risk_level=expected.get("risk_level"),
                expected_requires_human_review=expected.get("requires_human_review"),
                expected_citations=list(expected.get("citations") or []),
                expected_rule_ids=list(expected.get("rule_ids") or []),
                features=list(row.get("features_being_tested") or []),
                security_test_type=row.get("security_test_type"),
                title=row.get("scenario_name"),
            )
        )
    return cases


# ================================================================= education


#: The education golden set poses no per-case question; the mortgage set spells
#: one out. Phrased to match, so neither product is scored against an easier
#: prompt than the other.
EDUCATION_QUESTION = (
    "Assess this education loan application: determine product eligibility, evaluate "
    "the borrower and any cosigner, screen for risk, and produce an underwriting "
    "recommendation with the policy rules and calculations that support it."
)


def load_education_cases() -> list[AgentCase]:
    path = GOLDEN_SETS[LendingProductDomain.EDUCATION_LOAN] / "evaluation_cases.jsonl"
    cases: list[AgentCase] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        application_id = row["input_application_id"]
        cases.append(
            AgentCase(
                case_id=row["case_id"],
                product=LendingProductDomain.EDUCATION_LOAN,
                application_id=application_id,
                packet_path=EDUCATION_APPLICATIONS / f"{application_id}.json",
                question=EDUCATION_QUESTION,
                expected_outcome=outcome_family(row.get("expected_decision")),
                expected_risk_level=row.get("expected_risk_grade"),
                expected_citations=list(row.get("expected_policy_citations") or []),
                must_not_do=list(row.get("must_not_do") or []),
                difficulty=row.get("difficulty"),
                title=row.get("title"),
            )
        )
    return cases


# ====================================================================== both


def load_cases(
    products: "list[LendingProductDomain] | None" = None,
    *,
    limit_per_product: int | None = None,
) -> list[AgentCase]:
    """Every case for the requested products.

    ``limit_per_product`` takes the first *n* of each rather than the first *n*
    overall: mortgage has 75 cases to education's 20, so a flat limit would leave
    a "both products" run that was almost entirely mortgage.
    """
    wanted = set(products or list(LendingProductDomain))
    cases: list[AgentCase] = []
    for product, loader in (
        (LendingProductDomain.MORTGAGE, load_mortgage_cases),
        (LendingProductDomain.EDUCATION_LOAN, load_education_cases),
    ):
        if product not in wanted:
            continue
        product_cases = loader()
        cases.extend(product_cases[:limit_per_product] if limit_per_product else product_cases)
    return cases


def iter_cases(**kwargs: Any) -> Iterator[AgentCase]:
    yield from load_cases(**kwargs)


# ============================================================== rule coverage


#: Rule families the runtime actually implements, and where.
#:
#: This is a deliberately honest list. The corpora declare far more families than
#: the engine evaluates: rules in the others are retrieved, cited and shown to the
#: reader, but no code compares them against a threshold.
IMPLEMENTED_RULE_FAMILIES = {
    LendingProductDomain.MORTGAGE: {
        # -- the original four, in src/rules.py ------------------------------
        "DTI-CONV": "src/rules.py — affordability ceiling, with the compensating-factor extension",
        "CRD-SCR": "src/rules.py — minimum representative score, graduated by leverage in v2.0",
        "AST-RSV": "src/rules.py — minimum reserves, measured after the funds-to-close draw",
        "AST-FTC": "src/rules.py — funds-to-close sufficiency",
        # -- added in src/rule_families/mortgage_ext.py -----------------------
        "GEN-ELG": "src/rule_families/mortgage_ext.py — programme loan limit and "
                   "ability-to-repay from verified information",
        "DOC-REQ": "src/rule_families/mortgage_ext.py — the baseline document set and "
                   "its freshness windows; an incomplete file is suspended, not declined",
        "EMP-CNT": "src/rule_families/mortgage_ext.py — two-year history (refer, not "
                   "fail) and employment that has not yet started",
        "CRD-EVT": "src/rule_families/mortgage_ext.py — seasoning after bankruptcy, "
                   "foreclosure, deed in lieu, short sale and mortgage charge-off",
        "CRD-DLQ": "src/rule_families/mortgage_ext.py — housing and non-housing "
                   "delinquency, weighed separately",
        "AST-SRC": "src/rule_families/mortgage_ext.py — large deposits excluded until "
                   "sourced",
        "VAL-APR": "src/rule_families/mortgage_ext.py — the lower of contract and "
                   "appraised value governs; valuation age with its update window",
        "JMB-ELG": "src/rule_families/mortgage_ext.py — the jumbo overlay's tighter "
                   "leverage, credit and reserve bars, and its mandatory human review",
        # -- elsewhere --------------------------------------------------------
        "SEC-INJ": "src/guardrails/ + input_guardrails_node — injection detection and quarantine",
        "UWR-HRV": "src/review_triggers.py — the mandatory human-review routing table",
    },
    LendingProductDomain.EDUCATION_LOAN: {
        # -- the original three ------------------------------------------------
        "EDU-INC": "src/rules.py — debt-to-income capacity and residual income",
        "EDU-SCH": "src/rules.py — school eligibility and certification",
        # -- added in src/rule_families/education_ext.py -----------------------
        "EDU-UW": "src/rule_families/education_ext.py — per-product underwriting "
                  "criteria: loan band, credit floor, cosigner trigger, residency, "
                  "enrolment and the REFI default knockout",
        "EDU-RG": "src/rule_families/education_ext.py — the grade band table, with "
                  "the worse of FICO and DTI governing, and the E-band hard decline",
        "EDU-COS": "src/rule_families/education_ext.py — cosigner citizenship, age, "
                   "score, bankruptcy, sanctions, DTI ceiling and the Reg Z notice",
        "EDU-INTL": "src/rule_families/education_ext.py — visa class, I-94 "
                    "verification, the no-cosigner pathway and cosigner residency",
        # -- elsewhere ---------------------------------------------------------
        "EDU-GOV": "src/review_triggers.py — the permitted-outcome vocabulary",
    },
}

#: Families named by education golden citations that do not exist in the corpus
#: at all. Documented in docs/rag/DATA_QUALITY_FINDINGS.md: 9 of 59 education
#: golden citations name rules that were never written. They are excluded from
#: the coverage figure because "not implemented" and "does not exist" are
#: different problems and only one of them is ours.
NONEXISTENT_EDUCATION_FAMILIES = frozenset({"EDU-CERT", "EDU-REFI", "EDU-AGG", "EDU-FRAUD"})


def _family(rule_id: str) -> str:
    return rule_id.rsplit("-", 1)[0]


def _coverage_for(
    product: LendingProductDomain,
    cases: "list[AgentCase]",
    rules_for: "Any",
) -> dict[str, Any]:
    implemented = set(IMPLEMENTED_RULE_FAMILIES.get(product, {}))
    uncovered: list[str] = []
    missing: dict[str, int] = {}
    nonexistent = 0

    for case in cases:
        families = {_family(rule) for rule in rules_for(case)}
        real = {f for f in families if f not in NONEXISTENT_EDUCATION_FAMILIES}
        nonexistent += len(families) - len(real)
        gaps = real - implemented
        if gaps:
            uncovered.append(case.case_id)
            for family in gaps:
                missing[family] = missing.get(family, 0) + 1

    return {
        "cases": len(cases),
        "cases_needing_an_unimplemented_family": len(uncovered),
        "share_affected": round(len(uncovered) / len(cases), 4) if cases else None,
        "implemented_families": IMPLEMENTED_RULE_FAMILIES.get(product, {}),
        "unimplemented_families_by_case_count": dict(
            sorted(missing.items(), key=lambda kv: (-kv[1], kv[0]))
        ),
        "citations_naming_a_nonexistent_rule": nonexistent,
    }


def rule_coverage() -> dict[str, Any]:
    """How much of each golden set the implemented rules can actually decide.

    Read this before reading ``outcome_accuracy``. A case whose golden outcome
    turns on a rule the engine does not implement cannot be scored correct except
    by coincidence, so this is the ceiling the accuracy figure sits under — not an
    excuse for it, but the number that makes it interpretable.

    Retrieval is not the gap. The indexes cover both corpora in full, and rules in
    the unimplemented families are retrieved, ranked and cited exactly like the
    others. What is missing is code that evaluates them against a threshold.
    """
    expectations = _mortgage_expectations()

    mortgage = _coverage_for(
        LendingProductDomain.MORTGAGE,
        load_mortgage_cases(),
        lambda case: expectations.get(case.application_id, {}).get("rule_ids", []),
    )
    education = _coverage_for(
        LendingProductDomain.EDUCATION_LOAN,
        load_education_cases(),
        lambda case: [
            rule
            for citation in case.expected_citations
            for rule in re.findall(r"EDU-[A-Z]+-\d+", citation)
        ],
    )

    return {
        "MORTGAGE": mortgage,
        "EDUCATION_LOAN": education,
        "note": (
            "Rules in the unimplemented families are still retrieved, cited and shown "
            "to the reader — the retrieval subsystem covers both corpora in full. What "
            "is missing is code evaluating them against a threshold, so a case whose "
            "golden outcome turns on one cannot be scored correct except by "
            "coincidence. This is the ceiling on outcome_accuracy and the first thing "
            "to extend."
        ),
    }


__all__ = [
    "APPROVE",
    "IMPLEMENTED_RULE_FAMILIES",
    "NONEXISTENT_EDUCATION_FAMILIES",
    "rule_coverage",
    "APPROVE_WITH_CONDITIONS",
    "AgentCase",
    "DECLINE",
    "EDUCATION_QUESTION",
    "EXPRESSIBLE_FAMILIES",
    "REFER",
    "direction_of",
    "iter_cases",
    "load_cases",
    "load_education_cases",
    "load_mortgage_cases",
    "outcome_family",
]
