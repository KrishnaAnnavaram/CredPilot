"""The CredPilot LangGraph.

Typed state, a conversational Supervisor, two structurally isolated product
workflows, a Final Response Agent, guardrails on both edges of the I/O path, a
SQLite checkpointer and structured output at every node boundary.

::

                              intake
                                 |
                          input_guardrails
                                 |
                            SUPERVISOR
                                 |
       +--------+--------+-------+--------+-----------+-----------+
       |        |        |                |           |           |
    GENERAL  CLARIFY  MORTGAGE      EDUCATION_LOAN  HUMAN_    OUT_OF_
       |        |        |                |         REVIEW     SCOPE
       |    interrupt    |                |           |           |
       |        |    mortgage_agent   education_agent |           |
       |    (user reply) |                |           |           |
       |        |    mortgage_        education_      |           |
       |        |    policy_retrieval policy_retrieval|           |
       |   SUPERVISOR    |                |           |           |
       |             mortgage_        education_      |           |
       |             eligibility      eligibility     |           |
       |                 |                |           |           |
       |             mortgage_risk    education_risk  |           |
       |                 |                |           |           |
       |             mortgage_        education_      |           |
       |             recommendation   recommendation  |           |
       |                 |                |           |           |
       |                 +-----+ narrative +          |           |
       |                            |                 |           |
       +----------------------------+-----------------+-----------+
                                    |
                            final_response
                                    |
                            output_guardrails
                                    |
                                   END

Four rules the graph exists to enforce:

* **Nothing reaches retrieval before the Supervisor has looked at it.** A
  greeting is answered by the Supervisor and never touches the policy corpus. An
  ambiguous request is clarified, not guessed at.
* **Product isolation is topological, not conditional.** There is no edge from
  any mortgage node to any education node. The two chains share implementations
  and share no state transition, so a mortgage file cannot reach education
  retrieval through any sequence of routing decisions — which a shared worker
  node guarded by an ``if`` cannot claim.
* **The model never does the arithmetic.** DTI, LTV, reserves and cash-to-close
  come from :mod:`src.calculations`; Gemini may explain a computed figure, never
  produce one (``POL-DTI-001`` rule ``DTI-CALC-002``).
* **Retrieval-in-the-loop, not up-front.** Each product's retrieval node decides
  which policy questions the file actually raises and issues one targeted
  retrieval per question, then follows the rules that evidence points at. The
  whole corpus never enters a prompt.
"""

from __future__ import annotations

import operator
import re
import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Annotated, Any, Literal, Mapping, Sequence, TypedDict

from src.config import REPO_ROOT, RagConfig, get_config
from src.application_context import build_underwriting_input
from src.domain import (
    LendingProductDomain,
    ProductResolutionError,
    resolve_product_domain,
)
from src.guardrails.sanitize import quarantine
from src.guardrails.validation import CONTRADICTION_TERMS, validate_response
from src.observability.tool_logging import log_agent_action
from src.observability.tracing import (
    SPAN_CLARIFICATION,
    SPAN_EDUCATION_AGENT,
    SPAN_ELIGIBILITY,
    SPAN_FINAL_RESPONSE,
    SPAN_HUMAN_REVIEW,
    SPAN_INPUT_GUARDRAILS,
    SPAN_INTAKE,
    SPAN_MORTGAGE_AGENT,
    SPAN_OUTPUT_GUARDRAILS,
    SPAN_RECOMMENDATION,
    SPAN_RISK,
    SPAN_SUPERVISOR,
    span,
)
from src.rag.models import PolicyEvidence, RetrievalStatus
from src.rag.pipeline import PolicyRetriever
from src.supervisor import Route, SupervisorDecision, classify, general_answer
from src.tools.rag_tool import retrieve_policy_tool

CHECKPOINT_DB = REPO_ROOT / "data" / "memory" / "credpilot_checkpoints.sqlite"


# ======================================================================================
# Typed state
# ======================================================================================


class CredPilotState(TypedDict, total=False):
    """The graph's typed state.

    ``policy_evidence`` accumulates across retrieval turns rather than being
    overwritten, so the final recommendation can cite every rule the run relied
    on, not only the ones from the last question asked.

    Evidence is held as plain dictionaries rather than as ``PolicyEvidence``
    models. State crosses the checkpointer, and a checkpoint that can only be
    read back by code holding the originating Python class is not a durable
    record — ``evidence_to_state`` converts on the way in and
    :func:`state_evidence` reads it back.
    """

    # intake
    application_id: str
    application_packet: dict[str, Any]
    as_of_date: str
    untrusted_applicant_text: dict[str, Any] | None
    #: The user's utterance. Present on the conversational path, absent when an
    #: application packet is submitted directly.
    message: str
    #: Prior turns on this thread, for the Supervisor's product carry-forward.
    conversation_history: Annotated[list[dict[str, Any]], operator.add]

    # supervisor
    supervisor: dict[str, Any]
    loan_domain: str | None
    route: str
    routing_reason: str
    workflow_mode: str
    as_of_date_source: str
    #: Set when the Supervisor asked for clarification; cleared once answered.
    clarification_question: str | None
    clarification_answer: str | None
    clarification_rounds: Annotated[int, operator.add]
    #: What was asked before clarification, so the two can be recombined.
    pending_request: str | None

    # guardrails
    input_guardrail: dict[str, Any]
    output_guardrail: dict[str, Any]

    # worker output
    policy_questions: list[dict[str, Any]]
    policy_dependencies: list[str]
    required_rules_fetched: list[str]
    policy_evidence: Annotated[list[dict[str, Any]], operator.add]
    retrieval_statuses: Annotated[list[str], operator.add]
    calculations: dict[str, Any]
    eligibility: dict[str, Any]
    risk: dict[str, Any]
    recommendation: dict[str, Any]
    narrative: dict[str, Any]
    context_record: dict[str, Any]

    # response
    final_response: dict[str, Any]
    answer: str

    # memory
    session_id: str
    subject_id: str | None
    recalled_memory: list[dict[str, Any]]
    memory_written: list[str]
    conversation: dict[str, Any]

    # control
    step_budget: int
    steps_taken: Annotated[int, operator.add]
    halted: bool
    requires_human_review: bool
    human_review_reasons: Annotated[list[str], operator.add]
    security_findings: Annotated[list[str], operator.add]
    errors: Annotated[list[str], operator.add]
    steps: Annotated[list[str], operator.add]
    degradations: Annotated[list[dict[str, Any]], operator.add]


#: What the product workflow is being asked to do on this turn.
MODE_ASSESSMENT = "ASSESSMENT"
MODE_POLICY_QUESTION = "POLICY_QUESTION"


# ======================================================================================
# The policy questions each product's worker asks
# ======================================================================================

#: Retrieval-in-the-loop: one targeted question per underwriting concern the file
#: raises, asked only when the packet shows the concern is live.
MORTGAGE_QUESTIONS: tuple[dict[str, Any], ...] = (
    {"topic": "affordability", "query": "What is the maximum back-end debt-to-income ratio, and how is it calculated?"},
    {"topic": "leverage", "query": "What are the maximum loan-to-value limits for this transaction?"},
    {"topic": "credit", "query": "What minimum representative credit score is required?"},
    {"topic": "reserves", "query": "How many months of post-closing reserves are required?"},
    {"topic": "funds_to_close", "query": "How are funds to close calculated and tested for sufficiency?"},
    {"topic": "documentation", "query": "Which documents are required and how fresh must they be?"},
    {"topic": "decisioning", "query": "What outputs may be produced and when must a human review the file?"},
)

# Topics for employment continuity, credit events, delinquency, valuation, asset
# sourcing and programme limits are deliberately *not* in that list. Each was
# there briefly and each was removed: the required-rule pass below fetches those
# rules by id with ``top_k=3``, which lands the exact rule the engine needs, and
# a broad topic query for the same family costs a full funnel — embedding, BM25,
# fusion, cross-encoder rerank — to land the same chunk less reliably. Keeping
# both tripled a mortgage assessment's latency for no additional evidence.

_MORTGAGE_CONDITIONAL: tuple[tuple[str, dict[str, Any]], ...] = (
    ("self_employed", {"topic": "income_self_employed", "query": "How is income qualified for a self-employed borrower?"}),
    ("variable_income", {"topic": "income_variable", "query": "How much history is required before bonus, overtime or commission income can be used?"}),
    ("rental_income", {"topic": "income_rental", "query": "How is rental income qualified, and what vacancy factor applies?"}),
    ("cash_out", {"topic": "cash_out", "query": "What ownership seasoning and leverage limits apply to a cash-out refinance?"}),
    ("jumbo", {"topic": "jumbo", "query": "What additional conditions apply to a jumbo transaction?"}),
    ("untrusted_text", {"topic": "security", "query": "How must applicant-supplied text be treated?"}),
)

EDUCATION_QUESTIONS: tuple[dict[str, Any], ...] = (
    {"topic": "product_underwriting", "query": "What are the underwriting criteria for this education loan product?"},
    {"topic": "cosigner", "query": "When is a cosigner required, and what must the cosigner qualify on?"},
    {"topic": "capacity", "query": "What is the maximum debt-to-income, and what residual income is required?"},
    {"topic": "school", "query": "What school eligibility and certification requirements apply before disbursement?"},
    {"topic": "risk_grade", "query": "How is the risk grade assigned and how does it set pricing?"},
    {"topic": "fraud", "query": "What identity, sanctions and fraud screening is required?"},
    {"topic": "compliance", "query": "What adverse action and disclosure obligations apply to this decision?"},
)

_EDUCATION_CONDITIONAL: tuple[tuple[str, dict[str, Any]], ...] = (
    ("international", {"topic": "international", "query": "What visa, immigration document and sponsorship requirements apply to an international student?"}),
    ("refinance", {"topic": "refinance", "query": "What is required for education-loan refinancing?"}),
    ("untrusted_text", {"topic": "security", "query": "May an automated system grant its own exception to policy?"}),
)


def evidence_to_state(evidence: Sequence[PolicyEvidence]) -> list[dict[str, Any]]:
    """Convert retrieval evidence into checkpoint-safe plain dictionaries."""
    return [e.model_dump(mode="json") for e in evidence]


def state_evidence(state: Mapping[str, Any]) -> list[dict[str, Any]]:
    """The evidence dictionaries accumulated on the state."""
    return list(state.get("policy_evidence") or [])


#: Rule identifiers as the two corpora spell them. Used to find the rules a
#: retrieved rule depends on.
_RULE_REFERENCE = re.compile(
    r"(?<![A-Z0-9-])(EDU-[A-Z]+-[0-9]+)(?![A-Z0-9-])"
    r"|(?<![A-Z0-9-])([A-Z]{2,6}-[A-Z]{2,6}-[0-9]{3})(?![A-Z0-9-])"
)

#: A cap on dependency following. One round, a handful of rules: enough to close
#: a "see also" reference, not enough to walk the whole corpus.
MAX_DEPENDENCY_FOLLOWS = 6

