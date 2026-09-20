"""
Test-case model and grading.

Grading rules, fixed by the task specification and deliberately strict:

* A test PASSES only when its check returns ``ok=True`` with concrete evidence.
* A requirement PASSES only when **every** test bound to it passes. Partial
  implementation stays FAIL even though it earns a partial fit score.
* Fit score is the weighted percentage of that requirement's tests that passed.
* No evidence is never a pass. There is no "probably", no benefit of the doubt.

The requirement wording printed in every record is read from the hashed baseline at
run time (see :mod:`requirement_loader`) and is never stored or edited here.
"""

from __future__ import annotations

import time
import traceback
from dataclasses import dataclass, field
from typing import Callable, Iterable, Sequence

from evidence_validator import Context, Evidence
from requirement_loader import Requirement, load_requirements

PASS = "PASS"
FAIL = "FAIL"

VERIFICATION_TYPES = {
    "RUNTIME_TEST", "API_TEST", "INTEGRATION_TEST", "WORKFLOW_TEST", "STATIC_TEST",
    "CONFIGURATION_TEST", "DOCUMENTATION_TEST", "ARCHITECTURE_TEST", "SECURITY_TEST",
    "GOVERNANCE_TEST", "OBSERVABILITY_TEST", "AUDITABILITY_TEST", "HUMAN_REVIEW_TEST",
    "DATA_VALIDATION_TEST", "OUTPUT_VALIDATION_TEST", "NEGATIVE_TEST", "BOUNDARY_TEST",
}

#: Which pytest module executes a test. Keeps runtime work out of the static suite.
SUITES = {"static", "functional", "workflow", "integration", "governance", "api"}


@dataclass(frozen=True)
class TestCase:
    """One requirement-validation test case.

    ``exact_requirement`` is NOT stored on the test: it is resolved from the hashed
    baseline via :meth:`requirement_text`, so it can never drift from the source.
    """

    # Not a pytest test class despite the name - it is the test-case record type.
    __test__ = False

    test_id: str
    req_id: str
    purpose: str
    preconditions: str
    inputs: str
    steps: tuple[str, ...]
    expected_result: str
    evidence_required: str
    pass_condition: str
    fail_condition: str
    weight: int
    test_type: str
    automatable: bool
    category: str
    suite: str
    check: Callable[[Context], Evidence] = field(repr=False)

    def __post_init__(self) -> None:
        if self.test_type not in VERIFICATION_TYPES:
            raise ValueError(f"{self.test_id}: unknown test type {self.test_type!r}")
        if self.suite not in SUITES:
            raise ValueError(f"{self.test_id}: unknown suite {self.suite!r}")
        if self.weight <= 0:
            raise ValueError(f"{self.test_id}: weight must be positive, got {self.weight}")

    @property
    def requirement(self) -> Requirement:
        return load_requirements()[self.req_id]

    @property
    def exact_requirement(self) -> str:
        """The EXACT original requirement text. Read-only, from the hashed baseline."""
        return self.requirement.text


@dataclass
class TestResult:
    test_id: str
    req_id: str
    status: str
    evidence: str
    details: dict
    duration_ms: int
    weight: int
    test_type: str
    automatable: bool
    suite: str
    category: str
    error: str | None = None

    @property
    def passed(self) -> bool:
        return self.status == PASS


@dataclass
class RequirementResult:
    req_id: str
    status: str
    fit_score: int
    req_class: str
    category: str
    source_location: str
    exact_requirement: str
    test_ids: list[str]
    evidence: list[str]
    reason: str
    weight_total: int
    weight_passed: int

    @property
    def passed(self) -> bool:
        return self.status == PASS


def run_test(case: TestCase, ctx: Context) -> TestResult:
    """Execute one test case. A check that raises is a FAIL, never an error-swallow."""
    started = time.perf_counter()
    try:
        ev = case.check(ctx)
        err = None
    except Exception as exc:  # noqa: BLE001 - a crashing check is a failed check
        ev = Evidence(False, f"check raised {type(exc).__name__}: {exc}", {})
        err = traceback.format_exc(limit=6)
    elapsed = int((time.perf_counter() - started) * 1000)
    return TestResult(
        test_id=case.test_id,
        req_id=case.req_id,
        status=PASS if ev.ok else FAIL,
        evidence=ev.summary,
        details=ev.details,
        duration_ms=elapsed,
        weight=case.weight,
        test_type=case.test_type,
        automatable=case.automatable,
        suite=case.suite,
        category=case.category,
        error=err,
    )


