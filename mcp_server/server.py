#!/usr/bin/env python
"""CredPilot's MCP server.

Runs over stdio using the MCP Python SDK and is consumed from the agent side via
``langchain-mcp-adapters`` (see ``mcp_server/client.py``).

Surface:

**Tools**

``retrieve_policy``
    Hybrid, product-isolated policy retrieval over the committed lending-policy
    corpora. The same implementation the in-process agentic-RAG tool uses.
``resolve_citation``
    Check that a citation resolves to a committed policy document, and say where.
``list_policy_rules``
    Enumerate the rules a policy document declares, for a product.

**Resources**

``credpilot://policies/mortgage``
    The indexed mortgage policy inventory.
``credpilot://policies/education``
    The indexed education-loan policy inventory.
``credpilot://index/manifest``
    The index build manifest: models, counts, source hashes.

Product isolation holds across the MCP boundary exactly as it does in process:
the ``retrieve_policy`` tool requires a product domain or an application id it can
resolve one from, and returns ``PRODUCT_CLARIFICATION_REQUIRED`` rather than
searching both corpora.
"""

from __future__ import annotations

import contextlib
import functools
import json
import os
import sys
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

from mcp.server.fastmcp import FastMCP  # noqa: E402

from src.config import get_config  # noqa: E402
from src.domain import LendingProductDomain  # noqa: E402
from src.observability.tool_logging import log_mcp_exchange  # noqa: E402
from src.rag.citations import CitationResolver, parse_citation  # noqa: E402
from src.tools.rag_tool import (  # noqa: E402
    TOOL_DESCRIPTION,
    policy_corpus_summary,
    result_to_payload,
    retrieve_policy_tool,
)

mcp = FastMCP("credpilot")


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


@mcp.tool(name="retrieve_policy", description=TOOL_DESCRIPTION)
@protocol_safe
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
    request = {
        "query": query,
        "product_domain": product_domain,
        "application_id": application_id,
        "as_of_date": as_of_date,
        "product_family": product_family,
        "loan_purpose": loan_purpose,
        "occupancy_type": occupancy_type,
        "product_code": product_code,
        "top_k": top_k,
    }
    log_mcp_exchange(direction="request", method="tools/call:retrieve_policy", payload=request)

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
    log_mcp_exchange(
        direction="response",
        method="tools/call:retrieve_policy",
        payload={
            "status": payload["status"],
            "product_domain": payload["product_domain"],
            "evidence_count": payload["evidence_count"],
            "citations": [e["citation"] for e in payload["evidence"]],
        },
    )
    return payload


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
def resolve_citation(citation: str) -> dict[str, Any]:
    """Resolve one citation against the committed corpora."""
    log_mcp_exchange(
        direction="request", method="tools/call:resolve_citation", payload={"citation": citation}
    )
    config = get_config()
    parsed = parse_citation(citation)
    resolves, reason = CitationResolver(config).resolve(citation)
    payload = {
        "citation": citation,
        "resolves": resolves,
        "reason": reason,
        "product_domain": parsed.product_domain.value if parsed else None,
        "policy_id": parsed.policy_id if parsed else None,
        "policy_version": parsed.policy_version if parsed else None,
        "rule_id": parsed.rule_id if parsed else None,
    }
    log_mcp_exchange(
        direction="response", method="tools/call:resolve_citation", payload=payload
    )
    return payload


@mcp.tool(
    name="list_policy_rules",
    description=(
        "List the rules a lending-policy document declares. "
        "product_domain must be MORTGAGE or EDUCATION_LOAN; policy_id is optional "
        "and narrows the listing to one document."
    ),
)
@protocol_safe
def list_policy_rules(product_domain: str, policy_id: str | None = None) -> dict[str, Any]:
    """Enumerate declared rules for a product, optionally for one policy."""
    log_mcp_exchange(
        direction="request",
        method="tools/call:list_policy_rules",
        payload={"product_domain": product_domain, "policy_id": policy_id},
    )
    domain = LendingProductDomain.from_any(product_domain)
    summary = policy_corpus_summary()
    product = summary["products"][domain.corpus_key]
    policies = product["policies"]
    if policy_id:
        policies = [p for p in policies if p["policy_id"] == policy_id]
    payload = {
        "product_domain": domain.value,
        "policy_count": len(policies),
        "rule_count": sum(len(p["rule_ids"]) for p in policies),
        "policies": policies,
    }
    log_mcp_exchange(
        direction="response",
        method="tools/call:list_policy_rules",
        payload={k: v for k, v in payload.items() if k != "policies"},
    )
    return payload


@mcp.resource(
    "credpilot://policies/mortgage",
    name="mortgage_policy_inventory",
    description="Indexed U.S. residential mortgage policy documents, versions and rule ids.",
    mime_type="application/json",
)
@protocol_safe
def mortgage_policies() -> str:
    """The mortgage policy inventory."""
    log_mcp_exchange(
        direction="request",
        method="resources/read",
        payload={"uri": "credpilot://policies/mortgage"},
    )
    return json.dumps(policy_corpus_summary()["products"]["mortgage"], indent=2)


@mcp.resource(
    "credpilot://policies/education",
    name="education_policy_inventory",
    description="Indexed private education-loan policy documents, versions and rule ids.",
    mime_type="application/json",
)
@protocol_safe
def education_policies() -> str:
    """The education-loan policy inventory."""
    log_mcp_exchange(
        direction="request",
        method="resources/read",
        payload={"uri": "credpilot://policies/education"},
    )
    return json.dumps(policy_corpus_summary()["products"]["education"], indent=2)


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

    log_mcp_exchange(
        direction="request",
        method="resources/read",
        payload={"uri": "credpilot://index/manifest"},
    )
    return json.dumps(load_manifest(), indent=2)


def main() -> None:
    warm_up()
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
