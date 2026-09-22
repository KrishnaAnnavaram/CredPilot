#!/usr/bin/env python
"""Check that no signed team document has changed since it was signed.

    python scripts/verify_signatures.py

The confirmations in ``docs/team/`` are **typed**, not cryptographic — nobody's
private key was used. A typed name is easy to write and easy to alter, so the
signature on its own says nothing about whether the text above it still reads the
way it did when someone put their name to it.

That is what this closes. ``docs/team/SIGNATURES.md`` records the SHA-256 of each
document at the moment it was signed; this recomputes them and fails on any
difference. It does not prove *who* signed — only that **what** they signed has
not moved underneath them, which is the part a hash can honestly establish.

Exit codes
----------
``0``  every signed document matches its recorded hash
``1``  at least one document changed, or a hash is missing
``2``  the manifest itself is missing or unreadable
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = REPO_ROOT / "docs" / "team" / "SIGNATURES.md"

#: `| [`NAME.md`](NAME.md) | REQ-0nn | `<64 hex>` |`
ROW = re.compile(
    r"^\|\s*\[`(?P<name>[^`]+)`\]\([^)]+\)\s*\|\s*(?P<req>[^|]*?)\s*\|\s*`(?P<sha>[0-9a-f]{64})`\s*\|",
    re.M,
)


def main() -> int:
    if not MANIFEST.is_file():
        print(f"ERROR: no signature manifest at {MANIFEST}")
        return 2

    text = MANIFEST.read_text(encoding="utf-8")
    rows = list(ROW.finditer(text))
    if not rows:
        print(f"ERROR: {MANIFEST.relative_to(REPO_ROOT)} lists no signed documents.")
        print("       Either the manifest is malformed or nothing has been signed.")
        return 2

    print(f"Signature manifest : {MANIFEST.relative_to(REPO_ROOT)}")
    print(f"Signed documents   : {len(rows)}\n")

    problems: list[str] = []
    for m in rows:
        name, req, expected = m.group("name"), m.group("req").strip(), m.group("sha")
        path = MANIFEST.parent / name
        rel = path.relative_to(REPO_ROOT).as_posix()

        if not path.is_file():
            print(f"  MISSING   {rel}")
            problems.append(f"{rel}: signed document no longer exists")
            continue

        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual == expected:
            label = f" ({req})" if req and req != "-" else ""
            print(f"  OK        {rel}{label}")
        else:
            print(f"  CHANGED   {rel}")
            print(f"              signed as {expected}")
            print(f"              now       {actual}")
            problems.append(f"{rel}: content changed since it was signed")

    print()
    if problems:
        print("=" * 68)
        print(f"{len(problems)} signed document(s) no longer match the manifest:")
        for p in problems:
            print(f"  - {p}")
        print("")
        print("A signed statement that has been edited is no longer the statement")
        print("anyone put their name to. Either restore the text, or have the")
        print("signers confirm the new wording and regenerate the manifest.")
        print("=" * 68)
        return 1

    print("Every signed document matches the hash recorded when it was signed.")
    print("")
    print("Note: this establishes that the text is unchanged. It does not establish")
    print("who signed it - the confirmations are typed, not cryptographic. See")
    print("docs/team/SIGNATURES.md for what that does and does not mean.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
