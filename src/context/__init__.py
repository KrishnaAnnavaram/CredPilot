"""Context engineering (REQ-074).

*"src/context/ | write/select/compress/isolate; summarization middleware;
quarantine of untrusted text"*

A model's context window is a budget, and an underwriting file is bigger than it.
Forty evidence chunks, an application packet, a calculation record and a rule
evaluation do not fit, and stuffing them in until they do is how a system starts
answering from whichever fragment survived truncation.

The four operations, each in its own module:

* :mod:`~src.context.write` — record what happened, in a form that can be read
  back: the run scratchpad.
* :mod:`~src.context.select` — choose what this turn actually needs, by relevance
  and by role, rather than passing everything.
* :mod:`~src.context.compress` — reduce what is selected to fit a budget, with a
  deterministic path that never calls a model and a summarization path that does.
* :mod:`~src.context.isolate` — keep untrusted applicant text, policy evidence
  and computed figures in separate compartments that cannot be confused for one
  another.

The ordering matters and is enforced by :func:`build_context`: isolate first,
then select, then compress, then write. Compressing before isolating would let a
summarizer read applicant text as instruction; selecting before isolating would
let it be selected *as* evidence.
"""

from src.context.compress import (
    CompressionResult,
    compress_evidence,
    summarize_text,
    truncate_to_budget,
)
from src.context.isolate import (
    Compartment,
    IsolatedContext,
    isolate,
)
from src.context.select import (
    SelectionResult,
    select_evidence,
    select_for_role,
)
from src.context.write import (
    ContextRecord,
    Scratchpad,
)
from src.context.assemble import AssembledContext, build_context

__all__ = [
    "AssembledContext",
    "Compartment",
    "CompressionResult",
    "ContextRecord",
    "IsolatedContext",
    "Scratchpad",
    "SelectionResult",
    "build_context",
    "compress_evidence",
    "isolate",
    "select_evidence",
    "select_for_role",
    "summarize_text",
    "truncate_to_budget",
]
