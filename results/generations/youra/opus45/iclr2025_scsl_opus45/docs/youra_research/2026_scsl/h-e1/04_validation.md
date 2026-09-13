# Phase 4 Validation Report: H-E1

**Hypothesis ID:** H-E1
**Hypothesis Type:** EXISTENCE
**Gate Type:** MUST_WORK
**Date:** 2026-04-14
**Status:** COMPLETED

---

## Executive Summary

**Gate Result: PASS**

The H-E1 hypothesis has been successfully validated. Per-sample loss trajectory features extracted from epochs 1-5 of ERM training on Waterbirds dataset predict minority group membership with **AUROC = 0.9452 ± 0.0072**, significantly exceeding the gate threshold of 0.75.

---

## Hypothesis Statement

> Under standard ERM training on Waterbirds, if we extract per-sample loss trajectory features (L₁, slope, variance, time-to-convergence) from epochs 1-5, then these features will predict minority group membership with AUROC > 0.75, because minority samples experience prolonged optimization conflict creating distinctive trajectory patterns.

---

## Experiment Configuration

| Parameter | Value |
|-----------|-------|
| Dataset | Waterbirds |
| Model | ResNet-50 (ImageNet pretrained) |
| Optimizer | SGD (lr=0.001, momentum=0.9, weight_decay=0.0001) |
| Batch Size | 128 |
| Total Epochs | 20 |
| Trajectory Epochs | 5 |
| Random Seed | 42 |
| CV Folds | 5 |

---

## Dataset Statistics

| Metric | Value |
|--------|-------|
| Training Samples | 4,795 |
| Validation Samples | 1,199 |
| Test Samples | 5,794 |
| Minority Samples | 240 (5.0%) |
| Majority Samples | 4,555 (95.0%) |

**Group Distribution:**
- Group 0 (Landbird on Land): 3,498 - Majority
- Group 1 (Landbird on Water): 184 - Minority
- Group 2 (Waterbird on Land): 56 - Minority
- Group 3 (Waterbird on Water): 1,057 - Majority

---

## Results

### Primary Metric: AUROC

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| AUROC (5-fold CV) | **0.9452 ± 0.0072** | 0.75 | **PASS** |

### Per-Feature AUROC Analysis

| Feature | AUROC | Interpretation |
|---------|-------|----------------|
| L₁ (Initial Loss) | **0.9473** | Most discriminative - minority samples have higher initial loss |
| Slope | 0.8970 | Strong discriminator - minority samples show steeper loss decrease |
| Variance | 0.7242 | Moderate discriminator - minority trajectories are more variable |
| Convergence Time | 0.5259 | Weak discriminator - near random |

**Key Finding:** The initial loss (L₁) alone achieves AUROC = 0.9473, suggesting that minority samples are immediately distinguishable at the start of training due to higher initial loss values.

---

## Gate Evaluation

### MUST_WORK Gate

| Criterion | Expected | Achieved | Status |
|-----------|----------|----------|--------|
| AUROC > 0.75 | > 0.75 | 0.9452 | **PASS** |
| Code executes without errors | Yes | Yes | **PASS** |
| Mechanism correctly implemented | Yes | Yes | **PASS** |
| Metrics measurable | Yes | Yes | **PASS** |

**Gate Verdict: PASS**

The hypothesis mechanism works as expected. Loss trajectory features can successfully predict minority group membership with high accuracy.

---

## Visualizations

### 1. Gate Metrics Comparison
![Gate Metrics](figures/gate_metrics.png)

Bar chart comparing random baseline (0.50), target threshold (0.75), and achieved AUROC (0.9452).

### 2. Loss Trajectory Comparison
![Loss Trajectories](figures/loss_trajectories.png)

Mean ± std normalized loss curves for minority vs majority groups across epochs 1-5.

### 3. ROC Curve
![ROC Curve](figures/roc_curve.png)

ROC curve with AUROC annotation showing classification performance.

### 4. Feature Distributions
![Feature Distributions](figures/feature_distributions.png)

Histogram distributions of each trajectory feature by group membership.

---

## Key Findings

1. **Trajectory Divergence Exists:** Minority samples exhibit statistically distinguishable trajectory patterns from majority samples (AUROC = 0.9452 >> 0.75).

2. **Initial Loss is Most Predictive:** The L₁ feature (initial loss at epoch 1) is the strongest single predictor (AUROC = 0.9473), suggesting early training dynamics are most informative.

3. **Slope Captures Learning Dynamics:** The slope feature (AUROC = 0.8970) indicates minority samples experience different learning rates compared to majority samples.

4. **Variance Shows Trajectory Instability:** Moderate discriminative power (AUROC = 0.7242) suggests minority samples have more variable loss trajectories.

5. **Convergence Time Less Informative:** Near-random performance (AUROC = 0.5259) suggests time-to-minimum-loss is not a strong differentiator in early training.

---

## Implications for Main Hypothesis

The successful validation of H-E1 provides strong evidence that:

1. Loss trajectory divergence is a real phenomenon observable in spuriously correlated datasets
2. Simple trajectory features can capture this divergence effectively
3. The methodology can serve as a foundation for subsequent mechanism hypotheses (H-M1, H-M2, H-M3)

---

## Files Generated

| File | Description |
|------|-------------|
| `code/config.py` | Experiment configuration |
| `code/data.py` | Waterbirds dataset loading |
| `code/model.py` | ResNet-50 classifier |
| `code/train.py` | Training loop with loss tracker |
| `code/evaluate.py` | Feature extraction and AUROC |
| `code/run.py` | Main experiment runner |
| `code/outputs/results.json` | Structured results |
| `figures/gate_metrics.png` | Gate comparison figure |
| `figures/loss_trajectories.png` | Trajectory comparison |
| `figures/roc_curve.png` | ROC curve |
| `figures/feature_distributions.png` | Feature distributions |

---

## Next Steps

With H-E1 validated (PASS), the pipeline can proceed to:

1. **H-M1 (Mechanism):** Investigate delayed curvature stabilization in minority samples
2. **H-M2 (Mechanism):** Test trajectory attenuation under GroupDRO vs random reweighting
3. **H-M3 (Mechanism):** Evaluate early divergence as predictor of final WGA

---

## Appendix: Raw Metrics

```json
{
  "auroc_mean": 0.9452,
  "auroc_std": 0.0072,
  "per_feature_auroc": {
    "L1": 0.9473,
    "slope": 0.8970,
    "variance": 0.7242,
    "convergence": 0.5259
  },
  "gate": {
    "threshold": 0.75,
    "achieved": 0.9452,
    "passed": true,
    "result": "PASS"
  }
}
```

---

*Generated by Phase 4 Validation Workflow*
*Gate Type: MUST_WORK | Result: PASS*
*Hypothesis H-E1 validated successfully*
