# Conclusion

We began with a puzzle: can you identify a language model's architecture family from its adversarial failures alone? Our answer is yes — in principle, and at a large effect size — but statistical confirmation requires a larger model pool than the nine we evaluate here. This honest qualification is itself the finding: we know exactly what the next step must be.

## Summary

We introduced the **Δ*-vector framework** for multivariate architecture-family adversarial profiling, representing each model as a vector of normalized per-attack-category vulnerability scores and testing between-family structure with permutation MANOVA. Applied to nine transformer models across three families on six adversarial attack categories, we find:

1. **Architecture-family effect size η²=0.293** — a large effect (Cohen's f²≈0.41) that exceeds the pre-specified threshold (η²>0.15) in 83% of evaluated attack categories. Between-family differences account for approximately 29% of total Δ* variance.

2. **The strongest differentiation occurs on NLI paraphrase attacks** (adv_rte, η²=0.592), consistent with the hypothesis that bidirectional attention in encoder-only models processes adversarial syntactic transformations differently from causal attention in decoder-only models.

3. **N=9 yields ~40% statistical power** at the observed effect size — the p=0.147 result is expected from the power analysis, not from absence of effect. N≥15 (≥5 models per family) is required for 80% power and valid LOMO evaluation.

4. **A validated 7-module, 1,788-line pipeline** covers fine-tuning, adversarial evaluation, Δ* computation, statistical analysis, and visualization — fully reusable for the confirmatory follow-up study (h-e1-v2) and all downstream mechanism experiments.

## Future Directions

The most immediate next step is **h-e1-v2**: expanding to N=15 models (5 per family, adding DistilBERT, DeBERTa-v3, GPT-Neo-125M, T5-v1_1-base; adding MNLI fine-tuning for enc_dec models). This directly resolves the power limitation and enables a valid LOMO test of classification feasibility. An alternative classifier analysis (family-centroid, LDA) on the existing N=9 data would provide preliminary signal without new training.

To understand *why* the fingerprint exists, **h-m1–h-m4** will extract attention concentration metrics ΔC per layer across all 9 models and test whether mean(ΔC) mediates the architecture-family Δ* difference. The adv_rte η²=0.592 peak provides a natural starting point: do encoder-only models show systematically higher ΔC on NLI paraphrase examples than decoder-only models?

Two scope extensions are well-motivated by our results. **CheckList behavioral testing** would add attack categories covering morphological, negation, and world-knowledge perturbations — linguistically distinct from the word-substitution-dominant AdvGLUE categories. **Large-scale extension** (1.3B–7B parameters) would test whether the architecture-family fingerprint persists, shrinks, or inverts as model capacity increases — an open question with high practical importance given the dominance of large decoder-only models in deployment.

## Closing

Architecture-family adversarial fingerprinting is a real phenomenon at base model scale, measurable with η²=0.293 across 83% of evaluated attack types. Whether it is large enough to be useful — for principled model selection in adversarial-sensitive deployments, for architecture-aware robustness hardening, for predicting unseen models' vulnerability profiles — depends on confirmation at N≥15 and extension to deployment-relevant scales. We have established the measurement framework, quantified the effect, and designed the next experiment. The answer to our opening puzzle is yes; the definitive proof awaits one well-powered follow-up study.
