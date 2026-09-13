# H-M2: LIMITATION_RECORDED (Phase 4 Reflection)

**Date:** 2026-08-21
**Hypothesis:** H-M2 — Variance Selection Reduces Zero-Gradient Groups
**Gate Type:** SHOULD_WORK
**Gate Result:** FAILED
**Reflection Outcome:** LIMITATION_RECORDED

## Root Cause

Cold-start problem. DeepSeek-Coder-7B-Instruct-v1.5 produces binary reward=0.0 for all G=4 completions on all MBPP problems throughout 50 training steps at lr=5e-7. With reward_std=0.0 per group, frac_reward_zero_std=1.0 identically for both variance-50 and random-50 conditions. No gradient signal → no differentiation.

## Limitation

Variance selection advantage (H-M1 validated: top-50 problems have higher variance_i than random-50) cannot be observed when model pass@k≈0 for all MBPP problems. The mechanism requires nonzero base rewards to produce measurable frac_zero_std differences between conditions.

## TRL 1.9.2 API Fixes (reuse in H-M3/H-M4)

- `max_completion_length` not `max_new_tokens` in GRPOConfig
- `processing_class` not `tokenizer` in GRPOTrainer
- `save_strategy="no"` not `save_steps=[list]`
- `youra-h-m1` conda env (torch 2.6.0+cu124, TRL 1.9.2)
- MBPP `full/train` (374 problems) not `sanitized/train` (120 problems)
- H-E1 JSON key is `top_ids` not `top50_ids`

## Recommended Pivot for H-M3/H-M4

1. **Online selection** — filter problems where current model pass@k ∈ (0,1) at each generation step
2. **Warmer model** — use Qwen2.5-7B-Instruct (MBPP pass@1 >30%) instead of DeepSeek-Coder-7B
3. **Longer warmup** — max_steps 500+ to develop nonzero pass@k before evaluating curriculum effect

## Pipeline Status

SHOULD_WORK failure is non-blocking. Pipeline continues to Phase 5 with limitation recorded.
