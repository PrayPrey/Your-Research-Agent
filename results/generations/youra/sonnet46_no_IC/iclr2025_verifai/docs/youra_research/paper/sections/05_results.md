# Results

## Main Comparison: Execution vs. Pylint/Mypy (RQ1)

Execution feedback significantly outperforms pylint/mypy feedback on both benchmarks. Figure 1 shows the pass@1 improvement delta with 95% bootstrap confidence intervals.

**Table 1: Main Results.** Pass@1 values and improvement deltas for all conditions.

| Condition | HumanEval pass@1 | Δ_HE | MBPP pass@1 | Δ_MBPP |
|-----------|-----------------|------|------------|-------|
| No-feedback (baseline) | 61.0% | — | 33.1% | — |
| Pylint/mypy repair | 56.7% | **−4.3pp** | 51.4% | +18.3pp |
| Execution feedback | 65.9% | **+4.9pp** | 73.3% | **+40.2pp** |

The most striking result is on MBPP: a single round of execution feedback repair improves pass@1 from 33.1% to 73.3% — a +40.2pp absolute improvement, more than doubling the baseline success rate. This is not a subtle statistical finding; it represents 152 additional problems solved from the same starting point, using the same model, with only feedback signal changed.

On HumanEval, the execution advantage is smaller in absolute terms (+4.9pp) but the *direction* of pylint repair is reversed: pylint feedback makes HumanEval performance *worse* (−4.3pp), a finding we interpret mechanistically in Section 5.3.

**McNemar Test Results (Table 2):**

| Benchmark | Exec-only | Pylint-only | McNemar p-value |
|-----------|-----------|-------------|----------------|
| HumanEval | 15 | 0 | p = 0.0001 |
| MBPP | 85 | 2 | p < 10⁻¹⁸ |

The McNemar test on paired problems makes the result unambiguous. On HumanEval, 15 problems are exclusively repaired by execution feedback — zero are exclusively repaired by pylint. On MBPP, 85 problems are exclusively repaired by execution, versus only 2 exclusively by pylint. The p-values (0.0001 and <10⁻¹⁸) indicate that this discrepancy is far beyond statistical noise.

*Figure 1 (figure1\_delta\_comparison.png)* shows the delta bar chart with CI and McNemar p-values, making the execution advantage and pylint regression immediately visible.

## Pylint/Mypy Coverage Analysis — The Mechanism (RQ2)

Why does pylint repair fail on HumanEval — and why does it even help on MBPP if the signal is dominated by noise? The coverage analysis answers the first half.

**Coverage result:** Pylint/mypy flags 100% of the 64 HumanEval baseline failures (bootstrap CI: [100%, 100%]). At first glance, this appears to *contradict* the claim that pylint is uninformative. The resolution is in the category decomposition.

**Table 3: Pylint Flag Category Distribution (64 HumanEval failures, 300 total flags).**

| Category | Flags | Fraction | Type |
|----------|-------|----------|------|
| C (Convention) | 283 | 94.3% | Style (C0304: missing newline, C0114: missing docstring) |
| R (Refactor) | 8 | 2.7% | Style/structure |
| W (Warning) | 7 | 2.3% | Functional (some) |
| E (Error) | 1 | 0.3% | Functional |
| I (Information) | 1 | 0.3% | Informational |

The 100% total coverage is deceptive. It is driven by C0304 ("missing newline at end of file") and C0114 ("missing docstring in public module") — rules that fire on virtually every LLM-generated code snippet because LLMs typically generate code without trailing newlines or module docstrings. These rules fire whether the code is correct or not; they are properties of the *generation context*, not indicators of logical errors.

**Functional coverage** (E+W categories only): 8 out of 64 failures receive a functional flag — 12.5%. This means that in 87.5% of HumanEval failures, pylint's entire feedback is composed of style complaints that provide no diagnostic information about *why* the code failed.

*Figure 2 (fig2\_pylint\_categories.png)* shows the category breakdown visually. *Figure 5 (fig1\_coverage\_bar.png)* shows total vs. functional coverage with confidence intervals.

**Mypy coverage:** 0 out of 64 failures. This confirms that the dominant HumanEval failure mode is not type errors — it is logic and runtime errors, which mypy cannot detect.

The style-function dissociation explains the mechanism: when the LLM receives "missing newline, missing docstring" as its primary feedback on a failed algorithmic solution, it is being prompted to rewrite based on formatting guidance rather than logical diagnosis. On complex HumanEval problems, this rewriting can corrupt the logical structure of a working attempt, explaining the −4.3pp regression.

## Benchmark Asymmetry and Task-Complexity Moderation (RQ3)

Pylint repair hurts HumanEval (−4.3pp) but helps MBPP (+18.3pp). This asymmetry — present despite the same 94.3% C-category dominance in both cases — reveals that task complexity moderates feedback utility.

*Figure 3 (figure2\_per\_round\_trajectory.png)* shows per-round pass@1 trajectories, confirming the direction of each condition on each benchmark and showing that most improvement (or degradation) occurs in round 1.

*Figure 4 (figure1\_pass\_at\_1\_comparison.png)* shows absolute pass@1 values for all four conditions (baseline × HumanEval/MBPP, pylint × HumanEval/MBPP), making the asymmetry visually clear.

**Interpretation:** MBPP's simpler function-completion tasks tend to be shorter (fewer lines, simpler control flow). When the LLM rewrites a solution in response to style guidance (C0304, C0114), it may restructure a syntactically simple function without losing its logical core — even occasionally fixing a functional issue in the process. HumanEval's algorithmic problems (sorting algorithms, string manipulation, mathematical reasoning) involve complex multi-step logic. A style-triggered rewrite is more likely to disrupt the logical structure of a 10-30 line function than a 3-5 line MBPP solution.

**Execution feedback is robust across both benchmarks.** The +4.9pp HumanEval and +40.2pp MBPP improvements — both statistically significant — confirm that execution feedback provides actionable functional information regardless of task complexity. A failing test always tells the LLM *what* went wrong functionally; pylint's 94.3% C-category flags tell it to fix formatting.

## Budget Saturation

At B=1000 output tokens, the token budget is effectively exhausted after round 1 for most problems. Initial generation uses approximately 400–512 tokens (max\_tokens=512); the first repair round uses the remainder. Per-round trajectory data from Figure 3 confirms that rounds 2–3 contribute near-zero incremental improvement under both conditions. The results therefore characterize **single-round repair at B=1000**, not multi-round iterative improvement. This does not invalidate the comparison — both conditions face the same budget constraint — but it narrows the scope of the finding, as we discuss in Section 6.
