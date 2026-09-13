# H-M3 Limitation Record

**Hypothesis:** H-M3 — Categorical Tag Count Dose-Response (NB-2 Monotonic Gate)
**Gate:** SHOULD_WORK
**Result:** INFORMATIVE_NEGATIVE
**Date:** 2026-08-05

## Limitation

The categorical dose-response for tag count bins (0, 1-2, 3-5, 6+) is not uniformly graded on the OpenML corpus (N=5,217).

- Monotonic IRR ordering CONFIRMED: IRR(1-2)=1.127 < IRR(3-5)=1.128 < IRR(6+)=1.286
- Adjacent contrasts: only 1/3 passing Bonferroni (α=0.0167) — only 3-5 vs 6+ significant (p=5.54e-10)
- Root cause: bin "1-2" too sparse (N=73, 1.4% of corpus); IRR gap between 1-2 and 3-5 negligible (Δ=0.001)

## Scientific Constraint

The FAIR F1 discovery mechanism operates as binary threshold (0 vs ≥1 tag, H-E1 IRR=1.23) plus high-count amplification (6+ tags). Intermediate bins (1-2, 3-5) are statistically indistinguishable given the corpus distribution.

## Lessons for Future Hypotheses

- Categorical binning requires pre-verification of bin sample sizes; bins <100 lack Bonferroni contrast power
- Use quantile-based bins for equal sample sizes in future categorical dose-response designs
- H-E1→H-M2 continuous evidence chain is sufficient without categorical step confirmation
