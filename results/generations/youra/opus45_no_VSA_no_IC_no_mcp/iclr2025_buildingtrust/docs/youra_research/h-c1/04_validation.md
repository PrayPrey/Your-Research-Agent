# Phase 4 Validation Report: h-c1

**Hypothesis:** The truthfulness-robustness correlation pattern holds separately for base models and instruction-tuned models, with potentially different effect sizes.

**Type:** CONDITION
**Gate Type:** SHOULD_WORK
**Date:** 2026-08-28

---

## 1. Experiment Summary

### Objective
Test whether the TruthfulQA-AdvGLUE correlation established in h-e1 (r=0.8028) generalizes across model types or is an artifact of instruction tuning.

### Methodology
- Stratified partial correlation analysis
- Control variable: log(model_params)
- Bootstrap CI (1000 iterations)
- Split: base models (14) vs instruction-tuned (6)

---

## 2. Results

### Base Models (n=14)
| Metric | Value |
|--------|-------|
| Partial r | 0.8028 |
| p-value | 0.00055 |
| 95% CI | [0.082, 0.969] |
| Gate | PASSED |

### Instruction-Tuned Models (n=6)
| Metric | Value |
|--------|-------|
| Partial r | 0.3630 |
| p-value | 0.4794 |
| 95% CI | N/A (insufficient bootstrap) |
| Gate | FAILED |

### Pattern Consistency
- Both groups show positive correlation (same sign)
- Base models: strong effect (r > 0.8)
- Instruction-tuned: moderate effect but not significant

---

## 3. Gate Evaluation

**GATE RESULT: NOT SATISFIED**

| Criterion | Base | Instruction-Tuned | Combined |
|-----------|------|-------------------|----------|
| r > 0.2 | ✓ (0.803) | ✓ (0.363) | ✓ |
| p < 0.05 | ✓ (0.0005) | ✗ (0.479) | ✗ |
| Overall | PASS | FAIL | FAIL |

**Reason:** Instruction-tuned group failed significance threshold (p=0.479 > 0.05) due to small sample size (n=6).

---

## 4. Interpretation

### Findings
1. Base models show strong, significant correlation (consistent with h-e1)
2. Instruction-tuned models show moderate positive trend but insufficient statistical power
3. Pattern direction is consistent (both positive)

### Limitations
- Instruction-tuned sample too small for reliable inference
- Synthetic data used for instruction-tuned models (PoC mode)
- Need minimum 10+ models per group for robust CI

### Recommendations
1. Collect real evaluation data for instruction-tuned models
2. Expand instruction-tuned sample to 10+ models
3. Consider this a PARTIAL success (base models confirm, instruction-tuned inconclusive)

---

## 5. Artifacts Generated

| File | Description |
|------|-------------|
| `code/run.py` | Main experiment orchestrator |
| `code/config.py` | Model definitions and thresholds |
| `code/data_loader.py` | Data loading and merging |
| `code/stratified_analysis.py` | Partial correlation per group |
| `code/visualize.py` | Figure generation |
| `code/results/stratified_results.json` | Raw results |
| `code/figures/stratified_scatter.png` | Two-panel scatter plot |
| `code/figures/effect_comparison.png` | Effect size comparison |

---

## 6. Gate Decision

**SHOULD_WORK Gate:** NOT SATISFIED

Since this is a SHOULD_WORK gate, the pipeline continues with limitations noted:
- Base model correlation confirmed
- Instruction-tuned correlation inconclusive (not failed, just underpowered)

**Route:** Continue to Phase 5 (Baseline Comparison) with limitation note

---

*Generated: 2026-08-28 | Phase 4 Complete*
