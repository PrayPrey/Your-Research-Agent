#!/usr/bin/env python3
"""Cumulative dismantling ladder + VSA x IC interaction for the ablation study.

Ladder (components removed cumulatively):
    full -> no_VSA_no_IC -> no_VSA_no_IC_no_mcp -> no_VSA_no_IC_no_mcp_no_reflection

Reads judge reviews from
    results/evaluations/mlrbench_overall_score/youra/<bb>/...            (full)
    results/evaluations/mlrbench_overall_score/youra_ablation_study/<lane>/...

Unit of analysis: the matched (backbone, task) cell; each cell is the mean of
the four judges' Overall scores (same convention as the paper). Paired
two-sided sign-flip permutation tests, 100k assignments, fixed seed.

VSA x IC interaction per cell:
    I = [Y(full) - Y(no_VSA)] - [Y(no_IC) - Y(no_VSA_no_IC)]
Positive I = super-additive (synergy); negative = sub-additive (redundancy).

Pure standard library. Writes dismantling_ladder_stats_results.txt next to
this script and prints the same text.
"""
from __future__ import annotations

import json
import random
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent  # repo root (analysis/MLRbench_scores_analysis/..)
EVAL = ROOT / "results" / "evaluations" / "mlrbench_overall_score"
BACKBONES = ["opus45", "sonnet45", "sonnet46"]
TASKS = ["bi_align", "buildingtrust", "data_problems", "dl4c", "mldpr",
         "question", "scope", "scsl", "verifai", "wsl"]
LADDER = [  # (label, lane dir under youra_ablation_study; None = full config)
    ("full", None),
    ("no_VSA_no_IC", "{bb}_no_VSA_no_IC"),
    ("no_VSA_no_IC_no_mcp", "{bb}_no_VSA_no_IC_no_mcp"),
    ("no_VSA_no_IC_no_mcp_no_reflection", "{bb}_no_VSA_no_IC_no_mcp_no_reflection"),
]
SINGLES = ["no_VSA", "no_IC", "no_mcp", "no_reflection"]
B = 100_000
SEED = 20260831


def cell_overall(lane_dir: Path, task: str) -> float | None:
    """Mean Overall over the judges for one task in one lane dir, or None."""
    scores = []
    for p in lane_dir.rglob(f"iclr2025_{task}/review_*.json"):
        if "hallucination" in p.name:
            continue
        with p.open(encoding="utf-8") as f:
            d = json.load(f)
        v = d.get("Overall")
        scores.append(float(v["score"] if isinstance(v, dict) else v))
    return statistics.mean(scores) if scores else None


def load_config(bb: str, lane: str | None) -> dict[str, float]:
    base = EVAL / "youra" / bb if lane is None else EVAL / "youra_ablation_study" / lane.format(bb=bb)
    if not base.is_dir():
        return {}
    out = {}
    for t in TASKS:
        v = cell_overall(base, t)
        if v is not None:
            out[t] = v
    return out


def sign_flip_p(diffs: list[float], rng: random.Random) -> float:
    obs = abs(statistics.mean(diffs))
    hits = 0
    for _ in range(B):
        s = sum(d if rng.random() < 0.5 else -d for d in diffs)
        if abs(s / len(diffs)) >= obs - 1e-12:
            hits += 1
    return (hits + 1) / (B + 1)


def fmt(v: float) -> str:
    return f"{v:+.2f}"


