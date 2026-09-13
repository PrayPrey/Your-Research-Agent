# Validation Report: H-M1

**Date:** 2026-08-28
**Hypothesis:** Spurious features produce stronger gradient signal than core features (gradient norm ratio > 1.5 in early epochs)
**Type:** MECHANISM
**Gate Type:** MUST_WORK

---

## Result Summary

| Metric | Value |
|--------|-------|
| **Gate Result** | **FAIL** |
| Mean Early Ratio (epochs 1-10) | 0.176 |
| Required Threshold | 1.5 |
| Decreasing Trend | Yes (all seeds) |

---

## Per-Seed Results

| Seed | Early Ratio | Decreasing | Pass |
|------|-------------|------------|------|
| 42 | 0.175 | Yes | No |
| 123 | 0.173 | Yes | No |
| 456 | 0.181 | Yes | No |

---

## Experimental Setup

- **Dataset:** Waterbirds v1.0 (11,788 images)
- **Model:** ResNet-50 (ImageNet pretrained)
- **Optimizer:** SGD (lr=0.001, momentum=0.9, weight_decay=1e-4)
- **Epochs:** 50
- **Seeds:** 3 (42, 123, 456)
- **Batch Size:** 128

### Measurement Methodology

Measured gradient norms at layer4 for two sample groups:
1. **Spurious-aligned:** Samples where label == place (bird type matches background type)
2. **Minority:** Samples where label != place (bird type does not match background type)

Computed ratio = spurious_norm / minority_norm per epoch.

---

## Key Findings

1. **Ratio consistently < 1.0:** Mean ratio 0.176 indicates minority group samples produce ~5.7x higher gradient norms than spurious-aligned samples.

2. **Decreasing trend observed:** Ratio decreases over training as expected, but from 0.45 at epoch 1 to 0.13-0.16 by epoch 50.

3. **Hypothesis falsified:** The stated mechanism "spurious features produce stronger gradient signal" is contradicted by the data. Instead:
   - Spurious-aligned samples (easy to classify via background) have LOW gradient norms
   - Minority samples (hard to classify, need bird features) have HIGH gradient norms

---

## Interpretation

The hypothesis mechanism is **inverted**. Spurious features dominate not because they receive stronger gradients, but because:

1. They are **simpler** to learn (lower loss = lower gradients)
2. The network reaches low loss on spurious-aligned samples quickly
3. Minority samples continue producing high gradients because they remain difficult

This aligns with Simplicity Bias (Shah et al., 2020): the network doesn't amplify spurious feature learning through stronger gradients — it simply converges faster on simpler patterns, leaving less optimization pressure on those samples.

---

## Gate Verdict

**FAIL** — The mechanism as stated is incorrect. Gradient norm ratio is 0.18, not >1.5.

### Routing Decision

Per MUST_WORK gate failure protocol:
- **Route to:** Phase 2A-Dialogue for mechanism revision
- **Reason:** The observed effect is inverted from hypothesis. Need to reformulate mechanism understanding.

### Lessons Learned

1. "Stronger gradient signal" ≠ "preferential learning." Lower gradients indicate faster convergence, not weaker learning.
2. Spurious feature dominance occurs because spurious patterns achieve low loss quickly, not because they receive more gradient signal.
3. Future mechanism hypotheses should consider loss landscape simplicity rather than gradient magnitude.

---

## Files Generated

- `figures/gate_bar_chart.png` - Per-seed early epoch ratio comparison
- `figures/ratio_trajectory.png` - Ratio over all 50 epochs
- `figures/norm_comparison.png` - Minority vs spurious-aligned gradient norms
- `results/gradient_norm_records.json` - Full per-epoch metrics
- `results/gate_result.json` - Gate check summary

---

## State Update

```yaml
h-m1:
  validation:
    status: COMPLETED
    result: FAIL
    key_findings:
      - Spurious/minority gradient ratio = 0.18 (inverse of hypothesis)
      - Minority samples produce 5.7x higher gradient norms
      - Decreasing trend observed but from 0.45 to 0.15, not from >1.5
      - Mechanism falsified: spurious dominance not from stronger gradients
  gate:
    type: MUST_WORK
    satisfied: false
    result: FAIL
  route_to: Phase 2A-Dialogue
  reflection_outcome: PIVOT
  completed: true
  completed_at: 2026-08-28T14:55:00+00:00
```
