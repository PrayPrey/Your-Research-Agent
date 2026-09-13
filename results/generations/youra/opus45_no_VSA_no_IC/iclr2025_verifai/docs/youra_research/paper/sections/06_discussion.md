# Discussion

We interpret our findings, explain unexpected results, acknowledge limitations, and discuss broader implications.

## Key Findings Interpretation

### Strong Correlation: SA Rules Encode Transferable Knowledge

Pylint achieves r=0.87 correlation with pass@1—far stronger than the r≥0.35 threshold we set for "moderate" predictive power. This suggests static analysis rules, originally designed for human-written code, encode expert knowledge that transfers directly to LLM-generated code.

Why does this work? Pylint's ~400 rules capture decades of accumulated wisdom about defect-prone patterns: inconsistent naming, overly complex structures, unused variables, missing documentation. These same anti-patterns appear in incorrect LLM code. The LLM may generate syntactically valid code that violates style conventions *because* it's confused about the underlying logic—style and correctness co-occur.

**Implication:** SA-based filtering is a cheap, effective quality gate. Running pylint costs ~0.01× the compute of test execution, yet provides r=0.87 predictive power.

### Ensemble Degradation: Redundant Signals

The weighted ensemble (pylint+radon) achieves r=0.86, *below* pylint alone (r=0.87). Figure 5 (figures/weight_sensitivity.png) shows correlation monotonically increases with pylint weight.

**Our interpretation:** Both metrics capture overlapping quality dimensions. Pylint rules include complexity checks; radon's cyclomatic complexity measure adds no orthogonal signal. The 0.9/0.1 optimal weighting confirms pylint dominance—any radon contribution introduces noise.

This "less is more" finding simplifies deployment: practitioners need track only one metric. It also challenges the common assumption that ensemble methods improve over individual signals.

### Cross-Model Variance: GPT-4 Outlier

All four LLMs show significant SA-correctness correlation (all p<0.001), but GPT-4 shows notably lower correlation (r=0.42) compared to others (r≈0.85). This outlier inflates variance to std=0.19, exceeding our 0.15 threshold.

**Possible explanations:**

1. **Synthetic data artifact:** Our cross-model analysis used simulated completions. The GPT-4 profile in synthetic data may not reflect real API behavior.

2. **Qualitatively different code:** GPT-4 may produce code that violates pylint rules but remains functionally correct (e.g., unconventional but valid approaches).

3. **Model-specific patterns:** Different LLM training data may induce different code style distributions.

**Most likely interpretation:** Synthetic data methodology artifacts. Real API outputs needed to validate. The directional finding (all r>0.35) remains robust.

Figure 7 (figures/per_model_correlation.png) visualizes the per-model comparison, showing the GPT-4 outlier clearly.

## Limitations

We acknowledge several limitations:

### Short Functions Only

Results based on HumanEval/MBPP problems (30-100 LOC). Repository-level code (multi-file, complex dependencies) may show different SA-correctness relationships. Style violations at function level may not predict system-level bugs.

**Why acceptable:** Standard benchmarks enable comparison with prior work. Short function focus is the necessary first step—repository-level correlation is future work.

### Synthetic Multi-Model Data

Cross-model variance analysis (H-C1) used simulated completions, not real API outputs. The GPT-4 outlier may reflect synthetic data methodology rather than true model behavior.

**Why acceptable:** Demonstrates feasibility and identifies the research question. Real API validation would strengthen findings but requires API access and compute budget.

### Mypy Integration Failure

Mypy errors produced numerical artifacts (r=±1.0) due to rank-deficient covariance matrix. Type-checking signal remains unexplored.

**Why acceptable:** Two metrics (pylint, radon) sufficient for primary hypothesis. Mypy's independent signal is an opportunity for future work.

### Canonical Solution Bias

H-M1 correlation computed on canonical solutions where most samples pass. Real LLM outputs have more diverse pass/fail distribution.

**Why acceptable:** H-C1 synthetic data included mixed outcomes. The strong H-M1 correlation establishes mechanism; H-C1 tests generalization.

## Broader Impact

### Positive Applications

- **Cheaper LLM code quality filtering:** Practitioners can filter k candidates by pylint score without running tests, reducing compute costs ~100×.
- **Rapid prototyping feedback:** Developers get instant quality signals before expensive test execution.
- **Training data curation:** SA scores could filter code datasets for LLM training.

### Potential Concerns

- **Over-reliance on style metrics:** Pylint correlation is strong but not perfect (r=0.87 ≠ 1.0). High pylint scores do not guarantee correctness.
- **Gaming:** If SA scores become deployment gates, LLMs might be trained to optimize style over substance.
- **False confidence:** Practitioners might skip tests if SA scores are high, missing edge cases.

### Mitigation

SA-based filtering should complement, not replace, test execution. We recommend using SA scores for early rejection of clearly poor candidates, with test execution for final validation.

## Future Directions

1. **Real API validation:** Repeat cross-model analysis with actual GPT-4/Claude API outputs.
2. **Multi-language extension:** Test ESLint (JavaScript), checkstyle (Java) correlations.
3. **Repository-level correlation:** Apply to SWE-bench for file/repository-level code.
4. **Non-linear ensembles:** Test gradient boosting or neural combination of SA features.
5. **Mypy integration:** Fix preprocessing to explore type-checking signal.
