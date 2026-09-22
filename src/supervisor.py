"""The Supervisor Agent: understand, clarify, route.

Every request reaches the Supervisor first. It produces one structured
:class:`SupervisorDecision` and nothing else — it does not retrieve, compute,
apply a threshold or decide an application. Its whole job is to work out what the
user is asking and which capability owns the answer.

Six routes, and the reason each exists:

``GENERAL``
    A greeting, a thank-you, a goodbye, "who are you". The Supervisor answers
    these itself. Running hybrid retrieval over a 42-document policy corpus to
    answer "hi" is not a capability, it is a cost — so no retrieval happens on
    this path and :func:`tests.test_supervisor` asserts it.
``CLARIFY``
    The request is real but underdetermined: "I need help with my loan" does not
    say whether it is a mortgage or an education loan, and guessing is the exact
    failure that product isolation exists to prevent. The Supervisor asks the
    **smallest** question that would resolve it, and the graph interrupts. When
    the answer arrives the original request is still on the checkpoint, and the
    two are combined and re-routed.
``MORTGAGE`` / ``EDUCATION_LOAN``
    Resolved to one product. Only that product's specialist runs, and only that
    product's corpus is searched.
``HUMAN_REVIEW``
    The request itself needs a person before anything else happens — an override
    request, a complaint, a dispute, an instruction to change a decision.
``OUT_OF_SCOPE``
    Not lending. Answered with a boundary, not a guess.

**Deterministic first, model second.** Classification runs a deterministic pass
over structured facts and unambiguous surface forms, and only falls through to
Gemini for the genuinely ambiguous middle. That ordering is not an optimisation:
an application packet carrying ``subject_property`` is a mortgage as a matter of
fact, and asking a language model to confirm it introduces a way for the answer
to be wrong. The model is also simply absent in a checkout with no key, and
routing has to work there.

The model, where it is used, may only choose among the enumerated routes and may
not invent a threshold, a decision or a policy statement; its output is validated
against the enum and falls back to ``CLARIFY`` when it does not parse.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Mapping, Sequence

from src.domain import (
    LendingProductDomain,
    ProductResolutionError,
    resolve_product_domain,
)


class Route(str, Enum):
    """Where the Supervisor sends a request."""

    GENERAL = "GENERAL"
    CLARIFY = "CLARIFY"
    MORTGAGE = "MORTGAGE"
    EDUCATION_LOAN = "EDUCATION_LOAN"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"

    @classmethod
    def from_any(cls, value: "str | Route | None") -> "Route | None":
        if value is None:
            return None
        if isinstance(value, cls):
            return value
        key = str(value).strip().upper().replace("-", "_").replace(" ", "_")
        aliases = {
            "EDUCATION": cls.EDUCATION_LOAN,
            "EDU": cls.EDUCATION_LOAN,
            "STUDENT_LOAN": cls.EDUCATION_LOAN,
            "MTG": cls.MORTGAGE,
            "HOME_LOAN": cls.MORTGAGE,
            "SMALL_TALK": cls.GENERAL,
            "GREETING": cls.GENERAL,
            "CLARIFICATION": cls.CLARIFY,
            "ESCALATE": cls.HUMAN_REVIEW,
            "HUMAN": cls.HUMAN_REVIEW,
            "OUT_OF_SCOPE_REQUEST": cls.OUT_OF_SCOPE,
        }
        if key in aliases:
            return aliases[key]
        try:
            return cls(key)
        except ValueError:
            return None


class ConversationType(str, Enum):
    """What kind of exchange this is, independent of which product it concerns."""

    GREETING = "GREETING"
    FAREWELL = "FAREWELL"
    GRATITUDE = "GRATITUDE"
    CAPABILITY_QUESTION = "CAPABILITY_QUESTION"
    POLICY_QUESTION = "POLICY_QUESTION"
    APPLICATION_ASSESSMENT = "APPLICATION_ASSESSMENT"
    STATUS_QUESTION = "STATUS_QUESTION"
    ESCALATION = "ESCALATION"
    AMBIGUOUS = "AMBIGUOUS"
    OFF_TOPIC = "OFF_TOPIC"


class Capability(str, Enum):
    """The capability a route hands the request to."""

    SUPERVISOR_DIRECT = "SUPERVISOR_DIRECT"
    POLICY_RETRIEVAL = "POLICY_RETRIEVAL"
    UNDERWRITING_ASSESSMENT = "UNDERWRITING_ASSESSMENT"
    HUMAN_REVIEW_QUEUE = "HUMAN_REVIEW_QUEUE"
    NONE = "NONE"


@dataclass
class SupervisorDecision:
    """The Supervisor's structured output. One per user turn."""

    intent: str
    normalized_question: str
    conversation_type: ConversationType
    domain: LendingProductDomain | None
    confidence: float
    required_capability: Capability
    clarification_required: bool
    route: Route
    routing_reason: str
    clarification_question: str | None = None
    missing_information: list[str] = field(default_factory=list)
    out_of_scope: bool = False
    decided_by: str = "deterministic"
    signals: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["conversation_type"] = self.conversation_type.value
        payload["required_capability"] = self.required_capability.value
        payload["route"] = self.route.value
        payload["domain"] = self.domain.value if self.domain else None
        return payload

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SupervisorDecision":
        return cls(
            intent=str(data.get("intent") or ""),
            normalized_question=str(data.get("normalized_question") or ""),
            conversation_type=ConversationType(
                data.get("conversation_type") or ConversationType.AMBIGUOUS.value
            ),
            domain=(
                LendingProductDomain.from_any(data["domain"]) if data.get("domain") else None
            ),
            confidence=float(data.get("confidence") or 0.0),
            required_capability=Capability(
                data.get("required_capability") or Capability.NONE.value
            ),
            clarification_required=bool(data.get("clarification_required")),
            route=Route.from_any(data.get("route")) or Route.CLARIFY,
            routing_reason=str(data.get("routing_reason") or ""),
            clarification_question=data.get("clarification_question"),
            missing_information=list(data.get("missing_information") or []),
            out_of_scope=bool(data.get("out_of_scope")),
            decided_by=str(data.get("decided_by") or "deterministic"),
            signals=list(data.get("signals") or []),
        )


