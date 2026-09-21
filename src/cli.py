#!/usr/bin/env python
"""CredPilot command line interface.

    python -m src.cli assess synthetic_data/mortgage/applications/APP-000056.json
    python -m src.cli assess synthetic_data/education/applications/APP-2026-00002.json
    python -m src.cli retrieve "What is the maximum back-end DTI?" --application-id APP-000056
    python -m src.cli corpus

``assess`` runs one application through the full LangGraph, writing the
tool-invocation log, the audit trail and (with ``--trace``) a Phoenix trace
export. ``retrieve`` exercises the agentic-RAG tool on its own. ``corpus`` prints
what is indexed.
"""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.console import use_utf8_stdio  # noqa: E402
from src.observability.tracing import configure_tracing, flush_traces  # noqa: E402


def cmd_assess(args: argparse.Namespace) -> int:
    from src.graph import build_graph, initial_state, state_evidence

    if args.trace:
        configure_tracing()

    graph, context = build_graph()
    try:
        state = initial_state(args.application, as_of_date=args.as_of_date)
        thread_id = args.thread_id or f"{state['application_id']}-{uuid.uuid4().hex[:8]}"
        result = graph.invoke(state, config={"configurable": {"thread_id": thread_id}})
    finally:
        if context is not None:
            context.__exit__(None, None, None)

    evidence = state_evidence(result)
    recommendation = result.get("recommendation") or {}
    payload = {
        "application_id": result.get("application_id"),
        "loan_domain": result.get("loan_domain"),
        "as_of_date": result.get("as_of_date"),
        "thread_id": thread_id,
        "nodes_visited": result.get("steps"),
        "retrieval_statuses": result.get("retrieval_statuses"),
        "policy_dependencies": result.get("policy_dependencies"),
        "calculations": result.get("calculations"),
        "eligibility": result.get("eligibility"),
        "risk": result.get("risk"),
        "recommendation": recommendation,
        "requires_human_review": result.get("requires_human_review"),
        "human_review_reasons": result.get("human_review_reasons"),
        "security_findings": result.get("security_findings"),
        "evidence_count": len(evidence),
        "citations": recommendation.get("citations", []),
        "narrative": result.get("narrative"),
        "review_triggers": recommendation.get("review_triggers"),
    }

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))
    else:
        _print_assessment(payload, evidence)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(
            json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8"
        )
        print(f"\nWritten to {args.output}")

    if args.trace:
        flush_traces()
    return 0


def _print_rationale(payload: dict) -> None:
    """Print the written rationale, and be explicit about its provenance.

    A reader has to be able to tell three states apart at a glance: prose a model
    wrote and that passed its grounding check, prose that failed it, and the
    deterministic summary produced when no model was reachable. Printing all
    three identically would be the quiet failure this whole node is guarded
    against.
    """
    narrative = payload.get("narrative") or {}
    text = (narrative.get("text") or "").strip()
    if not text:
        return

    print("Rationale")
    if not narrative.get("available"):
        print(f"  [no model — deterministic summary. {narrative.get('note', '')}]")
    elif not narrative.get("is_faithful"):
        print("  [!] this rationale asserted something its evidence does not support:")
        for citation in narrative.get("unsupported_citations") or []:
            print(f"      unsupported citation: {citation}")
        for figure in narrative.get("unsupported_figures") or []:
            print(f"      unsupported figure:   {figure}")
        print("      it is shown as written, marked, and routed to a human.")
    else:
        used = len(narrative.get("citations_used") or [])
        print(f"  [{narrative.get('model')} — {used} citation(s), all supported by the evidence]")

    print()
    for line in textwrap.wrap(text, width=88, replace_whitespace=False) if "\n" not in text \
            else text.splitlines():
        print(f"  {line}")
    print()


def _print_review_triggers(payload: dict) -> None:
    """The mandatory routing table, when it fired."""
    review = payload.get("review_triggers") or {}
    triggers = review.get("triggers") or []
    if not triggers:
        return
    print(f"Human review required — {review.get('rule_citation')}")
    for trigger in triggers:
        print(f"  - {trigger['trigger']}: {trigger['detail']}")
    print()


