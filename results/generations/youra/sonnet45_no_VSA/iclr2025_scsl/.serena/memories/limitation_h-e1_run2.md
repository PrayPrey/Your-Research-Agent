# Limitation Record: h-e1 (Run 2)

**Date:** 2026-07-10T21:40:00+00:00
**Hypothesis:** h-e1
**Run:** 2
**Gate Type:** SHOULD_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

SAM+SWA compositional method failed to achieve the hypothesized ≥3 percentage point improvement in worst-group test accuracy over SAM-only on ColoredMNIST. The combination actually performed slightly worse than SAM alone, with SAM+SWA achieving 0.08% worst-group accuracy compared to SAM's 0.26%.

## Failed Checks

- Mean improvement ≥ 3.0%: Actual = -0.18% (FAIL)
- Statistical significance p < 0.05: Actual p-value = 0.8195 (FAIL)
- Effect size Cohen's d ≥ 0.5: Actual = -0.4609 (FAIL)
- 95% CI does not overlap zero: CI = [-0.0066, 0.0030] (FAIL)

## Partial Results

| Metric | Value |
|--------|-------|
| SAM+SWA worst-group accuracy | 0.0008 (0.08%) |
| SAM worst-group accuracy | 0.0026 (0.26%) |
| Mean difference | -0.0018 (-0.18pp) |
| p-value | 0.8195 |
| Cohen's d | -0.4609 |
| Seeds tested | 5 |
| Experiments run | 20 |

## Experiment Summary

The experiment successfully implemented and tested the SAM+SWA compositional method across 5 random seeds (42, 123, 456, 789, 1011) on ColoredMNIST with spurious color correlations (ρ=0.95 training, ρ=0.10 test). Four methods were compared: ERM baseline, SAM-only, SWA-only, and SAM+SWA compositional.

**Key Findings:**
1. SAM alone collapsed worst-group accuracy to near-zero (0.26% mean)
2. SWA alone maintained similar performance to ERM baseline (8.89% vs 8.44%)
3. SAM+SWA combination further reduced worst-group accuracy (0.08% mean)
4. The compositional method did not exhibit the hypothesized synergistic improvement

**Likely Causes:**
- SAM's sharpness minimization may be fundamentally incompatible with spurious correlation robustness on this task
- Weight averaging in SWA cannot recover from SAM's poor minority group performance
- The geometric mechanisms (flat minima + trajectory averaging) may not address the distributional shift problem

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded with this limitation noted and routed to EXPLORE for alternative approaches.

Future research attempts should consider:
1. The specific checks that failed (all gate criteria failed)
2. The limitation appears fundamental rather than circumstantial (SAM actively harms minority group performance)
3. Alternative approaches that avoid SAM's sharpness-awareness mechanism or use different robustness strategies

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0 (from Phase 5 PARTIAL or exploration),
  this limitation informs brainstorming to avoid SAM-based compositional approaches for spurious correlation robustness
- **Phase 2A:** This failure pattern suggests investigating mechanistic hypotheses about why SAM fails on spurious correlations
- **Phase 6 Discussion:** Limitation is included in paper's Limitations section or negative results discussion

---
*Limitation recorded at: 2026-07-10T21:40:00+00:00*
*For cross-phase reference*
