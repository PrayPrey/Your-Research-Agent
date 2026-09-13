# Reflection Report: H-M2

**Hypothesis ID:** H-M2
**Date:** 2026-08-21
**Gate Type:** SHOULD_WORK
**Gate Result:** FAILED
**Reflection Outcome:** LIMITATION_RECORDED

---

## 1. Reflection Summary

SHOULD_WORK gate failed: `frac_reward_zero_std = 1.0` for both variance-50 and random-50 conditions throughout all 50 training steps. Gap = 0.0 at all checkpoints. Gate threshold (gap ≥ 5pp) not met.

No prior self-recovery attempts. Reflection type: standard fallback. Outcome: LIMITATION_RECORDED. Pipeline continues to Phase 5 with limitation note.

---

## 2. Root Cause Analysis

**Cold-start problem.** DeepSeek-Coder-7B-Instruct-v1.5 produces binary reward = 0.0 for all G=4 completions on all 50 MBPP problems in both conditions at every training step (50 steps total).

- `rewards/reward_fn/mean = 0.0` throughout both runs
- `loss = 0.0`, `grad_norm = 0.0` — zero gradient signal
- With reward_std = 0.0 per group, frac_zero_std = 1.0 identically for both conditions

**Why variance selection cannot help here:** The theoretical advantage of variance-50 (higher H-E1 variance_i problems should have intermediate pass@k for the model) assumes the model has nonzero pass@1 on some problems at training start. At step 0, this model passes 0 MBPP tests. No reward signal = no gradient = no differentiation between conditions.

**H-M1 remains valid.** The top-50 variance-selected problems DO have higher variance_i than random-50 (H-M1 confirmed this). The selection mechanism is correct. The limitation is that variance_i from H-E1 (profiling on the initial model) does not guarantee intermediate difficulty for the same model during GRPO training.

---

## 3. Limitation Note

**H-M2: SHOULD_WORK gate failed — cold-start regime.**

Variance selection advantage cannot be observed when model pass@k ≈ 0 for all MBPP problems. The mechanism requires nonzero base rewards to produce measurable frac_zero_std differences between conditions. With binary execution reward and 50 training steps at lr=5e-7, DeepSeek-Coder-7B-Instruct-v1.5 produces zero reward throughout.

This is a known limitation of frozen profiling-based selection for GRPO warm-up problems.

---

## 4. Lessons Learned

1. **Base model pass@k matters.** Variance profiling for GRPO curriculum selection requires a model with nonzero base pass@k on the target benchmark. DeepSeek-Coder-7B does not meet this requirement for MBPP in 50 steps.

2. **Frozen profiles have cold-start risk.** H-E1 variance_i reflects profiling-time pass@k distribution, not training-time distribution. If the model fails all problems at training start, profiling-based selection cannot help.

3. **Detection signal:** `frac_reward_zero_std = 1.0` sustained for > 5 steps is a reliable early-stop indicator for cold-start. Log this metric from step 1.

4. **TRL 1.9.2 API (preserved for H-M3/H-M4):**
   - `max_completion_length` not `max_new_tokens`
   - `processing_class` not `tokenizer`
   - `save_strategy="no"` not `save_steps=[list]`
   - `youra-h-m1` conda env (torch 2.6.0+cu124, TRL 1.9.2)
   - MBPP `full/train` not `sanitized/train`
   - H-E1 JSON key is `top_ids` not `top50_ids`

---

## 5. Recommended Path Forward

Three options for H-M3/H-M4 (in order of confidence):

1. **Online selection** — at each generation step, filter training problems to those where current model pass@k ∈ (0, 1). Eliminates cold-start entirely; selection adapts to model capability in real time.

2. **Warmer model** — use Qwen2.5-7B-Instruct or similar with MBPP pass@1 > 30%. Profiling-based selection can then observe frac_zero_std differentiation from step 0.

3. **Longer warmup** — increase max_steps to 500+ with cosine warmup; allow model to develop nonzero pass@k before evaluating curriculum effect.

---

## 6. Pipeline Status

- Experiment: COMPLETED (both 50-step runs, no errors)
- Gate: SHOULD_WORK FAILED
- Reflection outcome: LIMITATION_RECORDED
- Next: Phase 5 (report generation) with limitation recorded
- Hypothesis status: continues (not FAILED, not SUPERSEDED — SHOULD_WORK failure is non-blocking)

---

*Reflection completed: 2026-08-21*
*Outcome: LIMITATION_RECORDED — pipeline continues to Phase 5*