# ======================================================================================
# Deterministic surface forms
# ======================================================================================

#: Whole-utterance greetings. Matched against the *whole* normalized message, not
#: searched inside it: "hi, what is the maximum DTI on a jumbo loan" is a policy
#: question that happens to open politely, and answering it with "Hello!" would
#: be a routing failure dressed up as friendliness.
_GREETINGS = frozenset(
    {
        "hi", "hii", "hiya", "hello", "hey", "heya", "yo", "howdy", "hi there",
        "hello there", "hey there", "good morning", "good afternoon", "good evening",
        "greetings", "morning", "afternoon", "evening", "namaste", "hola",
    }
)

_FAREWELLS = frozenset(
    {
        "bye", "byebye", "bye bye", "goodbye", "good bye", "see you", "see ya",
        "cheers", "later", "take care", "that is all", "that's all", "nothing else",
        "no thanks", "no thank you", "we are done", "we're done", "i am done",
        "i'm done", "exit", "quit",
    }
)

_GRATITUDE = frozenset(
    {
        "thanks", "thank you", "thanks a lot", "thank you very much", "thx", "ty",
        "much appreciated", "appreciate it", "great thanks", "perfect thanks",
        "thanks!", "cheers thanks", "thank u",
    }
)

#: "What are you / what can you do" — answered from the capability statement, not
#: from the policy corpus.
_CAPABILITY_PATTERNS = (
    re.compile(r"^(who|what) (are|r) (you|u)\b"),
    re.compile(r"^what (can|do) (you|u|credpilot) (do|help|handle|support)"),
    re.compile(r"^what is credpilot"),
    re.compile(r"^(tell me|explain) (about )?(yourself|credpilot)"),
    re.compile(r"^how (do|does) (you|this|credpilot) work"),
    re.compile(r"^(help|what are your capabilities|capabilities)$"),
    re.compile(r"^what (kinds?|types?) of loans?"),
)

#: Words that put a request in one product without ambiguity.
_MORTGAGE_TERMS = (
    "mortgage", "home loan", "house loan", "housing loan", "refinance my home",
    "cash-out refi", "cash out refi", "home equity", "property", "appraisal",
    "escrow", "ltv", "loan-to-value", "loan to value", "conforming", "jumbo",
    "fha", "va loan", "usda", "closing costs", "down payment", "homebuyer",
    "purchase a home", "buying a house", "buy a house", "primary residence",
    "investment property", "second home", "pmi", "private mortgage insurance",
    "amortization", "hoa",
)

