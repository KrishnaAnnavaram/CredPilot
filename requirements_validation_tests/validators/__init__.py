"""
CredPilot independent requirements-validation layer.

This package is an EXTERNAL QA layer. It must never be imported by, depended on by,
or merged into the CredPilot implementation.

Modules
-------
requirement_loader   Parses source_requirements/requirements_verbatim.md (the baseline).
baseline_guard       Verifies the baseline hash before any validation run.
evidence_validator   Primitive, evidence-producing checks against the implementation.
response_validator   Validation of runtime responses and produced output artifacts.
requirement_validator  Executes test cases and grades PASS / FAIL + fit score.
"""

__all__ = [
    "requirement_loader",
    "baseline_guard",
    "evidence_validator",
    "response_validator",
    "requirement_validator",
]
