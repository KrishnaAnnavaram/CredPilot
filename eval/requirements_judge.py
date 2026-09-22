"""Grade the implementation against the requirements document, with Gemini as judge.

The suite in ``requirements_validation_tests/`` grades deterministically: a check
either found its evidence or it did not. This is the second opinion — a model
reads the *exact* source requirement beside the *actual* evidence collected for
it, and says whether the evidence really satisfies what the sentence asked for.

The two answer different questions, and the difference is the point. A
deterministic check can pass on a file that exists and is empty of meaning, and
it can fail on a requirement that is genuinely met in a shape nobody anticipated.
A judge catches both, and misses things a regex never would. Neither is
authoritative alone, so this reports **both** and flags every disagreement.

Strictness, as instructed
-------------------------
The rubric below is deliberately unforgiving:

* no evidence is ``NOT_MET``, never "probably fine";
* evidence that shows a *path exists* is not evidence the path contains what the
  requirement asked for;
* a requirement naming several things is met only when every one of them is
  evidenced;
* where the source document fixes no value to test against, the verdict is
  ``UNVERIFIABLE`` and the requirement is **excluded from the score** rather than
  counted either way — scoring an unanswerable question would move the total
  without measuring anything.

Never invented
--------------
If Gemini does not answer, this writes a report whose every judged figure is
``null``, records why, and exits non-zero. It does not fall back to the
deterministic result and present it as a judgment, and it does not carry a score
over from an earlier run. A grade nobody produced is worse than no grade.

Usage
-----
    python eval/requirements_judge.py
    python eval/requirements_judge.py --limit 10          # a cheap smoke run
    python eval/requirements_judge.py --only REQ-038 REQ-042
    python eval/requirements_judge.py --model gemini-flash-latest
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src import llm  # noqa: E402

VALIDATION_REPORT = (
    REPO_ROOT / "requirements_validation_tests" / "reports" / "latest_test_report.json"
)
DEFAULT_OUT = REPO_ROOT / "reports" / "requirements_judge.json"
DEFAULT_MD = REPO_ROOT / "reports" / "requirements_judge.md"

#: Cold, for the same reason the DeepEval judge is: grading is classification,
#: and a judge that changes its mind between runs makes a regression
#: indistinguishable from noise.
TEMPERATURE = 0.0
THINKING_LEVEL = "low"

VERDICTS = ("MET", "PARTIAL", "NOT_MET", "UNVERIFIABLE")

#: Verdict -> the score it contributes. PARTIAL is worth half; NOT_MET nothing.
#: UNVERIFIABLE is absent on purpose: those requirements leave the denominator.
VERDICT_SCORE = {"MET": 1.0, "PARTIAL": 0.5, "NOT_MET": 0.0}

SYSTEM_RUBRIC = """\
You are grading a software implementation against a requirements document for a
loan origination and underwriting copilot. You are a strict, sceptical reviewer.
Your reputation depends on not passing work that was not done.

You will be given ONE requirement, verbatim from the requirements document, and
the EVIDENCE an automated validator collected from the repository for it.

Grade with one of exactly four verdicts:

MET
    The evidence demonstrates every part of what the requirement asks for. If the
    requirement names several things (a library AND its use; a file AND its
    contents), every one must be evidenced.

PARTIAL
    Some of what the requirement asks for is evidenced and some is not. Use this
    when a requirement names several things and only some are shown.

NOT_MET
    The evidence does not demonstrate the requirement. No evidence is NOT_MET.
    A path existing is NOT evidence that the path contains what was asked for.

UNVERIFIABLE
    The requirement asks for something the source document itself never fixes a
    value for, so no implementation could be checked against it - for example a
    numeric threshold the document never states, or the identity of an externally
    assigned system. Use this ONLY for a gap in the requirement, never for a gap
    in the implementation.

Rules:
- Judge ONLY from the evidence given. Do not assume code exists because it would
  be sensible for it to exist.
- Do not reward intent, documentation about a thing, or a plan to do a thing.
- Be harsher than you feel comfortable being. A generous grade here is a defect
  shipped to an underwriting system.

