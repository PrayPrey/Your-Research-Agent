# Results

Our experiments reveal that error feedback granularity significantly affects LLM repair success—but in the opposite direction predicted by conventional wisdom. Simpler feedback dramatically outperforms detailed feedback at the 7B scale.

## Foundation: Runtime Error Prevalence (RQ1)

Before comparing granularity levels, we verify that runtime errors are prevalent enough to make the comparison meaningful.

| Error Category | Count | Percentage |
|----------------|-------|------------|
| Runtime Error | 304 | 60.8% |
| Syntax Error | 193 | 38.6% |
| Wrong Output | 3 | 0.6% |
| Timeout | 0 | 0% |
| **Total Failures** | **500** | **100%** |

**Finding:** Runtime errors with localizable stack traces constitute 60.8% of failures (95% CI: [56.5%, 65.0%]), well above our 30% threshold.

**Interpretation:** The foundation hypothesis (H-E1) is strongly supported. Runtime errors dominate LLM code failures on MBPP, validating that granularity comparison addresses a substantial portion of the repair problem. This prevalence exceeds prior estimates and confirms that modern instruction-tuned LLMs produce syntactically valid but semantically incorrect code.

## Main Effect: Granularity Affects Repair Success (RQ2)

Table 1 presents repair success rates across all five granularity levels.

**Table 1: Repair Success Rates by Granularity Level**

| Level | Definition | Successes | Rate | 95% CI |
|-------|------------|-----------|------|--------|
| G0 | Pass/fail only | 127/304 | **41.8%** | [36.3%, 47.4%] |
| G1 | Error type | 124/304 | **40.8%** | [35.4%, 46.4%] |
| G2 | Error + message | 56/304 | 18.4% | [14.4%, 23.2%] |
| G3 | Error + line | 51/304 | 16.8% | [12.9%, 21.4%] |
| G4 | Full trace | 69/304 | 22.7% | [18.3%, 27.8%] |

One-way ANOVA confirms a highly significant effect of granularity:

| Statistic | Value |
|-----------|-------|
| F-statistic | 23.89 |
| p-value | 3.5 × 10⁻¹⁹ |
| η² (effect size) | 0.059 (medium) |

**Finding:** Granularity has a statistically significant effect on repair success (p < 10⁻¹⁸) with medium effect size (η² = 0.059).

**Interpretation:** The mechanism hypothesis (H-M1) is supported—granularity matters. However, the pattern is striking: success rates cluster into two distinct groups rather than showing the expected non-monotonic curve. Minimal feedback (G0, G1) achieves approximately 41% success, while detailed feedback (G2, G3, G4) achieves only 17-23%.

## Two-Cluster Pattern

Tukey's HSD post-hoc analysis reveals the cluster structure:

**Table 2: Pairwise Comparisons (Tukey HSD)**

| Comparison | Difference | p-value | Significant |
|------------|------------|---------|-------------|
| G0 vs G1 | +1.0pp | 0.99 | No |
| G0 vs G2 | +23.4pp | <0.001 | **Yes** |
| G0 vs G3 | +25.0pp | <0.001 | **Yes** |
| G0 vs G4 | +19.1pp | <0.001 | **Yes** |
| G1 vs G2 | +22.4pp | <0.001 | **Yes** |
| G2 vs G3 | +1.6pp | 0.95 | No |
| G2 vs G4 | -4.3pp | 0.52 | No |
| G3 vs G4 | -5.9pp | 0.22 | No |

**Finding:** The data reveals two statistically distinct clusters:
- **High-success cluster:** G0, G1 (~41%)
- **Low-success cluster:** G2, G3, G4 (~17-23%)

**Interpretation:** The threshold effect occurs at the G1→G2 boundary—the moment we include the error message, performance drops by approximately 22 percentage points. Within clusters, differences are not significant. This suggests a qualitative shift in how the model processes feedback, not a gradual degradation.

## Directional Test: G0 vs G3 (RQ3)

We originally predicted G3 would outperform G0 by at least 10 percentage points. McNemar's test for paired comparisons reveals the opposite:

| Metric | Value |
|--------|-------|
| G0 success rate | 41.8% |
| G3 success rate | 16.8% |
| Difference | **-25.0pp** |
| 95% CI for difference | [-32.0%, -18.0%] |
| McNemar χ² | 77 |
| p-value | 5.23 × 10⁻²² |

**Contingency Analysis:**

| | G3 Success | G3 Failure |
|---|-----------|------------|
| **G0 Success** | 50 | 77 |
| **G0 Failure** | 1 | 176 |

**Finding:** G0 dramatically outperforms G3 by 25 percentage points (p < 10⁻²¹). The effect is in the opposite direction predicted.

**Interpretation:** The directional hypothesis (H-M2) is refuted. The "attention window hypothesis"—that intermediate granularity would focus attention optimally—is not supported. Instead, detailed localization appears to actively harm repair. Of 77 cases where G0 succeeded but G3 failed, only 1 case showed the reverse pattern.

## Non-Monotonicity Test: G3 vs G4 (RQ4)

We predicted G4 (full trace) would not significantly outperform G3 (error + line). McNemar's test:

| Metric | Value |
|--------|-------|
| G3 success rate | 16.8% |
| G4 success rate | 22.7% |
| Difference | +5.9pp |
| McNemar χ² | 19 |
| p-value | 4.0 × 10⁻⁵ |

**Finding:** G4 significantly outperforms G3 (p < 10⁻⁴), contradicting our non-monotonicity prediction.

**Interpretation:** The non-monotonicity hypothesis (H-M3) is refuted. Within the low-success cluster, full traces (G4) provide modest recovery compared to partial information (G3). If a model is going to receive detailed feedback, providing the complete context appears slightly better than partial context—though both remain far below minimal feedback (G0/G1).

## Summary of Hypothesis Outcomes

| Hypothesis | Type | Gate | Prediction | Actual | Status |
|------------|------|------|------------|--------|--------|
| H-E1 | Existence | MUST_WORK | ≥30% runtime | 60.8% | **PASS** |
| H-M1 | Mechanism | MUST_WORK | p < 0.05 | p < 10⁻¹⁸ | **PASS** |
| H-M2 | Direction | SHOULD_WORK | G3 ≥ G0 + 10pp | -25.0pp | **FAIL** |
| H-M3 | Non-monotonicity | SHOULD_WORK | G4 ≤ G3 + 2% | +5.9pp | **FAIL** |

The foundation and mechanism hypotheses pass with strong evidence. The directional predictions fail—but these failures are scientifically informative, revealing that the "more information is better" assumption is wrong at this scale.
