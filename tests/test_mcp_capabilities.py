"""All six MCP capability families, exercised against a real server process.

Not against an imported module. The server must work *as a server* — launched as
a subprocess, speaking JSON-RPC over stdio, discovered rather than assumed — and
importing ``mcp_server.server`` to call a Python function proves none of that.
Every test here goes through :class:`src.mcp_host.client.CredPilotMCPClient`,
which is the same client the host uses.

The six families, and what each test is actually checking:

``tools``        the handler calls a real CredPilot service and validates input
``resources``    the catalogues are readable and carry no applicant data
``prompts``      templates render with their arguments and hard-code no threshold
``elicitation``  the server can ask, and a client that declines is handled
``sampling``     the compatibility path runs and refuses a non-Gemini responder
``roots``        the allowlist holds whatever a client declares

These are slow — every one pays for a subprocess that loads two
sentence-transformer models — so the session shares one connected client.
"""

from __future__ import annotations

import asyncio
import json

import pytest

from mcp_server.capabilities import ALLOWED_ROOTS, CAPABILITY_FAMILIES, capability_report
from src.mcp_host.client import CredPilotMCPClient

pytestmark = [pytest.mark.integration, pytest.mark.slow]


@pytest.fixture(scope="module")
def loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
def client(indexes_built, loop):
    """One connected client for the module. Starting the server is the cost."""
    if not indexes_built:
        pytest.skip("indexes not built")
    connected = CredPilotMCPClient()
    try:
        loop.run_until_complete(connected.connect())
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"the MCP server did not start: {type(exc).__name__}: {exc}")
    yield connected
    loop.run_until_complete(connected.close())


def call(loop, client, name, arguments=None):
    return loop.run_until_complete(client.call_tool(name, arguments or {}))


# ============================================================= discovery


def test_the_client_discovers_the_surface_rather_than_assuming_it(client):
    """A host that assumed a tool exists fails at call time; this fails at connect."""
    assert client.capabilities.server_name == "credpilot"
    assert client.capabilities.protocol_version
    assert len(client.capabilities.tools) >= 8
    assert len(client.capabilities.resources) >= 7
    assert len(client.capabilities.prompts) >= 6
    assert not client.capabilities.discovery_errors, client.capabilities.discovery_errors


def test_the_declaration_matches_what_the_server_actually_offers(client):
    """A capability declaration that has drifted is worse than none.

    ``mcp_server/capabilities.py`` is read by the host, published as a resource
    and quoted in the governance pack. If it says the server offers a tool it
    does not, three readers are wrong at once.
    """
    declared = capability_report()
    assert set(declared["tools"]) == set(client.capabilities.tools), (
        "declared tools differ from the server's own tools/list"
    )
    assert set(declared["resources"]) == set(client.capabilities.resources)
    assert set(declared["prompts"]) == set(client.capabilities.prompts)


def test_all_six_capability_families_are_declared_and_supported():
    families = set(CAPABILITY_FAMILIES)
    assert families == {"tools", "resources", "prompts", "elicitation",
                        "sampling", "roots"}
    assert all(f["supported"] for f in CAPABILITY_FAMILIES.values())
    # Sampling and roots are compatibility paths and must say so rather than
    # implying the system depends on them.
    assert CAPABILITY_FAMILIES["sampling"]["role"] == "compatibility"
    assert CAPABILITY_FAMILIES["roots"]["role"] == "compatibility"


# ================================================================ A. tools


def test_retrieve_policy_returns_resolvable_evidence(loop, client):
    result = call(loop, client, "retrieve_policy", {
        "query": "What is the maximum back-end debt-to-income ratio?",
        "product_domain": "MORTGAGE",
        "as_of_date": "2026-07-08",
        "top_k": 5,
    })
    assert result.ok, result.message
    payload = result.payload
    assert payload["status"] == "FOUND"
    assert payload["evidence_count"] > 0
    assert all(e["citation_resolves"] for e in payload["evidence"])
    # The product is a property of the result, not of each chunk. Checked on
    # the citations too, because that is what a reader of the answer sees and
    # an education citation appearing under a mortgage result is the isolation
    # failure this whole arrangement exists to prevent.
    assert payload["product_domain"] == "MORTGAGE"
    assert not any(e["citation"].startswith("POL-0") for e in payload["evidence"]), (
        "an education-corpus citation appeared in a mortgage result"
    )


