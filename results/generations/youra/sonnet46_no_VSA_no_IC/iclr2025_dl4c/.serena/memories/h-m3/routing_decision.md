# H-M3 Routing Decision: LIMITATION_RECORDED

## Result
FAILED (EXPLORE: cold_start_persists)

## Finding
Warm-start GRPO (LR=1e-6, 200 steps, max_completion_length=512) on deepseek-coder-7b-instruct-v1.5 still produces frac_reward_zero_std=1.0 and max_reward=0.0 in both variance-50 and random-50 conditions. Cold-start not broken by doubling LR or extending to 200 steps.

## Implication for H-M4
Cold-start is a model-regime issue, not a training-duration issue. H-M4 must address via:
1. Online/dynamic problem selection (select problems where current model has recent nonzero reward)
2. Warmer model (SFT pre-adaptation to MBPP before GRPO)
3. Reward shaping (partial credit for syntax correctness or partial test pass)

## Gate
SHOULD_WORK gate not satisfied. Hypothesis cannot be tested in current cold-start regime.

## See also
`mem:h-m2/limitation_recorded`
