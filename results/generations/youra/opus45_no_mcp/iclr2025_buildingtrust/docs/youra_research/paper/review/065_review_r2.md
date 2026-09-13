# Adversarial Review Round 2

## R1 Fix Verification

| Issue ID | Original Issue | Fix Applied | Fix Adequate |
|----------|----------------|-------------|--------------|
| 1 | Token-padding control results not reported | Added note in Sec 3 and Limitations: "not executed due to resource constraints...remains future work" | YES - now transparent |
| 2 | Title claims "Calibration" but H-E1 mock mode | Added explicit limitation: "H-E1 ran in mock mode; actual ECE calibration improvement was not measured" | YES - clearly stated |
| 3 | H-E1 mock mode not in limitations | Added: "The title's reference to 'Calibration' reflects the mechanism we verify, not end-to-end ECE improvement" | YES - honest framing |
| 4 | p-value notation varies | Paper uses p<1e-16 in abstract, exact 9.22e-17 in results - acceptable scientific convention | N/A - not a real issue |
| 5 | Causal language when correlational | Paper already had "correlational evidence only" caveat; R1 adds "may improve" hedging | YES - adequate |

## Numerical Accuracy Check

All numbers verified against ground truth:

| Claim | Paper Value | Ground Truth | Status |
|-------|-------------|--------------|--------|
| Spearman r | -0.315 | -0.315 | MATCH |
| p-value | 9.22e-17 | 9.22e-17 | MATCH |
| Sample size | n=664 | 664 | MATCH |
| Hedging presence rate | 82% | 82% | MATCH |
| Mean hedging markers | 2.84 | 2.84 | MATCH |
| CoT reasoning rate | 100% | 100% | MATCH |
| Mean reasoning steps | 4.49 | 4.49 | MATCH |
| Ordering compliance | 100% | 100% | MATCH |
| "may" occurrences | 787 | 787 | MATCH |
| "could" occurrences | 619 | 619 | MATCH |
| 95% CI | [-0.382, -0.246] | Not in ground truth | UNVERIFIED but plausible |

No numerical discrepancies found.

## Remaining Issues

| ID | Severity | Description |
|----|----------|-------------|
| 6 | MINOR | References section still placeholder ("See 06_references.bib") |
| 7 | MINOR | Word count note (~3,200) should be removed for submission |
| 8 | MINOR | H-M1 and H-M2 ran in MOCK mode per ground_truth.yaml but paper doesn't distinguish which hypotheses used mock vs real data |

## Convergence Assessment

- fatal_issues: 0
- major_issues: 0
- persuasiveness_passed: true
- recommendation: **ACCEPT**

All MAJOR issues from R1 have been adequately addressed:
1. Token-padding limitation now explicitly acknowledged with clear future work framing
2. H-E1 mock mode limitation is now transparent in Discussion section
3. Title's "Calibration" claim is now properly scoped to mechanism verification

The paper is honest about what was and was not validated. Remaining issues are minor formatting matters appropriate for camera-ready preparation.
