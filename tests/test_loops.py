"""Loop and cascade guard (REQ-095).

*"asserts a max-steps / recursion-limit stops runaway loops"*

A runaway loop in an underwriting system is not a performance problem. It is an
unbounded spend against an applicant's file that never produces a decision, and
— because every retrieval writes to the tool log and the audit trail — an
unbounded write amplification alongside it.

Two independent guards, tested separately because they fail differently:

* **the in-state step budget** (``DEFAULT_STEP_BUDGET``) is checked by every
  node, so a run that exhausts it halts *cleanly*: it routes to human review
  with a reason a person can read, and the recommendation still exists;
* **LangGraph's ``recursion_limit``** sits outside the graph and raises
  ``GraphRecursionError``. It is the backstop for a cycle that never reaches a
  node able to check anything.

The shipped graph is linear, so neither fires in normal operation. That is
exactly why they are tested against a deliberately cyclic graph rather than
against the real one — a guard nothing exercises is a guard nobody knows works.
"""

from __future__ import annotations

import uuid

import pytest

from src.graph import (
    DEFAULT_STEP_BUDGET,
    RECURSION_LIMIT,
    CredPilotState,
    budget_exhausted,
    build_graph,
    initial_state,
)


# ------------------------------------------------------------------ the budget itself


def test_a_fresh_run_has_budget():
    assert not budget_exhausted({"step_budget": DEFAULT_STEP_BUDGET, "steps_taken": 0})


def test_an_exhausted_run_is_detected():
    assert budget_exhausted({"step_budget": 5, "steps_taken": 5})
    assert budget_exhausted({"step_budget": 5, "steps_taken": 99})


def test_a_missing_budget_falls_back_to_the_default():
    """An absent budget must not mean an infinite one."""
    assert not budget_exhausted({"steps_taken": 0})
    assert budget_exhausted({"steps_taken": DEFAULT_STEP_BUDGET})
    assert budget_exhausted({"steps_taken": DEFAULT_STEP_BUDGET + 1})


def test_the_budget_leaves_headroom_over_a_real_run():
    """The budget must not trip on ordinary work, or it is just an outage."""
    assert DEFAULT_STEP_BUDGET >= 12
    assert RECURSION_LIMIT > DEFAULT_STEP_BUDGET


# ------------------------------------------------------ a deliberately cyclic graph


def _cycle_graph(step_budget: int, recursion_limit: int):
    """Two nodes that route to each other forever, with the real guard in place."""
    from langgraph.graph import END, START, StateGraph

    from src.graph import _guard

    def ping(state: CredPilotState) -> dict:
        halt = _guard(state, "ping")
        if halt is not None:
            return halt
        return {"steps": ["ping"], "steps_taken": 1, "route": "pong"}

    def pong(state: CredPilotState) -> dict:
        halt = _guard(state, "pong")
        if halt is not None:
            return halt
        return {"steps": ["pong"], "steps_taken": 1, "route": "ping"}

    def route(state: CredPilotState):
        if state.get("halted"):
            return "__end__"
        return "pong" if state.get("route") == "pong" else "ping"

    builder = StateGraph(CredPilotState)
    builder.add_node("ping", ping)
    builder.add_node("pong", pong)
    builder.add_edge(START, "ping")
    builder.add_conditional_edges("ping", route, {"pong": "pong", "__end__": END, "ping": "ping"})
    builder.add_conditional_edges("pong", route, {"ping": "ping", "__end__": END, "pong": "pong"})
    return builder.compile().with_config(recursion_limit=recursion_limit)


def test_a_runaway_loop_is_stopped_by_the_step_budget():
    """The cycle halts itself, cleanly, before the recursion limit fires."""
    graph = _cycle_graph(step_budget=8, recursion_limit=RECURSION_LIMIT)
    result = graph.invoke(
        {"step_budget": 8, "steps_taken": 0, "steps": [], "human_review_reasons": []},
        config={"configurable": {"thread_id": f"loop-{uuid.uuid4().hex[:8]}"}},
    )

    assert result["halted"] is True
    assert result["steps_taken"] <= 8 + 1, "the budget was overshot"
    assert result["requires_human_review"] is True
    assert any("halted" in reason for reason in result["human_review_reasons"])
    assert result["steps"][-1].endswith(":halted")


