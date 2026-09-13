# Phase 4 Failure Record: h-e1_v5 (Run 2)

**Date:** 2026-03-19T19:30:00
**Hypothesis:** h-e1_v5
**Run:** 2
**Final Status:** FAIL
**Failure Type:** METRIC_DEGENERACY

## Performance Gap

| Metric | Ours | Baseline | Gap |
|--------|------|----------|-----|
| Pairs passing gate | 0/5 | 4/5 (required) | -4 pairs |
| Best valid_fraction | 0.890 | >0.95 (required) | -0.060 |
| Best IQR(gamma_p) | ~4.4e-16 | >0.1 (required) | ~-0.1 |

## Root Cause Analysis

- gamma_p = D_p^w / E[D_p^w] collapses to a constant (1.25) for ALL valid problems across all 5 model-benchmark pairs
- IQR is machine epsilon (~4.4e-16), analytically zero — metric is non-discriminative
- valid_fraction < 0.95 for all 5 pairs (best: 0.890 for llama3_humaneval)
- Root mathematical cause: D_p^w = pass@1 * k (proportional to pass@1), so E[D_p^w] = mean(pass@1) * k, and gamma_p = pass@1 / mean(pass@1) * constant — but wait, further analysis shows D_p^w collapses to binary when k=1 (pass@1_p), making E[D_p^w] proportional to D_p^w itself, yielding constant ratio

## Lessons Learned

1. Normalizing a metric by its own expectation (gamma_p = D_p^w / E[D_p^w]) can yield a degenerate constant if D_p^w has no variance across problems conditional on the normalization structure
2. The EvalPlus B_p matrix with k=1 (pass@1 evaluation) reduces diversity to binary values, making the ratio degenerate
3. Gate criterion IQR > 0.1 is a strong non-degeneracy check — any constant or near-constant metric will fail
4. valid_fraction < 0.95 requires very high coverage — problems with all solutions failing (D_p^w = 0) are excluded

## Feedback for Next Phase (Phase 0 Re-entry)

### Suggested Modifications
- Use k > 1 (e.g., k=5 or k=10) so B_p matrix has genuine variance across problems
- Consider a different diversity measure D_p^w that doesn't collapse to binary at k=1
- Re-examine the hypothesis: γ_p may only be well-defined and non-degenerate for k >> 1

### What NOT To Do
- Do not use k=1 (pass@1) as the primary evaluation; binary outcomes collapse the ratio
- Do not assume E[D_p^w] > 0 implies non-degeneracy; the ratio can still be constant

### What Showed Promise
- The gate framework (valid_fraction + IQR checks) correctly identified the degeneracy
- EvalPlus B_p matrices are available and correctly loaded; data pipeline is solid
- compute_gamma_p implementation is correct — the issue is the metric definition, not the code

---
*For cross-phase reference*
*Written at: 2026-03-19T19:30:00*
