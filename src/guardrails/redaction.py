"""PII redaction for anything CredPilot writes down.

Synthetic data is still sensitive-*shaped* data, and the Synthetic-Data Rule is
explicit that applicant identifiers must never be written to logs in plaintext.
Every log line, trace attribute and evaluation artifact passes through
:func:`redact_text` before it leaves the process.

Deterministic regex redaction runs first and always. Microsoft Presidio, when
installed, runs afterwards as a second pass that catches entities the patterns
miss (names, locations, free-form account references). Presidio is optional at
runtime: its absence weakens recall, it does not open a hole, because the
pattern layer alone already covers the identifier shapes the corpora contain.
"""

from __future__ import annotations

import functools
import re
from typing import Any, Iterable, Mapping

#: Ordered, non-overlapping redaction patterns. Each maps to the placeholder that
#: replaces it, so a redacted string still says *what kind* of value was removed.
_PATTERNS: tuple[tuple[str, re.Pattern[str], str], ...] = (
    # SSN / ITIN, masked or not: 123-45-6789, XXX-XX-0001, ***-**-0067
    (
        "SSN",
        re.compile(r"(?<![\w-])(?:\d{3}|[X*x]{3})[- ](?:\d{2}|[X*x]{2})[- ]\d{4}(?![\w-])"),
        "[REDACTED_SSN]",
    ),
    # Bank / credit account numbers of 12-19 digits, optionally grouped
    (
        "ACCOUNT",
        re.compile(r"(?<![\w.])(?:\d[ -]?){12,19}(?![\w.])"),
        "[REDACTED_ACCOUNT]",
    ),
    # A labelled account value. The label must be followed by an actual
    # *identifier* — digits, or a masked value. Matching any word after
    # "account" would redact the phrase "account number" wherever a policy
    # document discusses one, which is prose, not data.
    (
        "ACCOUNT",
        re.compile(
            r"(?<![\w-])(?:acct|account|card|routing)\s*(?:no\.?|number|#)?\s*[:=#]?\s*"
            r"(?=[\d*x]{4,})[\d*x][\d*x -]{3,}",
            re.IGNORECASE,
        ),
        "[REDACTED_ACCOUNT]",
    ),
    # A masked tail on its own: ``******0217``
    (
        "ACCOUNT",
        re.compile(r"(?<![\w-])[*x]{4,}\d{2,}(?![\w-])", re.IGNORECASE),
        "[REDACTED_ACCOUNT]",
    ),
    # The corpora's surrogate credential tokens: SYN-ACCT-000221, SYN-CRDT-000068,
    # SYN-SSN-000067 — synthetic, but identifier-shaped, and they stand in for a
    # credential wherever they appear.
    (
        "TOKEN",
        re.compile(r"(?<![\w-])SYN-[A-Z]{3,6}-\d{4,}(?![\w-])", re.IGNORECASE),
        "[REDACTED_TOKEN]",
    ),
    # Anything else spelled as a token: ...-TOKEN-1234, SSN_TOKEN
    (
        "TOKEN",
        re.compile(r"(?<![\w-])[A-Z]{2,}[-_]?TOKEN[-_]?[A-Za-z0-9]{2,}(?![\w-])"),
        "[REDACTED_TOKEN]",
    ),
    ("EMAIL", re.compile(r"(?<![\w.])[\w.+-]+@[\w-]+\.[\w.]{2,}(?![\w.])"), "[REDACTED_EMAIL]"),
    (
        "PHONE",
        re.compile(r"(?<![\w-])(?:\+?1[ .-]?)?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?![\w-])"),
        "[REDACTED_PHONE]",
    ),
    (
        "DOB",
        re.compile(r"(?<![\w-])(?:dob|date of birth)\s*[:=]?\s*\d{4}-\d{2}-\d{2}", re.IGNORECASE),
        "[REDACTED_DOB]",
    ),
    (
        # An immigration identifier must contain a digit. Without that, the
        # lookahead below, this matched the policy phrase "SEVIS records" —
        # redacting prose from POL-012 and failing the log scan on text that
        # contains no identifier at all.
        "PASSPORT",
        re.compile(
            r"(?<![\w-])(?:passport|i-?94|sevis)\s*(?:no\.?|number|#|id)?\s*[:=]?\s*"
            r"(?=[A-Z0-9-]*[0-9])[A-Z0-9][A-Z0-9-]{5,}",
            re.IGNORECASE,
        ),
        "[REDACTED_IMMIGRATION_ID]",
    ),
)

