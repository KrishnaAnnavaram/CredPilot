#!/usr/bin/env python
"""CredPilot's MCP server.

Runs over stdio using the MCP Python SDK and is consumed from the agent side via
``langchain-mcp-adapters`` and :mod:`src.mcp_host.client`.

All six MCP capability families are implemented; see
:mod:`mcp_server.capabilities` for the declaration and what each is for.

**Tools** (11)
    ``retrieve_policy``, ``compute_affordability``, ``screen_risk_flags``,
    ``resolve_citation``, ``list_policy_rules``, ``get_policy_version``,
    ``get_rule_dependencies``, ``validate_evidence``, ``clarify_loan_product``
    (elicitation), ``draft_with_sampling`` (sampling), ``list_project_roots``
    (roots).

**Resources** (10)
    Policy catalogues, rule inventories and threshold tables per product, the
    index manifest, and ``credpilot://system/capabilities``.

**Prompts** (6)
    Reusable templates for clarification, per-product policy analysis, the
    underwriting rationale, the human-review brief and evidence explanation.

Two invariants hold across the MCP boundary exactly as they do in process:

* **Product isolation.** Every product-scoped tool requires a product domain or
  an application id it can resolve one from, and returns
  ``PRODUCT_CLARIFICATION_REQUIRED`` rather than searching both corpora.
* **No business logic in a handler.** Each tool validates its input, calls the
  same CredPilot service the in-process agents call, and shapes the result. A
  threshold never appears in this file.
"""

from __future__ import annotations

import contextlib
import functools
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# ---------------------------------------------------------------------------------
# stdout belongs to the protocol
#
# On stdio transport, stdout *is* the JSON-RPC channel. Anything else written to
# it corrupts the stream, and the client then waits forever for a frame it can
# parse — which is exactly what happened here: `transformers` prints a
# "Loading weights: 0%|..." progress bar to stdout while the embedding model
# loads, the first retrieve_policy call wedged, and the server sat at 0% CPU
# holding 900 MB.
#
# Three defences, in order of how early they act:
#   1. turn the progress bars off before anything imports them,
#   2. load the models at start-up, before the protocol owns stdout,
#   3. redirect stdout to stderr for the duration of every tool call.
# ---------------------------------------------------------------------------------
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("TRANSFORMERS_NO_ADVISORY_WARNINGS", "1")
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("TQDM_DISABLE", "1")

from mcp.server.fastmcp import Context, FastMCP  # noqa: E402
from mcp.server.fastmcp.prompts import base as prompt_base  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

from mcp_server.capabilities import (  # noqa: E402
    ALLOWED_ROOTS,
    LIMITS,
    capability_report,
)
from src.config import get_config  # noqa: E402
from src.domain import LendingProductDomain, ProductResolutionError  # noqa: E402
from src.observability.tool_logging import log_mcp_exchange  # noqa: E402
from src.rag.citations import CitationResolver, parse_citation  # noqa: E402
from src.tools.rag_tool import (  # noqa: E402
    TOOL_DESCRIPTION,
    policy_corpus_summary,
    result_to_payload,
    retrieve_policy_tool,
)

mcp = FastMCP("credpilot")


class ToolError(ValueError):
    """An input this server will not act on.

    Raised rather than returned so the SDK marks the tool call as failed: a
    client that receives ``{"error": ...}`` with a success status has to know to
    look for it, and one that does not will treat a refusal as a result.
    """


def protocol_safe(fn):
    """Keep a handler's stray stdout writes out of the JSON-RPC stream.

    Any library that prints — a progress bar, a deprecation notice, a debug line
    — sends it to stderr instead, where the client's error log picks it up
    harmlessly.
    """

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        with contextlib.redirect_stdout(sys.stderr):
            return fn(*args, **kwargs)

    return wrapper


def traced(method: str):
    """Log the request and response of a tool call, and time it.

    The transcript at ``logs/mcp_transcript.jsonl`` is written from here, which
    is why every tool has the decorator and none of them logs by hand.
    """

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            started = time.perf_counter()
            log_mcp_exchange(direction="request", method=method, payload=dict(kwargs))
            try:
                result = fn(*args, **kwargs)
            except Exception as exc:  # noqa: BLE001 - logged, then re-raised
                log_mcp_exchange(
                    direction="response",
                    method=method,
                    payload={
                        "ok": False,
                        "error_type": type(exc).__name__,
                        "error": str(exc)[:300],
                        "latency_ms": round((time.perf_counter() - started) * 1000, 1),
                    },
                )
                raise
            log_mcp_exchange(
                direction="response",
                method=method,
                payload={
                    "ok": True,
                    "latency_ms": round((time.perf_counter() - started) * 1000, 1),
                    **_summary_of(result),
                },
            )
            return result

        return wrapper

    return decorator


def _summary_of(result: Any) -> dict[str, Any]:
    """A short, PII-free description of a result, for the transcript."""
    if not isinstance(result, dict):
        return {"result_type": type(result).__name__}
    keep = ("status", "product_domain", "evidence_count", "resolves", "policy_count",
            "rule_count", "verdict", "valid", "level", "count", "governing_version")
    summary = {k: result[k] for k in keep if k in result}
    if "citations" in result and isinstance(result["citations"], list):
        summary["citations"] = result["citations"][:12]
    return summary or {"keys": sorted(result)[:12]}


