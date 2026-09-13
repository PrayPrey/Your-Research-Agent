#!/usr/bin/env python3
"""Extract hallucination-analysis CSVs from raw MLRBench judge JSON outputs.

Raw input layout:
  results/evaluations/mlrbench_hallucination/
    <method>/<model>/reviews_<judge>_.../<venue>/review_hallucination_<judge>.json

Generated output layout:
  <output-dir>/<Method>/<model>/
    hallucination_reviews_summary.csv
    hallucination_findings_individual.csv
    hallucination_findings_matrix.csv
    hallucination_findings_matrix_with_totals.csv
    hallucination_flag_matrix.csv
    per_type_prevalence_<model>.csv

The plot scripts consume the per_type_prevalence_<model>.csv files.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
DEFAULT_RELATIVE_INPUT = Path("results") / "evaluations" / "mlrbench_hallucination"

METHOD_LABELS = {
    "youra": "YouRA",
    "mlragent": "MLRbench",
    "ai_scientist_v2": "AI_Scientist_V2",
    "YouRA": "YouRA",
    "MLRbench": "MLRbench",
    "AI_Scientist_V2": "AI_Scientist_V2",
}

METHOD_ORDER = ["YouRA", "MLRbench", "AI_Scientist_V2"]
MODEL_ORDER = ["sonnet45", "opus45", "sonnet46"]
JUDGE_ORDER = ["claude-opus-4.6", "gemini-3.1-pro-preview", "gpt-5.4", "grok-4.3"]
TYPE_ORDER = [
    "Nonexistent Citations",
    "Hallucinated Methodology",
    "Mathematical Errors",
    "Faked Experimental Results",
]


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
        description="Build hallucination-analysis CSVs from raw MLRBench judge JSON files."
    )
    parser.add_argument(
        "--input-root",
        type=Path,
        help=(
            "Raw input root. Defaults to auto-detected "
            "results/evaluations/mlrbench_hallucination."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=HERE,
        help="Directory where method/model CSV folders are written.",
    )
    parser.add_argument(
        "--methods",
        nargs="*",
        help="Optional raw or output method names to include, e.g. youra mlragent ai_scientist_v2.",
    )
    parser.add_argument(
        "--models",
        nargs="*",
        help="Optional model names to include, e.g. sonnet45 opus45 sonnet46.",
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


def normalize_method(raw_method: str) -> str:
    return METHOD_LABELS.get(raw_method, raw_method)


def normalize_type(value: str) -> str:
    value = (value or "").strip()
    lowered = value.lower()
    for known in TYPE_ORDER:
        if lowered == known.lower():
            return known
    return value


def judge_from_path(path: Path, review_dir: str, raw_method: str, model: str) -> str:
    stem = path.stem
    prefix = "review_hallucination_"
    if stem.startswith(prefix):
        return stem[len(prefix):]
    review_prefix = "reviews_"
    review_suffix = f"_{raw_method}_{model}"
    if review_dir.startswith(review_prefix) and review_suffix in review_dir:
        return review_dir[len(review_prefix):review_dir.index(review_suffix)]
    return stem


def sort_key(value: str, order: list[str]) -> tuple[int, str]:
    return (order.index(value) if value in order else len(order), value)


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def discover_records(
    input_root: Path,
    selected_methods: set[str] | None,
    selected_models: set[str] | None,
) -> dict[tuple[str, str], list[dict[str, Any]]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)

    for path in sorted(input_root.rglob("review_hallucination*.json")):
        rel = path.relative_to(input_root)
        if len(rel.parts) < 5:
            continue

        raw_method, model = rel.parts[0], rel.parts[1]
        method = normalize_method(raw_method)
        if selected_methods and raw_method not in selected_methods and method not in selected_methods:
            continue
        if selected_models and model not in selected_models:
            continue

        review_dir = rel.parts[2]
        venue = path.parent.name
        judge = judge_from_path(path, review_dir, raw_method, model)
        data = read_json(path)
        hallucinations = data.get("hallucinations") or []

        grouped[(method, model)].append(
            {
                "method": method,
                "model": model,
                "venue": venue,
                "judge": judge,
                "path": path,
                "has_hallucination": bool(data.get("has_hallucination")),
                "hallucinations": hallucinations,
                "overall_assessment": data.get("overall_assessment", ""),
                "confidence": data.get("confidence", ""),
            }
        )

    if not grouped:
        raise FileNotFoundError(f"No review_hallucination_*.json files found under {input_root}")
    return dict(grouped)


def write_dict_rows(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_matrix(
    path: Path,
    first_column: str,
    row_names: list[str],
    column_names: list[str],
    values: dict[tuple[str, str], int],
    include_totals: bool,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [first_column] + column_names + (["TOTAL"] if include_totals else [])
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(fields)
        column_totals = {col: 0 for col in column_names}
        for row_name in row_names:
            row_values = [values.get((row_name, col), 0) for col in column_names]
            for col, value in zip(column_names, row_values):
                column_totals[col] += value
            writer.writerow(
                [row_name] + row_values + ([sum(row_values)] if include_totals else [])
            )
        if include_totals:
            total_values = [column_totals[col] for col in column_names]
            writer.writerow(["TOTAL"] + total_values + [sum(total_values)])


def build_group_outputs(records: list[dict[str, Any]], output_dir: Path, method: str, model: str) -> list[Path]:
    out_dir = output_dir / method / model
    judges = sorted({r["judge"] for r in records}, key=lambda name: sort_key(name, JUDGE_ORDER))
    venues = sorted({r["venue"] for r in records})

    records_by_venue_judge = {(r["venue"], r["judge"]): r for r in records}

    summary_rows = []
    individual_rows = []
    count_values: dict[tuple[str, str], int] = {}
    flag_values: dict[tuple[str, str], int] = {}
    type_flags: dict[str, dict[str, set[str]]] = {
        hallucination_type: {venue: set() for venue in venues} for hallucination_type in TYPE_ORDER
    }

    for venue in venues:
        for judge in judges:
            record = records_by_venue_judge.get((venue, judge))
            hallucinations = record["hallucinations"] if record else []
            count_values[(venue, judge)] = len(hallucinations)
            flag_values[(venue, judge)] = 1 if record and record["has_hallucination"] else 0

            if record:
                summary_rows.append(
                    {
                        "judge": judge,
                        "venue": venue,
                        "has_hallucination": record["has_hallucination"],
                        "n_hallucinations": len(hallucinations),
                        "confidence": record["confidence"],
                        "overall_assessment": record["overall_assessment"],
                    }
                )

            for hallucination in hallucinations:
                type_norm = normalize_type(str(hallucination.get("type", "")))
                individual_rows.append(
                    {
                        "judge": judge,
                        "venue": venue,
                        "type": hallucination.get("type", ""),
                        "description": hallucination.get("description", ""),
                        "evidence": hallucination.get("evidence", ""),
                        "type_norm": type_norm,
                    }
                )
                type_flags.setdefault(type_norm, {v: set() for v in venues})
                type_flags[type_norm].setdefault(venue, set()).add(judge)

    written: list[Path] = []

    summary_path = out_dir / "hallucination_reviews_summary.csv"
    write_dict_rows(
        summary_path,
        ["judge", "venue", "has_hallucination", "n_hallucinations", "confidence", "overall_assessment"],
        sorted(summary_rows, key=lambda r: (sort_key(r["judge"], JUDGE_ORDER), r["venue"])),
    )
    written.append(summary_path)

    individual_path = out_dir / "hallucination_findings_individual.csv"
    write_dict_rows(
        individual_path,
        ["judge", "venue", "type", "description", "evidence", "type_norm"],
        sorted(individual_rows, key=lambda r: (sort_key(r["judge"], JUDGE_ORDER), r["venue"], r["type_norm"])),
    )
    written.append(individual_path)

    matrix_path = out_dir / "hallucination_findings_matrix.csv"
    write_matrix(matrix_path, "task", venues, judges, count_values, include_totals=False)
    written.append(matrix_path)

    matrix_totals_path = out_dir / "hallucination_findings_matrix_with_totals.csv"
    write_matrix(matrix_totals_path, "task", venues, judges, count_values, include_totals=True)
    written.append(matrix_totals_path)

    flag_path = out_dir / "hallucination_flag_matrix.csv"
    flag_matrix_values = dict(flag_values)
    write_matrix(flag_path, "venue", venues, judges, flag_matrix_values, include_totals=False)
    written.append(flag_path)

    prevalence_rows = []
    denominator = len(venues)
    for hallucination_type in TYPE_ORDER:
        venue_flags = type_flags.get(hallucination_type, {})
        union_n = sum(1 for venue in venues if venue_flags.get(venue))
        inter_n = sum(1 for venue in venues if set(judges).issubset(venue_flags.get(venue, set())))
        prevalence_rows.append(
            {
                "type": hallucination_type,
                "union_n": union_n,
                "union_pct": round(union_n / denominator * 100, 1) if denominator else 0.0,
                "inter_n": inter_n,
                "inter_pct": round(inter_n / denominator * 100, 1) if denominator else 0.0,
            }
        )

    prevalence_path = out_dir / f"per_type_prevalence_{model}.csv"
    write_dict_rows(
        prevalence_path,
        ["type", "union_n", "union_pct", "inter_n", "inter_pct"],
        prevalence_rows,
    )
    written.append(prevalence_path)

    return written


def main() -> None:
    args = parse_args()
    input_root = resolve_input_root(args.input_root)
    output_dir = args.output_dir.expanduser().resolve()
    selected_methods = set(args.methods) if args.methods else None
    selected_models = set(args.models) if args.models else None

    grouped = discover_records(input_root, selected_methods, selected_models)
    all_written: list[Path] = []
    for method, model in sorted(
        grouped,
        key=lambda key: (sort_key(key[0], METHOD_ORDER), sort_key(key[1], MODEL_ORDER)),
    ):
        written = build_group_outputs(grouped[(method, model)], output_dir, method, model)
        all_written.extend(written)
        print(f"{method}/{model}: {len(grouped[(method, model)])} reviews -> {len(written)} CSVs")

    print(f"Wrote {len(all_written)} CSV files under {output_dir}")


if __name__ == "__main__":
    main()
