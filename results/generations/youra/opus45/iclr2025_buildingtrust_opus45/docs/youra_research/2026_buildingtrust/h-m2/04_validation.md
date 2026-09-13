# Validation Report: H-M2

**Hypothesis:** Percentile-Normalized Monotonicity Attenuation
**Generated:** 2026-03-24 20:25:15
**Gate Type:** MUST_WORK
**Gate Result:** **PASS**

---

## Summary

This experiment tests whether RLHF instruction tuning attenuates the monotonic relationship between confidence (margin) and correctness.

**Hypothesis Statement:** Margin inflation decouples confidence-correctness relationship, measurable via attenuated percentile-normalized slope (β_percentile_instruct < β_percentile_base) under 2x2 prompt controls.

**Gate Criteria:**
1. β_instruct < β_base (direction check)
2. p < 0.05 (statistical significance via paired bootstrap)
3. All families must pass

---

## Results by Family

| Family | β_base | β_instruct | Δβ | p-value | Effect Size | Gate |
|--------|--------|------------|-----|---------|-------------|------|
| Qwen | 2.2222 | 1.4661 | 0.7581 | 0.0000 | 15.3052 | ✅ |
| Mistral | 1.5579 | 0.9305 | 0.6284 | 0.0000 | 16.9774 | ✅ |

---

## Detailed Results

### Qwen

**Sample Size:** 14042

**β_percentile (with 95% CI):**
- Base: 2.2222 [2.1140, 2.3453]
- Instruct: 1.4661 [1.4094, 1.5267]

**Difference Test (paired bootstrap):**
- Δβ = β_base - β_instruct: 0.7581 [0.6626, 0.8563]
- p-value: 0.0000
- Effect size (Δβ / σ): 15.3052

**Gate Check:**
- Direction (β_inst < β_base): ✅ Yes
- Significance (p < 0.05): ✅ Yes
- **Gate Pass:** ✅ PASS

### Mistral

**Sample Size:** 14042

**β_percentile (with 95% CI):**
- Base: 1.5579 [1.4855, 1.6323]
- Instruct: 0.9305 [0.8911, 0.9672]

**Difference Test (paired bootstrap):**
- Δβ = β_base - β_instruct: 0.6284 [0.5570, 0.7005]
- p-value: 0.0000
- Effect size (Δβ / σ): 16.9774

**Gate Check:**
- Direction (β_inst < β_base): ✅ Yes
- Significance (p < 0.05): ✅ Yes
- **Gate Pass:** ✅ PASS

---

## Gate Verdict

### ✅ GATE PASSED

All model families show statistically significant monotonicity attenuation:
- β_instruct < β_base (the instruct models have weaker confidence-correctness relationship)
- p < 0.05 (the difference is statistically significant)

**Interpretation:** RLHF instruction tuning degrades the discriminative quality of confidence signals by inflating margins for incorrect predictions, which weakens the monotonic relationship between margin and correctness probability.

---

## Figures

- `figures/gate_metrics_beta_percentile.png`: β comparison bar chart
- `figures/bootstrap_distributions.png`: Bootstrap β distributions
- `figures/logistic_curves.png`: Pr(correct) vs z(margin) curves
- `figures/forest_plot.png`: Effect size forest plot