def _domain(value: str | None, *, field: str = "product_domain") -> LendingProductDomain:
    """Resolve a product domain argument, refusing rather than guessing."""
    if not value:
        raise ToolError(
            f"PRODUCT_CLARIFICATION_REQUIRED: {field} is required. CredPilot keeps "
            f"its two lending products isolated and will not search both corpora. "
            f"Pass MORTGAGE or EDUCATION_LOAN."
        )
    try:
        return LendingProductDomain.from_any(value)
    except ValueError as exc:
        raise ToolError(f"{field} must be MORTGAGE or EDUCATION_LOAN, not {value!r}") from exc


def warm_up() -> None:
    """Load the models and open the indexes before the protocol starts.

    Model loading is the noisy part. Doing it here means it happens while stdout
    is still an ordinary stream, and it also takes the multi-second first-call
    penalty off the client's first request.
    """
    with contextlib.redirect_stdout(sys.stderr):
        try:
            from src.rag.pipeline import get_retriever

            retriever = get_retriever()
            _ = retriever.embedder.dimension
            if retriever.reranker is not None:
                retriever.reranker.score("warm up", ["a passage to warm the model"])
            for domain in ("MORTGAGE", "EDUCATION_LOAN"):
                retriever.lexical(retriever.config.product(domain).domain)
                retriever.store(retriever.config.product(domain).domain).count()
            print("credpilot mcp: retrieval warm", file=sys.stderr, flush=True)
        except Exception as exc:  # noqa: BLE001 - a cold start still serves requests
            print(f"credpilot mcp: warm-up skipped ({exc})", file=sys.stderr, flush=True)


# ======================================================================================
# A. Tools
# ======================================================================================


@mcp.tool(name="retrieve_policy", description=TOOL_DESCRIPTION)
@protocol_safe
@traced("tools/call:retrieve_policy")
def retrieve_policy(
    query: str,
    product_domain: str | None = None,
    application_id: str | None = None,
    as_of_date: str | None = None,
    product_family: str | None = None,
    loan_purpose: str | None = None,
    occupancy_type: str | None = None,
    product_code: str | None = None,
    top_k: int | None = None,
) -> dict[str, Any]:
    """Retrieve the lending-policy rules that govern an application."""
    if not (query or "").strip():
        raise ToolError("query must not be empty")
    if len(query) > LIMITS["max_query_chars"]:
        raise ToolError(f"query exceeds {LIMITS['max_query_chars']} characters")
    if top_k is not None and (top_k < 1 or top_k > LIMITS["max_top_k"]):
        raise ToolError(f"top_k must be between 1 and {LIMITS['max_top_k']}")

    result = retrieve_policy_tool(
        query=query,
        product_domain=product_domain,
        application_id=application_id,
        as_of_date=as_of_date,
        product_family=product_family,
        loan_purpose=loan_purpose,
        occupancy_type=occupancy_type,
        product_code=product_code,
        top_k=top_k,
        agent="mcp_client",
    )
    payload = result_to_payload(result)
    payload["citations"] = [e["citation"] for e in payload["evidence"]]
    return payload


