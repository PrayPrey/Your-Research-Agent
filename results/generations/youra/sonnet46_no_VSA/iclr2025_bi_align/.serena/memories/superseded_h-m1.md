# Superseded Hypothesis Record

**Date:** 2026-07-30T00:25:00+00:00
**Hypothesis:** h-m1
**Superseded By:** h-m1-v2
**Status:** SUPERSEDED

## Supersede Reason

MUST_WORK gate FAIL: proportion_negative=0.305 ≤ 0.50. The hypothesis predicted >70% of base→instruct pairs would show ΔTruthfulQA MC2 < 0 (alignment tax). Instead, 69.5% of pairs show improvement. The direction is opposite to the hypothesis — RLHF/SFT reliably improves TruthfulQA on community models. Fundamental redesign needed. Routing to /phase2a-dialogue.

## Compatibility Assessment

| Factor | Score/Result |
|--------|--------------|
| Compatibility Score | 0.0 |
| Recommendation | SUPERSEDE |
| Reasoning | Direction of effect is reversed. InstructGPT improvement pattern applies to community models. MUST_WORK gate cannot be salvaged with parameter adjustment — the hypothesis framing itself is wrong. |

## Key Results

| Metric | Value |
|--------|-------|
| N pairs | 321 |
| proportion_negative | 0.305 (expected >0.70) |
| p_value (one-sided binomtest) | ~1.000 |
| mean_delta (instruct − base) | +3.406 TruthfulQA points |
| BCa 95% CI | [+2.589, +4.212] — entirely positive |
| Stratum-A mean_delta | +9.912 |
| Gate passed | False |

## Root Cause

TruthfulQA MC2 measures "would a truthful, calibrated expert answer like this?" RLHF/SFT makes models sound more authoritative and confident, which matches TruthfulQA's target distribution. The "alignment tax" hypothesis was based on the intuition that preference optimization suppresses hedging — but on TruthfulQA, confident answers score higher, not lower.

## What Was Preserved

- Data pipeline (H-E1 pairs.csv) is robust and reusable for h-m1-v2
- Sign test + BCa bootstrap implementation correct and validated
- Within-family matching methodology valid
- 321-pair dataset with clean TruthfulQA MC2 columns confirmed

## Recommendations for h-m1-v2 (Phase 2A-Dialogue)

1. Reframe hypothesis: investigate *which* instruct models lose TruthfulQA and why
2. Split by training methodology (RLHF vs SFT vs DPO)
3. Consider alternative truthfulness metrics less sensitive to confident phrasing
4. Investigate the 30.5% minority that DO show degradation — what characterizes them?

## Timeline

1. Original hypothesis: h-m1 (alignment tax direction)
2. FAIL result detected: proportion=0.305 opposite to predicted direction
3. LLM assessment: compatibility_score = 0.0
4. Decision: SUPERSEDE (fundamental framing error, not parameter issue)
5. New direction: h-m1-v2 (to be defined in /phase2a-dialogue)

---
*Superseded at: 2026-07-30T00:25:00+00:00*
