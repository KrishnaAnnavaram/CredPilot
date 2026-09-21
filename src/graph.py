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

    # control
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


def supervisor_node(state: CredPilotState) -> dict[str, Any]:
    """Intake: quarantine untrusted text and decide where the file goes next."""
    packet = state.get("application_packet") or {}
    untrusted = packet.get("untrusted_applicant_text")

    quarantined = None
    findings: list[str] = []
    if untrusted:
        content = untrusted.get("content") if isinstance(untrusted, dict) else str(untrusted)
        quarantined = quarantine(content)
        findings = list(quarantined["injection_findings"])

    update: dict[str, Any] = {
        "untrusted_applicant_text": quarantined,
        "security_findings": findings,
        "steps": ["supervisor"],
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
    }


def make_policy_retrieval_node(retriever: PolicyRetriever | None = None):
    """Build the Policy Retrieval Agent node.

    It plans the questions the file raises, then calls the agentic-RAG tool once
    per question, scoped to the resolved product domain. It does not retrieve on
    every turn, and it never retrieves across products.
    """

    def policy_retrieval_node(state: CredPilotState) -> dict[str, Any]:
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
    }
    if eligibility["status"] == "INDETERMINATE":
        update["requires_human_review"] = True
        update["human_review_reasons"] = [
            f"{e['measure']}: {e['detail']}" for e in eligibility["indeterminate"]
        ]
    return update


def risk_node(state: CredPilotState) -> dict[str, Any]:
    """Risk Screening Agent: deterministic flags from the packet plus policy."""
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
    return {"risk": risk, "route": "recommend", "steps": ["risk"]}


def recommendation_node(state: CredPilotState) -> dict[str, Any]:
    """Assemble the recommendation and decide whether a human must see it."""
    eligibility = state.get("eligibility") or {}
    risk = state.get("risk") or {}
    evidence = state_evidence(state)

    breaches = eligibility.get("breaches") or []
    reasons = list(state.get("human_review_reasons") or [])
    requires_review = bool(state.get("requires_human_review"))

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
        "route": "human_review" if requires_review else "done",
        "steps": ["recommendation"],
    }


def human_review_node(state: CredPilotState) -> dict[str, Any]:
    """Terminal node for files a human must decide."""
    log_agent_action(
        actor="supervisor",
        action="route_for_human_review",
        decision="HUMAN_REVIEW_REQUIRED",
        application_id=state.get("application_id"),
        product_domain=state.get("loan_domain"),
        detail={"reasons": state.get("human_review_reasons") or []},
    )
    return {"route": "done", "steps": ["human_review"]}


# ======================================================================================
# Conditional edges
# ======================================================================================


def route_after_supervisor(state: CredPilotState) -> Literal["domain_router"]:
    return "domain_router"


def route_after_domain(state: CredPilotState) -> Literal["policy_retrieval", "human_review"]:
    return "human_review" if state.get("route") == "human_review" else "policy_retrieval"


def route_after_retrieval(state: CredPilotState) -> Literal["eligibility", "human_review"]:
    return "human_review" if state.get("route") == "human_review" else "eligibility"


def route_after_recommendation(state: CredPilotState) -> Literal["human_review", "__end__"]:
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
        "recommendation", route_after_recommendation, {"human_review": "human_review", "__end__": END}
    )
    builder.add_edge("human_review", END)

    context = None
    if checkpointer is None:
        from langgraph.checkpoint.sqlite import SqliteSaver

        path = checkpoint_path or CHECKPOINT_DB
        path.parent.mkdir(parents=True, exist_ok=True)
        context = SqliteSaver.from_conn_string(str(path))
        checkpointer = context.__enter__()

    return builder.compile(checkpointer=checkpointer), context


def initial_state(
    application_path: "str | Path",
    *,
    as_of_date: "str | date | None" = None,
    config: RagConfig | None = None,
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
        "requires_human_review": False,
    }


__all__ = [
    "CHECKPOINT_DB",
    "CredPilotState",
    "EDUCATION_QUESTIONS",
    "MORTGAGE_QUESTIONS",
    "MAX_DEPENDENCY_FOLLOWS",
    "build_graph",
    "evidence_to_state",
    "referenced_rules",
    "initial_state",
    "state_evidence",
    "plan_policy_questions",
    "get_config",
]
