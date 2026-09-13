# Phase 4 Failure Record: h-e1 (Run 1)

**Date:** 2026-08-05T21:15:00
**Hypothesis:** h-e1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK_GATE_FAIL — Existence proof not established

## Gate Result

| Gate | Type | Result |
|------|------|--------|
| P0a — H(W₀) non-uniformity | MUST_WORK | FAIL (0/3 models) |
| P0b — PARA cross-task stability | MUST_WORK | PENDING (training in progress, gate already FAIL) |
| **Overall** | MUST_WORK | **FAIL** |

## Performance Gap

| Metric | Observed | Required | Gap |
|--------|----------|----------|-----|
| P0a CV — DeBERTa | 0.0323 | > 0.1 | -0.068 |
| P0a CV — BERT | 0.0403 | > 0.1 | -0.060 |
| P0a CV — ViT | 0.0752 | > 0.1 | -0.025 |
| P0a Levene p — ViT | 0.0038 | < 0.05 | ✓ (only Levene passes for ViT) |
| Models passing P0a | 0/3 | ≥ 2/3 | -2 |

## Root Cause Analysis

- Spectral entropy H(W₀) for large pretrained transformers is inherently concentrated near log(min(d_in, d_out)). The CV metric is mean-sensitive — values cluster near this upper bound (~5.9), making CV = std/mean small even when real differences exist.
- ViT shows the strongest signal (CV=0.075, Levene p=0.0038 for positional thirds), confirming depth-dependent specialization exists but below the CV>0.1 threshold.
- Intermediate/FFN matrices have higher entropy (DeBERTa intermediate mean=6.20) than attention Q/K/V (mean=5.89), confirming layer-type specialization, but overall distribution CV remains low.
- The CV > 0.1 criterion was likely calibrated on rank diversity (from PARA oracle), not spectral entropy, which varies less as a metric.

## Lessons Learned

1. Spectral entropy CV for pretrained transformers is empirically bounded ~0.03–0.08; CV > 0.1 may require a different non-uniformity metric (e.g., rank diversity, effective rank ratio).
2. ViT shows stronger layer specialization than NLP models due to early-layer concentration vs late-layer diffusion patterns; it comes closest to passing (CV=0.075).
3. Grouping by layer type (attention vs FFN) for the Levene test reveals more structure than positional thirds for NLP models (BERT Levene p=0.0001 with type grouping).
4. The MUST_WORK gate correctly identified that the static predictor premise (H(W₀) → rank) lacks sufficient empirical basis in the tested form.

## Feedback for Future Research

### Suggested Modifications
- Use effective rank or participation ratio instead of spectral entropy as the non-uniformity metric
- Lower CV threshold to 0.05 to match empirically observed variation
- Test PARA rank vector non-uniformity directly (rank diversity) as the existence criterion rather than entropy

### What NOT To Do
- Do not expect spectral entropy CV > 0.1 from standard pretrained checkpoints — the metric is too smooth
- Do not rely on positional thirds Levene grouping for NLP models; use layer-type grouping (attention vs FFN)

### What Showed Promise
- ViT base/16 shows clear depth-dependent entropy variation (early layers 4.27, late layers 6.44)
- BERT Levene test passes with type-based grouping (p=0.0001), suggesting real but subtle layer specialization
- P0b (PARA stability) was not completed but the training infrastructure is solid (real GLUE data, 5×H100)

---
*Failure recorded at: 2026-08-05T21:15:00*
*For cross-phase reference*
