"""Console helpers.

The source requirements contain characters the Windows default console codepage
(cp1252) cannot encode: U+2265 (>=), U+2014 (em dash), U+00B7 (middle dot),
U+2192 (arrow), U+00D7 (multiplication sign). Requirement text is quoted verbatim
in every report and CLI listing, so stdout/stderr must be UTF-8 before anything is
printed. Never transliterate the requirement text to make it printable.
"""

from __future__ import annotations

import sys


def use_utf8_console() -> None:
    """Force UTF-8 on stdout/stderr where the runtime allows it."""
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError):  # pragma: no cover - exotic stream
            pass
