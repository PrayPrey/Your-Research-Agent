#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

CATEGORIES = ["Win", "Tie", "Lose"]

COMPARISON_LABELS = {
    "youra_vs_mlragent": "YouRA vs MLR-Agent",
    "youra_vs_aisv2": "YouRA vs AI Scientist V2",
}

WRITER_LABELS = {
    "sonnet45": "Sonnet 4.5",
    "opus45":   "Opus 4.5",
    "sonnet46": "Sonnet 4.6",
}
WRITER_ORDER = ["sonnet45", "opus45", "sonnet46"]

JUDGE_LABELS = {
    "gpt54":       "GPT-5.4",
    "gemini31pro": "Gemini 3.1 Pro",
    "grok43":      "Grok 4.3",
    "opus46":      "Opus 4.6",
}

FILENAME_RE = re.compile(
    r"^LLM_judge_(?P<comparison>[a-z0-9]+_vs_[a-z0-9]+)_"
    r"(?P<writer>[a-z0-9]+)_(?P<judge>[a-z0-9]+)_results\.csv$",
    re.IGNORECASE,
)


def parse_filename(name: str):
    m = FILENAME_RE.match(name)
    if not m:
        return None
    return m.group("comparison").lower(), m.group("writer").lower(), m.group("judge").lower()


def load_verdicts(csv_path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            task = row.get("task", "").strip()
            verdict = row.get("verdict", "").strip()
            if task and verdict in CATEGORIES:
                out[task] = verdict
    return out


def fleiss_kappa(matrix: list[list[int]]) -> tuple[float, float, float]:
    n_items = len(matrix)
    if n_items == 0:
        return 0.0, 0.0, 0.0
    n_raters = sum(matrix[0])
    if n_raters < 2:
        return 0.0, 0.0, 0.0
    n_cats = len(matrix[0])

    p_i = []
    for row in matrix:
        s = sum(r * r for r in row)
        p_i.append((s - n_raters) / (n_raters * (n_raters - 1)))
    p_bar = sum(p_i) / n_items

    col_totals = [0] * n_cats
    for row in matrix:
        for j, v in enumerate(row):
            col_totals[j] += v
    denom = n_items * n_raters
    p_j = [c / denom for c in col_totals]
    p_e = sum(p * p for p in p_j)

    if p_e >= 1.0:
        kappa = 1.0
    else:
        kappa = (p_bar - p_e) / (1.0 - p_e)
    return kappa, p_bar, p_e


def interpret_kappa(k: float) -> str:
    if k < 0:
        return "Poor"
    if k <= 0.20:
        return "Slight"
    if k <= 0.40:
        return "Fair"
    if k <= 0.60:
        return "Moderate"
    if k <= 0.80:
        return "Substantial"
    return "Almost Perfect"


def cohens_kappa(r1: list[str], r2: list[str]) -> float:
    n = len(r1)
    if n == 0:
        return 0.0
    p_o = sum(1 for a, b in zip(r1, r2) if a == b) / n
    p_e = 0.0
    for cat in CATEGORIES:
        f1 = sum(1 for r in r1 if r == cat) / n
        f2 = sum(1 for r in r2 if r == cat) / n
        p_e += f1 * f2
    if p_e >= 1.0:
        return 1.0
    return (p_o - p_e) / (1.0 - p_e)


def build_rating_matrix(per_judge: dict[str, dict[str, str]]) -> tuple[list[str], list[list[int]]]:
    judge_keys = list(per_judge.keys())
    task_sets = [set(per_judge[j].keys()) for j in judge_keys]
    if not task_sets:
        return [], []
    common = sorted(set.intersection(*task_sets))
    matrix = []
    for task in common:
        counts = [0] * len(CATEGORIES)
        for j in judge_keys:
            v = per_judge[j][task]
            counts[CATEGORIES.index(v)] += 1
        matrix.append(counts)
    return common, matrix


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Aggregate LLM-as-Judge verdict CSVs and compute Fleiss' kappa."
    )
    p.add_argument(
        "--input-dir",
        action="append",
        type=Path,
        required=True,
        help="Directory containing LLM_judge_*_results.csv files. "
             "May be passed multiple times to merge MLRagent + AI Scientist v2 dirs.",
    )
    p.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output file. Extension picks format: .json or .csv. "
             "Default: print to stdout only.",
    )
    p.add_argument(
        "--format",
        choices=["json", "csv", "auto"],
        default="auto",
        help="Override output format (auto = infer from --output extension).",
    )
    p.add_argument(
        "--include-cohen",
        action="store_true",
        help="Also include pairwise Cohen's kappa matrix per (comparison, backbone) in JSON output.",
    )
    return p.parse_args()


