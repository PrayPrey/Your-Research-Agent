# Methodology

Our methodology isolates feedback ordering from information volume through a matched-content experimental design. We describe the design rationale, conditions, and evaluation approach.

## Design Rationale

Building on our observation that feedback ordering may independently affect repair quality, we design an experiment that controls the primary confound in prior studies: information volume. Rather than comparing "static feedback" vs "execution feedback" (which varies content), we compare "static→execution" vs "execution→static" (which varies only order).

**Key Design Principle:** Both conditions receive identical feedback content; only presentation order differs.

This requires:
1. Generating both static and execution feedback for each problem
2. Truncating each to a fixed token budget (500 tokens per type, 1000 total)
3. Concatenating in different orders for each condition
4. Ensuring byte-identical content across conditions

## Experimental Conditions

We define two matched conditions:

**Condition A (Static→Execution):**
```
[Static Analysis Feedback: 500 tokens]
[Execution Feedback: 500 tokens]
```

**Condition B (Execution→Static):**
```
[Execution Feedback: 500 tokens]
[Static Analysis Feedback: 500 tokens]
```

The feedback content is generated once per problem-iteration pair, then presented in both orders. Deterministic truncation (first 500 tokens) ensures identical content.

## Feedback Generation

### Static Analysis

We run Pylint and Mypy on generated code:
- Pylint catches style violations, unused variables, potential bugs
- Mypy catches type errors when type hints are present

Output is concatenated and truncated to 500 tokens.

### Execution Feedback

We execute code against test cases in a sandboxed environment:
- Capture stdout/stderr
- Record pass/fail per test
- Collect stack traces for failures

Output is truncated to 500 tokens, preserving traceback structure.

## Repair Loop

Algorithm 1 describes the repair loop:

```
Input: problem P, model M, max_iterations=3
Output: final_code, pass_status

1. initial_code ← M.generate(P.prompt)
2. for iter in 1..max_iterations:
3.     static_fb ← run_static_analysis(code)
4.     exec_fb ← run_tests(code, P.tests)
5.     if exec_fb.all_pass: return code, PASS
6.     if condition == A:
7.         feedback ← concat(static_fb, exec_fb)
8.     else:
9.         feedback ← concat(exec_fb, static_fb)
10.    code ← M.repair(code, feedback)
11. return code, FAIL
```

Both conditions use identical generation/execution logic; only line 6-9 differs.

## Evaluation Metrics

### Primary Metric: pass@1

We compute pass@1 as the fraction of problems where the final code passes all tests:

$$\text{pass@1} = \frac{|\{p : \text{passes}(p)\}|}{|P|}$$

### Secondary Metrics

**Relative Improvement:**
$$\text{RelImprove} = \frac{\text{pass@1}_A - \text{pass@1}_B}{\text{pass@1}_B} \times 100\%$$

**Bootstrap Confidence Interval:** 10,000 resamples for 95% CI on relative improvement.

**McNemar's Test:** Paired comparison on per-problem outcomes (pass/fail) to assess statistical significance.

## Mechanism Hypotheses

We test two mechanism hypotheses:

**H-M1 (Early-Gain Amplification):** If static-first scaffolds repair, early iterations should show larger gains:
$$\Delta\text{Pass}_{1\to2}(A) > \Delta\text{Pass}_{1\to2}(B)$$

**H-M2 (Regression Prevention):** If static-first stabilizes trajectories, regression rates should be lower:
$$\text{RegRate}_{1\to2}(A) < \text{RegRate}_{1\to2}(B)$$

where RegRate = P(pass@iter1 → fail@iter2).

## Controlled Variables

| Variable | Value | Rationale |
|----------|-------|-----------|
| Dataset | HumanEval + MBPP | Standard benchmarks, 664 problems |
| Model | GPT-4o-mini | Cost-effective, sufficient capability |
| Temperature | 0.0 | Deterministic for reproducibility |
| Token Budget | 500 + 500 | Balanced, fits context |
| Iterations | 3 | Standard in literature |

## Implementation

Code is implemented in Python with:
- OpenAI API for model inference
- subprocess isolation for test execution
- Pylint/Mypy for static analysis
- NumPy/SciPy for statistical analysis

The matched-content design ensures both conditions share identical feedback generation pipelines, differing only in concatenation order.