_EDUCATION_TERMS = (
    "student loan", "education loan", "student-loan", "tuition", "college",
    "university", "undergraduate", "graduate school", "grad school", "campus",
    "school", "enrollment", "enrolment", "fafsa", "title iv",
    "cost of attendance", "semester", "degree", "scholarship", "f-1", "j-1",
    "sevis", "opt", "study abroad", "student visa", "refinance my student",
    "education refinance", "medical school", "law school", "mba",
)

#: A term that sits in both products is not a discriminator, and treating one as
#: though it were is how a student-loan question gets answered out of the
#: mortgage corpus.
#:
#: ``cosigner`` was on the education list until a test asked what one *is*.
#: Both products take cosigners — mortgage under co-borrower rules, education
#: under ``EDU-COS`` — so the word says nothing about which corpus answers the
#: question. The same is true of ``refinance``: there is a cash-out refinance
#: and there is an education refinance, and they share no rule.
_SHARED_TERMS = ("refinance", "refinancing", "refi", "loan", "credit score", "dti",
                 "debt to income", "debt-to-income", "interest rate", "apr",
                 "cosigner", "co-signer", "cosign", "reserves", "underwriting",
                 "eligibility", "income verification", "documentation")

#: Requests a person must own. An automated system changing its own decision on
#: being asked to is the failure mode POL-UWR-001 exists to prevent.
_ESCALATION_PATTERNS = (
    re.compile(r"\boverride\b"),
    # "connect me with an underwriter" needs two filler words, not one: the
    # earlier pattern allowed "connect me an underwriter" and "connect with an
    # underwriter" but not the phrasing anyone actually uses.
    re.compile(r"\b(speak|talk|connect|escalate|refer|transfer)\s+"
               r"(?:(?:to|with|me|us)\s+){0,2}(?:a|an|the)?\s*"
               r"(human|person|agent|underwriter|manager|supervisor|representative|"
               r"someone|somebody)\b"),
    re.compile(r"\b(complaint|complain|dispute|appeal|discriminat)\w*\b"),
    re.compile(r"\b(change|reverse|overturn|reconsider)\s+(the\s+|my\s+|this\s+)?"
               r"(decision|decline|denial|outcome|recommendation)\b"),
    re.compile(r"\b(ignore|bypass|waive|skip)\s+(the\s+)?(policy|rule|threshold|limit|check)"),
    re.compile(r"\bapprove\s+(me|it|this|my\s+\w+)\s+anyway\b"),
    re.compile(r"\bsue\b|\blawyer\b|\blegal action\b|\bregulator\b"),
)

#: Clearly not lending. Kept narrow on purpose — a false OUT_OF_SCOPE refuses a
#: real applicant, which is worse than a needless clarification.
_OFF_TOPIC_PATTERNS = (
    re.compile(r"\b(weather|football|cricket|movie|recipe|joke|poem|song|lyrics)\b"),
    re.compile(r"\bwrite\s+(me\s+)?(a|an|some)\s+(python|javascript|java|c\+\+|sql|code|script|program)\b"),
    re.compile(r"\b(stock|crypto|bitcoin|forex)\s+(tip|advice|price|prediction)"),
    re.compile(r"\bwho (won|is the president|is the prime minister)\b"),
    re.compile(r"\b(medical|health|legal|tax)\s+advice\b"),
    re.compile(r"\bcar insurance|life insurance|travel booking|flight booking\b"),
)

#: Utterances that say "loan" and nothing that resolves which one.
_AMBIGUOUS_PATTERNS = (
    re.compile(r"^(i need|i want|i'd like|i would like|can you|could you|please)\s+"
               r"(some\s+)?help\b"),
    re.compile(r"^help( me)?\b.*\bloan\b"),
    re.compile(r"\bmy (loan|application|file|case)\b"),
    re.compile(r"^(what|how) (about|do i|can i)\b.*\bloan\b"),
    re.compile(r"^i (have|had) a question\b"),
)

#: The clarification the Supervisor asks when the product is the missing fact.
PRODUCT_CLARIFICATION = (
    "Is this about a **home mortgage** or a **private education (student) loan**? "
    "CredPilot underwrites the two separately, and the policy that applies is "
    "different for each."
)

