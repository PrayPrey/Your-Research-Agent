# Methodology

Our goal is to quantify the correlation between static analysis metrics and functional correctness for LLM-generated code. We describe our experimental design, statistical framework, and the rationale behind key choices.

## Overview

We compute point-biserial correlation between SA metrics (continuous) and pass@1 outcomes (binary) on HumanEval and MBPP benchmarks. To isolate the SA signal from confounding factors, we compute partial correlations controlling for code length (LOC). The core question: after accounting for the fact that shorter code tends to be both cleaner and more correct, does SA signal provide additional predictive power?

**Rationale:** Direct correlation measurement (rather than feedback loop improvement) enables rejection sampling—filtering k candidates by SA score without additional LLM calls. This requires knowing whether SA predicts correctness, not whether SA feedback improves correctness.

## Static Analysis Metrics

We extract three SA metrics capturing different quality dimensions:

**Pylint Score (0-10):** Measures code style, conventions, and potential errors. Pylint applies ~400 rules encoding decades of Python best practices. Higher scores indicate cleaner code. We hypothesize style quality correlates with logical correctness because both reflect underlying code clarity.

**Mypy Error Count:** Static type checking. More type errors may indicate logical inconsistencies, though the relationship is less direct than style metrics. We include mypy to test whether type-level analysis adds predictive signal.

**Radon Cyclomatic Complexity:** Measures decision branches (if/else, loops, boolean operators). Higher complexity correlates with more potential logical errors—fewer branches mean fewer opportunities for mistakes. We expect negative correlation with correctness.

**Implementation:** We wrap each tool in subprocess calls with 30-second timeouts, following patterns validated in preliminary experiments. All tools produce valid outputs on 100% of samples (no crashes or timeouts), as verified in our tool coverage experiment.

## Confound Control: Code Length

Code length (LOC) is a potential confound: shorter code may be both (1) cleaner (fewer SA warnings) and (2) more correct (simpler logic). If we observe SA-correctness correlation without controlling for LOC, the relationship might be spurious—driven by length rather than SA signal.

**Partial Correlation:** We compute partial correlation controlling for LOC using the formula:

$$r_{xy \cdot z} = \frac{r_{xy} - r_{xz} \cdot r_{yz}}{\sqrt{(1 - r_{xz}^2)(1 - r_{yz}^2)}}$$

where x = SA metric, y = pass@1, z = LOC. If partial correlation remains strong (comparable to raw correlation), the SA signal is genuine.

**Implementation:** We use `pingouin.partial_corr()` for partial correlation computation, with `scipy.stats.pointbiserialr()` for raw point-biserial correlation.

## Statistical Framework

**Point-Biserial Correlation:** Appropriate when correlating a continuous variable (SA metric) with a binary outcome (pass/fail). Equivalent to Pearson correlation when one variable is dichotomous.

**Significance Testing:** We use α=0.05 as significance threshold. Given sample sizes N>400, we have >99% power to detect r≥0.20 effects.

**Success Criterion:** We set r≥0.35 as the threshold for "moderate" correlation, following conventional interpretation. This threshold indicates SA scores would provide meaningful signal for rejection sampling.

## Dataset

We combine HumanEval (164 problems) and MBPP sanitized (427 problems) for 591 unique problem-solution pairs. This combination provides:

- **Diversity:** HumanEval emphasizes algorithmic problems; MBPP includes more practical tasks
- **Standard benchmarks:** Both are widely used, enabling comparison with prior work
- **Known ground truth:** Test suites define correctness unambiguously

For correlation analysis, we use canonical solutions (one completion per problem) to establish the SA-correctness relationship on known-correct code. Cross-model analysis uses LLM-generated completions to test generalization.

## Experimental Hypotheses

We structure the study around four sub-hypotheses:

**H-E1 (Existence):** SA tools produce valid outputs on all samples. Gate: ≥95% valid rate. This validates infrastructure before correlation analysis.

**H-M1 (Mechanism):** At least one SA metric achieves r≥0.35 with pass@1, controlling for LOC. Gate: max(|r_partial|) ≥ 0.35 with p<0.05. This tests the core hypothesis.

**H-M2 (Mechanism):** Weighted ensemble of SA metrics outperforms individual metrics. Gate: r_ensemble > max(r_individual). This tests whether combining signals improves prediction.

**H-C1 (Cross-Model):** SA-correctness correlation generalizes across LLMs with variance std(r)<0.15. Gate: All models show r>0.35 with low cross-model variance. This tests whether findings transfer beyond a single model.

## Analysis Pipeline

1. **Load problems:** HumanEval + MBPP sanitized (N=591)
2. **Obtain completions:** Canonical solutions or LLM-generated code
3. **Execute tests:** Determine pass/fail for each completion
4. **Extract SA metrics:** Pylint score, mypy errors, radon CC
5. **Extract LOC:** Lines of code as covariate
6. **Compute correlations:** Raw point-biserial and partial (LOC-controlled)
7. **Determine gate status:** Compare max(|r_partial|) to 0.35 threshold

## Visualization

We generate four figure types to communicate results:

- **Bar chart:** Correlation coefficients for all SA metrics with r=0.35 threshold line
- **Scatter plots:** SA metric vs pass@1 (jittered for binary outcome)
- **Heatmap:** Correlation matrix including SA metrics, LOC, and pass@1
- **Weight sensitivity:** For ensemble analysis, r vs. pylint weight (0 to 1)

## Reproducibility

All code, data, and configurations are available in the supplementary material. Key dependencies: scipy 1.11+, pingouin 0.5+, pandas 2.0+, matplotlib 3.7+, pylint 3.0+, mypy 1.0+, radon 6.0+.
