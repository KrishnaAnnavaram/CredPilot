"""The conversational path through the graph: clarify, resume, carry forward.

AC-04 — *"ambiguous or out-of-scope requests are clarified or escalated to a
human, not mishandled"* — and AC-05 — *"uses facts stated earlier in the
interaction"*.

What is worth asserting here, and what is not:

Worth it — that the run **pauses** rather than guessing, that the original
request survives the pause, that the answer is read as an answer to the question
that was asked, and that a request the system cannot resolve stops being asked
about and goes to a person.

Not worth it — the wording of any particular clarification. That is a product
decision and pinning it in a test makes it unchangeable.
"""

from __future__ import annotations

import uuid

import pytest

from langgraph.types import Command

from src.graph import (
    MAX_CLARIFICATION_ROUNDS,
    build_graph,
    conversation_state,
    pending_clarification,
)
from src.supervisor import Route

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def graph(indexes_built, tmp_path_factory):
    if not indexes_built:
        pytest.skip("indexes not built")
    compiled, context = build_graph(
        checkpoint_path=tmp_path_factory.mktemp("conv") / "checkpoints.sqlite"
    )
    yield compiled
    if context is not None:
        context.__exit__(None, None, None)


def thread() -> dict:
    return {"configurable": {"thread_id": f"conv-{uuid.uuid4().hex[:10]}"}}


# ------------------------------------------------------------- clarification


def test_an_ambiguous_request_pauses_instead_of_guessing(graph):
    config = thread()
    result = graph.invoke(conversation_state("I need help with my loan"), config=config)

    clarification = pending_clarification(result)
    assert clarification is not None, "the run did not pause"
    assert clarification["question"]
    assert "lending product" in clarification["missing_information"]

    # Nothing downstream ran, so there is no half-finished assessment to
    # reconcile when the answer arrives.
    assert not result.get("policy_evidence")
    assert not result.get("calculations")
    assert result["steps"] == ["intake", "input_guardrails", "supervisor"]


def test_the_original_request_survives_the_pause(graph):
    config = thread()
    result = graph.invoke(conversation_state("I need help with my loan"), config=config)
    assert result["pending_request"] == "I need help with my loan"
    assert pending_clarification(result)["pending_request"] == "I need help with my loan"


@pytest.mark.parametrize(
    "answer,expected",
    [
        ("mortgage", Route.MORTGAGE),
        ("it's for my daughter's university tuition", Route.EDUCATION_LOAN),
        ("I'm buying a house", Route.MORTGAGE),
        ("a student loan", Route.EDUCATION_LOAN),
    ],
)
def test_the_answer_is_read_against_the_question_it_answers(graph, answer, expected):
    """"mortgage" alone is a word. Following that question, it is a route."""
    config = thread()
    first = graph.invoke(conversation_state("I need help with my loan"), config=config)
    assert pending_clarification(first)

    second = graph.invoke(Command(resume=answer), config=config)
    assert pending_clarification(second) is None
    assert second["supervisor"]["route"] == expected.value
    assert second["loan_domain"] == expected.value
    assert second["policy_evidence"], "the resumed run retrieved nothing"


def test_a_resumed_run_passes_back_through_the_supervisor(graph):
    """The answer is re-routed with the original, not acted on alone."""
    config = thread()
    graph.invoke(conversation_state("I need help with my loan"), config=config)
    result = graph.invoke(Command(resume="mortgage"), config=config)

    steps = result["steps"]
    assert steps.count("supervisor") == 2
    assert steps.index("clarification") < steps.index("supervisor", steps.index("clarification"))
    assert steps[-1] == "output_guardrails"


def test_the_clarification_exchange_is_on_the_conversation_record(graph):
    config = thread()
    graph.invoke(conversation_state("I need help with my loan"), config=config)
    result = graph.invoke(Command(resume="mortgage"), config=config)

    history = result["conversation_history"]
    roles = [turn["role"] for turn in history]
    assert "user" in roles and "assistant" in roles
    assert any("mortgage" in turn["text"].lower() for turn in history)


