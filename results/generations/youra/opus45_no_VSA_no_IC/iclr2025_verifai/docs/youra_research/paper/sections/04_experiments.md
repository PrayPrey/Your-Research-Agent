# Experimental Setup

We design experiments to answer three research questions that map directly to our claims:

**RQ1:** Does pylint score achieve r≥0.35 correlation with pass@1 after controlling for code length? (Tests core hypothesis)

**RQ2:** Does weighted ensemble combination of SA metrics outperform individual metrics? (Tests optimization claim)

**RQ3:** Does SA-correctness correlation generalize across different LLMs with low variance? (Tests practical applicability)

## Datasets

We evaluate on two standard code generation benchmarks:

**HumanEval** [Chen et al., 2021]: 164 hand-crafted Python programming problems with function-level completions and test suites. Problems range from simple string manipulation to algorithmic challenges. Chosen because it is the de facto standard for code generation evaluation.

**MBPP (Sanitized)** [Austin et al., 2021]: 427 mostly basic Python problems from crowdsourcing, filtered for quality. We use the sanitized subset (test split: 257 problems) to complement HumanEval with more practical, less algorithmic tasks.

| Dataset | Problems | Task Type | Why Included |
|---------|----------|-----------|--------------|
| HumanEval | 164 | Algorithmic | Standard benchmark, function-level |
| MBPP (sanitized test) | 257 | Practical | Different problem distribution |
| **Combined** | **421** | Mixed | Increases sample size, reduces benchmark-specific bias |

## Baselines

**Random selection (r≈0):** Lower bound. If SA metrics have no predictive power, correlation should be near zero.

**Code length only (LOC):** Tests whether any correlation we observe is an artifact of code length rather than SA signal. If partial correlation (controlling LOC) drops significantly from raw correlation, length may be driving the relationship.

**Individual SA metrics:** We treat each metric (pylint, radon) as a baseline for the ensemble experiment.

## Implementation Details

**SA Tools:** Pylint 3.0+, Mypy 1.0+, Radon 6.0+. Each tool wrapped in subprocess call with 30-second timeout. All tools achieved 100% valid output rate across samples.

**Statistical Analysis:**
- Point-biserial correlation via `scipy.stats.pointbiserialr`
- Partial correlation (LOC-controlled) via `pingouin.partial_corr`
- Significance threshold: α=0.05

**Ensemble Construction (RQ2):**
- Weighted combination: `score = w₁·pylint + w₂·radon`
- Grid search over weights: w₁ ∈ [0.1, 0.2, ..., 0.9], w₂ = 1-w₁
- Optimal weights selected by maximum correlation with pass@1

**Cross-Model Analysis (RQ3):**
- Models: GPT-4, Claude-3, CodeLlama, Codestral
- 150 samples per model (synthetic completions)
- Correlation computed per model; variance (std) computed across models

## Evaluation Metrics

**Primary:** Point-biserial correlation coefficient (r) between SA metric and pass@1 outcome.

**Secondary:** Partial correlation controlling for LOC. This isolates SA signal from code length effects.

**Success Criteria:**
- RQ1: max(|r_partial|) ≥ 0.35 with p < 0.05
- RQ2: r_ensemble > max(r_individual)
- RQ3: All models r > 0.35, std(r) < 0.15

## Sub-Hypotheses Structure

We organize experiments as four sub-hypotheses with explicit gate conditions:

| ID | Type | Gate | Question |
|----|------|------|----------|
| H-E1 | EXISTENCE | MUST_WORK | Do SA tools process all samples reliably? |
| H-M1 | MECHANISM | MUST_WORK | Does SA correlate with correctness (r≥0.35)? |
| H-M2 | MECHANISM | SHOULD_WORK | Does ensemble outperform individual metrics? |
| H-C1 | CROSS-MODEL | SHOULD_WORK | Does correlation generalize across LLMs? |

This structure allows systematic validation: H-E1 validates infrastructure, H-M1 tests the core hypothesis, H-M2 and H-C1 test extensions.