#: What CredPilot answers "what can you do" with. Written here, not retrieved:
#: it is a statement about this system, and the policy corpus does not contain
#: one.
CAPABILITY_STATEMENT = (
    "I am CredPilot, a loan origination and underwriting copilot. I work on two "
    "products, kept strictly separate: **U.S. residential mortgages** and "
    "**private education loans**.\n\n"
    "For either one I can:\n"
    "- retrieve the lending policy that governed a file on the day it was underwritten, "
    "including the right version of it;\n"
    "- compute affordability — DTI, LTV, reserves, funds to close, residual income — "
    "deterministically, never by asking a language model to do arithmetic;\n"
    "- evaluate the retrieved rules against those figures and report any breach with "
    "the threshold it failed and the rule that set it;\n"
    "- recommend approve, refer or decline, with a written rationale whose every "
    "citation and figure is checked back against the evidence;\n"
    "- route the file to a human wherever policy requires it — every decline, every "
    "high-value case, and anything where the evidence conflicts or is missing.\n\n"
    "I do not make the credit decision. A person does."
)

GREETING_RESPONSE = (
    "Hello — I am CredPilot, a loan origination and underwriting copilot for "
    "mortgages and private education loans. What can I help you with?"
)

FAREWELL_RESPONSE = (
    "Goodbye. Anything we discussed stays on this thread, so you can pick it up "
    "again next time."
)

GRATITUDE_RESPONSE = "You are welcome. Anything else I can look at?"

OUT_OF_SCOPE_RESPONSE = (
    "That is outside what I do. I am a loan origination and underwriting copilot "
    "for U.S. residential mortgages and private education loans — I can retrieve "
    "the lending policy that applies, compute affordability, and explain a "
    "recommendation and the rule behind it. I cannot help with anything else, and "
    "I would rather say so than give you an answer I have no basis for."
)

ESCALATION_RESPONSE = (
    "I am routing this to a human. Decisions, overrides, disputes and complaints "
    "are a person's to make, not mine — I have recorded the request with the "
    "reason and the reference for this conversation so a reviewer picks it up with "
    "the full context."
)


def normalize(message: str | None) -> str:
    """Lower-case, collapse whitespace, strip terminal punctuation."""
    if not message:
        return ""
    text = re.sub(r"\s+", " ", str(message)).strip().lower()
    return text.strip(" .!?,;:")


def _contains_any(text: str, terms: Sequence[str]) -> list[str]:
    return [t for t in terms if t in text]


def product_signals(text: str) -> tuple[list[str], list[str]]:
    """Mortgage and education terms present in the text."""
    return _contains_any(text, _MORTGAGE_TERMS), _contains_any(text, _EDUCATION_TERMS)


def looks_like_greeting(text: str) -> bool:
    """A whole-utterance greeting, not a greeting with a question attached."""
    if text in _GREETINGS:
        return True
    # "hi there credpilot", "hello credpilot" — still nothing being asked.
    stripped = re.sub(r"\b(credpilot|bot|assistant|there|again)\b", "", text).strip()
    return bool(stripped) and stripped in _GREETINGS


def looks_like_farewell(text: str) -> bool:
    return text in _FAREWELLS


def looks_like_gratitude(text: str) -> bool:
    if text in _GRATITUDE:
        return True
    return bool(re.fullmatch(r"(ok(ay)?|great|perfect|cool|nice|good)?\s*,?\s*"
                             r"thank(s| you)( so much| very much| a lot)?\s*!*", text))


def looks_like_capability_question(text: str) -> bool:
    return any(pattern.search(text) for pattern in _CAPABILITY_PATTERNS)


def looks_like_escalation(text: str) -> bool:
    return any(pattern.search(text) for pattern in _ESCALATION_PATTERNS)


def looks_off_topic(text: str) -> bool:
    if any(pattern.search(text) for pattern in _OFF_TOPIC_PATTERNS):
        # An off-topic pattern inside an otherwise-lending question is not
        # off-topic: "does the weather where the property is affect the hazard
        # premium" is a mortgage question.
        mortgage, education = product_signals(text)
        return not (mortgage or education)
    return False


def looks_ambiguous(text: str) -> bool:
    return any(pattern.search(text) for pattern in _AMBIGUOUS_PATTERNS)


def mentions_lending(text: str) -> bool:
    mortgage, education = product_signals(text)
    return bool(mortgage or education or _contains_any(text, _SHARED_TERMS))


# ======================================================================================
# Classification
# ======================================================================================


