# H-E1 Hypothesis Failure Record

**Hypothesis:** Different data curation strategies produce statistically distinguishable capability-normalized performance profiles

**Type:** EXISTENCE
**Gate:** MUST_WORK
**Result:** FAIL

## Gate Evaluation

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| p-value | 0.3543 | < 0.05 | FAIL |
| η² | 0.6544 | > 0.14 | PASS |

## Analysis

The MANOVA analysis showed a large effect size (η² = 0.654) but failed to reach statistical significance (p = 0.354). This suggests:

1. **Effect likely exists** - Strong effect size indicates curation strategies do produce different profiles
2. **Insufficient statistical power** - PoC scale (50 training steps, WikiText-103 substitute) was inadequate
3. **High variance** - 3 seeds per condition may be insufficient for MANOVA

## PoC Limitations

- Training: 50 steps vs 5000+ required
- Dataset: WikiText-103 substitute vs SlimPajama-627B
- Model: 152M params vs 1.3B specified
- Evaluation: Quick proxy vs full lm-evaluation-harness

## Recommendation

Before abandoning hypothesis, consider full-scale experiment with:
- Full SlimPajama-627B dataset access
- 5000+ training steps per model
- Full benchmark evaluation
- 5 seeds per condition for better power

## Files

- Validation report: `h-e1/04_validation.md`
- Results: `h-e1/code/outputs/experiment_results.json`
- Figures: `h-e1/figures/`

**Date:** 2026-08-10
