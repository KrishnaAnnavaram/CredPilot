"""NFR-04: timeouts, bounded retries, and graceful degradation.

*"Agent pipeline uses async where it calls tools/models; graceful degradation on
tool/model failure (timeouts, retries, exit conditions)."*

Three properties, and the third is the one that is usually missing:

* a call that hangs is **cut off** at its deadline;
* a call that keeps failing is **given up on** after a bounded number of
  attempts, and says how many it used;
* what is **not** retried is as important as what is. A malformed response, a
  validation error and a refusal are deterministic — retrying them spends money
  to receive the same answer — so they stop after one attempt.

No sleeping in these tests beyond a few tens of milliseconds. A retry test that
waits for real backoff is a slow test that people disable.
"""

from __future__ import annotations

import asyncio
import time

import pytest

from src.resilience import (
    DependencyUnavailable,
    NonRetryableError,
    OperationTimeout,
    RetryExhausted,
    RetryPolicy,
    ToolFailure,
    call_sync_with_resilience,
    call_with_resilience,
    failure_summary,
    first_failure,
    run_async,
    safe_call,
    safe_call_sync,
)

FAST = RetryPolicy(max_attempts=3, timeout_seconds=0.25, backoff_seconds=0.01,
                   jitter=False)


def run(coro):
    return asyncio.run(coro)


# ------------------------------------------------------------------ timeouts


def test_a_hanging_call_is_cut_off_at_its_deadline():
    async def hangs():
        await asyncio.sleep(30)

    started = time.perf_counter()
    with pytest.raises(RetryExhausted) as caught:
        run(call_with_resilience("hangs", hangs, policy=FAST))
    elapsed = time.perf_counter() - started

    # Three attempts at 0.25s, not one wait of 30.
    assert elapsed < 3.0, f"took {elapsed:.1f}s; the deadline was not enforced"
    assert caught.value.attempts == 3
    assert isinstance(caught.value.cause, OperationTimeout)


def test_a_timeout_comes_back_as_a_value_from_safe_call():
    """A graph node has to produce a state update however the call went."""
    async def hangs():
        await asyncio.sleep(30)

    outcome = run(safe_call("hangs", hangs, policy=FAST))
    assert isinstance(outcome, ToolFailure)
    assert outcome.ok is False
    assert outcome.error_type == "OperationTimeout"
    assert outcome.attempts == 3
    assert outcome.as_dict()["retryable"] is True


# ------------------------------------------------------------------- retries


def test_a_transient_failure_is_retried_and_then_succeeds():
    attempts = {"n": 0}

    async def flaky():
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise ConnectionError("not yet")
        return "recovered"

    assert run(call_with_resilience("flaky", flaky, policy=FAST)) == "recovered"
    assert attempts["n"] == 3


def test_retries_are_bounded_and_the_count_is_reported():
    """An unbounded retry against a paid endpoint is unbounded spend."""
    attempts = {"n": 0}

    async def always_fails():
        attempts["n"] += 1
        raise ConnectionError("down")

    with pytest.raises(RetryExhausted) as caught:
        run(call_with_resilience("always", always_fails, policy=FAST))
    assert attempts["n"] == 3, "the cap was not enforced"
    assert caught.value.attempts == 3
    assert "3 attempt" in str(caught.value)


def test_a_deterministic_failure_is_not_retried():
    """A malformed response will be malformed again. Retrying it buys nothing."""
    attempts = {"n": 0}

    async def malformed():
        attempts["n"] += 1
        raise NonRetryableError("the server returned something unparseable")

    with pytest.raises(NonRetryableError):
        run(call_with_resilience("malformed", malformed, policy=FAST))
    assert attempts["n"] == 1, f"a non-retryable error was retried {attempts['n']} times"


def test_an_unlisted_exception_propagates_on_the_first_attempt():
    """Only faults that might not recur are worth another go."""
    attempts = {"n": 0}

    async def bug():
        attempts["n"] += 1
        raise ValueError("a programming error, not a transient one")

    with pytest.raises(ValueError):
        run(call_with_resilience("bug", bug, policy=FAST))
    assert attempts["n"] == 1


def test_backoff_grows_and_is_capped():
    policy = RetryPolicy(backoff_seconds=1.0, max_backoff_seconds=4.0, jitter=False)
    assert policy.delay_for(1) == 0.0, "the first attempt never waits"
    assert policy.delay_for(2) == 1.0
    assert policy.delay_for(3) == 2.0
    assert policy.delay_for(4) == 4.0
    assert policy.delay_for(9) == 4.0, "backoff exceeded its cap"


