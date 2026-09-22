"""Guardrails-AI, wired into the live input and output paths.

The source document's Security row names ``Guardrails-AI / LLM Guard`` beside
Presidio and python-dotenv. This module is the Guardrails-AI half. It does not
replace anything: Presidio still finds the PII, :mod:`src.guardrails.sanitize`
still decides whether applicant text may be acted on, and
:mod:`src.guardrails.validation` still decides whether a response may be
published. Guardrails-AI is the declarative layer those controls are expressed
*through*, so a validator is a named, individually testable object rather than a
branch inside a longer function.

Where it sits
-------------
Input::

    applicant text
        -> Presidio / redaction          (src.guardrails.redaction)
        -> Guardrails-AI input guard     (here)
        -> injection detection, stripping, quarantine  (src.guardrails.sanitize)
        -> allow / quarantine / human review

Output::

    generated response
        -> Guardrails-AI output guard    (here)
        -> PII scan                      (src.guardrails.redaction)
        -> citation and numeric consistency  (src.guardrails.validation)
        -> publish, or fall back to the deterministic summary

Both guards are constructed once and reused. Building a ``Guard`` per call is
what makes a guardrail layer look slow enough to be worth removing.

Why the telemetry is switched off here
--------------------------------------
Guardrails-AI ships anonymous metrics to a vendor HTTPS endpoint by default, and
the switch that stops it is ``~/.guardrailsrc`` — a file on whichever machine
happens to run the code. For a system whose entire claim is that applicant data
stays local, "off on the developer's laptop" is not off. :func:`_silence_telemetry`
does it in committed code instead, and ``tests/test_guardrails_library.py``
asserts it stayed done.

The validators are local and deterministic. None of them calls a model, which
matters twice over: the guardrail cannot be talked out of its verdict by the text
it is inspecting, and it still works when the model quota is gone.
"""

from __future__ import annotations

import re
import threading
from dataclasses import dataclass, field
from typing import Any, Dict, Mapping

#: Set once, by :func:`_silence_telemetry`, under this lock.
_TELEMETRY_LOCK = threading.Lock()
_TELEMETRY_SILENCED = False

#: Built lazily and reused. ``Guard`` construction parses the validator registry.
_GUARD_LOCK = threading.Lock()
_INPUT_GUARD = None
_OUTPUT_GUARD = None


class GuardrailsUnavailable(RuntimeError):
    """Guardrails-AI is not importable, so its layer is skipped."""


def _silence_telemetry() -> None:
    """Stop Guardrails-AI exporting spans to its vendor endpoint.

    Three things, because one is not enough:

    * ``settings.disable_tracing`` turns off the guard-level spans;
    * the ``HubTelemetry`` singleton is claimed *before* any ``Guard`` exists, so
      the instance that gets created is one with metrics already off — it is a
      singleton, and whoever instantiates it first decides;
    * every ``Guard`` is then configured with ``allow_metrics_collection=False``,
      because ``Guard.__init__`` reloads ``~/.guardrailsrc`` and would otherwise
      re-enable what the first two just turned off.
    """
    global _TELEMETRY_SILENCED
    with _TELEMETRY_LOCK:
        if _TELEMETRY_SILENCED:
            return
        from guardrails.settings import settings
        from guardrails.utils.hub_telemetry_utils import HubTelemetry

        settings.disable_tracing = True
        HubTelemetry(enabled=False)._enabled = False
        _TELEMETRY_SILENCED = True


def available() -> bool:
    """Whether Guardrails-AI can be used in this process."""
    try:
        import guardrails  # noqa: F401
    except Exception:  # noqa: BLE001
        return False
    return True


# --------------------------------------------------------------------------------------
# Validators
# --------------------------------------------------------------------------------------


