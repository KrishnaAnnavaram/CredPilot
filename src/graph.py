"""The CredPilot LangGraph.

Typed state, a supervisor, a loan-domain router and specialized worker agents,
with conditional edges, a SQLite checkpointer and structured output at every node
boundary.

::

                              Supervisor
                                   |
                          Loan Domain Router
                          /                \\
                   MORTGAGE              EDUCATION_LOAN
                          \\                /
                           +------+-------+
                                  |
                       Policy Retrieval Agent   <-- calls the agentic-RAG tool
                                  |
                    Eligibility & Affordability Agent
                                  |
                        Risk Screening Agent
                                  |
                          Recommendation
                                  |
                        Narrative Rationale      <-- the only node an LLM touches
                                  |
                        (conditional) Human Review

Three rules the graph exists to enforce:

* **Retrieval-in-the-loop, not up-front.** The Policy Retrieval Agent decides
  which policy questions the file actually raises and issues one targeted
  retrieval per question. The whole corpus never enters a prompt.
* **The model never does the arithmetic.** DTI, LTV, reserves and cash-to-close
  come from :mod:`src.calculations`; Gemini may explain a computed figure, never
  produce one (``POL-DTI-001`` rule ``DTI-CALC-002``).
* **Product isolation happens before retrieval.** The domain router resolves the
  lending product from structured facts, and every downstream retrieval is scoped
  to it. Where the product cannot be resolved the graph escalates rather than
  searching both corpora.
"""

from __future__ import annotations

import operator
import re
import uuid
from datetime import date
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
from src.observability.tool_logging import log_agent_action
from src.rag.models import PolicyEvidence, RetrievalStatus
from src.rag.pipeline import PolicyRetriever
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

    # routing
    loan_domain: str | None
    route: str
    routing_reason: str

    # worker output
    policy_questions: list[dict[str, Any]]
    policy_dependencies: list[str]
    policy_evidence: Annotated[list[dict[str, Any]], operator.add]
    retrieval_statuses: Annotated[list[str], operator.add]
    calculations: dict[str, Any]
    eligibility: dict[str, Any]
    risk: dict[str, Any]
    recommendation: dict[str, Any]
    narrative: dict[str, Any]
    context_record: dict[str, Any]

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

#: How many node executions one assessment may use. The graph is linear today, so
#: a correct run visits at most seven nodes; the budget leaves room for a
#: conditional edge to be added later without immediately tripping.
#:
#: Two independent guards, because they fail differently:
#:   * this budget is *inside* the state, so a node can see it running out and
#:     halt cleanly with a reason a human can read;
#:   * LangGraph's own ``recursion_limit`` is *outside* and raises
#:     ``GraphRecursionError`` — the backstop for a cycle that never reaches a
#:     node able to check anything.
#: A runaway loop in an underwriting system is not a performance problem; it is
#: an unbounded spend against an applicant's file with no decision at the end.
DEFAULT_STEP_BUDGET = 24
RECURSION_LIMIT = 40


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
# Nodes
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


def supervisor_node(state: CredPilotState) -> dict[str, Any]:
    """Intake: quarantine untrusted text and decide where the file goes next."""
    halt = _guard(state, "supervisor")
    if halt is not None:
        return halt

    packet = state.get("application_packet") or {}
    untrusted = packet.get("untrusted_applicant_text")

    quarantined = None
    findings: list[str] = []
    if untrusted:
        content = untrusted.get("content") if isinstance(untrusted, dict) else str(untrusted)
        quarantined = quarantine(content)
        findings = list(quarantined["injection_findings"])

    subject = subject_of(packet)
    recalled = recall_prior_context(subject)

    update: dict[str, Any] = {
        "untrusted_applicant_text": quarantined,
        "security_findings": findings,
        "subject_id": subject,
        "recalled_memory": recalled,
        "steps": ["supervisor"],
        "steps_taken": 1,
        "route": "domain_router",
    }
    if quarantined and quarantined["requires_human_review"]:
        update["requires_human_review"] = True
        update["human_review_reasons"] = [
            "applicant-supplied text attempted to alter policy, thresholds or data access "
            "(POL-SEC-001 SEC-INJ-001)"
        ]
    return update


