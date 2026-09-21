"""Console helpers.

Windows consoles still default to cp1252, which cannot encode the em dashes and
arrows the scripts print. Reconfiguring the streams to UTF-8 once at start-up is
cheaper than policing every string, and keeps the scripts' output identical
across platforms.
"""

from __future__ import annotations

import sys


def use_utf8_stdio() -> None:
    """Switch stdout/stderr to UTF-8, replacing anything the terminal cannot show."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (ValueError, OSError):  # pragma: no cover - exotic stream
                pass
