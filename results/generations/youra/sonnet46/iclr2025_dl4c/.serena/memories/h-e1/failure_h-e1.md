# Phase 4 Failure Record: h-e1 (EXISTENCE hypothesis)

**Hypothesis:** Under GRPO-based RLEF training with Qwen2.5-Coder-7B on high-S_term APPS problems (S_term > 0.85), substituting R_binary with R_ratio decreases the fraction of training batches receiving zero-reward signal by >=20% and increases gradient SNR by >=1.5x in the first 25% of training steps.

**Gate:** MUST_WORK
**Outcome:** FAIL → ROUTED_TO_PHASE_0
**Date:** 2026-03-15

## Root Cause

The hypothesis assumed that **partial-pass solutions exist** (0 < k_pass < k_total) on high-difficulty problems, enabling R_ratio to provide non-zero gradient signal where R_binary gives zero.

**Empirical finding:** On competition + interview APPS problems with Qwen2.5-Coder-7B-Instruct, the model produces k_pass=0 for ALL 8 rollouts in ALL 90 training steps (3 seeds × 30 steps per seed), for BOTH conditions:
- R_binary: ZRF = 1.0 (100% zero rewards), advantage_mean = 0.0, gradient_snr = 0.0
- R_ratio: ZRF = 1.0 (100% zero rewards), advantage_mean = 0.0, gradient_snr = 0.0

## Key Insight

At S_term > 0.85 (APPS competition + interview difficulty), a 7B model cannot pass even **one** test case. The model either produces syntactically invalid code or semantically wrong code that fails all test cases. There are **no near-miss solutions** — the model is well below the threshold where partial credit could be informative.

The hypothesis conflates "hard for the model" (high ZRF under R_binary) with "partially tractable" (some k_pass > 0). These are different conditions.

## Lessons Learned

1. **S_term > 0.85 is too hard**: Problems where SFT model rarely solves them (S_term > 0.85) may also be problems where k_pass = 0 always. R_ratio only helps when the model can partially solve problems.
2. **R_ratio requires a sweet spot difficulty**: The benefit of R_ratio over R_binary requires 0 < k_pass < k_total for at least some rollouts. This requires medium-hard problems, not maximum-hard problems.
3. **Better threshold for partial-credit benefit**: S_term in range [0.5, 0.8] where the model fails most but not all test cases would be more appropriate.
4. **Qwen2.5-Coder-7B on APPS**: The model achieves 0% pass rate on competition+interview APPS problems post-SFT (3 epochs). It should not be treated as capable of partial solutions on these tasks.

## Experiment Details

- Model: Qwen2.5-Coder-7B-Instruct
- Dataset: APPS (codeparrot/apps), high-S subset (competition + interview = 2361 problems)
- Seeds: 42, 1337, 2024 (3 seeds per condition)
- Steps: 30 per run (= 25% of planned training)
- Total runs: 6 (2 conditions × 3 seeds)
- Implementation: TRL GRPOTrainer v0.29.0, transformers v5.3.0, accelerate v1.13.0

## Recommendation for Redesign

If the main hypothesis (R_ratio > R_binary) is still worth testing, a redesigned experiment should:
1. Use medium-difficulty APPS problems (introductory level, where model has some partial success)
2. Or use a stronger model (13B+) that can partially solve competition problems
3. Or use a different dataset with more granular difficulty (e.g., HumanEval+ with subtask decomposition)
4. Target S_term in [0.4, 0.75] range where partial solutions naturally exist
