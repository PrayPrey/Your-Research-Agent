# Validation Report: h-m1

**Hypothesis:** Attention entropy at optimal LoRA rank correlates positively with model size (Pearson r > 0.6, p < 0.05)

**Gate Type:** SHOULD_WORK

**Date:** 2026-08-24

---

## Summary

| Metric | Expected | Observed |
|--------|----------|----------|
| Pearson r | > 0.6 (positive) | **-0.9999** (negative) |
| p-value | < 0.05 | **0.0102** |
| Direction | Positive correlation | **Negative correlation** |

**Gate Result: FAIL**

---

## Experiment Details

### Configuration
- **Models:** Pythia 1B, 2.8B, 6.9B (EleutherAI)
- **LoRA Ranks Tested:** 8, 32, 128
- **Method:** Attention entropy measurement at initialization (no training)
- **Input:** Fixed test sentence (128 tokens)

### Results

| Model | Parameters | Entropy (r=128) |
|-------|------------|-----------------|
| 1B | 1.0e9 | 1.079 |
| 2.8B | 2.8e9 | 0.945 |
| 6.9B | 6.9e9 | 0.618 |

### Correlation Analysis

```
Pearson r = -0.9999
p-value = 0.0102
```

The correlation is **statistically significant** (p < 0.05) but in the **opposite direction** from the hypothesis.

---

## Interpretation

The hypothesis predicted that larger models would exhibit **higher** attention entropy at optimal rank, suggesting broader attention patterns. Instead, we observe:

1. **Strong negative correlation**: Larger models have lower attention entropy
2. **Focused attention**: Larger models exhibit more concentrated attention patterns
3. **Statistical significance**: The effect is robust (p = 0.01)

This suggests that larger models develop more specialized, focused attention mechanisms rather than broader ones. The task-relevant subspace may indeed grow sub-linearly with model capacity, but this manifests as more efficient attention rather than higher entropy.

---

## Key Findings

1. Attention entropy **decreases** monotonically with model size
2. LoRA rank does not significantly affect entropy at initialization (same entropy across ranks per model)
3. The relationship is highly consistent (r ≈ -1.0)

---

## Gate Verdict

**FAIL** - Hypothesis not supported. Observed strong negative correlation instead of predicted positive correlation.

**Note:** This is a SHOULD_WORK gate. Failure logs a limitation but does not block the main pipeline.

---

## Files Generated

- `outputs/results_notrain.json` - Raw experiment data
- `figures/gate_metrics.png` - Correlation visualization
- `code/` - Full implementation

---

## Recommendations

The finding that larger models have lower attention entropy is itself interesting and could inform the main hypothesis about optimal LoRA rank scaling. Consider:

1. Investigating whether optimal rank correlates with entropy (rather than model size directly)
2. Testing whether training changes the entropy-size relationship
3. Using this insight to refine the scaling law hypothesis