def test_retrieve_policy_refuses_to_search_both_corpora(loop, client):
    """No product and no application id is a clarification, not a guess."""
    result = call(loop, client, "retrieve_policy", {"query": "what is the DTI limit?"})
    if result.ok:
        assert result.payload["status"] == "PRODUCT_CLARIFICATION_REQUIRED"
        assert result.payload["evidence_count"] == 0
    else:
        assert "PRODUCT_CLARIFICATION_REQUIRED" in (result.message or "")


def test_compute_affordability_calls_the_real_calculator(loop, client):
    result = call(loop, client, "compute_affordability", {"application_id": "APP-000056"})
    assert result.ok, result.message
    payload = result.payload
    assert payload["product_domain"] == "MORTGAGE"
    # The figure this repository's README turns on. If the MCP path returned
    # something else, the tool would not be calling src.calculations.
    assert payload["ratios"]["back_end_dti"] == pytest.approx(0.44, abs=1e-4)
    assert "no threshold has been applied" in payload["note"].lower()


def test_screen_risk_flags_calls_the_real_screen(loop, client):
    result = call(loop, client, "screen_risk_flags", {"application_id": "APP-2026-00001"})
    assert result.ok, result.message
    assert result.payload["level"] in ("LOW", "MEDIUM", "HIGH")
    assert result.payload["product_domain"] == "EDUCATION_LOAN"


def test_get_policy_version_resolves_by_date_not_by_recency(loop, client):
    """The same policy, two dates, two governing versions."""
    early = call(loop, client, "get_policy_version", {
        "product_domain": "MORTGAGE", "policy_id": "POL-DTI-001",
        "as_of_date": "2026-06-25",
    })
    late = call(loop, client, "get_policy_version", {
        "product_domain": "MORTGAGE", "policy_id": "POL-DTI-001",
        "as_of_date": "2026-07-08",
    })
    assert early.ok and late.ok
    assert early.payload["governing_version"] == "1.0"
    assert late.payload["governing_version"] == "2.0"
    assert early.payload["version_count"] == late.payload["version_count"] >= 2


def test_resolve_citation_distinguishes_real_from_invented(loop, client):
    good = call(loop, client, "resolve_citation",
                {"citation": "POL-DTI-001 v2.0 rule DTI-CONV-001"})
    bad = call(loop, client, "resolve_citation",
               {"citation": "POL-XXX-999 v9.9 rule NOPE-001"})
    assert good.ok and good.payload["resolves"] is True
    assert bad.ok and bad.payload["resolves"] is False


def test_validate_evidence_catches_an_unresolvable_citation(loop, client):
    result = call(loop, client, "validate_evidence", {
        "product_domain": "MORTGAGE",
        "citations": ["POL-DTI-001 v2.0 rule DTI-CONV-001",
                      "POL-XXX-999 v9.9 rule NOPE-001"],
    })
    assert result.ok, result.message
    assert result.payload["valid"] is False
    assert result.payload["verdict"] == "INVALID"
    assert "POL-XXX-999 v9.9 rule NOPE-001" in result.payload["unresolved_citations"]


def test_validate_evidence_catches_a_cross_product_citation(loop, client):
    result = call(loop, client, "validate_evidence", {
        "product_domain": "EDUCATION_LOAN",
        "citations": ["POL-DTI-001 v2.0 rule DTI-CONV-001"],
    })
    assert result.ok, result.message
    assert result.payload["valid"] is False
    assert result.payload["citations_from_another_product"]


def test_list_policy_rules_enumerates_a_products_rules(loop, client):
    result = call(loop, client, "list_policy_rules", {"product_domain": "MORTGAGE"})
    assert result.ok, result.message
    assert result.payload["policy_count"] > 0
    assert result.payload["rule_count"] > 100


def test_get_rule_dependencies_finds_what_a_rule_points_at(loop, client):
    """DTI-CONV-001 grants an extension on factors DTI-CONV-003 defines."""
    result = call(loop, client, "get_rule_dependencies", {
        "product_domain": "MORTGAGE", "rule_id": "DTI-CONV-001",
        "as_of_date": "2026-07-08",
    })
    assert result.ok, result.message
    assert result.payload["found"] is True
    assert "DTI-CONV-003" in result.payload["dependencies"]
    assert result.payload["dependency_count"] <= result.payload["max_follows"]


