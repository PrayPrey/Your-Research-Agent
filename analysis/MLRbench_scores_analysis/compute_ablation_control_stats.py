#!/usr/bin/env python3
"""Compute the substitution-control statistics from the raw judge JSONs.

Derives, directly from the per-review JSON files bundled in this repository,
the full statistics for the two within-YouRA substitution controls on the
Sonnet 4.5 backbone:

  * baseline        results/evaluations/mlrbench_overall_score/youra/sonnet45
  * no-VSA          .../youra_ablation_study/sonnet45_no_VSA
                    (persistence-versus-context control)
  * controller-off  .../youra_ablation_study/sonnet45_no_IC
                    (independent-controller control)

For each lane it reports the per-metric lane summary (mean +/- sample SD
across the ten task-level four-judge averages), the deltas of each control
against the baseline, the per-task Overall comparison with direction counts,
the exact two-sided paired permutation test (all 2^10 sign assignments) and
the two-sided sign test (ties excluded), and the per-lane Overall task-mean
range.

Pure standard library; locates the repository root by walking up from this
file, so it runs from any working directory in a fresh clone:

    python analysis/MLRbench_scores_analysis/compute_ablation_control_stats.py

The full report (no timestamps, so re-runs are byte-identical) is also
written to compute_ablation_control_stats_results.txt next to this script.
"""
from __future__ import annotations

import itertools
import json
from math import comb
from pathlib import Path
from statistics import mean, stdev

HERE = Path(__file__).resolve().parent
MARKER = Path("results") / "evaluations" / "mlrbench_overall_score"

METRICS = ["Clarity", "Novelty", "Soundness", "Significance", "Overall"]
TASKS = ["bi_align", "buildingtrust", "data_problems", "dl4c", "mldpr",
         "question", "scope", "scsl", "verifai", "wsl"]

LANES = [
    # (label, system dir, lane dir)
    ("baseline (full YouRA)", "youra", "sonnet45"),
    ("no-VSA (state in context)", "youra_ablation_study", "sonnet45_no_VSA"),
    ("controller-off (no-IC)", "youra_ablation_study", "sonnet45_no_IC"),
]

REPORT: list[str] = []


def emit(line: str = "") -> None:
    REPORT.append(line)
    print(line)


def find_repo_root() -> Path:
    cur = HERE
    while True:
        if (cur / MARKER).is_dir():
            return cur
        if cur.parent == cur:
            raise RuntimeError(f"Could not locate {MARKER} above {HERE}")
        cur = cur.parent


def score(path: Path, metric: str) -> float:
    v = json.load(path.open())[metric]
    return float(v["score"] if isinstance(v, dict) else v)


def task_means(lane_root: Path, metric: str) -> dict[str, float]:
    """Judge-averaged mean per task. Task dirs may carry lane suffixes."""
    out: dict[str, float] = {}
    for t in TASKS:
        vals = [score(p, metric)
                for d in lane_root.rglob(f"iclr2025_{t}*")
                if d.is_dir()
                for p in sorted(d.glob("review*.json"))
                if "hallucination" not in p.name]
        assert len(vals) == 4, f"{lane_root} {t}: expected 4 judge scores, got {len(vals)}"
        out[t] = mean(vals)
    return out


def perm_test(diffs: list[float]) -> tuple[int, float]:
    """Exact two-sided paired permutation test over all sign assignments."""
    obs = abs(mean(diffs))
    n_ge = sum(1 for signs in itertools.product([1, -1], repeat=len(diffs))
               if abs(mean(s * x for s, x in zip(signs, diffs))) >= obs - 1e-12)
    return n_ge, n_ge / 2 ** len(diffs)


def sign_test(diffs: list[float]) -> tuple[int, int, float]:
    """Two-sided exact sign test after excluding ties."""
    nz = [x for x in diffs if abs(x) > 1e-9]
    n = len(nz)
    k = max(sum(1 for x in nz if x < 0), sum(1 for x in nz if x > 0))
    p = 2 * sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n
    return n, k, min(p, 1.0)


