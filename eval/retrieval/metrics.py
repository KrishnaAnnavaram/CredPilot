"""Retrieval quality metrics.

All rank-based metrics are computed over the *final* evidence list the pipeline
returns, in the order it returns it, so what is measured is what an agent would
actually see.

Two levels of ground truth are scored separately, because they fail differently:

* **policy accuracy** — did the right policy document come back at all,
* **rule accuracy** — did the right rule inside it come back.

Retrieving ``POL-DTI-001`` when the answer is ``DTI-CONV-001`` is a much smaller
failure than retrieving ``POL-VAL-001``, and collapsing them into one number
hides which one happened. Mortgage additionally scores **version accuracy**,
since the wrong version of the right rule silently flips a decision.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence

DEFAULT_K_VALUES = (1, 3, 5, 10)


def recall_at_k(retrieved: Sequence[str], relevant: Iterable[str], k: int) -> float | None:
    """Fraction of relevant items appearing in the top ``k``.

    ``None`` when there is nothing relevant to find, so the case is excluded from
    the average rather than scored as a free 1.0 or a free 0.0.
    """
    relevant_set = {r for r in relevant if r}
    if not relevant_set:
        return None
    top = set(retrieved[:k])
    return len(relevant_set & top) / len(relevant_set)


def coverage_at_k(retrieved: Sequence[str], relevant: Iterable[str], k: int) -> float | None:
    """Recall normalized by what ``k`` slots can physically hold.

    Plain Recall@5 is bounded above by ``5 / |relevant|``. On the mortgage golden
    set, where a single whole-file question has ~16 governing policies, Recall@5
    cannot exceed 0.32 however perfect the ranking is — so reporting it as a
    quality number would be measuring the slot count, not the retriever.

    Coverage divides by ``min(|relevant|, k)`` instead, giving 1.0 when the top
    ``k`` are all correct. It is reported alongside, never instead of, the raw
    recall figures.
    """
    relevant_set = {r for r in relevant if r}
    if not relevant_set:
        return None
    achievable = min(len(relevant_set), k)
    if achievable == 0:  # pragma: no cover - guarded by the emptiness check above
        return None
    return len(relevant_set & set(retrieved[:k])) / achievable


def precision_at_k(retrieved: Sequence[str], relevant: Iterable[str], k: int) -> float | None:
    relevant_set = {r for r in relevant if r}
    if not relevant_set:
        return None
    top = retrieved[:k]
    if not top:
        return 0.0
    return sum(1 for item in top if item in relevant_set) / len(top)


def reciprocal_rank(retrieved: Sequence[str], relevant: Iterable[str], k: int = 10) -> float | None:
    """1/rank of the first relevant item within the top ``k``, else 0."""
    relevant_set = {r for r in relevant if r}
    if not relevant_set:
        return None
    for position, item in enumerate(retrieved[:k], start=1):
        if item in relevant_set:
            return 1.0 / position
    return 0.0



#: Decimal places for a per-case metric written to disk.
#:
#: Six, not the four used for published aggregates: per-case values are what
#: you read when debugging one case, and the extra resolution is worth
#: something there. What is not worth anything is the seventeenth significant
#: digit of a float — it is repr noise, and it is why the committed per-case
#: files were full of 16-digit runs that a payment-card detector cannot
#: distinguish from a Visa number. A `policy_ndcg@10` of `0.444097…` printed
#: to full precision ends in sixteen digits beginning with a 4, and a decimal
#: point is a word boundary, so the detector sees a Visa number. (The literal
#: is not written out here for the obvious reason.)
SERIALIZED_PLACES = 6


def round_for_serialization(value: "Any", places: int = SERIALIZED_PLACES) -> "Any":
    """Round floats anywhere inside a JSON-shaped structure, leaving the rest.

    Applied where a record is written, not where it is computed, so
    aggregation keeps full precision and no published figure moves.
    """
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, float):
        return round(value, places)
    if isinstance(value, dict):
        return {k: round_for_serialization(v, places) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [round_for_serialization(v, places) for v in value]
    return value

def ndcg_at_k(retrieved: Sequence[str], relevant: Iterable[str], k: int = 10) -> float | None:
    """Binary-gain nDCG at ``k``."""
    relevant_set = {r for r in relevant if r}
    if not relevant_set:
        return None
    dcg = sum(
        1.0 / math.log2(position + 1)
        for position, item in enumerate(retrieved[:k], start=1)
        if item in relevant_set
    )
    ideal = sum(
        1.0 / math.log2(position + 1)
        for position in range(1, min(len(relevant_set), k) + 1)
    )
    return dcg / ideal if ideal else None


def hit_at_k(retrieved: Sequence[str], relevant: Iterable[str], k: int) -> float | None:
    """1.0 when *any* relevant item is in the top ``k``."""
    relevant_set = {r for r in relevant if r}
    if not relevant_set:
        return None
    return 1.0 if relevant_set & set(retrieved[:k]) else 0.0


@dataclass
class MetricAccumulator:
    """Collects per-case scores and averages only over the cases that scored."""

    values: dict[str, list[float]] = field(default_factory=dict)

    def add(self, name: str, value: float | None) -> None:
        if value is None:
            return
        self.values.setdefault(name, []).append(float(value))

    def add_many(self, scores: Mapping[str, float | None]) -> None:
        for name, value in scores.items():
            self.add(name, value)

    def mean(self, name: str) -> float | None:
        vals = self.values.get(name)
        return sum(vals) / len(vals) if vals else None

    def count(self, name: str) -> int:
        return len(self.values.get(name, []))

    def summary(self, round_to: int = 4) -> dict[str, float]:
        return {
            name: round(sum(vals) / len(vals), round_to)
            for name, vals in sorted(self.values.items())
            if vals
        }


def percentile(values: Sequence[float], pct: float) -> float:
    """Nearest-rank percentile, so p50/p95 are real observed latencies."""
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = max(1, math.ceil(pct / 100.0 * len(ordered)))
    return float(ordered[min(rank, len(ordered)) - 1])


def score_case(
    *,
    retrieved_rules: Sequence[str],
    retrieved_policies: Sequence[str],
    retrieved_versions: Sequence[tuple[str, str | None]],
    expected_rules: Sequence[str],
    expected_policies: Sequence[str],
    expected_versions: Mapping[str, str] | None = None,
    k_values: Sequence[int] = DEFAULT_K_VALUES,
) -> dict[str, float | None]:
    """Score one evaluation case across every metric.

    ``retrieved_*`` sequences are in final rank order and may contain duplicates
    (several rules of the same policy); policy-level metrics deduplicate while
    preserving first-seen order, so a policy's rank is the rank at which it first
    appeared.
    """
    policies_ordered: list[str] = []
    for pid in retrieved_policies:
        if pid and pid not in policies_ordered:
            policies_ordered.append(pid)

    scores: dict[str, float | None] = {}
    for k in k_values:
        scores[f"rule_recall@{k}"] = recall_at_k(retrieved_rules, expected_rules, k)
        scores[f"policy_recall@{k}"] = recall_at_k(policies_ordered, expected_policies, k)
        scores[f"rule_hit@{k}"] = hit_at_k(retrieved_rules, expected_rules, k)
        scores[f"policy_hit@{k}"] = hit_at_k(policies_ordered, expected_policies, k)
        scores[f"rule_coverage@{k}"] = coverage_at_k(retrieved_rules, expected_rules, k)
        scores[f"policy_coverage@{k}"] = coverage_at_k(policies_ordered, expected_policies, k)

    scores["rule_precision@5"] = precision_at_k(retrieved_rules, expected_rules, 5)
    scores["policy_precision@5"] = precision_at_k(policies_ordered, expected_policies, 5)
    scores["rule_mrr@10"] = reciprocal_rank(retrieved_rules, expected_rules, 10)
    scores["policy_mrr@10"] = reciprocal_rank(policies_ordered, expected_policies, 10)
    scores["rule_ndcg@10"] = ndcg_at_k(retrieved_rules, expected_rules, 10)
    scores["policy_ndcg@10"] = ndcg_at_k(policies_ordered, expected_policies, 10)

    # Version accuracy: of the expected policies that came back, did they come
    # back at the version that governs on the as-of date?
    if expected_versions:
        retrieved_version_map: dict[str, set[str]] = {}
        for pid, ver in retrieved_versions:
            if pid:
                retrieved_version_map.setdefault(pid, set()).add(ver or "")
        checked = 0
        correct = 0
        wrong = 0
        for pid, expected_version in expected_versions.items():
            seen = retrieved_version_map.get(pid)
            if not seen:
                continue
            checked += 1
            if expected_version in seen:
                correct += 1
            if seen - {expected_version}:
                wrong += 1
        if checked:
            scores["version_accuracy"] = correct / checked
            scores["wrong_version_rate"] = wrong / checked

    return scores
