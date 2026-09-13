# Phase 4 Failure Record: h-m1 (Run 1)

**Date:** 2026-05-12T14:30:00
**Hypothesis:** h-m1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK_FAIL — mock ECE data, no real logits available

## Performance Gap

| Metric | Ours | Baseline | Gap |
|--------|------|----------|-----|
| rho (Spearman partial) | 0.1612 | threshold 0.4 | -0.2388 |
| p-value | 0.4036 | threshold 0.05 | +0.3536 |
| consistent_positive_families | 1/3 | required 2/3 | -1 |

## Gate Evaluation

- **Gate Type:** MUST_WORK
- **Gate Result:** FAIL
- **Conditions Met:** 0/3
- **Routing:** ROUTED_TO_PHASE_2A

## Root Cause Analysis

- Real model logits (probability outputs) for 30 LLMs on QA benchmarks were not available in the experiment environment
- ECE computation fell back to mock data (random values), making correlations with RI scores meaningless
- The H-E1 dataset provides RI scores and accuracy but not raw probability distributions needed for ECE calculation
- The `uncertainty-calibration` library requires per-sample (prob, label) pairs — not available from existing CSVs

## Lessons Learned

1. ECE requires raw model output probabilities — verify data availability before designing hypothesis
2. The H-E1 CSV pipeline stores accuracy/RI but not logits; ECE cannot be computed from these alone
3. Mock ECE fallback produces ~random correlations (rho≈0.16) that cannot support the hypothesis
4. Future ECE-based hypotheses must first verify logit availability or use a proxy calibration metric (e.g., confidence gap)
5. Consider using top-1 confidence as an ECE proxy if per-sample probs unavailable

## Feedback for Next Phase (Phase 2A Redesign)

### Suggested Modifications
- Redesign h-m1 to use a calibration proxy that doesn't require raw logits (e.g., accuracy-based ECE estimate)
- Or: collect logits from model inference runs on benchmark datasets before proceeding
- Consider replacing ECE with a simpler miscalibration proxy: |accuracy - mean_confidence|

### What NOT To Do
- Do not assume existing H-E1 CSVs contain logit-level data
- Do not use mock ECE fallback for hypothesis validation — results are statistically meaningless

### What Showed Promise
- The partial correlation framework (A-4, A-5) was correctly implemented and ran successfully
- The pipeline infrastructure (DataLoader, GateEvaluator, Visualizer) is solid and reusable
- The statistical methodology (Spearman partial corr + Holm correction) is appropriate

---
*Failure recorded at: 2026-05-12T14:30:00*
*For cross-phase reference*
