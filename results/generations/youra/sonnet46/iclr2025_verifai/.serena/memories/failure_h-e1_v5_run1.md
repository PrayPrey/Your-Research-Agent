# H-E1_v5 Phase 4 Failure Record

## Hypothesis
H-E1_v5 (EXISTENCE): gamma_p = D_p^w / E[D_p^w] is well-defined and non-degenerate for ≥4/5 model-benchmark pairs.

## Gate Result
FAIL (MUST_WORK) — 0/5 pairs passing

## Failure Mode
**Metric degeneracy**: gamma_p collapses to constant 1.25 for ALL valid problems.
- IQR(gamma_p) ≈ 4.4e-16 (machine zero) for all 5 pairs
- valid_fraction below threshold for all pairs (range: 0.59–0.89, threshold: >0.95)

## Root Cause
The formula `D_p^w / E[D_p^w]` is analytically constant by construction:
- D_p^w = weighted mean pairwise Hamming diversity
- E[D_p^w] = expected value of D_p^w under Bernoulli null (same weights)
- The ratio D_p^w / E[D_p^w] converges to 1.25 by algebraic identity for k=5, C(5,2)=10 pairs
- Normalizing by the expected value of the same statistic makes it constant → zero variance across problems

## Additional Failure
- Many problems have all-identical solutions → w_t=0 for all tests → E[D_p^w]=0 → marked invalid
- With pass@1=0.16–0.44 across models, single solution cluster common → invalid
- valid_fraction: 0.59–0.89 (best pair: 0.890), required >0.95

## Lessons Learned
1. **Ratio metrics normalizing by own expected value are analytically constant** — avoid this pattern
2. B_p matrix k=5 has limited diversity at extreme pass rates (all-pass or all-fail)
3. Need metric capturing actual inter-problem variability, not normalized-to-expectation ratios
4. EvalPlus JSONL archives may have limited solution diversity if sampling was deterministic

## Routing
ROUTED_TO_PHASE_0 for hypothesis redesign

## Cascade
- h-e2_v5: CASCADE_FAILED
- h-m1_v5: CASCADE_FAILED

## Date
2026-03-19