def classify(
    message: str | None,
    *,
    application_packet: Mapping[str, Any] | None = None,
    application_id: str | None = None,
    explicit_domain: "str | LendingProductDomain | None" = None,
    prior_domain: "str | LendingProductDomain | None" = None,
    clarification_context: str | None = None,
    use_model: bool = False,
) -> SupervisorDecision:
    """Classify one user turn into a :class:`SupervisorDecision`.

    ``clarification_context`` is the question that was pending when the user was
    asked to clarify. When it is present the reply is read **as an answer to that
    question**, combined with the original, and the pair routed — which is what
    makes "mortgage" a complete request rather than a one-word utterance nobody
    can act on.
    """
    raw = (message or "").strip()
    combined_raw = f"{clarification_context} {raw}".strip() if clarification_context else raw
    text = normalize(combined_raw)
    turn_text = normalize(raw)
    signals: list[str] = []

    # ---- 1. A structured application always wins ------------------------------
    # A packet carrying `subject_property` is a mortgage as a matter of fact. No
    # amount of free text changes that, and nothing is asked of a model.
    if application_packet or application_id or explicit_domain:
        try:
            domain = resolve_product_domain(
                explicit_domain=explicit_domain,
                application_id=application_id,
                packet=application_packet,
            )
        except ProductResolutionError as exc:
            return SupervisorDecision(
                intent="assess_application",
                normalized_question=combined_raw or "assess this application",
                conversation_type=ConversationType.APPLICATION_ASSESSMENT,
                domain=None,
                confidence=0.4,
                required_capability=Capability.UNDERWRITING_ASSESSMENT,
                clarification_required=True,
                route=Route.CLARIFY,
                routing_reason=str(exc),
                clarification_question=PRODUCT_CLARIFICATION,
                missing_information=["lending product"],
                signals=["application_supplied", "product_unresolved"],
            )
        signals.append("structured_application")
        return SupervisorDecision(
            intent="assess_application",
            normalized_question=combined_raw or f"assess application {application_id or ''}".strip(),
            conversation_type=ConversationType.APPLICATION_ASSESSMENT,
            domain=domain,
            confidence=1.0,
            required_capability=Capability.UNDERWRITING_ASSESSMENT,
            clarification_required=False,
            route=Route.MORTGAGE if domain is LendingProductDomain.MORTGAGE
            else Route.EDUCATION_LOAN,
            routing_reason=(
                f"the application packet resolves to {domain.value} from structured "
                f"facts, so no product inference is needed"
            ),
            signals=signals,
        )

    if not text:
        return SupervisorDecision(
            intent="empty_request",
            normalized_question="",
            conversation_type=ConversationType.AMBIGUOUS,
            domain=None,
            confidence=1.0,
            required_capability=Capability.SUPERVISOR_DIRECT,
            clarification_required=True,
            route=Route.CLARIFY,
            routing_reason="nothing was asked",
            clarification_question="What would you like help with?",
            missing_information=["the request itself"],
            signals=["empty"],
        )

    # ---- 2. Social turns, answered directly -----------------------------------
    # Checked before anything else touches retrieval. This is the requirement
    # that greetings must not invoke RAG, and it is enforced by never reaching a
    # route that can.
    if looks_like_greeting(turn_text) and not mentions_lending(turn_text):
        return _direct(
            "greet", combined_raw, ConversationType.GREETING,
            "a greeting with nothing asked; answered by the Supervisor without retrieval",
            ["whole_utterance_greeting"],
        )
    if looks_like_farewell(turn_text):
        return _direct(
            "farewell", combined_raw, ConversationType.FAREWELL,
            "a closing turn; answered by the Supervisor without retrieval",
            ["whole_utterance_farewell"],
        )
    if looks_like_gratitude(turn_text) and not mentions_lending(turn_text):
        return _direct(
            "thanks", combined_raw, ConversationType.GRATITUDE,
            "an acknowledgement; answered by the Supervisor without retrieval",
            ["whole_utterance_gratitude"],
        )
    if looks_like_capability_question(text):
        return _direct(
            "describe_capabilities", combined_raw, ConversationType.CAPABILITY_QUESTION,
            "a question about this system, answered from its capability statement "
            "rather than from the lending-policy corpus",
            ["capability_question"],
        )

    # ---- 3. Escalation ---------------------------------------------------------
    if looks_like_escalation(text):
        return SupervisorDecision(
            intent="escalate_to_human",
            normalized_question=combined_raw,
            conversation_type=ConversationType.ESCALATION,
            domain=_domain_hint(text, prior_domain),
            confidence=0.9,
            required_capability=Capability.HUMAN_REVIEW_QUEUE,
            clarification_required=False,
            route=Route.HUMAN_REVIEW,
            routing_reason=(
                "the request asks for a decision, an override or a dispute to be "
                "handled, which is a person's to own (POL-UWR-001 UWR-HRV-001)"
            ),
            signals=["escalation_language"],
        )

    # ---- 4. Out of scope -------------------------------------------------------
    if looks_off_topic(text):
        return SupervisorDecision(
            intent="out_of_scope",
            normalized_question=combined_raw,
            conversation_type=ConversationType.OFF_TOPIC,
            domain=None,
            confidence=0.85,
            required_capability=Capability.NONE,
            clarification_required=False,
            route=Route.OUT_OF_SCOPE,
            routing_reason="the request is not about lending",
            out_of_scope=True,
            signals=["off_topic_pattern"],
        )

    # ---- 5. Product resolution from language ----------------------------------
    mortgage_hits, education_hits = product_signals(text)
    if mortgage_hits and not education_hits:
        return _product(
            LendingProductDomain.MORTGAGE, combined_raw, mortgage_hits,
            f"mortgage-specific terms present ({', '.join(mortgage_hits[:3])}) and no "
            f"education-specific term",
        )
    if education_hits and not mortgage_hits:
        return _product(
            LendingProductDomain.EDUCATION_LOAN, combined_raw, education_hits,
            f"education-specific terms present ({', '.join(education_hits[:3])}) and no "
            f"mortgage-specific term",
        )
    if mortgage_hits and education_hits:
        # Both products named in one request. Not a routing problem to solve by
        # picking the one with more hits — the answer differs per product and
        # giving one of them silently is the isolation failure.
        return SupervisorDecision(
            intent="ambiguous_product",
            normalized_question=combined_raw,
            conversation_type=ConversationType.AMBIGUOUS,
            domain=None,
            confidence=0.55,
            required_capability=Capability.POLICY_RETRIEVAL,
            clarification_required=True,
            route=Route.CLARIFY,
            routing_reason=(
                "both a mortgage term and an education-loan term appear; the policy "
                "that applies differs by product, so the answer cannot be given for "
                "both at once"
            ),
            clarification_question=PRODUCT_CLARIFICATION,
            missing_information=["lending product"],
            signals=[f"mortgage:{','.join(mortgage_hits[:3])}",
                     f"education:{','.join(education_hits[:3])}"],
        )

    # ---- 6. Carry the product forward within a thread --------------------------
    # A follow-up ("and what about the reserves requirement?") inherits the
    # product from earlier in the conversation rather than asking again.
    # Anything that is a greeting, an escalation or off-topic has already
    # returned above, so what reaches here in a scoped thread is a substantive
    # follow-up — and a follow-up is about the product the thread is about.
    # Requiring a lending *term* as well was too strict: "and what about the
    # reserves requirement?" names no product and obviously inherits one.
    carried = LendingProductDomain.from_any(prior_domain) if prior_domain else None
    if carried is not None:
        return _product(
            carried, combined_raw, [],
            f"a follow-up in a thread already scoped to {carried.value}; the product "
            f"is carried forward rather than asked again",
            confidence=0.75, signals=["carried_from_thread"],
        )

    # ---- 7. Ambiguous ----------------------------------------------------------
    if looks_ambiguous(text) or mentions_lending(text):
        decision = SupervisorDecision(
            intent="ambiguous_request",
            normalized_question=combined_raw,
            conversation_type=ConversationType.AMBIGUOUS,
            domain=None,
            confidence=0.5,
            required_capability=Capability.POLICY_RETRIEVAL,
            clarification_required=True,
            route=Route.CLARIFY,
            routing_reason=(
                "the request concerns lending but names no product, and the two "
                "corpora answer it differently"
            ),
            clarification_question=PRODUCT_CLARIFICATION,
            missing_information=["lending product"],
            signals=["ambiguous_pattern"],
        )
        if use_model:
            refined = _classify_with_model(combined_raw, prior_domain=prior_domain)
            if refined is not None:
                return refined
        return decision

    # ---- 8. Nothing matched ----------------------------------------------------
    if use_model:
        refined = _classify_with_model(combined_raw, prior_domain=prior_domain)
        if refined is not None:
            return refined

    return SupervisorDecision(
        intent="unclassified",
        normalized_question=combined_raw,
        conversation_type=ConversationType.AMBIGUOUS,
        domain=None,
        confidence=0.35,
        required_capability=Capability.NONE,
        clarification_required=True,
        route=Route.CLARIFY,
        routing_reason=(
            "no lending signal was found and the request is not a recognised social "
            "turn; asking is safer than guessing which of the two corpora to search"
        ),
        clarification_question=(
            "I want to make sure I help with the right thing. Is this about a "
            "**mortgage**, a **private education loan**, or something else?"
        ),
        missing_information=["lending product", "what is being asked"],
        signals=["no_match"],
    )


