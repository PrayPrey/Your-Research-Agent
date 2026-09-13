# Experimental Setup

We design experiments to answer the following questions:

**RQ1:** Does feedback presentation order affect LLM code repair quality under matched content?

**RQ2:** If an ordering effect exists, what is its mechanism—early-gain amplification or regression prevention?

## Datasets

We evaluate on two standard code generation benchmarks:

**HumanEval** [Chen et al., 2021]: 164 hand-crafted Python programming problems with comprehensive test suites. Problems range from simple string manipulation to algorithm implementation. We use HumanEval because it is the most widely-adopted benchmark in LLM code generation research, enabling direct comparison with prior self-repair studies.

**MBPP** [Austin et al., 2021]: 500 crowd-sourced Python programming problems covering a broader difficulty range than HumanEval. We include MBPP to test generalization beyond HumanEval's curated style and to increase statistical power.

| Dataset | Problems | Avg. Tests/Problem | Difficulty Range |
|---------|----------|-------------------|------------------|
| HumanEval | 164 | ~5 | Medium-Hard |
| MBPP | 500 | ~3 | Easy-Medium |
| **Total** | **664** | ~4 | Varied |

The combined dataset (664 problems) provides sufficient statistical power for detecting effect sizes observed in prior self-repair work (10-17% improvement).

## Conditions

We compare two feedback ordering conditions under matched content:

**Condition A (Static→Execution):** Static analysis feedback appears first, followed by execution feedback.

**Condition B (Execution→Static):** Execution feedback appears first, followed by static analysis feedback.

Both conditions receive identical feedback content generated from the same code state. Content is truncated to 500 tokens per feedback type (1000 total) using deterministic first-token truncation to ensure byte-identical content across conditions.

## Baselines

Our primary comparison is between Condition A and Condition B. This within-method comparison isolates ordering effects:

- **Same model:** GPT-4o-mini
- **Same feedback content:** Byte-identical
- **Same token budget:** 1000 tokens total
- **Same iterations:** 3 repair iterations

We do not compare against execution-only or static-only baselines in this study, as those comparisons confound ordering with information volume—the confound we aim to eliminate.

## Implementation Details

**Model:** GPT-4o-mini (gpt-4o-mini-2024-07-18) via OpenAI API

**Inference Parameters:**
- Temperature: 0.0 (deterministic)
- Max tokens: 2048 per response
- System prompt: Standard code generation instruction

**Static Analysis:**
- Pylint 3.0+: Style, potential bugs, unused variables
- Mypy 1.0+: Type checking when type hints present
- Output concatenated and truncated to 500 tokens

**Execution Environment:**
- Sandboxed Python 3.10 subprocess
- 10-second timeout per test
- Stdout/stderr capture for feedback

**Repair Loop:**
- Maximum 3 iterations
- Early termination on all tests passing
- Per-iteration feedback regeneration

**Compute:** Single A100 GPU for local execution; API calls to OpenAI

## Evaluation Metrics

**Primary Metric: pass@1**

The fraction of problems where final code passes all tests:
$$\text{pass@1} = \frac{|\{p : \text{all\_tests\_pass}(p)\}|}{664}$$

**Relative Improvement:**
$$\text{RelImprove} = \frac{\text{pass@1}_A - \text{pass@1}_B}{\text{pass@1}_B} \times 100\%$$

Success criterion: RelImprove ≥ 15%, 95% CI lower bound > 10%.

**Statistical Tests:**

- Bootstrap CI: 10,000 resamples for 95% confidence interval on relative improvement
- McNemar's test: Paired comparison on per-problem pass/fail outcomes (p < 0.05)

**Mechanism Metrics (RQ2):**

- ΔPass₁→₂: Change in pass rate from iteration 1 to iteration 2
- RegRate₁→₂: P(pass@iter1 ∧ fail@iter2) — regression probability
