# Limitation Record: h-m1 (Run 1)

**Date:** 2026-08-09T23:25:00Z
**Hypothesis:** h-m1
**Run:** 1
**Gate Type:** MUST_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (limitation noted, not blocked)

## Limitation Details

3/4 geometry metrics showed significant difference between contrastive and reconstruction training. Alpha (power-law exponent) failed statistical significance (p = 0.5547). Core hypothesis partially supported.

## Failed Checks

- alpha: p = 0.5547 (not significant at p < 0.05)

## Partial Results

| Metric | Value |
|--------|-------|
| r_eff | p < 0.05, d = -6.2 |
| PR | p < 0.05, d = -11.8 |
| d_MLE | p < 0.05, d = -18.4 |
| alpha | p = 0.5547 (FAILED) |

## Experiment Summary

Contrastive training induces lower effective dimensionality (r_eff, PR, d_MLE all significantly lower) compared to reconstruction baseline. Power-law exponent (alpha) does not differ significantly - both training regimes produce similar spectral decay patterns.

## Context

This limitation was recorded but **did not block the pipeline**.
Strong support for 3/4 mechanism metrics. Alpha metric failure suggests power-law structure is not the distinguishing geometric feature.

Future research attempts should consider:
1. Alpha may not be a relevant discriminator for contrastive vs reconstruction
2. Focus on effective dimensionality metrics (r_eff, PR, d_MLE) which showed large effect sizes
3. Consider dropping alpha from mechanism hypothesis or investigating why it doesn't differ

---
*Limitation recorded at: 2026-08-09T23:25:00Z*
*For cross-phase reference*
