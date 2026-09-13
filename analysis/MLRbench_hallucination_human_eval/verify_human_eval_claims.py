#!/usr/bin/env python3
"""Verify the human-evaluation statistics quoted in the author responses.

Recomputes, from the bundled annotation label files (and the hallucination
review JSONs they point into), every human-evaluation number cited in the
discussion-period responses:

  * overall with-context flag precision 203/270 = 75.2%
    with Wilson 95% CI 69.7-80.0,
  * per-category precision (hallucinated methodology 92/102 = 90.2%,
    faked experimental results 64/85 = 75.3%, mathematical errors
    15/21 = 71.4%, nonexistent citations 32/62 = 51.6%),
  * per-system precision (YouRA 68/90, MLR-Agent 70/90,
    AI Scientist V2 65/90) and the chi-square test
    (chi2(2) = 0.75, p = 0.686),
  * anchor reliability on the 90-item overlap: agreement 69/90 = 76.7%,
    Cohen's kappa = 0.54, 18 of 21 disagreements in the primary-True ->
    anchor-False direction, YouRA-subset agreement 26/30 = 86.7% with
    subset kappa = 0.72.

Item ids are repository-root-relative paths, so the category join works from
a fresh clone. Pure standard library; locates the repository root by walking
up from this file:

    python analysis/MLRbench_hallucination_human_eval/verify_human_eval_claims.py

Also writes the full PASS/FAIL report (no timestamps, so re-runs are
byte-identical) to a *_results.txt file next to this script.
Exit code 0 iff every check passes.
"""
from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
MARKER = Path("results") / "evaluations" / "mlrbench_hallucination"

PRIMARY = ["labels_a_AnnotatorA.json", "labels_b_AnnotatorB.json",
           "labels_c_AnnotatorC.json"]
ANCHOR = ["labels_d_anchor_1-30.json", "labels_d1_anchor_31-90.json"]

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


def load_labels(path: Path) -> dict[tuple[str, int], bool]:
    return {(it["file"], it["idx"]): bool(it["human_assessment"])
            for it in json.load(path.open())["results"]}


def wilson_ci(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return center - half, center + half


def cohen_kappa(pairs: list[tuple[bool, bool]]) -> float:
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    pa = sum(a for a, _ in pairs) / n
    pb = sum(b for _, b in pairs) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return (po - pe) / (1 - pe)


def main() -> int:
    root = find_repo_root()

    # ---- primary labels: precision -----------------------------------------
    primary: dict[tuple[str, int], bool] = {}
    for f in PRIMARY:
        primary.update(load_labels(HERE / f))
    n, k = len(primary), sum(primary.values())
    check("overall precision (true/total)", (k, n), (203, 270))
    check("overall precision %", round(100 * k / n, 1), 75.2, 0.05)
    lo, hi = wilson_ci(k, n)
    check("Wilson CI low", round(100 * lo, 1), 69.7, 0.05)
    check("Wilson CI high", round(100 * hi, 1), 80.0, 0.05)

    # ---- per-category (join to the flagged review JSONs by file+idx) --------
    cat = defaultdict(lambda: [0, 0])
    sys_counts = defaultdict(lambda: [0, 0])
    for (file, idx), v in primary.items():
        flag = json.load((root / file).open())["hallucinations"][idx]
        c = cat[flag["type"]]
        c[0] += v; c[1] += 1
        s = sys_counts[file.split("/")[3]]
        s[0] += v; s[1] += 1
    claimed_cat = {"Hallucinated Methodology": (92, 102, 90.2),
                   "Faked Experimental Results": (64, 85, 75.3),
                   "Mathematical Errors": (15, 21, 71.4),
                   "Nonexistent Citations": (32, 62, 51.6)}
    for name, (ck, cn, pct) in claimed_cat.items():
        got = tuple(cat[name])
        check(f"category {name}", (got[0], got[1]), (ck, cn))
        check(f"category {name} %", round(100 * got[0] / got[1], 1), pct, 0.05)

    claimed_sys = {"youra": 68, "mlragent": 70, "ai_scientist_v2": 65}
    for s, ck in claimed_sys.items():
        check(f"system {s} precision", tuple(sys_counts[s]), (ck, 90))

    # chi-square (2x3, no correction); df=2 so p = exp(-x/2)
    rows = [(sys_counts[s][0], sys_counts[s][1] - sys_counts[s][0])
            for s in ("youra", "mlragent", "ai_scientist_v2")]
    col = [sum(r[j] for r in rows) for j in (0, 1)]
    tot = sum(col)
    chi2 = sum((rows[i][j] - 90 * col[j] / tot) ** 2 / (90 * col[j] / tot)
               for i in range(3) for j in (0, 1))
    check("chi-square statistic", round(chi2, 2), 0.75, 0.005)
    check("chi-square p (df=2)", round(math.exp(-chi2 / 2), 3), 0.686, 0.0005)

    # ---- anchor reliability on the 90-item overlap ---------------------------
    anchor: dict[tuple[str, int], bool] = {}
    for f in ANCHOR:
        anchor.update(load_labels(HERE / f))
    pairs = [(primary[key], anchor[key]) for key in anchor if key in primary]
    check("overlap size", len(pairs), 90)
    agree = sum(a == b for a, b in pairs)
    check("anchor agreement", agree, 69)
    check("anchor agreement %", round(100 * agree / 90, 1), 76.7, 0.05)
    check("pooled Cohen's kappa", cohen_kappa(pairs), 0.54, 0.005)
    p_true_a_false = sum(1 for a, b in pairs if a and not b)
    disagreements = 90 - agree
    check("disagreement direction (primary True -> anchor False)",
          (p_true_a_false, disagreements), (18, 21))
    youra_pairs = [(primary[key], anchor[key]) for key in anchor
                   if key in primary and key[0].split("/")[3] == "youra"]
    check("YouRA overlap agreement",
          (sum(a == b for a, b in youra_pairs), len(youra_pairs)), (26, 30))
    check("YouRA subset kappa", cohen_kappa(youra_pairs), 0.72, 0.005)

    summary = f"{len(PASS)} passed, {len(FAIL)} failed."
    report_path = HERE / (Path(__file__).stem + "_results.txt")
    report_path.write_text("\n".join(REPORT + ["", summary]) + "\n", encoding="utf-8")
    print(f"\n{summary}")
    print(f"Report saved to {report_path.name}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