Reply with ONLY a JSON object, no prose and no code fence:
{"verdict": "MET|PARTIAL|NOT_MET|UNVERIFIABLE",
 "confidence": 0.0-1.0,
 "reason": "one sentence, citing what in the evidence decided it",
 "missing": "what is absent, or empty string if nothing is"}
"""

PROMPT = """\
REQUIREMENT ID: {req_id}
CATEGORY: {category}
SOURCE LOCATION: {source_location}

REQUIREMENT (verbatim from the requirements document):
\"\"\"
{requirement}
\"\"\"

EVIDENCE COLLECTED FROM THE REPOSITORY:
\"\"\"
{evidence}
\"\"\"

Grade this requirement. JSON only.
"""

_JSON = re.compile(r"\{.*\}", re.S)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_requirements(report_path: Path) -> list[dict]:
    """Each requirement, with the evidence the validator actually collected."""
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    if payload.get("partial_run"):
        raise SystemExit(
            f"ERROR: {report_path} is from a partial validator run. Run the full "
            "suite first: python requirements_validation_tests/runners/run_all_tests.py"
        )

    evidence_by_req: dict[str, list[str]] = defaultdict(list)
    for t in payload["tests"]:
        block = t["evidence"]
        text = block if isinstance(block, str) else "\n".join(str(x) for x in block)
        evidence_by_req[t["requirement_id"]].append(
            f"[{t['test_id']} {t['status']}] {text}"
        )

    out = []
    for r in payload["requirements"]:
        out.append({
            "requirement_id": r["requirement_id"],
            "requirement": r["exact_requirement"],
            "category": r["category"],
            "requirement_class": r["requirement_class"],
            "source_location": r["source_location"],
            "deterministic_status": r["status"],
            "deterministic_fit": r["fit_score"],
            "evidence": "\n".join(evidence_by_req.get(r["requirement_id"], [])) or
                        "(no evidence was collected)",
        })
    return out


def parse_verdict(text: str) -> dict | None:
    """Read the judge's JSON, tolerating a code fence or stray prose around it."""
    match = _JSON.search(text or "")
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    verdict = str(data.get("verdict", "")).upper().strip()
    if verdict not in VERDICTS:
        return None
    try:
        confidence = float(data.get("confidence", 0.0))
    except (TypeError, ValueError):
        confidence = 0.0
    return {
        "verdict": verdict,
        "confidence": max(0.0, min(1.0, confidence)),
        "reason": str(data.get("reason", ""))[:600],
        "missing": str(data.get("missing", ""))[:600],
    }


def judge_all(rows: list[dict], model_name: str, *, max_evidence: int,
              quiet: bool = False) -> tuple[list[dict], dict]:
    """Grade every requirement. Returns (results, usage)."""
    from langchain_core.messages import HumanMessage, SystemMessage

    chat = llm.chat_model(model_name, temperature=TEMPERATURE,
                          thinking_level=THINKING_LEVEL)

    results: list[dict] = []
    usage = {"calls": 0, "input_tokens": 0, "output_tokens": 0, "failures": 0}

    for i, row in enumerate(rows, 1):
        evidence = row["evidence"]
        if len(evidence) > max_evidence:
            evidence = evidence[:max_evidence] + "\n...[evidence truncated]"

        prompt = PROMPT.format(
            req_id=row["requirement_id"],
            category=row["category"],
            source_location=row["source_location"],
            requirement=row["requirement"],
            evidence=evidence,
        )

        verdict, error = None, None
        for attempt in range(3):
            try:
                reply = chat.invoke([
                    SystemMessage(content=SYSTEM_RUBRIC),
                    HumanMessage(content=prompt),
                ])
                usage["calls"] += 1
                counts = llm.usage_of(reply)
                usage["input_tokens"] += counts.get("input_tokens", 0)
                usage["output_tokens"] += counts.get("output_tokens", 0)
                verdict = parse_verdict(llm.message_text(reply))
                if verdict:
                    break
                error = "the judge did not return a parsable verdict"
            except Exception as exc:  # noqa: BLE001 - recorded, not raised
                error = f"{type(exc).__name__}: {str(exc)[:200]}"
                time.sleep(1.5 * (attempt + 1))

        if verdict is None:
            usage["failures"] += 1
            # Not scored, and not quietly treated as a pass or a fail.
            verdict = {"verdict": None, "confidence": None,
                       "reason": f"NOT JUDGED: {error}", "missing": ""}

        results.append({**row, "judge": verdict})
        if not quiet:
            v = verdict["verdict"] or "NOT JUDGED"
            print(f"[{i:>3}/{len(rows)}] {row['requirement_id']}  {v:<12} "
                  f"(deterministic: {row['deterministic_status']})", flush=True)

    return results, usage