#: Field names whose *values* are always redacted, whatever they look like.
SENSITIVE_FIELD_NAMES = frozenset(
    {
        "ssn",
        "ssn_token",
        "ssn_masked",
        "ssn_itin_masked",
        "itin",
        "taxpayer_id",
        "tax_id",
        "account_token",
        "account_number",
        "credit_file_token",
        "card_number",
        "routing_number",
        "dob",
        "date_of_birth",
        "email",
        "phone",
        "passport_number",
        "i94_number",
        "sevis_id",
        "api_key",
        "password",
        "secret",
        "token",
    }
)

#: Demographic fields that must never influence a credit decision, and must not
#: be carried into prompts, evidence or logs (ECOA / fair-lending).
FORBIDDEN_DECISION_FIELDS = frozenset(
    {"race", "ethnicity", "sex", "gender", "age_band", "marital_status", "national_origin"}
)


@functools.lru_cache(maxsize=1)
def _presidio_analyzer():
    """Load Presidio lazily; return ``None`` when it is not installed."""
    try:
        from presidio_analyzer import AnalyzerEngine

        return AnalyzerEngine()
    except Exception:  # noqa: BLE001 - optional dependency, optional NLP model
        return None


#: Presidio entities worth running as a second pass.
#:
#: ``US_DRIVER_LICENSE`` and ``US_PASSPORT`` are deliberately excluded. Both match
#: generic alphanumeric runs, and on this corpus they destroy the identifiers the
#: audit trail exists to carry: ``POL-DTI-001 v2.0 rule DTI-CONV-001`` came back
#: as ``POL-DTI-001 [REDACTED_US_DRIVER_LICENSE].0 rule DTI-CONV-001``, and
#: ``APP-000056`` as ``APP-[REDACTED_US_DRIVER_LICENSE]``. A citation a reviewer
#: cannot resolve is worse than useless (REQ-030). The deterministic patterns
#: above already cover the passport and I-94 references the corpora contain.
_PRESIDIO_ENTITIES = (
    "US_SSN",
    "US_BANK_NUMBER",
    "CREDIT_CARD",
    "US_ITIN",
    "IBAN_CODE",
)

#: CredPilot's own identifier grammar. These are never redacted: they name a
#: policy, a rule, an application or a document, and every one of them has to
#: survive into the log for the audit trail to reconcile with the code.
_PROTECTED_IDENTIFIERS = re.compile(
    r"\bPOL-[A-Z]+-\d{3}\b"          # mortgage policy id
    r"|\bPOL-\d{3}\b"                 # education policy id
    r"|\bAPP-\d{6}\b"                 # mortgage application id
    r"|\bAPP-\d{4}-\d{5}\b"           # education application id
    r"|\bEDU-[A-Z]+-\d+\b"            # education rule id
    r"|\b[A-Z]{2,6}-[A-Z]{2,6}-\d{3}\b"  # mortgage rule id
    r"|\bv\d+\.\d+\b"                 # version marker
    r"|\bSCN-\d{3}\b"                 # scenario id
    r"|\bBORR-\d+\b|\bCOSIG-\d+\b|\bSCH-\d+\b"  # record ids (not credentials)
    # Trace, span and event ids. Machine-generated correlation keys with no
    # applicant in them — and the thing a failure analysis cites (REQ-080), so
    # they must survive intact.
    #
    # Each alternative requires at least one a-f character. A bare 16-digit run
    # is a card number far more often than it is a span id, and an earlier
    # version of this pattern matched `4111111111111111` and stopped it being
    # redacted. A span id that happens to be all digits loses its protection and
    # gets redacted; that is the right way round for this trade.
    r"|\b(?=[0-9a-f]{8}-)(?=[0-9a-f-]*[a-f])[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b"
    r"|\b(?=[0-9a-f]{32}\b)(?=[0-9a-f]*[a-f])[0-9a-f]{32}\b"
    r"|\b(?=[0-9a-f]{16}\b)(?=[0-9a-f]*[a-f])[0-9a-f]{16}\b",
    re.IGNORECASE,
)


def _protected_spans(text: str) -> list[tuple[int, int]]:
    return [(m.start(), m.end()) for m in _PROTECTED_IDENTIFIERS.finditer(text)]