def _direct(
    intent: str, question: str, kind: ConversationType, reason: str, signals: list[str]
) -> SupervisorDecision:
    return SupervisorDecision(
        intent=intent,
        normalized_question=question,
        conversation_type=kind,
        domain=None,
        confidence=0.95,
        required_capability=Capability.SUPERVISOR_DIRECT,
        clarification_required=False,
        route=Route.GENERAL,
        routing_reason=reason,
        signals=signals,
    )


def _product(
    domain: LendingProductDomain,
    question: str,
    hits: list[str],
    reason: str,
    *,
    confidence: float = 0.9,
    signals: list[str] | None = None,
) -> SupervisorDecision:
    return SupervisorDecision(
        intent=f"{domain.corpus_key}_policy_question",
        normalized_question=question,
        conversation_type=ConversationType.POLICY_QUESTION,
        domain=domain,
        confidence=confidence,
        required_capability=Capability.POLICY_RETRIEVAL,
        clarification_required=False,
        route=Route.MORTGAGE if domain is LendingProductDomain.MORTGAGE
        else Route.EDUCATION_LOAN,
        routing_reason=reason,
        signals=signals or [f"term:{h}" for h in hits[:4]],
    )


def _domain_hint(
    text: str, prior_domain: "str | LendingProductDomain | None"
) -> LendingProductDomain | None:
    mortgage_hits, education_hits = product_signals(text)
    if mortgage_hits and not education_hits:
        return LendingProductDomain.MORTGAGE
    if education_hits and not mortgage_hits:
        return LendingProductDomain.EDUCATION_LOAN
    return LendingProductDomain.from_any(prior_domain) if prior_domain else None


