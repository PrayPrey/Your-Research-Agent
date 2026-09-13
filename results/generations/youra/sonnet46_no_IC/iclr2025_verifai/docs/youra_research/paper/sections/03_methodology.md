# Methodology

## Overview

Our study addresses a fundamental question in LLM code repair: which feedback signal — execution test results or pylint/mypy static analysis warnings — produces larger pass@1 improvement when both are given the same inference compute budget? The iso-compute constraint is the methodological core: without it, apparent feedback quality differences may simply reflect differences in the number of tokens spent on repair.

Building on the observation that execution and static analysis signals capture fundamentally different error properties, we design a three-condition experiment with compute-matched repair loops, paired on the same problems, evaluated with McNemar's test. We also run a separate mechanism study that decomposes pylint/mypy coverage by flag category to understand *why* one signal outperforms the other.

## Experimental Conditions

We compare three conditions on HumanEval (164 problems) and MBPP (378 problems):

**Condition A: No-feedback baseline.** Single-pass greedy decoding. No repair. All token budget B spent on initial generation. This establishes the baseline pass@1 against which improvement deltas are measured.

**Condition B: Pylint/mypy iterative repair.** After initial generation, failing solutions receive pylint and mypy output formatted as structured feedback. The LLM re-generates given the original problem + failed solution + feedback. Repair continues until the token budget is exhausted.

**Condition C: Execution test feedback iterative repair.** After initial generation, failing solutions are executed against the benchmark test suite. The error output (exception type, traceback, expected vs. actual values) is formatted as structured feedback. The LLM re-generates given the original problem + failed solution + execution feedback.

**Key invariant:** All three conditions use the same model (Llama 3.1 8B Instruct), the same decoding parameters (greedy, temperature=0, seed=42), and the same token budget (B=1000 output tokens per problem, summed across all repair rounds).

## Iso-Compute Token Budget

The token budget B=1000 output tokens per problem is the experimental unit of compute. For each problem, we track cumulative output tokens across rounds; repair stops when the remaining budget falls below a minimum threshold (50 tokens) or when the problem passes. This ensures that Conditions B and C spend the same total compute, making their pass@1 deltas directly comparable.

**Practical implication:** At B=1000, with max\_tokens=512 per round and initial generation consuming approximately 400–512 tokens, most problems complete one repair round before budget exhaustion. The multi-round repair design (max 3 rounds) was intended to enable iterative improvement, but B=1000 effectively constrains the comparison to single-round repair for most problems. Per-round trajectory data confirms that rounds 2–3 contribute near-zero incremental improvement, so single-round repair at B=1000 captures the primary effect.

## Feedback Signal Design

**Pylint/mypy feedback format.** We run `pylint --output-format=text` and `mypy` on each failing solution. The output is parsed, filtered to problem-relevant lines, and formatted as a structured prompt: the problem statement, the failing solution, and the tool output. Pylint uses default rule configuration (all categories: E, W, C, R, I).

**Execution feedback format.** We execute the failing solution in a sandboxed subprocess (15-second timeout) against the benchmark's test assertions. The exception type, traceback (truncated to 512 characters), and the first failing assertion (expected vs. actual) are formatted as structured feedback.

Both feedback formats are injected at the same position in the prompt template to control for prompt structure effects.

## Statistical Analysis

**Primary test: McNemar's test.** For each benchmark, we form a 2×2 contingency table of (pylint-passes, pylint-fails) × (execution-passes, execution-fails) on paired problems. McNemar's test evaluates whether the off-diagonal cells (problems where one condition passes and the other fails) differ significantly (α=0.05). This paired test is appropriate because both conditions process the same problems from the same baseline.

**Effect size: Δ_pass@1.** We report the improvement delta Δ = pass@1(condition) − pass@1(no-feedback baseline) for each condition. Positive Δ indicates improvement; negative Δ indicates regression.

**Bootstrap confidence intervals.** 95% confidence intervals on Δ_pass@1 use 10,000 bootstrap samples (seed=42).

## Mechanism Study: Pylint Coverage Analysis

To understand *why* pylint feedback performs as it does, we run a separate measurement experiment on the 64 HumanEval baseline failures. For each failing solution, we run pylint and mypy and record all flags, annotated by category (E: Error, W: Warning, C: Convention, R: Refactor, I: Information). We compute:

- **Total coverage:** fraction of failures that receive any pylint or mypy flag
- **Functional coverage (E+W):** fraction receiving at least one Error or Warning flag
- **Category distribution:** proportion of total flags in each category

Bootstrap confidence intervals on coverage fractions use 10,000 samples (seed=42). This decomposition reveals whether high total coverage reflects functional signal or style noise.

## Model and Infrastructure

| Parameter | Value |
|-----------|-------|
| Model | meta-llama/Llama-3.1-8B-Instruct |
| Backend | vLLM v0.10.1.1 (bfloat16) |
| Hardware | 5× H100 NVL (GPU memory utilization 0.4) |
| Max model length | 4096 tokens |
| Decoding | Greedy (temperature=0, seed=42) |
| Token budget B | 1000 output tokens per problem |
| Max repair rounds | 3 (effectively 1 at B=1000) |
| Execution timeout | 15 seconds |

Code is available at [anonymous repository link].