@mcp.tool(
    name="compute_affordability",
    description=(
        "Compute every underwriting figure for one application, deterministically. "
        "Mortgage returns front-end and back-end DTI, LTV/CLTV/HCLTV, months of "
        "reserves and funds to close; education returns DTI, residual income and "
        "the certified maximum. No model is involved and no threshold is applied — "
        "this reports what the file computes to, not whether it passes. "
        "Pass application_id to load a committed packet, or packet for an ad-hoc one."
    ),
)
@protocol_safe
@traced("tools/call:compute_affordability")
def compute_affordability(
    product_domain: str | None = None,
    application_id: str | None = None,
    packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run the deterministic calculation stack over one application."""
    from src.calculations import compute_affordability as _compute

    resolved_packet, domain = _load_packet(product_domain, application_id, packet)
    figures = _compute(domain, resolved_packet)
    return {
        "product_domain": domain.value,
        "application_id": resolved_packet.get("application_id"),
        "formula_version": figures.get("formula_version"),
        "ratios": figures.get("ratios", {}),
        "amounts": figures.get("amounts", {}),
        "counts": figures.get("counts", {}),
        "indeterminate": figures.get("indeterminate", []),
        "inputs_used": figures.get("inputs_used", {}),
        "note": (
            "Computed by src.calculations, not by a model (POL-DTI-001 "
            "DTI-CALC-002). No threshold has been applied to these figures."
        ),
    }


@mcp.tool(
    name="screen_risk_flags",
    description=(
        "Screen one application for the risk indicators its product's policy names "
        "— credit events, delinquency, fraud and identity signals, unsourced "
        "deposits, thin files, sanctions hits. Returns a level and the flags that "
        "set it. Deterministic; sets no threshold of its own."
    ),
)
@protocol_safe
@traced("tools/call:screen_risk_flags")
def screen_risk_flags(
    product_domain: str | None = None,
    application_id: str | None = None,
    packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run the deterministic risk screen over one application."""
    from src.calculations import screen_risk

    resolved_packet, domain = _load_packet(product_domain, application_id, packet)
    risk = screen_risk(domain, resolved_packet)
    return {
        "product_domain": domain.value,
        "application_id": resolved_packet.get("application_id"),
        "level": risk.get("level"),
        "flags": risk.get("flags", []),
        "detail": risk.get("detail", {}),
    }


@mcp.tool(
    name="resolve_citation",
    description=(
        "Check that a policy citation resolves to a committed source document and "
        "report where. Accepts either product's convention: "
        "'POL-DTI-001 v2.0 rule DTI-CONV-001' (mortgage) or "
        "'POL-002 EDU-UW-001' (education). Use it before relying on any citation "
        "that did not come straight from retrieve_policy."
    ),
)
@protocol_safe
@traced("tools/call:resolve_citation")
def resolve_citation(citation: str) -> dict[str, Any]:
    """Resolve one citation against the committed corpora."""
    if not (citation or "").strip():
        raise ToolError("citation must not be empty")
    config = get_config()
    parsed = parse_citation(citation)
    resolves, reason = CitationResolver(config).resolve(citation)
    source = None
    if parsed is not None:
        path = CitationResolver(config).source_path_for(parsed)
        if path is not None:
            source = path.resolve().relative_to(config.repo_root).as_posix() \
                if hasattr(config, "repo_root") else path.name
    return {
        "citation": citation,
        "resolves": resolves,
        "reason": reason,
        "product_domain": parsed.product_domain.value if parsed else None,
        "policy_id": parsed.policy_id if parsed else None,
        "policy_version": parsed.policy_version if parsed else None,
        "rule_id": parsed.rule_id if parsed else None,
        "source_path": source,
    }


@mcp.tool(
    name="list_policy_rules",
    description=(
        "List the rules a lending-policy document declares. "
        "product_domain must be MORTGAGE or EDUCATION_LOAN; policy_id is optional "
        "and narrows the listing to one document."
    ),
)
@protocol_safe
@traced("tools/call:list_policy_rules")
def list_policy_rules(product_domain: str, policy_id: str | None = None) -> dict[str, Any]:
    """Enumerate declared rules for a product, optionally for one policy."""
    domain = _domain(product_domain)
    summary = policy_corpus_summary()
    product = summary["products"][domain.corpus_key]
    policies = product["policies"]
    if policy_id:
        policies = [p for p in policies if p["policy_id"] == policy_id]
        if not policies:
            raise ToolError(
                f"no policy {policy_id!r} in the {domain.value} corpus; call this "
                f"tool without policy_id to see what is indexed"
            )
    return {
        "product_domain": domain.value,
        "policy_count": len(policies),
        "rule_count": sum(len(p["rule_ids"]) for p in policies),
        "policies": policies,
    }


@mcp.tool(
    name="get_policy_version",
    description=(
        "Which version of a policy document governed on a given date. The same "
        "question asked on two dates can return two versions with two different "
        "thresholds, which is the whole point of asking. Returns every published "
        "version with its effective window, and marks the governing one."
    ),
)
@protocol_safe
@traced("tools/call:get_policy_version")
def get_policy_version(
    product_domain: str, policy_id: str, as_of_date: str | None = None
) -> dict[str, Any]:
    """Resolve the governing version of one policy document on a date."""
    from datetime import date as _date

    from src.rag.applicability import select_effective_versions

    domain = _domain(product_domain)
    summary = policy_corpus_summary()
    product = summary["products"][domain.corpus_key]
    versions = [p for p in product["policies"] if p["policy_id"] == policy_id]
    if not versions:
        raise ToolError(f"no policy {policy_id!r} in the {domain.value} corpus")

    as_of: _date | None = None
    if as_of_date:
        try:
            as_of = _date.fromisoformat(str(as_of_date)[:10])
        except ValueError as exc:
            raise ToolError(f"as_of_date must be ISO yyyy-mm-dd, not {as_of_date!r}") from exc

    metas = [
        {
            "policy_id": v["policy_id"],
            "policy_version": v["policy_version"],
            "effective_date": v["effective_date"],
            "expiration_date": v["expiration_date"],
        }
        for v in versions
    ]
    # select_effective_versions returns {policy_id: (version, effective_date)};
    # a policy with no version eligible on the date is simply absent.
    governing = select_effective_versions(metas, as_of)
    governing_version = (governing.get(policy_id) or (None, None))[0]

    return {
        "product_domain": domain.value,
        "policy_id": policy_id,
        "as_of_date": as_of.isoformat() if as_of else None,
        "governing_version": governing_version,
        "version_count": len(versions),
        "versions": [
            {
                "policy_version": v["policy_version"],
                "effective_date": v["effective_date"],
                "expiration_date": v["expiration_date"],
                "policy_title": v["policy_title"],
                "rule_ids": v["rule_ids"],
                "governs_on_as_of_date": v["policy_version"] == governing_version,
            }
            for v in sorted(versions, key=lambda v: str(v["effective_date"] or ""))
        ],
        "note": (
            "Without as_of_date every published version is returned and none is "
            "marked governing: 'current' is not a property of a policy, it is a "
            "property of a policy and a date."
        ),
    }


@mcp.tool(
    name="get_rule_dependencies",
    description=(
        "The rules a rule points at but does not contain. A rule reading 'at least "
        "two compensating factors from DTI-CONV-003' cannot be applied without "
        "DTI-CONV-003, and this returns that list so the caller can fetch it. "
        "Bounded to one round of following; it does not walk the corpus."
    ),
)
@protocol_safe
@traced("tools/call:get_rule_dependencies")
def get_rule_dependencies(
    product_domain: str, rule_id: str, as_of_date: str | None = None
) -> dict[str, Any]:
    """Find the rules one rule depends on."""
    domain = _domain(product_domain)
    if not (rule_id or "").strip():
        raise ToolError("rule_id must not be empty")

    result = retrieve_policy_tool(
        query=f"{rule_id} requirements and any rule it refers to",
        product_domain=domain.value,
        as_of_date=as_of_date,
        agent="mcp_client",
    )
    payload = result_to_payload(result)
    evidence = payload.get("evidence", [])
    target = next((e for e in evidence if e.get("rule_id") == rule_id), None)
    if target is None:
        return {
            "product_domain": domain.value,
            "rule_id": rule_id,
            "found": False,
            "dependencies": [],
            "note": (
                f"{rule_id} was not among the top retrieved chunks for its own id. "
                f"It may not exist in this corpus; call list_policy_rules to check."
            ),
        }

    from src.graph import referenced_rules

    deps = referenced_rules([target])[: LIMITS["max_rule_dependency_follows"]]
    return {
        "product_domain": domain.value,
        "rule_id": rule_id,
        "found": True,
        "citation": target.get("citation"),
        "dependencies": deps,
        "dependency_count": len(deps),
        "max_follows": LIMITS["max_rule_dependency_follows"],
    }


@mcp.tool(
    name="validate_evidence",
    description=(
        "Check that an evidence bundle holds together before anything is decided on "
        "it: every citation resolves to a committed document, every chunk belongs to "
        "the stated product, and no two chunks come from different versions of the "
        "same policy. The last of those is the one that matters — mixing v1.0 and "
        "v2.0 of one document produces a verdict against two different rulebooks."
    ),
)
@protocol_safe
@traced("tools/call:validate_evidence")
def validate_evidence(
    product_domain: str, evidence: list[dict[str, Any]] | None = None,
    citations: list[str] | None = None,
) -> dict[str, Any]:
    """Validate an evidence bundle or a bare list of citations."""
    domain = _domain(product_domain)
    items = list(evidence or [])
    bare = list(citations or [])
    if not items and not bare:
        raise ToolError("pass either evidence (a list of chunks) or citations")
    if len(items) + len(bare) > LIMITS["max_citations_per_validate_call"]:
        raise ToolError(
            f"at most {LIMITS['max_citations_per_validate_call']} items per call"
        )

    resolver = CitationResolver(get_config())
    all_citations = [str(e.get("citation", "")) for e in items if e.get("citation")] + bare
    results = {c: resolver.resolve(c) for c in all_citations}
    unresolved = sorted(c for c, (ok, _) in results.items() if not ok)

    wrong_product: list[str] = []
    for citation in all_citations:
        parsed = parse_citation(citation)
        if parsed is not None and parsed.product_domain is not domain:
            wrong_product.append(citation)

    version_conflict: str | None = None
    if items:
        try:
            from src.rules import assert_single_version

            assert_single_version(items)
        except Exception as exc:  # noqa: BLE001 - reported, not raised
            version_conflict = str(exc)[:400]

    valid = not unresolved and not wrong_product and version_conflict is None
    return {
        "product_domain": domain.value,
        "valid": valid,
        "citation_count": len(all_citations),
        "unresolved_citations": unresolved,
        "citations_from_another_product": sorted(set(wrong_product)),
        "mixed_policy_versions": version_conflict,
        "verdict": "VALID" if valid else "INVALID",
        "note": (
            "A bundle that fails here must not be used to decide a file. Route it "
            "for human review (POL-GEN-001 GEN-ELG-005) rather than deciding on "
            "evidence that does not hold together."
        ),
    }


def _load_packet(
    product_domain: str | None,
    application_id: str | None,
    packet: dict[str, Any] | None,
) -> tuple[dict[str, Any], LendingProductDomain]:
    """Resolve the packet and its product for the calculation tools."""
    from src.application_context import build_underwriting_input, strip_embedded_outcomes
    from src.domain import resolve_product_domain

    if packet is None and not application_id:
        raise ToolError("pass application_id or packet")

    if packet is not None:
        clean = strip_embedded_outcomes(packet)
        try:
            domain = resolve_product_domain(
                explicit_domain=product_domain,
                application_id=clean.get("application_id") or application_id,
                packet=clean,
            )
        except ProductResolutionError as exc:
            raise ToolError(str(exc)) from exc
        return clean, domain

    try:
        domain = resolve_product_domain(
            explicit_domain=product_domain, application_id=application_id
        )
    except ProductResolutionError as exc:
        raise ToolError(str(exc)) from exc

    path = _application_path(domain, str(application_id))
    if path is None:
        raise ToolError(
            f"no committed application packet for {application_id!r} under the "
            f"{domain.value} corpus"
        )
    return build_underwriting_input(path), domain


def _application_path(domain: LendingProductDomain, application_id: str) -> Path | None:
    root = REPO_ROOT / "synthetic_data" / domain.corpus_key / "applications"
    candidate = root / f"{application_id}.json"
    return candidate if candidate.exists() else None


# ======================================================================================
# D. Elicitation — asking the client for the one fact that is missing
# ======================================================================================


class LoanProductChoice(BaseModel):
    """What the client is asked for when the product cannot be resolved."""

    product: str = Field(
        description="Which lending product this concerns: MORTGAGE or EDUCATION_LOAN"
    )
    as_of_date: str | None = Field(
        default=None,
        description="The underwriting as-of date, ISO yyyy-mm-dd, if known",
    )


@mcp.tool(
    name="clarify_loan_product",
    description=(
        "Ask the connected client which lending product a request concerns, using "
        "MCP elicitation. Call this instead of guessing when a request names no "
        "product — CredPilot keeps the two corpora isolated and will not search "
        "both. Never used to request a credential, an account number or any secret."
    ),
)
async def clarify_loan_product(
    ctx: Context, user_request: str, reason: str | None = None
) -> dict[str, Any]:
    """Elicit the missing product from the client.

    A client that does not support elicitation, or a user who declines, is a
    normal outcome and not an error: the result says so and the caller falls
    back to asking in its own channel.
    """
    log_mcp_exchange(
        direction="request",
        method="elicitation/create",
        payload={"user_request": str(user_request)[:300], "reason": reason},
    )
    message = (
        f"CredPilot needs to know which lending product this concerns before it can "
        f"retrieve the policy that applies.\n\nRequest: {str(user_request)[:400]}\n"
        + (f"Why it is unclear: {reason}\n" if reason else "")
        + "\nAnswer MORTGAGE or EDUCATION_LOAN."
    )

    try:
        result = await ctx.elicit(message=message, schema=LoanProductChoice)
    except Exception as exc:  # noqa: BLE001 - an unsupporting client is not an error
        payload = {
            "elicited": False,
            "action": "unsupported",
            "reason": f"the client did not accept an elicitation request: "
                      f"{type(exc).__name__}",
            "fallback": "ask the user directly in the host's own channel",
        }
        log_mcp_exchange(direction="response", method="elicitation/create", payload=payload)
        return payload

    action = getattr(result, "action", None)
    if action == "accept" and getattr(result, "data", None) is not None:
        try:
            domain = LendingProductDomain.from_any(result.data.product)
        except ValueError:
            payload = {
                "elicited": True,
                "action": "accept",
                "product_domain": None,
                "reason": f"{result.data.product!r} is not a lending product "
                          f"CredPilot serves",
            }
            log_mcp_exchange(direction="response", method="elicitation/create", payload=payload)
            return payload
        payload = {
            "elicited": True,
            "action": "accept",
            "product_domain": domain.value,
            "as_of_date": result.data.as_of_date,
        }
    else:
        payload = {
            "elicited": False,
            "action": str(action or "unknown"),
            "product_domain": None,
            "reason": "the user declined or cancelled; nothing is assumed",
        }

    log_mcp_exchange(direction="response", method="elicitation/create", payload=payload)
    return payload


# ======================================================================================
# E. Sampling — compatibility only
# ======================================================================================

#: A client offering a model outside this family is refused. CredPilot's model
#: provider is a requirement, not a default, and delegating a generation to a
#: client would silently move it off Gemini.
_ALLOWED_SAMPLING_MODEL_TOKENS = ("gemini", "google")


@mcp.tool(
    name="draft_with_sampling",
    description=(
        "Ask the connected client to run one short generation on the server's "
        "behalf, using MCP sampling. This is a protocol-compatibility path and is "
        "not how CredPilot normally generates text: the host calls Google Gemini "
        "through src/llm.py so the provider stays under its control. A sampling "
        "response from a model outside the Gemini family is refused rather than "
        "used."
    ),
)
async def draft_with_sampling(
    ctx: Context, instruction: str, max_tokens: int = 256
) -> dict[str, Any]:
    """Exercise the sampling capability, refusing a non-Gemini responder."""
    from mcp.types import SamplingMessage, TextContent

    log_mcp_exchange(
        direction="request",
        method="sampling/createMessage",
        payload={"instruction": str(instruction)[:300], "max_tokens": max_tokens},
    )

    if not (instruction or "").strip():
        raise ToolError("instruction must not be empty")
    max_tokens = max(16, min(int(max_tokens), 1024))

    system = (
        "You are assisting CredPilot, a loan underwriting copilot. Explain only "
        "what you are given. Do not invent a policy, a threshold or a decision."
    )
    try:
        response = await ctx.session.create_message(
            messages=[
                SamplingMessage(
                    role="user",
                    content=TextContent(type="text", text=str(instruction)[:4000]),
                )
            ],
            max_tokens=max_tokens,
            system_prompt=system,
        )
    except Exception as exc:  # noqa: BLE001 - an unsupporting client is not an error
        payload = {
            "sampled": False,
            "reason": f"the client does not support sampling or refused: "
                      f"{type(exc).__name__}",
            "fallback": "the host generates through src/llm.py (Google Gemini)",
        }
        log_mcp_exchange(direction="response", method="sampling/createMessage", payload=payload)
        return payload

    model = str(getattr(response, "model", "") or "")
    text = ""
    content = getattr(response, "content", None)
    if content is not None:
        text = str(getattr(content, "text", "") or "")

    allowed = any(token in model.lower() for token in _ALLOWED_SAMPLING_MODEL_TOKENS)
    payload = {
        "sampled": True,
        "model": model,
        "model_allowed": allowed,
        "text": text if allowed else "",
        "stop_reason": str(getattr(response, "stopReason", "") or ""),
        **(
            {}
            if allowed
            else {
                "refused": (
                    f"the client answered with {model!r}. Google Gemini is the only "
                    f"approved provider for CredPilot, so the text is discarded "
                    f"rather than used."
                )
            }
        ),
    }
    log_mcp_exchange(
        direction="response",
        method="sampling/createMessage",
        payload={k: v for k, v in payload.items() if k != "text"},
    )
    return payload


# ======================================================================================
# F. Roots — compatibility, over an allowlist
# ======================================================================================


@mcp.tool(
    name="list_project_roots",
    description=(
        "The committed project directories this server will talk about, "
        "intersected with the roots the connected client declared. Roots are a "
        "convenience for locating committed policy sources — they are not an "
        "authorization mechanism, and a directory outside CredPilot's allowlist is "
        "never returned however a client declares it."
    ),
)
async def list_project_roots(ctx: Context) -> dict[str, Any]:
    """Report the allowlisted roots, and what the client declared."""
    log_mcp_exchange(direction="request", method="roots/list", payload={})

    declared: list[str] = []
    supported = True
    try:
        result = await ctx.session.list_roots()
        declared = [str(getattr(r, "uri", r)) for r in (getattr(result, "roots", None) or [])]
    except Exception as exc:  # noqa: BLE001 - an unsupporting client is not an error
        supported = False
        declared = []
        note = f"the client does not support roots: {type(exc).__name__}"
    else:
        note = "intersected with CredPilot's allowlist"

    allowed = [
        {
            "path": rel,
            "exists": (REPO_ROOT / rel).exists(),
            "uri": (REPO_ROOT / rel).resolve().as_uri(),
        }
        for rel in ALLOWED_ROOTS
    ]
    declared_allowed = [
        d for d in declared
        if any(rel.replace("/", "") in d.replace("\\", "").replace("/", "")
               for rel in ALLOWED_ROOTS)
    ]

    payload = {
        "client_supports_roots": supported,
        "client_declared_roots": declared,
        "client_roots_within_allowlist": declared_allowed,
        "credpilot_allowlist": allowed,
        "note": note,
        "warning": (
            "Roots are not authorization. Every tool on this server enforces "
            "product isolation and the outcome-table boundary regardless of what "
            "roots a client declares."
        ),
    }
    log_mcp_exchange(
        direction="response",
        method="roots/list",
        payload={k: v for k, v in payload.items() if k != "credpilot_allowlist"},
    )
    return payload


# ======================================================================================
# B. Resources
# ======================================================================================


def _resource(uri: str, payload_fn) -> str:
    log_mcp_exchange(direction="request", method="resources/read", payload={"uri": uri})
    body = json.dumps(payload_fn(), indent=2, sort_keys=True, default=str)
    log_mcp_exchange(
        direction="response", method="resources/read",
        payload={"uri": uri, "bytes": len(body)},
    )
    return body


@mcp.resource(
    "credpilot://policies/mortgage",
    name="mortgage_policy_inventory",
    description="Indexed U.S. residential mortgage policy documents, versions and rule ids.",
    mime_type="application/json",
)
@protocol_safe
def mortgage_policies() -> str:
    """The mortgage policy inventory."""
    return _resource(
        "credpilot://policies/mortgage",
        lambda: policy_corpus_summary()["products"]["mortgage"],
    )


@mcp.resource(
    "credpilot://policies/education",
    name="education_policy_inventory",
    description="Indexed private education-loan policy documents, versions and rule ids.",
    mime_type="application/json",
)
@protocol_safe
def education_policies() -> str:
    """The education-loan policy inventory."""
    return _resource(
        "credpilot://policies/education",
        lambda: policy_corpus_summary()["products"]["education"],
    )


@mcp.resource(
    "credpilot://policies/mortgage/catalog",
    name="mortgage_policy_catalog",
    description="Mortgage policy catalogue with effective windows and version chains.",
    mime_type="application/json",
)
@protocol_safe
def mortgage_catalog() -> str:
    """Mortgage catalogue, with each document's effective window."""
    return _resource(
        "credpilot://policies/mortgage/catalog",
        lambda: _catalog(LendingProductDomain.MORTGAGE),
    )


@mcp.resource(
    "credpilot://policies/education/catalog",
    name="education_policy_catalog",
    description="Education-loan policy catalogue with effective windows.",
    mime_type="application/json",
)
@protocol_safe
def education_catalog() -> str:
    """Education catalogue, with each document's effective window."""
    return _resource(
        "credpilot://policies/education/catalog",
        lambda: _catalog(LendingProductDomain.EDUCATION_LOAN),
    )


@mcp.resource(
    "credpilot://rules/mortgage",
    name="mortgage_rule_inventory",
    description="Every declared mortgage rule id, grouped by family and policy.",
    mime_type="application/json",
)
@protocol_safe
def mortgage_rules() -> str:
    """The mortgage rule inventory, by family."""
    return _resource(
        "credpilot://rules/mortgage", lambda: _rules(LendingProductDomain.MORTGAGE)
    )


@mcp.resource(
    "credpilot://rules/education",
    name="education_rule_inventory",
    description="Every declared education-loan rule id, grouped by family and policy.",
    mime_type="application/json",
)
@protocol_safe
def education_rules() -> str:
    """The education rule inventory, by family."""
    return _resource(
        "credpilot://rules/education", lambda: _rules(LendingProductDomain.EDUCATION_LOAN)
    )


@mcp.resource(
    "credpilot://thresholds/mortgage",
    name="mortgage_thresholds",
    description=(
        "The numeric parameters the mortgage rule engine reads out of policy text, "
        "with the rule that publishes each. Reference only: the engine reads them "
        "from retrieved evidence at decision time, never from here."
    ),
    mime_type="application/json",
)
@protocol_safe
def mortgage_thresholds() -> str:
    """Published mortgage parameters, by rule."""
    return _resource(
        "credpilot://thresholds/mortgage",
        lambda: _thresholds(LendingProductDomain.MORTGAGE),
    )


@mcp.resource(
    "credpilot://thresholds/education",
    name="education_thresholds",
    description="The same for education-loan policy.",
    mime_type="application/json",
)
@protocol_safe
def education_thresholds() -> str:
    """Published education parameters, by rule."""
    return _resource(
        "credpilot://thresholds/education",
        lambda: _thresholds(LendingProductDomain.EDUCATION_LOAN),
    )


@mcp.resource(
    "credpilot://system/capabilities",
    name="system_capabilities",
    description=(
        "What this server exposes: the six MCP capability families and how each is "
        "used, every tool with the CredPilot service it delegates to, every "
        "resource, every prompt, the roots allowlist and the enforced limits."
    ),
    mime_type="application/json",
)
@protocol_safe
def system_capabilities() -> str:
    """The server's own capability declaration."""
    return _resource("credpilot://system/capabilities", capability_report)


@mcp.resource(
    "credpilot://index/manifest",
    name="index_manifest",
    description="Index build manifest: embedding model, chunk counts, source hashes.",
    mime_type="application/json",
)
@protocol_safe
def index_manifest() -> str:
    """The index build manifest."""
    from src.rag.indexer import load_manifest

    return _resource("credpilot://index/manifest", load_manifest)


def _catalog(domain: LendingProductDomain) -> dict[str, Any]:
    product = policy_corpus_summary()["products"][domain.corpus_key]
    by_policy: dict[str, list[dict[str, Any]]] = {}
    for policy in product["policies"]:
        by_policy.setdefault(policy["policy_id"], []).append(policy)
    return {
        "product_domain": domain.value,
        "collection": product["collection"],
        "corpus_root": product["corpus_root"],
        "document_count": product["document_count"],
        "declared_rule_count": product["declared_rule_count"],
        "documents_with_multiple_versions": sorted(
            pid for pid, versions in by_policy.items() if len(versions) > 1
        ),
        "policies": {
            pid: sorted(
                (
                    {
                        "policy_version": v["policy_version"],
                        "policy_title": v["policy_title"],
                        "effective_date": v["effective_date"],
                        "expiration_date": v["expiration_date"],
                        "rule_count": len(v["rule_ids"]),
                        "rule_ids": v["rule_ids"],
                    }
                    for v in versions
                ),
                key=lambda v: str(v["effective_date"] or ""),
            )
            for pid, versions in sorted(by_policy.items())
        },
        "note": (
            "Which version applies is a function of the underwriting as-of date, "
            "not of which one is newest. Use get_policy_version to resolve it."
        ),
    }


def _rules(domain: LendingProductDomain) -> dict[str, Any]:
    product = policy_corpus_summary()["products"][domain.corpus_key]
    families: dict[str, list[str]] = {}
    by_policy: dict[str, list[str]] = {}
    for policy in product["policies"]:
        for rule_id in policy["rule_ids"]:
            family = rule_id.rsplit("-", 1)[0]
            families.setdefault(family, [])
            if rule_id not in families[family]:
                families[family].append(rule_id)
            key = f"{policy['policy_id']} v{policy['policy_version']}"
            by_policy.setdefault(key, []).append(rule_id)
    return {
        "product_domain": domain.value,
        "family_count": len(families),
        "rule_count": sum(len(v) for v in families.values()),
        "families": {k: sorted(v) for k, v in sorted(families.items())},
        "by_policy_version": {k: sorted(v) for k, v in sorted(by_policy.items())},
    }


def _thresholds(domain: LendingProductDomain) -> dict[str, Any]:
    """Parameters declared in the corpus, read straight from the documents."""
    from src.rag.parsers import get_parser
    from src.rag.parsers.base import parse_front_matter
    from src.domain import read_text_tolerant
    from src.rules import parse_value

    import re as _re

    config = get_config()
    product = config.product(domain.value)
    parser = get_parser(product.parser)
    param_row = _re.compile(r"^\|\s*`([a-z0-9_]+)`\s*\|\s*([^|]+?)\s*\|\s*$", _re.MULTILINE)
    rule_heading = _re.compile(r"^###\s+([A-Z][A-Z0-9-]+)\s+—", _re.MULTILINE)

    published: dict[str, dict[str, Any]] = {}
    for path in parser.corpus_files(product.corpus_root):
        text = read_text_tolerant(path)
        fm, body, _ = parse_front_matter(text, str(path))
        policy_id = str(fm.get("policy_id", ""))
        version = str(fm.get("version", ""))
        headings = list(rule_heading.finditer(body))
        for index, heading in enumerate(headings):
            rule_id = heading.group(1)
            end = headings[index + 1].start() if index + 1 < len(headings) else len(body)
            section = body[heading.start():end]
            params = {k: parse_value(v) for k, v in param_row.findall(section)}
            numeric = {k: v for k, v in params.items() if isinstance(v, (int, float))}
            if numeric:
                published[f"{policy_id} v{version} {rule_id}"] = numeric

    return {
        "product_domain": domain.value,
        "rules_publishing_a_numeric_parameter": len(published),
        "parameters": dict(sorted(published.items())),
        "warning": (
            "Reference only. The rule engine reads every threshold out of the "
            "evidence retrieval returned for the file's as-of date. Reading a "
            "threshold from this resource would defeat the temporal selection that "
            "makes two files with identical ratios decide differently."
        ),
    }


# ======================================================================================
# C. Prompts
# ======================================================================================


@mcp.prompt(
    name="supervisor_clarification",
    description=(
        "Draft the single smallest question that would resolve an ambiguous "
        "request, without guessing at the answer."
    ),
)
def supervisor_clarification(user_message: str, ambiguity: str) -> list[prompt_base.Message]:
    """Prompt for drafting one clarification question."""
    return [
        prompt_base.UserMessage(
            "You are the routing component of CredPilot, a loan underwriting "
            "copilot serving two strictly separated products: U.S. residential "
            "mortgage and private education lending.\n\n"
            f"The user said:\n{user_message}\n\n"
            f"What is unresolved: {ambiguity}\n\n"
            "Write ONE short question that would resolve it. Ask for the least "
            "information that settles the routing — not a form, not a list of "
            "questions. Do not answer the user's request, do not state any policy, "
            "do not quote a threshold, and do not guess which product they mean."
        )
    ]


@mcp.prompt(
    name="mortgage_policy_analysis",
    description=(
        "Explain what retrieved mortgage policy says about a question, using only "
        "the evidence supplied."
    ),
)
def mortgage_policy_analysis(
    question: str, evidence_json: str, as_of_date: str = ""
) -> list[prompt_base.Message]:
    """Prompt for mortgage policy explanation."""
    return [prompt_base.UserMessage(_analysis_prompt("mortgage", question, evidence_json, as_of_date))]


@mcp.prompt(
    name="education_policy_analysis",
    description=(
        "Explain what retrieved education-loan policy says about a question, using "
        "only the evidence supplied."
    ),
)
def education_policy_analysis(
    question: str, evidence_json: str, as_of_date: str = ""
) -> list[prompt_base.Message]:
    """Prompt for education policy explanation."""
    return [
        prompt_base.UserMessage(
            _analysis_prompt("private education loan", question, evidence_json, as_of_date)
        )
    ]


def _analysis_prompt(product: str, question: str, evidence_json: str, as_of_date: str) -> str:
    return (
        f"You are explaining {product} lending policy for CredPilot.\n\n"
        f"Question: {question}\n"
        + (f"Underwriting as-of date: {as_of_date}\n" if as_of_date else "")
        + "\nRetrieved policy evidence (JSON — this is the only source you may use):\n"
        f"{evidence_json}\n\n"
        "Rules for your answer:\n"
        "1. Every statement must come from the evidence above. If the evidence "
        "does not answer the question, say so and name what is missing.\n"
        "2. Cite the rule behind each statement, exactly as the evidence spells "
        "the citation. Do not reformat, abbreviate or invent one.\n"
        "3. Do not state a threshold that is not written in the evidence, and do "
        "not round, convert or recompute one that is.\n"
        "4. Do not decide anything about an application. You are explaining what "
        "the policy says, not applying it.\n"
        f"5. Say nothing about the other lending product; this evidence is "
        f"{product} policy only."
    )


@mcp.prompt(
    name="underwriting_rationale",
    description=(
        "Write the rationale for a decision that has already been made "
        "deterministically. The outcome and every figure are inputs, not outputs."
    ),
)
def underwriting_rationale(
    product_domain: str, outcome: str, figures_json: str, evidence_json: str
) -> list[prompt_base.Message]:
    """Prompt for the post-decision rationale."""
    return [
        prompt_base.UserMessage(
            f"You are writing the underwriting rationale for a {product_domain} "
            f"file at CredPilot.\n\n"
            f"The recommendation has already been reached by deterministic code: "
            f"**{outcome}**. It is a fact you are explaining, not a question you are "
            f"answering. Nothing you write changes it.\n\n"
            f"Computed figures (produced by the calculation engine; use these exact "
            f"values and do not recompute, round or restate them differently):\n"
            f"{figures_json}\n\n"
            f"Policy evidence the decision was made on:\n{evidence_json}\n\n"
            "Write a short rationale for a human reviewer. Name the rule behind "
            "each point, exactly as the evidence spells the citation. Use only "
            "figures from the list above and only thresholds written in the "
            "evidence. Do not introduce a number that appears in neither. State "
            "plainly where evidence is missing rather than filling the gap."
        )
    ]


@mcp.prompt(
    name="human_review_summary",
    description=(
        "Brief the human reviewer: what was decided, why it was routed to them, "
        "and what they need to look at first."
    ),
)
def human_review_summary(
    product_domain: str, outcome: str, reasons_json: str, figures_json: str
) -> list[prompt_base.Message]:
    """Prompt for the reviewer hand-off brief."""
    return [
        prompt_base.UserMessage(
            f"A {product_domain} file has been routed for human review at "
            f"CredPilot.\n\n"
            f"Machine recommendation: {outcome}\n"
            f"Why it was routed: {reasons_json}\n"
            f"Computed figures: {figures_json}\n\n"
            "Write a brief for the reviewer, at most six sentences. Lead with what "
            "they have to decide. Then the one or two facts that decide it. Then "
            "anything missing from the file.\n\n"
            "Do not recommend an outcome — the reviewer makes the decision, and a "
            "brief that pre-empts it is not a brief. Do not restate the machine "
            "recommendation as though it were settled. Do not introduce a figure "
            "or a threshold that is not above."
        )
    ]


@mcp.prompt(
    name="evidence_explanation",
    description=(
        "Explain one retrieved rule in plain English, without turning the "
        "explanation into a new threshold."
    ),
)
def evidence_explanation(
    citation: str, rule_text: str, applied_to: str = ""
) -> list[prompt_base.Message]:
    """Prompt for explaining a single rule."""
    return [
        prompt_base.UserMessage(
            f"Explain this lending rule to someone who is not an underwriter.\n\n"
            f"Citation: {citation}\n"
            f"Rule text:\n{rule_text}\n"
            + (f"\nIt was applied to: {applied_to}\n" if applied_to else "")
            + "\nThree or four sentences. Keep every number exactly as the rule "
            "states it — do not round, convert a percentage, or restate a limit in "
            "different units. If the rule depends on another rule, say which one "
            "rather than summarising what you assume it says. Do not say whether "
            "any particular file passes."
        )
    ]


def main() -> None:
    warm_up()
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
