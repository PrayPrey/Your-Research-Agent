# Methodology

Our experimental design isolates error feedback granularity as the sole independent variable, enabling causal attribution of performance differences to the feedback level rather than confounding factors.

## Overview

We adopt a within-subject experimental design where the same set of runtime error cases is repaired under all five granularity conditions. This eliminates case-difficulty confounds: if one granularity level succeeds more often, it cannot be attributed to receiving "easier" problems.

The experimental pipeline consists of three stages:
1. **Error Collection**: Generate code for MBPP problems, execute against tests, and collect cases with runtime errors
2. **Feedback Generation**: For each error case, construct five versions of the repair prompt varying only the error feedback section
3. **Repair Evaluation**: Attempt repair under each condition and record binary success (all tests pass)

## Granularity Level Definitions

We define five levels spanning the full spectrum from minimal to maximal feedback:

**G0 (Pass/Fail Only)**: The prompt indicates only that the test failed, with no error details.
```
The code failed the test. Please fix it.
```

**G1 (Error Type)**: Adds the exception class name.
```
The code failed with: IndexError
Please fix it.
```

**G2 (Error + Message)**: Adds the full error message.
```
The code failed with: IndexError: list index out of range
Please fix it.
```

**G3 (Error + Line)**: Adds the line number where the error occurred.
```
The code failed with: IndexError: list index out of range
Error occurred at line 7.
Please fix it.
```

**G4 (Full Stack Trace)**: Provides the complete traceback with context.
```
The code failed with the following error:
Traceback (most recent call last):
  File "solution.py", line 7, in find_max
    return max(arr[i], find_max(arr, i+1))
IndexError: list index out of range
Please fix it.
```

**Rationale**: These levels capture natural breakpoints in error information granularity. G0 represents the minimal baseline (equivalent to naive retry). G1-G3 represent progressively more specific localization. G4 represents the maximum information typically available from Python's traceback module.

## Prompt Template

We use a Self-Debug style prompt template [Chen et al., 2023] across all conditions. The template structure is:

```
You are a helpful programming assistant. The following code was written
to solve this problem:

[PROBLEM DESCRIPTION]

```python
[ORIGINAL CODE]
```

[ERROR FEEDBACK - varies by granularity level]

Please provide the corrected code.
```

**Design Choice**: Using the same template for all conditions ensures that observed differences are attributable to the error feedback content, not template variations. We selected the Self-Debug template as it represents the established baseline in the literature.

## Model Configuration

We use CodeLlama-7B-Instruct for all experiments with the following configuration:

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Model | CodeLlama-7B-Instruct | Representative instruction-tuned code LLM |
| Temperature | 0 | Deterministic generation for reproducibility |
| Max tokens | 512 | Sufficient for single-function repairs |
| Timeout | 10s per test | Standard execution timeout |

**Design Choice**: Temperature 0 ensures reproducible results—the same input produces the same output. While stochastic sampling (T > 0) with multiple attempts might show different patterns, deterministic generation provides a cleaner experimental signal.

## Statistical Analysis

Our analysis employs standard statistical methods appropriate for the data structure:

**Primary Analysis (H-M1)**: One-way ANOVA across five granularity levels tests whether repair success rates differ significantly. We report F-statistic, p-value, and effect size (η²).

**Pairwise Comparisons**: Tukey's Honestly Significant Difference (HSD) identifies which specific pairs of granularity levels differ significantly, controlling for multiple comparisons.

**Directional Tests (H-M2, H-M3)**: McNemar's test for paired binary outcomes compares specific granularity pairs (G0 vs G3, G3 vs G4), leveraging the within-subject design.

**Confidence Intervals**: Wilson score intervals for proportions provide uncertainty quantification for success rates.

## Hypothesis Structure

Our experimental design tests a hierarchy of hypotheses:

**H-E1 (Foundation)**: Runtime errors with localizable stack traces are prevalent (≥30%) in LLM code failures. This validates that granularity comparison is meaningful.
- Gate type: MUST_WORK
- If fails: Abandon study (insufficient error cases)

**H-M1 (Mechanism)**: Granularity has a statistically significant effect on repair success (ANOVA p < 0.05).
- Gate type: MUST_WORK
- If fails: Conclude granularity doesn't matter

**H-M2 (Direction)**: G3 achieves ≥10pp higher success than G0.
- Gate type: SHOULD_WORK
- Our original prediction based on attention window hypothesis

**H-M3 (Non-monotonicity)**: G4 does not significantly outperform G3.
- Gate type: SHOULD_WORK
- Tests whether "more is better" holds at the high end

This hierarchical structure ensures we don't over-interpret results if foundation hypotheses fail, while allowing falsification of specific predictions (H-M2, H-M3) to be scientifically informative.

## Controlled Variables

To isolate granularity as the causal factor, we control:

| Variable | Control Method |
|----------|---------------|
| Problem difficulty | Same 304 cases across all conditions |
| Model | Same CodeLlama-7B-Instruct weights |
| Prompt structure | Same Self-Debug template |
| Generation parameters | Same T=0, max_tokens=512 |
| Execution environment | Same Python 3.10, timeout settings |
| Random seed | Fixed for reproducibility |

The only variable that changes between conditions is the error feedback content, ensuring observed differences are attributable to granularity.
