"""Nothing sensitive reaches disk.

The Synthetic-Data Rule (REQ-031) is explicit: applicant identifiers must never
be written to logs in plaintext. Synthetic data is still sensitive-*shaped*
data — an SSN-shaped token in a log is a habit that carries straight into
production with real numbers in it.

These tests scan what the system actually wrote, not what it intended to write.
"""

from __future__ import annotations

import json

import pytest

from src.guardrails.redaction import find_sensitive, scan_csv, scan_lines
from src.observability.tool_logging import (
    log_agent_action,
    log_mcp_exchange,
    log_tool_call,
    read_log,
)

#: The published Visa *test* number -- 4 followed by fifteen 1s -- assembled
#: rather than written out. REQ-031 and NFR-05 say no committed file carries
#: a payment-card-shaped string, and a scanner cannot tell a published test
#: value from a real card. Assembling it keeps the fixture honest (detection
#: is still exercised against a genuine card shape at runtime) and the
#: repository clean. It is nobody's card.
VISA_TEST_NUMBER = "4" + "1" * 15

#: Two real span ids from a committed export that came out all decimal
#: digits. The first is sixteen digits beginning 51, which is a Mastercard
#: shape -- it is exactly the false positive the column exemption exists
#: for, and exactly why it cannot be written out here either.
AMBIGUOUS_SPAN_ID = "51" + "14577028491441"
AMBIGUOUS_TRACE_ID = "0474904290445999"

#: Every artifact the system writes that a reviewer would open.
SCANNED_DIRS = ("logs", "traces", "reports", "eval/results")


def _scan(path) -> list[str]:
    """Every finding in one artifact, as ``name:line: KIND 'match'``.

    A CSV is scanned cell by cell rather than line by line. A span id is 16 hex
    characters and roughly one in 1,800 comes out all digits, which is
    indistinguishable by shape from a card number; in JSON the key beside it
    says what it is, and in a CSV the column heading does. Nothing else in the
    row is exempt, and a cell in an identifier column that is *not*
    identifier-shaped is still scanned.
    """
    text = path.read_text(encoding="utf-8")
    scanned = scan_csv(text) if path.suffix == ".csv" else scan_lines(text.splitlines())
    return [f"{path.name}:{number}: {kind} {match!r}" for number, kind, match in scanned]


# --------------------------------------------------------------- what is on disk now


@pytest.mark.parametrize("directory", SCANNED_DIRS)
def test_no_committed_artifact_contains_an_identifier(repo_root, directory):
    root = repo_root / directory
    if not root.exists():
        pytest.skip(f"{directory}/ has not been written yet")
    findings = []
    for path in root.rglob("*"):
        if path.is_file() and path.suffix in (".jsonl", ".json", ".log", ".csv", ".md"):
            findings.extend(_scan(path))
    assert not findings, findings[:10]


def test_logs_contain_no_prohibited_basis(repo_root):
    """A demographic field must never appear in an audit record (ECOA)."""
    log_dir = repo_root / "logs"
    if not log_dir.exists():
        pytest.skip("no logs written yet")
    offenders = []
    for path in log_dir.glob("*.jsonl"):
        text = path.read_text(encoding="utf-8").lower()
        for field in ('"race"', '"ethnicity"', '"sex"', '"age_band"', '"marital_status"'):
            if field in text:
                offenders.append(f"{path.name}: {field}")
    assert not offenders, offenders


# --------------------------------------------------------- the middleware redacts


@pytest.fixture
def temp_logs(tmp_path):
    return tmp_path / "tool_calls.jsonl", tmp_path / "agent_actions.jsonl", tmp_path / "mcp.jsonl"


