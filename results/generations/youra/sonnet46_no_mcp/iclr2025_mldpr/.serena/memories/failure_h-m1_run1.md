# Phase 4 Failure Record: h-m1 (Run 1)

**Date:** 2026-05-04T07:30:00Z
**Hypothesis:** h-m1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** WRONG_DIRECTION — positive correlation observed (mechanism direction opposite to hypothesis)

## Hypothesis Summary

H-M1 hypothesized that benchmark publication frequency (number of papers citing a benchmark per year) negatively correlates with benchmark saturation rate (Spearman rho < -0.15, p < 0.10). The hypothesis predicted that saturating benchmarks attract fewer new publications over time.

## Performance Gap

| Metric | Observed | Target | Gap |
|--------|----------|--------|-----|
| Spearman rho | +0.0960 | < -0.15 | +0.246 (wrong direction) |
| p_one_sided | 0.9990 | < 0.10 | +0.899 |
| N | 1031 | — | — |

## Gate Evaluation

- **Gate Type:** MUST_WORK
- **Gate Satisfied:** False
- **Failure Reason:** rho=+0.096 is positive (wrong direction). Target was rho < -0.15 (negative correlation).

## Root Cause Analysis

- The overall correlation is positive (+0.0960), meaning popular benchmarks (high publication frequency) are NOT saturating faster — they are actually staying unsaturated longer or attracting more papers despite saturation.
- Vision domain (N=764) drives the positive signal: large vision benchmarks remain active long after high performance is achieved.
- Audio domain (N=16) shows rho=-0.425 (near-significant, in expected direction) but N is too small to dominate.
- The mechanism assumption — that saturation reduces research interest — may be reversed: saturated benchmarks may *attract* more papers as researchers try to improve SOTA.

## Domain Stratification Results

- Vision (N=764): positive rho (drives overall positive signal)
- Audio (N=16): rho=-0.425 (supports hypothesis but N insufficient)
- Other domains: mixed signal

## Lessons Learned

1. The direction of the saturation-publication relationship is likely confounded by domain size and benchmark prestige — large vision benchmarks remain active even when saturated.
2. A simple cross-benchmark Spearman correlation conflates domain effects. Controlling for domain or normalizing within domain is needed.
3. Audio domain shows the expected signal but with N=16 is underpowered. Future hypotheses should focus on audio or use within-domain normalization.
4. The MUST_WORK gate was not satisfied — this is a fundamental directional failure, not an implementation bug. The code ran correctly; the hypothesis was wrong.
5. Alternative framing: instead of "publication frequency vs. saturation rate," consider "within-domain rank of saturation rate vs. within-domain rank of publication frequency" to remove domain size confounds.

## Feedback for Next Phase (Phase 0 Redesign)

### Suggested Modifications
- Reformulate hypothesis within domains (control for domain size)
- Test within-domain normalized correlation instead of raw cross-benchmark
- Focus on audio/NLP domains where N is reasonable and signal direction matches expectation
- Consider time-lagged analysis: does saturation at time T predict publication drop at T+1?

### What NOT To Do
- Do not use raw cross-benchmark Spearman without domain control
- Do not assume vision benchmark behavior generalizes to other domains
- Do not set rho < -0.15 as target without accounting for domain confounds

### What Showed Promise
- Audio domain (N=16): rho=-0.425 — mechanism may be valid in audio
- The data pipeline and analysis code work correctly
- H-E1 intermediate outputs (eligible_benchmarks.csv, N=1031) are reusable

## Routing Decision

**Route to:** Phase 0 for hypothesis redesign
**Reason:** Gate MUST_WORK not satisfied. Positive correlation observed — mechanism direction opposite to hypothesis. Fundamental redesign required.

---
*Failure recorded at: 2026-05-04T07:30:00Z*
*For cross-phase reference*
*Written by: Phase 4 completion step (h-m1, run 1)*