# ======================================================================================
# The model path — only for what the deterministic pass could not settle
# ======================================================================================

_MODEL_SYSTEM = """\
You are the routing component of CredPilot, a loan underwriting copilot. You do \
exactly one thing: read a user's message and say which capability should handle \
it. You never answer the question, never state a policy, never quote a \
threshold, never make or comment on an underwriting decision.

CredPilot serves two products and keeps them strictly apart:
  MORTGAGE        U.S. residential mortgage lending
  EDUCATION_LOAN  private education / student lending

Choose exactly one route:
  GENERAL         greeting, farewell, thanks, or a question about what CredPilot is
  CLARIFY         a lending request whose product is not determined
  MORTGAGE        clearly and only about mortgage lending
  EDUCATION_LOAN  clearly and only about education lending
  HUMAN_REVIEW    asks for an override, a decision change, a dispute or a person
  OUT_OF_SCOPE    not about lending at all

If the product is not certain, choose CLARIFY. Guessing sends the request to the \
wrong policy corpus, which is worse than asking one short question.

Reply with JSON only, no prose and no code fence:
{"route": "...", "domain": "MORTGAGE" | "EDUCATION_LOAN" | null,
 "intent": "short_snake_case", "confidence": 0.0-1.0,
 "clarification_question": "one short question, or null",
 "missing_information": ["..."], "routing_reason": "one sentence"}
"""