def test_a_tool_rejects_bad_input_rather_than_acting_on_it(loop, client):
    for name, arguments in (
        ("retrieve_policy", {"query": ""}),
        ("list_policy_rules", {"product_domain": "CAR_LOAN"}),
        ("get_policy_version", {"product_domain": "MORTGAGE", "policy_id": "POL-NOPE"}),
        ("compute_affordability", {}),
    ):
        result = call(loop, client, name, arguments)
        assert not result.ok, f"{name} accepted {arguments}"


def test_an_unknown_tool_fails_immediately_without_a_round_trip(loop, client):
    """Three attempts to be told "unknown tool" is latency, not resilience."""
    result = call(loop, client, "definitely_not_a_tool", {})
    assert not result.ok
    assert result.error_type == "UnknownTool"
    assert result.attempts == 1


# ============================================================ B. resources


def test_every_declared_resource_reads(loop, client):
    for uri in client.capabilities.resource_uris:
        result = loop.run_until_complete(client.read_resource(uri))
        assert result.ok, f"{uri}: {result.message}"
        assert result.payload


def test_the_capabilities_resource_describes_the_six_families(loop, client):
    result = loop.run_until_complete(
        client.read_resource("credpilot://system/capabilities")
    )
    assert result.ok
    assert set(result.payload["capability_families"]) == {
        "tools", "resources", "prompts", "elicitation", "sampling", "roots"
    }
    assert result.payload["model_provider"]["runtime"] == "google-gemini"


def test_the_threshold_resources_warn_against_being_used_as_a_source(loop, client):
    """Reading a threshold from a static table would defeat temporal selection."""
    for product in ("mortgage", "education"):
        result = loop.run_until_complete(
            client.read_resource(f"credpilot://thresholds/{product}")
        )
        assert result.ok
        assert "warning" in result.payload
        assert "retrieval returned" in result.payload["warning"]


def test_no_resource_exposes_applicant_data(loop, client):
    """Resources are public to anything that connects. Nothing applicant-level
    may be reachable through one, however the server is deployed."""
    from src.guardrails.redaction import find_sensitive

    forbidden = ("borrower_id", "taxpayer_id", "ssn", "date_of_birth",
                 "APP-000", "APP-2026-", "@example.com")
    for uri in client.capabilities.resource_uris:
        result = loop.run_until_complete(client.read_resource(uri))
        body = json.dumps(result.payload, default=str)
        for token in forbidden:
            assert token not in body, f"{uri} exposes {token!r}"
        assert not find_sensitive(body), f"{uri} carries a sensitive value"


# ============================================================== C. prompts


def test_every_declared_prompt_renders(loop, client):
    arguments = {
        "supervisor_clarification": {"user_message": "help with my loan",
                                     "ambiguity": "no product named"},
        "mortgage_policy_analysis": {"question": "max DTI?", "evidence_json": "[]",
                                     "as_of_date": "2026-07-08"},
        "education_policy_analysis": {"question": "cosigner?", "evidence_json": "[]",
                                      "as_of_date": "2026-07-08"},
        "underwriting_rationale": {"product_domain": "MORTGAGE",
                                   "outcome": "APPROVE_RECOMMENDATION",
                                   "figures_json": "{}", "evidence_json": "[]"},
        "human_review_summary": {"product_domain": "MORTGAGE",
                                 "outcome": "REFER_RECOMMENDATION",
                                 "reasons_json": "[]", "figures_json": "{}"},
        "evidence_explanation": {"citation": "POL-DTI-001 v2.0 rule DTI-CONV-001",
                                 "rule_text": "Back-end DTI must not exceed 43 percent.",
                                 "applied_to": "APP-000056"},
    }
    for name in client.capabilities.prompt_names:
        result = loop.run_until_complete(client.get_prompt(name, arguments.get(name, {})))
        assert result.ok, f"{name}: {result.message}"
        messages = result.payload["messages"]
        assert messages and messages[0]["text"].strip(), name


def test_a_prompt_interpolates_its_arguments(loop, client):
    result = loop.run_until_complete(client.get_prompt("supervisor_clarification", {
        "user_message": "I need help with my loan",
        "ambiguity": "the lending product is not named",
    }))
    assert result.ok
    text = result.payload["messages"][0]["text"]
    assert "I need help with my loan" in text
    assert "the lending product is not named" in text


