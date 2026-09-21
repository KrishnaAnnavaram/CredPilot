"""Gemini as the LLM-as-judge behind DeepEval.

REQ-097 asks for *"DeepEval (or equiv) over a golden set: hallucination +
faithfulness/relevance; LLM-as-judge"*, and REQ-036 allows exactly one provider.
DeepEval reaches for OpenAI by default, so this module supplies the judge
instead; nothing here changes what is scored, only who scores it.

A standing caveat, recorded because it affects how the numbers should be read:
the judge and the system under test are the same model family. A judge shares
its own blind spots with the thing it is judging, so these scores are evidence,
not proof. That is why every generated rationale also passes the deterministic
check in :func:`src.narrative.verify_narrative`, which does not ask a model
anything — and why the report carries both, separately. Where the two disagree,
the deterministic one is the one to believe.
"""

from __future__ import annotations

import json
import threading
from typing import Any

from deepeval.models import DeepEvalBaseLLM

from src import llm

#: Judging is a classification task, so it is pinned cold. A judge that changes
#: its mind between runs makes a regression indistinguishable from noise.
JUDGE_TEMPERATURE = 0.0

#: And for the same reason it is given little room to deliberate. Measured on a
#: claim-extraction prompt: 778 reasoning tokens and 3.0s by default against 0.9s
#: at ``"low"``, with byte-identical output. Over the ten or so calls DeepEval
#: makes per case, across 95 cases, that difference is the whole run.
JUDGE_THINKING_LEVEL = "low"


class GeminiJudge(DeepEvalBaseLLM):
    """A DeepEval judge backed by Gemini.

    DeepEval calls ``generate(prompt, schema=SomePydanticModel)`` for metrics
    that need structured verdicts and ``generate(prompt)`` for the rest, so both
    paths are supported. When a schema is asked for, the response is coerced into
    it rather than returned as prose — a metric that receives a string where it
    expected a model silently scores zero.
    """

    def __init__(self, model: str | None = None):
        self._model_name = model or llm.require()
        self._client = None
        self._lock = threading.Lock()
        self.calls = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.reasoning_tokens = 0
        super().__init__(self._model_name)

    # -- DeepEvalBaseLLM ----------------------------------------------------------

    def load_model(self, *args: Any, **kwargs: Any):
        if self._client is None:
            llm.load_environment()
            from google import genai

            self._client = genai.Client(api_key=llm.api_key())
        return self._client

    def get_model_name(self, *args: Any, **kwargs: Any) -> str:
        return f"gemini:{self._model_name}"

    def generate(self, prompt: str, schema: Any | None = None, *args: Any, **kwargs: Any):
        client = self.load_model()
        config: dict[str, Any] = {
            "temperature": JUDGE_TEMPERATURE,
            "thinking_config": {"thinking_level": JUDGE_THINKING_LEVEL},
        }
        if schema is not None:
            config["response_mime_type"] = "application/json"
            config["response_schema"] = schema

        response = client.models.generate_content(
            model=self._model_name, contents=prompt, config=config
        )
        self._record(response)

        text = (response.text or "").strip()
        if schema is None:
            return text
        return self._coerce(text, schema, response)

    async def a_generate(self, prompt: str, schema: Any | None = None, *args: Any, **kwargs: Any):
        # The SDK call is synchronous; DeepEval only needs the coroutine shape.
        return self.generate(prompt, schema, *args, **kwargs)

    # -- internals ----------------------------------------------------------------

    def _record(self, response: Any) -> None:
        usage = getattr(response, "usage_metadata", None)
        with self._lock:
            self.calls += 1
            if usage:
                self.input_tokens += int(getattr(usage, "prompt_token_count", 0) or 0)
                self.output_tokens += int(getattr(usage, "candidates_token_count", 0) or 0)
                self.reasoning_tokens += int(getattr(usage, "thoughts_token_count", 0) or 0)

    @staticmethod
    def _coerce(text: str, schema: Any, response: Any) -> Any:
        """Turn the judge's reply into the model DeepEval asked for."""
        parsed = getattr(response, "parsed", None)
        if isinstance(parsed, schema):
            return parsed
        try:
            return schema(**json.loads(text))
        except Exception:  # noqa: BLE001 - fall through to the salvage attempt
            pass
        # A judge occasionally wraps its JSON in a fence despite the mime type.
        stripped = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```")
        return schema(**json.loads(stripped))

    # -- accounting ---------------------------------------------------------------

    @property
    def usage(self) -> dict[str, int]:
        """What the judging itself cost, kept apart from the system's own spend."""
        return {
            "judge_calls": self.calls,
            "judge_input_tokens": self.input_tokens,
            "judge_output_tokens": self.output_tokens,
            "judge_reasoning_tokens": self.reasoning_tokens,
        }

    @property
    def cost_usd(self) -> float:
        return llm.estimate_cost_usd(self.input_tokens, self.output_tokens)


__all__ = ["GeminiJudge", "JUDGE_TEMPERATURE", "JUDGE_THINKING_LEVEL"]