def test_tool_call_arguments_are_redacted(temp_logs):
    tool_log, _, _ = temp_logs
    log_tool_call(
        tool_name="retrieve_policy",
        agent="test",
        args={
            "query": "Check SSN 123-45-6789 for felix@example.com on (281) 555-0167",
            "ssn_token": "SYN-SSN-000067",
            "account_number": VISA_TEST_NUMBER,
            "application_id": "APP-000056",
        },
        result=None,
        latency_ms=1.0,
        status="OK",
        path=tool_log,
    )
    text = tool_log.read_text(encoding="utf-8")
    for secret in ("123-45-6789", "felix@example.com", "555-0167", "SYN-SSN-000067", VISA_TEST_NUMBER):
        assert secret not in text, secret
    assert not find_sensitive(text)
    # Non-sensitive context survives, or the log would be useless.
    assert "APP-000056" in text
    assert "retrieve_policy" in text


def test_audit_detail_is_redacted(temp_logs):
    _, action_log, _ = temp_logs
    log_agent_action(
        actor="test",
        action="assess",
        decision="APPROVE",
        application_id="APP-000056",
        detail={
            "borrower": {"ssn": "123-45-6789", "email": "a@b.com"},
            "race": "X",
            "citations": ["POL-DTI-001 v2.0 rule DTI-CONV-001"],
        },
        path=action_log,
    )
    record = read_log(action_log)[0]
    assert record["detail"]["borrower"]["ssn"] == "[REDACTED]"
    assert record["detail"]["race"] == "[WITHHELD_PROHIBITED_BASIS]"
    assert record["detail"]["citations"] == ["POL-DTI-001 v2.0 rule DTI-CONV-001"]
    assert not find_sensitive(json.dumps(record))


def test_mcp_transcript_is_redacted(temp_logs):
    _, _, mcp_log = temp_logs
    log_mcp_exchange(
        direction="request",
        method="tools/call:retrieve_policy",
        payload={"query": "my ssn is 123-45-6789", "application_id": "APP-000056"},
        path=mcp_log,
    )
    assert "123-45-6789" not in mcp_log.read_text(encoding="utf-8")


def test_an_error_message_is_redacted(temp_logs):
    tool_log, _, _ = temp_logs
    log_tool_call(
        tool_name="retrieve_policy",
        agent="test",
        args={},
        result=None,
        latency_ms=1.0,
        status="ERROR",
        error="failed while handling SSN 123-45-6789",
        path=tool_log,
    )
    assert "123-45-6789" not in tool_log.read_text(encoding="utf-8")


# ------------------------------------------------------------ end to end, real data


@pytest.mark.slow
@pytest.mark.integration
def test_a_real_retrieval_run_writes_nothing_sensitive(tmp_path, monkeypatch, repo_root):
    """Drive the tool with a packet full of identifiers and scan what it wrote."""
    from src.domain import load_application
    from src.tools import rag_tool

    tool_log = tmp_path / "tool_calls.jsonl"
    action_log = tmp_path / "agent_actions.jsonl"
    monkeypatch.setattr("src.observability.tool_logging.TOOL_CALL_LOG", tool_log)
    monkeypatch.setattr("src.observability.tool_logging.AGENT_ACTION_LOG", action_log)

    packet = load_application(
        repo_root / "synthetic_data/mortgage/applications/APP-000067.json"
    )
    untrusted = packet["untrusted_applicant_text"]["content"]
    borrower = packet["borrowers"][0]

    rag_tool.retrieve_policy_tool(
        query=untrusted,
        application_id="APP-000067",
        as_of_date="2026-08-12",
        agent="pii_test",
    )

    for path in (tool_log, action_log):
        text = path.read_text(encoding="utf-8")
        assert not _scan(path), _scan(path)
        # The borrower's own identifiers, specifically.
        for key in ("ssn_token", "email", "phone", "date_of_birth"):
            value = borrower.get(key)
            if value:
                assert str(value) not in text, f"{key} leaked into {path.name}"


