# 5. Results

## 5.1 h-e1: NTI Existence (VALIDATED)

NTI achieves mean AUROC **0.5657** across 5-fold CV, exceeding the 0.55 threshold.

| Fold | AUROC | Status |
|------|-------|--------|
| 1 | 0.5356 | Below threshold |
| 2 | 0.5954 | Pass |
| 3 | 0.5665 | Pass |
| 4 | 0.5469 | Below threshold |
| 5 | 0.5839 | Pass |
| **Mean** | **0.5657** | **Pass** |

All folds exceed the 0.52 falsification boundary, confirming the existence of discriminative signal. The variance across folds (0.5356-0.5954) indicates sensitivity to data splits but consistent above-chance performance.

**Gate Verdict**: PASS. The EXISTENCE hypothesis is validated.

## 5.2 h-m1: Combined Model (VALIDATED)

The combined model [H_L + NTI + CMI] significantly outperforms the H_L-only baseline.

| Metric | Value |
|--------|-------|
| Null AUROC (H_L only) | 0.5000 |
| Full AUROC (H_L + NTI + CMI) | 0.5712 |
| **AUROC Gain** | **+0.0712** |
| **Combined p-value** | **1.15e-05** |

Per-fold LRT results:

| Fold | Null AUROC | Full AUROC | Gain | p-value |
|------|------------|------------|------|---------|
| 0 | 0.5000 | 0.5645 | +0.0645 | 0.156 |
| 1 | 0.5000 | 0.6062 | +0.1062 | 4.84e-04 |
| 2 | 0.5000 | 0.5747 | +0.0747 | 6.19e-03 |
| 3 | 0.5000 | 0.5381 | +0.0381 | 0.460 |
| 4 | 0.5000 | 0.5727 | +0.0727 | 6.00e-03 |

All folds show positive gain; 3/5 are individually significant. Fisher's combined p-value (1.15e-05) strongly rejects the null hypothesis that trajectory features add no predictive value.

**Gate Verdict**: PASS. The MECHANISM hypothesis is validated.

## 5.3 h-m2: Low-Entropy Subset (REFUTED)

On the low-entropy subset (H_L < 25th percentile, n=1029), NTI fails to discriminate.

| Metric | Value | Threshold |
|--------|-------|-----------|
| AUROC | 0.5136 | > 0.55 |
| 95% CI | [0.4639, 0.5628] | LB > 0.50 |

The confidence interval includes chance (0.50), indicating no reliable signal. This refutes the hypothesis that trajectory metrics provide orthogonal information to entropy.

**Interpretation**: NTI's discriminative power is driven by high-entropy cases. When the model is confident (low entropy), trajectory instability collapses to noise. This is a fundamental limitation: NTI is defined as variance/mean of entropy, making it mathematically coupled to the entropy regime.

**Gate Verdict**: FAIL. Recorded as limitation.

## 5.4 h-m3: RCI Flip Pattern (REFUTED)

The RCI flip pattern occurs in nearly all samples regardless of correctness.

| Class | Flip Rate | Threshold | Status |
|-------|-----------|-----------|--------|
| Hallucinations | 95.1% (756/795) | ≥ 30% | Pass |
| Correct | 90.9% (20/22) | < 10% | **Fail** |
| Separation | 4.2% | ≥ 20% | **Fail** |

The flip pattern is near-universal (>90% in both classes), providing no discriminative signal.

**Interpretation**: Layer-wise top-token competition is an architectural property of iterative refinement in transformers (Elhage et al., 2022), not an epistemic indicator of hallucination. This negative result informs future interpretability research: token-level dynamics may be too coarse to capture semantic uncertainty.

**Gate Verdict**: FAIL. Recorded as limitation.

## 5.5 Summary

| Hypothesis | Prediction | Result | Status |
|------------|------------|--------|--------|
| h-e1 | NTI AUROC > 0.55 | 0.5657 | **VALIDATED** |
| h-m1 | Combined gain ≥ 0.03 | +0.0712 | **VALIDATED** |
| h-m2 | Low-entropy AUROC > 0.55 | 0.5136 | **REFUTED** |
| h-m3 | Flip separation ≥ 20% | 4.2% | **REFUTED** |

Core claims validated; secondary mechanisms partially refuted. The hypothesis scope is narrowed to high-entropy cases.