def _classify_with_model(
    message: str, *, prior_domain: "str | LendingProductDomain | None" = None
) -> SupervisorDecision | None:
    """Ask Gemini to route what the deterministic pass could not.

    Returns ``None`` on any failure — no key, no network, unparseable output —
    and the caller keeps its deterministic answer. Routing must work in a
    checkout with no API key, so the model is an improvement on the ambiguous
    middle and never a dependency.
    """
    try:
        from src import llm
        from src.observability.tracing import SPAN_KIND_THINKING, span

        status = llm.probe()
        if not status.available:
            return None

        prompt = _MODEL_SYSTEM + "\n\nUser message:\n" + message[:2000]
        with span(
            "supervisor.classify",
            span_kind=SPAN_KIND_THINKING,
            model=status.model,
            agent="supervisor",
        ) as sp:
            model = llm.chat_model(status.model, temperature=0.0)
            response = model.invoke(prompt)
            text = llm.message_text(response).strip()
            usage = llm.usage_of(response)
            sp.set(
                input_tokens=usage.get("input_tokens", 0),
                output_tokens=usage.get("output_tokens", 0),
                total_tokens=usage.get("total_tokens", 0),
                llm_call=True,
            )
    except Exception:  # noqa: BLE001 - routing must not depend on a model
        return None

    payload = _parse_json(text)
    if not payload:
        return None

    route = Route.from_any(payload.get("route"))
    if route is None:
        return None

    domain: LendingProductDomain | None = None
    if payload.get("domain"):
        try:
            domain = LendingProductDomain.from_any(payload["domain"])
        except ValueError:
            domain = None
    if route is Route.MORTGAGE:
        domain = LendingProductDomain.MORTGAGE
    elif route is Route.EDUCATION_LOAN:
        domain = LendingProductDomain.EDUCATION_LOAN
    elif route is Route.CLARIFY:
        domain = None

    clarification = payload.get("clarification_question") or PRODUCT_CLARIFICATION
    return SupervisorDecision(
        intent=str(payload.get("intent") or "model_classified"),
        normalized_question=message,
        conversation_type=(
            ConversationType.POLICY_QUESTION
            if route in (Route.MORTGAGE, Route.EDUCATION_LOAN)
            else ConversationType.AMBIGUOUS if route is Route.CLARIFY
            else ConversationType.ESCALATION if route is Route.HUMAN_REVIEW
            else ConversationType.OFF_TOPIC if route is Route.OUT_OF_SCOPE
            else ConversationType.CAPABILITY_QUESTION
        ),
        domain=domain,
        confidence=min(max(float(payload.get("confidence") or 0.6), 0.0), 1.0),
        required_capability=(
            Capability.POLICY_RETRIEVAL
            if route in (Route.MORTGAGE, Route.EDUCATION_LOAN)
            else Capability.HUMAN_REVIEW_QUEUE if route is Route.HUMAN_REVIEW
            else Capability.SUPERVISOR_DIRECT if route is Route.GENERAL
            else Capability.NONE
        ),
        clarification_required=route is Route.CLARIFY,
        route=route,
        routing_reason=str(payload.get("routing_reason") or "classified by the model"),
        clarification_question=clarification if route is Route.CLARIFY else None,
        missing_information=list(payload.get("missing_information") or []),
        out_of_scope=route is Route.OUT_OF_SCOPE,
        decided_by="gemini",
        signals=["model_classified"],
    )


def _parse_json(text: str) -> dict[str, Any] | None:
    """Parse the model's reply, tolerating a code fence around it."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z]*\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        return None
    try:
        payload = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def general_answer(decision: SupervisorDecision) -> str:
    """The Supervisor's own answer for a ``GENERAL`` turn. No retrieval."""
    return {
        ConversationType.GREETING: GREETING_RESPONSE,
        ConversationType.FAREWELL: FAREWELL_RESPONSE,
        ConversationType.GRATITUDE: GRATITUDE_RESPONSE,
        ConversationType.CAPABILITY_QUESTION: CAPABILITY_STATEMENT,
    }.get(decision.conversation_type, CAPABILITY_STATEMENT)


__all__ = [
    "CAPABILITY_STATEMENT",
    "Capability",
    "ConversationType",
    "ESCALATION_RESPONSE",
    "FAREWELL_RESPONSE",
    "GRATITUDE_RESPONSE",
    "GREETING_RESPONSE",
    "OUT_OF_SCOPE_RESPONSE",
    "PRODUCT_CLARIFICATION",
    "Route",
    "SupervisorDecision",
    "classify",
    "general_answer",
    "looks_ambiguous",
    "looks_like_capability_question",
    "looks_like_escalation",
    "looks_like_farewell",
    "looks_like_gratitude",
    "looks_like_greeting",
    "looks_off_topic",
    "mentions_lending",
    "normalize",
    "product_signals",
]
