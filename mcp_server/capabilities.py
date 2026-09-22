"""What the CredPilot MCP server exposes, described in one place.

The server's surface is declared here as data rather than discovered by
reflection so that three separate readers agree on it:

* the ``credpilot://system/capabilities`` resource, which is how a client sees
  the surface without calling anything;
* :mod:`src.mcp_host.client`, which checks the server offered what the host
  needs before the host relies on it;
* ``tests/test_mcp_capabilities.py``, which asserts the six MCP capability
  families are actually present rather than merely claimed.

A declaration that drifts from the implementation is worse than no declaration,
so ``test_mcp_capabilities.py`` reconciles every name below against the running
server's own ``list_tools`` / ``list_resources`` / ``list_prompts``.
"""

from __future__ import annotations

from typing import Any

#: MCP protocol capability families, and how CredPilot uses each.
#:
#: Sampling and roots are *compatibility* implementations and say so. CredPilot
#: calls Gemini through its own integration (``src/llm.py``) rather than asking
#: the client to sample on its behalf: a host that delegated its model calls to
#: whatever client connected would have no control over which provider answered,
#: and "Google Gemini only" is a requirement, not a preference. The sampling path
#: exists, is exercised, and refuses to run against a non-Gemini client.
CAPABILITY_FAMILIES: dict[str, dict[str, Any]] = {
    "tools": {
        "supported": True,
        "role": "primary",
        "note": "Typed, validated capabilities backed by the same services the "
                "in-process agents call. No business logic lives in a handler.",
    },
    "resources": {
        "supported": True,
        "role": "primary",
        "note": "Read-only catalogues of committed policy artifacts. No applicant "
                "data is exposed through any resource.",
    },
    "prompts": {
        "supported": True,
        "role": "primary",
        "note": "Reusable, parameterised prompt templates. They carry structure and "
                "instructions; every threshold comes from retrieved evidence passed "
                "in as an argument, never hard-coded in a template.",
    },
    "elicitation": {
        "supported": True,
        "role": "controlled",
        "note": "Used only to ask for a missing routing fact (which lending "
                "product, which as-of date) or an explicit confirmation. Never used "
                "to request a credential, an account number or any secret.",
    },
    "sampling": {
        "supported": True,
        "role": "compatibility",
        "note": "Implemented and tested for protocol compatibility. Normal "
                "operation does not depend on it: CredPilot calls Gemini through "
                "src/llm.py so the provider stays under the host's control. A "
                "sampling request that would be served by a non-Gemini model is "
                "refused.",
    },
    "roots": {
        "supported": True,
        "role": "compatibility",
        "note": "A fixed allowlist of committed project directories — the policy "
                "corpora and the index manifest. Arbitrary filesystem paths are "
                "never exposed, and roots are not treated as an authorization "
                "mechanism.",
    },
}

#: Tools, with the CredPilot service each delegates to.
TOOLS: dict[str, str] = {
    "retrieve_policy": "src.tools.rag_tool.retrieve_policy_tool — hybrid, "
                       "product-isolated policy retrieval",
    "compute_affordability": "src.calculations.compute_affordability — every "
                             "underwriting figure, per product",
    "screen_risk_flags": "src.calculations.screen_risk — deterministic risk screen",
    "resolve_citation": "src.rag.citations.CitationResolver — does this citation "
                        "resolve to a committed document",
    "list_policy_rules": "src.tools.rag_tool.policy_corpus_summary — declared rules "
                         "per policy document",
    "get_policy_version": "src.rag.applicability — which version of a policy "
                          "governed on a given date",
    "get_rule_dependencies": "src.rag.pipeline — the rules a rule refers to and "
                             "cannot be applied without",
    "validate_evidence": "src.rag.citations + src.rules.assert_single_version — "
                         "does an evidence bundle hold together",
    "clarify_loan_product": "MCP elicitation — ask the client for the one missing "
                            "routing fact",
    "draft_with_sampling": "MCP sampling — compatibility path; refuses a "
                           "non-Gemini client model",
    "list_project_roots": "MCP roots — the committed directories the client "
                          "declared, intersected with CredPilot's allowlist",
}

