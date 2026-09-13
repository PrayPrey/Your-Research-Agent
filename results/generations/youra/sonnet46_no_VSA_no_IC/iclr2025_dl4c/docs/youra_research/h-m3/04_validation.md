---
hypothesis_id: h-m3
type: MECHANISM
validation_result: FAILED
gate_type: SHOULD_WORK
gate_passed: false
explore_finding: cold_start_persists
generated_at: 2026-08-21
author: yoon303@etri.re.kr
---

# H-M3 Validation Report: Proxy Temporal Stability

## Summary

**Result: FAILED (EXPLORE — cold-start persists)**

H-M3 attempted to test whether the variance-50 selection advantage over random-50 (lower `frac_reward_zero_std`) is sustained across 200 GRPO training steps under warm-start conditions. The warm-start configuration (LR=1e-6, max_steps=200, max_completion_length=512) still produced zero rewards in both conditions, preventing any measurement of the temporal stability of the proxy.

---

## Gate Evaluation

| Criterion | Result | Value |
|-----------|--------|-------|
| Warm-start succeeded | **FAIL** | max_reward_var50=0.0, max_reward_rnd50=0.0 |
| P1: gap > 0 at steps 10, 20, 50 | N/A (warm-start failed) | null |
| P2: gap_retention >= 0.5 | N/A (warm-start failed) | null |
| **Gate (SHOULD_WORK)** | **FAILED** | EXPLORE: cold_start_persists |

---

## Experiment Details

### Configuration
| Parameter | H-M3 Value | H-M2 Value | Change |
|-----------|-----------|-----------|--------|
| max_steps | 200 | 50 | +150 |
| learning_rate | 1e-6 | 5e-7 | ×2 |
| max_completion_length | 512 | 512 | same (reduced from planned 1024 due to GPU memory) |
| num_generations | 4 | 4 | same |
| seed | 42 | 42 | same |
| model | deepseek-coder-7b-instruct-v1.5 | same | same |
| dataset | MBPP full/train, k=50 | same | same |

### Training Results
- **Condition A (variance-50)**: 200 steps completed. `frac_reward_zero_std = 1.0` at all 200 steps. `max_reward = 0.0`.
- **Condition B (random-50)**: 200 steps completed. `frac_reward_zero_std = 1.0` at all 200 steps. `max_reward = 0.0`.
- **Early-stop detection**: Both conditions flagged cold-start (frac=1.0 for first 50 steps).
- **Warm-start check**: Failed — neither condition produced any nonzero reward in 200 steps.

### Runtime
- Condition A: ~8 min (200 steps × ~2.4 s/step)
- Condition B: ~8 min (200 steps × ~1.4 s/step, after warm GPU)
- Environment: NVIDIA H100 NVL, youra-h-m1 conda env (torch 2.6.0+cu124, TRL 1.9.2)

---

## Root Cause Analysis

The cold-start persists despite doubling the learning rate (5e-7 → 1e-6) and extending training to 200 steps. The deepseek-coder-7b-instruct model requires generating correct Python code to receive any reward — with `exec_timeout=5.0` and 4 generations per problem, the model never generates a passing solution in 200 attempts.

Key factors:
1. **Model capability gap**: The instruct model generates syntactically valid but semantically incorrect Python in this zero-shot GRPO setup. Without an initial correct solution, the reward signal never starts.
2. **Exploration insufficient**: 4 generations × 50 problems × 200 steps = 40,000 attempts, all returning reward=0.0. The policy is not exploring broadly enough to accidentally pass any test case.
3. **Cold-start is a model-regime issue, not a training-duration issue**: H-M2 ran 50 steps with the same result. H-M3 ran 200 steps — same result. More steps at the same LR do not help if the initial policy generates 0% correct solutions.

---

## EXPLORE Finding

The cold-start limitation identified in H-M2 extends to H-M3's warm-start configuration. The proxy temporal stability hypothesis (H-M3) cannot be tested in this cold-start regime because:
- There is no nonzero reward signal to differentiate variance-50 from random-50
- The gap trajectory (frac_rnd - frac_var) cannot be measured when both conditions have frac=1.0

---

## Implications for H-M4

Per the architecture plan, H-M4 should address the cold-start problem through:
1. **Online selection**: Rather than pre-selecting 50 problems once, dynamically select problems where the current model has nonzero recent reward history
2. **Warmer model initialization**: Use a model pre-adapted to MBPP via SFT before GRPO
3. **Reward shaping**: Add partial-credit rewards (e.g., syntax correctness, partial test pass) to break the zero-reward regime

The variance profiling approach (H-E1, H-M1) remains valid as a concept — the limitation is that GRPO cold-start prevents testing it empirically in this setup.

---

## Files Generated
- `results/gate_results.json`: EXPLORE results with cold-start finding
- No figures generated (warm-start failed before analysis phase)
- `experiment.log`: Full training log (200+200 steps, both conditions)

---

## Gate Decision

**FAILED (EXPLORE: cold_start_persists)**

Gate type: SHOULD_WORK. The hypothesis that warm-start GRPO would break cold-start did not hold at LR=1e-6, 200 steps. The cold-start is a fundamental regime issue that requires a different approach (H-M4).
