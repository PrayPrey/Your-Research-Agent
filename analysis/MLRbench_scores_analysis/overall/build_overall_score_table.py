#!/usr/bin/env python3
"""Build Table 1 MLR-Bench overall-score summaries from raw judge JSON files.

Raw input layout:
  results/evaluations/mlrbench_overall_score/
    <system>/<backbone>/reviews_<judge>_.../<task>/review_<judge>.json

Aggregation:
  1. Average the four judge scores for each system/backbone/task.
  2. Report the mean and sample SD across the 10 tasks.

Outputs:
  table1_mlrbench_overall_scores.csv
  table1_mlrbench_overall_scores.md
  table1_mlrbench_overall_scores.tex
  table1_task_level_scores.csv
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
SYSTEM_ORDER = ["mlragent", "ai_scientist_v2", "youra"]
BACKBONE_ORDER = ["sonnet45", "opus45", "sonnet46"]

SYSTEM_LABELS = {
    "mlragent": "MLR-Agent",
    "ai_scientist_v2": "AI Scientist V2",
    "youra": "YouRA",
}

BACKBONE_LABELS = {
    "sonnet45": "Sonnet 4.5",
    "opus45": "Opus 4.5",
    "sonnet46": "Sonnet 4.6",
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
        description="Create Table 1 MLR-Bench overall-score summaries."
    )
    parser.add_argument(
        "--input-root",
        type=Path,
        help=(
            "Raw input root. Defaults to auto-detected "
            "results/evaluations/mlrbench_overall_score."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=HERE,
        help="Directory where table CSV/Markdown/LaTeX outputs are written.",
    )
    parser.add_argument(
        "--systems",
        nargs="*",
        help="Optional systems to include, e.g. mlragent ai_scientist_v2 youra.",
    )
    parser.add_argument(
        "--backbones",
        nargs="*",
        help="Optional backbones to include, e.g. sonnet45 opus45 sonnet46.",
    )
    return parser.parse_args()


def resolve_input_root(input_root: Path | None) -> Path:
    if input_root:
        root = input_root.expanduser().resolve()
    else:
        root = find_repo_root(HERE) / DEFAULT_RELATIVE_INPUT
    if not root.is_dir():
        raise RuntimeError(f"Input root does not exist or is not a directory: {root}")
    return root


def sort_key(value: str, order: list[str]) -> tuple[int, str]:
    return (order.index(value) if value in order else len(order), value)


def read_score_file(path: Path) -> dict[str, float]:
    with path.open("r", encoding="utf-8") as f:
        data: dict[str, Any] = json.load(f)

    scores: dict[str, float] = {}
    for metric in METRICS:
        metric_data = data.get(metric)
        if not isinstance(metric_data, dict) or "score" not in metric_data:
            raise ValueError(f"{path} is missing {metric}.score")
        scores[metric] = float(metric_data["score"])
    return scores


def discover_scores(
    input_root: Path,
    selected_systems: set[str] | None,
    selected_backbones: set[str] | None,
) -> dict[tuple[str, str, str], list[dict[str, float]]]:
    grouped: dict[tuple[str, str, str], list[dict[str, float]]] = defaultdict(list)

    for path in sorted(input_root.rglob("review*.json")):
        rel = path.relative_to(input_root)
        if len(rel.parts) < 5:
            continue
        system, backbone = rel.parts[0], rel.parts[1]
        task = path.parent.name
        if selected_systems and system not in selected_systems:
            continue
        if selected_backbones and backbone not in selected_backbones:
            continue
        grouped[(system, backbone, task)].append(read_score_file(path))

    if not grouped:
        raise FileNotFoundError(f"No review*.json score files found under {input_root}")
    return dict(grouped)


def mean(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def sample_sd(values: list[float]) -> float:
    return statistics.stdev(values) if len(values) >= 2 else 0.0


def build_task_rows(
    grouped: dict[tuple[str, str, str], list[dict[str, float]]]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for (system, backbone, task), judge_scores in sorted(
        grouped.items(),
        key=lambda item: (
            sort_key(item[0][0], SYSTEM_ORDER),
            sort_key(item[0][1], BACKBONE_ORDER),
            item[0][2],
        ),
    ):
        row: dict[str, Any] = {
            "system": SYSTEM_LABELS.get(system, system),
            "system_key": system,
            "backbone": BACKBONE_LABELS.get(backbone, backbone),
            "backbone_key": backbone,
            "task": task,
            "n_judges": len(judge_scores),
        }
        for metric in METRICS:
            row[f"{metric.lower()}_task_mean"] = mean([scores[metric] for scores in judge_scores])
        rows.append(row)
    return rows


def build_summary_rows(task_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows_by_system_backbone: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in task_rows:
        rows_by_system_backbone[(row["system_key"], row["backbone_key"])].append(row)

    summary_rows: list[dict[str, Any]] = []
    for system, backbone in sorted(
        rows_by_system_backbone,
        key=lambda key: (sort_key(key[0], SYSTEM_ORDER), sort_key(key[1], BACKBONE_ORDER)),
    ):
        group = sorted(rows_by_system_backbone[(system, backbone)], key=lambda row: row["task"])
        summary: dict[str, Any] = {
            "system": SYSTEM_LABELS.get(system, system),
            "system_key": system,
            "backbone": BACKBONE_LABELS.get(backbone, backbone),
            "backbone_key": backbone,
            "n_tasks": len(group),
            "min_judges_per_task": min(int(row["n_judges"]) for row in group),
            "max_judges_per_task": max(int(row["n_judges"]) for row in group),
        }
        for metric in METRICS:
            task_values = [float(row[f"{metric.lower()}_task_mean"]) for row in group]
            summary[f"{metric.lower()}_mean"] = mean(task_values)
            summary[f"{metric.lower()}_sd"] = sample_sd(task_values)
        summary_rows.append(summary)
    return summary_rows


def write_task_csv(path: Path, task_rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "system",
        "backbone",
        "task",
        "n_judges",
        "clarity_task_mean",
        "novelty_task_mean",
        "soundness_task_mean",
        "significance_task_mean",
        "overall_task_mean",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in task_rows:
            writer.writerow({field: row[field] for field in fieldnames})


def write_summary_csv(path: Path, summary_rows: list[dict[str, Any]]) -> None:
    fieldnames = ["system", "backbone", "n_tasks", "min_judges_per_task", "max_judges_per_task"]
    for metric in METRICS:
        slug = metric.lower()
        fieldnames.extend([f"{slug}_mean", f"{slug}_sd"])

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in summary_rows:
            writer.writerow({field: row[field] for field in fieldnames})


def best_means_by_backbone(summary_rows: list[dict[str, Any]]) -> dict[tuple[str, str], float]:
    best: dict[tuple[str, str], float] = {}
    for backbone in {row["backbone_key"] for row in summary_rows}:
        rows = [row for row in summary_rows if row["backbone_key"] == backbone]
        for metric in METRICS:
            best[(backbone, metric)] = max(float(row[f"{metric.lower()}_mean"]) for row in rows)
    return best


def formatted_cell(row: dict[str, Any], metric: str, best: dict[tuple[str, str], float], markdown: bool) -> str:
    slug = metric.lower()
    mean_value = float(row[f"{slug}_mean"])
    sd_value = float(row[f"{slug}_sd"])
    value = f"{mean_value:.2f} +/- {sd_value:.2f}" if markdown else f"{mean_value:.2f} $\\pm$ {sd_value:.2f}"
    if abs(mean_value - best[(row["backbone_key"], metric)]) < 1e-12:
        return f"**{value}**" if markdown else f"\\textbf{{{value}}}"
    return value


def write_markdown(path: Path, summary_rows: list[dict[str, Any]]) -> None:
    best = best_means_by_backbone(summary_rows)
    lines = [
        "| System | Backbone LLM | Clarity | Novelty | Soundness | Significance | Overall |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        cells = [
            row["system"],
            row["backbone"],
            *[formatted_cell(row, metric, best, markdown=True) for metric in METRICS],
        ]
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")
    lines.append(
        "Table 1: MLR-Bench end-to-end scores (10 tasks; 1-10, higher is better). "
        "Each cell reports mean +/- task SD of scores averaged over four judges; "
        "bold marks the best mean score per matched-backbone block."
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_latex(path: Path, summary_rows: list[dict[str, Any]]) -> None:
    best = best_means_by_backbone(summary_rows)
    lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\small",
        "\\begin{tabular}{llccccc}",
        "\\toprule",
        "System & Backbone LLM & Clarity & Novelty & Soundness & Significance & Overall \\\\",
        "\\midrule",
    ]
    previous_system = None
    for row in summary_rows:
        if previous_system is not None and previous_system != row["system"]:
            lines.append("\\midrule")
        previous_system = row["system"]
        cells = [
            row["system"],
            row["backbone"],
            *[formatted_cell(row, metric, best, markdown=False) for metric in METRICS],
        ]
        lines.append(" & ".join(cells) + " \\\\")
    lines.extend(
        [
            "\\bottomrule",
            "\\end{tabular}",
            "\\caption{MLR-Bench end-to-end scores (10 tasks; 1--10, higher is better). "
            "Each cell reports mean $\\pm$ task SD of scores averaged over four judges; "
            "bold marks the best mean score per matched-backbone block.}",
            "\\end{table}",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    input_root = resolve_input_root(args.input_root)
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    grouped = discover_scores(
        input_root=input_root,
        selected_systems=set(args.systems) if args.systems else None,
        selected_backbones=set(args.backbones) if args.backbones else None,
    )
    task_rows = build_task_rows(grouped)
    summary_rows = build_summary_rows(task_rows)

    summary_csv = output_dir / "table1_mlrbench_overall_scores.csv"
    task_csv = output_dir / "table1_task_level_scores.csv"
    markdown_path = output_dir / "table1_mlrbench_overall_scores.md"
    latex_path = output_dir / "table1_mlrbench_overall_scores.tex"

    write_summary_csv(summary_csv, summary_rows)
    write_task_csv(task_csv, task_rows)
    write_markdown(markdown_path, summary_rows)
    write_latex(latex_path, summary_rows)

    print(f"Wrote {summary_csv}")
    print(f"Wrote {task_csv}")
    print(f"Wrote {markdown_path}")
    print(f"Wrote {latex_path}")


if __name__ == "__main__":
    main()
