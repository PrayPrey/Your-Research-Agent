# Adversarial Review Round 2

## R1 Issue Resolution Check

| Issue | Status | Evidence |
|-------|--------|----------|
| Semantic entropy limitation | FIXED | "We compare against raw token entropy, not semantic entropy (Kuhn et al., 2023), which clusters responses by meaning before computing entropy and achieves higher AUROC (0.75-0.85). A direct comparison with semantic entropy remains future work." (Limitations, lines 259-261) |
| Inference cost limitation | FIXED | "Consistency requires 10 forward passes per question (for 10 samples), while entropy can be computed from a single pass. This 10x cost difference is critical for practitioners weighing deployment tradeoffs." (Limitations, lines 262-263) |

Both MAJOR issues from R1 have been properly addressed in the revised paper.

## Numerical Verification

| Claim | Paper Value | Source Value | Source File | Status |
|-------|-------------|--------------|-------------|--------|
| Consistency AUROC | 0.81 | 0.808 | h-m2/04_validation.md:46 | OK (rounded) |
| Entropy AUROC | 0.65 | 0.6454 | h-m1/04_validation.md:25 | OK (rounded) |
| Consistency Cohen's d | 1.19 | 1.188 | h-m2/04_validation.md:48 | OK (rounded) |
| Entropy Cohen's d | 0.47 | 0.47 | h-m1/04_validation.md:31 | OK |
| Correlation r | -0.54 | -0.543 | h-m2/04_validation.md:62 | OK (rounded) |
| H-M1 p-value | 0.0246 | 0.0246 | h-m1/04_validation.md:24 | OK |
| H-M2 p-value | 0.0083 | 0.0083 | h-m2/04_validation.md:16 | OK |
| Optimal alpha | 0.0 | 0.0 | h-m3/04_validation.md:49 | OK |
| Optimal beta | 0.1 | 0.1 | h-m3/04_validation.md:50 | OK |
| N for H-M1 | 100 | 100 | h-m1/04_validation.md:14 | OK |
| N for H-M2/H-M3 | 20 | 20 | h-m2/04_validation.md:28, h-m3/04_validation.md:14 | OK |
| "16 percentage points" | 0.81-0.65=0.16 | Mathematical derivation | N/A | OK |
| Fusion AUROC entropy-only | 0.675 | 0.6750 | h-m3/04_validation.md:42 | OK |
| Fusion AUROC consistency-only | 0.812 | 0.8125 | h-m3/04_validation.md:43 | OK |
| Fusion improvement | 0.000 | 0.0000 | h-m3/04_validation.md:56 | OK |

All numerical claims verified against source data. No discrepancies found.

## New Issues Found

None. No new FATAL or MAJOR issues identified.

The R1 fixes adequately address the two MAJOR issues (semantic entropy baseline fairness and inference cost). The paper now honestly acknowledges both limitations.

## Summary

| Persona | FATAL | MAJOR |
|---------|-------|-------|
| Accuracy Checker | 0 | 0 |
| Skeptical Expert | 0 | 0 |

**Recommendation:** Paper is ready for submission. All R1 MAJOR issues resolved, all numerical claims verified against source data.