def _overlaps(start: int, end: int, spans: list[tuple[int, int]]) -> bool:
    return any(start < span_end and end > span_start for span_start, span_end in spans)


def redact_text(text: str, *, use_presidio: bool = False) -> str:
    """Redact identifier-shaped substrings from free text.

    ``use_presidio`` is off by default because the analyzer costs tens of
    milliseconds per call and the pattern layer already covers the corpora's
    identifier shapes. Batch artifacts (logs flushed to disk, evaluation output)
    turn it on.
    """
    if not text:
        return text
    out = str(text)
    protected = _protected_spans(out)
    for _, pattern, placeholder in _PATTERNS:
        out = _sub_outside_protected(pattern, placeholder, out)

    if use_presidio:
        analyzer = _presidio_analyzer()
        if analyzer is not None:
            try:
                protected = _protected_spans(out)
                results = analyzer.analyze(
                    text=out, entities=list(_PRESIDIO_ENTITIES), language="en"
                )
                for res in sorted(results, key=lambda r: r.start, reverse=True):
                    if _overlaps(res.start, res.end, protected):
                        continue
                    out = out[: res.start] + f"[REDACTED_{res.entity_type}]" + out[res.end :]
            except Exception:  # noqa: BLE001 - never fail a call because of redaction
                pass
    return out


def _sub_outside_protected(pattern: re.Pattern[str], placeholder: str, text: str) -> str:
    """Apply a redaction pattern, skipping matches that hit a protected identifier."""
    protected = _protected_spans(text)
    if not protected:
        return pattern.sub(placeholder, text)
    out: list[str] = []
    cursor = 0
    for match in pattern.finditer(text):
        if _overlaps(match.start(), match.end(), protected):
            continue
        out.append(text[cursor : match.start()])
        out.append(placeholder)
        cursor = match.end()
    out.append(text[cursor:])
    return "".join(out)


def redact_value(key: str, value: Any, *, use_presidio: bool = False) -> Any:
    """Redact one key/value pair, honouring the sensitive-field name list."""
    normalized = str(key).split(".")[-1].lower()
    if normalized in SENSITIVE_FIELD_NAMES:
        return "[REDACTED]"
    if normalized in FORBIDDEN_DECISION_FIELDS:
        return "[WITHHELD_PROHIBITED_BASIS]"
    return redact_structure(value, use_presidio=use_presidio)


def redact_structure(value: Any, *, use_presidio: bool = False, _depth: int = 0) -> Any:
    """Recursively redact a JSON-shaped structure."""
    if _depth > 12:  # pragma: no cover - defensive
        return "[TRUNCATED]"
    if isinstance(value, str):
        return redact_text(value, use_presidio=use_presidio)
    if isinstance(value, Mapping):
        return {
            k: (
                "[REDACTED]"
                if str(k).lower() in SENSITIVE_FIELD_NAMES
                else "[WITHHELD_PROHIBITED_BASIS]"
                if str(k).lower() in FORBIDDEN_DECISION_FIELDS
                else redact_structure(v, use_presidio=use_presidio, _depth=_depth + 1)
            )
            for k, v in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [redact_structure(v, use_presidio=use_presidio, _depth=_depth + 1) for v in value]
    return value


def find_sensitive(text: str) -> list[tuple[str, str]]:
    """Return ``(kind, matched_text)`` for every sensitive pattern found.

    Used by the log-scanning tests, which assert that nothing matching these
    patterns ever reaches ``logs/`` or ``traces/``. Protected identifiers —
    policy ids, rule ids, application ids, trace and span ids — are skipped, so
    the scanner does not report a UUID's digit run as an account number.
    """
    found: list[tuple[str, str]] = []
    protected = _protected_spans(text or "")
    for kind, pattern, _ in _PATTERNS:
        for match in pattern.finditer(text or ""):
            if _overlaps(match.start(), match.end(), protected):
                continue
            found.append((kind, match.group(0)))
    return found


def scan_lines(lines: Iterable[str]) -> list[tuple[int, str, str]]:
    """Scan an iterable of lines, returning ``(line_number, kind, match)``."""
    out: list[tuple[int, str, str]] = []
    for n, line in enumerate(lines, start=1):
        for kind, match in find_sensitive(line):
            out.append((n, kind, match))
    return out
