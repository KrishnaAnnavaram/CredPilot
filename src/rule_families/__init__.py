"""Deterministic evaluators for the rule families the core engine did not cover.

:mod:`src.rules` holds the families this system started with — mortgage
affordability, the credit-score floor, reserves, funds to close, education
capacity. This package holds the rest, split by product, and is dispatched from
the same :func:`src.rules.evaluate` entry point.

The split is by size, not by kind. Every evaluator here obeys the same three
rules as the ones in :mod:`src.rules`:

* **the threshold comes out of the retrieved rule**, never out of this code. An
  evaluator whose rule was not retrieved reports INDETERMINATE and says which
  rule is missing. Absence of evidence is never permission (``GEN-ELG-005``);
* **the figure comes out of the packet or the calculators**, never out of a
  model;
* **the verdict is one of four words** — PASS, FAIL, INDETERMINATE,
  NOT_APPLICABLE — and a family that does not apply to this file says so
  explicitly rather than silently passing.

The last of those matters for the accuracy figure. An evaluator that returns
nothing when it does not apply is indistinguishable from one that was never
written, and the coverage report would count both the same way.
"""

from src.rule_families.education_ext import evaluate_education_families
from src.rule_families.mortgage_ext import evaluate_mortgage_families

__all__ = ["evaluate_education_families", "evaluate_mortgage_families"]
