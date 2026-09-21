"""Google Gemini — the only model provider CredPilot uses.

REQ-036: *"LLM Provider | Google Gemini (API) — the only approved provider; not
Claude"*. Every model call in the system goes through this module, so there is
one place to look to see what is called and with what.

Where the model is **not** used, and deliberately:

* retrieval, ranking and filtering — deterministic, so the evaluation is
  reproducible (REQ-033);
* every underwriting figure — ``POL-DTI-001`` DTI-CALC-002 forbids a model
  producing one;
* every threshold and verdict — those come from retrieved policy and the rule
  engine.

The model explains what the deterministic pipeline decided. It never decides.
"""

from __future__ import annotations

import os
import threading
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]

#: Both spellings are accepted. The committed `.env` has used each at different
#: times and a rename should not silently disable the model.
_KEY_VARIABLES = ("GOOGLE_API_KEY", "GEMINI_API_KEY")

#: `gemini-2.0-flash` and `gemini-2.5-flash` now return 404 *"no longer
#: available"*. Pinning a dated model name means it rots; `-latest` tracks the
#: current flash model, and the manifest records which one actually answered.
DEFAULT_MODEL = os.environ.get("CREDPILOT_GEMINI_MODEL", "gemini-flash-latest")

#: Tried in order when the configured model is unavailable.
FALLBACK_MODELS = ("gemini-flash-latest", "gemini-3.5-flash", "gemini-pro-latest")

_ENV_LOADED = False
_LOCK = threading.Lock()


def load_environment() -> None:
    """Load ``.env`` once, and normalize the key variable."""
    global _ENV_LOADED
    with _LOCK:
        if _ENV_LOADED:
            return
        try:
            from dotenv import load_dotenv

            load_dotenv(REPO_ROOT / ".env")
        except Exception:  # noqa: BLE001 - python-dotenv is optional at runtime
            pass
        key = api_key()
        if key:
            # The SDK reads GOOGLE_API_KEY; accept either spelling in .env.
            os.environ.setdefault("GOOGLE_API_KEY", key)
        _ENV_LOADED = True


def api_key() -> str | None:
    for variable in _KEY_VARIABLES:
        value = os.environ.get(variable)
        if value and value.strip():
            return value.strip()
    return None


@dataclass(frozen=True)
class LLMStatus:
    """Whether a model can actually be called, and which one answered."""

    available: bool
    model: str | None
    reason: str

    def as_dict(self) -> dict[str, Any]:
        return {"available": self.available, "model": self.model, "reason": self.reason}


class LLMUnavailableError(RuntimeError):
    """Raised when a caller requires the model and it cannot be reached."""


@lru_cache(maxsize=1)
def probe(timeout_seconds: int = 60) -> LLMStatus:
    """Check once whether Gemini answers, and with which model.

    Cached for the process. Callers that must degrade gracefully check
    ``probe().available``; callers that cannot proceed use :func:`require`.
    """
    load_environment()
    key = api_key()
    if not key:
        return LLMStatus(False, None, f"no key in {' or '.join(_KEY_VARIABLES)}")

    try:
        from google import genai
    except ImportError as exc:  # pragma: no cover - declared in requirements.txt
        return LLMStatus(False, None, f"google-genai not installed: {exc}")

    client = genai.Client(api_key=key)
    candidates = [DEFAULT_MODEL, *[m for m in FALLBACK_MODELS if m != DEFAULT_MODEL]]
    last_error = "no candidate model answered"
    for model in candidates:
        try:
            client.models.generate_content(model=model, contents="Reply with exactly: OK")
            return LLMStatus(True, model, "reachable")
        except Exception as exc:  # noqa: BLE001 - report, do not raise
            last_error = f"{model}: {type(exc).__name__}: {str(exc)[:160]}"
    return LLMStatus(False, None, last_error)


def require() -> str:
    """Return a working model name, or raise with a usable explanation."""
    status = probe()
    if not status.available:
        raise LLMUnavailableError(
            f"Gemini is required for this step but is not reachable ({status.reason}). "
            f"Set GOOGLE_API_KEY in .env to a key from https://aistudio.google.com/apikey. "
            f"Retrieval, the indexes, the tests and the retrieval evaluation do not "
            f"need it and still run."
        )
    return status.model  # type: ignore[return-value]


