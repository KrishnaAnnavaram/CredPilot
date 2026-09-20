"""
pytest configuration for the CredPilot requirements-validation suite.

Two things happen before any test runs:

1. ``bootstrap`` puts the suite and its ``validators/`` package on ``sys.path``.
2. The requirements baseline hash is verified. If the baseline has been altered since it
   was generated from the source document, the whole session is aborted with
   ``REQUIREMENTS_BASELINE_MODIFIED`` rather than quietly validating against edited
   requirements.
"""

from __future__ import annotations

import pytest

import bootstrap  # noqa: F401
from baseline_guard import BaselineIntegrityError, check_baseline, require_baseline
from console import use_utf8_console
from evidence_validator import Context


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--target",
        action="store",
        default=None,
        help="Path to the CredPilot implementation to validate. Overrides CREDPILOT_ROOT "
             "and config/validation_config.json.",
    )
    parser.addoption(
        "--allow-modified-baseline",
        action="store_true",
        default=False,
        help="Diagnostic only. Report the baseline mismatch but continue. Never use this to "
             "make a failing implementation pass.",
    )


def pytest_configure(config: pytest.Config) -> None:
    use_utf8_console()
    config.addinivalue_line("markers", "requirement(req_id): the requirement this test validates")
    config.addinivalue_line("markers", "verification(kind): the verification method used")


def pytest_sessionstart(session: pytest.Session) -> None:
    status = check_baseline()
    if status.ok:
        return
    if session.config.getoption("--allow-modified-baseline"):
        session.config.stash  # noqa: B018 - keep the object alive; warning is printed below
        print(f"\nWARNING: {status.code} - continuing because --allow-modified-baseline was given.")
        print(f"  expected sha256: {status.expected_sha256}")
        print(f"  actual   sha256: {status.actual_sha256}\n")
        return
    try:
        require_baseline()
    except BaselineIntegrityError as exc:
        raise pytest.UsageError(f"STOP VALIDATION - {exc}") from exc


@pytest.fixture(scope="session")
def ctx(pytestconfig: pytest.Config) -> Context:
    """The implementation under validation."""
    return Context(pytestconfig.getoption("--target"))
