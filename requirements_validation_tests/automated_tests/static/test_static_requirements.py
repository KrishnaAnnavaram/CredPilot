"""
Static and structural requirement validation.

Architecture, configuration, data-validation, negative and boundary checks that inspect the committed implementation without running it.

Generated-by-hand wrapper: the test cases themselves live in
``automated_tests/registry/`` and are the single source of truth. This module only binds
the "static" slice of that registry to pytest.
"""

from __future__ import annotations

import bootstrap  # noqa: F401
from evidence_validator import Context
from requirement_validator import TestCase

from automated_tests._suite_runner import check_case, parametrize

SUITE = "static"


@parametrize(SUITE)
def test_requirement(case: TestCase, ctx: Context, record_property) -> None:
    """Validate one requirement test case from the registry."""
    check_case(case, ctx, record_property)
