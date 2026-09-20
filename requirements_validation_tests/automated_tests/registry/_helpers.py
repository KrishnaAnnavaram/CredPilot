"""
Test-case construction helpers.

``T()`` is the single way a test case enters the registry. It fills in the boilerplate
fields consistently so each case file can concentrate on the two things that matter:
which requirement it is bound to, and what evidence would prove that requirement.

The category of a test is inherited from its requirement's category in the hashed
baseline, so a test can never be filed under a category the baseline does not give it.
"""

from __future__ import annotations

from typing import Callable, Sequence

import bootstrap  # noqa: F401  (side effect: sys.path)
from evidence_validator import UNSPECIFIED, Context, Evidence
from requirement_loader import load_requirements
from requirement_validator import TestCase

DEFAULT_PRECONDITION = (
    "The requirements baseline hash verifies, and the CredPilot implementation root is "
    "resolvable (config/validation_config.json, CREDPILOT_ROOT, or --target)."
)

RUNTIME_PRECONDITION = (
    DEFAULT_PRECONDITION
    + " Runtime execution is enabled and the implementation documents a runnable command."
)

#: Which pytest module executes a test, derived from its verification type unless the
#: case states a suite explicitly. Keeps every automated_tests/ folder meaningful and
#: keeps slow runtime work out of the static suite.
SUITE_BY_TYPE = {
    "RUNTIME_TEST": "functional",
    "OUTPUT_VALIDATION_TEST": "functional",
    "API_TEST": "api",
    "WORKFLOW_TEST": "workflow",
    "HUMAN_REVIEW_TEST": "workflow",
    "INTEGRATION_TEST": "integration",
    "GOVERNANCE_TEST": "governance",
    "AUDITABILITY_TEST": "governance",
    "DOCUMENTATION_TEST": "governance",
}


def suite_for(test_type: str, explicit: str | None) -> str:
    """Resolve the executing suite for a test case."""
    return explicit or SUITE_BY_TYPE.get(test_type, "static")


def T(
    test_id: str,
    req_id: str,
    purpose: str,
    check: Callable[[Context], Evidence],
    *,
    test_type: str,
    suite: str | None = None,
    steps: Sequence[str] = (),
    expected: str = "",
    evidence: str = "",
    inputs: str = UNSPECIFIED,
    preconditions: str | None = None,
    pass_condition: str = "",
    fail_condition: str = "",
    weight: int = 1,
    automatable: bool = True,
) -> TestCase:
    req = load_requirements()[req_id]
    expected = expected or purpose
    resolved_suite = suite_for(test_type, suite)
    needs_runtime = test_type in {"RUNTIME_TEST", "OUTPUT_VALIDATION_TEST", "API_TEST"}
    return TestCase(
        test_id=test_id,
        req_id=req_id,
        purpose=purpose,
        preconditions=preconditions
        or (RUNTIME_PRECONDITION if needs_runtime else DEFAULT_PRECONDITION),
        inputs=inputs,
        steps=tuple(steps) or ("Execute the bound evidence check against the implementation root.",),
        expected_result=expected,
        evidence_required=evidence or "Concrete artifact evidence: resolved path, matched line with "
                                      "line number, record count, or captured process output.",
        pass_condition=pass_condition or f"Collected evidence satisfies: {expected}",
        fail_condition=fail_condition
        or f"Evidence is absent, incomplete, or contradicts: {expected}",
        weight=weight,
        test_type=test_type,
        automatable=automatable,
        category=req.category,
        suite=resolved_suite,
        check=check,
    )


def manual_T(
    test_id: str,
    req_id: str,
    purpose: str,
    what: str,
    *,
    test_type: str = "DOCUMENTATION_TEST",
    steps: Sequence[str] = (),
    expected: str = "",
    weight: int = 1,
) -> TestCase:
    """A statement that no artifact in the implementation can settle on its own.

    It still gets a test, it still reports PASS/FAIL, and with no recorded human
    evidence it reports FAIL. Silence is never a pass.
    """
    from evidence_validator import manual_attestation

    return T(
        test_id,
        req_id,
        purpose,
        manual_attestation(test_id, what),
        test_type=test_type,
        suite="governance",
        steps=tuple(steps)
        or (
            f"Read manual_evidence/manual_attestations.json for entry '{test_id}'.",
            "Require a non-empty evidence string, an attester and an attestation date.",
        ),
        expected=expected or purpose,
        evidence=f"A completed attestation record for {test_id} naming '{what}', its attester and date.",
        pass_condition=f"A complete, dated, attributed attestation of '{what}' is recorded.",
        fail_condition=f"No attestation, or an incomplete attestation, for '{what}'.",
        weight=weight,
        automatable=False,
        preconditions="A reviewer has had the opportunity to record out-of-band evidence.",
    )


def unspecified_T(
    test_id: str,
    req_id: str,
    purpose: str,
    what: str,
    *,
    test_type: str = "DOCUMENTATION_TEST",
    weight: int = 1,
) -> TestCase:
    """The source document supplies no value or artifact against which to test.

    Recorded as UNSPECIFIED_BY_REQUIREMENT rather than guessed. The test exists so the
    gap is visible in the matrix and the report, and it does not pass.
    """
    from evidence_validator import not_verifiable_from_artifact

    return T(
        test_id,
        req_id,
        purpose,
        not_verifiable_from_artifact(what),
        test_type=test_type,
        suite="governance",
        steps=(
            f"Re-read the exact source text of {req_id}.",
            f"Confirm the document specifies no verifiable value or artifact for '{what}'.",
            "Record UNSPECIFIED_BY_REQUIREMENT rather than inventing a threshold or path.",
        ),
        expected=f"UNSPECIFIED_BY_REQUIREMENT for '{what}'",
        evidence=f"The exact source text of {req_id}, showing it fixes no testable value for '{what}'.",
        pass_condition="Not reachable: the document supplies nothing to verify against.",
        fail_condition=f"Recorded as UNSPECIFIED_BY_REQUIREMENT because the document fixes no value for '{what}'.",
        weight=weight,
        automatable=False,
    )