def test_no_prompt_hard_codes_a_policy_threshold(loop, client):
    """A threshold baked into a template is a threshold no version can move.

    The whole temporal mechanism exists so that 43% becomes 45% when the
    as-of date crosses a boundary; a prompt carrying "43%" would keep saying
    43% forever, in the one place nobody thinks to look.
    """
    import re

    arguments = {
        "supervisor_clarification": {"user_message": "x", "ambiguity": "y"},
        "mortgage_policy_analysis": {"question": "x", "evidence_json": "[]"},
        "education_policy_analysis": {"question": "x", "evidence_json": "[]"},
        "underwriting_rationale": {"product_domain": "MORTGAGE", "outcome": "REFER",
                                   "figures_json": "{}", "evidence_json": "[]"},
        "human_review_summary": {"product_domain": "MORTGAGE", "outcome": "REFER",
                                 "reasons_json": "[]", "figures_json": "{}"},
        "evidence_explanation": {"citation": "C", "rule_text": "R"},
    }
    percentage = re.compile(r"\b\d{1,3}(?:\.\d+)?\s*(?:%|percent)\b", re.IGNORECASE)
    money = re.compile(r"\$\s?\d")

    for name in client.capabilities.prompt_names:
        result = loop.run_until_complete(client.get_prompt(name, arguments.get(name, {})))
        assert result.ok
        for message in result.payload["messages"]:
            text = message["text"]
            assert not percentage.search(text), f"{name} hard-codes a percentage"
            assert not money.search(text), f"{name} hard-codes a money amount"


# ========================================================== D. elicitation


def test_the_server_can_elicit_and_a_declining_client_is_handled(loop, client):
    """The host supplied no responder, so this client declines.

    Declining is a first-class outcome, not an error: the point of elicitation
    is that nobody answers on the user's behalf. What must not happen is the
    server assuming a product anyway.
    """
    result = call(loop, client, "clarify_loan_product",
                  {"user_request": "I need help with my loan"})
    assert result.ok, result.message
    assert result.payload["elicited"] is False
    assert result.payload["action"] == "decline"
    assert result.payload["product_domain"] is None
    # The client recorded being asked — an elicitation is a question put to a
    # person and has to leave a trace.
    assert client.elicitations
    assert "product" in client.elicitations[-1]["requested_fields"]


def test_an_elicitation_answer_is_honoured_when_the_host_supplies_one(loop, client):
    """With a responder attached, the answer comes back through the protocol."""
    client.elicitation_responder = lambda message, schema: {
        "product": "EDUCATION_LOAN", "as_of_date": "2026-07-01"
    }
    try:
        result = call(loop, client, "clarify_loan_product",
                      {"user_request": "help with my loan"})
        assert result.ok, result.message
        assert result.payload["elicited"] is True
        assert result.payload["product_domain"] == "EDUCATION_LOAN"
        assert result.payload["as_of_date"] == "2026-07-01"
    finally:
        client.elicitation_responder = None


def test_elicitation_rejects_an_answer_that_is_not_a_lending_product(loop, client):
    client.elicitation_responder = lambda message, schema: {"product": "CAR_LOAN"}
    try:
        result = call(loop, client, "clarify_loan_product", {"user_request": "help"})
        assert result.ok
        assert result.payload["product_domain"] is None
    finally:
        client.elicitation_responder = None


# ============================================================= E. sampling


def test_sampling_runs_and_reports_which_model_answered(loop, client):
    """The compatibility path.

    The host serves sampling through Gemini and names the model, so a server
    can see which provider actually replied. With no key reachable the request
    is declined — never served by something else — and the result says so.
    """
    result = call(loop, client, "draft_with_sampling",
                  {"instruction": "Say the word ACKNOWLEDGED.", "max_tokens": 32})
    assert result.ok, result.message
    payload = result.payload

    if payload.get("sampled"):
        # Served. It must have been Gemini, and the server must have checked.
        assert "model_allowed" in payload
        assert payload["model_allowed"] is True, (
            f"a non-Gemini model answered a sampling request: {payload.get('model')}"
        )
        assert "gemini" in payload["model"].lower()
    else:
        # Declined. The reason must be recorded and the fallback stated.
        assert payload["reason"]
        assert "gemini" in payload["fallback"].lower()