def summarise(results: list[dict]) -> dict:
    """Aggregate, excluding UNVERIFIABLE from the denominator."""
    judged = [r for r in results if r["judge"]["verdict"] is not None]
    counts = {v: sum(1 for r in judged if r["judge"]["verdict"] == v) for v in VERDICTS}

    scorable = [r for r in judged if r["judge"]["verdict"] in VERDICT_SCORE]
    earned = sum(VERDICT_SCORE[r["judge"]["verdict"]] for r in scorable)
    score = round(100.0 * earned / len(scorable), 1) if scorable else None

    by_category: dict[str, dict] = {}
    for r in scorable:
        c = by_category.setdefault(r["category"], {"scorable": 0, "earned": 0.0})
        c["scorable"] += 1
        c["earned"] += VERDICT_SCORE[r["judge"]["verdict"]]
    for c in by_category.values():
        c["score_pct"] = round(100.0 * c["earned"] / c["scorable"], 1)

    disagreements = [
        {
            "requirement_id": r["requirement_id"],
            "deterministic": r["deterministic_status"],
            "judge": r["judge"]["verdict"],
            "reason": r["judge"]["reason"],
        }
        for r in judged
        if (r["deterministic_status"] == "PASS" and r["judge"]["verdict"] in ("NOT_MET", "PARTIAL"))
        or (r["deterministic_status"] == "FAIL" and r["judge"]["verdict"] == "MET")
    ]

    return {
        "total_requirements": len(results),
        "judged": len(judged),
        "not_judged": len(results) - len(judged),
        "scorable": len(scorable),
        "excluded_unverifiable": counts["UNVERIFIABLE"],
        "verdict_counts": counts,
        "judge_score_pct": score,
        "by_category": by_category,
        "disagreements_with_deterministic": disagreements,
    }