def test_jitter_keeps_the_delay_inside_the_window():
    """Several callers that failed together must not retry together."""
    policy = RetryPolicy(backoff_seconds=1.0, max_backoff_seconds=4.0, jitter=True)
    delays = [policy.delay_for(3) for _ in range(200)]
    assert all(0 < d <= 2.0 for d in delays), (min(delays), max(delays))
    assert len(set(delays)) > 50, "jitter produced the same delay every time"


# ---------------------------------------------------------------- sync surface


def test_the_sync_surface_retries_and_gives_up():
    attempts = {"n": 0}

    def always_fails():
        attempts["n"] += 1
        raise ConnectionError("down")

    outcome = safe_call_sync("sync", always_fails, policy=FAST)
    assert isinstance(outcome, ToolFailure)
    assert attempts["n"] == 3


def test_the_sync_surface_returns_a_value_on_success():
    assert call_sync_with_resilience("ok", lambda: 42, policy=FAST) == 42


def test_the_sync_surface_treats_an_overrun_as_a_failure():
    """It cannot interrupt a synchronous call, so it checks afterwards.

    Weaker than the async deadline and stated as such — what matters is that an
    overrunning call does not come back as a success.
    """
    def slow():
        time.sleep(0.4)
        return "late"

    policy = RetryPolicy(max_attempts=1, timeout_seconds=0.05, backoff_seconds=0.0,
                         jitter=False)
    outcome = safe_call_sync("slow", slow, policy=policy)
    assert isinstance(outcome, ToolFailure)


# ------------------------------------------------------------------- helpers


def test_run_async_works_from_inside_a_running_loop():
    """The web app invokes the graph from an event loop; the graph is sync."""
    async def outer():
        # Calling asyncio.run from here would raise; run_async must not.
        return run_async(_answer())

    async def _answer():
        return "inner"

    assert asyncio.run(outer()) == "inner"


def test_run_async_works_with_no_loop_running():
    async def answer():
        return "value"

    assert run_async(answer()) == "value"


def test_failures_roll_up_for_the_state_record():
    failures = [
        ToolFailure("retrieve_policy", "OperationTimeout", "slow", attempts=2),
        ToolFailure("retrieve_policy", "OperationTimeout", "slow", attempts=3),
        ToolFailure("mcp.tool:x", "ConnectionError", "down", attempts=1),
    ]
    summary = failure_summary(failures)
    assert summary["count"] == 3
    assert summary["by_error_type"] == {"ConnectionError": 1, "OperationTimeout": 2}
    assert summary["operations"] == ["mcp.tool:x", "retrieve_policy"]
    assert summary["total_attempts"] == 6


def test_first_failure_finds_the_one_that_matters():
    assert first_failure(["a", "b"]) is None
    failure = ToolFailure("op", "X", "m")
    assert first_failure(["a", failure, "b"]) is failure


def test_a_tool_failure_serializes_for_the_checkpoint():
    """It crosses SQLite on the state, so it has to be plain data."""
    import json

    failure = ToolFailure("retrieve_policy", "OperationTimeout", "timed out",
                          attempts=2, latency_ms=1234.5)
    payload = failure.as_dict()
    assert json.loads(json.dumps(payload)) == payload
    assert payload["ok"] is False
    assert payload["attempts"] == 2


# ---------------------------------------------------- degradation in the graph


