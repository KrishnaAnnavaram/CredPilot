"""The assembled policy corpus and its registry."""

from __future__ import annotations

from .policies import Policy, build_registry
from .policy_defs_a import PART_A_POLICIES
from .policy_defs_b import PART_B_POLICIES
from .policy_defs_c import PART_C_POLICIES

ALL_POLICIES: tuple[Policy, ...] = PART_A_POLICIES + PART_B_POLICIES + PART_C_POLICIES

REGISTRY = build_registry(ALL_POLICIES)

POLICY_IDS = tuple(sorted(REGISTRY))
