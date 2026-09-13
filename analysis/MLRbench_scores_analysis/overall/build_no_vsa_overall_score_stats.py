#!/usr/bin/env python3
"""Overall-score statistics for the YouRA sonnet45_no_VSA ablation lane.

Raw input layout (same as build_overall_score_table.py):
  results/evaluations/mlrbench_overall_score/
    <system>/<lane>/reviews_<judge>_.../<task>/review_<judge>.json

Ablation lanes (e.g. sonnet45_no_VSA) live under system folder
`youra_ablation_study`; baselines (e.g. sonnet45) under `youra`. Lanes are
looked up in both, in that order.

Statistics reported per metric (Clarity/Novelty/Soundness/Significance/Overall):
  * task-level: raw score per (task, judge) plus the judge-averaged task mean
  * lane summary: mean +/- sample SD across tasks of the judge-averaged means
    (identical aggregation to Table 1)
  * judge summary: per-judge mean +/- SD across tasks (judge strictness check)

With --with-baseline, the matching rows for the `sonnet45` lane (the with-VSA
baseline) and the no_VSA - baseline delta are added for ablation comparison.

Outputs (written next to this script):
  no_vsa_task_level_scores.csv
  no_vsa_overall_score_stats.csv
  no_vsa_overall_score_stats.md
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
DEFAULT_RELATIVE_INPUT = Path("results") / "evaluations" / "mlrbench_overall_score"

METRICS = ["Clarity", "Novelty", "Soundness", "Significance", "Overall"]
SYSTEM_DIRS = ["youra_ablation_study", "youra"]
LANE = "sonnet45_no_VSA"
BASELINE_LANE = "sonnet45"

LANE_LABELS = {
    "sonnet45_no_VSA": "Sonnet 4.5 (no VSA)",
    "sonnet45": "Sonnet 4.5 (baseline)",
}


def find_repo_root(start: Path) -> Path:
    cur = start.resolve()
    while True:
        if (cur / DEFAULT_RELATIVE_INPUT).is_dir():
            return cur
        if cur.parent == cur:
            raise RuntimeError(
                f"Could not locate {DEFAULT_RELATIVE_INPUT} walking up from {start}."
            )
        cur = cur.parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Overall-score statistics for the sonnet45_no_VSA lane."
    )
    parser.add_argument("--input-root", type=Path,
                        help="Raw input root (default: auto-detected "
                             "results/evaluations/mlrbench_overall_score).")
    parser.add_argument("--output-dir", type=Path, default=HERE,
                        help="Directory for the CSV/Markdown outputs.")
    parser.add_argument("--lane", default=LANE,
                        help=f"Lane (backbone folder) to analyse (default: {LANE}).")
    parser.add_argument("--baseline-lane", default=None,
                        help="Baseline lane for --with-baseline. Default: "
                             "sonnet46 for sonnet46_* lanes, else sonnet45.")
    parser.add_argument("--with-baseline", action="store_true",
                        help="Also report the baseline lane and the delta.")
    return parser.parse_args()


def read_score_file(path: Path) -> dict[str, float]:
    with path.open("r", encoding="utf-8") as f:
        data: dict[str, Any] = json.load(f)
    scores: dict[str, float] = {}
    for metric in METRICS:
        metric_data = data.get(metric)
        if isinstance(metric_data, dict) and "score" in metric_data:
            scores[metric] = float(metric_data["score"])
        elif isinstance(metric_data, (int, float)):
            scores[metric] = float(metric_data)
        else:
            raise ValueError(f"{path} is missing {metric}.score")
    return scores


def judge_from_filename(path: Path) -> str:
    # review_<judge>.json -> <judge>
    return path.stem[len("review_"):]


def load_lane(input_root: Path, lane: str) -> dict[str, dict[str, dict[str, float]]]:
    """Return {task: {judge: {metric: score}}} for one lane."""
    lane_root = next(
        (input_root / sys_dir / lane for sys_dir in SYSTEM_DIRS
         if (input_root / sys_dir / lane).is_dir()),
        None,
    )
    if lane_root is None:
        raise FileNotFoundError(
            f"Lane '{lane}' not found under any of "
            f"{[str(input_root / s) for s in SYSTEM_DIRS]}")
    scores: dict[str, dict[str, dict[str, float]]] = defaultdict(dict)
    for path in sorted(lane_root.rglob("review_*.json")):
        if "hallucination" in path.name:
            continue
        task = path.parent.name
        scores[task][judge_from_filename(path)] = read_score_file(path)
    if not scores:
        raise FileNotFoundError(f"No review_*.json files under {lane_root}")
    return dict(scores)


def mean(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def sample_sd(values: list[float]) -> float:
    return statistics.stdev(values) if len(values) >= 2 else 0.0


def task_means(lane_scores: dict[str, dict[str, dict[str, float]]],
               metric: str) -> dict[str, float]:
    """Judge-averaged score per task for one metric."""
    return {task: mean([js[metric] for js in judges.values()])
            for task, judges in lane_scores.items()}


def write_task_csv(path: Path, lane: str,
                   lane_scores: dict[str, dict[str, dict[str, float]]]) -> None:
    fieldnames = ["lane", "task", "judge"] + [m.lower() for m in METRICS]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for task in sorted(lane_scores):
            for judge in sorted(lane_scores[task]):
                row = {"lane": lane, "task": task, "judge": judge}
                row.update({m.lower(): lane_scores[task][judge][m] for m in METRICS})
                writer.writerow(row)
            writer.writerow({
                "lane": lane, "task": task, "judge": "MEAN(judges)",
                **{m.lower(): round(mean([js[m] for js in lane_scores[task].values()]), 3)
                   for m in METRICS},
            })


def lane_summary(lane_scores: dict[str, dict[str, dict[str, float]]]) -> dict[str, tuple[float, float]]:
    """{metric: (mean across tasks, SD across tasks)} of judge-averaged means."""
    out = {}
    for metric in METRICS:
        values = list(task_means(lane_scores, metric).values())
        out[metric] = (mean(values), sample_sd(values))
    return out


def judge_summary(lane_scores: dict[str, dict[str, dict[str, float]]]) -> dict[str, dict[str, tuple[float, float]]]:
    """{judge: {metric: (mean across tasks, SD across tasks)}}."""
    judges = sorted({j for judges in lane_scores.values() for j in judges})
    out: dict[str, dict[str, tuple[float, float]]] = {}
    for judge in judges:
        out[judge] = {}
        for metric in METRICS:
            values = [judges_scores[judge][metric]
                      for judges_scores in lane_scores.values()
                      if judge in judges_scores]
            out[judge][metric] = (mean(values), sample_sd(values))
    return out


def fmt(ms: tuple[float, float]) -> str:
    return f"{ms[0]:.2f} +/- {ms[1]:.2f}"


def main() -> None:
    args = parse_args()
    if args.input_root:
        input_root = args.input_root.expanduser().resolve()
    else:
        input_root = find_repo_root(HERE) / DEFAULT_RELATIVE_INPUT
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    lane_scores = load_lane(input_root, args.lane)
    n_tasks = len(lane_scores)
    summary = lane_summary(lane_scores)
    per_judge = judge_summary(lane_scores)

    baseline_lane = args.baseline_lane or (
        "sonnet46" if args.lane.startswith("sonnet46") else BASELINE_LANE)
    baseline_summary = None
    baseline_n = 0
    if args.with_baseline:
        baseline_scores = load_lane(input_root, baseline_lane)
        # Restrict the baseline to the tasks the ablation lane actually has
        # (e.g. no mldpr in no_VSA) so the delta compares matched task sets.
        baseline_scores = {t: v for t, v in baseline_scores.items()
                           if t in lane_scores}
        baseline_n = len(baseline_scores)
        baseline_summary = lane_summary(baseline_scores)

    # Output filenames: keep the historical no_vsa_* names for the default
    # lane; derive from the lane name otherwise so lanes don't clobber
    # each other's outputs.
    stem = "no_vsa" if args.lane == LANE else args.lane.lower()

    # ---- CSV: task x judge raw scores -------------------------------------
    task_csv = output_dir / f"{stem}_task_level_scores.csv"
    write_task_csv(task_csv, args.lane, lane_scores)

    # ---- CSV: summary stats ------------------------------------------------
    stats_csv = output_dir / f"{stem}_overall_score_stats.csv"
    with stats_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["row_type", "lane", "judge", "n_tasks"]
                        + [f"{m.lower()}_{s}" for m in METRICS for s in ("mean", "sd")])
        writer.writerow(["lane_summary", args.lane, "ALL(4-judge mean)", n_tasks]
                        + [round(v, 4) for m in METRICS for v in summary[m]])
        for judge, ms in per_judge.items():
            writer.writerow(["judge_summary", args.lane, judge, n_tasks]
                            + [round(v, 4) for m in METRICS for v in ms[m]])
        if baseline_summary:
            writer.writerow(["lane_summary", baseline_lane, "ALL(4-judge mean)", ""]
                            + [round(v, 4) for m in METRICS for v in baseline_summary[m]])
            writer.writerow(["delta_vs_baseline", args.lane, "", ""]
                            + [round(summary[m][0] - baseline_summary[m][0], 4)
                               if s == "mean" else ""
                               for m in METRICS for s in ("mean", "sd")])

    # ---- Markdown + console ------------------------------------------------
    lines = [
        f"# Overall-score statistics: {LANE_LABELS.get(args.lane, args.lane)}",
        "",
        f"{n_tasks} tasks; each task averaged over {min(len(j) for j in lane_scores.values())}"
        f"-{max(len(j) for j in lane_scores.values())} judges; "
        "cells are mean +/- sample SD across tasks (1-10, higher is better).",
        "",
        "| Lane | Clarity | Novelty | Soundness | Significance | Overall |",
        "|---|---:|---:|---:|---:|---:|",
        "| " + " | ".join([LANE_LABELS.get(args.lane, args.lane)]
                          + [fmt(summary[m]) for m in METRICS]) + " |",
    ]
    if baseline_summary:
        lines.append("| " + " | ".join([LANE_LABELS.get(baseline_lane, baseline_lane)]
                                       + [fmt(baseline_summary[m]) for m in METRICS]) + " |")
        lines.append("| " + " | ".join(
            [f"delta ({args.lane} - {baseline_lane})"]
            + [f"{summary[m][0] - baseline_summary[m][0]:+.2f}" for m in METRICS]) + " |")
        lines.append("")
        lines.append(f"Baseline restricted to the {baseline_n} tasks shared "
                     "with the ablation lane (matched task sets).")
    lines += [
        "",
        "## Per-judge means (judge strictness)",
        "",
        "| Judge | Clarity | Novelty | Soundness | Significance | Overall |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for judge, ms in per_judge.items():
        lines.append("| " + " | ".join([judge] + [fmt(ms[m]) for m in METRICS]) + " |")
    lines += [
        "",
        "## Per-task judge-averaged Overall",
        "",
        "| Task | " + " | ".join(sorted(next(iter(lane_scores.values())))) + " | mean |",
        "|---|" + "---:|" * (len(per_judge) + 1),
    ]
    for task in sorted(lane_scores):
        judges = lane_scores[task]
        cells = [f"{judges[j]['Overall']:.0f}" if j in judges else "-"
                 for j in sorted(per_judge)]
        cells.append(f"{mean([js['Overall'] for js in judges.values()]):.2f}")
        lines.append("| " + " | ".join([task] + cells) + " |")

    md_path = output_dir / f"{stem}_overall_score_stats.md"
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\n".join(lines))
    print(f"\nWrote {task_csv}")
    print(f"Wrote {stats_csv}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
