"""Compress — fit a budget without losing what decides the file.

Two paths, and which one runs matters:

* **Deterministic truncation** is the default. It trims at paragraph boundaries,
  keeps the parameter tables that carry the thresholds, and calls no model. It is
  reproducible, free, and cannot invent anything.
* **Model summarization** is opt-in, and only ever applied to *narrative* text —
  never to a policy rule. A summarized threshold is a threshold nobody can cite,
  and a paraphrase of "must not exceed 43 percent" that comes back as "around
  43%" is exactly the failure this system exists to avoid.

So: policy evidence is truncated, never summarized. Conversation history and
prior-session notes may be summarized.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

#: Roughly four characters per token for English. Used to size budgets without
#: paying for a tokenizer round trip; deliberately conservative.
CHARS_PER_TOKEN = 4

#: Lines that carry a threshold. A parameter table is the part of a rule that a
#: decision rests on, so it survives truncation ahead of prose.
_PARAMETER_LINE = re.compile(r"^\s*\|\s*`[a-z0-9_]+`\s*\|")
_TABLE_LINE = re.compile(r"^\s*\|")


@dataclass
class CompressionResult:
    text: str
    original_chars: int
    kept_chars: int
    method: str
    dropped_items: int = 0
    notes: list[str] = field(default_factory=list)

    @property
    def ratio(self) -> float:
        return self.kept_chars / self.original_chars if self.original_chars else 1.0

    def summary(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "original_chars": self.original_chars,
            "kept_chars": self.kept_chars,
            "ratio": round(self.ratio, 4),
            "dropped_items": self.dropped_items,
            "notes": self.notes,
        }


def tokens_for(text: str) -> int:
    return max(1, len(text) // CHARS_PER_TOKEN)


def truncate_to_budget(text: str, max_chars: int) -> str:
    """Trim at a paragraph boundary, keeping any parameter table intact.

    A rule's prose can go; the table under it cannot, because that is where the
    number is.
    """
    if len(text) <= max_chars:
        return text

    lines = text.splitlines()
    table_lines = [line for line in lines if _TABLE_LINE.match(line)]
    table_text = "\n".join(table_lines)

    # Reserve room for the table, then fill with as much prose as fits.
    reserve = len(table_text) + 2 if table_lines else 0
    prose_budget = max(max_chars - reserve, max_chars // 2)

    prose: list[str] = []
    used = 0
    for paragraph in re.split(r"\n{2,}", text):
        if any(_TABLE_LINE.match(line) for line in paragraph.splitlines()):
            continue
        if used + len(paragraph) + 2 > prose_budget:
            break
        prose.append(paragraph)
        used += len(paragraph) + 2

    parts = ["\n\n".join(prose).strip()]
    if table_text:
        parts.append(table_text)
    out = "\n\n".join(p for p in parts if p)
    return out[:max_chars] if len(out) > max_chars else out + "\n[truncated]"


def compress_evidence(
    evidence: Sequence[Mapping[str, Any]],
    *,
    max_chars: int,
    max_items: int | None = None,
    per_item_chars: int = 1200,
) -> CompressionResult:
    """Fit evidence into a character budget, deterministically.

    Never calls a model. Drops whole items from the tail rather than truncating
    every item into uselessness — six complete rules beat twelve fragments.
    """
    items = list(evidence)[: max_items or len(evidence)]
    original = sum(len(str(item.get("text", ""))) for item in items)

    rendered: list[str] = []
    used = 0
    dropped = 0
    notes: list[str] = []

    for item in items:
        citation = item.get("citation", "")
        title = item.get("rule_title") or item.get("section_title") or ""
        body = truncate_to_budget(str(item.get("text", "")), per_item_chars)
        block = f"[{citation}] {title}\n{body}".strip()

        if used + len(block) > max_chars:
            dropped = len(items) - len(rendered)
            notes.append(
                f"{dropped} evidence chunk(s) dropped whole at the budget rather "
                f"than truncating every chunk"
            )
            break
        rendered.append(block)
        used += len(block) + 2

    text = "\n\n".join(rendered)
    return CompressionResult(
        text=text,
        original_chars=original,
        kept_chars=len(text),
        method="deterministic-truncation",
        dropped_items=dropped,
        notes=notes,
    )


def summarize_text(
    text: str,
    *,
    max_chars: int = 1500,
    purpose: str = "prior-session context",
    model: str | None = None,
) -> CompressionResult:
    """Summarize narrative text with Gemini, falling back to truncation.

    **Only for narrative.** Policy rules are never passed here — a paraphrased
    threshold cannot be cited and may not survive the paraphrase intact.

    When the model is unreachable this degrades to deterministic truncation
    rather than failing: a run must not stop because summarization is
    unavailable, and the result records which path it took.
    """
    if len(text) <= max_chars:
        return CompressionResult(text, len(text), len(text), "no-compression-needed")

    from src import llm

    status = llm.probe()
    if not status.available:
        truncated = truncate_to_budget(text, max_chars)
        return CompressionResult(
            truncated,
            len(text),
            len(truncated),
            "deterministic-truncation-fallback",
            notes=[f"summarization unavailable ({status.reason}); truncated instead"],
        )

    prompt = (
        f"Summarize the following {purpose} for an underwriting assistant.\n\n"
        f"Rules:\n"
        f"- Keep every figure, date, identifier and decision exactly as written.\n"
        f"- Do not infer, estimate or round anything.\n"
        f"- Do not add a conclusion the text does not state.\n"
        f"- Keep it under {max_chars // 5} words.\n\n"
        f"Text:\n{text}"
    )
    try:
        response = llm.chat_model(model or status.model).invoke(prompt)
        summary = llm.message_text(response).strip()
        if not summary:
            raise ValueError("empty summary")
        return CompressionResult(
            summary,
            len(text),
            len(summary),
            f"gemini-summarization:{status.model}",
            notes=[f"tokens {llm.usage_of(response)}"],
        )
    except Exception as exc:  # noqa: BLE001 - never fail a run on compression
        truncated = truncate_to_budget(text, max_chars)
        return CompressionResult(
            truncated,
            len(text),
            len(truncated),
            "deterministic-truncation-fallback",
            notes=[f"summarization failed ({type(exc).__name__}); truncated instead"],
        )