#: Gemini flash reasons before answering and bills the reasoning as output, where
#: it never appears in the text. How much it spends is **allocated dynamically by
#: how hard it judges the task**, which makes the figure prompt-dependent rather
#: than a property of the model:
#:
#: * a two-sentence probe ("write two sentences about DTI") drew 388 of 419
#:   output tokens as reasoning, and ``thinking_budget=0`` only moved it to 332 —
#:   that parameter is accepted and then effectively ignored;
#: * ``thinking_level`` does move it: on a short prompt, 714 with no setting
#:   against 468 at ``"low"``;
#: * on the **actual narrative prompt** — long, fully specified, with the decision
#:   already made and every figure supplied — it measured **zero**, with output
#:   tokens matching the visible text.
#:
#: The last of those is the one that describes this system, and it makes sense:
#: there is nothing left to work out. "low" is set because it helps where the
#: model does decide to think, and ``reasoning_tokens`` is reported as its own
#: line so the figure is visible rather than inferred either way.
DEFAULT_THINKING_LEVEL = os.environ.get("CREDPILOT_THINKING_LEVEL", "low")


def chat_model(
    model: str | None = None,
    *,
    temperature: float = 0.0,
    thinking_level: str | None = DEFAULT_THINKING_LEVEL,
    **kwargs: Any,
):
    """A LangChain chat model bound to Gemini.

    Temperature defaults to 0: a narrative that changes between runs cannot be
    reconciled with the trace that produced it.
    """
    load_environment()
    from langchain_google_genai import ChatGoogleGenerativeAI

    if thinking_level is not None:
        kwargs.setdefault("thinking_level", thinking_level)

    return ChatGoogleGenerativeAI(
        model=model or require(), temperature=temperature, **kwargs
    )


def message_text(message: Any) -> str:
    """Flatten a LangChain message's content to plain text.

    ``content`` is a list of typed blocks on current Gemini responses, not a
    string. Treating it as a string raises ``AttributeError`` at the worst
    possible moment, so every caller goes through here.
    """
    content = getattr(message, "content", message)
    if isinstance(content, str):
        return content
    if isinstance(content, Sequence):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("text"):
                parts.append(str(block["text"]))
            elif getattr(block, "text", None):
                parts.append(str(block.text))
        return "".join(parts)
    return str(content)


def usage_of(message: Any) -> dict[str, int]:
    """Token usage from a response, for the cost report. Empty when absent.

    ``reasoning_tokens`` is reported separately because it is billed as output but
    never appears in the answer, and because how much of it there is depends on
    the prompt: a short under-specified one drew 388 of 419 output tokens, while
    the narrative prompt draws none. Folded into the output figure, either case
    would be unreadable — the first as unexplained spend, the second as spend that
    looks avoided when it was simply never incurred.
    """
    usage = getattr(message, "usage_metadata", None) or {}
    details = usage.get("output_token_details") or {}
    return {
        "input_tokens": int(usage.get("input_tokens", 0) or 0),
        "output_tokens": int(usage.get("output_tokens", 0) or 0),
        "total_tokens": int(usage.get("total_tokens", 0) or 0),
        "reasoning_tokens": int(details.get("reasoning", 0) or 0),
        "cached_input_tokens": int(
            (usage.get("input_token_details") or {}).get("cache_read", 0) or 0
        ),
    }


#: Published per-million-token pricing for the Gemini flash tier, used for the
#: cost estimate in reports/golden_signals.json. An estimate is labelled as one:
#: it is not a billing record, and the rate is recorded alongside the figure so a
#: reader can recompute it when pricing changes.
PRICE_PER_MILLION_INPUT_USD = float(os.environ.get("CREDPILOT_PRICE_IN", "0.30"))
PRICE_PER_MILLION_OUTPUT_USD = float(os.environ.get("CREDPILOT_PRICE_OUT", "2.50"))


def estimate_cost_usd(input_tokens: int, output_tokens: int) -> float:
    return round(
        input_tokens / 1_000_000 * PRICE_PER_MILLION_INPUT_USD
        + output_tokens / 1_000_000 * PRICE_PER_MILLION_OUTPUT_USD,
        6,
    )


__all__ = [
    "DEFAULT_MODEL",
    "DEFAULT_THINKING_LEVEL",
    "LLMStatus",
    "LLMUnavailableError",
    "PRICE_PER_MILLION_INPUT_USD",
    "PRICE_PER_MILLION_OUTPUT_USD",
    "api_key",
    "chat_model",
    "estimate_cost_usd",
    "load_environment",
    "message_text",
    "probe",
    "require",
    "usage_of",
]
