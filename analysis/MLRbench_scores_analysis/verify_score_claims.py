#!/usr/bin/env python3
"""Verify the score-level statistics quoted in the author discussion responses.

Recomputes, from the raw judge JSONs bundled in this repository, every
score-related number cited in the discussion-period responses:

  * the persistence-versus-context (no-VSA) ablation table
    (per-metric mean +/- sample SD for both conditions and their deltas),
  * the task-level direction (8/10 tasks lower) and its calibration
    (exact paired permutation test over all 2^10 sign assignments and the
    two-sided sign test),
  * the per-task details (dl4c, question, wsl transitions; the single high
    Grok-4.3 scores behind the two exceptions),
  * the MLR-Agent Sonnet 4.5 reference point (Overall 3.10),
  * the YouRA-vs-MLR-Agent Sonnet 4.5 contrast (+1.10, permutation p=0.059),
  * the six Table 1 first-place cells (Overall / Soundness on three backbones),
  * the qualitative-trace numbers for the Sonnet 4.6 scsl run (gradient-norm
    ratio 8.8 and minority AUC 0.914) as recorded in the released artifacts.

Pure standard library; locates the repository root by walking up from this
file, so it runs from any working directory in a fresh clone:

    python analysis/MLRbench_scores_analysis/verify_score_claims.py

Also writes the full PASS/FAIL report (no timestamps, so re-runs are
byte-identical) to a *_results.txt file next to this script.
Exit code 0 iff every check passes.
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

PASS: list[str] = []
FAIL: list[str] = []
REPORT: list[str] = []


def find_repo_root() -> Path:
    cur = HERE
    while True:
        if (cur / MARKER).is_dir():
            return cur
        if cur.parent == cur:
            raise RuntimeError(f"Could not locate {MARKER} above {HERE}")
        cur = cur.parent


def check(name: str, got, want, tol: float | None = None) -> None:
    ok = (abs(got - want) <= tol + 1e-12) if tol is not None else (got == want)
    (PASS if ok else FAIL).append(name)
    line = f"[{'PASS' if ok else 'FAIL'}] {name}: computed={got} claimed={want}"
    REPORT.append(line)
    print(line)


def score(path: Path, metric: str) -> float:
    v = json.load(path.open())[metric]
    return float(v["score"] if isinstance(v, dict) else v)


def task_means(lane_root: Path, metric: str, judge_reviews: bool = True) -> dict[str, float]:
    """Judge-averaged mean per task. Task dirs may carry lane suffixes."""
    pattern = "review_*.json" if judge_reviews else "review*.json"
    out: dict[str, float] = {}
    for t in TASKS:
        vals = [score(p, metric)
                for d in lane_root.rglob(f"iclr2025_{t}*")
                if d.is_dir()
                for p in sorted(d.glob(pattern))
                if "hallucination" not in p.name]
        assert len(vals) == 4, f"{lane_root} {t}: expected 4 judge scores, got {len(vals)}"
        out[t] = mean(vals)
    return out


def main() -> int:
    root = find_repo_root()
    B = root / MARKER

    # ---- no-VSA ablation table --------------------------------------------
    claimed = {
        "no_VSA": {"Clarity": (7.17, 0.46), "Novelty": (4.12, 1.09),
                   "Soundness": (2.73, 1.29), "Significance": (3.02, 0.92),
                   "Overall": (2.88, 0.94)},
        "baseline": {"Clarity": (7.50, 0.49), "Novelty": (5.22, 0.92),
                     "Soundness": (3.98, 1.74), "Significance": (4.30, 1.28),
                     "Overall": (4.20, 1.45)},
    }
    deltas_claimed = {"Clarity": -0.33, "Novelty": -1.10, "Soundness": -1.25,
                      "Significance": -1.27, "Overall": -1.33}

    no_vsa_root = B / "youra_ablation_study" / "sonnet45_no_VSA"
    base_root = B / "youra" / "sonnet45"
    for metric in METRICS:
        nv, bs = task_means(no_vsa_root, metric), task_means(base_root, metric)
        for label, tm in (("no_VSA", nv), ("baseline", bs)):
            m, sd = claimed[label][metric]
            check(f"{label} {metric} mean", round(mean(tm.values()), 2), m, 0.005)
            check(f"{label} {metric} SD", round(stdev(tm.values()), 2), sd, 0.005)
        d = mean(nv.values()) - mean(bs.values())
        check(f"delta {metric}", d, deltas_claimed[metric], 0.0051)

    # ---- direction + calibration ------------------------------------------
    nv, bs = task_means(no_vsa_root, "Overall"), task_means(base_root, "Overall")
    d = [nv[t] - bs[t] for t in TASKS]
    lower = sum(1 for x in d if x < 0)
    check("tasks lower without persistence", lower, 8)
    exceptions = sorted(t for t in TASKS if nv[t] - bs[t] > 0)
    check("exceptions are question and wsl", exceptions, ["question", "wsl"])

    obs = abs(mean(d))
    n_ge = sum(1 for signs in itertools.product([1, -1], repeat=10)
               if abs(mean(s * x for s, x in zip(signs, d))) >= obs - 1e-12)
    check("exact paired permutation p", n_ge / 2 ** 10, 0.092, 0.00055)
    k = max(lower, 10 - lower)
    check("sign test p", 2 * sum(comb(10, i) for i in range(k, 11)) / 2 ** 10,
          0.109, 0.0005)

    # ---- per-task details ---------------------------------------------------
    check("dl4c baseline", bs["dl4c"], 3.75, 0.005)
    check("dl4c no_VSA", nv["dl4c"], 2.50, 0.005)
    check("question baseline", bs["question"], 2.25, 0.005)
    check("question baseline is lane minimum", bs["question"], min(bs.values()), 1e-9)
    check("question no_VSA", nv["question"], 4.25, 0.005)
    check("wsl baseline", bs["wsl"], 3.00, 0.005)
    check("wsl no_VSA", nv["wsl"], 4.50, 0.005)
    for t in ("question", "wsl"):
        by_judge = {p.stem[len("review_"):]: score(p, "Overall")
                    for p in (no_vsa_root).rglob(f"iclr2025_{t}/review_*.json")
                    if "hallucination" not in p.name}
        check(f"{t} no_VSA grok-4.3 score", by_judge["grok-4.3"], 8.0, 1e-9)
        others = [v for j, v in by_judge.items() if j != "grok-4.3"]
        check(f"{t} no_VSA other judges <= 5", max(others) <= 5.0, True)

    # ---- MLR-Agent reference + contrast ------------------------------------
    mlr = task_means(B / "mlragent" / "sonnet45", "Overall", judge_reviews=False)
    check("MLR-Agent sonnet45 Overall", round(mean(mlr.values()), 2), 3.10, 0.005)
    check("no_VSA sits below MLR-Agent", mean(nv.values()) < mean(mlr.values()), True)

    diff = [bs[t] - mlr[t] for t in TASKS]
    check("YouRA - MLR-Agent mean diff", round(mean(diff), 2), 1.10, 0.005)
    obs = abs(mean(diff))
    n_ge = sum(1 for signs in itertools.product([1, -1], repeat=10)
               if abs(mean(s * x for s, x in zip(signs, diff))) >= obs - 1e-12)
    check("YouRA vs MLR-Agent permutation p", n_ge / 2 ** 10, 0.059, 0.0006)

    # ---- Table 1 first-place cells ------------------------------------------
    t1 = {("sonnet45", "Overall"): 4.20, ("opus45", "Overall"): 4.45,
          ("sonnet46", "Overall"): 5.05, ("sonnet45", "Soundness"): 3.98,
          ("opus45", "Soundness"): 4.58, ("sonnet46", "Soundness"): 4.92}
    for (bb, metric), want in t1.items():
        tm = task_means(B / "youra" / bb, metric)
        check(f"Table1 youra {bb} {metric}", round(mean(tm.values()), 2), want, 0.005)

    # ---- scsl trace numbers in released artifacts ---------------------------
    trace = (root / "results" / "generations" / "youra" / "sonnet46" /
             "iclr2025_scsl" / "docs" / "youra_research" / "2026_scsl" /
             "045_validated_hypothesis.md").read_text()
    for token, name in (("8.805", "scsl gradient-norm ratio 8.8"),
                        ("0.914", "scsl minority AUC 0.914")):
        check(name + " recorded in artifact", token in trace, True)

    summary = f"{len(PASS)} passed, {len(FAIL)} failed."
    report_path = HERE / (Path(__file__).stem + "_results.txt")
    report_path.write_text("\n".join(REPORT + ["", summary]) + "\n", encoding="utf-8")
    print(f"\n{summary}")
    print(f"Report saved to {report_path.name}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
