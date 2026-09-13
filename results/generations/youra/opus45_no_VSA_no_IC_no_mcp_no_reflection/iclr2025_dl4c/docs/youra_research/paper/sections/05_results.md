# Results

Our main finding is negative: all conditions produced 0% pass@1 at PoC scale, preventing the planned statistical comparison. We report these null results honestly and interpret what they reveal about experimental scale requirements.

## Main Results

Table 1 presents pass@1 results across all conditions and seeds.

| Condition | Seed 1 | Seed 2 | Seed 3 | Mean ± Std |
|-----------|--------|--------|--------|------------|
| LOW (Binary) | 0.00 | 0.00 | 0.00 | 0.0000 ± 0.0000 |
| MEDIUM (Continuous) | 0.00 | 0.00 | 0.00 | 0.0000 ± 0.0000 |
| HIGH (Bandwidth) | 0.00 | 0.00 | 0.00 | 0.0000 ± 0.0000 |

**Key Observation:** All nine training runs (3 conditions × 3 seeds) achieved 0% pass@1 after 1 epoch. No model learned to generate correct code.

**Interpretation:** This is a floor effect. The experimental scale was insufficient for ANY condition to show learning, making comparison between conditions meaningless. This null result does not falsify the information bandwidth hypothesis—it establishes that the hypothesis cannot be tested at PoC scale.

## Statistical Analysis

**Planned Analysis:** Independent t-test comparing HIGH vs LOW samples-to-threshold.

**Actual Result:**
- t-statistic: NaN (undefined—no variance)
- p-value: NaN
- Cohen's d: NaN

**Why NaN:** Statistical tests require variance. With all values at 0, there is no variance to compare. The planned analysis is mathematically impossible.

**Interpretation:** The null result is not "no significant difference." It is "comparison impossible at this scale." This distinction matters: failure to reject the null hypothesis typically means insufficient evidence for an effect. Here, we have no evidence at all—only confirmation that the experiment was underpowered.

## Samples-to-Threshold Analysis

**Threshold:** pass@1 > 0.3 (from hypothesis)

| Condition | Seeds Reaching Threshold | Mean Samples-to-Threshold |
|-----------|-------------------------|---------------------------|
| LOW | 0 / 3 | Not reached |
| MEDIUM | 0 / 3 | Not reached |
| HIGH | 0 / 3 | Not reached |

**Interpretation:** No seed in any condition reached the threshold. The samples-to-threshold metric, which was our primary dependent variable, could not be measured.

## Error-Type Distribution

**Planned Analysis:** Track proportion of syntax/runtime/assertion/pass errors per checkpoint to test RQ3.

**Actual Result:** With 0% pass@1, all generated code failed execution. Error-type distribution analysis was not performed because:
1. Training did not progress beyond the floor
2. No meaningful comparison possible when all outputs fail

**Future Work:** Error-type distribution remains a valuable signal for validating the credit assignment hypothesis. A properly powered experiment should track this metric throughout training.

## What We Learned

The null result establishes a lower bound for future work:

1. **Scale matters more than reward design at low compute.** At 1-epoch scale, the reward function is irrelevant because no policy improvement occurs in any condition.

2. **PoC pilots may be systematically uninformative.** If the goal is to compare reward designs, the minimum scale must exceed the threshold for ANY learning to emerge.

3. **~1000 gradient updates is insufficient.** Prior work (CodeRL, PPOCoder) used substantially more training. Our PoC scale may be 10-100x below the necessary threshold.

**Concrete Guidance:** Future experiments should budget ≥3 epochs, ≥5 seeds, and include learning rate warm-up before expecting measurable reward effects.
