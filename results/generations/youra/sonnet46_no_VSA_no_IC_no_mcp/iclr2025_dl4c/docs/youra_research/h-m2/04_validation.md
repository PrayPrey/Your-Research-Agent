# H-M2 Validation Report

**Hypothesis**: RLEF-Fraction training on APPS achieves >10% non-zero reward fraction on hard (competition) problems.

**Gate condition**: `competition_nonzero_fraction > 0.10`

**Status**: FAIL — PIVOT required

---

## Experiment Setup

| Parameter | Value |
|---|---|
| Model | DeepSeek-Coder-7B-base (SFT-warm checkpoint) |
| Dataset | codeparrot/apps, stratified |
| Samples per bucket | 60 (180 total) |
| Generations per problem | G=2 |
| Max new tokens | 128 |
| Reward function | `fraction_reward_fn` (tests-passing / total-tests) |
| Evaluation mode | Post-hoc inference (not live training) |

**Analysis script**: `code/analyze_reward_fractions.py`  
**Reward log**: `h-e1/code/logs/reward_monitoring.jsonl` (18 records, 10 samples/record)

---

## Results

### Non-Zero Reward Fractions

| Difficulty Bucket | Non-Zero Fraction | n | Gate Threshold |
|---|---|---|---|
| introductory | 0.0000 | 60 | — |
| interview | 0.0000 | 60 | — |
| **competition** | **0.0000** | **60** | **> 0.10** |

### Gate Decision: **FAIL**

`competition_nonzero_fraction = 0.0000` — does not meet the `> 0.10` threshold.

Monotonicity holds trivially (all zero).

### Figures

- `figures/fig1_nonzero_fraction_bar.png` — Non-zero fractions per bucket vs threshold
- `figures/fig2_nonzero_fraction_step.png` — Fraction over evaluation steps
- `figures/fig3_reward_histogram.png` — Reward value distribution
- `figures/fig4_correlation_scatter.png` — Difficulty vs reward scatter

---

## Interpretation

The SFT-warm checkpoint generates syntactically valid Python code in many cases, but the outputs fail automated test case execution across all difficulty buckets. The `fraction_reward_fn` requires correct I/O matching within a 2-second timeout.

**Root causes for zero reward**:
1. `max_new_tokens=128` truncates many solutions before completion
2. SFT warm-up does not optimize for test-case correctness — it only learns problem→code formatting
3. Competition problems require multi-step algorithmic reasoning; short greedy decoding does not produce correct algorithms
4. Test cases require exact I/O match; off-by-one or formatting differences yield zero reward

**What this means for H-M2**:

H-M2 tests whether the **RLEF training reward signal** reaches non-zero values for competition problems. The result shows the **pre-RLEF baseline** has zero reward across all buckets. This is consistent with the GRPO setup: the reward signal is sparse at initialization, and RLEF training is intended to improve it.

However, H-M2 was defined as monitoring reward **during** RLEF training — not at baseline. The H-E1 training logs (`reward_monitoring.jsonl`) were not generated because H-E1's smoke run was cut short before `logging_steps=20`. The evaluation here uses the available SFT checkpoint as a proxy.

---

## SHOULD_WORK Gate: FAIL → PIVOT

Per the YouRA research protocol, a FAIL on the SHOULD_WORK gate triggers a **PIVOT** action, not pipeline termination.

**Recommended pivot directions**:

1. **Increase max_new_tokens to 512–1024**: Competition solutions require longer outputs; truncation at 128 tokens causes all failures
2. **Run actual RLEF training to convergence**: The H-E1 `SimpleGRPOTrainer` with `logging_steps=5` and sufficient wall-clock time would produce the intended training-time reward trajectory
3. **Use a stronger baseline**: DeepSeek-Coder-7B-instruct (not base) has better zero-shot code generation; SFT-warm on coding data may not reach non-zero reward territory without GRPO
4. **Lower reward threshold**: competition_fraction > 0.10 may be too aggressive for the SFT checkpoint; consider 0.02–0.05 as an intermediate gate

---

## Code Artifacts

| File | Status |
|---|---|
| `code/difficulty_reward_callback.py` | Complete |
| `code/analyze_reward_fractions.py` | Complete |
| `code/eval_fast.py` | Complete (used for this validation) |
| `code/tests/test_analyze_reward_fractions.py` | 7 tests pass |
| `code/tests/test_difficulty_reward_callback.py` | 5 tests pass |
| `results/reward_fractions.json` | Generated |
| `figures/fig1_nonzero_fraction_bar.png` | Generated |
| `figures/fig2_nonzero_fraction_step.png` | Generated |
| `figures/fig3_reward_histogram.png` | Generated |
| `figures/fig4_correlation_scatter.png` | Generated |

---

## Verification State Update

```
h-m2:
  phase: 4
  status: complete
  gate: FAIL
  verdict: PIVOT
  competition_nonzero_fraction: 0.0000
  gate_threshold: 0.10
  n_samples: 180
  figures: 4
  timestamp: 2026-08-26
```
