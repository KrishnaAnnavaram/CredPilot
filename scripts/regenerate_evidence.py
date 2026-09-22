#!/usr/bin/env python
"""Regenerate every committed measurement from the current code, in one pass.

    python scripts/regenerate_evidence.py

Runs, in order:

1. ``scripts/build_policy_indexes.py``   — indexes, manifests, integrity report
2. ``eval/retrieval/sweep_pipeline.py``  — funnel-width table
3. ``eval/retrieval/ablation.py``        — layer-by-layer contribution
4. ``eval/retrieval/run_retrieval_eval.py`` — headline retrieval metrics
5. ``scripts/export_traces.py``          — Phoenix span export, both products
   and all six Supervisor routes
6. ``eval.agent.run_agent_eval``         — the 95-case end-to-end evaluation
7. ``scripts/build_golden_signals.py``   — Phoenix-derived operational signals,
   the dashboard table and the raw span CSV
8. ``scripts/build_dashboard.py``        — the chart, from that CSV

Why one command: every number published in ``docs/`` has to come from the same
code state. Measuring the funnel on Monday, changing the pipeline on Tuesday and
quoting Monday's figure is how a document ends up asserting two different values
for one configuration — which is exactly what happened here once, and what this
script exists to stop happening again.

The benchmarks (``benchmark_embeddings.py``, ``benchmark_rerankers.py``) are not
included: they take roughly an hour between them and only need re-running when a
candidate model list changes. Run them separately.

Anything non-zero fails the run, and the step that failed is named.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

STEPS: tuple[tuple[str, list[str]], ...] = (
    ("indexes", ["scripts/build_policy_indexes.py"]),
    ("funnel sweep", ["eval/retrieval/sweep_pipeline.py"]),
    ("ablation", ["eval/retrieval/ablation.py"]),
    ("retrieval evaluation", ["eval/retrieval/run_retrieval_eval.py", "--quiet"]),
    ("trace export", ["scripts/export_traces.py"]),
    ("agent evaluation", ["-m", "eval.agent.run_agent_eval", "--judge-all"]),
    ("golden signals", ["scripts/build_golden_signals.py",
                        "--raw-spans-csv", "reports/phoenix_spans.csv"]),
    ("dashboard", ["scripts/build_dashboard.py"]),
)

#: The agent evaluation's judged pass needs a model that actually answers.
#:
#: The test used to be "is a key present", which is the wrong question and was
#: wrong here: the committed key is correctly formed, reaches the service, and
#: returns 402 RESOURCE_EXHAUSTED from every model. On that test the step ran,
#: the judge failed case by case, and the run produced a report with null
#: judged metrics under a command that promised judged ones.
#:
#: The gate is now whether the model answers. When it does not, the step still
#: runs — with `--no-judge`, so every deterministic metric refreshes and the
#: report says plainly that no case was judged and why.
STEPS_NEEDING_A_WORKING_MODEL: dict[str, list[str]] = {
    "agent evaluation": ["-m", "eval.agent.run_agent_eval", "--no-judge"],
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--skip", nargs="*", default=[], help="step names to skip")
    parser.add_argument("--only", nargs="*", default=None, help="run only these steps")
    args = parser.parse_args(argv)

    from src.console import use_utf8_stdio

    use_utf8_stdio()

    print("CredPilot — regenerating committed evidence")
    print(f"  python {sys.version.split()[0]}")
    print()

    started = time.perf_counter()
    from src import llm

    status = llm.probe()
    if status.available:
        print(f"  model  {status.model} (reachable)")
    else:
        print(f"  model  unreachable — {status.reason[:140]}")
        print("         steps that need one fall back to their deterministic mode")
    print()

    for name, command in STEPS:
        if name in args.skip or (args.only and name not in args.only):
            print(f"[skip] {name}")
            continue
        if name in STEPS_NEEDING_A_WORKING_MODEL and not status.available:
            command = STEPS_NEEDING_A_WORKING_MODEL[name]
            print(f"[note] {name}: the model does not answer, so this runs "
                  f"deterministic-only. Every judge_* figure in the report will "
                  f"be null, with the reason recorded.")
        print(f"[run ] {name}: python {' '.join(command)}", flush=True)
        step_started = time.perf_counter()
        result = subprocess.run(
            [sys.executable, *command], cwd=str(REPO_ROOT), check=False
        )
        elapsed = time.perf_counter() - step_started
        if result.returncode != 0:
            print()
            print(f"[FAIL] {name} exited {result.returncode} after {elapsed:.0f}s")
            return result.returncode
        print(f"[ ok ] {name} in {elapsed:.0f}s")
        print()

    print(f"All steps completed in {time.perf_counter() - started:.0f}s.")
    print("Committed evidence is now consistent with the current code.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