def render_markdown(payload: dict) -> str:
    s = payload["summary"]
    j = payload["judge"]
    out = [
        "# Requirements grade — Gemini as judge\n",
        f"Generated: {payload['generated_at']}  ",
        f"Judge: `{j['model'] or 'none'}` ({j['provider']})  ",
        f"Judge available: **{j['available']}**  ",
        f"Source of requirements: `{payload['requirements_source']}`  ",
        f"Baseline SHA-256: `{payload['baseline_sha256']}`\n",
    ]

    if not j["available"]:
        out += [
            "\n> ## NO REQUIREMENT WAS JUDGED\n",
            f"> The judge was unreachable: `{j['unavailable_reason']}`\n",
            "> Every judged figure below is `null`. They are **not** zero, and they "
            "have **not** been carried over from an earlier run — they were not "
            "measured. The deterministic validator result is reported beside them "
            "and is unaffected.\n",
        ]
        return "\n".join(out) + "\n"

    out += [
        "\n## Headline\n",
        "```",
        f"Requirements graded      : {s['judged']} / {s['total_requirements']}",
        f"Scorable (excl. UNVERIF.): {s['scorable']}",
        f"MET                      : {s['verdict_counts']['MET']}",
        f"PARTIAL                  : {s['verdict_counts']['PARTIAL']}",
        f"NOT_MET                  : {s['verdict_counts']['NOT_MET']}",
        f"UNVERIFIABLE (excluded)  : {s['verdict_counts']['UNVERIFIABLE']}",
        "",
        f"JUDGE SCORE              : {s['judge_score_pct']}%",
        "```\n",
        "\nPARTIAL counts as half. UNVERIFIABLE requirements are excluded from the "
        "denominator rather than scored, because the source document fixes no value "
        "for them and grading an unanswerable question would move the total without "
        "measuring anything.\n",
        "\n## Where it is missing\n",
    ]

    missing = [r for r in payload["results"]
               if r["judge"]["verdict"] in ("NOT_MET", "PARTIAL")]
    if missing:
        out += ["| Requirement | Verdict | Category | What is missing |",
                "| --- | --- | --- | --- |"]
        for r in sorted(missing, key=lambda x: (x["judge"]["verdict"], x["requirement_id"])):
            gap = " ".join((r["judge"]["missing"] or r["judge"]["reason"]).split())
            out.append(f"| `{r['requirement_id']}` | **{r['judge']['verdict']}** | "
                       f"{r['category']} | {gap[:220]} |")
    else:
        out.append("Nothing. Every scorable requirement was judged MET.\n")

    out += ["\n## By category\n", "| Category | Scorable | Score |",
            "| --- | --- | --- |"]
    for cat, c in sorted(payload["summary"]["by_category"].items(),
                         key=lambda kv: kv[1]["score_pct"]):
        out.append(f"| {cat} | {c['scorable']} | {c['score_pct']}% |")

    dis = s["disagreements_with_deterministic"]
    out += ["\n## Where the judge disagrees with the deterministic validator\n"]
    if dis:
        out += ["These are the rows worth a human's attention: one of the two graders "
                "is wrong.\n",
                "| Requirement | Deterministic | Judge | Judge's reason |",
                "| --- | --- | --- | --- |"]
        for d in dis:
            out.append(f"| `{d['requirement_id']}` | {d['deterministic']} | "
                       f"**{d['judge']}** | {' '.join(d['reason'].split())[:200]} |")
    else:
        out.append("None. The two graders agree on every requirement.\n")

    out += [
        "\n---\n",
        "## How to read this\n",
        "* The judge and the system under test are the same model family, so a "
        "shared blind spot would not show up here. This is evidence, not proof.\n"
        "* The judge sees the evidence the validator collected, not the repository. "
        "It can therefore only be as good as that evidence.\n"
        "* **This is not the 7-category / 100-mark Hackathon Rubric.** That rubric is "
        "not in this repository and has not been run. This grades the requirements "
        "document, which is a different thing.\n",
    ]
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--report", default=str(VALIDATION_REPORT))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--md-out", default=str(DEFAULT_MD))
    ap.add_argument("--model", default=None, help="override the judge model")
    ap.add_argument("--limit", type=int, default=None, help="grade only the first N")
    ap.add_argument("--only", nargs="*", default=None, help="grade only these requirement IDs")
    ap.add_argument("--max-evidence", type=int, default=6000,
                    help="characters of evidence per requirement")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    from src.console import use_utf8_stdio

    use_utf8_stdio()

    report_path = Path(args.report)
    if not report_path.exists():
        print(f"ERROR: no validation report at {report_path}.")
        print("Run: python requirements_validation_tests/runners/run_all_tests.py")
        return 2

    validation = json.loads(report_path.read_text(encoding="utf-8"))
    rows = load_requirements(report_path)
    if args.only:
        wanted = set(args.only)
        rows = [r for r in rows if r["requirement_id"] in wanted]
    if args.limit:
        rows = rows[: args.limit]
    if not rows:
        print("No requirements selected.")
        return 2

    status = llm.probe()
    print(f"Judge model      : {args.model or status.model or '(none reachable)'}")
    print(f"Judge available  : {status.available}")
    if not status.available:
        print(f"Reason           : {status.reason}")
    print(f"Requirements     : {len(rows)}\n")

    started = time.perf_counter()

    if not status.available:
        payload = {
            "generated_at": _now(),
            "requirements_source": "requirements_validation_tests/source_requirements/requirements_verbatim.md",
            "baseline_sha256": validation.get("baseline_sha256"),
            "judge": {
                "provider": "google-gemini",
                "model": None,
                "available": False,
                "unavailable_reason": status.reason,
                "note": (
                    "NO REQUIREMENT WAS JUDGED. Every judged figure is null. They are "
                    "not zero and they were not carried over from an earlier run - "
                    "they were not measured."
                ),
            },
            "summary": None,
            "results": [],
            "deterministic_reference": {
                "requirements_passed": validation["summary"]["requirements_passed"],
                "requirements_failed": validation["summary"]["requirements_failed"],
                "overall_fit_pct": validation["summary"]["overall_fit_pct"],
                "failed_requirement_ids": validation["summary"]["failed_requirement_ids"],
            },
        }
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        Path(args.md_out).write_text(render_markdown(payload), encoding="utf-8")
        print("=" * 72)
        print("NO REQUIREMENT WAS JUDGED - the judge is unreachable.")
        print(f"  {status.reason}")
        print("")
        print("No score has been written. The deterministic validator result is")
        print(f"  {validation['summary']['requirements_passed']} / "
              f"{validation['summary']['total_requirements']} requirements, "
              f"{validation['summary']['overall_fit_pct']}% fit")
        print("and is unaffected by the judge being down.")
        print("=" * 72)
        print(f"\nReports written:\n  {args.out}\n  {args.md_out}")
        return 3

    model_name = args.model or status.model
    results, usage = judge_all(rows, model_name, max_evidence=args.max_evidence,
                               quiet=args.quiet)
    summary = summarise(results)
    duration = round(time.perf_counter() - started, 1)

    payload = {
        "generated_at": _now(),
        "requirements_source": "requirements_validation_tests/source_requirements/requirements_verbatim.md",
        "baseline_sha256": validation.get("baseline_sha256"),
        "duration_seconds": duration,
        "judge": {
            "provider": "google-gemini",
            "model": model_name,
            "available": True,
            "unavailable_reason": None,
            "temperature": TEMPERATURE,
            "thinking_level": THINKING_LEVEL,
            "calls": usage["calls"],
            "input_tokens": usage["input_tokens"],
            "output_tokens": usage["output_tokens"],
            "unparsable_or_failed": usage["failures"],
            "cost_usd": round(
                llm.estimate_cost_usd(usage["input_tokens"], usage["output_tokens"]), 4
            ),
            "caveat": (
                "The judge and the system under test are the same model family, so a "
                "shared blind spot would not show up here. Evidence, not proof."
            ),
        },
        "summary": summary,
        "results": results,
        "deterministic_reference": {
            "requirements_passed": validation["summary"]["requirements_passed"],
            "requirements_failed": validation["summary"]["requirements_failed"],
            "overall_fit_pct": validation["summary"]["overall_fit_pct"],
            "failed_requirement_ids": validation["summary"]["failed_requirement_ids"],
        },
    }

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                              encoding="utf-8")
    Path(args.md_out).write_text(render_markdown(payload), encoding="utf-8")

    print("\n" + "=" * 72)
    print("Requirements grade - Gemini as judge")
    print("")
    print(f"Graded           : {summary['judged']} / {summary['total_requirements']}")
    print(f"MET              : {summary['verdict_counts']['MET']}")
    print(f"PARTIAL          : {summary['verdict_counts']['PARTIAL']}")
    print(f"NOT_MET          : {summary['verdict_counts']['NOT_MET']}")
    print(f"UNVERIFIABLE     : {summary['verdict_counts']['UNVERIFIABLE']} (excluded)")
    print("")
    print(f"JUDGE SCORE      : {summary['judge_score_pct']}%")
    print("=" * 72)
    if usage["failures"]:
        print(f"WARNING: {usage['failures']} requirement(s) could not be judged and are "
              "excluded. They are recorded as NOT JUDGED, not as failures.")
    print(f"\nReports written:\n  {args.out}\n  {args.md_out}")
    return 0 if summary["verdict_counts"]["NOT_MET"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
