"""The output guardrail: what must hold before a response is published.

The input guardrail — :mod:`src.guardrails.sanitize` — decides whether text is
safe to act on. This is its counterpart on the way out, and it lived in
``src/graph.py`` as a private helper until the two were put in the same place.
That was not only untidy: an output guardrail inside the graph module is one
nobody can call, test or audit without building a graph.

Three things are checked here, and they fail differently on purpose:

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

A fourth comes from :mod:`src.guardrails.policy_guard`, which runs the
Guardrails-AI output guard over the same text: **no sensitive value reaches the
published response.** There is no counterpart to it above, so a PII leak on the
way out arrives only through that layer.

Two of the Guardrails-AI validators re-check what this module already checks,
and that redundancy is the point of having a second layer — but only the
findings this module did *not* make are appended to ``failures``. Reporting both
copies would show a reviewer two problems where there is one. What the second
layer concluded either way is kept under ``guardrails`` in the verdict, so the
two can be compared.

Nothing here calls a model, and neither does any validator in the guard. The
check that a narrative is faithful is made where the narrative is made
(:mod:`src.narrative`); this reads the verdict.
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


#: Guardrails-AI validators whose finding this module already makes for itself.
#: Kept as names rather than by matching message text, which would break the
#: first time either wording changed.
_ALREADY_CHECKED_ABOVE = frozenset({"NoUnresolvedCitation", "DecisionConsistent"})


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

    # The Guardrails-AI output guard, over the same response and the same facts.
    # It re-checks citation resolution and decision consistency declaratively and
    # adds a PII scan of the published text. A failure it alone finds still fails
    # the response: the whole point of the second layer is that it catches what
    # the first did not.
    from src.guardrails.policy_guard import check_output

    guard_verdict = check_output(
        text,
        metadata={
            "outcome": outcome,
            "unresolved_citations": [c for c in unresolved if c],
        },
    )
    # Only what the checks above did not already find. `NoUnresolvedCitation` and
    # `DecisionConsistent` deliberately re-check what this function checks — that
    # redundancy is the point of a second layer — but reporting both copies would
    # show a reviewer two problems where there is one. `NoSensitiveValue` has no
    # counterpart here, so a PII leak in the published text arrives only through
    # Guardrails-AI and is always appended.
    if not guard_verdict.skipped:
        for validator, message in sorted(guard_verdict.failures_by_validator.items()):
            if validator in _ALREADY_CHECKED_ABOVE:
                continue
            failures.append(f"guardrails-ai: {message}")

    return {
        "passed": not failures,
        "failures": failures,
        "citations_resolve": not unresolved,
        "narrative_faithful": narrative.get("is_faithful"),
        "decision_consistent": contradiction is None,
        "guardrails": guard_verdict.as_dict(),
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
