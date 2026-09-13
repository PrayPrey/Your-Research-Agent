# Hypothesis Completion Snapshot: h-e1

**Date:** 2026-03-16T18:15:00Z
**Pipeline:** YouRA | Spurious Correlations & Shortcut Learning (20260315_scsl)
**Hypothesis:** h-e1
**Statement:** Under ERM+SGD training on Waterbirds and CelebA, minority-group samples produce disproportionately large gradient norms (>=2x majority) and lambda_1 increases monotonically (progressive sharpening), instantiating the opposing-signal heavy-tailed gradient regime of Rosenfeld & Risteski (2023).

**Final Status:** COMPLETED (partial)
**Gate Result:** PARTIAL (MUST_WORK)
**Reflection Outcome:** SELF_MODIFY → h-e1-v2

## Key Results

- gradient_norm_ratio: 12.20 (epoch5) ✅ strongly confirmed (>>2x)
- lambda1_trajectory: {5: 704.33, 10: 669.66, 20: 498.93} — EOS dynamics (decreasing)
- lambda1_monotonic: False ❌
- oscillation_index: NaN (not computed — implementation gap)

## Next Hypothesis

h-e1-v2 is READY with relaxed lambda1 criterion (EOS threshold instead of monotonic) and oscillation_index fix.
