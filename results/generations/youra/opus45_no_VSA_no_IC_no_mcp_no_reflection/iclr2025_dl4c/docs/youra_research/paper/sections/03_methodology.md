# Methodology

We describe our approach to measuring reward information bandwidth effects on code LLM training. The core insight is that reward signals can be characterized by their information content—the number of bits conveyed per gradient update—and that higher bandwidth should enable more precise credit assignment.

## Information Bandwidth Framework

We formalize reward bandwidth as follows. Given a code generation attempt, the reward function maps the execution outcome to a scalar signal. Different reward designs provide different amounts of information:

**LOW (Binary):** $r \in \{0, 1\}$ provides 1 bit per update.
- 1 if all test cases pass
- 0 otherwise

**MEDIUM (Continuous):** $r = \frac{n_{\text{passed}}}{n_{\text{total}}} \in [0, 1]$ provides ~1.5 bits per update.
- Partial credit for partial success
- No error type information

**HIGH (Categorical + Continuous):** $r = 0.5 \times \text{pass\_rate} + 0.5 \times \text{error\_score}$ provides ~2 bits per update.
- Combines continuous test pass rate
- Adds categorical error type scoring

This ordering—LOW < MEDIUM < HIGH—reflects increasing information content about why code succeeded or failed.

## Error-Type Scoring

The key innovation in our HIGH condition is the error score based on distance-to-correct. We define a principled ordering of error types:

| Error Type | Score | Rationale |
|------------|-------|-----------|
| Syntax error | 0.00 | Code does not parse—farthest from correct |
| Runtime error | 0.33 | Code runs but crashes—closer to correct |
| Assertion failure | 0.67 | Code runs completely but produces wrong output |
| Pass | 1.00 | Code is correct |

This ordering reflects execution stages: parse → execute → assert → pass. A syntax error indicates fundamental problems; an assertion failure indicates the code is structurally sound but logically flawed. By scoring these differently, we provide the model with information about *which kind* of error it made, not just *that* it failed.

**Rationale:** If a model's output shifts from syntax errors to assertion failures, it is making progress toward correctness even if the reward is still 0 under binary scoring. The error score captures this progress.

## Reward Function Definitions

We implemented three reward conditions:

```
LOW:    reward = 1.0 if all_tests_pass else 0.0

MEDIUM: reward = num_passed / num_total

HIGH:   reward = 0.5 × (num_passed / num_total)
              + 0.5 × error_score(error_type)
```

The 0.5/0.5 weighting in HIGH is a heuristic choice. We acknowledge this as a limitation—optimal weighting may vary by task or model. A full study would include weight sensitivity analysis, but our PoC scale precluded this.

## Training Configuration

We use policy gradient training (REINFORCE with advantage baseline) via the TRL library:

- **Model:** CodeLlama-7B-Instruct
- **Training data:** MBPP sanitized training split
- **Evaluation data:** MBPP validation subset (50 problems)
- **Optimizer:** AdamW with linear learning rate decay
- **Epochs:** 1 (PoC scale)
- **Seeds:** 3 per condition

The PoC scale was chosen for rapid iteration. As we report in Results, this scale proved insufficient for any learning to emerge.

## Hypothesis and Predictions

**Main Hypothesis (H-RewardBandwidth-v1):** Under PPO training of CodeLlama-7B on MBPP with fixed compute budget, if reward function provides higher information bandwidth, then model reaches pass@1 > 0.3 in fewer training samples, because denser feedback enables gradient updates to more precisely target error-inducing code patterns.

**Null Hypothesis (H0):** There is no significant difference in samples-to-threshold between reward bandwidth conditions.

**Predictions:**
- P1: HIGH < LOW in samples-to-threshold
- P2: MEDIUM < LOW in samples-to-threshold
- P3: HIGH shows different error-type distribution by epoch 3

At PoC scale, none of these predictions could be tested because all conditions remained at 0% pass@1—a floor effect that prevented meaningful comparison.

## Limitations of This Design

Several limitations constrain interpretation:

1. **Scale:** 1 epoch is likely insufficient for PPO policy improvement on code generation
2. **Seeds:** 3 seeds may not capture variance across initializations
3. **Weighting:** 0.5/0.5 is heuristic; sensitivity analysis was planned but not executed
4. **Single model:** Only 7B tested; scaling effects unknown
5. **Python-only:** Error parsing assumes standard Python error formatting

These limitations, particularly scale, proved decisive. The methodology itself is sound—the execution was underpowered.