@pytest.mark.integration
def test_a_retrieval_failure_degrades_rather_than_killing_the_run(
    indexes_built, tmp_path, repo_root, monkeypatch
):
    """A file whose retrieval keeps failing is still assessable.

    The remaining questions are still asked, the loss is recorded on the state,
    and the reviewer sees what was missing — rather than a traceback inside a
    checkpoint with no decision attached.

    The fault has to be **persistent** for a degradation to be the right
    outcome. `ConnectionError` is on `RetryPolicy.retry_on` and the policy
    allows two attempts, so one raise is retried and succeeds; recording a
    degradation for a fault the retry absorbed would be reporting a loss that
    did not happen. Both attempts of one question fail here, and only that
    question's.
    """
    if not indexes_built:
        pytest.skip("indexes not built")

    import src.graph as graph_module
    from src.graph import build_graph, initial_state

    real = graph_module.retrieve_policy_tool
    calls = {"n": 0}

    def flaky(*args, **kwargs):
        calls["n"] += 1
        # Attempts 1 and 2 of the second question, and nothing else.
        if calls["n"] in (2, 3):
            raise ConnectionError("the retriever fell over on this question")
        return real(*args, **kwargs)

    monkeypatch.setattr(graph_module, "retrieve_policy_tool", flaky)

    graph, context = build_graph(checkpoint_path=tmp_path / "degrade.sqlite")
    try:
        result = graph.invoke(
            initial_state(repo_root / "synthetic_data/mortgage/applications/APP-000057.json"),
            config={"configurable": {"thread_id": "degrade-1"}},
        )
    finally:
        if context is not None:
            context.__exit__(None, None, None)

    # It finished, and it finished with a decision.
    assert result["steps"][-1] == "output_guardrails"
    assert (result.get("recommendation") or {}).get("outcome")
    # And the loss is on the record rather than silently absorbed.
    assert result.get("degradations"), "a failed retrieval left no trace"
    failure = result["degradations"][0]
    assert failure["stage"] == "policy_retrieval"
    assert failure["attempts"] == 2, "the policy allows two attempts; both should be spent"
    assert failure["error_type"] == "ConnectionError"
    assert any("TOOL_FAILURE" in s for s in result["retrieval_statuses"])


@pytest.mark.integration
def test_a_transient_retrieval_failure_is_retried_and_leaves_no_degradation(
    indexes_built, tmp_path, repo_root, monkeypatch
):
    """The other half of NFR-04, and the one that is easy to get wrong.

    A fault the retry absorbed is not a loss, and reporting one would tell a
    reviewer that evidence is missing when it is not. The run must come back
    with a clean record and the retrieval must actually have been attempted
    twice — so this asserts the extra call as well as the empty degradation
    list, or a policy that silently stopped retrying would pass.
    """
    if not indexes_built:
        pytest.skip("indexes not built")

    import src.graph as graph_module
    from src.graph import build_graph, initial_state

    real = graph_module.retrieve_policy_tool
    calls = {"n": 0}

    def once_flaky(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] == 2:
            raise ConnectionError("one dropped connection, then fine")
        return real(*args, **kwargs)

    monkeypatch.setattr(graph_module, "retrieve_policy_tool", once_flaky)

    graph, context = build_graph(checkpoint_path=tmp_path / "transient.sqlite")
    try:
        result = graph.invoke(
            initial_state(repo_root / "synthetic_data/mortgage/applications/APP-000057.json"),
            config={"configurable": {"thread_id": "transient-1"}},
        )
    finally:
        if context is not None:
            context.__exit__(None, None, None)

    assert result["steps"][-1] == "output_guardrails"
    assert (result.get("recommendation") or {}).get("outcome")
    assert result.get("degradations") == [], (
        "a fault the retry absorbed was reported as a loss: " f"{result.get('degradations')}"
    )
    assert not any("TOOL_FAILURE" in s for s in result["retrieval_statuses"])
    assert calls["n"] > 2, "the failed call was never retried"


@pytest.mark.integration
def test_losing_every_retrieval_refers_the_file_rather_than_deciding_it(
    indexes_built, tmp_path, repo_root, monkeypatch
):
    """No evidence is not permission (GEN-ELG-005)."""
    if not indexes_built:
        pytest.skip("indexes not built")

    import src.graph as graph_module
    from src.graph import build_graph, initial_state

    def always_fails(*args, **kwargs):
        raise ConnectionError("retrieval is down")

    monkeypatch.setattr(graph_module, "retrieve_policy_tool", always_fails)
    monkeypatch.setattr(
        graph_module, "_fetch_rules_resiliently", lambda **kwargs: []
    )

    graph, context = build_graph(checkpoint_path=tmp_path / "nodata.sqlite")
    try:
        result = graph.invoke(
            initial_state(repo_root / "synthetic_data/mortgage/applications/APP-000057.json"),
            config={"configurable": {"thread_id": "nodata-1"}},
        )
    finally:
        if context is not None:
            context.__exit__(None, None, None)

    assert result["requires_human_review"] is True
    assert not result.get("policy_evidence")
    assert any(
        "no applicable policy evidence" in reason
        for reason in result["human_review_reasons"]
    )
    # It did not approve anything on an empty rulebook.
    assert (result.get("recommendation") or {}).get("outcome") != "APPROVE_RECOMMENDATION"


