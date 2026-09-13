# H-M1 Validation Report: Granularity Effect on Repair Success

**Hypothesis:** Error feedback granularity (G0-G4) has a statistically significant effect on LLM code repair success rate.

**Gate Type:** MUST_WORK
**Gate Condition:** ANOVA p < 0.05
**Gate Result:** **PASS**

---

## Executive Summary

The H-M1 experiment successfully demonstrated that error feedback granularity has a **statistically significant effect** on LLM repair success rate (F=23.89, p=3.5e-19). However, the direction of the effect was **opposite to the initial expectation**: simpler feedback (G0, G1) yielded significantly higher repair success rates than more detailed feedback (G2-G4).

---

## Experiment Configuration

| Parameter | Value |
|-----------|-------|
| Model | CodeLlama-7B-Instruct |
| Dataset | MBPP (304 runtime error cases from H-E1) |
| Granularity Levels | G0, G1, G2, G3, G4 |
| Total Repair Attempts | 1,520 (304 cases x 5 levels) |
| Execution Timeout | 10 seconds |
| Statistical Test | One-way ANOVA with Tukey HSD post-hoc |
| Significance Level | alpha = 0.05 |

### Granularity Level Definitions

| Level | Feedback Content |
|-------|------------------|
| G0 | "Test failed." (minimal) |
| G1 | Error type only (e.g., "Test failed: TypeError") |
| G2 | Error type + message |
| G3 | Error type + message + line number |
| G4 | Full traceback (maximum detail) |

---

## Results

### Success Rates by Granularity

| Granularity | Successes | Total | Success Rate |
|-------------|-----------|-------|--------------|
| G0 | 127 | 304 | **41.8%** |
| G1 | 124 | 304 | **40.8%** |
| G2 | 56 | 304 | 18.4% |
| G3 | 51 | 304 | 16.8% |
| G4 | 69 | 304 | 22.7% |
| **Overall** | **427** | **1,520** | **28.1%** |

### ANOVA Results

| Metric | Value | Interpretation |
|--------|-------|----------------|
| F-statistic | 23.89 | Large F indicates significant between-group variance |
| p-value | 3.50e-19 | Highly significant (p << 0.05) |
| eta-squared | 0.059 | Medium effect size (0.01=small, 0.06=medium, 0.14=large) |

### Post-hoc Analysis (Tukey HSD)

**Significant pairwise differences (p < 0.05):**

| Comparison | p-value | Difference |
|------------|---------|------------|
| G0 vs G2 | 5.87e-10 | +23.4% |
| G0 vs G3 | 2.52e-11 | +25.0% |
| G0 vs G4 | 8.25e-07 | +19.1% |
| G1 vs G2 | 3.52e-09 | +22.4% |
| G1 vs G3 | 1.71e-10 | +24.0% |
| G1 vs G4 | 3.63e-06 | +18.1% |

**Non-significant differences:**

| Comparison | p-value | Interpretation |
|------------|---------|----------------|
| G0 vs G1 | 0.999 | Same group (high success) |
| G2 vs G3 | 0.990 | Same group (low success) |
| G2 vs G4 | 0.747 | Same group (low success) |
| G3 vs G4 | 0.452 | Same group (low success) |

### Group Clustering

The results reveal two distinct performance clusters:

1. **High-Success Group (G0, G1):** ~41% success rate
   - Minimal to basic error information
   - No significant difference within group

2. **Low-Success Group (G2, G3, G4):** ~17-23% success rate
   - Detailed error information
   - No significant differences within group

---

## Figures

### 1. Success Rate Bar Chart
![Success Rate by Granularity](figures/success_rate_bar.png)

### 2. Granularity Effect Curve
![Granularity Curve](figures/granularity_curve.png)

### 3. ANOVA Summary
![ANOVA Summary](figures/anova_summary.png)

### 4. Gate Comparison
![Gate Comparison](figures/gate_comparison.png)

### 5. Post-hoc Heatmap
![Tukey HSD Heatmap](figures/posthoc_heatmap.png)

### 6. Error Breakdown
![Error Breakdown](figures/error_breakdown.png)

---

## Analysis and Interpretation

### Key Findings

1. **Granularity matters:** The ANOVA confirms a statistically significant effect of error feedback granularity on repair success (p < 0.001).

2. **Less is more:** Counter-intuitively, simpler error feedback (G0, G1) leads to significantly higher repair rates than detailed feedback (G2-G4).

3. **Medium effect size:** The eta-squared of 0.059 indicates a medium-sized effect, explaining ~6% of variance in repair outcomes.

### Hypotheses for Observed Pattern

The unexpected inverse relationship between feedback detail and repair success may be explained by:

1. **Prompt length effects:** Detailed error messages increase prompt length, potentially degrading model attention on the actual code.

2. **Overfitting to error details:** Models may over-fixate on specific error details rather than understanding the underlying issue.

3. **Self-Debug paradigm mismatch:** The original Self-Debug work used different models and may have had different prompt formatting.

4. **Model capacity:** CodeLlama-7B may lack capacity to effectively utilize detailed error information, making simpler signals more actionable.

### Implications for Future Work

1. **Adaptive granularity:** Consider using simple feedback first, escalating to detailed feedback only on retry.

2. **Error type stratification:** Different error types may benefit from different granularity levels.

3. **Model scaling:** Larger models may better leverage detailed feedback - worth investigating with CodeLlama-13B/34B.

---

## Gate Verdict

| Criterion | Threshold | Actual | Status |
|-----------|-----------|--------|--------|
| ANOVA p-value | < 0.05 | 3.50e-19 | **PASS** |

**GATE RESULT: PASS**

The H-M1 hypothesis is **VALIDATED**. Error feedback granularity has a statistically significant effect on LLM repair success rate, though the direction of the effect (simpler = better) warrants further investigation.

---

## Files Generated

| File | Description |
|------|-------------|
| `results/repair_results.json` | All 1,520 repair attempt results |
| `results/metrics.yaml` | ANOVA metrics and success rates |
| `results/posthoc.yaml` | Tukey HSD pairwise comparisons |
| `results/experiment_summary.yaml` | High-level experiment summary |
| `figures/success_rate_bar.png` | Success rate by granularity |
| `figures/granularity_curve.png` | Effect curve G0→G4 |
| `figures/anova_summary.png` | ANOVA visualization |
| `figures/gate_comparison.png` | p-value vs threshold |
| `figures/posthoc_heatmap.png` | Pairwise comparison matrix |
| `figures/error_breakdown.png` | Success/failure counts |

---

## Reproducibility

```bash
# Activate environment
conda activate youra-h-m1

# Run experiment
CUDA_VISIBLE_DEVICES=0 python train.py --gpu 0 --h-e1-results data/h_e1_results.json --results-dir results
```

**Runtime:** ~40 minutes on single NVIDIA A100 GPU

---

*Generated: 2026-03-30*
*Phase 4 Validation Complete*