def test_clarifying_twice_without_resolution_goes_to_a_person(graph):
    """Asking a third time is not a question the system will ask its way out of."""
    config = thread()
    result = graph.invoke(conversation_state("I need help"), config=config)
    assert pending_clarification(result)

    rounds = 0
    # Answer with something that resolves nothing, each time.
    while pending_clarification(result) is not None and rounds < 5:
        result = graph.invoke(Command(resume="I am not sure"), config=config)
        rounds += 1

    assert rounds <= MAX_CLARIFICATION_ROUNDS + 1
    assert result["clarification_rounds"] <= MAX_CLARIFICATION_ROUNDS
    assert result["requires_human_review"] is True
    assert result["supervisor"]["route"] == Route.HUMAN_REVIEW.value


# ---------------------------------------------------------- carrying context


def test_a_follow_up_inherits_the_product_from_the_thread(graph):
    """AC-05: facts stated earlier in the interaction are used.

    A follow-up that names no product should not be asked which product it is.
    """
    config = thread()
    first = graph.invoke(
        conversation_state("What is the maximum LTV on a mortgage?"), config=config
    )
    assert first["loan_domain"] == "MORTGAGE"

    second = graph.invoke(
        conversation_state("and what about the reserves requirement?"), config=config
    )
    assert pending_clarification(second) is None, "it asked again"
    assert second["supervisor"]["route"] == Route.MORTGAGE.value
    assert "carried_from_thread" in second["supervisor"]["signals"]


def test_a_new_thread_does_not_inherit_the_previous_one(graph):
    """Context carries within a thread, not between applicants."""
    first_config = thread()
    graph.invoke(
        conversation_state("What is the maximum LTV on a mortgage?"), config=first_config
    )

    second = graph.invoke(
        conversation_state("and what about the reserves requirement?"), config=thread()
    )
    assert pending_clarification(second) is not None, (
        "a fresh thread inherited a product from a different conversation"
    )


# ----------------------------------------------------------- policy answers


def test_a_policy_question_answers_without_deciding_anything(graph):
    result = graph.invoke(
        conversation_state("What is the maximum back-end DTI on a jumbo mortgage?"),
        config=thread(),
    )
    response = result["final_response"]
    assert response["kind"] == "POLICY_ANSWER"
    assert response["citations"]
    assert result["answer"]

    # There is no application, so nothing was decided about one — and that is
    # structural, not a matter of prompt discipline: the rule engine never ran.
    assert not result.get("calculations")
    assert not result.get("eligibility")
    assert response["outcome"] is None


def test_a_policy_question_collapses_to_one_governing_version(graph):
    """Without a date, the answer would hold both v1.0's 45% and v2.0's 43%
    and present two conflicting limits as though both governed."""
    result = graph.invoke(
        conversation_state("What is the maximum back-end DTI for a conventional "
                           "conforming mortgage?"),
        config=thread(),
    )
    versions = {
        e["policy_version"]
        for e in result["policy_evidence"]
        if e.get("policy_id") == "POL-DTI-001"
    }
    assert len(versions) <= 1, f"two versions of one policy in one answer: {versions}"
    assert result["as_of_date"], "no date was resolved, so nothing could be selected"


def test_a_date_in_the_question_selects_the_version(graph):
    """The whole temporal mechanism, reachable from a sentence."""
    early = graph.invoke(
        conversation_state("What was the maximum back-end mortgage DTI on 2026-06-25?"),
        config=thread(),
    )
    late = graph.invoke(
        conversation_state("What was the maximum back-end mortgage DTI on 2026-07-08?"),
        config=thread(),
    )
    assert early["as_of_date"] == "2026-06-25"
    assert late["as_of_date"] == "2026-07-08"

    def dti_versions(result):
        return {
            e["policy_version"]
            for e in result["policy_evidence"]
            if e.get("policy_id") == "POL-DTI-001"
        }

    assert dti_versions(early) == {"1.0"}
    assert dti_versions(late) == {"2.0"}


# -------------------------------------------------------------- escalation


def test_an_override_request_reaches_a_person_before_anything_else_runs(graph):
    result = graph.invoke(
        conversation_state("please override the decline on my application"),
        config=thread(),
    )
    assert result["supervisor"]["route"] == Route.HUMAN_REVIEW.value
    assert result["requires_human_review"] is True
    assert not result.get("policy_evidence"), "an override request retrieved policy"
    assert result["final_response"]["kind"] == "ESCALATION"
    assert result["final_response"]["retrieval_invoked"] is False