@pytest.mark.integration
def test_an_application_with_no_as_of_date_is_referred_not_crashed(
    indexes_built, tmp_path
):
    """A missing input is a referral, not an exception.

    Which policy version governs is a function of the as-of date — the whole
    point of APP-000055/56/57 — so a file without one cannot be assessed and
    must not be assessed against a guess. Found by submitting an uploaded
    packet with no date: temporal filtering collapsed nothing, both versions of
    POL-DTI-001 reached the rule engine, and `assert_single_version` raised out
    of the eligibility node as an unhandled error.
    """
    if not indexes_built:
        pytest.skip("indexes not built")

    from src.graph import DEFAULT_STEP_BUDGET, build_graph

    state = {
        "application_id": "APP-999001",
        "application_packet": {
            "application_id": "APP-999001",
            "subject_property": {},
            "borrowers": [],
            "product_family": "conventional_conforming",
            "loan_purpose": "purchase",
        },
        "as_of_date": None,
        "message": "",
        "policy_evidence": [], "retrieval_statuses": [], "human_review_reasons": [],
        "security_findings": [], "errors": [], "steps": [], "degradations": [],
        "conversation_history": [], "recalled_memory": [],
        "session_id": "undated", "subject_id": None,
        "step_budget": DEFAULT_STEP_BUDGET, "steps_taken": 0,
        "clarification_rounds": 0, "halted": False, "requires_human_review": False,
    }

    graph, context = build_graph(checkpoint_path=tmp_path / "undated.sqlite")
    try:
        result = graph.invoke(state, config={"configurable": {"thread_id": "undated-1"}})
    finally:
        if context is not None:
            context.__exit__(None, None, None)

    assert result["requires_human_review"] is True
    assert any(
        "as-of date" in reason for reason in result["human_review_reasons"]
    ), result["human_review_reasons"]
    # It stopped before retrieving, rather than retrieving both versions.
    assert not result.get("policy_evidence")
    assert result["steps"][-1] == "output_guardrails"


@pytest.mark.integration
def test_mixed_version_evidence_refers_rather_than_raising(indexes_built, tmp_path):
    """Defence in depth behind the check above.

    Deciding a file against two versions of one rulebook is the wrong answer;
    so is a traceback inside a checkpoint. The engine raises
    MixedVersionEvidenceError and the node turns it into INDETERMINATE.
    """
    if not indexes_built:
        pytest.skip("indexes not built")

    from src import rules
    from src.domain import LendingProductDomain
    from src.graph import make_eligibility_node

    mixed = [
        {"rule_id": "DTI-CONV-001", "policy_id": "POL-DTI-001", "policy_version": "1.0",
         "citation": "POL-DTI-001 v1.0 rule DTI-CONV-001", "text": "45 percent"},
        {"rule_id": "DTI-CONV-001", "policy_id": "POL-DTI-001", "policy_version": "2.0",
         "citation": "POL-DTI-001 v2.0 rule DTI-CONV-001", "text": "43 percent"},
    ]
    with pytest.raises(rules.MixedVersionEvidenceError):
        rules.evaluate(
            LendingProductDomain.MORTGAGE, {"ratios": {}, "amounts": {}}, {}, mixed
        )

    node = make_eligibility_node(LendingProductDomain.MORTGAGE)
    update = node({
        "loan_domain": "MORTGAGE", "application_packet": {}, "policy_evidence": mixed,
        "step_budget": 32, "steps_taken": 0,
    })
    assert update["eligibility"]["status"] == "INDETERMINATE"
    assert update["requires_human_review"] is True
    assert "more than one version" in update["human_review_reasons"][0]


@pytest.mark.integration
def test_the_model_being_unreachable_does_not_fail_an_assessment(
    indexes_built, tmp_path, repo_root, monkeypatch
):
    """A recommendation without prose is still a recommendation."""
    if not indexes_built:
        pytest.skip("indexes not built")

    from src import llm
    from src.graph import build_graph, initial_state

    monkeypatch.setattr(
        llm, "probe",
        lambda *a, **k: llm.LLMStatus(False, None, "forced unavailable for this test"),
    )

    graph, context = build_graph(checkpoint_path=tmp_path / "nollm.sqlite")
    try:
        result = graph.invoke(
            initial_state(repo_root / "synthetic_data/mortgage/applications/APP-000057.json"),
            config={"configurable": {"thread_id": "nollm-1"}},
        )
    finally:
        if context is not None:
            context.__exit__(None, None, None)

    assert (result.get("recommendation") or {}).get("outcome")
    narrative = result.get("narrative") or {}
    assert narrative.get("available") is False
    # The reader must be able to tell a deterministic summary from model prose.
    assert narrative.get("note")
    assert result["final_response"]["text"]
