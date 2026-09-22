"""Render ``reports/dashboard.png`` from the committed golden signals.

REQ-099: *"Dashboard | reports/dashboard.png + dashboard_data.csv"*.

The chart is drawn from ``reports/dashboard_data.csv``, which
``scripts/build_golden_signals.py`` writes — so the picture and the numbers
behind it cannot disagree, and a reader who distrusts the picture can open the
CSV.

Four panels, chosen because they answer the four questions actually asked of a
system like this:

1. **Is it right?** — outcome accuracy, per product and macro.
2. **Is it grounded?** — citation validity and recall, faithfulness by both the
   deterministic check and the judge, and the hallucination rate.
3. **Is it fast enough, and what does it cost?** — latency percentiles split
   between the deterministic pipeline and the single model call.
4. **Is it stable?** — failures, unfaithful rationales, budget halts.

Where a target exists it is drawn as a marker on the bar, so a reader sees the
measurement against the bar rather than in isolation.

Run::

    python -m eval.agent.run_agent_eval
    python scripts/build_golden_signals.py
    python scripts/build_dashboard.py
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Sequence

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
# Running this file directly puts scripts/ on sys.path; importing it as a module
# does not, so it is added explicitly rather than relied on.
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.config import REPO_ROOT  # noqa: E402
from src.console import use_utf8_stdio  # noqa: E402

REPORTS = REPO_ROOT / "reports"

# Both paths are defined by the script that *writes* them, and imported here.
# One definition of where an artifact lives, in the place that produces it —
# which also means this script, which only reads them, does not contain the
# literal filename and so cannot be mistaken for their producer.
from build_golden_signals import DASHBOARD_DATA, SIGNALS_PATH  # noqa: E402
DASHBOARD_PNG = REPORTS / "dashboard.png"

#: Muted, print-safe, and distinguishable in greyscale — these get screenshotted
#: into decks and printed for review meetings.
INK = "#1b1f23"
MUTED = "#6a737d"
GOOD = "#2f6f4f"
WARN = "#b07d2b"
BAD = "#a03232"
ACCENT = "#31566f"
GRID = "#e3e6ea"


def _load_rows(path: Path) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    with path.open("r", encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            row["value"] = float(row["value"])
            row["target"] = float(row["target"]) if row["target"] not in ("", None) else None
            grouped[row["group"]].append(row)
    return grouped


def _label(metric: str) -> str:
    return metric.replace("_", " ")


def _rate_colour(value: float, target: float | None, higher_is_better: bool = True) -> str:
    if target is not None:
        met = value >= target if higher_is_better else value <= target
        return GOOD if met else BAD
    if not higher_is_better:
        return GOOD if value <= 0.02 else (WARN if value <= 0.10 else BAD)
    return GOOD if value >= 0.9 else (WARN if value >= 0.7 else BAD)


def _rate_panel(ax, rows: Sequence[dict[str, Any]], title: str,
                lower_is_better: frozenset[str] = frozenset()) -> None:
    """Horizontal bars on a 0..1 axis, with targets marked."""
    labels = [_label(r["metric"]) for r in rows]
    values = [r["value"] for r in rows]
    positions = range(len(rows))

    colours = [
        _rate_colour(r["value"], r["target"], r["metric"] not in lower_is_better)
        for r in rows
    ]
    ax.barh(list(positions), values, color=colours, height=0.62, zorder=3)

    for index, row in enumerate(rows):
        ax.text(min(row["value"] + 0.02, 1.02), index, f"{row['value']:.3f}",
                va="center", ha="left", fontsize=8, color=INK, zorder=4)
        if row["target"] is not None:
            ax.plot([row["target"]], [index], marker="|", markersize=14,
                    color=INK, zorder=5)

    ax.set_yticks(list(positions))
    ax.set_yticklabels(labels, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlim(0, 1.12)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_title(title, fontsize=10, color=INK, loc="left", pad=8)
    ax.grid(axis="x", color=GRID, zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=MUTED, length=0)


def _latency_panel(ax, rows: Sequence[dict[str, Any]], signals: dict[str, Any]) -> None:
    labels = [_label(r["metric"]) for r in rows]
    values = [r["value"] for r in rows]
    positions = range(len(rows))
    # Thinking time is the billed, variable part; it gets the accent.
    colours = [
        ACCENT if r["metric"].startswith(("thinking", "narrative")) else MUTED
        for r in rows
    ]

    ax.barh(list(positions), values, color=colours, height=0.62, zorder=3)
    for index, value in enumerate(values):
        # A p50 of 36 ms printed as "0.0s" tells a reader nothing and looks
        # like a missing measurement. Sub-second values keep their unit.
        label = f"{value:.0f}ms" if value < 1000 else f"{value / 1000:.1f}s"
        ax.text(value * 1.02 + 20, index, label, va="center", ha="left",
                fontsize=8, color=INK, zorder=4)

    ax.set_yticks(list(positions))
    ax.set_yticklabels(labels, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlim(0, max(values) * 1.25 if values else 1)
    ax.set_title("Latency, from Phoenix spans — thinking / acting / tool",
                 fontsize=10, color=INK, loc="left", pad=8)
    ax.set_xlabel("milliseconds", fontsize=8, color=MUTED)
    ax.grid(axis="x", color=GRID, zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=MUTED, length=0)

    cost = signals.get("cost", {})
    tokens = signals.get("tokens", {})
    per_request = cost.get("system_per_traced_request")

    if tokens.get("model_calls_recorded_no_tokens"):
        # Saying "$0.0000 per assessment" here would read as an efficiency
        # result when it is the opposite: the calls never reached the provider.
        footer = (
            f"{tokens.get('model_calls', 0)} model call(s), all of which recorded "
            f"zero tokens — the provider was unreachable, so cost is unmeasured "
            f"rather than zero"
        )
    elif per_request is not None:
        footer = (
            f"${per_request:.4f} per traced request  ·  "
            f"{tokens.get('input_total', 0):,} in / "
            f"{tokens.get('output_total', 0):,} out tokens over "
            f"{tokens.get('model_calls', 0)} model call(s)  ·  "
            f"{(tokens.get('reasoning_share_of_output') or 0) * 100:.0f}% of output "
            f"is reasoning"
        )
    else:
        footer = ""

    if footer:
        ax.text(0.99, -0.30, footer, transform=ax.transAxes, ha="right", va="top",
                fontsize=7.5, color=MUTED)


def _reliability_panel(ax, rows: Sequence[dict[str, Any]], signals: dict[str, Any]) -> None:
    """Counts, not rates — a single unfaithful rationale matters, a mean does not."""
    ax.axis("off")
    ax.set_title("Reliability", fontsize=10, color=INK, loc="left", pad=8)

    lines: list[tuple[str, str, str]] = []
    for row in rows:
        if row["metric"] == "steps_taken_mean":
            budget = signals.get("saturation", {}).get("step_budget", 32)
            lines.append((
                "step budget used",
                f"{row['value']:.1f} of {budget}",
                GOOD if row["value"] < budget * 0.6 else WARN,
            ))
        elif row["metric"] == "failure_rate":
            lines.append((
                "failed runs",
                f"{row['value'] * 100:.1f}%",
                GOOD if row["value"] == 0 else BAD,
            ))
        else:
            lines.append((
                _label(row["metric"]),
                f"{int(row['value'])}",
                GOOD if row["value"] == 0 else BAD,
            ))

    # Two counts, because they measure different runs: the evaluation says how
    # many golden cases completed, the trace export says how many requests were
    # instrumented. Showing one under a label that implies the other is how the
    # panel came to read "0 of 0".
    errors = signals.get("errors", {})
    traffic = signals.get("traffic", {})
    completed = errors.get("eval_completed")
    cases = errors.get("eval_cases")
    if completed is not None and cases:
        lines.insert(0, ("golden cases run", f"{completed} of {cases}", INK))
    lines.insert(
        1 if completed is not None and cases else 0,
        ("traces instrumented", f"{traffic.get('traces', 0)}", INK),
    )

    for index, (label, value, colour) in enumerate(lines):
        y = 0.88 - index * 0.16
        ax.text(0.0, y, label, fontsize=9, color=MUTED, transform=ax.transAxes, va="center")
        ax.text(1.0, y, value, fontsize=11, color=colour, transform=ax.transAxes,
                va="center", ha="right", fontweight="bold")


def build(data_path: Path, signals_path: Path, output: Path) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    grouped = _load_rows(data_path)
    signals = json.loads(signals_path.read_text(encoding="utf-8")) if signals_path.exists() else {}

    figure, axes = plt.subplots(2, 2, figsize=(13, 8.5))
    figure.patch.set_facecolor("white")

    accuracy_rows = grouped.get("accuracy", []) + grouped.get("accuracy_by_product", [])
    _rate_panel(axes[0][0], accuracy_rows, "Decision accuracy (macro across products)")

    _rate_panel(
        axes[0][1],
        grouped.get("grounding", []),
        "Grounding — deterministic and judged",
        lower_is_better=frozenset({"hallucination_rate"}),
    )

    _latency_panel(axes[1][0], grouped.get("latency", []), signals)
    _reliability_panel(axes[1][1], grouped.get("reliability", []), signals)

    # `derived_from` became `sources` when the operational figures moved to
    # Phoenix, and reading the old key rendered every chart as "run unknown".
    # The subtitle now names both provenances, because the chart carries two.
    sources = signals.get("sources") or signals.get("derived_from") or {}
    evaluated = sources.get("eval_generated_at_utc") or "unknown"
    spans_from = str(sources.get("operational") or "unknown").split(":")[0]
    figure.suptitle(
        "CredPilot — agentic RAG underwriting copilot",
        fontsize=14, color=INK, x=0.06, ha="left", y=0.975, fontweight="bold",
    )
    figure.text(
        0.06, 0.935,
        f"Quality from the golden-set evaluation of {evaluated}  ·  "
        f"latency, tokens and cost from {spans_from.replace('_', ' ')}  ·  "
        f"synthetic data throughout",
        fontsize=9, color=MUTED, ha="left",
    )
    figure.text(
        0.06, 0.022,
        "Accuracy measures agreement with a synthetic generator, not correctness (R-01).",
        fontsize=7.5, color=MUTED, ha="left",
    )
    figure.text(
        0.06, 0.006,
        "The judge shares a model family with the system it grades (R-02); where the judged "
        "and deterministic figures disagree, the deterministic one governs.",
        fontsize=7.5, color=MUTED, ha="left",
    )

    figure.tight_layout(rect=(0.04, 0.055, 0.98, 0.91))
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=160, facecolor="white")
    plt.close(figure)
    return output


def main(argv: Sequence[str] | None = None) -> int:
    use_utf8_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default=str(DASHBOARD_DATA))
    parser.add_argument("--signals", default=str(SIGNALS_PATH))
    parser.add_argument("--output", default=str(DASHBOARD_PNG))
    args = parser.parse_args(argv)

    data_path = Path(args.data)
    if not data_path.exists():
        print(f"!! {data_path} not found — run `python scripts/build_golden_signals.py` first")
        return 1

    output = build(data_path, Path(args.signals), Path(args.output))
    size_kb = output.stat().st_size / 1024
    print(f"wrote {output} ({size_kb:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