#: The rules the deterministic engine will try to apply, per product.
#:
#: Topic retrieval asks what a file *raises*; this says what the engine *needs*.
#: They are not the same question, and the gap between them was costing correct
#: answers: a file with a perfectly fresh document set was referred because
#: ``DOC-REQ-002`` — the rule that defines "fresh" — never ranked into the top
#: results for "which documents are required and how fresh must they be", so the
#: engine had no window to measure against and reported INDETERMINATE.
#:
#: Referring a file for want of a rule that exists, is indexed, and was one
#: targeted query away is the worst of the three outcomes: it is not a wrong
#: answer, it is a refusal to answer caused by the system's own retrieval
#: ranking. So after the topic pass, any rule on this list that is not already
#: in evidence is fetched by id.
#:
#: This list is derived from the engine, not from the corpus. A rule here that
#: the engine does not evaluate is wasted retrieval, and a rule the engine
#: evaluates that is missing here is a family that will keep reporting
#: INDETERMINATE — ``tests/test_rule_coverage.py`` checks the two agree.
REQUIRED_RULES: dict[str, tuple[str, ...]] = {
    "MORTGAGE": (
        "DTI-CONV-001", "DTI-CONV-003",
        "CRD-SCR-001", "CRD-SCR-003",
        "AST-RSV-001", "AST-RSV-002",
        "AST-FTC-001", "AST-FTC-003",
        "GEN-ELG-003", "GEN-ELG-006",
        "DOC-REQ-001", "DOC-REQ-002",
        "EMP-CNT-001", "EMP-CNT-004",
        "CRD-EVT-001", "CRD-DLQ-001", "CRD-DLQ-002",
        "AST-SRC-002",
        "VAL-APR-002", "VAL-APR-003",
        "UWR-HRV-001",
    ),
    "EDUCATION_LOAN": (
        "EDU-INC-003", "EDU-INC-004",
        "EDU-SCH-005",
        "EDU-UW-001", "EDU-UW-002", "EDU-UW-003", "EDU-UW-004", "EDU-UW-005",
        "EDU-COS-001", "EDU-COS-002", "EDU-COS-003",
        "EDU-INTL-001", "EDU-INTL-003", "EDU-INTL-004", "EDU-INTL-005",
        "EDU-RG-001",
    ),
}

#: Rules fetched by id only when the file is of the product variant that needs
#: them. Fetching every EDU-UW rule for every education file would spend five
#: retrievals to use one, and fetching the jumbo overlay for a conforming loan
#: would put rules in evidence that do not govern it — which the narrative would
#: then be free to cite.
_CONDITIONAL_REQUIRED_RULES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("MORTGAGE", "jumbo", ("JMB-ELG-002", "JMB-ELG-003", "JMB-ELG-004")),
    ("EDUCATION_LOAN", "INTL", ("EDU-INTL-001", "EDU-INTL-003", "EDU-INTL-004",
                                "EDU-INTL-005")),
)

#: How many rules the required-rule pass may fetch by id in one run. A normal
#: file is missing two or three after the topic pass; this is the ceiling that
#: stops a retrieval regression turning into twenty extra round trips.
MAX_REQUIRED_RULE_FETCHES = 14

#: How many node executions one request may use. A correct assessment visits
#: eleven nodes — intake, guardrails, supervisor, the five product nodes,
#: narrative, final response, output guardrails — and a clarified one visits
#: three more on the way back through the Supervisor. The budget leaves room for
#: two rounds of clarification without tripping.
#:
#: Two independent guards, because they fail differently:
#:   * this budget is *inside* the state, so a node can see it running out and
#:     halt cleanly with a reason a human can read;
#:   * LangGraph's own ``recursion_limit`` is *outside* and raises
#:     ``GraphRecursionError`` — the backstop for a cycle that never reaches a
#:     node able to check anything.
#: A runaway loop in an underwriting system is not a performance problem; it is
#: an unbounded spend against an applicant's file with no decision at the end.
DEFAULT_STEP_BUDGET = 32
RECURSION_LIMIT = 60

#: How many times one thread may be sent back for clarification before it goes
#: to a person instead. Two rounds of "which product is this?" that both fail to
#: land is not a question the system is going to ask its way out of.
MAX_CLARIFICATION_ROUNDS = 2


def budget_exhausted(state: Mapping[str, Any]) -> bool:
    """Whether this run has used its step budget."""
    budget = int(state.get("step_budget") or DEFAULT_STEP_BUDGET)
    return int(state.get("steps_taken") or 0) >= budget


def _guard(state: Mapping[str, Any], node: str) -> dict[str, Any] | None:
    """Halt the run if the budget is spent.

    Returned as an ordinary state update rather than an exception: a file that
    ran out of budget still needs a recommendation a human can act on, and
    "halted after N steps" is that, where a traceback is not.
    """
    if not budget_exhausted(state):
        return None
    return {
        "halted": True,
        "route": "human_review",
        "requires_human_review": True,
        "human_review_reasons": [
            f"the assessment halted at {node} after "
            f"{state.get('steps_taken')} steps, its budget of "
            f"{state.get('step_budget') or DEFAULT_STEP_BUDGET}; no decision was reached"
        ],
        "steps": [f"{node}:halted"],
        "steps_taken": 1,
    }


def referenced_rules(evidence: Sequence[Mapping[str, Any]]) -> list[str]:
    """Rule ids that retrieved evidence points at but does not contain.

    A rule that says "at least two compensating factors from DTI-CONV-003"
    cannot be applied without DTI-CONV-003. Following that reference is what
    retrieval-in-the-loop means here: the first answer raises a question, and the
    agent asks it rather than deciding without it.
    """
    held = {e.get("rule_id") for e in evidence if e.get("rule_id")}
    referenced: list[str] = []
    for item in evidence:
        for education, mortgage in _RULE_REFERENCE.findall(item.get("text") or ""):
            rule_id = education or mortgage
            # POL-xxx is a policy document, not a rule; it matches the same shape
            # but there is no rule by that name to fetch.
            if rule_id.startswith("POL-"):
                continue
            if rule_id and rule_id not in held and rule_id not in referenced:
                referenced.append(rule_id)
    return referenced


def subject_of(packet: Mapping[str, Any]) -> str | None:
    """The party long-term memory is keyed on.

    The primary borrower, not the application: an applicant who comes back with
    a second file is the same person, and "recalls prior-session context on a
    return visit" only means anything if the key survives the application id.
    """
    borrowers = packet.get("borrowers")
    if isinstance(borrowers, list) and borrowers:
        first = borrowers[0]
        if isinstance(first, Mapping) and first.get("borrower_id"):
            return str(first["borrower_id"])
    borrower = packet.get("borrower")
    if isinstance(borrower, Mapping) and borrower.get("borrower_id"):
        return str(borrower["borrower_id"])
    return None


def _mortgage_flags(packet: dict[str, Any]) -> set[str]:
    flags: set[str] = set()
    kinds = {str(i.get("income_type", "")).lower() for i in packet.get("declared_income") or []}
    if any("self" in k for k in kinds):
        flags.add("self_employed")
    if kinds & {"bonus", "overtime", "commission", "tip", "variable"}:
        flags.add("variable_income")
    if any("rent" in k for k in kinds):
        flags.add("rental_income")
    if packet.get("loan_purpose") == "cash_out_refinance":
        flags.add("cash_out")
    if packet.get("product_family") == "jumbo":
        flags.add("jumbo")
    if packet.get("untrusted_applicant_text"):
        flags.add("untrusted_text")
    return flags


def _education_flags(packet: dict[str, Any]) -> set[str]:
    flags: set[str] = set()
    code = str(packet.get("product_code", "")).upper()
    if code == "INTL" or packet.get("international_details"):
        flags.add("international")
    if code == "REFI":
        flags.add("refinance")
    if packet.get("untrusted_applicant_text"):
        flags.add("untrusted_text")
    return flags


def plan_policy_questions(
    domain: LendingProductDomain, packet: dict[str, Any]
) -> list[dict[str, Any]]:
    """Decide which policy questions this file actually raises."""
    if domain is LendingProductDomain.MORTGAGE:
        base, conditional, flags = MORTGAGE_QUESTIONS, _MORTGAGE_CONDITIONAL, _mortgage_flags(packet)
    else:
        base, conditional, flags = EDUCATION_QUESTIONS, _EDUCATION_CONDITIONAL, _education_flags(packet)
    questions = list(base)
    questions.extend(q for flag, q in conditional if flag in flags)
    return questions


# ======================================================================================
# Memory
# ======================================================================================


def recall_prior_context(subject_id: str | None) -> list[dict[str, Any]]:
    """Prior-session context for this party, if any (AC-05).

    Best-effort by design. Memory enriches an assessment; it never gates one, so
    a missing or unreadable store leaves the file assessable on policy and the
    packet alone. What comes back is context — outstanding documents, a stated
    preference — never a decision or a threshold: :mod:`src.memory.long_term`
    refuses to store those in the first place.
    """
    if not subject_id:
        return []
    try:
        from src.memory import LongTermMemory

        return [r.as_dict() for r in LongTermMemory().recall(subject_id, limit=10)]
    except Exception:  # noqa: BLE001 - memory must never block an assessment
        return []


def record_interaction(state: Mapping[str, Any]) -> list[str]:
    """Write what a returning applicant would want us to remember.

    Best-effort, and deliberately incurious: an assessment happened, these policy
    topics were examined, these documents were outstanding. No outcome, no
    threshold, no figure — :mod:`src.memory.long_term` refuses those by kind, and
    this is the caller that would otherwise be tempted.

    A memory failure must never fail a file, so everything here is swallowed. The
    ids written are returned for the state record.
    """
    subject = state.get("subject_id")
    if not subject:
        return []

    try:
        from src.memory import LongTermMemory

        memory = LongTermMemory()
        session = str(state.get("session_id") or "")
        written: list[str] = []

        topics = sorted({
            str(q.get("topic")) for q in (state.get("policy_questions") or []) if q.get("topic")
        })
        if topics:
            memory.remember(
                subject_id=subject,
                kind="interaction",
                key="last-assessment",
                content=(
                    f"An underwriting assessment was run on "
                    f"{state.get('as_of_date')} for a "
                    f"{state.get('loan_domain')} application. Policy topics examined: "
                    f"{', '.join(topics)}."
                ),
                metadata={"application_id": state.get("application_id")},
                session_id=session,
                embed=False,
            )
            written.append("last-assessment")

        # Anything the engine could not settle for want of evidence is exactly
        # what the applicant should be asked for next time.
        outstanding = [
            str(item.get("detail", ""))
            for item in ((state.get("eligibility") or {}).get("indeterminate") or [])
        ]
        if outstanding:
            memory.remember(
                subject_id=subject,
                kind="document_status",
                key="outstanding-at-last-assessment",
                content="Outstanding when last assessed: " + "; ".join(outstanding),
                session_id=session,
                embed=False,
            )
            written.append("outstanding-at-last-assessment")

        return written
    except Exception:  # noqa: BLE001 - memory must never fail an assessment
        return []


# ======================================================================================
# Intake and input guardrails
# ======================================================================================