def _register_validators():
    """Define and register CredPilot's validators with Guardrails-AI.

    Done inside a function so importing this module does not require
    Guardrails-AI to be installed. Everything a validator needs it takes from the
    value it is given; none of them reaches for a model, a network call or a
    clock.
    """
    from guardrails.validators import (
        FailResult,
        PassResult,
        ValidationResult,
        Validator,
        register_validator,
    )

    from src.guardrails.redaction import find_sensitive, redact_text
    from src.guardrails.sanitize import detect_injection

    @register_validator(name="credpilot/no-injected-instruction", data_type="string")
    class NoInjectedInstruction(Validator):
        """Applicant text carrying an instruction is not safe to act on.

        The fix value is the redacted text with the imperative stripped, which is
        what :mod:`src.guardrails.sanitize` would produce anyway. Reported as a
        failure regardless, so the caller can route for human review rather than
        silently accepting a repaired string.
        """

        def _validate(self, value: Any, metadata: Dict) -> ValidationResult:
            findings = detect_injection(str(value or ""))
            if findings:
                return FailResult(
                    error_message=(
                        "input carries instruction-shaped text "
                        f"({', '.join(sorted(set(findings)))}); applicant text is "
                        "evidence, never instruction (POL-SEC-001 SEC-INJ-001)"
                    ),
                    fix_value=redact_text(str(value or "")),
                )
            return PassResult()

    @register_validator(name="credpilot/no-sensitive-value", data_type="string")
    class NoSensitiveValue(Validator):
        """No identifier, account number or other sensitive value passes.

        Uses the project's own Presidio-backed scanner rather than a second
        opinion about what counts as sensitive, so the guardrail and the audit
        trail cannot disagree about whether something was PII.
        """

        def _validate(self, value: Any, metadata: Dict) -> ValidationResult:
            text = str(value or "")
            found = find_sensitive(text)
            if found:
                kinds = sorted({str(kind) for kind, _matched in found})
                return FailResult(
                    error_message=f"text carries sensitive value(s): {', '.join(kinds)}",
                    fix_value=redact_text(text),
                )
            return PassResult()

    @register_validator(name="credpilot/bounded-length", data_type="string")
    class BoundedLength(Validator):
        """Report a query past the ceiling, and offer the truncation as the fix.

        It reports rather than truncates because every validator here runs under
        ``NOOP`` — the verdict is data the caller routes on. The truncation
        itself happens in :func:`src.guardrails.sanitize.sanitize_query`, against
        the same ceiling, so there is one place where the length is enforced and
        one place where it is reported.

        A long message is far more often a pasted document than an attack, which
        is why it is bounded rather than refused: refusing it loses a real
        question.
        """

        def __init__(self, max_chars: int = 2000, **kwargs: Any):
            super().__init__(**kwargs)
            self._max_chars = int(max_chars)

        def _validate(self, value: Any, metadata: Dict) -> ValidationResult:
            text = str(value or "")
            if len(text) > self._max_chars:
                return FailResult(
                    error_message=f"input is {len(text)} chars, over the {self._max_chars} ceiling",
                    fix_value=text[: self._max_chars],
                )
            return PassResult()

    @register_validator(name="credpilot/no-unresolved-citation", data_type="string")
    class NoUnresolvedCitation(Validator):
        """Every citation in a published response must name a real document.

        The resolution itself is done upstream, where the evidence is; this
        validator reads the verdict out of ``metadata`` and refuses to let an
        unresolved one through. Deliberately not repairable: substituting prose
        would hide a retrieval failure rather than fix it.
        """

        def _validate(self, value: Any, metadata: Dict) -> ValidationResult:
            unresolved = list((metadata or {}).get("unresolved_citations") or [])
            if unresolved:
                return FailResult(
                    error_message=(
                        f"{len(unresolved)} citation(s) do not resolve to a committed "
                        f"document: {', '.join(str(c) for c in unresolved[:5])}"
                    )
                )
            return PassResult()

    @register_validator(name="credpilot/decision-consistent", data_type="string")
    class DecisionConsistent(Validator):
        """The prose must not say the opposite of the decision it explains.

        "Approved" inside the rationale of a decline is the most dangerous string
        this system can emit: it reads as authoritative, and it is wrong in the
        direction the borrower would act on.
        """

        def _validate(self, value: Any, metadata: Dict) -> ValidationResult:
            from src.guardrails.validation import CONTRADICTION_TERMS

            outcome = str((metadata or {}).get("outcome") or "")
            text = str(value or "")
            if not outcome or not text:
                return PassResult()
            for pattern in CONTRADICTION_TERMS.get(outcome, ()):
                if re.search(pattern, text, re.IGNORECASE):
                    return FailResult(
                        error_message=(
                            f"the prose reads as {pattern!r} while the recommendation "
                            f"is {outcome}"
                        )
                    )
            return PassResult()

    return {
        "NoInjectedInstruction": NoInjectedInstruction,
        "NoSensitiveValue": NoSensitiveValue,
        "BoundedLength": BoundedLength,
        "NoUnresolvedCitation": NoUnresolvedCitation,
        "DecisionConsistent": DecisionConsistent,
    }


# --------------------------------------------------------------------------------------
# Guards
# --------------------------------------------------------------------------------------


