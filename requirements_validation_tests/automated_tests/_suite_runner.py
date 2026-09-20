"""
Shared pytest plumbing for the per-suite test modules.

Each module under ``automated_tests/<suite>/`` is a thin wrapper that calls
:func:`parametrize` for its suite. The test body is identical everywhere: run the bound
check, attach the evidence, assert.

The failure message always carries the EXACT original requirement text, read from the
hashed baseline, so a failing run tells the reader precisely which requirement is unmet
and what evidence was looked for.
"""

from __future__ import annotations

from typing import Callable, List

import pytest

import bootstrap  # noqa: F401
from evidence_validator import Context
from requirement_validator import TestCase, run_test

from automated_tests.registry import by_suite


def cases_for(suite: str) -> List[TestCase]:
    return sorted(by_suite(suite), key=lambda c: c.test_id)


def _ids(cases: List[TestCase]) -> List[str]:
    return [c.test_id for c in cases]


def parametrize(suite: str) -> Callable:
    """Decorator that parametrizes a test function over one suite's cases."""
    cases = cases_for(suite)
    return pytest.mark.parametrize("case", cases, ids=_ids(cases))


def check_case(case: TestCase, ctx: Context, record_property) -> None:
    """Execute one registry case and assert it, recording the evidence either way."""
    result = run_test(case, ctx)

    record_property("requirement_id", case.req_id)
    record_property("exact_requirement", case.exact_requirement)
    record_property("test_type", case.test_type)
    record_property("automatable", case.automatable)
    record_property("weight", case.weight)
    record_property("evidence", result.evidence)

    if result.passed:
        return

    steps = "\n".join(f"    {i}. {s}" for i, s in enumerate(case.steps, 1))
    pytest.fail(
        f"\n{case.test_id} FAILED  (requirement {case.req_id}, weight {case.weight}, "
        f"{case.test_type})\n"
        f"\n  EXACT ORIGINAL REQUIREMENT:\n    {case.exact_requirement}\n"
        f"\n  Purpose:\n    {case.purpose}\n"
        f"\n  Execution steps:\n{steps}\n"
        f"\n  Expected result:\n    {case.expected_result}\n"
        f"\n  Fail condition:\n    {case.fail_condition}\n"
        f"\n  Evidence collected:\n    "
        + result.evidence.replace("\n", "\n    ")
        + "\n",
        pytrace=False,
    )
