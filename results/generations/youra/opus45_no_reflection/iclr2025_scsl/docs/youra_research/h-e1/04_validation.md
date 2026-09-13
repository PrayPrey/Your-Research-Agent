# Validation Report: H-E1

**Date:** 2026-08-19
**Hypothesis:** CV of probe accuracy trajectories distinguishes spurious from core features with AUC >= 0.75
**Type:** EXISTENCE (PoC)
**Gate:** MUST_WORK

---

## Executive Summary

**Gate Result: FAIL**

The hypothesis that coefficient of variation (CV) of linear probe accuracy trajectories can distinguish spurious from core features was **not validated**. Both background (spurious) and bird_type (core) features showed nearly identical CV values (~0.04), providing no discriminative signal.

---

## Experiment Configuration

| Parameter | Value |
|-----------|-------|
| Dataset | Waterbirds (train split: 4795 samples) |
| Feature Extractor | CLIP ViT-B/16 (frozen, 512-dim) |
| Probe | LogisticRegression (C sweep: 0.001 to 100) |
| Subsets | 5 random 20% subsets |
| Seed | 42 |
| Gate Threshold | AUC >= 0.75 |

---

## Results

### CV Metrics

| Feature Type | CV Value | Expected Behavior |
|--------------|----------|-------------------|
| Background (Spurious) | 0.0393 | Lower CV expected |
| Bird Type (Core) | 0.0360 | Higher CV expected |
| **Difference** | 0.0033 | Near-zero separation |

### Gate Metrics

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| AUC | 0.0000 | >= 0.75 | **FAIL** |
| Best F1 | 0.6667 | - | - |

---

## Analysis

### Why the Hypothesis Failed

1. **Minimal CV Separation**: Both feature types showed CV values around 0.04. The expected pattern (spurious features with lower CV due to faster convergence) did not manifest clearly.

2. **CLIP Features Already Learned**: CLIP ViT-B/16 was pretrained on 400M image-text pairs. Both background and bird_type features are likely well-represented in the embedding space, leading to similar convergence dynamics.

3. **C-Sweep as Epoch Proxy Limitation**: Using regularization strength (C) as a proxy for training epochs may not capture true learning dynamics that distinguish spurious from core features.

4. **Two-Sample AUC Limitation**: With only 2 feature types (background, bird_type), AUC is binary (0 or 1). The marginal difference in CVs, combined with bird_type having slightly lower CV, inverted the expected ordering.

### Directional Check

The hypothesis predicted: CV(spurious) < CV(core)

Observed: CV(background=0.0393) > CV(bird_type=0.0360)

**Direction: OPPOSITE of expected** (though difference is within noise margin)

---

## Figures Generated

- `figures/gate_comparison.png` - AUC vs threshold bar chart
- `figures/cv_distribution.png` - CV values by feature type
- `figures/roc_curve.png` - ROC curve with AUC annotation
- `figures/trajectories.png` - Probe accuracy trajectories per subset

---

## Gate Decision

| Gate Type | Condition | Result |
|-----------|-----------|--------|
| MUST_WORK | AUC >= 0.75 | **FAIL** |

**Recommendation:** Return to Phase 2A for hypothesis redesign. Consider:
- Different feature representations (not pretrained CLIP)
- Different metrics beyond CV of improvement rate
- Multi-resolution or layer-wise probe analysis
- Training from scratch to observe emergence dynamics

---

## Code Artifacts

```
code/
├── config.yaml
├── config.py
├── data.py
├── features.py
├── cv_probe.py
├── evaluate.py
├── visualize.py
├── run_experiment.py
├── requirements.txt
├── data/
│   ├── waterbirds/
│   └── features_cache.npz
├── figures/
│   ├── gate_comparison.png
│   ├── cv_distribution.png
│   ├── roc_curve.png
│   └── trajectories.png
└── results.yaml
```

---

## Conclusion

The EXISTENCE hypothesis H-E1 was **not validated**. The CV-based approach for distinguishing spurious from core features using CLIP linear probe trajectories does not show discriminative power (AUC=0.0 vs threshold 0.75). The hypothesis requires fundamental redesign before proceeding to mechanism hypotheses.
