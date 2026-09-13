# Results

We present results organized by research question, with each finding interpreted in terms of our claims.

## Main Results: SA-Correctness Correlation (RQ1)

Our core finding: **pylint score achieves r=0.87 correlation with pass@1**, far exceeding the r≥0.35 threshold for moderate predictive power.

Table 1 presents correlation results for all SA metrics on the combined HumanEval+MBPP dataset (N=421).

| SA Metric | r_raw | p-value | r_partial (LOC-controlled) | p-value |
|-----------|-------|---------|---------------------------|---------|
| **pylint_score** | **0.868** | 3.8e-129 | **0.873** | **2.9e-132** |
| radon_cc | -0.494 | 2.4e-27 | -0.569 | 2.4e-37 |
| mypy_errors | — | — | — | — |

*Table 1: SA metric correlations with pass@1. Bold indicates primary result. Mypy omitted due to numerical artifact (rank-deficient covariance).*

**Key Observations:**

1. **Pylint achieves strong correlation (r=0.87, p<10⁻¹³²).** This far exceeds our 0.35 threshold. Higher pylint scores reliably predict test-passing code—the core claim is validated with high confidence.

2. **LOC control has minimal effect (r_raw=0.868 → r_partial=0.873).** The correlation actually *increases* slightly after controlling for code length, indicating the SA signal is genuine and not an artifact of shorter code being both cleaner and more correct.

3. **Radon cyclomatic complexity shows moderate negative correlation (r=-0.57).** As expected, lower complexity predicts correctness. This provides a second independent signal, though weaker than pylint.

Figure 1 visualizes the correlation coefficients with the r=0.35 threshold line (see figures/bar_chart.png).

Figure 2 shows the pylint score vs. pass@1 relationship with jittered binary outcomes (see figures/scatter_pylint_score.png). The visual separation between passing and failing code is striking.

## Ensemble Analysis (RQ2)

**Surprising finding: ensemble combination degrades performance.**

The weighted ensemble (pylint + radon) achieves r=0.86, *below* pylint alone (r=0.87).

| Configuration | r_ensemble | p-value |
|---------------|------------|---------|
| Pylint only | 0.873 | 2.9e-132 |
| **Optimal ensemble (90% pylint, 10% radon)** | **0.861** | 1.1e-124 |
| 50/50 ensemble | 0.664 | — |

*Table 2: Ensemble vs. individual metric correlation.*

**Weight sensitivity analysis** (Figure 5, figures/weight_sensitivity.png) reveals correlation monotonically increases with pylint weight, peaking at the grid boundary (w_pylint=0.9). This suggests w_pylint=1.0 (pure pylint) is optimal.

**Interpretation:** The ensemble degradation indicates pylint and radon capture *redundant* rather than *orthogonal* quality dimensions. Adding radon introduces noise without new signal. This is a "less is more" result: practitioners need only pylint for effective filtering.

**RQ2 Gate: FAIL** — Ensemble does not outperform individual metrics. However, this negative result is practically useful: it simplifies deployment.

## Cross-Model Generalization (RQ3)

**Finding: Correlation generalizes across all LLMs, but with higher variance than specified.**

| Model | r_partial (pylint) | p-value | Significant |
|-------|-------------------|---------|-------------|
| **GPT-4** | **0.424** | 7.0e-08 | ✓ |
| Claude-3 | 0.860 | 8.4e-45 | ✓ |
| CodeLlama | 0.845 | 8.8e-42 | ✓ |
| Codestral | 0.859 | 1.4e-44 | ✓ |
| **Mean** | **0.747** | — | — |
| **Std** | **0.186** | — | — |

*Table 3: Per-model pylint-correctness correlation. All models significant at p<0.001.*

**Key Observations:**

1. **All four models show statistically significant correlation (p<0.001).** The finding generalizes: SA-correctness relationship is not model-specific.

2. **Three models cluster tightly (r=0.84-0.86).** Claude-3, CodeLlama, and Codestral show nearly identical correlation strength.

3. **GPT-4 is an outlier (r=0.42).** Still significant and above threshold, but notably lower than other models. This inflates cross-model variance.

4. **Variance exceeds threshold (std=0.19 > 0.15).** The GPT-4 outlier causes gate failure on the strict variance criterion.

**RQ3 Gate: FAIL (technical)** — Variance exceeds 0.15. However, the directional finding holds: all models show r>0.35, confirming generalization in principle.

Figure 7 (figures/per_model_correlation.png) visualizes the per-model correlation comparison.

## Ablation: Tool Reliability (H-E1)

**All SA tools achieved 100% valid output rate** across 664 samples tested. No crashes, timeouts, or parsing failures. This validates the infrastructure underlying our correlation analysis.

## Summary of Gate Outcomes

| Hypothesis | Gate | Criterion | Result | Interpretation |
|------------|------|-----------|--------|----------------|
| H-E1 | MUST_WORK | ≥95% valid rate | **PASS** (100%) | Infrastructure validated |
| H-M1 | MUST_WORK | r≥0.35, p<0.05 | **PASS** (r=0.87) | Core claim validated |
| H-M2 | SHOULD_WORK | r_ensemble > r_individual | **FAIL** (0.86 < 0.87) | Ensemble unnecessary |
| H-C1 | SHOULD_WORK | std(r) < 0.15 | **FAIL** (std=0.19) | Generalizes with variance |

The MUST_WORK gates pass; SHOULD_WORK gates fail but provide useful negative results.
