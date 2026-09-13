# 5. Results

## 5.1 Summary of Findings

| Sub-Hypothesis | Prediction | Result | Status |
|----------------|------------|--------|--------|
| h-e1 (Existence) | NTI AUROC > 0.55 | **0.5657** | **VALIDATED** |
| h-m1 (Mechanism) | Combined gain ≥ 3% | **+7.1%** ($p = 1.15 \times 10^{-5}$) | **VALIDATED** |
| h-m2 (Low-entropy) | AUROC > 0.55 on confident subset | 0.5136 (CI includes 0.50) | **REFUTED** |
| h-m3 (RCI pattern) | ≥20pp separation | 4.2% separation | **REFUTED** |

## 5.2 Primary Results

### NTI Provides Weak but Consistent Signal

NTI alone achieves AUROC 0.5657, a modest but statistically significant improvement over chance. The effect is consistent across folds (range: 0.5356-0.5954), with no fold falling below the 0.52 falsification boundary.

### Combined Model Achieves +7.1% Gain

The full model ($H_L$ + NTI + CMI) achieves AUROC 0.5712, representing a +7.1% improvement over the $H_L$-only baseline. The likelihood ratio test confirms this is not due to overfitting (LRT $\chi^2 = 39.2$, $p = 1.15 \times 10^{-5}$).

Feature importance (logistic regression coefficients):
- $H_L$: $\beta = 0.42$ (positive: higher entropy → more likely incorrect)
- NTI: $\beta = 0.31$ (positive: higher instability → more likely incorrect)
- CMI: $\beta = -0.18$ (negative: higher monotonicity → less likely incorrect)

## 5.3 Negative Results

### Trajectory Metrics Fail on Confident Predictions

On the low-entropy subset (25th percentile of $H_L$), NTI achieves only AUROC 0.5136 with 95% CI [0.4639, 0.5628]. The confidence interval includes 0.50 (chance), indicating no reliable discrimination. This failure is structural: NTI is computed from entropy variance, which collapses when mean entropy is low.

### RCI Flip Pattern Is Architectural, Not Epistemic

RCI flip patterns appear in 95.1% of hallucinations and 90.9% of correct responses---a separation of only 4.2%, far below the 20% threshold. This reveals that top-token changes across layers are a universal feature of transformer processing \citep{elhage2022toy}, reflecting iterative refinement rather than epistemic uncertainty.

## 5.4 Effect Sizes

| Comparison | Cohen's $d$ | Interpretation |
|------------|-------------|----------------|
| NTI: halluc vs. correct | 0.18 | Small |
| Combined model AUC gain | 0.34 | Small-medium |
| RCI: halluc vs. correct | 0.05 | Negligible |

The effect sizes are modest, consistent with the challenging nature of single-pass hallucination detection.
