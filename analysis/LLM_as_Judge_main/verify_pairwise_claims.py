#!/usr/bin/env python3
"""Verify the pairwise-preference statistics quoted in the author responses.

Recomputes, from the raw per-judge result JSONs under
``LLM_as_Judge_results/``, every pairwise number cited in the
discussion-period responses:

  * all six Table 2 rows (order-collapsed judge-task win/tie/lose counts),
  * the aggregate counts (72/33/15 vs MLR-Agent, 55/38/27 vs AI Scientist V2),
  * the task-level verdicts for YouRA vs MLR-Agent on Sonnet 4.5
    (5 wins / 5 ties / 0 losses under per-task judge plurality, ties -> Tie)
    and the resulting two-sided sign test after dropping ties (p = 0.063),
  * Fleiss' kappa per comparison-by-backbone cell, recomputed from the raw
    verdicts and cross-checked against ``fleiss_kappa_summary.csv``
    (fair-to-moderate in five of six cells; -0.02 for YouRA vs MLR-Agent
    on Sonnet 4.6).

Pure standard library; locates the repository root by walking up from this
file, so it runs from any working directory in a fresh clone:

    python analysis/LLM_as_Judge_main/verify_pairwise_claims.py

Also writes the full PASS/FAIL report (no timestamps, so re-runs are
byte-identical) to a *_results.txt file next to this script.
Exit code 0 iff every check passes.
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "LLM_as_Judge_results"

BACKBONES = ["sonnet45", "opus45", "sonnet46"]
COMPARISONS = {
    "YouRA vs MLR-Agent": RESULTS / "LLM_as_Judge_YouRA_vs_MLRagent",
    "YouRA vs AI Scientist V2": RESULTS / "LLM_as_Judge_YouRA_vs_AI_scientist_v2",
}

# Claimed Table 2 rows: (win, tie, lose) per comparison x backbone.
TABLE2 = {
    ("YouRA vs MLR-Agent", "sonnet45"): (25, 14, 1),
    ("YouRA vs MLR-Agent", "opus45"): (26, 5, 9),
    ("YouRA vs MLR-Agent", "sonnet46"): (21, 14, 5),
    ("YouRA vs AI Scientist V2", "sonnet45"): (18, 14, 8),
    ("YouRA vs AI Scientist V2", "opus45"): (17, 12, 11),
    ("YouRA vs AI Scientist V2", "sonnet46"): (20, 12, 8),
}

PASS: list[str] = []
FAIL: list[str] = []
REPORT: list[str] = []


def check(name: str, got, want, tol: float | None = None) -> None:
    ok = (abs(got - want) <= tol + 1e-12) if tol is not None else (got == want)
    (PASS if ok else FAIL).append(name)
    line = f"[{'PASS' if ok else 'FAIL'}] {name}: computed={got} claimed={want}"
    REPORT.append(line)
    print(line)


def cell_verdicts(comp_dir: Path, backbone: str) -> dict[str, list[str]]:
    """{task: [4 order-collapsed judge verdicts (Win/Tie/Lose)]}"""
    per_task: dict[str, list[str]] = {}
    files = sorted(comp_dir.glob(f"*_{backbone}_*_results.json"))
    assert len(files) == 4, f"{comp_dir} {backbone}: expected 4 judge files, got {len(files)}"
    for f in files:
        for det in json.load(f.open())["details"]:
            per_task.setdefault(det["name"], []).append(det["verdict"])
    return per_task


def fleiss_kappa(per_task: dict[str, list[str]]) -> tuple[float, float, float]:
    """Fleiss' kappa over N tasks, 4 raters, categories Win/Tie/Lose."""
    cats = ["Win", "Tie", "Lose"]
    N, n = len(per_task), 4
    counts = [[v.count(c) for c in cats] for v in per_task.values()]
    p_j = [sum(row[j] for row in counts) / (N * n) for j in range(3)]
    P_i = [(sum(c * c for c in row) - n) / (n * (n - 1)) for row in counts]
    P_bar = sum(P_i) / N
    P_e = sum(p * p for p in p_j)
    return (P_bar - P_e) / (1 - P_e), P_bar, P_e


def main() -> int:
    totals: dict[str, Counter] = {c: Counter() for c in COMPARISONS}
    kappas: dict[tuple[str, str], float] = {}

    for comp, comp_dir in COMPARISONS.items():
        for bb in BACKBONES:
            per_task = cell_verdicts(comp_dir, bb)
            c = Counter(v for vs in per_task.values() for v in vs)
            check(f"Table2 {comp} {bb} (W,T,L)",
                  (c["Win"], c["Tie"], c["Lose"]), TABLE2[(comp, bb)])
            totals[comp].update(c)
            kappas[(comp, bb)], _, _ = fleiss_kappa(per_task)

    check("aggregate vs MLR-Agent (W,T,L)",
          tuple(totals["YouRA vs MLR-Agent"][k] for k in ("Win", "Tie", "Lose")),
          (72, 33, 15))
    check("aggregate vs AI Scientist V2 (W,T,L)",
          tuple(totals["YouRA vs AI Scientist V2"][k] for k in ("Win", "Tie", "Lose")),
          (55, 38, 27))

    # ---- task-level verdicts, focal comparison ------------------------------
    per_task = cell_verdicts(COMPARISONS["YouRA vs MLR-Agent"], "sonnet45")
    task_level = Counter()
    for verdicts in per_task.values():
        c = Counter(verdicts)
        top = max(c.values())
        leaders = [k for k, v in c.items() if v == top]
        task_level[leaders[0] if len(leaders) == 1 else "Tie"] += 1
    check("task-level (wins, ties, losses)",
          (task_level["Win"], task_level["Tie"], task_level["Lose"]), (5, 5, 0))
    n = task_level["Win"] + task_level["Lose"]
    check("sign test after dropping ties p", 2 * (0.5 ** n), 0.063, 0.0005)

    # ---- Fleiss' kappa -------------------------------------------------------
    with (HERE / "fleiss_kappa_summary.csv").open() as f:
        csv_rows = {(r["comparison"], r["backbone"]): r for r in csv.DictReader(f)}
    bb_label = {"sonnet45": "Sonnet 4.5", "opus45": "Opus 4.5", "sonnet46": "Sonnet 4.6"}
    for (comp, bb), k in kappas.items():
        row = csv_rows[(comp, bb_label[bb])]
        check(f"Fleiss kappa {comp} {bb} (vs bundled CSV)",
              k, float(row["fleiss_kappa"]), 0.001)
    check("kappa YouRA vs MLR-Agent sonnet46 ~ -0.02",
          kappas[("YouRA vs MLR-Agent", "sonnet46")], -0.02, 0.005)
    fair_or_mod = sum(1 for (comp, bb) in kappas
                      if csv_rows[(comp, bb_label[bb])]["interpretation"] in ("Fair", "Moderate"))
    check("fair-to-moderate cells", fair_or_mod, 5)

    summary = f"{len(PASS)} passed, {len(FAIL)} failed."
    report_path = HERE / (Path(__file__).stem + "_results.txt")
    report_path.write_text("\n".join(REPORT + ["", summary]) + "\n", encoding="utf-8")
    print(f"\n{summary}")
    print(f"Report saved to {report_path.name}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