def grade_requirement(req: Requirement, results: Sequence[TestResult]) -> RequirementResult:
    """Grade one requirement from its test results.

    PASS requires complete satisfaction of every mandatory part of the requirement,
    i.e. every test bound to it must pass.
    """
    if not results:
        # Cannot happen once the coverage audit is green, but never silently pass.
        return RequirementResult(
            req_id=req.req_id, status=FAIL, fit_score=0, req_class=req.req_class,
            category=req.category, source_location=req.source_location,
            exact_requirement=req.text, test_ids=[], evidence=[],
            reason="No test case is bound to this requirement - coverage gap, graded FAIL.",
            weight_total=0, weight_passed=0,
        )

    total = sum(r.weight for r in results)
    gained = sum(r.weight for r in results if r.passed)
    failed = [r for r in results if not r.passed]
    fit = int(round(100 * gained / total)) if total else 0
    status = PASS if not failed else FAIL

    if status == PASS:
        reason = f"All {len(results)} bound test(s) passed with committed evidence."
    else:
        names = ", ".join(r.test_id for r in failed[:6])
        more = f" (+{len(failed) - 6} more)" if len(failed) > 6 else ""
        reason = (
            f"{len(failed)} of {len(results)} bound test(s) produced no satisfying evidence: "
            f"{names}{more}."
        )
    return RequirementResult(
        req_id=req.req_id, status=status, fit_score=fit, req_class=req.req_class,
        category=req.category, source_location=req.source_location,
        exact_requirement=req.text, test_ids=[r.test_id for r in results],
        evidence=[f"[{r.status}] {r.test_id}: {r.evidence}" for r in results],
        reason=reason, weight_total=total, weight_passed=gained,
    )


@dataclass
class SuiteSummary:
    total_requirements: int
    tests_executed: int
    requirements_passed: int
    requirements_failed: int
    requirement_coverage_pct: float
    overall_fit_pct: int
    final_status: str
    failed_requirement_ids: list[str]
    mandatory_total: int
    mandatory_passed: int
    mandatory_failed: int
    optional_total: int
    optional_passed: int
    engagement_total: int
    engagement_passed: int
    automated_tests: int
    manual_tests: int


def summarise(
    req_results: Iterable[RequirementResult], test_results: Sequence[TestResult]
) -> SuiteSummary:
    """Aggregate to the project-level score.

    ``final_status`` is gated on IMPLEMENTATION-class requirements: those are the ones
    the source document places on the CredPilot deliverable. OPTIONAL and ENGAGEMENT
    requirements are still executed, scored and reported - they simply do not fail a
    build for something the source text itself calls optional, or for something that
    describes the engagement rather than the software.
    """
    rs = list(req_results)
    total = len(rs)
    passed = sum(1 for r in rs if r.passed)
    covered = sum(1 for r in rs if r.test_ids)

    mandatory = [r for r in rs if r.req_class == "IMPLEMENTATION"]
    optional = [r for r in rs if r.req_class == "OPTIONAL"]
    engagement = [r for r in rs if r.req_class == "ENGAGEMENT"]

    weight_total = sum(r.weight_total for r in rs)
    weight_passed = sum(r.weight_passed for r in rs)
    overall_fit = int(round(100 * weight_passed / weight_total)) if weight_total else 0

    mandatory_failed = [r for r in mandatory if not r.passed]
    return SuiteSummary(
        total_requirements=total,
        tests_executed=len(test_results),
        requirements_passed=passed,
        requirements_failed=total - passed,
        requirement_coverage_pct=round(100 * covered / total, 2) if total else 0.0,
        overall_fit_pct=overall_fit,
        final_status=PASS if not mandatory_failed else FAIL,
        failed_requirement_ids=[r.req_id for r in rs if not r.passed],
        mandatory_total=len(mandatory),
        mandatory_passed=sum(1 for r in mandatory if r.passed),
        mandatory_failed=len(mandatory_failed),
        optional_total=len(optional),
        optional_passed=sum(1 for r in optional if r.passed),
        engagement_total=len(engagement),
        engagement_passed=sum(1 for r in engagement if r.passed),
        automated_tests=sum(1 for t in test_results if t.automatable),
        manual_tests=sum(1 for t in test_results if not t.automatable),
    )