def main() -> int:
    root = find_repo_root()
    base = root / MARKER

    # {label: {metric: {task: judge-averaged mean}}}
    lanes: dict[str, dict[str, dict[str, float]]] = {}
    for label, system, lane in LANES:
        lane_root = base / system / lane
        lanes[label] = {m: task_means(lane_root, m) for m in METRICS}

    labels = [label for label, _, _ in LANES]
    base_label, controls = labels[0], labels[1:]

    emit("Substitution-control statistics computed from the raw judge JSONs")
    emit("=" * 68)
    emit()
    emit("Input: results/evaluations/mlrbench_overall_score/")
    for label, system, lane in LANES:
        emit(f"  {label:28s} {system}/{lane}")
    emit()
    emit(f"{len(TASKS)} tasks x 4 judges per lane; per-task score = mean over the")
    emit("4 judge scores; lane summary = mean +/- sample SD across the")
    emit(f"{len(TASKS)} task-level means. Deltas are computed from unrounded means.")
    emit()

    # ---- [1] lane summaries -------------------------------------------------
    emit("[1] Lane summaries (mean +/- sample SD across tasks)")
    emit()
    w = max(len(l) for l in labels)
    emit(f"{'lane':{w}s}  " + "  ".join(f"{m:>14s}" for m in METRICS))
    for label in labels:
        cells = []
        for m in METRICS:
            vals = list(lanes[label][m].values())
            cells.append(f"{mean(vals):.2f} +/- {stdev(vals):.2f}")
        emit(f"{label:{w}s}  " + "  ".join(c.rjust(14) for c in cells))
    emit()

    # ---- [2] deltas vs baseline ---------------------------------------------
    emit("[2] Deltas vs baseline (control mean - baseline mean, unrounded)")
    emit()
    emit(f"{'control':{w}s}  " + "  ".join(f"{m:>14s}" for m in METRICS))
    for label in controls:
        cells = []
        for m in METRICS:
            d = mean(lanes[label][m].values()) - mean(lanes[base_label][m].values())
            cells.append(f"{d:+.3f}")
        emit(f"{label:{w}s}  " + "  ".join(c.rjust(14) for c in cells))
    emit()

    # ---- [3] per-task Overall -----------------------------------------------
    emit("[3] Per-task judge-averaged Overall")
    emit()
    tw = max(len(t) for t in TASKS)
    emit(f"{'task':{tw}s}  baseline  no-VSA  delta   no-IC  delta")
    for t in TASKS:
        b = lanes[base_label]["Overall"][t]
        v = lanes[controls[0]]["Overall"][t]
        c = lanes[controls[1]]["Overall"][t]
        emit(f"{t:{tw}s}  {b:8.2f}  {v:6.2f}  {v - b:+.2f}  {c:6.2f}  {c - b:+.2f}")
    emit()

    # ---- [4] direction + calibration ----------------------------------------
    emit("[4] Task-level direction and calibration (Overall)")
    for label in controls:
        d = [lanes[label]["Overall"][t] - lanes[base_label]["Overall"][t]
             for t in TASKS]
        lower = sum(1 for x in d if x < -1e-9)
        tied = sum(1 for x in d if abs(x) <= 1e-9)
        higher = sum(1 for x in d if x > 1e-9)
        tied_tasks = sorted(t for t in TASKS
                            if abs(lanes[label]["Overall"][t]
                                   - lanes[base_label]["Overall"][t]) <= 1e-9)
        higher_tasks = sorted(t for t in TASKS
                              if lanes[label]["Overall"][t]
                              - lanes[base_label]["Overall"][t] > 1e-9)
        emit()
        emit(f"  {label}:")
        emit(f"    lower on {lower}/{len(TASKS)}, tied on {tied}/{len(TASKS)}"
             + (f" ({', '.join(tied_tasks)})" if tied_tasks else "")
             + f", higher on {higher}/{len(TASKS)}"
             + (f" ({', '.join(higher_tasks)})" if higher_tasks else ""))
        n_ge, p_perm = perm_test(d)
        emit(f"    exact two-sided paired permutation test: "
             f"{n_ge}/{2 ** len(d)} assignments -> p = {p_perm:.4f}")
        n, k, p_sign = sign_test(d)
        emit(f"    two-sided sign test (ties excluded, {k}/{n} negative): "
             f"p = {p_sign:.4f}")
    emit()

    # ---- [5] Overall range --------------------------------------------------
    emit("[5] Overall task-mean range per lane")
    emit()
    for label in labels:
        vals = lanes[label]["Overall"]
        lo, hi = min(vals, key=vals.get), max(vals, key=vals.get)
        emit(f"  {label:{w}s}  min {vals[lo]:.2f} ({lo})  "
             f"max {vals[hi]:.2f} ({hi})")
    emit()

    out = HERE / (Path(__file__).stem + "_results.txt")
    out.write_text("\n".join(REPORT) + "\n", encoding="utf-8")
    print(f"Report saved to {out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