def _print_assessment(payload: dict, evidence: list[dict]) -> None:
    print(f"Application    {payload['application_id']}  ({payload['loan_domain']})")
    print(f"As-of date     {payload['as_of_date']}")
    print(f"Nodes visited  {' -> '.join(payload['nodes_visited'] or [])}")
    print()

    calculations = payload.get("calculations") or {}
    if calculations.get("ratios"):
        print("Calculations (deterministic, formula "
              f"{calculations.get('formula_version')})")
        for name, value in sorted(calculations["ratios"].items()):
            print(f"  {name:<28} {value:.4f}")
        for name in calculations.get("indeterminate", []):
            print(f"  {name:<28} INDETERMINATE")
        print()

    eligibility = payload.get("eligibility") or {}
    print(f"Eligibility    {eligibility.get('status')}")
    for breach in eligibility.get("breaches", []):
        print(
            f"  BREACH {breach['measure']}: observed {breach['observed']:.4f} "
            f"{breach['comparator']} {breach['threshold']:.4f}  [{breach['citation']}]"
        )
    risk = payload.get("risk") or {}
    print(f"Risk           {risk.get('level')}  {risk.get('flags') or ''}")
    print()

    recommendation = payload.get("recommendation") or {}
    print(f"Recommendation {recommendation.get('outcome')}")
    if payload.get("requires_human_review"):
        print("  HUMAN REVIEW REQUIRED")
        for reason in payload.get("human_review_reasons") or []:
            print(f"    - {reason}")
    print()

    _print_review_triggers(payload)
    _print_rationale(payload)

    print(f"Policy evidence ({len(evidence)} chunks, "
          f"{len(payload.get('citations') or [])} distinct citations, "
          f"all resolve: {recommendation.get('all_citations_resolve')})")
    for citation in (payload.get("citations") or [])[:12]:
        print(f"  {citation}")
    if len(payload.get("citations") or []) > 12:
        print(f"  ... and {len(payload['citations']) - 12} more")


def cmd_retrieve(args: argparse.Namespace) -> int:
    from src.tools.rag_tool import retrieve_policy_tool

    if args.trace:
        configure_tracing()

    result = retrieve_policy_tool(
        query=args.query,
        product_domain=args.product_domain,
        application_id=args.application_id,
        as_of_date=args.as_of_date,
        top_k=args.top_k,
        agent="cli",
    )
    print(f"status         {result.status.value}")
    print(f"product        {result.product_domain.value}")
    print(f"latency        {result.latency_ms:.0f} ms")
    if result.message:
        print(f"message        {result.message}")
    print()
    for item in result.evidence:
        print(f"{item.final_rank}. {item.citation}   (resolves: {item.citation_resolves})")
        print(f"   {item.rule_title or item.section_title or item.policy_title}")
        if args.verbose:
            print(f"   {item.text[:400].replace(chr(10), ' ')}")
        print()

    if args.trace:
        flush_traces()
    return 0


def cmd_corpus(args: argparse.Namespace) -> int:
    from src.tools.rag_tool import policy_corpus_summary

    summary = policy_corpus_summary()
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    for key, product in sorted(summary["products"].items()):
        print(f"{product['product_domain']}  ({product['collection']})")
        print(f"  corpus root  {product['corpus_root']}")
        print(f"  documents    {product['document_count']}")
        print(f"  rules        {product['declared_rule_count']}")
        for policy in product["policies"]:
            version = f" v{policy['policy_version']}" if policy["policy_version"] else ""
            print(
                f"    {policy['policy_id']}{version:<6} "
                f"eff {policy['effective_date']}  "
                f"{len(policy['rule_ids'])} rules  {policy['policy_title'][:44]}"
            )
        print()
    print(f"embedding {summary['embedding_model']}  ·  reranker {summary['reranker_model']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="credpilot", description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)

    assess = sub.add_parser("assess", help="run one application through the graph")
    assess.add_argument("application", help="path to an application packet JSON")
    assess.add_argument("--as-of-date", default=None, help="override the underwriting as-of date")
    assess.add_argument("--thread-id", default=None, help="checkpointer thread id")
    assess.add_argument("--json", action="store_true", help="print JSON instead of a report")
    assess.add_argument("--output", default=None, help="also write the result to this path")
    assess.add_argument("--trace", action="store_true", help="emit Phoenix spans")
    assess.set_defaults(func=cmd_assess)

    retrieve = sub.add_parser("retrieve", help="run the agentic-RAG tool directly")
    retrieve.add_argument("query")
    retrieve.add_argument("--product-domain", default=None, help="MORTGAGE or EDUCATION_LOAN")
    retrieve.add_argument("--application-id", default=None)
    retrieve.add_argument("--as-of-date", default=None)
    retrieve.add_argument("--top-k", type=int, default=None)
    retrieve.add_argument("--verbose", action="store_true", help="print evidence text")
    retrieve.add_argument("--trace", action="store_true", help="emit Phoenix spans")
    retrieve.set_defaults(func=cmd_retrieve)

    corpus = sub.add_parser("corpus", help="show what is indexed")
    corpus.add_argument("--json", action="store_true")
    corpus.set_defaults(func=cmd_corpus)

    return parser


def main(argv: list[str] | None = None) -> int:
    use_utf8_stdio()
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
