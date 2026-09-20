"""
Import bootstrap for the validation suite.

Puts the suite root and its ``validators/`` directory on ``sys.path`` so the suite can
be executed from anywhere (pytest, the runner, or a CI step) without being installed
and without the CredPilot implementation needing to know it exists.
"""

from __future__ import annotations

import sys
from pathlib import Path

SUITE_ROOT = Path(__file__).resolve().parent
VALIDATORS = SUITE_ROOT / "validators"


def bootstrap() -> Path:
    for entry in (SUITE_ROOT, VALIDATORS):
        s = str(entry)
        if s not in sys.path:
            sys.path.insert(0, s)
    return SUITE_ROOT


bootstrap()
