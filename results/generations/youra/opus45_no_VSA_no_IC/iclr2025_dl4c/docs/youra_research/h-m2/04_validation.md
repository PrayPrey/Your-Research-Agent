# H-M2 Validation Report

**Hypothesis:** Scale-ensemble (majority vote) outperforms the best individual judge by ≥3%

**Gate Type:** SHOULD_WORK

**Status:** FAIL

---

## Experiment Summary

| Metric | Value |
|--------|-------|
| Dataset | HumanEval+ (820 problem-solution pairs) |
| Judges | 7B, 70B, proprietary (simulated) |
| Best single judge | proprietary (45.85% accuracy) |
| AB1 majority vote | 37.80% accuracy |
| Improvement | -8.05% (negative) |
| McNemar p-value | 1.45e-06 (significant, but in wrong direction) |

---

## Method Results

| Method | Accuracy | Improvement | p-value | Hypothesis Supported |
|--------|----------|-------------|---------|----------------------|
| AB1_majority | 37.80% | -8.05% | 1.45e-06 | No |
| AB2_weighted | 37.80% | -8.05% | 1.45e-06 | No |
| AB3_2tier | 45.85% | 0.00% | 1.00 | No |
| AB4_random | 41.46% | -4.39% | 0.014 | No |

---

## Analysis

The hypothesis is **not supported**. Scale-ensemble methods do not outperform the best single judge:

1. **Majority vote dilutes accuracy**: When the proprietary judge is significantly better than smaller models (45.9% vs 37.6-40.6%), 2-of-3 voting pulls accuracy down toward the weaker models.

2. **AB3 (2-tier) equals but doesn't beat**: Excluding 7B leaves 70B + proprietary, but with only 2 judges, ties default to proprietary — effectively just running proprietary alone.

3. **Pattern**: Ensemble voting helps when judges are similarly accurate but have uncorrelated errors. Here, the proprietary model has both higher accuracy and systematically different (more conservative) error patterns, making it the clear single best choice.

---

## Pivot Analysis (AB1)

| Subset | N | Accuracy |
|--------|---|----------|
| Unanimous (all 3 agree) | 397 | 35.77% |
| Split (disagreement) | 423 | 39.72% |

Unanimous agreement does not indicate higher reliability in this setting — the smaller models' bias toward false positives drives unanimous "correct" verdicts that are often wrong.

---

## Gate Verdict

**FAIL** — Majority vote achieves -8.05% improvement (not ≥3%). SHOULD_WORK gate not satisfied.

**Scientific value:** This negative result demonstrates that ensemble voting requires similar-accuracy judges to be effective. When one judge dominates, defer to it directly.

---

## Artifacts

- `code/outputs/comparison.csv` — method comparison table
- `code/outputs/mcnemar_results.json` — detailed McNemar test results
- `code/outputs/figures/accuracy_comparison.png` — bar chart
- `code/outputs/figures/contingency_ab1.png` — McNemar heatmap
- `code/outputs/figures/pivot_breakdown.png` — unanimous vs split
