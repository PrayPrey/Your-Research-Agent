# Conclusion

We began by observing a coverage paradox: pylint flags 100% of HumanEval baseline failures, yet pylint-guided repair *reduces* HumanEval pass@1 by 4.3 percentage points. Our study shows that this paradox resolves cleanly once coverage is decomposed by flag category. The 100% coverage is a mirage — it is driven by Convention-category style rules (C0304: missing newline, C0114: missing docstring) that fire universally on LLM-generated code regardless of functional correctness. Only 12.5% of HumanEval failures receive a functional (Error or Warning category) flag; mypy coverage is 0%. When the LLM receives "fix your formatting" as its primary repair guidance on a failed algorithmic solution, it may restructure code while addressing style — and on complex HumanEval problems, this rewriting introduces new logical errors.

In this work, we addressed the question of which feedback signal — execution tests or pylint/mypy static analysis — produces larger pass@1 improvement at fixed inference compute (B=1000 output tokens per problem). Our main contributions are:

1. **Iso-compute comparison showing execution dominates.** McNemar's test confirms execution feedback significantly outperforms pylint/mypy on both HumanEval (p=0.0001, exec-only=15 vs. pylint-only=0) and MBPP (p<10⁻¹⁸, exec-only=85 vs. pylint-only=2). Execution feedback improves HumanEval by +4.9pp and MBPP by +40.2pp; pylint/mypy harms HumanEval by −4.3pp.

2. **Style-function dissociation measurement.** Decomposing pylint flags by category reveals that 94.3% are Convention-category style complaints with no functional diagnostic value. This measurement — not previously reported for pylint feedback on code generation failures — shows that coverage and informativeness are decoupled for LLM-generated code.

3. **Benchmark asymmetry as task-complexity moderation.** Pylint repair helps MBPP's simple function-completion tasks (+18.3pp) while harming HumanEval's complex algorithmic tasks (−4.3pp). This asymmetry is consistent with style-guided rewrites being more disruptive on complex multi-step logic than on short, simple functions.

## Future Directions

The style-function dissociation we identify opens several concrete research directions:

**From untested mechanisms:** Per-problem analysis of round-0 vs. round-1 solutions for HumanEval regressions could directly confirm whether pylint feedback triggers structural rewrites (style-guided corruption hypothesis) or merely introduces truncation artifacts. For the 7 HumanEval problems that regressed, comparing the solution structure before and after repair would resolve the competing explanations.

**From unverified assumptions:** Qwen2.5-Coder-7B replication at identical B=1000 would determine whether the feedback type ranking generalizes beyond Llama 3.1 8B. If Qwen shows similar execution dominance, the finding is a property of 7B instruction-tuned models and pylint's signal structure; if Qwen shows different rankings, the interaction with model training becomes the finding.

**From scope extensions:** Filtering pylint to W+E categories only (excluding C-category style flags) would test whether pylint feedback becomes competitive when the noise is removed. Running the comparison at B=2000 or B=4000 would characterize the multi-round regime. Extending to non-Python benchmarks (MultiPL-E) and code-specialized models (DeepSeek-Coder, Qwen2.5-Coder) would establish the generality of the asymmetry.

For LLM code repair, the question is not whether a tool detects errors — it is whether it detects the *right* errors. Pylint detects formatting; execution detects failure. At B=1000 on functional correctness benchmarks, the difference is +40.2pp on MBPP.
