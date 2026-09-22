"""Every evidence citation in the failure analysis must still resolve.

AC-08 asks for real failures each citing the evidence that showed it. The
artifacts those citations point into are regenerated, so a citation written once
and never re-checked drifts: the run that fixes a bug is also the run that
deletes the evidence of it. These tests are the tripwire —
``scripts/verify_evidence_citations.py`` holds the manifest, and this runs it.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from scripts.verify_evidence_citations import (
    CITATIONS,
    FAILURE_ANALYSIS,
    INVARIANTS,
    verify,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_every_cited_artifact_still_says_what_the_document_claims():
    results = verify()
    failures = [line for ok, line in results if not ok]
    assert not failures, "citations that no longer resolve:\n  " + "\n  ".join(failures)


def test_at_least_three_failures_carry_a_machine_evidence_citation():
    """AC-08's actual bar: >= 3 failures, EACH citing its evidence.

    Counted over distinct failures, not citations, so two citations on one
    failure cannot stand in for two failures.
    """
    cited = {c.failure for c in CITATIONS}
    assert len(cited) >= 3, f"only {len(cited)} failure(s) carry an evidence citation: {cited}"


def test_the_manifest_covers_only_failures_the_document_documents():
    text = FAILURE_ANALYSIS.read_text(encoding="utf-8")
    documented = set(re.findall(r"(?m)^##\s+(F-\d+)\s+—", text))
    for citation in CITATIONS:
        assert citation.failure in documented, (
            f"{citation.failure} is cited in the manifest but has no section in "
            f"{FAILURE_ANALYSIS.name}"
        )


@pytest.mark.parametrize("name,artifact,_check", INVARIANTS, ids=lambda v: str(v)[:24])
def test_the_artifacts_the_citations_read_are_committed(name, artifact, _check):
    assert (REPO_ROOT / artifact).exists(), f"{name} reads {artifact}, which is not present"


def test_the_failure_analysis_documents_at_least_three_failures():
    text = FAILURE_ANALYSIS.read_text(encoding="utf-8")
    sections = re.findall(r"(?m)^##\s+(F-\d+)\s+—", text)
    assert len(sections) >= 3, f"only {len(sections)} failure section(s)"
    # Each needs the three things the requirement names.
    for ident in sections:
        body = re.split(rf"(?m)^##\s+{ident}\s+—", text)[1].split("\n## ")[0]
        assert re.search(r"###\s+Observed", body), f"{ident} has no observed behaviour"
        assert re.search(r"###\s+(Root cause|Diagnosis)", body), f"{ident} has no root cause"
        assert re.search(r"###\s+Fix", body), f"{ident} has no fix"
        # Verification, under whichever heading the failure earned. F-13 is
        # the open one: its section says what is still missing and what it
        # costs, which is the honest heading for a fix that is partial.
        assert re.search(
            r"###\s+(Measured|Why it was caught|What is still missing)", body
        ), f"{ident} has no verification section"