def test_the_halt_reason_names_the_node_and_the_budget():
    """A halt has to be diagnosable from the record alone."""
    graph = _cycle_graph(step_budget=4, recursion_limit=RECURSION_LIMIT)
    result = graph.invoke(
        {"step_budget": 4, "steps_taken": 0, "steps": [], "human_review_reasons": []},
        config={"configurable": {"thread_id": f"loop-{uuid.uuid4().hex[:8]}"}},
    )
    reason = " ".join(result["human_review_reasons"])
    assert "4" in reason
    assert "ping" in reason or "pong" in reason
    assert "no decision was reached" in reason


def test_the_recursion_limit_stops_a_loop_the_budget_cannot_see():
    """The backstop: a cycle whose nodes never check the budget still terminates.

    This is the case the in-state guard cannot catch — a node that does not call
    ``_guard`` can loop forever, so LangGraph's own limit must raise rather than
    the process spinning.
    """
    from langgraph.errors import GraphRecursionError
    from langgraph.graph import START, StateGraph

    def spin(state: CredPilotState) -> dict:
        return {"steps_taken": 1}

    builder = StateGraph(CredPilotState)
    builder.add_node("spin", spin)
    builder.add_edge(START, "spin")
    builder.add_conditional_edges("spin", lambda s: "spin", {"spin": "spin"})
    graph = builder.compile().with_config(recursion_limit=12)

    with pytest.raises(GraphRecursionError):
        graph.invoke(
            {"steps_taken": 0},
            config={"configurable": {"thread_id": f"spin-{uuid.uuid4().hex[:8]}"}},
        )


# ------------------------------------------------------------- the real graph


@pytest.mark.slow
@pytest.mark.integration
def test_the_real_graph_carries_the_recursion_limit(indexes_built, tmp_path):
    if not indexes_built:
        pytest.skip("indexes not built")
    graph, context = build_graph(checkpoint_path=tmp_path / "loops.sqlite")
    try:
        configured = graph.config or {}
        assert configured.get("recursion_limit") == RECURSION_LIMIT
    finally:
        if context is not None:
            context.__exit__(None, None, None)


@pytest.mark.slow
@pytest.mark.integration
def test_a_real_assessment_stays_well_inside_the_budget(indexes_built, tmp_path, repo_root):
    """An ordinary run must not be anywhere near the limit."""
    if not indexes_built:
        pytest.skip("indexes not built")
    graph, context = build_graph(checkpoint_path=tmp_path / "loops2.sqlite")
    try:
        for relative in (
            "synthetic_data/mortgage/applications/APP-000056.json",
            "synthetic_data/education/applications/APP-2026-00001.json",
        ):
            state = initial_state(repo_root / relative)
            result = graph.invoke(
                state,
                config={"configurable": {"thread_id": f"budget-{uuid.uuid4().hex[:8]}"}},
            )
            assert result["halted"] is False, f"{relative} halted unexpectedly"
            assert 0 < result["steps_taken"] < DEFAULT_STEP_BUDGET / 2, (
                f"{relative} used {result['steps_taken']} of {DEFAULT_STEP_BUDGET} steps"
            )
    finally:
        if context is not None:
            context.__exit__(None, None, None)


@pytest.mark.slow
@pytest.mark.integration
def test_a_starved_budget_halts_a_real_assessment(indexes_built, tmp_path, repo_root):
    """Force the guard on the production graph, not just a toy one."""
    if not indexes_built:
        pytest.skip("indexes not built")
    graph, context = build_graph(checkpoint_path=tmp_path / "loops3.sqlite")
    try:
        state = initial_state(
            repo_root / "synthetic_data/mortgage/applications/APP-000056.json"
        )
        state["step_budget"] = 2
        result = graph.invoke(
            state, config={"configurable": {"thread_id": f"starved-{uuid.uuid4().hex[:8]}"}}
        )
        assert result["halted"] is True
        assert result["requires_human_review"] is True
        # The budget bounds the *work*; halting then costs a fixed tail of node
        # visits — the node that detected it, the human-review handoff, and the
        # two response nodes that turn "halted after N steps" into something a
        # reviewer can read. Four, and it does not grow with the file.
        assert result["steps_taken"] <= 2 + 4
        # It halted rather than producing a decision on partial evidence.
        assert not (result.get("recommendation") or {}).get("outcome")
        assert any("halted" in reason for reason in result["human_review_reasons"])
    finally:
        if context is not None:
            context.__exit__(None, None, None)
