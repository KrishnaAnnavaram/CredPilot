"""
Optional API-surface requirement validation.

The FastAPI streaming endpoint, which the source document marks optional / bonus.

Generated-by-hand wrapper: the test cases themselves live in
``automated_tests/registry/`` and are the single source of truth. This module only binds
the "api" slice of that registry to pytest.
"""

from __future__ import annotations

import bootstrap  # noqa: F401
from evidence_validator import Context
from requirement_validator import TestCase

from automated_tests._suite_runner import check_case, parametrize

SUITE = "api"


@parametrize(SUITE)
def test_requirement(case: TestCase, ctx: Context, record_property) -> None:
    """Validate one requirement test case from the registry."""
    check_case(case, ctx, record_property)