def domain_router_node(state: CredPilotState) -> dict[str, Any]:
    """Resolve the lending product from structured facts, before any retrieval."""
    halt = _guard(state, "domain_router")
    if halt is not None:
        return halt

    try:
        domain = resolve_product_domain(
            explicit_domain=state.get("loan_domain"),
            application_id=state.get("application_id"),
            packet=state.get("application_packet"),
        )
    except ProductResolutionError as exc:
        log_agent_action(
            actor="domain_router",
            action="resolve_product_domain",
            decision=RetrievalStatus.PRODUCT_CLARIFICATION_REQUIRED.value,
            application_id=state.get("application_id"),
            detail={"reason": str(exc)},
        )
        return {
            "loan_domain": None,
            "route": "human_review",
            "routing_reason": str(exc),
            "requires_human_review": True,
            "human_review_reasons": ["lending product could not be resolved from structured facts"],
            "steps": ["domain_router"],
        "steps_taken": 1,
        }

    log_agent_action(
        actor="domain_router",
        action="resolve_product_domain",
        decision=domain.value,
        application_id=state.get("application_id"),
        product_domain=domain.value,
        detail={"signal": "application_id" if state.get("application_id") else "packet_shape"},
    )
    return {
        "loan_domain": domain.value,
        "route": "policy_retrieval",
        "routing_reason": f"resolved to {domain.value}",
        "steps": ["domain_router"],
        "steps_taken": 1,
    }


def make_policy_retrieval_node(retriever: PolicyRetriever | None = None):
    """Build the Policy Retrieval Agent node.

    It plans the questions the file raises, then calls the agentic-RAG tool once
    per question, scoped to the resolved product domain. It does not retrieve on
    every turn, and it never retrieves across products.
    """

    def policy_retrieval_node(state: CredPilotState) -> dict[str, Any]:
        halt = _guard(state, "policy_retrieval")
        if halt is not None:
            return halt

        domain = LendingProductDomain.from_any(state["loan_domain"])
        packet = state.get("application_packet") or {}
        as_of = state.get("as_of_date")

        questions = plan_policy_questions(domain, packet)
        context = _retrieval_context(domain, packet)

        evidence: list[PolicyEvidence] = []
        statuses: list[str] = []
        review_reasons: list[str] = []
        seen: set[str] = set()

        for question in questions:
            result = retrieve_policy_tool(
                query=question["query"],
                product_domain=domain,
                application_id=state.get("application_id"),
                as_of_date=as_of,
                retriever=retriever,
                **context,
            )
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
            result = retrieve_policy_tool(
                query=f"What does rule {rule_id} say?",
                product_domain=domain,
                application_id=state.get("application_id"),
                as_of_date=as_of,
                retriever=retriever,
                top_k=3,
                **context,
            )
            statuses.append(f"dependency:{rule_id}:{result.status.value}")
            for item in result.evidence:
                if item.chunk_id not in seen:
                    seen.add(item.chunk_id)
                    evidence.append(item)

        update: dict[str, Any] = {
            "policy_questions": questions,
            "policy_dependencies": dependencies,
            "policy_evidence": evidence_to_state(evidence),
            "retrieval_statuses": statuses,
            "route": "eligibility",
            "steps": ["policy_retrieval"],
        "steps_taken": 1,
        }
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

    return policy_retrieval_node


def _retrieval_context(domain: LendingProductDomain, packet: dict[str, Any]) -> dict[str, Any]:
    if domain is LendingProductDomain.MORTGAGE:
        return {
            "product_family": packet.get("product_family"),
            "loan_purpose": packet.get("loan_purpose"),
            "occupancy_type": packet.get("occupancy_type"),
        }
    return {"product_code": packet.get("product_code")}