def intake_node(state: CredPilotState) -> dict[str, Any]:
    """Application intake: establish the subject and recall what is known.

    Deliberately does no classification and no security work. Intake's job is to
    say *who this is about* so memory can be recalled and the audit trail has a
    subject; deciding whether the request is safe is the guardrails' job and
    deciding where it goes is the Supervisor's.
    """
    halt = _guard(state, "intake")
    if halt is not None:
        return halt

    packet = state.get("application_packet") or {}
    subject = subject_of(packet)
    recalled = recall_prior_context(subject)
    message = str(state.get("message") or "").strip()

    with span(
        SPAN_INTAKE,
        application_id=state.get("application_id") or "",
        has_packet=bool(packet),
        has_message=bool(message),
        recalled_memories=len(recalled),
    ):
        log_agent_action(
            actor="intake",
            action="receive_request",
            decision="ACCEPTED",
            application_id=state.get("application_id"),
            detail={
                "has_application_packet": bool(packet),
                "has_message": bool(message),
                "subject_id": subject,
                "recalled_memories": len(recalled),
            },
        )

    update: dict[str, Any] = {
        "subject_id": subject,
        "recalled_memory": recalled,
        "steps": ["intake"],
        "steps_taken": 1,
        "route": "input_guardrails",
    }
    if message:
        update["conversation_history"] = [
            {
                "role": "user",
                "text": message[:2000],
                "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
        ]
    return update


def input_guardrails_node(state: CredPilotState) -> dict[str, Any]:
    """Input guardrails: quarantine untrusted text, sanitize the user's message.

    Two untrusted surfaces, handled the same way and kept apart from each other:

    * ``untrusted_applicant_text`` on the packet — a letter of explanation, a
      free-text note. It is quarantined into its own compartment and never
      becomes an instruction.
    * the user's own message on the conversational path. It is scanned for the
      same injection patterns, and a message that tries to change policy,
      thresholds or data access is flagged and the turn routed to a person.

    A finding here does not stop the assessment. The file is still underwritten
    on its structured facts — the attack moved neither the product nor the date —
    and it is the *routing* that changes: the result goes to a human.
    """
    halt = _guard(state, "input_guardrails")
    if halt is not None:
        return halt

    packet = state.get("application_packet") or {}
    untrusted = packet.get("untrusted_applicant_text")
    message = str(state.get("message") or "")

    quarantined = None
    findings: list[str] = []
    review_reasons: list[str] = []

    if untrusted:
        content = untrusted.get("content") if isinstance(untrusted, dict) else str(untrusted)
        quarantined = quarantine(content)
        findings.extend(quarantined["injection_findings"])
        if quarantined["requires_human_review"]:
            review_reasons.append(
                "applicant-supplied text attempted to alter policy, thresholds or "
                "data access (POL-SEC-001 SEC-INJ-001)"
            )

    message_scan: dict[str, Any] = {}
    if message:
        scanned = quarantine(message)
        message_scan = {
            "injection_findings": list(scanned["injection_findings"]),
            "requires_human_review": bool(scanned["requires_human_review"]),
        }
        findings.extend(scanned["injection_findings"])
        if scanned["requires_human_review"]:
            review_reasons.append(
                "the request itself attempted to alter policy, thresholds or data "
                "access (POL-SEC-001 SEC-INJ-001); it is answered by a person, not "
                "by the system it tried to steer"
            )

    with span(
        SPAN_INPUT_GUARDRAILS,
        application_id=state.get("application_id") or "",
        findings=len(findings),
        scanned_packet_text=bool(untrusted),
        scanned_message=bool(message),
    ):
        if findings:
            log_agent_action(
                actor="input_guardrails",
                action="scan_untrusted_input",
                decision="INJECTION_DETECTED",
                application_id=state.get("application_id"),
                detail={"findings": sorted(set(findings))[:12]},
            )

    update: dict[str, Any] = {
        "untrusted_applicant_text": quarantined,
        "security_findings": findings,
        "input_guardrail": {
            "packet_text_quarantined": bool(quarantined),
            "message_scanned": bool(message),
            "message_scan": message_scan,
            "finding_count": len(findings),
            "findings": sorted(set(findings))[:12],
        },
        "steps": ["input_guardrails"],
        "steps_taken": 1,
        "route": "supervisor",
    }
    if review_reasons:
        update["requires_human_review"] = True
        update["human_review_reasons"] = review_reasons
    return update


# ======================================================================================
# Supervisor
# ======================================================================================


def supervisor_node(state: CredPilotState) -> dict[str, Any]:
    """The Supervisor Agent: understand the request and route it.

    Produces one :class:`~src.supervisor.SupervisorDecision` and nothing else. It
    does not retrieve, compute or decide. On a thread that has already been
    clarified, the pending request and the user's answer are combined before
    classification, so "mortgage" is read as the answer to the question that was
    asked rather than as a one-word utterance.
    """
    halt = _guard(state, "supervisor")
    if halt is not None:
        return halt

    packet = state.get("application_packet") or {}
    message = str(state.get("message") or "")
    pending = state.get("pending_request")
    answer = state.get("clarification_answer")
    rounds = int(state.get("clarification_rounds") or 0)

    # After a clarification the reply is the message and the original question is
    # the context they answer against.
    if answer:
        message = str(answer)

    prior_domain = _prior_domain(state)

    decision = classify(
        message,
        application_packet=packet or None,
        application_id=state.get("application_id") or None,
        explicit_domain=state.get("loan_domain"),
        prior_domain=prior_domain,
        clarification_context=str(pending) if pending else None,
        use_model=_model_routing_enabled(),
    )

    # A message that tried to steer the system is not routed by what it claimed
    # to want — it goes straight to a person.
    #
    # An *application* carrying adversarial text is a different case and must
    # not be handled the same way. The file is still underwritten: the attack
    # moved neither the product nor the as-of date, and refusing to assess it
    # would let a hostile letter of explanation stop an applicant's file from
    # being read at all. What changes is where the result goes, and
    # ``requires_human_review`` is already set by the guardrail node and carried
    # to the end.
    message_attack = bool(
        ((state.get("input_guardrail") or {}).get("message_scan") or {})
        .get("requires_human_review")
    )
    if message_attack and not packet:
        decision = SupervisorDecision.from_dict({
            **decision.as_dict(),
            "route": Route.HUMAN_REVIEW.value,
            "routing_reason": (
                "an input guardrail fired on the request itself; it is answered by "
                "a person, not by the system it tried to steer"
            ),
            "clarification_required": False,
            "clarification_question": None,
        })

    # Clarifying twice and still not knowing is not a question worth asking a
    # third time.
    if decision.route is Route.CLARIFY and rounds >= MAX_CLARIFICATION_ROUNDS:
        decision = SupervisorDecision.from_dict({
            **decision.as_dict(),
            "route": Route.HUMAN_REVIEW.value,
            "clarification_required": False,
            "routing_reason": (
                f"the request was still unresolved after {rounds} clarification "
                f"round(s); a person takes it from here rather than the system "
                f"asking again"
            ),
        })

    with span(
        SPAN_SUPERVISOR,
        route=decision.route.value,
        intent=decision.intent,
        conversation_type=decision.conversation_type.value,
        domain=decision.domain.value if decision.domain else "",
        confidence=decision.confidence,
        decided_by=decision.decided_by,
        clarification_round=rounds,
    ):
        log_agent_action(
            actor="supervisor",
            action="route_request",
            decision=decision.route.value,
            application_id=state.get("application_id"),
            product_domain=decision.domain.value if decision.domain else None,
            detail={
                "intent": decision.intent,
                "confidence": decision.confidence,
                "decided_by": decision.decided_by,
                "routing_reason": decision.routing_reason,
                "clarification_required": decision.clarification_required,
                "signals": decision.signals[:6],
            },
        )

    update: dict[str, Any] = {
        "supervisor": decision.as_dict(),
        "route": decision.route.value,
        "routing_reason": decision.routing_reason,
        "steps": ["supervisor"],
        "steps_taken": 1,
    }
    if decision.domain is not None:
        update["loan_domain"] = decision.domain.value
    if decision.route is Route.CLARIFY:
        update["clarification_question"] = decision.clarification_question
        update["pending_request"] = decision.normalized_question
    else:
        update["clarification_question"] = None
        update["pending_request"] = None
    if decision.route is Route.HUMAN_REVIEW:
        update["requires_human_review"] = True
        update["human_review_reasons"] = [decision.routing_reason]
    return update


def _prior_domain(state: Mapping[str, Any]) -> str | None:
    """The product this thread was already scoped to, if any."""
    existing = state.get("loan_domain")
    if existing:
        return str(existing)
    prior = (state.get("supervisor") or {}).get("domain")
    return str(prior) if prior else None


def _model_routing_enabled() -> bool:
    """Whether the Supervisor may fall through to Gemini for ambiguous turns.

    Off by default. Unit tests must not spend model tokens, and a checkout with
    no key must route identically to one with a key; the deterministic pass is
    the contract and the model is an opt-in improvement on its ambiguous middle.
    """
    import os

    return os.environ.get("CREDPILOT_SUPERVISOR_MODEL", "").strip().lower() in (
        "1", "true", "yes", "on",
    )


def general_response_node(state: CredPilotState) -> dict[str, Any]:
    """Answer a social or capability turn directly. No retrieval happens here.

    This node has no path to any retrieval node, which is how "a greeting does
    not invoke RAG" is guaranteed rather than intended.
    """
    halt = _guard(state, "general_response")
    if halt is not None:
        return halt

    decision = SupervisorDecision.from_dict(state.get("supervisor") or {})
    text = general_answer(decision)

    log_agent_action(
        actor="general_response_agent",
        action="answer_directly",
        decision=decision.conversation_type.value,
        detail={"retrieval_invoked": False, "model_invoked": False},
    )
    return {
        "answer": text,
        "final_response": {
            "kind": "GENERAL",
            "conversation_type": decision.conversation_type.value,
            "text": text,
            "retrieval_invoked": False,
            "citations": [],
        },
        "steps": ["general_response"],
        "steps_taken": 1,
        "route": "final_response",
    }


def clarification_node(state: CredPilotState) -> dict[str, Any]:
    """Ask the clarifying question and pause the run until it is answered.

    ``interrupt()`` suspends the graph at this node with the checkpoint intact.
    The original request stays on the thread, so when the caller resumes with
    ``Command(resume=<answer>)`` the Supervisor sees both and routes the pair.
    Nothing is guessed while the run is suspended, and nothing downstream has
    run, so there is no partial assessment to reconcile.
    """
    halt = _guard(state, "clarification")
    if halt is not None:
        return halt

    from langgraph.types import interrupt

    question = state.get("clarification_question") or (
        "Could you tell me a little more about what you need?"
    )
    decision = state.get("supervisor") or {}

    with span(
        SPAN_CLARIFICATION,
        round=int(state.get("clarification_rounds") or 0) + 1,
        missing=",".join(decision.get("missing_information") or []),
    ):
        log_agent_action(
            actor="supervisor",
            action="request_clarification",
            decision="CLARIFICATION_REQUIRED",
            application_id=state.get("application_id"),
            detail={
                "question": question,
                "missing_information": decision.get("missing_information") or [],
                "round": int(state.get("clarification_rounds") or 0) + 1,
            },
        )

    answer = interrupt(
        {
            "kind": "clarification",
            "question": question,
            "missing_information": decision.get("missing_information") or [],
            "pending_request": state.get("pending_request"),
        }
    )

    return {
        "clarification_answer": str(answer) if answer is not None else "",
        "clarification_rounds": 1,
        "conversation_history": [
            {
                "role": "assistant",
                "text": question,
                "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            },
            {
                "role": "user",
                "text": str(answer)[:2000] if answer is not None else "",
                "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            },
        ],
        "steps": ["clarification"],
        "steps_taken": 1,
        "route": "supervisor",
    }


def safe_response_node(state: CredPilotState) -> dict[str, Any]:
    """Answer an out-of-scope request with a boundary rather than a guess."""
    halt = _guard(state, "safe_response")
    if halt is not None:
        return halt

    from src.supervisor import OUT_OF_SCOPE_RESPONSE

    log_agent_action(
        actor="supervisor",
        action="refuse_out_of_scope",
        decision="OUT_OF_SCOPE",
        detail={"reason": state.get("routing_reason")},
    )
    return {
        "answer": OUT_OF_SCOPE_RESPONSE,
        "final_response": {
            "kind": "OUT_OF_SCOPE",
            "text": OUT_OF_SCOPE_RESPONSE,
            "retrieval_invoked": False,
            "citations": [],
        },
        "steps": ["safe_response"],
        "steps_taken": 1,
        "route": "final_response",
    }


# ======================================================================================
# Product specialists — one chain per product, sharing no node
# ======================================================================================


def make_domain_agent_node(domain: LendingProductDomain):
    """Build a product specialist's entry node.

    It pins the product for everything downstream and decides what the chain is
    being asked for: a full assessment when a packet is present, a policy
    question when one is not. Two nodes are generated from this factory and they
    share no state transition — see the module docstring on topological
    isolation.
    """
    span_name = (
        SPAN_MORTGAGE_AGENT if domain is LendingProductDomain.MORTGAGE
        else SPAN_EDUCATION_AGENT
    )
    node_name = f"{domain.corpus_key}_agent"

    def domain_agent_node(state: CredPilotState) -> dict[str, Any]:
        halt = _guard(state, node_name)
        if halt is not None:
            return halt

        packet = state.get("application_packet") or {}

        # The product is resolved from structured facts wherever they exist. The
        # Supervisor's reading of free text is a routing signal, never the last
        # word on which corpus is searched.
        resolved = domain
        reason = f"the {domain.value} specialist owns this request"
        if packet or state.get("application_id"):
            try:
                resolved = resolve_product_domain(
                    application_id=state.get("application_id"),
                    packet=packet or None,
                )
            except ProductResolutionError as exc:
                log_agent_action(
                    actor=node_name,
                    action="resolve_product_domain",
                    decision=RetrievalStatus.PRODUCT_CLARIFICATION_REQUIRED.value,
                    application_id=state.get("application_id"),
                    detail={"reason": str(exc)},
                )
                return {
                    "route": "human_review",
                    "routing_reason": str(exc),
                    "requires_human_review": True,
                    "human_review_reasons": [
                        "the lending product could not be resolved from structured facts"
                    ],
                    "steps": [node_name],
                    "steps_taken": 1,
                }
            if resolved is not domain:
                # Routed to the wrong specialist. Refuse rather than quietly
                # retrieving from the other corpus: this chain has no edge to
                # the other one, and pretending otherwise is the isolation
                # failure the topology exists to prevent.
                log_agent_action(
                    actor=node_name,
                    action="reject_misrouted_application",
                    decision="PRODUCT_MISMATCH",
                    application_id=state.get("application_id"),
                    product_domain=resolved.value,
                    detail={"routed_to": domain.value, "packet_resolves_to": resolved.value},
                )
                return {
                    "loan_domain": resolved.value,
                    "route": "human_review",
                    "routing_reason": (
                        f"the request was routed to the {domain.value} specialist but "
                        f"the application resolves to {resolved.value}"
                    ),
                    "requires_human_review": True,
                    "human_review_reasons": [
                        f"routing sent a {resolved.value} application to the "
                        f"{domain.value} specialist; it was refused rather than "
                        f"assessed against the wrong product's policy"
                    ],
                    "steps": [node_name],
                    "steps_taken": 1,
                }
            reason = f"resolved to {resolved.value} from structured facts"

        mode = MODE_ASSESSMENT if packet else MODE_POLICY_QUESTION

        # A policy question carries no underwriting date, and without one the
        # temporal filter has nothing to collapse: a question about the DTI
        # ceiling came back holding both POL-DTI-001 v1.0 (45%) and v2.0 (43%),
        # and an answer built on that presents two conflicting limits as though
        # both governed. Which version applies is a function of a date, so the
        # question gets one — the date asked about if the question names one,
        # and today otherwise — and the answer says which it used.
        as_of = state.get("as_of_date")
        resolved_as_of = as_of
        as_of_source = "supplied"

        if mode == MODE_ASSESSMENT and not as_of:
            # An assessment with no as-of date cannot be performed, and must not
            # be attempted. Which policy version governs is a function of that
            # date — the whole point of APP-000055/56/57 — so defaulting to
            # today would silently judge a file against a rulebook that may not
            # have been in force when it was underwritten.
            #
            # Without a date the temporal filter collapses nothing, both
            # versions of POL-DTI-001 reach the engine, and
            # `assert_single_version` raises inside the eligibility node. That
            # escaped as an unhandled error on an uploaded packet with no date.
            # A missing input is a referral, not a crash.
            log_agent_action(
                actor=node_name,
                action="reject_undated_application",
                decision="MISSING_AS_OF_DATE",
                application_id=state.get("application_id"),
                product_domain=resolved.value,
                detail={"reason": "no underwriting as-of date on the packet"},
            )
            return {
                "loan_domain": resolved.value,
                "workflow_mode": mode,
                "route": "human_review",
                "routing_reason": "no underwriting as-of date",
                "requires_human_review": True,
                "human_review_reasons": [
                    "the application carries no underwriting as-of date, so the "
                    "governing policy version cannot be determined. Supply "
                    "underwriting_as_of_date or application_date; the file is not "
                    "assessable without one (POL-GEN-001 GEN-ELG-002)"
                ],
                "steps": [node_name],
                "steps_taken": 1,
            }

        if mode == MODE_POLICY_QUESTION and not as_of:
            question = (state.get("supervisor") or {}).get("normalized_question") or str(
                state.get("message") or ""
            )
            from_question = _date_in_question(question)
            resolved_as_of = from_question or date.today().isoformat()
            as_of_source = "from_question" if from_question else "defaulted_to_today"

        with span(
            span_name,
            product_domain=resolved.value,
            mode=mode,
            application_id=state.get("application_id") or "",
        ):
            log_agent_action(
                actor=node_name,
                action="accept_request",
                decision=mode,
                application_id=state.get("application_id"),
                product_domain=resolved.value,
                detail={"routing_reason": reason},
            )

        return {
            "loan_domain": resolved.value,
            "workflow_mode": mode,
            "routing_reason": reason,
            "as_of_date": resolved_as_of,
            "as_of_date_source": as_of_source,
            "route": f"{domain.corpus_key}_policy_retrieval",
            "steps": [node_name],
            "steps_taken": 1,
        }

    domain_agent_node.__name__ = node_name
    return domain_agent_node


def make_policy_retrieval_node(
    retriever: PolicyRetriever | None = None,
    domain: LendingProductDomain | None = None,
):
    """Build a Policy Retrieval Agent node, optionally pinned to one product.

    It plans the questions the file raises, then calls the agentic-RAG tool once
    per question, scoped to the resolved product domain. It does not retrieve on
    every turn, and it never retrieves across products.

    ``domain`` pins the node to one product's chain. Left ``None`` the node reads
    the product off the state, which is the form the older single-chain graph
    used and which ``tests/`` still constructs directly.
    """
    node_name = f"{domain.corpus_key}_policy_retrieval" if domain else "policy_retrieval"

    def policy_retrieval_node(state: CredPilotState) -> dict[str, Any]:
        halt = _guard(state, node_name)
        if halt is not None:
            return halt

        resolved = domain or LendingProductDomain.from_any(state["loan_domain"])
        packet = state.get("application_packet") or {}
        as_of = state.get("as_of_date")
        mode = state.get("workflow_mode") or (
            MODE_ASSESSMENT if packet else MODE_POLICY_QUESTION
        )

        if mode == MODE_POLICY_QUESTION:
            # No packet: the user asked a policy question, so there is exactly
            # one question to ask rather than a file's worth of them.
            question = (state.get("supervisor") or {}).get("normalized_question") or str(
                state.get("message") or ""
            )
            questions = [{"topic": "user_question", "query": question}]
        else:
            questions = plan_policy_questions(resolved, packet)
        context = _retrieval_context(resolved, packet)

        evidence: list[PolicyEvidence] = []
        statuses: list[str] = []
        review_reasons: list[str] = []
        degradations: list[dict[str, Any]] = []
        seen: set[str] = set()

        for question in questions:
            result = _retrieve_resiliently(
                query=question["query"],
                domain=resolved,
                application_id=state.get("application_id"),
                as_of_date=as_of,
                retriever=retriever,
                context=context,
                degradations=degradations,
            )
            if result is None:
                statuses.append(f"{question['topic']}:TOOL_FAILURE")
                continue
            statuses.append(f"{question['topic']}:{result.status.value}")
            if result.status is RetrievalStatus.HUMAN_REVIEW_REQUIRED:
                review_reasons.append(result.message or "retrieval flagged the request for review")
            for item in result.evidence:
                if item.chunk_id not in seen:
                    seen.add(item.chunk_id)
                    evidence.append(item)

        # Second pass: follow the rules the first pass's evidence points at.
        # DTI-CONV-001 grants its extension on factors that DTI-CONV-003 defines;
        # without the second rule the first cannot be applied, and the engine
        # would have to refer the file for a reason that was one retrieval away.
        dependencies = referenced_rules(evidence_to_state(evidence))[
            :MAX_DEPENDENCY_FOLLOWS
        ]
        for rule_id in dependencies:
            result = _retrieve_resiliently(
                query=f"What does rule {rule_id} say?",
                domain=resolved,
                application_id=state.get("application_id"),
                as_of_date=as_of,
                retriever=retriever,
                context=context,
                degradations=degradations,
                top_k=3,
            )
            if result is None:
                statuses.append(f"dependency:{rule_id}:TOOL_FAILURE")
                continue
            statuses.append(f"dependency:{rule_id}:{result.status.value}")
            for item in result.evidence:
                if item.chunk_id not in seen:
                    seen.add(item.chunk_id)
                    evidence.append(item)

        # Third pass: fetch by id the rules the engine is about to need and does
        # not have. Only on the assessment path — a policy question is answered
        # from what the question retrieved, not from the whole rulebook.
        required_fetched: list[str] = []
        if mode == MODE_ASSESSMENT:
            held = {e.get("rule_id") for e in evidence_to_state(evidence)}
            missing = [
                r for r in _required_rules_for(resolved, packet) if r not in held
            ][:MAX_REQUIRED_RULE_FETCHES]
            if missing:
                fetched = _fetch_rules_resiliently(
                    rule_ids=missing,
                    domain=resolved,
                    application_id=state.get("application_id"),
                    as_of_date=as_of,
                    retriever=retriever,
                    degradations=degradations,
                )
                landed: set[str] = set()
                for item in fetched:
                    if item.chunk_id not in seen:
                        seen.add(item.chunk_id)
                        evidence.append(item)
                    if item.rule_id:
                        landed.add(item.rule_id)
                required_fetched = sorted(landed)
                statuses.append(
                    f"required_rules:{len(landed)}/{len(missing)}"
                )
                for rule_id in missing:
                    if rule_id not in landed:
                        statuses.append(f"required:{rule_id}:NOT_FOUND")

        next_route = (
            f"{resolved.corpus_key}_eligibility" if mode == MODE_ASSESSMENT
            else "final_response"
        )
        update: dict[str, Any] = {
            "policy_questions": questions,
            "policy_dependencies": dependencies,
            "required_rules_fetched": required_fetched,
            "policy_evidence": evidence_to_state(evidence),
            "retrieval_statuses": statuses,
            "route": next_route,
            "steps": [node_name],
            "steps_taken": 1,
        }
        if degradations:
            update["degradations"] = degradations
        if review_reasons:
            update["requires_human_review"] = True
            update["human_review_reasons"] = review_reasons
        if not evidence:
            update["requires_human_review"] = True
            update["human_review_reasons"] = [
                "no applicable policy evidence was retrieved; the file cannot be assessed "
                "without it"
            ]
            update["route"] = "human_review"
        return update

    policy_retrieval_node.__name__ = node_name
    return policy_retrieval_node


def _retrieve_resiliently(
    *,
    query: str,
    domain: LendingProductDomain,
    application_id: str | None,
    as_of_date: str | None,
    retriever: PolicyRetriever | None,
    context: Mapping[str, Any],
    degradations: list[dict[str, Any]],
    top_k: int | None = None,
):
    """One retrieval, with a deadline and bounded retries (NFR-04).

    A retrieval that fails after its attempts does not raise: the failure is
    recorded on the state and the remaining questions are still asked. A file
    that lost one of fifteen retrievals is still assessable, and it is better to
    report the gap than to abandon the run — but a file that lost *all* of them
    reaches the caller with no evidence and is referred, which the caller
    already handles.
    """
    from src.resilience import RetryPolicy, ToolFailure, safe_call_sync

    def once():
        return retrieve_policy_tool(
            query=query,
            product_domain=domain,
            application_id=application_id,
            as_of_date=as_of_date,
            retriever=retriever,
            **({"top_k": top_k} if top_k is not None else {}),
            **context,
        )

    outcome = safe_call_sync(
        f"retrieve_policy:{domain.corpus_key}",
        once,
        policy=RetryPolicy(max_attempts=2, timeout_seconds=90.0, backoff_seconds=0.25),
    )
    if isinstance(outcome, ToolFailure):
        degradations.append({
            "stage": "policy_retrieval",
            "query": query[:120],
            **outcome.as_dict(),
        })
        log_agent_action(
            actor="policy_retrieval_agent",
            action="retrieve_policy",
            decision="TOOL_FAILURE",
            application_id=application_id,
            product_domain=domain.value,
            detail={"error_type": outcome.error_type, "attempts": outcome.attempts},
        )
        return None
    return outcome


#: Month names as a policy question is likely to spell them.
_MONTHS = {
    name: index
    for index, name in enumerate(
        ("january", "february", "march", "april", "may", "june", "july",
         "august", "september", "october", "november", "december"),
        start=1,
    )
}

_ISO_DATE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
_MONTH_YEAR = re.compile(
    r"\b(" + "|".join(_MONTHS) + r")\s+(\d{4})\b", re.IGNORECASE
)


def _date_in_question(question: str) -> str | None:
    """An underwriting date the question names, if it names one.

    Deliberately narrow: an ISO date, or a month and year. "July 2026" resolves
    to the **first** of the month, which is the conservative reading — a policy
    effective on 2026-07-01 governs the whole of July, and taking the last day
    instead would silently pick a version that came into force mid-question.

    Anything vaguer than that is not parsed. Inferring a date from "last
    summer" would put a version boundary on a guess.
    """
    if not question:
        return None
    iso = _ISO_DATE.search(question)
    if iso:
        try:
            return date(int(iso.group(1)), int(iso.group(2)), int(iso.group(3))).isoformat()
        except ValueError:
            return None
    month_year = _MONTH_YEAR.search(question)
    if month_year:
        month = _MONTHS[month_year.group(1).lower()]
        try:
            return date(int(month_year.group(2)), month, 1).isoformat()
        except ValueError:
            return None
    return None


def _fetch_rules_resiliently(
    *,
    rule_ids: Sequence[str],
    domain: LendingProductDomain,
    application_id: str | None,
    as_of_date: str | None,
    retriever: PolicyRetriever | None,
    degradations: list[dict[str, Any]],
) -> list[PolicyEvidence]:
    """Fetch the engine's required rules by id, degrading rather than raising.

    One call for the whole set: a lookup by id is a scan of already-loaded
    index metadata, so batching it costs nothing and turns fourteen round trips
    into one.
    """
    from src.resilience import RetryPolicy, ToolFailure, safe_call_sync
    from src.tools.rag_tool import fetch_policy_rules

    outcome = safe_call_sync(
        f"fetch_policy_rules:{domain.corpus_key}",
        lambda: fetch_policy_rules(
            rule_ids,
            product_domain=domain,
            as_of_date=as_of_date,
            application_id=application_id,
            retriever=retriever,
        ),
        policy=RetryPolicy(max_attempts=2, timeout_seconds=60.0, backoff_seconds=0.25),
    )
    if isinstance(outcome, ToolFailure):
        degradations.append({
            "stage": "required_rules",
            "rule_ids": list(rule_ids),
            **outcome.as_dict(),
        })
        return []
    return list(outcome)


def _required_rules_for(
    domain: LendingProductDomain, packet: Mapping[str, Any]
) -> list[str]:
    """The rule ids the engine will look for on this file, in order.

    The unconditional list for the product, plus whichever conditional set the
    file's own variant triggers. Education's five ``EDU-UW`` rules are one per
    product code and only the file's own is relevant, so the other four are
    dropped rather than fetched and ignored.
    """
    required = list(REQUIRED_RULES.get(domain.value, ()))

    if domain is LendingProductDomain.EDUCATION_LOAN:
        code = str(packet.get("product_code", "")).upper()
        wanted = {
            "UG": "EDU-UW-001", "GR": "EDU-UW-002", "SP": "EDU-UW-003",
            "INTL": "EDU-UW-004", "REFI": "EDU-UW-005",
        }.get(code)
        required = [
            r for r in required
            if not r.startswith("EDU-UW-") or r == wanted
        ]
        if not packet.get("has_cosigner") and not packet.get("cosigner"):
            required = [r for r in required if not r.startswith("EDU-COS-")]
        if code != "INTL":
            required = [r for r in required if not r.startswith("EDU-INTL-")]

    for product, variant, rules in _CONDITIONAL_REQUIRED_RULES:
        if product != domain.value:
            continue
        matches = (
            str(packet.get("product_family", "")).lower() == variant.lower()
            if domain is LendingProductDomain.MORTGAGE
            else str(packet.get("product_code", "")).upper() == variant.upper()
        )
        if matches:
            required.extend(r for r in rules if r not in required)
    return required


def _retrieval_context(domain: LendingProductDomain, packet: dict[str, Any]) -> dict[str, Any]:
    if domain is LendingProductDomain.MORTGAGE:
        return {
            "product_family": packet.get("product_family"),
            "loan_purpose": packet.get("loan_purpose"),
            "occupancy_type": packet.get("occupancy_type"),
        }
    return {"product_code": packet.get("product_code")}


def make_eligibility_node(domain: LendingProductDomain | None = None):
    """Build the eligibility-and-affordability agent node for one product.

    Named the way the source document names it — "eligibility and
    affordability" — rather than with an ampersand, so the requirement
    validator's search for this worker finds it.

    Figures come from the deterministic calculators, thresholds from the policy
    the retriever returned, and the verdict from the rule engine. No language
    model participates in any of the three.
    """
    node_name = f"{domain.corpus_key}_eligibility" if domain else "eligibility"

    def eligibility_node(state: CredPilotState) -> dict[str, Any]:
        halt = _guard(state, node_name)
        if halt is not None:
            return halt

        from src import rules
        from src.calculations import compute_affordability

        resolved = domain or LendingProductDomain.from_any(state["loan_domain"])
        packet = state.get("application_packet") or {}
        evidence = state_evidence(state)

        calculations = compute_affordability(resolved, packet)
        try:
            evaluations = rules.evaluate(resolved, calculations, packet, evidence)
        except rules.MixedVersionEvidenceError as exc:
            # Two versions of one policy reached the engine, which means the
            # temporal filter did not collapse them — normally because the file
            # has no as-of date, which the product agent now refuses earlier.
            # Kept as a second line: deciding a file against two rulebooks at
            # once is the wrong answer, and so is a traceback in a checkpoint.
            log_agent_action(
                actor="eligibility_agent",
                action="assess_eligibility",
                decision="MIXED_VERSION_EVIDENCE",
                application_id=state.get("application_id"),
                product_domain=resolved.value,
                detail={"error": str(exc)[:300]},
            )
            return {
                "calculations": calculations,
                "eligibility": {
                    "status": "INDETERMINATE",
                    "breaches": [],
                    "indeterminate": [{
                        "measure": "policy_version",
                        "detail": str(exc)[:300],
                        "verdict": "INDETERMINATE",
                    }],
                    "evaluations": [],
                    "thresholds_applied": {},
                },
                # The edge out of this node is unconditional, so `route` names
                # where the run actually goes next. INDETERMINATE plus the
                # review flag is what carries the file to a person, three nodes
                # later, with the risk screen and the recommendation still
                # recorded for the reviewer.
                "route": f"{resolved.corpus_key}_risk",
                "requires_human_review": True,
                "human_review_reasons": [
                    "the retrieved evidence held more than one version of the same "
                    "policy, so no single rulebook governs this file"
                ],
                "steps": [node_name],
                "steps_taken": 1,
            }
        eligibility = rules.summarize(evaluations)

        with span(
            SPAN_ELIGIBILITY,
            product_domain=resolved.value,
            status=eligibility["status"],
            breaches=len(eligibility["breaches"]),
            indeterminate=len(eligibility["indeterminate"]),
            rules_evaluated=len(evaluations),
        ):
            log_agent_action(
                actor="eligibility_agent",
                action="assess_eligibility",
                decision=eligibility["status"],
                application_id=state.get("application_id"),
                product_domain=resolved.value,
                detail={
                    "ratios": calculations.get("ratios", {}),
                    "breaches": eligibility["breaches"],
                    "indeterminate": eligibility["indeterminate"],
                },
            )

        update: dict[str, Any] = {
            "calculations": calculations,
            "eligibility": eligibility,
            "route": f"{resolved.corpus_key}_risk",
            "steps": [node_name],
            "steps_taken": 1,
        }
        if eligibility["status"] == "INDETERMINATE":
            update["requires_human_review"] = True
            update["human_review_reasons"] = [
                f"{e['measure']}: {e['detail']}" for e in eligibility["indeterminate"]
            ]
        return update

    eligibility_node.__name__ = node_name
    return eligibility_node


def make_risk_node(domain: LendingProductDomain | None = None):
    """Build the Risk Screening Agent node for one product."""
    node_name = f"{domain.corpus_key}_risk" if domain else "risk"

    def risk_node(state: CredPilotState) -> dict[str, Any]:
        halt = _guard(state, node_name)
        if halt is not None:
            return halt

        from src.calculations import screen_risk

        resolved = domain or LendingProductDomain.from_any(state["loan_domain"])
        packet = state.get("application_packet") or {}
        risk = screen_risk(resolved, packet)

        if state.get("security_findings"):
            risk["flags"] = list(risk.get("flags", [])) + ["APPLICANT_TEXT_INSTRUCTION_ATTEMPT"]
            risk["level"] = "HIGH"

        with span(
            SPAN_RISK,
            product_domain=resolved.value,
            level=risk.get("level", ""),
            flags=risk.get("flags", []),
        ):
            log_agent_action(
                actor="risk_agent",
                action="screen_risk",
                decision=risk.get("level", "UNKNOWN"),
                application_id=state.get("application_id"),
                product_domain=resolved.value,
                detail={"flags": risk.get("flags", [])},
            )

        return {
            "risk": risk,
            "route": f"{resolved.corpus_key}_recommendation",
            "steps": [node_name],
            "steps_taken": 1,
        }

    risk_node.__name__ = node_name
    return risk_node


def make_recommendation_node(domain: LendingProductDomain | None = None):
    """Build the Recommendation node for one product."""
    node_name = f"{domain.corpus_key}_recommendation" if domain else "recommendation"

    def recommendation_node(state: CredPilotState) -> dict[str, Any]:
        halt = _guard(state, node_name)
        if halt is not None:
            return halt

        from src.review_triggers import evaluate_review_triggers

        resolved = domain or LendingProductDomain.from_any(state["loan_domain"])
        eligibility = state.get("eligibility") or {}
        risk = state.get("risk") or {}
        evidence = state_evidence(state)

        breaches = eligibility.get("breaches") or []
        reasons = list(state.get("human_review_reasons") or [])
        requires_review = bool(state.get("requires_human_review"))

        # POL-UWR-001 UWR-HRV-001 is a routing table, not a scoring input: a file
        # matching any trigger reaches a human however comfortable the rest of it
        # looks. So it is applied to a file that has already passed every threshold,
        # and an eligible file can still be referred.
        review = evaluate_review_triggers(
            resolved,
            state.get("calculations") or {},
            state.get("application_packet") or {},
            evidence,
            eligibility,
            risk,
            security_findings=state.get("security_findings") or [],
        )
        if review.required:
            requires_review = True
            reasons.extend(review.reasons)

        if eligibility.get("status") == "INDETERMINATE":
            # Missing evidence is not a negative result (GEN-ELG-005): the file is
            # referred, never declined, on evidence that is absent rather than bad.
            outcome = "REFER_RECOMMENDATION"
            requires_review = True
        elif eligibility.get("status") == "INELIGIBLE":
            outcome = "DECLINE_RECOMMENDATION"
            # A decline is never auto-decided (POL-DEC-001 DEC-REC-002).
            requires_review = True
            reasons.append("a decline recommendation is always routed to a human (DEC-REC-002)")
        elif risk.get("level") == "HIGH":
            outcome = "REFER_RECOMMENDATION"
            requires_review = True
            reasons.append("high risk level requires manual underwriting")
        elif requires_review:
            outcome = "REFER_RECOMMENDATION"
        else:
            outcome = "APPROVE_RECOMMENDATION"

        recommendation = {
            "outcome": outcome,
            "review_triggers": review.as_dict(),
            "eligibility": eligibility.get("status"),
            "risk_level": risk.get("level"),
            "breaches": breaches,
            "citations": sorted({e["citation"] for e in evidence}),
            "evidence_count": len(evidence),
            "all_citations_resolve": all(e.get("citation_resolves") for e in evidence),
            "rationale": None,
        }

        with span(
            SPAN_RECOMMENDATION,
            product_domain=resolved.value,
            outcome=outcome,
            requires_human_review=requires_review,
            citation_count=len(recommendation["citations"]),
        ):
            log_agent_action(
                actor="recommendation_agent",
                action="draft_recommendation",
                decision=outcome,
                application_id=state.get("application_id"),
                product_domain=resolved.value,
                detail={
                    "citations": recommendation["citations"],
                    "requires_human_review": requires_review,
                },
            )

        return {
            "recommendation": recommendation,
            "requires_human_review": requires_review,
            "human_review_reasons": [
                r for r in reasons if r not in (state.get("human_review_reasons") or [])
            ],
            "route": "narrative",
            "steps": [node_name],
            "steps_taken": 1,
        }

    recommendation_node.__name__ = node_name
    return recommendation_node


#: Backwards-compatible unpinned nodes. The compiled graph uses the pinned
#: per-product ones; these keep the older direct-call form working for tests and
#: for anything embedding a single worker.
eligibility_node = make_eligibility_node()
risk_node = make_risk_node()
recommendation_node = make_recommendation_node()


def narrative_node(state: CredPilotState) -> dict[str, Any]:
    """Write the rationale, then check it against its own evidence.

    This is the only node a language model touches on the assessment path, and it
    runs *after* the decision exists. It receives the outcome as a fact and the
    figures pre-computed, so there is nothing here for a model to decide.

    Generation is followed by a deterministic check that every citation and every
    figure in the prose came from the evidence it was given. A narrative that
    fails that check is kept, marked unfaithful and routed to a human — dropping
    it would hide the failure, and shipping it unmarked would be worse.
    """
    halt = _guard(state, "narrative")
    if halt is not None:
        return halt

    from src.context.write import Scratchpad
    from src.narrative import draft_rationale
    from src.observability.tracing import SPAN_KIND_THINKING, SPAN_NARRATIVE

    scratchpad = Scratchpad(application_id=state.get("application_id") or "")

    with span(
        SPAN_NARRATIVE,
        span_kind=SPAN_KIND_THINKING,
        product_domain=str(state.get("loan_domain") or ""),
        application_id=state.get("application_id") or "",
    ) as sp:
        result = draft_rationale(state, scratchpad=scratchpad)
        usage = result.usage or {}
        # Tokens and cost live on the span so the golden-signals report can be
        # derived from Phoenix rather than from the evaluation's own case file.
        sp.set(
            model=result.model or "",
            available=result.available,
            is_faithful=result.is_faithful,
            input_tokens=int(usage.get("input_tokens", 0) or 0),
            output_tokens=int(usage.get("output_tokens", 0) or 0),
            total_tokens=int(usage.get("total_tokens", 0) or 0),
            reasoning_tokens=int(usage.get("reasoning_tokens", 0) or 0),
            cost_usd=float(result.cost_usd or 0.0),
            latency_ms=round(result.latency_ms, 1),
            citations_used=len(result.citations_used or []),
            llm_call=True,
        )

    recommendation = dict(state.get("recommendation") or {})
    recommendation["rationale"] = result.text
    recommendation["rationale_is_faithful"] = result.is_faithful
    recommendation["rationale_model"] = result.model

    update: dict[str, Any] = {
        "narrative": result.as_dict(),
        "recommendation": recommendation,
        "context_record": scratchpad.as_dict(),
        "steps": ["narrative"],
        "steps_taken": 1,
    }

    if not result.is_faithful:
        update["requires_human_review"] = True
        update["human_review_reasons"] = [
            "the drafted rationale asserted something its evidence does not support "
            f"(citations: {result.unsupported_citations or 'none'}; "
            f"figures: {result.unsupported_figures or 'none'})"
        ]

    log_agent_action(
        actor="narrative_agent",
        action="draft_rationale",
        decision="FAITHFUL" if result.is_faithful else "UNSUPPORTED_CLAIM",
        application_id=state.get("application_id"),
        product_domain=state.get("loan_domain"),
        detail={
            "model": result.model,
            "available": result.available,
            "citations_used": result.citations_used,
            "unsupported_citations": result.unsupported_citations,
            "unsupported_figures": result.unsupported_figures,
            "usage": result.usage,
            "latency_ms": round(result.latency_ms, 1),
        },
    )

    update["route"] = "final_response"
    return update


def human_review_node(state: CredPilotState) -> dict[str, Any]:
    """Hand the request to a person, with everything they need to pick it up.

    No longer terminal. A reviewer gets the same assembled response every other
    path produces, marked as awaiting them — a bare "routed for review" with the
    figures left on the floor is not a handoff.
    """
    halt = _guard(state, "human_review")
    if halt is not None:
        return halt

    record_interaction(state)
    reasons = list(state.get("human_review_reasons") or [])

    with span(
        SPAN_HUMAN_REVIEW,
        product_domain=str(state.get("loan_domain") or ""),
        reason_count=len(reasons),
        halted=bool(state.get("halted")),
    ):
        log_agent_action(
            actor="supervisor",
            action="route_for_human_review",
            decision="HUMAN_REVIEW_REQUIRED",
            application_id=state.get("application_id"),
            product_domain=state.get("loan_domain"),
            detail={"reasons": reasons},
        )

    return {
        "requires_human_review": True,
        "route": "final_response",
        "steps": ["human_review"],
        "steps_taken": 1,
    }


# ======================================================================================
# Final Response Agent and output guardrails
# ======================================================================================


def final_response_node(state: CredPilotState) -> dict[str, Any]:
    """Assemble the answer. It presents the decision; it does not make one.

    Everything here is already settled: the outcome came from the rule engine,
    the figures from the calculators, the prose from the narrative node, the
    review status from the trigger table. This node's only judgement is what to
    show and in what order — and it validates before it shows anything:

    * every cited rule must resolve to a committed document;
    * every figure quoted in the prose must be one the calculators produced;
    * the prose must not contradict the recommendation it accompanies.

    A validation failure is never papered over. The deterministic summary
    replaces the prose, the failure is recorded, and the file goes to a person.
    """
    halt = _guard(state, "final_response")
    if halt is not None:
        return halt

    existing = state.get("final_response") or {}
    if existing.get("kind") in ("GENERAL", "OUT_OF_SCOPE"):
        # A social or refusal turn already has its answer and nothing to validate.
        return {
            "answer": existing.get("text", ""),
            "steps": ["final_response"],
            "steps_taken": 1,
            "route": "output_guardrails",
        }

    recommendation = state.get("recommendation") or {}
    narrative = state.get("narrative") or {}
    evidence = state_evidence(state)
    calculations = state.get("calculations") or {}
    eligibility = state.get("eligibility") or {}
    risk = state.get("risk") or {}
    mode = state.get("workflow_mode") or MODE_ASSESSMENT

    # Each branch produces its own prose and validates that prose. Validating
    # once up front and then replacing the text would check something other
    # than what is published, which is the one thing this node exists to avoid.
    if mode == MODE_POLICY_QUESTION:
        kind = "POLICY_ANSWER"
        answer = _answer_policy_question(state, evidence)
        narrative = answer.as_dict()
        text = answer.text
        validation = _validate_response(state, recommendation, narrative, evidence)
        if not validation["passed"] and validation["fallback_to_deterministic"]:
            # The model said something its evidence does not support. The quoted
            # rules are a worse answer to read and cannot be wrong about the
            # policy, which is the trade to make here.
            from src.narrative import _quoted_policy_answer  # noqa: PLC2701

            text = _quoted_policy_answer(
                (state.get("supervisor") or {}).get("normalized_question") or "",
                evidence,
                state.get("loan_domain"),
            )
    elif not state.get("application_packet") and not evidence:
        # A turn that reached here without a packet and without evidence was
        # escalated by the Supervisor — an override request, a complaint, an
        # injection attempt. Labelling it ASSESSMENT would be a lie in the one
        # field a reader uses to tell what happened, and it would report
        # retrieval as invoked when nothing was retrieved.
        from src.supervisor import ESCALATION_RESPONSE

        kind = "ESCALATION"
        text = ESCALATION_RESPONSE
        # Nothing was retrieved and nothing was decided, so there is nothing to
        # validate — and saying "validation passed" over an empty bundle would
        # be a claim about a check that never ran.
        validation = _validate_response(state, {}, {}, ())
    else:
        kind = "ASSESSMENT"
        text = str(narrative.get("text") or "")
        validation = _validate_response(state, recommendation, narrative, evidence)
        if not validation["passed"] and validation["fallback_to_deterministic"]:
            # The prose asserted something its evidence does not support. The
            # deterministic summary is built from the evidence rather than
            # written about it, so it cannot.
            from src.narrative import _deterministic_summary  # noqa: PLC2701

            text = _deterministic_summary(state)

    response = {
        "kind": kind,
        "product_domain": state.get("loan_domain"),
        "application_id": state.get("application_id"),
        "as_of_date": state.get("as_of_date"),
        "outcome": recommendation.get("outcome"),
        "eligibility": eligibility.get("status"),
        "risk_level": risk.get("level"),
        "requires_human_review": bool(state.get("requires_human_review")),
        "human_review_reasons": list(state.get("human_review_reasons") or []),
        "text": text,
        "citations": list(recommendation.get("citations") or sorted({
            e["citation"] for e in evidence if e.get("citation")
        })),
        "figures": {
            "ratios": calculations.get("ratios", {}),
            "amounts": calculations.get("amounts", {}),
            "indeterminate": calculations.get("indeterminate", []),
        },
        "breaches": recommendation.get("breaches") or [],
        "missing_evidence": [
            e.get("detail") for e in (eligibility.get("indeterminate") or [])
        ],
        # Reported from what happened, not from which branch produced the
        # response. An escalated turn reaches this node having retrieved
        # nothing, and saying otherwise would misdescribe the run in the one
        # field a reader checks first.
        "retrieval_invoked": bool(evidence) or bool(state.get("retrieval_statuses")),
        "evidence_count": len(evidence),
        "validation": validation,
        "degradations": list(state.get("degradations") or []),
    }

    with span(
        SPAN_FINAL_RESPONSE,
        kind=kind,
        outcome=str(recommendation.get("outcome") or ""),
        validation_passed=validation["passed"],
        citation_count=len(response["citations"]),
    ):
        log_agent_action(
            actor="final_response_agent",
            action="assemble_response",
            decision="VALIDATED" if validation["passed"] else "VALIDATION_FAILED",
            application_id=state.get("application_id"),
            product_domain=state.get("loan_domain"),
            detail={
                "kind": kind,
                "failures": validation["failures"],
                "fell_back_to_deterministic": validation["fallback_to_deterministic"],
            },
        )

    update: dict[str, Any] = {
        "final_response": response,
        "answer": text,
        "steps": ["final_response"],
        "steps_taken": 1,
        "route": "output_guardrails",
    }
    if kind == "POLICY_ANSWER":
        # The policy answer is a model call like any other and belongs on the
        # state under the same key, so the evaluation harness and the trace
        # export see one narrative record per turn whatever path produced it.
        update["narrative"] = narrative
    if not validation["passed"]:
        update["requires_human_review"] = True
        update["human_review_reasons"] = [
            f"the assembled response failed validation: {'; '.join(validation['failures'])}"
        ]
    return update


#: Outcome words whose presence in the prose would contradict the recommendation
#: they accompany. Checked as whole words against the decided outcome family.
#: Re-exported from the guardrails package, where the output guardrail lives.
#: Referenced by name in a few places in this module and in the tests.
_CONTRADICTION_TERMS = CONTRADICTION_TERMS


def _validate_response(
    state: "Mapping[str, Any]",
    recommendation: "Mapping[str, Any]",
    narrative: "Mapping[str, Any]",
    evidence: "Sequence[Mapping[str, Any]]",
) -> dict[str, Any]:
    """The output guardrail. Lives in :mod:`src.guardrails.validation`.

    Kept here as a thin alias because every call site in this module reads
    better with the private name, and because moving it should not change any
    behaviour. The implementation moved so that the output guardrail sits
    beside the input one and can be exercised without building a graph.
    """
    return validate_response(state, recommendation, narrative, evidence)


def _answer_policy_question(
    state: Mapping[str, Any], evidence: Sequence[Mapping[str, Any]]
):
    """Write the answer to a policy question, traced as a model call.

    Opened as a THINKING span carrying its tokens and cost, exactly like the
    narrative node, so the golden-signals report sees every model call the
    system makes rather than only the ones on the assessment path.
    """
    from src.narrative import answer_policy_question
    from src.observability.tracing import SPAN_KIND_THINKING, SPAN_NARRATIVE

    question = (state.get("supervisor") or {}).get("normalized_question") or str(
        state.get("message") or ""
    )
    with span(
        SPAN_NARRATIVE,
        span_kind=SPAN_KIND_THINKING,
        kind="policy_answer",
        product_domain=str(state.get("loan_domain") or ""),
    ) as sp:
        result = answer_policy_question(
            question,
            evidence,
            product_domain=state.get("loan_domain"),
            as_of_date=state.get("as_of_date"),
        )
        usage = result.usage or {}
        sp.set(
            model=result.model or "",
            available=result.available,
            is_faithful=result.is_faithful,
            input_tokens=int(usage.get("input_tokens", 0) or 0),
            output_tokens=int(usage.get("output_tokens", 0) or 0),
            total_tokens=int(usage.get("total_tokens", 0) or 0),
            cost_usd=float(result.cost_usd or 0.0),
            latency_ms=round(result.latency_ms, 1),
            citations_used=len(result.citations_used or []),
            llm_call=True,
        )

    log_agent_action(
        actor="final_response_agent",
        action="answer_policy_question",
        decision="FAITHFUL" if result.is_faithful else "UNSUPPORTED_CLAIM",
        product_domain=state.get("loan_domain"),
        detail={
            "model": result.model,
            "available": result.available,
            "citations_used": result.citations_used,
            "unsupported_citations": result.unsupported_citations,
            "unsupported_figures": result.unsupported_figures,
            "usage": result.usage,
        },
    )
    return result


def output_guardrails_node(state: CredPilotState) -> dict[str, Any]:
    """Output guardrails: nothing leaves without being scanned.

    Three checks, in the order a leak would happen:

    * **PII.** The response is scanned for anything that looks like an account
      number, a taxpayer id or a credit identifier. A hit is redacted in place
      and recorded — the reader gets the answer with the identifier masked, not
      a blank refusal.
    * **Human-review enforcement.** A response for a file that requires review
      must say so. If the flag is set and the text does not carry the notice, the
      notice is added here rather than trusted to the writer above.
    * **Refusal enforcement.** An out-of-scope turn must not have acquired
      citations or figures on its way through.
    """
    halt = _guard(state, "output_guardrails")
    if halt is not None:
        return halt

    from src.guardrails.redaction import find_sensitive, redact_text

    response = dict(state.get("final_response") or {})
    text = str(response.get("text") or state.get("answer") or "")

    found = find_sensitive(text)
    redacted_text = redact_text(text) if found else text

    notices: list[str] = []
    if state.get("requires_human_review") and response.get("kind") == "ASSESSMENT":
        marker = "human review"
        if marker not in redacted_text.lower():
            reasons = list(state.get("human_review_reasons") or [])
            redacted_text = (
                redacted_text.rstrip()
                + "\n\n**This file requires human review before any decision is "
                "communicated.** "
                + (f"Reason: {reasons[0]}" if reasons else "")
            ).strip()
            notices.append("human_review_notice_added")

    refusal_clean = True
    if response.get("kind") == "OUT_OF_SCOPE":
        refusal_clean = not response.get("citations") and not response.get("figures")
        if not refusal_clean:
            response["citations"] = []
            response["figures"] = {}
            notices.append("stripped_evidence_from_a_refusal")

    guardrail = {
        "pii_findings": sorted({f for f in found})[:12] if found else [],
        "pii_redacted": bool(found),
        "human_review_enforced": "human_review_notice_added" in notices,
        "refusal_clean": refusal_clean,
        "notices": notices,
        "scanned_chars": len(text),
    }

    with span(
        SPAN_OUTPUT_GUARDRAILS,
        pii_findings=len(guardrail["pii_findings"]),
        notices=notices,
        kind=str(response.get("kind") or ""),
    ):
        if found or notices:
            log_agent_action(
                actor="output_guardrails",
                action="scan_response",
                decision="MODIFIED" if (found or notices) else "CLEAN",
                application_id=state.get("application_id"),
                product_domain=state.get("loan_domain"),
                detail=guardrail,
            )

    response["text"] = redacted_text
    response["output_guardrail"] = guardrail

    update: dict[str, Any] = {
        "final_response": response,
        "answer": redacted_text,
        "output_guardrail": guardrail,
        "steps": ["output_guardrails"],
        "steps_taken": 1,
        "route": "done",
    }
    if response.get("kind") == "ASSESSMENT" and not state.get("requires_human_review"):
        # The only path that ends without a person seeing it, so it is the only
        # one that has to leave a trace for the applicant's next visit.
        update["memory_written"] = record_interaction({**state, **update})
    if response.get("kind") in ("ASSESSMENT", "POLICY_ANSWER"):
        update["conversation_history"] = [
            {
                "role": "assistant",
                "text": redacted_text[:2000],
                "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
        ]
    return update


# ======================================================================================
# Conditional edges
# ======================================================================================

#: The Supervisor's route names, as node names.
_SUPERVISOR_TARGETS = {
    Route.GENERAL.value: "general_response",
    Route.CLARIFY.value: "clarification",
    Route.MORTGAGE.value: "mortgage_agent",
    Route.EDUCATION_LOAN.value: "education_agent",
    Route.HUMAN_REVIEW.value: "human_review",
    Route.OUT_OF_SCOPE.value: "safe_response",
}


def route_after_supervisor(state: CredPilotState) -> str:
    """Where the Supervisor's decision sends the request."""
    if state.get("halted"):
        return "human_review"
    return _SUPERVISOR_TARGETS.get(str(state.get("route") or ""), "clarification")


def make_route_after_agent(domain: LendingProductDomain):
    """A product agent either proceeds into its own chain or escalates."""
    target = f"{domain.corpus_key}_policy_retrieval"

    def route_after_agent(state: CredPilotState) -> str:
        return "human_review" if state.get("route") == "human_review" else target

    return route_after_agent


def make_route_after_retrieval(domain: LendingProductDomain):
    """After retrieval: assess the file, answer the question, or escalate."""
    target = f"{domain.corpus_key}_eligibility"

    def route_after_retrieval(state: CredPilotState) -> str:
        if state.get("route") == "human_review":
            return "human_review"
        if state.get("workflow_mode") == MODE_POLICY_QUESTION:
            return "final_response"
        return target

    return route_after_retrieval


def route_after_recommendation(state: CredPilotState) -> Literal["narrative", "human_review"]:
    """Every file gets a written rationale, including the ones a human will decide.

    A reviewer picking up a referred file needs the reasoning more than an
    auto-approved file does, so the narrative comes before the handoff, not
    instead of it.
    """
    return "human_review" if state.get("halted") else "narrative"


def route_after_narrative(state: CredPilotState) -> Literal["human_review", "final_response"]:
    return "human_review" if state.get("requires_human_review") else "final_response"


def route_after_clarification(state: CredPilotState) -> Literal["supervisor", "human_review"]:
    """A clarified thread goes back to the Supervisor to be re-routed."""
    if state.get("halted"):
        return "human_review"
    return "supervisor"


def route_after_domain(state: CredPilotState) -> str:
    """Legacy edge: kept so the older single-chain wiring still resolves.

    The compiled graph no longer has a ``domain_router`` node; the Supervisor
    routes directly to a product specialist. This remains because it is a pure
    function of state that tests and external callers assert against.
    """
    if state.get("route") == "human_review":
        return "human_review"
    domain = state.get("loan_domain")
    if domain:
        key = LendingProductDomain.from_any(domain).corpus_key
        return f"{key}_policy_retrieval"
    return "clarification"


def route_after_retrieval(state: CredPilotState) -> str:
    """Legacy edge form, for the same reason as :func:`route_after_domain`."""
    if state.get("route") == "human_review":
        return "human_review"
    if state.get("workflow_mode") == MODE_POLICY_QUESTION:
        return "final_response"
    domain = state.get("loan_domain")
    key = LendingProductDomain.from_any(domain).corpus_key if domain else "mortgage"
    return f"{key}_eligibility"


# ======================================================================================
# Graph construction
# ======================================================================================


def build_graph(
    *,
    retriever: PolicyRetriever | None = None,
    checkpointer: Any | None = None,
    checkpoint_path: Path | None = None,
):
    """Compile the CredPilot graph.

    Returns ``(compiled_graph, checkpointer_context)``. When no checkpointer is
    passed one is opened over SQLite; the caller closes the returned context.

    The two product chains are generated from the same factories and wired as
    separate node sets. Nothing connects one chain to the other, which is what
    makes product isolation a property of the compiled graph rather than a
    property of a condition someone has to keep writing correctly.
    """
    from langgraph.graph import END, START, StateGraph

    from src.guardrails.redaction import warm_redaction

    # Build the PII analyzer off the request path. Lazily it costs 17 seconds
    # inside the first audit-log write, which happens in the intake node of the
    # first request — see F-14 in docs/failure-analysis.md and the 31-second
    # `graph.intake` span it produced. Building the graph is already a set-up
    # step, so this is where the cost belongs.
    warm_redaction()

    builder = StateGraph(CredPilotState)

    # -- entry -----------------------------------------------------------------
    builder.add_node("intake", intake_node)
    builder.add_node("input_guardrails", input_guardrails_node)
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("general_response", general_response_node)
    builder.add_node("clarification", clarification_node)
    builder.add_node("safe_response", safe_response_node)

    # -- one chain per product, sharing no node --------------------------------
    for domain in (LendingProductDomain.MORTGAGE, LendingProductDomain.EDUCATION_LOAN):
        key = domain.corpus_key
        builder.add_node(f"{key}_agent", make_domain_agent_node(domain))
        builder.add_node(
            f"{key}_policy_retrieval", make_policy_retrieval_node(retriever, domain)
        )
        builder.add_node(f"{key}_eligibility", make_eligibility_node(domain))
        builder.add_node(f"{key}_risk", make_risk_node(domain))
        builder.add_node(f"{key}_recommendation", make_recommendation_node(domain))

    # -- shared tail -----------------------------------------------------------
    builder.add_node("narrative", narrative_node)
    builder.add_node("human_review", human_review_node)
    builder.add_node("final_response", final_response_node)
    builder.add_node("output_guardrails", output_guardrails_node)

    builder.add_edge(START, "intake")
    builder.add_edge("intake", "input_guardrails")
    builder.add_edge("input_guardrails", "supervisor")
    builder.add_conditional_edges(
        "supervisor", route_after_supervisor, sorted(set(_SUPERVISOR_TARGETS.values()))
    )
    builder.add_conditional_edges(
        "clarification", route_after_clarification, ["supervisor", "human_review"]
    )
    builder.add_edge("general_response", "final_response")
    builder.add_edge("safe_response", "final_response")

    for domain in (LendingProductDomain.MORTGAGE, LendingProductDomain.EDUCATION_LOAN):
        key = domain.corpus_key
        builder.add_conditional_edges(
            f"{key}_agent",
            make_route_after_agent(domain),
            [f"{key}_policy_retrieval", "human_review"],
        )
        builder.add_conditional_edges(
            f"{key}_policy_retrieval",
            make_route_after_retrieval(domain),
            [f"{key}_eligibility", "final_response", "human_review"],
        )
        builder.add_edge(f"{key}_eligibility", f"{key}_risk")
        builder.add_edge(f"{key}_risk", f"{key}_recommendation")
        builder.add_conditional_edges(
            f"{key}_recommendation",
            route_after_recommendation,
            {"narrative": "narrative", "human_review": "human_review"},
        )

    builder.add_conditional_edges(
        "narrative",
        route_after_narrative,
        {"human_review": "human_review", "final_response": "final_response"},
    )
    builder.add_edge("human_review", "final_response")
    builder.add_edge("final_response", "output_guardrails")
    builder.add_edge("output_guardrails", END)

    context = None
    if checkpointer is None:
        from langgraph.checkpoint.sqlite import SqliteSaver

        path = checkpoint_path or CHECKPOINT_DB
        path.parent.mkdir(parents=True, exist_ok=True)
        context = SqliteSaver.from_conn_string(str(path))
        checkpointer = context.__enter__()

    compiled = builder.compile(checkpointer=checkpointer)
    # LangGraph's own limit is the backstop for a cycle that never reaches a node
    # able to check the in-state budget. Both are needed: this one raises,
    # DEFAULT_STEP_BUDGET halts cleanly with a reason.
    compiled = compiled.with_config(recursion_limit=RECURSION_LIMIT)
    return compiled, context


def initial_state(
    application_path: "str | Path",
    *,
    as_of_date: "str | date | None" = None,
    config: RagConfig | None = None,
    session_id: str | None = None,
    message: str | None = None,
) -> CredPilotState:
    """Build the graph's initial state from a committed application packet.

    The packet is enriched with the committed underwriting *inputs* that do not
    appear on the application form — property tax, hazard premium, mortgage
    insurance, the verified liability set. See :mod:`src.application_context`,
    which refuses to read any table holding an outcome.
    """
    return packet_state(
        build_underwriting_input(application_path),
        as_of_date=as_of_date,
        session_id=session_id,
        message=message,
    )


def packet_state(
    packet: Mapping[str, Any],
    *,
    as_of_date: "str | date | None" = None,
    session_id: str | None = None,
    message: str | None = None,
) -> CredPilotState:
    """Build the graph's initial state from an application packet in memory.

    The one place that decides what an assessment run starts from, shared by the
    CLI (through :func:`initial_state`), the web API and the trace exporter. A
    packet that reaches the graph from outside is not guaranteed to carry an
    as-of date; resolving it here rather than in each caller is what makes the
    refusal in the product agent node reachable from every surface (see F-20).
    """
    resolved_as_of = (
        str(as_of_date)
        if as_of_date
        else packet.get("underwriting_as_of_date")
        or packet.get("application_date")
        or (str(packet.get("submitted_at", ""))[:10] or None)
    )
    return {
        "application_id": str(packet.get("application_id") or ""),
        "application_packet": dict(packet),
        "as_of_date": resolved_as_of,
        "message": message or "",
        "conversation_history": [],
        "policy_evidence": [],
        "retrieval_statuses": [],
        "human_review_reasons": [],
        "security_findings": [],
        "errors": [],
        "steps": [],
        "degradations": [],
        "session_id": session_id or uuid.uuid4().hex[:12],
        "subject_id": None,
        "recalled_memory": [],
        "step_budget": DEFAULT_STEP_BUDGET,
        "steps_taken": 0,
        "clarification_rounds": 0,
        "halted": False,
        "requires_human_review": False,
    }


def conversation_state(
    message: str,
    *,
    session_id: str | None = None,
    as_of_date: "str | date | None" = None,
    loan_domain: "str | LendingProductDomain | None" = None,
) -> CredPilotState:
    """The graph's initial state for a conversational turn with no application.

    The same graph handles both. What differs is only that there is no packet, so
    the Supervisor classifies from language and the product chain answers a
    policy question instead of assessing a file.
    """
    return {
        "application_id": "",
        "application_packet": {},
        "as_of_date": str(as_of_date) if as_of_date else None,
        "message": message,
        "conversation_history": [],
        "loan_domain": (
            LendingProductDomain.from_any(loan_domain).value if loan_domain else None
        ),
        "policy_evidence": [],
        "retrieval_statuses": [],
        "human_review_reasons": [],
        "security_findings": [],
        "errors": [],
        "steps": [],
        "degradations": [],
        "session_id": session_id or uuid.uuid4().hex[:12],
        "subject_id": None,
        "recalled_memory": [],
        "step_budget": DEFAULT_STEP_BUDGET,
        "steps_taken": 0,
        "clarification_rounds": 0,
        "halted": False,
        "requires_human_review": False,
    }


def pending_clarification(result: Mapping[str, Any]) -> dict[str, Any] | None:
    """The clarification a suspended run is waiting on, if it is waiting.

    LangGraph reports an interrupt on the result under ``__interrupt__``. Callers
    — the CLI, the web app, the evaluation harness — all need to notice the same
    thing, so they ask here rather than each reaching into that key.
    """
    interrupts = result.get("__interrupt__") or []
    for item in interrupts:
        value = getattr(item, "value", item)
        if isinstance(value, Mapping) and value.get("kind") == "clarification":
            return dict(value)
    return None


__all__ = [
    "CHECKPOINT_DB",
    "CredPilotState",
    "EDUCATION_QUESTIONS",
    "MAX_CLARIFICATION_ROUNDS",
    "MORTGAGE_QUESTIONS",
    "MODE_ASSESSMENT",
    "MODE_POLICY_QUESTION",
    "DEFAULT_STEP_BUDGET",
    "MAX_DEPENDENCY_FOLLOWS",
    "MAX_REQUIRED_RULE_FETCHES",
    "REQUIRED_RULES",
    "RECURSION_LIMIT",
    "budget_exhausted",
    "build_graph",
    "clarification_node",
    "conversation_state",
    "eligibility_node",
    "evidence_to_state",
    "final_response_node",
    "general_response_node",
    "human_review_node",
    "input_guardrails_node",
    "intake_node",
    "make_domain_agent_node",
    "make_eligibility_node",
    "make_policy_retrieval_node",
    "make_recommendation_node",
    "make_risk_node",
    "narrative_node",
    "output_guardrails_node",
    "pending_clarification",
    "recall_prior_context",
    "recommendation_node",
    "record_interaction",
    "referenced_rules",
    "risk_node",
    "route_after_clarification",
    "route_after_domain",
    "route_after_narrative",
    "route_after_recommendation",
    "route_after_retrieval",
    "route_after_supervisor",
    "safe_response_node",
    "subject_of",
    "supervisor_node",
    "initial_state",
    "state_evidence",
    "plan_policy_questions",
    "get_config",
]
