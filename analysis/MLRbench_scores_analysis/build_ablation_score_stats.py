#!/usr/bin/env python3
"""Per-lane score statistics for the YouRA ablation study (CSV only).

Reads every judge review under

    results/evaluations/mlrbench_overall_score/youra_ablation_study/
        <lane>/reviews_<judge>_*/iclr2025_<task>/review_<judge>.json

and writes, next to this script, under ``ablation_score_stats/``:

    <lane>_task_level_scores.csv
        one row per (task, judge) with the five rubric scores, plus a
        MEAN(judges) row per task
    youra_ablation_study_summary.csv
        one row per lane: mean and sample SD for each metric

Aggregation matches Table 1 of the paper: scores are first averaged over
the judges within each task, then the mean and sample standard deviation
are taken across tasks.

The repository root is located by walking up from this file, so the script
works from a fresh clone regardless of the current working directory:

    python analysis/MLRbench_scores_analysis/build_ablation_score_stats.py

Pure standard library (Python >= 3.10); no third-party dependencies.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
ABLATION_RELPATH = (
    Path("results") / "evaluations" / "mlrbench_overall_score" / "youra_ablation_study"
)
METRICS = ["Clarity", "Novelty", "Soundness", "Significance", "Overall"]
OUTPUT_DIRNAME = "ablation_score_stats"


def find_repo_root(start: Path) -> Path:
    cur = start
    while True:
        if (cur / ABLATION_RELPATH).is_dir():
            return cur
        if cur.parent == cur:
            raise RuntimeError(
                f"Could not locate {ABLATION_RELPATH} walking up from {start}. "
                "Run this script from inside a clone of the YouRA repository."
            )
        cur = cur.parent


def read_scores(path: Path) -> dict[str, float]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    scores: dict[str, float] = {}
    for metric in METRICS:
        value = data.get(metric)
        if isinstance(value, dict) and "score" in value:
            scores[metric] = float(value["score"])
        elif isinstance(value, (int, float)):
            scores[metric] = float(value)
        else:
            raise ValueError(f"{path} is missing {metric}.score")
    return scores


def load_lane(lane_dir: Path) -> dict[str, dict[str, dict[str, float]]]:
    """Return {task: {judge: {metric: score}}} for one lane folder."""
    lane: dict[str, dict[str, dict[str, float]]] = {}
    for path in sorted(lane_dir.rglob("review_*.json")):
        if "hallucination" in path.name:
            continue
        judge = path.stem[len("review_"):]
        task = path.parent.name
        lane.setdefault(task, {})[judge] = read_scores(path)
    return lane


def mean(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def sample_sd(values: list[float]) -> float:
    return statistics.stdev(values) if len(values) >= 2 else 0.0


def write_task_csv(path: Path, lane_name: str,
                   lane: dict[str, dict[str, dict[str, float]]]) -> None:
    fieldnames = ["lane", "task", "judge"] + [m.lower() for m in METRICS]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for task in sorted(lane):
            for judge in sorted(lane[task]):
                row = {"lane": lane_name, "task": task, "judge": judge}
                row.update({m.lower(): lane[task][judge][m] for m in METRICS})
                writer.writerow(row)
            writer.writerow({
                "lane": lane_name, "task": task, "judge": "MEAN(judges)",
                **{m.lower(): round(mean([s[m] for s in lane[task].values()]), 4)
                   for m in METRICS},
            })


def lane_summary(lane: dict[str, dict[str, dict[str, float]]]) -> dict[str, tuple[float, float]]:
    """{metric: (mean across tasks, sample SD across tasks)} of judge-averaged means."""
    out: dict[str, tuple[float, float]] = {}
    for metric in METRICS:
        task_means = [mean([s[metric] for s in judges.values()])
                      for judges in lane.values()]
        out[metric] = (mean(task_means), sample_sd(task_means))
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--output-dir", type=Path, default=HERE / OUTPUT_DIRNAME,
                        help="Where to write the CSVs (default: "
                             f"{OUTPUT_DIRNAME}/ next to this script).")
    args = parser.parse_args()

    repo_root = find_repo_root(HERE)
    ablation_root = repo_root / ABLATION_RELPATH
    lanes = sorted(p.name for p in ablation_root.iterdir() if p.is_dir())
    if not lanes:
        raise RuntimeError(f"No lane folders found under {ABLATION_RELPATH}")

    out_dir = args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    summary_rows: list[dict[str, object]] = []
    for lane_name in lanes:
        lane = load_lane(ablation_root / lane_name)
        if not lane:
            print(f"[WARN] {lane_name}: no review_*.json found, skipping")
            continue
        write_task_csv(out_dir / f"{lane_name}_task_level_scores.csv",
                       lane_name, lane)
        stats = lane_summary(lane)
        n_reviews = sum(len(j) for j in lane.values())
        row: dict[str, object] = {
            "lane": lane_name,
            "n_tasks": len(lane),
            "n_reviews": n_reviews,
        }
        for metric in METRICS:
            m, sd = stats[metric]
            row[f"{metric.lower()}_mean"] = round(m, 4)
            row[f"{metric.lower()}_sd"] = round(sd, 4)
        summary_rows.append(row)

    summary_path = out_dir / "youra_ablation_study_summary.csv"
    fieldnames = ["lane", "n_tasks", "n_reviews"] + [
        f"{m.lower()}_{s}" for m in METRICS for s in ("mean", "sd")
    ]
    with summary_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)

    width = max(len(r["lane"]) for r in summary_rows)
    print(f"{'lane':{width}s}  " + "  ".join(f"{m:>13s}" for m in METRICS))
    for r in summary_rows:
        cells = [f"{r[f'{m.lower()}_mean']:.2f} +/- {r[f'{m.lower()}_sd']:.2f}"
                 for m in METRICS]
        print(f"{r['lane']:{width}s}  " + "  ".join(f"{c:>13s}" for c in cells))
    try:  # print repo-relative so notebook outputs never embed local paths
        out_label = str(out_dir.relative_to(repo_root))
    except ValueError:
        out_label = out_dir.name
    print(f"\nWrote {len(summary_rows)} task-level CSV(s) and "
          f"{summary_path.name} to {out_label}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
