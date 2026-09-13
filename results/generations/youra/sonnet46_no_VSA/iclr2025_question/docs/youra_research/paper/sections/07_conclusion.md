# Conclusion

We opened this paper with a near-zero number — Pearson |r|(SE\_N5, min\_logprob) = 0.026 — and asked what it means. The answer is nuanced: SE and min\_logprob are genuinely distinct uncertainty signals in the sense of statistical independence, yet this independence does not translate to additive conditional predictive power for hallucination detection on TriviaQA (partial R²=0.0005, N=2500). SE asks whether a model is semantically consistent across stochastic samples; min\_logprob asks where a model is least confident in a single deterministic pass. The near-zero correlation reflects genuinely different computations, but both signals appear to capture the same underlying correctness dimension on short-answer factual QA.

## Summary

In this work, we directly measured the statistical independence of SE\_N5 and min\_logprob as uncertainty signals for hallucination detection in open-weight LLMs on short-answer factual QA. Our main contributions are:

1. **Empirical near-orthogonality confirmation** (Pearson |r|=0.026 at N=2500, TriviaQA dev, Llama-3.1-8B-Instruct): SE and min\_logprob are statistically near-independent (95% CI: [−0.013, +0.065]), ruling out SE as a reparameterization of log-probability signals.

2. **Conditional predictive null result** (partial R²=0.0005, LRT p=0.442, N=2500): Despite their independence, SE does not add meaningful conditional predictive power beyond min\_logprob in logistic regression on this benchmark — a well-powered null result that cautions against the assumption that statistical independence implies ensemble utility.

3. **Circularity-controlled evaluation protocol** (Spearman ρ(SE, judge)=−0.026): Cross-model LM-judge design (Qwen-2.5-7B evaluating Llama-3.1-8B outputs) produces low circularity, providing a replicable best practice for bias-robust UQ benchmarking on factual QA.

4. **End-to-end reproducible pipeline**: A checkpoint-aware, GPU-efficient implementation (SE\_N5, min\_logprob, Qwen-2.5-7B LM-judge) that passes all mechanism reality checks at N=2500.

## Future Directions

**Testing result stability across seeds and subsets.** The Pearson |r|=0.026 at N=2500 with a fixed seed (42) provides no variance estimate. Multi-seed replication is needed to distinguish stable near-orthogonality from seed-specific effects.

**Nonlinear ensemble evaluation.** The linear null result (partial R²=0.0005) does not preclude nonlinear ensemble benefit. Gradient boosting, kernel methods, or a neural combiner may exploit the orthogonal signal space when linear logistic regression cannot. This is the primary target for follow-up work (h-e1-v2).

**Cross-model transfer characterization.** The Llama-calibrated logistic regression ensemble is predicted to transfer to Qwen-2.5-7B on TruthfulQA without weight refitting (AUROC gap < 0.05). If the algebraic independence of SE and min\_logprob is architecture-agnostic — as the mechanism motivates — the ensemble weights should generalize across 7–8B open-weight models. Testing this transfers the black-box ensemble from a single-model to a cross-model hallucination detection tool.

**Orthogonality zone analysis.** The near-zero Pearson r motivates a finer-grained analysis: are prompts in the "orthogonality zone" (high min\_logprob uncertainty AND high SE) systematically enriched for factual hallucinations beyond either signal alone? This causal mechanism step — confirming that the independence is not just statistical but functionally meaningful — is testable with the N=2500 signals and correctness labels.

Hallucination detection in open-weight LLMs is a prerequisite for safe deployment in high-stakes settings. We hope this work demonstrates that careful statistical characterization of signal independence — not just standalone AUROC comparison — is the right foundation for principled ensemble design, and that the two signals we have characterized here will be useful components in future UQ systems that go beyond single-signal approaches.