def eligibility_node(state: CredPilotState) -> dict[str, Any]:
    """Eligibility & Affordability Agent.

    Figures come from the deterministic calculators, thresholds from the policy
    the retriever returned, and the verdict from the rule engine. No language
    model participates in any of the three.
    """
    halt = _guard(state, "eligibility")
    if halt is not None:
        return halt

    from src import rules
    from src.calculations import compute_affordability

    domain = LendingProductDomain.from_any(state["loan_domain"])
    packet = state.get("application_packet") or {}
    evidence = state_evidence(state)

    calculations = compute_affordability(domain, packet)
    evaluations = rules.evaluate(domain, calculations, packet, evidence)
    eligibility = rules.summarize(evaluations)

    log_agent_action(
        actor="eligibility_agent",
        action="assess_eligibility",
        decision=eligibility["status"],
        application_id=state.get("application_id"),
        product_domain=domain.value,
        detail={
            "ratios": calculations.get("ratios", {}),
            "breaches": eligibility["breaches"],
            "indeterminate": eligibility["indeterminate"],
        },
    )

    update: dict[str, Any] = {
        "calculations": calculations,
        "eligibility": eligibility,
        "route": "risk",
        "steps": ["eligibility"],
        "steps_taken": 1,
    }
    if eligibility["status"] == "INDETERMINATE":
        update["requires_human_review"] = True
        update["human_review_reasons"] = [
            f"{e['measure']}: {e['detail']}" for e in eligibility["indeterminate"]
        ]
    return update


def risk_node(state: CredPilotState) -> dict[str, Any]:
    """Risk Screening Agent: deterministic flags from the packet plus policy."""
    halt = _guard(state, "risk")
    if halt is not None:
        return halt

    from src.calculations import screen_risk

    domain = LendingProductDomain.from_any(state["loan_domain"])
    packet = state.get("application_packet") or {}
    risk = screen_risk(domain, packet)

    if state.get("security_findings"):
        risk["flags"] = list(risk.get("flags", [])) + ["APPLICANT_TEXT_INSTRUCTION_ATTEMPT"]
        risk["level"] = "HIGH"

    log_agent_action(
        actor="risk_agent",
        action="screen_risk",
        decision=risk.get("level", "UNKNOWN"),
        application_id=state.get("application_id"),
        product_domain=domain.value,
        detail={"flags": risk.get("flags", [])},
    )
    return {
        "risk": risk,
        "route": "recommend",
        "steps": ["risk"],
        "steps_taken": 1,
    }


def recommendation_node(state: CredPilotState) -> dict[str, Any]:
    """Assemble the recommendation and decide whether a human must see it."""
    halt = _guard(state, "recommendation")
    if halt is not None:
        return halt

    from src.domain import LendingProductDomain as _Domain
    from src.review_triggers import evaluate_review_triggers

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
        _Domain.from_any(state["loan_domain"]),
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

    log_agent_action(
        actor="recommendation_agent",
        action="draft_recommendation",
        decision=outcome,
        application_id=state.get("application_id"),
        product_domain=state.get("loan_domain"),
        detail={
            "citations": recommendation["citations"],
            "requires_human_review": requires_review,
        },
    )

    return {
        "recommendation": recommendation,
        "requires_human_review": requires_review,
        "human_review_reasons": [r for r in reasons if r not in (state.get("human_review_reasons") or [])],
        "route": "narrative",
        "steps": ["recommendation"],
        "steps_taken": 1,
    }