def collect(input_dirs: list[Path]):
    raw: dict[tuple[str, str], dict[str, dict[str, str]]] = defaultdict(dict)
    for d in input_dirs:
        d = d.resolve()
        if not d.is_dir():
            print(f"[WARN] not a directory: {d}", file=sys.stderr)
            continue
        for csv_path in sorted(d.glob("LLM_judge_*_results.csv")):
            parsed = parse_filename(csv_path.name)
            if not parsed:
                continue
            comparison, writer, judge = parsed
            verdicts = load_verdicts(csv_path)
            if verdicts:
                raw[(comparison, writer)][judge] = verdicts
    return raw


def summarize(raw):
    rows = []
    cohen_blocks = []
    for comparison in sorted(raw.keys() and {c for c, _ in raw.keys()}):
        cmp_label = COMPARISON_LABELS.get(comparison, comparison)
        present_writers = [w for w in WRITER_ORDER if (comparison, w) in raw]
        for w in raw.keys():
            pass
        unknown = sorted(
            {w for (c, w) in raw.keys() if c == comparison} - set(WRITER_ORDER)
        )
        for writer in present_writers + unknown:
            per_judge = raw[(comparison, writer)]
            tasks, matrix = build_rating_matrix(per_judge)
            if not matrix:
                continue
            win = sum(r[0] for r in matrix)
            tie = sum(r[1] for r in matrix)
            lose = sum(r[2] for r in matrix)
            total = win + tie + lose
            kappa, p_bar, p_e = fleiss_kappa(matrix)
            rows.append({
                "comparison": cmp_label,
                "comparison_key": comparison,
                "backbone": WRITER_LABELS.get(writer, writer),
                "backbone_key": writer,
                "n_tasks": len(tasks),
                "n_judges": len(per_judge),
                "judges": [JUDGE_LABELS.get(j, j) for j in per_judge.keys()],
                "win": win,
                "tie": tie,
                "lose": lose,
                "total": total,
                "win_pct": round(win / total * 100, 2) if total else 0.0,
                "fleiss_kappa": round(kappa, 4),
                "observed_agreement": round(p_bar, 4),
                "expected_agreement": round(p_e, 4),
                "interpretation": interpret_kappa(kappa),
            })

            ck = {}
            judge_keys = list(per_judge.keys())
            for i, a in enumerate(judge_keys):
                for b in judge_keys[i + 1:]:
                    ratings_a = [per_judge[a][t] for t in tasks]
                    ratings_b = [per_judge[b][t] for t in tasks]
                    ck[f"{JUDGE_LABELS.get(a, a)} vs {JUDGE_LABELS.get(b, b)}"] = round(
                        cohens_kappa(ratings_a, ratings_b), 4
                    )
            cohen_blocks.append({
                "comparison": cmp_label,
                "backbone": WRITER_LABELS.get(writer, writer),
                "cohens_kappa_pairs": ck,
            })
    return rows, cohen_blocks


def print_table(rows):
    if not rows:
        print("(no rows)")
        return
    header = ["Comparison", "Backbone", "Win", "Tie", "Lose", "Total", "Win%", "Kappa", "Agreement"]
    widths = [len(h) for h in header]
    table = []
    last_cmp = None
    for r in rows:
        cmp_cell = "" if r["comparison"] == last_cmp else r["comparison"]
        last_cmp = r["comparison"]
        cells = [
            cmp_cell, r["backbone"],
            str(r["win"]), str(r["tie"]), str(r["lose"]),
            str(r["total"]), f'{r["win_pct"]:.1f}',
            f'{r["fleiss_kappa"]:.4f}', r["interpretation"],
        ]
        table.append(cells)
        for i, c in enumerate(cells):
            widths[i] = max(widths[i], len(c))

    def fmt(cells):
        return "  ".join(c.ljust(widths[i]) for i, c in enumerate(cells))

    print(fmt(header))
    print("  ".join("-" * w for w in widths))
    for cells in table:
        print(fmt(cells))


def write_output(rows, cohen_blocks, output: Path, fmt: str):
    if fmt == "auto":
        fmt = output.suffix.lower().lstrip(".") or "json"
    output.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "json":
        payload = {"summary": rows}
        if cohen_blocks:
            payload["cohens_kappa"] = cohen_blocks
        with output.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
    elif fmt == "csv":
        cols = [
            "comparison", "backbone", "win", "tie", "lose", "total", "win_pct",
            "fleiss_kappa", "observed_agreement", "expected_agreement",
            "interpretation", "n_tasks", "n_judges",
        ]
        with output.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=cols)
            writer.writeheader()
            for r in rows:
                writer.writerow({k: r.get(k, "") for k in cols})
    else:
        raise SystemExit(f"Unsupported format: {fmt}")
    print(f"Wrote {output}")


def main() -> int:
    args = parse_args()
    raw = collect(args.input_dir)
    if not raw:
        print("No LLM_judge_*_results.csv files matched the expected naming.", file=sys.stderr)
        return 1
    rows, cohen_blocks = summarize(raw)
    print_table(rows)
    if args.output is not None:
        write_output(rows, cohen_blocks if args.include_cohen else [], args.output, args.format)
    return 0


if __name__ == "__main__":
    sys.exit(main())
