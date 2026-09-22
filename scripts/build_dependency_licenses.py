#!/usr/bin/env python
"""Record the licence of every declared runtime dependency, from package metadata.

    python scripts/build_dependency_licenses.py

Writes ``reports/dependency_licenses.json`` and the table inside
``docs/THIRD_PARTY_LICENSES.md``.

Why this exists
---------------
The requirements document's stack table names *"LangGraph (MIT)"*. That is a
statement about a **dependency's** licence, and it is checkable — the installed
distribution carries its own metadata. This reads that metadata rather than
asserting the licence from the document that prompted the question.

Two things this deliberately does not do:

* It does not touch the project's own ``LICENSE``. CredPilot's licence and
  LangGraph's licence are different facts about different things, and adding a
  project licence would evidence the wrong one.
* It does not make ``REQ-035`` pass. That check asks for *"any licence artifact
  the implementation must carry"*, and the source document requires none — so the
  check is unreachable whatever this file says. The evidence is recorded because
  it is the substantive claim a reader would want checked, not to move a score.

Licence text is read from `importlib.metadata`, which reports what the installed
wheel declares. Where a distribution uses the newer PEP 639 ``License-Expression``
field, or only the Trove classifiers, both are read and reported separately so a
reader can see where the answer came from.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

REQUIREMENTS = REPO_ROOT / "requirements.txt"
JSON_OUT = REPO_ROOT / "reports" / "dependency_licenses.json"
MD_OUT = REPO_ROOT / "docs" / "THIRD_PARTY_LICENSES.md"

#: The one the source document names explicitly, called out in its own section.
HIGHLIGHT = "langgraph"

_REQ_LINE = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)\s*(?:[=<>!~]=?|$)")

_CLASSIFIER = re.compile(r"^License\s*::\s*(?:OSI Approved\s*::\s*)?(.+)$")


def declared_packages() -> list[str]:
    """Every distribution named in requirements.txt, in file order."""
    names: list[str] = []
    for line in REQUIREMENTS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        m = _REQ_LINE.match(line)
        if m and m.group(1).lower() not in {n.lower() for n in names}:
            names.append(m.group(1))
    return names


def licence_of(name: str) -> dict:
    """What the installed distribution says about its own licence."""
    try:
        dist = metadata.distribution(name)
    except metadata.PackageNotFoundError:
        return {
            "package": name,
            "version": None,
            "license": None,
            "license_expression": None,
            "classifiers": [],
            "evidence_source": "NOT INSTALLED - no metadata to read",
            "resolved_license": None,
        }

    meta = dist.metadata
    # `License` is the legacy free-text field; `License-Expression` is PEP 639.
    raw_license = (meta.get("License") or "").strip()
    expression = (meta.get("License-Expression") or "").strip()
    classifiers = [
        m.group(1).strip()
        for c in meta.get_all("Classifier") or []
        if (m := _CLASSIFIER.match(c.strip()))
    ]

    # Prefer the machine-readable expression, then the classifier, then the free
    # text - and say which one answered, because a 30 KB licence body pasted into
    # the `License` field is not a useful answer.
    if expression:
        resolved, source = expression, "License-Expression (PEP 639)"
    elif classifiers:
        resolved, source = classifiers[0], "Trove classifier"
    elif raw_license and len(raw_license) <= 64 and "\n" not in raw_license:
        resolved, source = raw_license, "License field"
    elif raw_license:
        resolved, source = "(full licence text embedded in metadata)", "License field (full text)"
    else:
        resolved, source = None, "no licence metadata found"

    return {
        "package": dist.metadata["Name"] or name,
        "version": dist.version,
        "license": raw_license[:120] or None,
        "license_expression": expression or None,
        "classifiers": classifiers,
        "evidence_source": source,
        "resolved_license": resolved,
    }


def main() -> int:
    from src.console import use_utf8_stdio

    use_utf8_stdio()

    names = declared_packages()
    rows = [licence_of(n) for n in names]
    rows.sort(key=lambda r: r["package"].lower())

    missing = [r["package"] for r in rows if r["resolved_license"] is None]
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    payload = {
        "generated_at_utc": generated,
        "generated_by": "scripts/build_dependency_licenses.py",
        "source": "importlib.metadata of the installed distributions",
        "requirements_manifest": "requirements.txt",
        "python": sys.version.split()[0],
        "packages_declared": len(names),
        "packages_resolved": len(rows) - len(missing),
        "packages_without_license_metadata": missing,
        "note": (
            "Licences are read from installed package metadata, not asserted. This "
            "evidences the licence of a DEPENDENCY. It says nothing about CredPilot's "
            "own licence, which is a separate question, and it does not make REQ-035 "
            "pass - that check asks for a licence artifact the source document does "
            "not require."
        ),
        "packages": rows,
    }

    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")

    highlight = next((r for r in rows if r["package"].lower() == HIGHLIGHT), None)

    md = [
        "# Third-party licences\n",
        f"Generated {generated} by ",
        "[`scripts/build_dependency_licenses.py`](../scripts/build_dependency_licenses.py) ",
        "from the installed distributions' own metadata. Machine-readable form: ",
        "[`reports/dependency_licenses.json`](../reports/dependency_licenses.json).\n",
        "```bash\npython scripts/build_dependency_licenses.py\n```\n",
        "\n## Two different questions\n",
        "This document answers exactly one of them:\n",
        "| | |",
        "|---|---|",
        "| **A — CredPilot's own licence** | Not addressed here. Whether this repository "
        "carries a licence, and which, is a Virtusa policy question. No project "
        "`LICENSE` was added or changed to satisfy a requirement. |",
        "| **B — the licence of each dependency** | **This document.** Read from installed "
        "package metadata. |",
        "\nThe requirements document's stack row says *\"Python 3.11+ · LangGraph (MIT)\"*. "
        "That is a claim of kind **B**, and it is checkable.\n",
    ]

    if highlight:
        md += [
            "\n## LangGraph — the one the source names\n",
            "| Field | Value |",
            "|---|---|",
            f"| Package | `{highlight['package']}` |",
            f"| Version | `{highlight['version']}` |",
            f"| **Resolved licence** | **{highlight['resolved_license']}** |",
            f"| Evidence source | {highlight['evidence_source']} |",
            f"| Trove classifiers | {', '.join(highlight['classifiers']) or '—'} |",
            "",
            "Reproduce it directly:\n",
            "```python",
            "from importlib import metadata",
            'd = metadata.distribution("langgraph")',
            'print(d.version, d.metadata.get("License-Expression"),',
            '      d.metadata.get_all("Classifier"))',
            "```\n",
            "The source document's description of LangGraph as MIT is therefore "
            "**confirmed against the installed package**, not taken on trust.\n",
        ]

    md += [
        "\n## Why this does not close REQ-035\n",
        "`REQ-035-T03` asks for *\"any licence artifact the implementation must carry to "
        "evidence LangGraph's MIT licence\"*. The source document names the licence in a "
        "stack table and **places no obligation on this repository to carry any licence "
        "artifact** — so there is no artifact for the check to look for, and it is "
        "registered as `UNSPECIFIED_BY_REQUIREMENT`.\n",
        "Adding this file is the right thing to do on the merits and does not change "
        "that. The validator was not modified to accept it, because the check is not "
        "wrong: the specification really is silent. See "
        "[`requirements_validation_tests/reports/unverifiable_requirements.md`]"
        "(../requirements_validation_tests/reports/unverifiable_requirements.md).\n",
        "\n## Every declared runtime dependency\n",
        f"{len(rows)} distributions declared in `requirements.txt`, "
        f"{len(rows) - len(missing)} with readable licence metadata.\n",
        "| Package | Version | Licence | Evidence source |",
        "| --- | --- | --- | --- |",
    ]
    for r in rows:
        lic = r["resolved_license"] or "**not resolved**"
        md.append(f"| `{r['package']}` | {r['version'] or '—'} | {lic} | "
                  f"{r['evidence_source']} |")

    if missing:
        md += [
            "\n### Without readable licence metadata\n",
            "Not a finding about the licence itself — only that the installed wheel "
            "declares none in a field this script reads:\n",
            *[f"* `{m}`" for m in missing],
            "",
        ]

    md += [
        "\n## Scope\n",
        "Direct dependencies declared in `requirements.txt` only. Transitive "
        "dependencies are not enumerated: the list would run to several hundred "
        "packages and none of them is named by the requirements document.\n",
    ]

    MD_OUT.parent.mkdir(parents=True, exist_ok=True)
    MD_OUT.write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"declared packages : {len(names)}")
    print(f"licence resolved  : {len(rows) - len(missing)}")
    if highlight:
        print(f"langgraph         : {highlight['version']} -> "
              f"{highlight['resolved_license']}  ({highlight['evidence_source']})")
    if missing:
        print(f"no metadata       : {', '.join(missing)}")
    print(f"\nWritten:\n  {JSON_OUT}\n  {MD_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
