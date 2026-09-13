# Adversary Review Round 2 - Numerical Verification

## Ground Truth Cross-Reference

| Source File | Key Values |
|-------------|------------|
| h-e1/04_validation.md | Completion=100%, CV_PR mean=0.0116, std=0.0059, range=[0.0014, 0.0326], n=100 |
| h-e2/04_validation.md | r=+0.6065, p=9.24e-11, Spearman=+0.6368 (p=5.26e-12), CI=[0.506,0.703], n=94 |
| 065_ground_truth.yaml | All above values confirmed; n_seeds=20, svd_rank=50, oversampling=10 |

## Numerical Verification Table

| Claim | Paper Location | Paper Value | Ground Truth | Status |
|-------|---------------|-------------|--------------|--------|
| Pearson r | Abstract, S5.2 | +0.61 (rounded), +0.6065 | +0.6065 | MATCH |
| p-value | Abstract, S5.2 | p < 10^{-10}, 9.24e-11 | 9.24e-11 | MATCH |
| 95% CI | S5.2 | [0.506, 0.703] | [0.506, 0.703] | MATCH |
| Sample size | S5.2 | 94 | 94 | MATCH |
| Spearman rho | S5.2 | +0.6368 | +0.6368 | MATCH |
| CV_PR mean | S5.1 | 0.0116 | 0.0116 | MATCH |
| CV_PR range | S5.1 | [0.0014, 0.0326] | [0.0014, 0.0326] | MATCH |
| Completion rate | S5.1 | 100% | 100% | MATCH |
| Models processed | S5.1 | 100 | 100 | MATCH |
| n_seeds | S3, S4 | 20 | 20 | MATCH |
| SVD rank | S3, S4 | 50 | 50 | MATCH |
| Oversampling | S3, S4 | 10 | 10 | MATCH |

## Mathematical Validity Analysis

### Statistical Plausibility

**CI Check for r=0.6065, n=94:**
Using Fisher z-transform: z = 0.5 * ln((1+r)/(1-r)) = 0.703
SE(z) = 1/sqrt(n-3) = 1/sqrt(91) = 0.1048
95% CI for z: [0.703 - 1.96*0.1048, 0.703 + 1.96*0.1048] = [0.498, 0.908]
Back-transform: [tanh(0.498), tanh(0.908)] = [0.460, 0.721]

Paper reports [0.506, 0.703]. Slight difference suggests bootstrap CI (valid alternative). Both intervals:
- Exclude zero
- Exclude negative values
- Contain r=0.6065

**Verdict: PLAUSIBLE** - Bootstrap CI is a valid method; values are consistent.

**Spearman vs Pearson:**
Spearman rho = +0.6368 vs Pearson r = +0.6065. Spearman slightly higher suggests mild positive skew or outliers pulling Pearson down. This is a normal pattern. **PLAUSIBLE**.

### Methodology Consistency

All hyperparameters consistent throughout:
- Section 3: n_seeds=20, rank=50, oversampling=10
- Section 4: Same values in table
- Ground truth YAML: Same values
- No contradictions found.

## Issues Found

### FATAL Issues
None.

### MAJOR Issues
None.

### MINOR Issues

1. **Abstract rounding**: States "r = +0.61" (rounded) and "p < 10^{-10}" (conservative bound). Both are correct representations of exact values. No issue.

2. **CI method not explicitly stated**: Paper uses bootstrap CI (implied by "via bootstrap") but doesn't detail bootstrap parameters. Acceptable for a methodology paper.

## Baseline Fairness Assessment

This is a **falsification study**, not a benchmark comparison:
- Hypothesis predicted r < -0.3
- Observed r = +0.61
- Study correctly concludes hypothesis is falsified

No unfair comparisons detected. The paper:
- Does not claim CV_PR is better than other metrics
- Acknowledges confounding as limitation
- Frames findings as negative result requiring further investigation

**Verdict: FAIR**

## Summary

- FATAL: 0
- MAJOR: 0
- MINOR: 0 (informational notes only)
- Numerical verification: **PASS** (all 12 values match exactly)
- Mathematical validity: **PASS** (CI plausible, Spearman/Pearson relationship normal)
- Recommendation: **PROCEED TO R3** (Structure/Claims verification)
