# H-M2 Reflection Report

**Date:** 2026-03-17
**Hypothesis:** h-m2 — DPO vs SFT Logit Delta Variance in Low-Margin Regions
**Gate Type:** SHOULD_WORK
**Gate Result:** NULL RESULT (FAIL)
**Reflection Outcome:** LIMITATION_RECORDED

---

## Experiment Results Summary

| Dataset | DPO Q1 var | SFT Q1 var | Variance Ratio | p (one-tailed) | Cohen's d |
|---------|-----------|-----------|----------------|----------------|-----------|
| MMLU | 0.7073 | 0.2229 | 1.18 | 1.000 | -0.490 |
| TruthfulQA | 0.7490 | 0.4124 | 0.678 | 1.000 | -1.536 |
| ARC | 1.9522 | 0.2720 | 2.386 | 0.992 | -0.225 |

**Gate criterion:** p < 0.05 (one-tailed, DPO > SFT mean delta_var in Q1) on ≥ 2/3 datasets

---

## Root Cause Analysis

**What the data shows:**
1. The per-quintile variance of delta_var (`quintile_variances[0]`) — i.e., the spread of DPO's responses in Q1 — IS higher than SFT on MMLU and ARC (ratios 1.18 and 2.39). This partial supports the hypothesis direction for distribution spread.
2. However, the **mean** per-item delta_var in Q1 is **lower for DPO than SFT** (negative Cohen's d for all datasets). The t-test on means finds the opposite direction.
3. The t-test correctly identifies: in low-margin regions, SFT makes larger average logit shifts per item than DPO.

**Interpretation:**
- DPO in Q1: low mean shift but high spread (some items shift a lot, most shift little)
- SFT in Q1: higher mean shift but more uniform (consistently larger shifts)
- The hypothesis was operationalized as "higher variance of delta_var" but tested as "higher mean delta_var"

**Root cause:** The gate criterion (one-tailed t-test on means) does not match the hypothesis intent (higher variance/spread of responses). If the gate were based on `quintile_variances[0]` (variance-of-delta_var), MMLU and ARC would pass.

---

## Self-Recovery Assessment

**Can improvement be achieved through modification?**

Potential modifications:
1. Change gate criterion to `quintile_variances[0]` ratio test (DPO/SFT > 1.5 on ≥ 2/3 datasets) — would yield PASS on MMLU and ARC
2. Reframe hypothesis: "DPO exhibits higher dispersion (not higher mean) of logit delta in low-margin regions"

**Decision:** LIMITATION_RECORDED (no retry)

Rationale: The current null result on mean delta_var is scientifically valid and meaningful. The finding that SFT has higher *mean* logit shift in Q1 while DPO has higher *spread* is itself an interesting finding. Retrying with a modified gate would be methodologically questionable (post-hoc hypothesis adjustment). The SHOULD_WORK gate null result is acceptable and documented.

---

## Lessons Learned

1. **Variance vs. mean distinction matters:** The hypothesis "higher variance in low-margin regions" can mean either (a) higher per-item variance (mean of delta_var) or (b) higher spread of per-item variances (variance of delta_var). Operationalization must be specified precisely.

2. **OLS residuals are zero-mean:** When using OLS residualization for KL control, the residuals have mean zero by construction — t-tests on residuals compare means (always ≈ 0 for both groups). Use raw delta_var values for mean-comparison tests; use residuals only for variance estimation.

3. **DPO behavioral signature:** DPO shows a clear quintile trend (Q1 var=0.71 → Q5 var=3.38 on MMLU) while SFT is flat (~0.22-0.29). This suggests DPO's alignment has stronger confidence-dependent effects: high-confidence items see larger adjustments, while low-confidence items see smaller but more variable adjustments.

4. **SHOULD_WORK null result is valid:** The pipeline continues without modification. This null result provides useful contrast with h-m1 findings.

---

## Gate Processing Result

- **Gate:** SHOULD_WORK (null result acceptable)
- **Pipeline Action:** Continue to Phase 5
- **Status:** LIMITATION_RECORDED
- **Limitation:** H-M2 null result — DPO does not have higher mean logit delta variance in Q1 vs SFT. Direction reversed: SFT shows higher mean Q1 delta_var. DPO shows higher spread but not higher mean. Documented for Phase 6 paper.