def _build_guards():
    """Construct the input and output guards once."""
    global _INPUT_GUARD, _OUTPUT_GUARD
    with _GUARD_LOCK:
        if _INPUT_GUARD is not None and _OUTPUT_GUARD is not None:
            return _INPUT_GUARD, _OUTPUT_GUARD

        _silence_telemetry()
        from guardrails import Guard, OnFailAction

        v = _register_validators()

        # NOEXCEPTION: the verdict is data the caller routes on, not an error it
        # has to catch. A guardrail that raises is a guardrail someone wraps in a
        # bare `except` the first time it fires on a real applicant.
        inp = Guard(name="credpilot-input").use(
            v["BoundedLength"](max_chars=2000, on_fail=OnFailAction.NOOP),
            v["NoInjectedInstruction"](on_fail=OnFailAction.NOOP),
            v["NoSensitiveValue"](on_fail=OnFailAction.NOOP),
        )
        inp.configure(allow_metrics_collection=False)

        out = Guard(name="credpilot-output").use(
            v["NoUnresolvedCitation"](on_fail=OnFailAction.NOOP),
            v["DecisionConsistent"](on_fail=OnFailAction.NOOP),
            v["NoSensitiveValue"](on_fail=OnFailAction.NOOP),
        )
        out.configure(allow_metrics_collection=False)

        _INPUT_GUARD, _OUTPUT_GUARD = inp, out
        return inp, out


def reset_guards() -> None:
    """Drop the cached guards. For tests that re-register validators."""
    global _INPUT_GUARD, _OUTPUT_GUARD
    with _GUARD_LOCK:
        _INPUT_GUARD = None
        _OUTPUT_GUARD = None


@dataclass
class GuardVerdict:
    """What a Guardrails-AI guard concluded about one piece of text."""

    passed: bool
    failures: list[str] = field(default_factory=list)
    validators_run: list[str] = field(default_factory=list)
    repaired_text: str | None = None
    skipped: bool = False
    skip_reason: str | None = None
    #: Failure messages keyed by the validator class that produced them. The
    #: caller needs this to tell a finding the custom layer already made from one
    #: only Guardrails-AI found — without it, a response that contradicts its own
    #: decision is reported twice and a reviewer reads two problems where there
    #: is one.
    failures_by_validator: dict[str, str] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "failures": list(self.failures),
            "validators_run": list(self.validators_run),
            "failed_validators": sorted(self.failures_by_validator),
            "skipped": self.skipped,
            "skip_reason": self.skip_reason,
            "library": "guardrails-ai",
        }


def _verdict_from(outcome: Any, names: list[str]) -> GuardVerdict:
    """Read a Guardrails ``ValidationOutcome`` into our own shape."""
    failures: list[str] = []
    by_validator: dict[str, str] = {}
    for summary in (getattr(outcome, "validation_summaries", None) or []):
        name = str(getattr(summary, "validator_name", "") or "")
        message = getattr(summary, "failure_reason", None) or name or "validation failed"
        failures.append(str(message))
        if name:
            by_validator[name] = str(message)

    if not failures and getattr(outcome, "error", None):
        failures.append(str(outcome.error))

    passed = bool(getattr(outcome, "validation_passed", False)) and not failures
    repaired = getattr(outcome, "validated_output", None)
    return GuardVerdict(
        passed=passed,
        failures=failures,
        validators_run=names,
        repaired_text=repaired if isinstance(repaired, str) else None,
        failures_by_validator=by_validator,
    )


def _skipped(reason: str) -> GuardVerdict:
    return GuardVerdict(passed=True, skipped=True, skip_reason=reason)


def check_input(text: str, *, metadata: Mapping[str, Any] | None = None) -> GuardVerdict:
    """Run the Guardrails-AI input guard over untrusted text.

    Never raises and never blocks on its own. A guard that is unavailable, or
    that throws, returns ``skipped`` and the existing custom controls in
    :mod:`src.guardrails.sanitize` still run — they are the ones that decide.
    """
    if not available():
        return _skipped("guardrails-ai is not installed")
    try:
        guard, _ = _build_guards()
        outcome = guard.validate(str(text or ""), metadata=dict(metadata or {}))
        return _verdict_from(
            outcome,
            ["credpilot/bounded-length", "credpilot/no-injected-instruction",
             "credpilot/no-sensitive-value"],
        )
    except Exception as exc:  # noqa: BLE001 - the custom layer is the backstop
        return _skipped(f"{type(exc).__name__}: {exc}")


def check_output(text: str, *, metadata: Mapping[str, Any] | None = None) -> GuardVerdict:
    """Run the Guardrails-AI output guard over a response about to be published.

    ``metadata`` carries ``outcome`` (the recommendation) and
    ``unresolved_citations``, because those are facts about the response that the
    text alone does not contain.
    """
    if not available():
        return _skipped("guardrails-ai is not installed")
    try:
        _, guard = _build_guards()
        outcome = guard.validate(str(text or ""), metadata=dict(metadata or {}))
        return _verdict_from(
            outcome,
            ["credpilot/no-unresolved-citation", "credpilot/decision-consistent",
             "credpilot/no-sensitive-value"],
        )
    except Exception as exc:  # noqa: BLE001
        return _skipped(f"{type(exc).__name__}: {exc}")