def narrative_node(state: CredPilotState) -> dict[str, Any]:
    """Write the rationale, then check it against its own evidence.

    This is the only node a language model touches, and it runs *after* the
    decision exists. It receives the outcome as a fact and the figures
    pre-computed, so there is nothing here for a model to decide.

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

    scratchpad = Scratchpad(application_id=state.get("application_id") or "")
    result = draft_rationale(state, scratchpad=scratchpad)

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

    requires_review = state.get("requires_human_review") or not result.is_faithful
    update["route"] = "human_review" if requires_review else "done"

    # A file that ends here never reaches human_review, so this is its only
    # chance to leave a trace for the applicant's next visit.
    if not requires_review:
        update["memory_written"] = record_interaction({**state, **update})

    return update


def human_review_node(state: CredPilotState) -> dict[str, Any]:
    """Terminal node for files a human must decide."""
    record_interaction(state)
    log_agent_action(
        actor="supervisor",
        action="route_for_human_review",
        decision="HUMAN_REVIEW_REQUIRED",
        application_id=state.get("application_id"),
        product_domain=state.get("loan_domain"),
        detail={"reasons": state.get("human_review_reasons") or []},
    )
    return {"route": "done", "steps": ["human_review"], "steps_taken": 1}


# ======================================================================================
# Conditional edges
# ======================================================================================


def route_after_supervisor(state: CredPilotState) -> Literal["domain_router"]:
    return "domain_router"


def route_after_domain(state: CredPilotState) -> Literal["policy_retrieval", "human_review"]:
    return "human_review" if state.get("route") == "human_review" else "policy_retrieval"


def route_after_retrieval(state: CredPilotState) -> Literal["eligibility", "human_review"]:
    return "human_review" if state.get("route") == "human_review" else "eligibility"


def route_after_recommendation(state: CredPilotState) -> Literal["narrative", "human_review"]:
    """Every file gets a written rationale, including the ones a human will decide.

    A reviewer picking up a referred file needs the reasoning more than an
    auto-approved file does, so the narrative comes before the handoff, not
    instead of it.
    """
    return "human_review" if state.get("halted") else "narrative"


def route_after_narrative(state: CredPilotState) -> Literal["human_review", "__end__"]:
    return "human_review" if state.get("requires_human_review") else "__end__"


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
    """
    from langgraph.graph import END, START, StateGraph

    builder = StateGraph(CredPilotState)
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("domain_router", domain_router_node)
    builder.add_node("policy_retrieval", make_policy_retrieval_node(retriever))
    builder.add_node("eligibility", eligibility_node)
    builder.add_node("risk", risk_node)
    builder.add_node("recommendation", recommendation_node)
    builder.add_node("narrative", narrative_node)
    builder.add_node("human_review", human_review_node)

    builder.add_edge(START, "supervisor")
    builder.add_conditional_edges("supervisor", route_after_supervisor, ["domain_router"])
    builder.add_conditional_edges(
        "domain_router", route_after_domain, ["policy_retrieval", "human_review"]
    )
    builder.add_conditional_edges(
        "policy_retrieval", route_after_retrieval, ["eligibility", "human_review"]
    )
    builder.add_edge("eligibility", "risk")
    builder.add_edge("risk", "recommendation")
    builder.add_conditional_edges(
        "recommendation", route_after_recommendation,
        {"narrative": "narrative", "human_review": "human_review"},
    )
    builder.add_conditional_edges(
        "narrative", route_after_narrative,
        {"human_review": "human_review", "__end__": END},
    )
    builder.add_edge("human_review", END)

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
) -> CredPilotState:
    """Build the graph's initial state from a committed application packet.

    The packet is enriched with the committed underwriting *inputs* that do not
    appear on the application form — property tax, hazard premium, mortgage
    insurance, the verified liability set. See :mod:`src.application_context`,
    which refuses to read any table holding an outcome.
    """
    packet = build_underwriting_input(application_path)
    resolved_as_of = (
        str(as_of_date)
        if as_of_date
        else packet.get("underwriting_as_of_date")
        or packet.get("application_date")
        or (str(packet.get("submitted_at", ""))[:10] or None)
    )
    return {
        "application_id": packet.get("application_id", ""),
        "application_packet": packet,
        "as_of_date": resolved_as_of,
        "policy_evidence": [],
        "retrieval_statuses": [],
        "human_review_reasons": [],
        "security_findings": [],
        "errors": [],
        "steps": [],
        "session_id": session_id or uuid.uuid4().hex[:12],
        "subject_id": None,
        "recalled_memory": [],
        "step_budget": DEFAULT_STEP_BUDGET,
        "steps_taken": 0,
        "halted": False,
        "requires_human_review": False,
    }


__all__ = [
    "CHECKPOINT_DB",
    "CredPilotState",
    "EDUCATION_QUESTIONS",
    "MORTGAGE_QUESTIONS",
    "DEFAULT_STEP_BUDGET",
    "MAX_DEPENDENCY_FOLLOWS",
    "RECURSION_LIMIT",
    "budget_exhausted",
    "build_graph",
    "evidence_to_state",
    "narrative_node",
    "recall_prior_context",
    "record_interaction",
    "referenced_rules",
    "subject_of",
    "initial_state",
    "state_evidence",
    "plan_policy_questions",
    "get_config",
]
