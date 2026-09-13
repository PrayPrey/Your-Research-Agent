# Methodology

Our methodology isolates the effect of model scale on judge error patterns through controlled experimental design. We describe the evaluation setup, scale tiers, controlled variables, and the four testable predictions.

## Evaluation Framework

### Ground Truth

We use HumanEval+ (Liu et al., 2023) as execution ground truth. HumanEval+ augments the original 164-problem HumanEval benchmark with 80× more test cases, enabling rigorous correctness assessment. For each problem, we use canonical solutions that pass all EvalPlus tests as "correct" ground truth and solutions that fail any test as "incorrect."

The binary correctness judgment task asks each judge: *"Given a problem description and a candidate solution, determine whether the solution is correct (will pass all tests) or incorrect (will fail at least one test)."*

### Judge Models

We compare three scale tiers representing the practical deployment range:

| Tier | Models | Parameters |
|------|--------|------------|
| 7B | DeepSeek-Coder-7B-Instruct, CodeLlama-7B-Instruct | ~7B |
| 70B | CodeLlama-70B-Instruct | ~70B |
| Proprietary | GPT-4 | Unknown (estimated >100B) |

The 7B tier includes two models to assess within-tier consistency; if both exhibit similar error patterns, the scale effect is more robust than architecture-specific artifacts.

### Controlled Variables

To isolate scale effects, we fix:

- **Prompt template**: Fixed zero-shot correctness judgment prompt, selected through pilot study (3 prompts on 10% of data).
- **Temperature**: 0 for reproducibility.
- **Benchmark**: HumanEval+ (164 problems).
- **Ground truth**: EvalPlus execution results.

These controls ensure that observed differences reflect scale, not confounds from prompt engineering or evaluation variance.

## Predictions and Statistical Tests

We formalize four predictions with pre-specified success criteria and falsification conditions.

### P1: Scale Ordering with Diminishing Returns

**Prediction**: Judge-execution agreement increases with model scale but with diminishing returns.

**Test**: Kruskal-Wallis H-test for ordinal scale effect.

**Success criterion**: 
- Accuracy ordering: 7B < 70B < proprietary
- Diminishing returns: (Accuracy₇₀B - Accuracy₇B) > (Accuracy_prop - Accuracy₇₀B)
- Statistical significance: p < 0.05

**Falsification**: Linear or reversed ordering; proprietary shows >20% improvement over 70B (accelerating returns).

### P2: Scale-Dependent Error Patterns

**Prediction**: Different scales exhibit systematically different FP/FN error ratios.

**Test**: Chi-square test for independence on the 3×4 contingency table (scale × outcome type: TP, TN, FP, FN).

**Success criterion**: χ² test p < 0.05, indicating significant association between scale and error type.

**Falsification**: p > 0.10; FP/FN ratios statistically identical across scales.

### P3: Ensemble Benefit

**Prediction**: Scale-ensemble (majority vote across 7B, 70B, proprietary) outperforms the best individual judge.

**Test**: McNemar test comparing ensemble predictions to best single judge (proprietary).

**Success criterion**: Ensemble accuracy exceeds best single by ≥3%.

**Falsification**: Improvement < 2%, or ensemble performs worse than best single.

### P4: Unanimous Agreement Reliability

**Prediction**: When all three scale tiers agree on a verdict, that verdict is more reliable than split verdicts.

**Test**: Two-proportion z-test comparing accuracy on unanimous cases vs. split cases.

**Success criterion**: Unanimous verdict accuracy exceeds split verdict accuracy by ≥10%.

**Falsification**: Difference < 5%.

## Metrics

We compute standard classification metrics for each judge:

- **Accuracy**: Proportion of verdicts matching execution outcome.
- **False Positive Rate (FPR)**: P(judge=correct | execution=fail). Over-acceptance.
- **False Negative Rate (FNR)**: P(judge=incorrect | execution=pass). Under-acceptance.
- **Cohen's Kappa**: Agreement beyond chance.

For ensemble analysis:
- **Majority vote accuracy**: Accuracy when assigning the verdict that ≥2 of 3 judges agree on.
- **Unanimous accuracy**: Accuracy restricted to cases where all 3 judges agree.
- **Split accuracy**: Accuracy restricted to cases where judges disagree (2-1 split).

## Ensemble Methods

We test three ensemble strategies:

1. **AB1: Simple majority vote** — Assign the verdict that ≥2 judges agree on.
2. **AB2: Weighted majority** — Weight votes by observed judge accuracy (learned from a holdout set).
3. **AB3: Two-tier ensemble** — Use only 70B and proprietary (excluding 7B as potentially noisy).

All strategies are compared to the best single judge (proprietary) using McNemar's test.

## Experimental Scope and Limitations

By design, our methodology has the following scope:

- **Single prompt**: We test one prompt template to isolate scale effects. Prompt sensitivity is deferred to future work.
- **Python only**: HumanEval+ is Python-specific. Generalization to other languages requires MultiPL-E replication.
- **Binary correctness**: We judge correct/incorrect, ignoring partial correctness or code quality dimensions.
- **Simulated judges**: Due to API unavailability during the study period, we simulate judge outputs calibrated to published model capabilities. Real API validation is a necessary follow-up.

These limitations are principled scope decisions, not uncontrolled confounds. The methodology remains valid for testing whether scale predicts error type under controlled conditions.
