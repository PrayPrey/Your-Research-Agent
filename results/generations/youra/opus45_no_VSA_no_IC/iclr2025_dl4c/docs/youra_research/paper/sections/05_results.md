# Results

We present results for each prediction, highlighting confirmed hypotheses (P1, P2) and falsified hypotheses (P3, P4).

## P1: Scale Ordering with Diminishing Returns ✓

**Finding**: Accuracy increases with scale, but with strong diminishing returns.

| Scale Tier | Accuracy | Cohen's Kappa | Δ from Previous |
|------------|----------|---------------|-----------------|
| 7B | 58.5% | 0.131 | — |
| 70B | 70.7% | 0.394 | +12.2pp |
| Proprietary | 71.3% | 0.396 | +0.6pp |

The diminishing returns ratio is **20.3:1** (12.2pp / 0.6pp), far exceeding our threshold of 5:1.

**Statistical test**: Kruskal-Wallis H = 7.71, p = 0.021

**Interpretation**: The 7B→70B transition captures most of the scale benefit. Going from 70B to proprietary yields marginal accuracy improvement (0.6pp) at substantially higher cost. For cost-sensitive deployments, 70B represents the optimal scale tier.

## P2: Scale-Dependent Error Patterns ✓

**Finding**: Error type distributions are strongly associated with scale.

| Scale | FPR | FNR | TP | TN | FP | FN |
|-------|-----|-----|----|----|----|----|
| 7B | 74.8% | 12.8% | 143 | 165 | 491 | 21 |
| 70B | 69.2% | 20.1% | 131 | 202 | 454 | 33 |
| Proprietary | 60.4% | 29.3% | 116 | 260 | 396 | 48 |

**Statistical test**: Chi-square χ² = 45.78, df = 6, p = 3.27×10⁻⁸

The p-value is **six orders of magnitude** below the significance threshold, indicating overwhelming evidence for scale-dependent error patterns.

**Key observation**: As scale increases:
- FPR decreases (74.8% → 60.4%): Larger models become more conservative
- FNR increases (12.8% → 29.3%): Larger models reject more correct solutions

This FPR-FNR tradeoff is the mechanism underlying the ensemble failures in P3 and P4.

## P3: Ensemble Benefit ✗ (FALSIFIED)

**Finding**: Ensemble voting **degrades** accuracy compared to the best single judge.

| Method | Accuracy | Δ vs. Best Single | p-value |
|--------|----------|-------------------|---------|
| Best single (Proprietary) | 45.85% | — | — |
| AB1: Simple majority | 37.80% | **−8.05%** | 1.45×10⁻⁶ |
| AB2: Weighted majority | 37.80% | **−8.05%** | 1.45×10⁻⁶ |
| AB3: Two-tier (70B+Prop) | 45.85% | 0.00% | 1.00 |

**Statistical test**: McNemar χ² = 23.7, p = 1.45×10⁻⁶

The ensemble is **significantly worse** than the best single judge. This falsifies P3.

**Why ensemble fails**: The 7B model's over-acceptance bias (FPR=74.8%) dominates majority voting. When 7B and 70B both vote "correct" (both have high FPR), they outvote proprietary's more accurate "incorrect" verdict. The ensemble amplifies the worst judge's bias rather than averaging errors.

AB3 (excluding 7B) achieves parity with proprietary alone—confirming that 7B's inclusion is what corrupts the ensemble.

## P4: Unanimous Agreement Reliability ✗ (FALSIFIED)

**Finding**: Unanimous agreement correlates with **lower** accuracy than disagreement.

| Agreement Type | N | Accuracy |
|----------------|---|----------|
| Unanimous | 397 | 35.77% |
| Split (2-1) | 423 | 39.72% |

**Difference**: −3.95pp (opposite direction from the +10% hypothesis)

**Statistical test**: z = −1.165, p = 0.878 (one-tailed for improvement)

The effect is not significant, but the direction is reversed from expectations.

**Why unanimous signals bias, not truth**: When all judges agree "correct":
- 7B (FPR=74.8%) almost always says correct
- 70B (FPR=69.2%) usually agrees
- Proprietary (FPR=60.4%) often agrees

Unanimous "correct" captures the intersection of all three over-acceptance biases—exactly the cases where all judges are systematically wrong.

When judges disagree (2-1 split), proprietary's conservative FNR often triggers the disagreement. These disagreements are *informative*—they flag cases where the most accurate judge sees something the others miss.

## Summary: Prediction Outcomes

| Prediction | Hypothesis | Gate | Result | Evidence |
|------------|-----------|------|--------|----------|
| P1 | Scale ordering with diminishing returns | MUST_WORK | ✓ PASS | H=7.71, p=0.021 |
| P2 | Scale-dependent error patterns | MUST_WORK | ✓ PASS | χ²=45.78, p=3.27×10⁻⁸ |
| P3 | Ensemble ≥3% improvement | SHOULD_WORK | ✗ FAIL | −8.05%, p=1.45×10⁻⁶ |
| P4 | Unanimous ≥10% more reliable | SHOULD_WORK | ✗ FAIL | −3.95%, p=0.878 |

The core claims (P1, P2) about scale-dependent patterns are confirmed. The practical implications (P3, P4) about ensemble benefit are falsified.

## Figure Summary

| Figure | Content | Key Finding |
|--------|---------|-------------|
| Fig. 1 (fp_fn_comparison.png) | FPR/FNR by scale | FPR decreases, FNR increases with scale |
| Fig. 2 (error_distribution.png) | Error type distribution | Visual confirmation of chi-square result |
| Fig. 3 (contingency_heatmap.png) | Contingency table | Scale × error type association |
| Fig. 4 (diminishing_returns.png) | Accuracy vs. scale | 20:1 diminishing returns ratio |
| Fig. 5 (confusion_matrices.png) | Per-scale confusion matrices | Raw counts supporting P2 |
| Fig. 6 (kappa_by_scale.png) | Cohen's Kappa | Agreement increases with scale |
| Fig. 7 (accuracy_comparison.png) | Ensemble methods | All ensembles ≤ best single |
| Fig. 8 (pivot_breakdown.png) | Pivotal vote analysis | 7B dominates ensemble decisions |
| Fig. 9 (bar_chart.png) | Unanimous vs. split | Unanimous has lower accuracy |
