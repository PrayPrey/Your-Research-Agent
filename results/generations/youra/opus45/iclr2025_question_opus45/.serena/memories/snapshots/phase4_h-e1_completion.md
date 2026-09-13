# Hypothesis Completion Snapshot: h-e1

**Date:** 2026-03-26T13:53:47Z
**Hypothesis:** h-e1
**Type:** EXISTENCE (Foundation)
**Final Status:** FAILED
**Gate Result:** FAIL

## Hypothesis Statement

Under autoregressive transformer LLMs processing factual QA questions, whitened hidden state dispersion at layers 60-80% depth will show Spearman correlation rho >= 0.5 with semantic entropy, because hidden states encode semantic representations and uncertainty manifests as geometric spread after removing anisotropic artifacts.

## Results

- **Validation:** FAIL
- **Gate Type:** MUST_WORK
- **Peak Spearman rho:** 0.188 (layer 29)
- **Threshold:** 0.5
- **Bootstrap 95% CI:** [0.117, 0.248]

## Reflection

- **Reflection Outcome:** ROUTED_TO_PHASE_0
- **Meaningful Findings:** None - fundamental assumption failure
- **Lessons Learned:**
  - ZCA whitening improves correlations but cannot create relationships that don't exist
  - Hidden state geometry may not directly encode uncertainty as hypothesized
  - Peak correlation at 91% depth, not 60-80% as predicted
  - Need fundamentally different approach for single-pass uncertainty quantification

## Cascade Effects

- h-m1: BLOCKED (prerequisite failed)
- h-m2: BLOCKED (cascade from h-e1)
- h-m3: BLOCKED (cascade from h-e1)
- h-m4: BLOCKED (cascade from h-e1)

## Next Action

Route to Phase 0 for new research direction. The commitment layer / crystallization hypothesis framework is invalidated.

---
*Per-hypothesis snapshot for Phase 2A reference*
