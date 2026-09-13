# Phase 4 Validation Report: H-M3

**Hypothesis:** Under QA conditions, if we combine inverse entropy and consistency via linear fusion (α·(1-entropy) + β·consistency), then the combined score is more predictive than either alone.

**Date:** 2026-08-19  
**Gate Type:** SHOULD_WORK  
**Gate Result:** FAIL (no improvement over best single metric)

---

## Executive Summary

H-M3 tested linear fusion of entropy and consistency signals for hallucination detection. Using h-m2's 20-question dataset:
- Combined AUROC: 0.8125
- Best single metric (consistency-only): 0.8125
- Improvement: 0.0000 (95% CI: [0.0000, 0.0000])

The optimal fusion weights (α=0.0, β=0.1) reduced to near-pure consistency scoring. At N=20, the fusion mechanism provides no improvement over consistency alone.

---

## Experiment Configuration

| Parameter | Value |
|-----------|-------|
| Input data | h-m2_results.json (N=20) |
| Val/Test split | 2/18 (10%/90%) |
| Alpha range | 0.0 to 1.0, step 0.1 |
| Beta range | 0.0 to 1.0, step 0.1 |
| Grid combos | 121 |
| Bootstrap samples | 1000 |
| Seed | 42 |

---

## Results

### Variant AUROC Comparison

| Variant | α | β | AUROC |
|---------|---|---|-------|
| entropy_only | 1.0 | 0.0 | 0.6750 |
| consistency_only | 0.0 | 1.0 | 0.8125 |
| equal | 0.5 | 0.5 | 0.8000 |
| optimal | 0.0 | 0.1 | 0.8125 |

### Optimal Weights

- **α (confidence weight):** 0.0
- **β (consistency weight):** 0.1
- **Val AUROC:** 1.0000 (overfitting on 2-sample val set)

### Bootstrap CI

- **Improvement:** 0.0000
- **95% CI:** [0.0000, 0.0000]

---

## Gate Evaluation

**Gate Type:** SHOULD_WORK  
**Criterion:** AUROC_combined > max(AUROC_entropy, AUROC_consistency)

| Metric | Value |
|--------|-------|
| AUROC_combined | 0.8125 |
| max(single metrics) | 0.8125 |
| Improvement | 0.0000 |

**Result:** FAIL — no improvement detected

---

## Analysis

### Why Fusion Didn't Help

1. **Tiny sample size (N=20):** Val set of 2 samples causes severe overfitting
2. **Consistency dominance:** AUROC 0.8125 vs entropy 0.675 — consistency already captures most signal
3. **Entropy adds noise:** At N=20, entropy signal is weak (AUROC 0.675), adding it dilutes consistency

### Implications

- Fusion hypothesis not disproven — needs N≥500 for meaningful test
- Consistency alone is strong predictor (AUROC 0.8125 matches h-m2 findings)
- Proceed to H-M4 per SHOULD_WORK gate (document limitation, continue)

---

## Artifacts Generated

### Figures

- `figures/gate_metrics.png` — 3-bar AUROC comparison
- `figures/roc_overlay.png` — ROC curves overlay
- `figures/weight_heatmap.png` — AUROC heatmap over (α, β) grid
- `figures/entropy_vs_consistency.png` — Scatter by correctness

### Results

- `code/results/h-m3_results.json` — Full results JSON

---

## Recommendations

1. **Proceed to H-M4** — SHOULD_WORK gate allows continuation
2. **Rerun with larger N:** If fusion improvement is critical, regenerate h-m2 with N≥500
3. **Document limitation:** Fusion benefit inconclusive at current sample size

---

## Code Validation

| Check | Status |
|-------|--------|
| Code executes without error | ✓ PASS |
| All modules implemented | ✓ PASS |
| Results JSON generated | ✓ PASS |
| All 4 figures generated | ✓ PASS |
| Grid search completed | ✓ PASS |
| Bootstrap CI computed | ✓ PASS |

---

## Conclusion

H-M3 implementation is complete and validated. Gate result is FAIL but this is expected at PoC scale (N=20). The SHOULD_WORK gate allows proceeding to H-M4. Fusion benefit should be retested with larger sample in future work.
