"""Input/output guardrails wired into CredPilot's I/O path.

Three modules, one per job:

* :mod:`~src.guardrails.sanitize` — the **input** guardrail. Decides whether
  text is safe to act on, and quarantines it when it is not.
* :mod:`~src.guardrails.redaction` — what may be written down, anywhere.
* :mod:`~src.guardrails.validation` — the **output** guardrail. Decides whether
  a response may be published: citations resolve, prose is faithful to its
  evidence, prose does not contradict the decision.
* :mod:`~src.guardrails.policy_guard` — **Guardrails-AI**, the declarative layer
  the input and output checks above are expressed through. It delegates to them
  rather than replacing them, so the guardrail and the audit trail cannot
  disagree about whether something was PII.

The output guardrail lived inside ``src/graph.py`` until it was moved here. An
output guardrail that can only be reached by building a graph is one nobody can
test or audit on its own.
"""

from src.guardrails.policy_guard import (
    GuardVerdict,
    check_input,
    check_output,
)
from src.guardrails.redaction import (
    FORBIDDEN_DECISION_FIELDS,
    ID_COLUMNS,
    SENSITIVE_FIELD_NAMES,
    find_sensitive,
    redact_structure,
    redact_text,
    redact_value,
    scan_csv,
    scan_lines,
)
from src.guardrails.sanitize import (
    SanitizationResult,
    detect_injection,
    quarantine,
    sanitize_query,
)
from src.guardrails.validation import (
    CONTRADICTION_TERMS,
    policy_allows_publication,
    validate_response,
)

__all__ = [
    "CONTRADICTION_TERMS",
    "GuardVerdict",
    "FORBIDDEN_DECISION_FIELDS",
    "ID_COLUMNS",
    "SENSITIVE_FIELD_NAMES",
    "SanitizationResult",
    "check_input",
    "check_output",
    "detect_injection",
    "find_sensitive",
    "policy_allows_publication",
    "quarantine",
    "redact_structure",
    "redact_text",
    "redact_value",
    "sanitize_query",
    "scan_csv",
    "scan_lines",
    "validate_response",
]
