"""Shared evaluation loop.

One function runs a set of cases through a retriever and produces the metric
block; the eval command, the embedding benchmark, the reranker benchmark and the
ablation study all call it, so every number in every report is produced the same
way.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Callable, Sequence

from src.domain import LendingProductDomain
from src.rag.citations import CitationResolver
from src.rag.models import PolicyRetrievalRequest, PolicyRetrievalResult, RetrievalStatus
from src.rag.pipeline import PolicyRetriever

from .dataset import EvalCase
from .metrics import MetricAccumulator, percentile, score_case


@dataclass
class CaseOutcome:
    """Everything one case produced — kept for the failure analysis."""

    case: EvalCase
    result: PolicyRetrievalResult
    scores: dict[str, float | None]
    latency_ms: float
    retrieved_rules: list[str] = field(default_factory=list)
    retrieved_policies: list[str] = field(default_factory=list)
    retrieved_citations: list[str] = field(default_factory=list)
    unresolved_citations: list[str] = field(default_factory=list)
    contaminated: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "query_id": self.case.query_id,
            "product_domain": self.case.product_domain.value,
            "category": self.case.category,
            "source": self.case.source,
            "query": self.case.query,
            "as_of_date": self.case.as_of_date,
            "status": self.result.status.value,
            "expected_rule_ids": self.case.expected_rule_ids,
            "expected_policy_ids": self.case.expected_policy_ids,
            "expected_policy_versions": self.case.expected_policy_versions,
            "retrieved_rule_ids": self.retrieved_rules,
            "retrieved_policy_ids": self.retrieved_policies,
            "retrieved_citations": self.retrieved_citations,
            "unresolved_citations": self.unresolved_citations,
            "cross_product_contamination": self.contaminated,
            "latency_ms": round(self.latency_ms, 2),
            "scores": {k: v for k, v in self.scores.items() if v is not None},
        }


#: Identifier prefixes that betray a chunk from the other product.
_FOREIGN_PREFIX = {
    LendingProductDomain.MORTGAGE: "EDUCATION__",
    LendingProductDomain.EDUCATION_LOAN: "MORTGAGE__",
}


def run_case(
    retriever: PolicyRetriever,
    case: EvalCase,
    *,
    top_k: int | None = None,
    citation_resolver: CitationResolver | None = None,
) -> CaseOutcome:
    """Run one case and score it."""
    request = PolicyRetrievalRequest(
        product_domain=case.product_domain,
        query_text=case.query,
        application_id=case.application_id,
        as_of_date=date.fromisoformat(case.as_of_date) if case.as_of_date else None,
        product_family=case.context.get("product_family"),
        loan_purpose=case.context.get("loan_purpose"),
        occupancy_type=case.context.get("occupancy_type"),
        education_product_code=case.context.get("product_code"),
        top_k=top_k,
    )

    started = time.perf_counter()
    result = retriever.retrieve(request)
    latency_ms = (time.perf_counter() - started) * 1000

    retrieved_rules = [e.rule_id for e in result.evidence if e.rule_id]
    retrieved_policies = [e.policy_id for e in result.evidence if e.policy_id]
    retrieved_versions = [(e.policy_id, e.policy_version) for e in result.evidence]
    citations = [e.citation for e in result.evidence]

    resolver = citation_resolver or CitationResolver(retriever.config)
    unresolved = [c for c in citations if not resolver.citation_exists(c)]

    foreign = _FOREIGN_PREFIX[case.product_domain]
    contaminated = any(e.chunk_id.startswith(foreign) for e in result.evidence)

    scores = score_case(
        retrieved_rules=retrieved_rules,
        retrieved_policies=retrieved_policies,
        retrieved_versions=retrieved_versions,
        expected_rules=case.expected_rule_ids,
        expected_policies=case.expected_policy_ids,
        expected_versions=case.expected_policy_versions,
    )
    scores["citation_validity"] = (
        (len(citations) - len(unresolved)) / len(citations) if citations else None
    )
    scores["no_result"] = 1.0 if not result.evidence else 0.0
    scores["cross_product_contamination"] = 1.0 if contaminated else 0.0
    scores["routing_correct"] = (
        1.0 if result.product_domain is case.product_domain else 0.0
    )

    return CaseOutcome(
        case=case,
        result=result,
        scores=scores,
        latency_ms=latency_ms,
        retrieved_rules=retrieved_rules,
        retrieved_policies=retrieved_policies,
        retrieved_citations=citations,
        unresolved_citations=unresolved,
        contaminated=contaminated,
    )


def evaluate(
    retriever: PolicyRetriever,
    cases: Sequence[EvalCase],
    *,
    top_k: int | None = None,
    progress: Callable[[int, int, EvalCase], None] | None = None,
) -> tuple[dict[str, Any], list[CaseOutcome]]:
    """Run a case set and return ``(metrics, outcomes)``."""
    resolver = CitationResolver(retriever.config)
    accumulator = MetricAccumulator()
    outcomes: list[CaseOutcome] = []
    latencies: list[float] = []

    for index, case in enumerate(cases, start=1):
        outcome = run_case(retriever, case, top_k=top_k, citation_resolver=resolver)
        outcomes.append(outcome)
        accumulator.add_many(outcome.scores)
        latencies.append(outcome.latency_ms)
        if progress:
            progress(index, len(cases), case)

    metrics = accumulator.summary()
    metrics["case_count"] = len(cases)
    metrics["latency_p50_ms"] = round(percentile(latencies, 50), 2)
    metrics["latency_p95_ms"] = round(percentile(latencies, 95), 2)
    metrics["latency_mean_ms"] = round(sum(latencies) / len(latencies), 2) if latencies else 0.0
    metrics["status_counts"] = _status_counts(outcomes)
    return metrics, outcomes


def _status_counts(outcomes: Sequence[CaseOutcome]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for outcome in outcomes:
        counts[outcome.result.status.value] = counts.get(outcome.result.status.value, 0) + 1
    return dict(sorted(counts.items()))


def macro_average(per_domain: dict[str, dict[str, Any]], keys: Sequence[str]) -> dict[str, float]:
    """Unweighted mean across products.

    Macro, not micro: the mortgage corpus is four times the size of the education
    one, and a micro average would let mortgage performance stand in for the
    system's.
    """
    out: dict[str, float] = {}
    for key in keys:
        values = [
            float(m[key])
            for m in per_domain.values()
            if isinstance(m.get(key), (int, float))
        ]
        if values:
            out[f"macro_{key}"] = round(sum(values) / len(values), 4)
    return out


#: Headline metrics for the authored family, where Recall@k is well posed.
HEADLINE_KEYS = (
    "policy_recall@1",
    "policy_recall@3",
    "policy_recall@5",
    "policy_recall@10",
    "rule_recall@1",
    "rule_recall@3",
    "rule_recall@5",
    "rule_recall@10",
    "rule_precision@5",
    "policy_precision@5",
    "rule_mrr@10",
    "policy_mrr@10",
    "rule_ndcg@10",
    "policy_ndcg@10",
    "citation_validity",
    "no_result",
    "cross_product_contamination",
    "routing_correct",
    "version_accuracy",
    "wrong_version_rate",
)

#: Metrics for the golden-application family. Coverage and hit rate lead, because
#: raw Recall@k there is capped by the slot count rather than by ranking quality.
GOLDEN_KEYS = (
    "policy_coverage@5",
    "policy_coverage@10",
    "policy_hit@1",
    "policy_hit@5",
    "policy_recall@10",
    "rule_coverage@5",
    "rule_hit@5",
    "policy_mrr@10",
    "policy_precision@5",
    "citation_validity",
    "no_result",
    "cross_product_contamination",
    "routing_correct",
    "version_accuracy",
    "wrong_version_rate",
)


def failures(outcomes: Sequence[CaseOutcome], metric: str = "rule_recall@5") -> list[CaseOutcome]:
    """Cases that scored below 1.0 on a metric — the failure-analysis input."""
    out = []
    for outcome in outcomes:
        value = outcome.scores.get(metric)
        if value is not None and value < 1.0:
            out.append(outcome)
    return out