def main() -> None:
    rng = random.Random(SEED)
    lines: list[str] = []
    say = lines.append

    # {label: {(bb, task): score}}
    data: dict[str, dict[tuple[str, str], float]] = {}
    for label, lane in LADDER:
        data[label] = {}
        for bb in BACKBONES:
            for t, v in load_config(bb, lane).items():
                data[label][(bb, t)] = v
    for s in SINGLES:
        data[s] = {}
        for bb in BACKBONES:
            for t, v in load_config(bb, f"{bb}_{s}").items():
                data[s][(bb, t)] = v

    say("== Overall mean +/- task SD per backbone (judge-averaged, n tasks) ==")
    order = ["full", "no_VSA", "no_IC", "no_mcp", "no_reflection",
             "no_VSA_no_IC", "no_VSA_no_IC_no_mcp",
             "no_VSA_no_IC_no_mcp_no_reflection"]
    for label in order:
        row = [f"{label:<34}"]
        for bb in BACKBONES:
            vals = [v for (b, _), v in data[label].items() if b == bb]
            row.append(f"{statistics.mean(vals):.2f}+/-{statistics.stdev(vals):.2f} (n={len(vals)})"
                       if len(vals) >= 2 else "--")
        say("  ".join(row))
    say("")

    say(f"== Paired sign-flip permutation tests (two-sided, B={B}, cell = (backbone, task)) ==")
    pairs = [("full", "no_VSA_no_IC"), ("full", "no_VSA_no_IC_no_mcp"),
             ("full", "no_VSA_no_IC_no_mcp_no_reflection"),
             ("no_VSA_no_IC", "no_VSA_no_IC_no_mcp"),
             ("no_VSA_no_IC_no_mcp", "no_VSA_no_IC_no_mcp_no_reflection")]
    for a, b in pairs:
        cells = sorted(set(data[a]) & set(data[b]))
        diffs = [data[a][c] - data[b][c] for c in cells]
        p = sign_flip_p(diffs, rng)
        wlt = (sum(d > 0 for d in diffs), sum(d < 0 for d in diffs), sum(d == 0 for d in diffs))
        say(f"{a} - {b}: delta={fmt(statistics.mean(diffs))}  n={len(cells)}  "
            f"W/L/T={wlt[0]}/{wlt[1]}/{wlt[2]}  perm p={p:.4f}")
    say("")

    say("== VSA x IC interaction: [full - no_VSA] - [no_IC - no_VSA_no_IC] ==")
    cells = sorted(set(data["full"]) & set(data["no_VSA"]) & set(data["no_IC"])
                   & set(data["no_VSA_no_IC"]))
    inter = [data["full"][c] - data["no_VSA"][c] - data["no_IC"][c] + data["no_VSA_no_IC"][c]
             for c in cells]
    p = sign_flip_p(inter, rng)
    say(f"mean interaction={fmt(statistics.mean(inter))}  n={len(cells)} cells  perm p={p:.4f}")
    say("  (positive = super-additive/synergy, negative = sub-additive/redundancy)")
    per_bb = {bb: [i for c, i in zip(cells, inter) if c[0] == bb] for bb in BACKBONES}
    for bb, vals in per_bb.items():
        if vals:
            say(f"  {bb}: mean={fmt(statistics.mean(vals))} (n={len(vals)})")
    say("")

    say("== MCP x state-core interaction: [full - no_mcp] - [no_VSA_no_IC - no_VSA_no_IC_no_mcp] ==")
    cells = sorted(set(data["full"]) & set(data["no_mcp"]) & set(data["no_VSA_no_IC"])
                   & set(data["no_VSA_no_IC_no_mcp"]))
    inter = [data["full"][c] - data["no_mcp"][c]
             - data["no_VSA_no_IC"][c] + data["no_VSA_no_IC_no_mcp"][c]
             for c in cells]
    p = sign_flip_p(inter, rng)
    say(f"mean interaction={fmt(statistics.mean(inter))}  n={len(cells)} cells  perm p={p:.4f}")
    say("  (positive = MCP's contribution depends on the VSA+IC state core being present)")
    per_bb = {bb: [i for c, i in zip(cells, inter) if c[0] == bb] for bb in BACKBONES}
    for bb, vals in per_bb.items():
        if vals:
            say(f"  {bb}: mean={fmt(statistics.mean(vals))} (n={len(vals)})")

    text = "\n".join(lines)
    (HERE / "dismantling_ladder_stats_results.txt").write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