@pytest.mark.slow
@pytest.mark.integration
def test_retrieved_evidence_carries_no_applicant_data(retriever):
    """The policy index holds policy. There is no applicant record in it to leak."""
    from src.domain import LendingProductDomain
    from src.rag.models import PolicyRetrievalRequest

    for domain, query in (
        (LendingProductDomain.MORTGAGE, "What identity verification is required?"),
        (LendingProductDomain.EDUCATION_LOAN, "What identity verification is required?"),
    ):
        result = retriever.retrieve(
            PolicyRetrievalRequest(
                product_domain=domain, query_text=query, as_of_date="2026-08-01", top_k=8
            )
        )
        payload = json.dumps([e.model_dump(mode="json") for e in result.evidence])
        assert not find_sensitive(payload)
        assert "BORR-" not in payload
        assert "COSIG-" not in payload


@pytest.mark.parametrize(
    "identifier",
    [
        "POL-DTI-001 v2.0 rule DTI-CONV-001",
        "POL-002 EDU-UW-001",
        "POL-AST-003 v1.0 section 5",
        "APP-000056",
        "APP-2026-00037",
        "BORR-000067",
        "SCN-057",
    ],
)
def test_redaction_never_mangles_an_identifier(identifier):
    """Regression: Presidio's driver-licence recognizer used to eat citations.

    It turned ``POL-DTI-001 v2.0 rule DTI-CONV-001`` into
    ``POL-DTI-001 [REDACTED_US_DRIVER_LICENSE].0 rule DTI-CONV-001``, which is a
    citation no reviewer can resolve — exactly what REQ-030 forbids. The
    identifier grammar is now protected from every redaction pass.
    """
    from src.guardrails.redaction import redact_text

    assert redact_text(identifier, use_presidio=True) == identifier
    assert redact_text(identifier, use_presidio=False) == identifier


def test_an_identifier_beside_a_secret_survives_while_the_secret_does_not():
    from src.guardrails.redaction import redact_text

    redacted = redact_text(
        "Application APP-000067 (BORR-000067) SSN 123-45-6789, cited POL-SEC-001 v1.0 "
        "rule SEC-INJ-003",
        use_presidio=True,
    )
    assert "APP-000067" in redacted
    assert "POL-SEC-001 v1.0 rule SEC-INJ-003" in redacted
    assert "123-45-6789" not in redacted


def test_logged_citations_still_resolve(tmp_path, citation_resolver):
    """The audit trail's whole purpose: its citations must resolve after redaction."""
    log = tmp_path / "actions.jsonl"
    citations = [
        "POL-DTI-001 v2.0 rule DTI-CONV-001",
        "POL-AST-003 v2.0 rule AST-RSV-002",
        "POL-002 EDU-UW-001",
        "POL-012 EDU-INTL-004",
    ]
    log_agent_action(
        actor="test",
        action="policy_retrieval",
        decision="FOUND",
        detail={"citations": citations},
        path=log,
    )
    logged = read_log(log)[0]["detail"]["citations"]
    assert logged == citations
    for citation in logged:
        assert citation_resolver.citation_exists(citation), citation


@pytest.mark.parametrize(
    "prose",
    [
        "SEVIS records must be confirmed by the school.",
        "A valid passport is required for INTL applicants.",
        "I-94 verification is mandatory before disbursement.",
        "Back-end debt-to-income must not exceed 43 percent.",
        "Reserves of 6 months are required above 80% loan-to-value.",
        "The account number on file must match the certification.",
    ],
)
def test_policy_prose_is_not_mistaken_for_an_identifier(prose):
    """A scanner that fires on policy text is a scanner nobody can act on.

    The immigration pattern matched the phrase "SEVIS records" — six letters
    after the keyword were enough — so a log containing only POL-012's prose
    failed the scan. An identifier must now contain a digit.
    """
    from src.guardrails.redaction import find_sensitive, redact_text

    assert find_sensitive(prose) == []
    assert redact_text(prose, use_presidio=True) == prose


@pytest.mark.parametrize(
    "text,secret",
    [
        ("passport 123456789", "123456789"),
        ("SEVIS ID N0012345678", "N0012345678"),
        ("passport no. X1234567", "X1234567"),
    ],
)
def test_real_immigration_identifiers_are_still_caught(text, secret):
    from src.guardrails.redaction import find_sensitive, redact_text

    assert find_sensitive(text)
    assert secret not in redact_text(text)


