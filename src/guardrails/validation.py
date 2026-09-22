"""The output guardrail: what must hold before a response is published.

The input guardrail — :mod:`src.guardrails.sanitize` — decides whether text is
safe to act on. This is its counterpart on the way out, and it lived in
``src/graph.py`` as a private helper until the two were put in the same place.
That was not only untidy: an output guardrail inside the graph module is one
nobody can call, test or audit without building a graph.

Three things are checked, and they fail differently on purpose:

* **citations resolve** — an unresolved citation is a *retrieval* problem.
  Substituting different prose would hide it, so it is reported and the
  response is not repaired.
* **the prose is faithful to its evidence** — a narrative asserting something
  its citations do not support is repairable, by falling back to the
  deterministic summary.
* **the prose does not contradict the decision** — "approved" in the rationale
  of a decline is the most dangerous output this system can produce, because
  it reads as authoritative and is wrong in the direction a borrower would act
  on. Also repairable by substitution.

Nothing here calls a model. The check that a narrative is faithful is made
where the narrative is made (:mod:`src.narrative`); this reads the verdict.
"""

from __future__ import annotations

import re
from typing import Any, Mapping, Sequence

#: Words whose presence contradicts the recommendation they appear under.
#:
#: Deliberately small and deliberately literal. The point is not to understand
#: the prose — it is to catch the one failure that matters, a rationale that
#: says the opposite of the decision it is attached to. A wider list would
#: start firing on "this file was declined for the reasons below" inside a
#: decline, which is the correct sentence.
CONTRADICTION_TERMS: dict[str, tuple[str, ...]] = {
    "APPROVE_RECOMMENDATION": (r"\bdeclin(e|ed|ing)\b", r"\bdenied\b", r"\brejected\b"),
    "DECLINE_RECOMMENDATION": (r"\bapproved\b", r"\bwe (?:can |will )?approve\b"),
    "REFER_RECOMMENDATION": (r"\bapproved\b", r"\bdeclined\b"),
}


def validate_response(
    state: Mapping[str, Any],
    recommendation: Mapping[str, Any],
    narrative: Mapping[str, Any],
    evidence: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Check citations, figures and decision consistency before publishing.

    Returns the verdict as a dictionary rather than raising: a response that
    fails validation still has to reach a human, with the reason attached.
    ``fallback_to_deterministic`` says whether substituting the deterministic
    summary would fix it — which is true for a prose problem and false for a
    retrieval one.
    """
    failures: list[str] = []

    unresolved = [
        e.get("citation") for e in evidence if e.get("citation_resolves") is False
    ]
    if unresolved:
        failures.append(
            f"{len(unresolved)} citation(s) do not resolve to a committed document"
        )

    if narrative.get("is_faithful") is False:
        unsupported = list(narrative.get("unsupported_citations") or [])
        figures = list(narrative.get("unsupported_figures") or [])
        failures.append(
            "the prose asserted something its evidence does not support "
            f"(citations: {unsupported or 'none'}; figures: {figures or 'none'})"
        )

    outcome = str(recommendation.get("outcome") or "")
    text = str(narrative.get("text") or "")
    contradiction = None
    if outcome and text and narrative.get("available"):
        for pattern in CONTRADICTION_TERMS.get(outcome, ()):
            if re.search(pattern, text, re.IGNORECASE):
                contradiction = pattern
                failures.append(
                    f"the prose reads as {pattern!r} while the recommendation is "
                    f"{outcome}"
                )
                break

    return {
        "passed": not failures,
        "failures": failures,
        "citations_resolve": not unresolved,
        "narrative_faithful": narrative.get("is_faithful"),
        "decision_consistent": contradiction is None,
        # Only a narrative problem is repairable by substitution. An unresolved
        # citation is a retrieval problem and swapping the prose would hide it.
        "fallback_to_deterministic": bool(
            narrative.get("is_faithful") is False or contradiction is not None
        ),
    }


def policy_allows_publication(verdict: Mapping[str, Any]) -> bool:
    """Whether a validated response may be published as it stands.

    Separated from :func:`validate_response` because the verdict is recorded
    whatever it says, and the decision about what to do with it belongs to the
    caller — the graph substitutes prose, the web API reports the failure, and
    the evaluation counts it.
    """
    return bool(verdict.get("passed"))
