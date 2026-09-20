"""
The requirement-validation test registry.

``TEST_CASES`` is the single authoritative list of test cases. Everything else in this
suite is derived from it: the pytest modules, the traceability matrix, the test-spec
documents and the report.

Invariants enforced at import time, so the suite cannot drift:

* Every test ID is unique and matches ``REQ-nnn-Tnn``.
* Every test binds to a requirement that exists in the hashed baseline.
* Every test's ``REQ-nnn`` prefix matches the requirement it binds to.
* Every requirement in the baseline has at least one test (100% coverage, by construction).
"""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Dict, List

import bootstrap  # noqa: F401
from requirement_loader import load_requirements
from requirement_validator import TestCase

from .cases_acceptance import CASES as _ACCEPTANCE
from .cases_artifacts import CASES as _ARTIFACTS
from .cases_core import CASES as _CORE
from .cases_evidence import CASES as _EVIDENCE

TEST_CASES: List[TestCase] = [*_CORE, *_ACCEPTANCE, *_ARTIFACTS, *_EVIDENCE]

_TEST_ID = re.compile(r"^(REQ-\d{3})-T\d{2}$")


class RegistryError(RuntimeError):
    """The registry violates one of its own invariants."""


def _validate() -> None:
    requirements = load_requirements()
    seen: set[str] = set()
    problems: list[str] = []

    for case in TEST_CASES:
        m = _TEST_ID.match(case.test_id)
        if not m:
            problems.append(f"{case.test_id}: malformed test ID (expected REQ-nnn-Tnn)")
            continue
        if case.test_id in seen:
            problems.append(f"{case.test_id}: duplicate test ID")
        seen.add(case.test_id)
        if m.group(1) != case.req_id:
            problems.append(
                f"{case.test_id}: ID prefix {m.group(1)} does not match its requirement {case.req_id}"
            )
        if case.req_id not in requirements:
            problems.append(f"{case.test_id}: bound to {case.req_id}, which is not in the baseline")

    covered = {c.req_id for c in TEST_CASES}
    for req_id in requirements:
        if req_id not in covered:
            problems.append(f"{req_id}: no test case is bound to this requirement")

    if problems:
        raise RegistryError(
            "Test registry invariants violated:\n  " + "\n  ".join(problems)
        )


_validate()


def by_requirement() -> Dict[str, List[TestCase]]:
    out: Dict[str, List[TestCase]] = defaultdict(list)
    for case in TEST_CASES:
        out[case.req_id].append(case)
    return dict(out)


def by_suite(suite: str) -> List[TestCase]:
    return [c for c in TEST_CASES if c.suite == suite]


def by_category(category: str) -> List[TestCase]:
    return [c for c in TEST_CASES if c.category == category]


def categories() -> List[str]:
    return sorted({c.category for c in TEST_CASES})


def suites() -> List[str]:
    return sorted({c.suite for c in TEST_CASES})


def get(test_id: str) -> TestCase:
    for case in TEST_CASES:
        if case.test_id == test_id:
            return case
    raise KeyError(test_id)


__all__ = [
    "TEST_CASES",
    "RegistryError",
    "by_requirement",
    "by_suite",
    "by_category",
    "categories",
    "suites",
    "get",
]
