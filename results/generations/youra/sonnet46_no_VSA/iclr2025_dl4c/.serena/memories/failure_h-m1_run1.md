# Phase 4 Failure Record: h-m1 (Run 1)

**Date:** 2026-08-02T14:30:00+00:00
**Hypothesis:** h-m1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK_FAIL
**Gate Type:** MUST_WORK
**Reflection Outcome:** ROUTED_TO_PHASE_0

## Hypothesis Statement

Under 1-epoch SFT of DeepSeek-Coder-1.3B on deduplicated LeetCodeDataset with SFTConfig(shuffle=False) and easy-to-hard presort, inter-batch gradient variance in the first 20% of training steps is lower than under random ordering (Var(update_norm_easy_hard)[0:20%] < Var(update_norm_random)[0:20%], Mann-Whitney p < 0.05).

## Performance Gap

| Metric | Observed | Target | Gap |
|--------|----------|--------|-----|
| variance_ratio (eh/rn) | 0.992 | < 1.0 (significant) | ~0% reduction |
| n_significant_seeds | 0/3 | ≥2/3 | -2 seeds |
| direction_correct | 2/3 seeds | 3/3 | -1 seed |
| Mann-Whitney p (best) | 0.159 | < 0.05 | far from significance |

## Root Cause Analysis

- **Gradient clipping suppresses signal:** SFTTrainer applies gradient clipping by default, which compresses norm differences between easy and hard examples — the curriculum-induced variance signal is largely eliminated before measurement
- **Gradient accumulation averages variance:** `gradient_accumulation_steps=4` averages 4 micro-batches per optimizer step, reducing per-step variance regardless of ordering
- **Insufficient statistical power:** With only 33 early steps (20% of 166 steps at 1-epoch scale), Mann-Whitney test has insufficient power to detect small effects
- **Effect not robust across seeds:** Seed 42 shows reversed direction (easy_hard variance > random), indicating the effect is not consistent even when the direction is sometimes correct
- **1.3B model gradient homogeneity:** At 1.3B scale, the model may produce sufficiently uniform gradient norms across LeetCode difficulty levels that ordering has negligible impact on variance

## Lessons Learned

1. Gradient clipping (SFTTrainer default) eliminates curriculum-induced gradient norm differences — future experiments must either disable clipping or measure pre-clip gradients
2. `gradient_accumulation_steps` reduces sensitivity to per-example variance — use smaller accumulation or measure per-micro-batch gradients
3. 20% of 1-epoch training = ~33 steps is insufficient for Mann-Whitney statistical power — need more steps (multiple epochs or larger dataset)
4. The premise that easy-to-hard difficulty ordering drives detectable gradient variance reduction is not empirically valid at 1.3B scale with standard SFT setup
5. A2 verification confirmed curriculum ordering was active (easy_fraction_early=1.0) — the mechanism was implemented correctly but the effect is not real at this scale

## Feedback for Next Phase (Phase 0 Brainstorm)

### What NOT To Do
- Do not rely on gradient norm variance as a signal for curriculum effectiveness with default SFTTrainer settings
- Do not use Mann-Whitney on <50 early steps — insufficient power
- Do not assume gradient clipping-invariant metrics without verifying

### What Showed Promise
- h-e1 (prerequisite) was validated: 1.3B model has 1.672x higher gradient magnitude on Easy problems than 6.7B (p=6.48e-14) — the capability differential exists
- Curriculum ordering was correctly implemented and verified (A2 check passed)
- Code infrastructure (data loading, gradient capture, statistical testing) is reusable

### Suggested Modifications for Phase 0
- Consider measuring loss reduction rate or learning efficiency instead of gradient variance
- Consider longer training (3-5 epochs) to accumulate more early-phase steps
- Consider measuring gradient direction cosine similarity instead of norm variance
- Consider a direct performance proxy: does easy-to-hard ordering reduce final loss faster?

## Cascade Effects

Dependent hypotheses h-m3 (SHOULD_WORK) and h-m4 (MUST_WORK) depend on h-m1 as a prerequisite. With h-m1 FAILED, these hypotheses' mechanistic foundation is not supported.

---
*Failure recorded at: 2026-08-02T14:30:00+00:00*
*For cross-phase reference*
*Written by: Phase 4 Step 6B Reflection*