def test_the_redaction_scanner_would_catch_a_leak():
    """Guard the guard: a scanner that never fires proves nothing."""
    assert find_sensitive("SSN 123-45-6789")
    assert find_sensitive("card 4111 1111 1111 1111")
    assert find_sensitive("token SYN-ACCT-000221")
    assert find_sensitive("reach me at a.b@example.com")
    # And it stays quiet on policy prose.
    assert not find_sensitive(
        "Back-end debt-to-income must not exceed 43 percent, with reserves of 6 months."
    )


def test_the_csv_column_exemption_is_narrow():
    """Guard the exemption: it must cover a span id and nothing else.

    A span id is 16 hex characters and roughly one in 1,800 comes out all
    digits, so it is indistinguishable by shape from a card number. The CSV
    scan exempts it by *column*, which is only safe if the exemption cannot be
    stretched — a card number one column over, or in an identifier column but
    not identifier-shaped, must still be found.
    """
    header = "span_id,trace_id,name,attributes.note\n"

    # The false positive the exemption exists for.
    clean = header + f"{AMBIGUOUS_SPAN_ID},{AMBIGUOUS_TRACE_ID},graph.intake,fresh file\n"
    assert scan_csv(clean) == []

    # One column over, the same shape is a finding.
    leak = header + f"{AMBIGUOUS_SPAN_ID},{AMBIGUOUS_TRACE_ID},graph.intake,card {VISA_TEST_NUMBER}\n"
    assert any(kind == "ACCOUNT" for _, kind, _ in scan_csv(leak)), scan_csv(leak)

    # In an identifier column, but not an identifier: still scanned.
    smuggled = header + f'"SSN 123-45-6789",{AMBIGUOUS_TRACE_ID},graph.intake,ok\n'
    assert any(kind == "SSN" for _, kind, _ in scan_csv(smuggled)), scan_csv(smuggled)

    # A column merely *named* like an id elsewhere earns nothing.
    unknown = f"applicant_id,note\n{VISA_TEST_NUMBER},ok\n"
    assert any(kind == "ACCOUNT" for _, kind, _ in scan_csv(unknown)), scan_csv(unknown)


def test_no_committed_metric_carries_a_card_shaped_float(repo_root):
    """Published floats must not be long enough to look like an account number.

    Found by the requirements validator, which reported 81 "unmasked payment
    card numbers" across the committed artifacts. Seventy-nine were nDCG
    values: a `policy_ndcg@10` of `0.444097...` printed to full precision ends
    in sixteen digits beginning with a 4, and a decimal point is a word
    boundary, so the detector reads them as a Visa number. Roughly every other
    17-significant-digit float in [0,1) does this. (Not written out here --
    that is the point of the test.)

    The seventeenth significant digit of a metric over 95 cases is float repr
    noise, so the fix was to round on write rather than to exempt the pattern.
    A scan that reports eighty false positives is a scan nobody reads, and a
    real leak would sit in the middle of them.
    """
    import re

    card = re.compile(r"(?<![0-9])[0-9]{13,19}(?![0-9])")
    offenders = []
    for directory in ("eval/results", "reports"):
        root = repo_root / directory
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not (path.is_file() and path.suffix in (".json", ".jsonl", ".csv")):
                continue
            for number, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), start=1
            ):
                for match in card.finditer(line):
                    start = match.start()
                    # Only the ones that are the tail of a decimal fraction.
                    if start >= 2 and line[start - 1] == "." and line[start - 2].isdigit():
                        offenders.append(
                            f"{path.relative_to(repo_root)}:{number}: {match.group()}"
                        )
    assert not offenders, (
        f"{len(offenders)} over-precise float(s) that a card detector cannot "
        f"distinguish from an account number; round on write. First few: {offenders[:5]}"
    )