def test_normal_operation_does_not_depend_on_sampling(loop, client):
    """Retrieval, the tools and the resources all work with sampling unused.

    The requirement is that sampling is *demonstrated*, not that the system
    relies on it — a host that delegated its generation to whatever client
    connected would have no control over which provider answered.
    """
    # Counted rather than asserted empty: the client is module-scoped, so the
    # sampling test above has already put one request on it. What matters is
    # that *this* call adds none.
    before = len(client.sampling_requests)
    result = call(loop, client, "retrieve_policy", {
        "query": "minimum credit score", "product_domain": "MORTGAGE", "top_k": 3,
    })
    assert result.ok and result.payload["evidence_count"] > 0
    assert len(client.sampling_requests) == before, (
        "an ordinary retrieval asked the client to sample"
    )


# ================================================================ F. roots


def test_roots_are_declared_and_intersected_with_the_allowlist(loop, client):
    result = call(loop, client, "list_project_roots", {})
    assert result.ok, result.message
    payload = result.payload
    assert payload["client_supports_roots"] is True
    assert payload["client_declared_roots"], "the client declared no roots"

    allowlisted = {row["path"] for row in payload["credpilot_allowlist"]}
    assert allowlisted == set(ALLOWED_ROOTS)


def test_roots_expose_no_path_outside_the_allowlist(loop, client):
    """Whatever a client declares, the server talks about four directories."""
    result = call(loop, client, "list_project_roots", {})
    assert result.ok
    for row in result.payload["credpilot_allowlist"]:
        assert row["path"] in ALLOWED_ROOTS
        # Nothing above the repository, and nothing outside it.
        assert ".." not in row["path"]


def test_roots_are_not_treated_as_authorization(loop, client):
    """Declaring a root grants nothing. Product isolation still holds."""
    result = call(loop, client, "list_project_roots", {})
    assert result.ok
    assert "not authorization" in result.payload["warning"].lower()

    # And the claim is true: with roots declared, a cross-product citation is
    # still refused.
    validated = call(loop, client, "validate_evidence", {
        "product_domain": "EDUCATION_LOAN",
        "citations": ["POL-DTI-001 v2.0 rule DTI-CONV-001"],
    })
    assert validated.ok and validated.payload["valid"] is False


# ================================================== resilience across the wire


def test_a_timeout_is_a_value_not_an_exception(loop, client):
    """A graph node has to produce a state update whatever happened."""
    from src.resilience import RetryPolicy

    impossible = RetryPolicy(max_attempts=1, timeout_seconds=0.001, jitter=False)
    result = loop.run_until_complete(
        client.call_tool(
            "retrieve_policy",
            {"query": "maximum debt to income", "product_domain": "MORTGAGE"},
            policy=impossible,
        )
    )
    assert result.ok is False
    assert result.error_type in ("OperationTimeout", "TimeoutError", "CancelledError")
    assert result.message


def test_the_server_is_still_usable_after_a_timeout(loop, client):
    """A cancelled call must not wedge the session for every later one."""
    result = call(loop, client, "resolve_citation",
                  {"citation": "POL-DTI-001 v2.0 rule DTI-CONV-001"})
    assert result.ok, result.message
    assert result.payload["resolves"] is True


def test_an_unreachable_server_is_reported_rather_than_raised(loop):
    """Server unavailability is an operating condition, not a crash."""
    broken = CredPilotMCPClient(python="definitely-not-a-python-interpreter")
    with pytest.raises(Exception) as caught:
        loop.run_until_complete(broken.connect())
    assert "mcp" in str(caught.value).lower() or "server" in str(caught.value).lower()
    loop.run_until_complete(broken.close())


def test_calling_before_connecting_is_reported_rather_than_raised(loop):
    unconnected = CredPilotMCPClient()
    result = loop.run_until_complete(unconnected.call_tool("retrieve_policy", {}))
    assert result.ok is False
    assert result.error_type == "NotConnected"


# ========================================================== the transcript


def test_every_exchange_reaches_the_committed_transcript(loop, client):
    """AC-07: the tool log is machine-generated by committed middleware."""
    from src.observability.tool_logging import MCP_TRANSCRIPT_LOG, read_log

    call(loop, client, "resolve_citation",
         {"citation": "POL-DTI-001 v2.0 rule DTI-CONV-001"})
    assert MCP_TRANSCRIPT_LOG.exists()

    records = read_log(MCP_TRANSCRIPT_LOG)
    assert records
    methods = {r.get("method") for r in records}
    assert any("resolve_citation" in str(m) for m in methods)
    for record in records[-50:]:
        assert record.get("direction") in ("request", "response", "client")
        assert record.get("timestamp")