#: Resource URIs, with what each holds.
RESOURCES: dict[str, str] = {
    "credpilot://policies/mortgage": "Indexed mortgage policy inventory (legacy "
                                     "URI, kept stable).",
    "credpilot://policies/education": "Indexed education policy inventory (legacy "
                                      "URI, kept stable).",
    "credpilot://policies/mortgage/catalog": "Mortgage policy catalogue: documents, "
                                             "versions, effective dates, rule ids.",
    "credpilot://policies/education/catalog": "Education policy catalogue: documents, "
                                              "versions, effective dates, rule ids.",
    "credpilot://rules/mortgage": "Every declared mortgage rule id, by family and "
                                  "policy.",
    "credpilot://rules/education": "Every declared education rule id, by family and "
                                   "policy.",
    "credpilot://thresholds/mortgage": "Numeric parameters the mortgage rule engine "
                                       "reads out of policy text, with the rule that "
                                       "publishes each.",
    "credpilot://thresholds/education": "The same for education.",
    "credpilot://system/capabilities": "This declaration: capability families, "
                                       "tools, resources, prompts, limits.",
    "credpilot://index/manifest": "Index build manifest: models, counts, source "
                                  "hashes.",
}

#: Prompts, with the arguments each takes.
PROMPTS: dict[str, dict[str, Any]] = {
    "supervisor_clarification": {
        "arguments": ["user_message", "ambiguity"],
        "purpose": "Draft the single smallest question that would resolve an "
                   "ambiguous request.",
    },
    "mortgage_policy_analysis": {
        "arguments": ["question", "evidence_json", "as_of_date"],
        "purpose": "Explain what retrieved mortgage policy says about a question, "
                   "using only the evidence supplied.",
    },
    "education_policy_analysis": {
        "arguments": ["question", "evidence_json", "as_of_date"],
        "purpose": "The same for education-loan policy.",
    },
    "underwriting_rationale": {
        "arguments": ["product_domain", "outcome", "figures_json", "evidence_json"],
        "purpose": "Write the rationale for a decision that has already been made "
                   "deterministically.",
    },
    "human_review_summary": {
        "arguments": ["product_domain", "outcome", "reasons_json", "figures_json"],
        "purpose": "Brief the human reviewer: what was decided, why it was routed, "
                   "and what they need to look at.",
    },
    "evidence_explanation": {
        "arguments": ["citation", "rule_text", "applied_to"],
        "purpose": "Explain one retrieved rule in plain English without restating "
                   "it as a new threshold.",
    },
}

#: Committed directories a client may be told about through roots. Everything
#: outside this list is invisible to the protocol, whatever a client asks for.
ALLOWED_ROOTS: tuple[str, ...] = (
    "synthetic_data/mortgage/policy_corpus",
    "synthetic_data/education/policy_corpus",
    "data/vectorstore",
    "config",
)

#: Limits the server enforces, published so a client can respect them rather
#: than discover them by being refused.
LIMITS: dict[str, Any] = {
    "max_top_k": 25,
    "max_query_chars": 2000,
    "max_citations_per_validate_call": 64,
    "max_rule_dependency_follows": 6,
    "default_tool_timeout_seconds": 60,
}


def capability_report() -> dict[str, Any]:
    """The payload behind ``credpilot://system/capabilities``."""
    return {
        "server": "credpilot",
        "protocol": "mcp",
        "host": "CredPilot (src/mcp_host/)",
        "capability_families": CAPABILITY_FAMILIES,
        "tools": TOOLS,
        "resources": RESOURCES,
        "prompts": PROMPTS,
        "allowed_roots": list(ALLOWED_ROOTS),
        "limits": LIMITS,
        "model_provider": {
            "runtime": "google-gemini",
            "note": "Google Gemini is the only model provider. The sampling "
                    "capability is a compatibility path and refuses a client "
                    "offering any other provider.",
        },
        "data": {
            "synthetic": True,
            "applicant_pii_exposed_through_resources": False,
        },
    }


__all__ = [
    "ALLOWED_ROOTS",
    "CAPABILITY_FAMILIES",
    "LIMITS",
    "PROMPTS",
    "RESOURCES",
    "TOOLS",
    "capability_report",
]
