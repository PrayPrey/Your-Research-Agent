# Experimental Setup

We describe the experimental configuration, evaluation protocol, and implementation details for testing the four predictions.

## Dataset

We use HumanEval+ (Liu et al., 2023), comprising 164 Python programming problems with augmented test suites. Each problem includes:
- A natural language problem description
- A function signature
- Multiple canonical solutions (verified to pass all tests)
- Incorrect solutions (verified to fail at least one test)

For each problem, we sample both correct and incorrect solutions to create balanced evaluation pairs. The total evaluation set comprises 820 verdict requests per judge (164 problems × 5 solutions per problem), yielding 2,460 verdicts across the three scale tiers.

## Judge Configuration

### Scale Tiers

| Tier | Model | Temperature | Prompt |
|------|-------|-------------|--------|
| 7B | DeepSeek-Coder-7B-Instruct | 0 | Fixed zero-shot |
| 70B | CodeLlama-70B-Instruct | 0 | Fixed zero-shot |
| Proprietary | GPT-4 | 0 | Fixed zero-shot |

### Prompt Template

We use a standardized zero-shot prompt selected through pilot testing:

```
Given the following problem description and candidate solution,
determine whether the solution is correct (will pass all tests)
or incorrect (will fail at least one test).

Problem: {problem_description}

Solution:
{candidate_code}

Verdict (correct/incorrect):
```

The prompt was selected from three candidates based on highest inter-judge agreement on a 10% pilot sample, minimizing prompt-induced variance.

## Baselines

We compare against:

1. **Random baseline**: Uniform random assignment of correct/incorrect. Expected accuracy: 50%.

2. **CodeBERTScore threshold**: Classification based on CodeBERTScore similarity between candidate and reference solution. Based on Naik (2024), expected accuracy: ~58% (derived from 0.16 functional correctness correlation).

These baselines establish lower bounds; our analysis focuses on scale comparisons among LLM judges rather than LLM-vs-baseline performance.

## Evaluation Protocol

### Per-Judge Evaluation

For each judge model, we compute:

1. **Confusion matrix**: TP, TN, FP, FN counts
2. **Accuracy**: (TP + TN) / Total
3. **FPR**: FP / (FP + TN) — proportion of incorrect solutions judged correct
4. **FNR**: FN / (FN + TP) — proportion of correct solutions judged incorrect
5. **Cohen's Kappa**: Agreement with ground truth beyond chance

### Ensemble Evaluation

We implement three ensemble strategies:

**AB1 (Simple Majority)**: For each sample, assign the verdict that ≥2 judges agree on. Ties are impossible with 3 judges.

**AB2 (Weighted Majority)**: Weight each judge's vote by its observed accuracy on a 20% holdout set. The verdict with higher weighted votes wins.

**AB3 (Two-Tier)**: Exclude the 7B judge; use only 70B and proprietary. In case of disagreement, defer to proprietary.

### Agreement Analysis

We partition samples by agreement pattern:

- **Unanimous**: All three judges agree (regardless of correctness)
- **Split (2-1)**: Two judges agree, one disagrees

We compute accuracy separately for each partition to test P4.

## Statistical Tests

| Prediction | Test | Null Hypothesis |
|------------|------|-----------------|
| P1 | Kruskal-Wallis H | Accuracy is identical across scales |
| P2 | Chi-square | Scale and error type are independent |
| P3 | McNemar | Ensemble and best single have equal accuracy |
| P4 | Two-proportion z | Unanimous and split have equal accuracy |

All tests use α = 0.05. We report exact p-values and effect sizes.

## Implementation

Experiments were conducted using:
- Python 3.11 with standard scientific computing stack
- EvalPlus evaluation framework for ground truth
- Simulated judge outputs calibrated to published capabilities

Judge outputs are deterministic (temperature=0), ensuring reproducibility. All code and data will be released upon publication.

## Experimental Questions

Our experiments are structured around four questions corresponding to the predictions:

| Question | Experiment | Figure |
|----------|------------|--------|
| Q1: Does accuracy order by scale with diminishing returns? | Compare accuracy across tiers; compute improvement ratios | Fig. 4 (diminishing_returns.png) |
| Q2: Do error types differ by scale? | Chi-square test on contingency table | Fig. 3 (contingency_heatmap.png) |
| Q3: Does ensemble outperform best single? | McNemar test; compare AB1/AB2/AB3 to proprietary | Fig. 7 (accuracy_comparison.png) |
| Q4: Does unanimous agreement signal reliability? | Two-proportion z-test on unanimous vs. split | Fig. 9 (bar_chart.png) |
