# Conclusion

We began by observing that every major LLM pipeline uses data curation, yet optimal filtering parameters remain undiscovered. Our work demonstrates that this gap can be addressed through systematic dose-response analysis, treating curation parameters as continuous variables rather than discrete configuration choices.

## Summary

In this work, we addressed the lack of controlled ablation studies for LLM data curation by applying fixed-token experimental design to map parameter effect surfaces. Our key insight—that perplexity filtering exhibits a concave dose-response relationship due to the quality-diversity tradeoff—enables principled threshold selection.

Our main contributions are:

1. **Existence of non-monotonic dose-response.** We demonstrated that the relationship between perplexity thresholds and benchmark performance is quadratic (R²=0.985), not linear. This validates the quality-diversity tradeoff as an empirical phenomenon and provides the first controlled evidence that intermediate thresholds outperform both extremes.

2. **Mechanistic validation through convergence analysis.** We showed that noise dilution accounts for the left side of the curve (unfiltered training shows 40% higher convergence AUC) while diversity loss explains the right side (p90 filtering degrades final performance despite reasonable convergence). This mechanistic understanding supports principled rather than heuristic parameter selection.

3. **Practical guidance with scale transfer.** We demonstrated 1.32% improvement over RedPajama defaults and showed that optimal thresholds transfer across model scales with ratio 0.85, enabling efficient optimization at smaller scales with predictable extrapolation.

## Future Directions

This work opens several promising directions grounded in our experimental findings.

**From untested alternative explanations:** Our experiments used only GPT-2 architecture. The non-monotonic pattern may be architecture-specific rather than universal. Future work should replicate the dose-response sweep with Llama-style architectures to test generalization. If the pattern persists, it suggests a fundamental property of data curation; if not, architecture-specific guidance will be needed.

**From unverified assumptions:** We assumed that KenLM 5-gram perplexity is an appropriate quality signal. Alternative signals—classifier-based quality scores, BERT perplexity, or semantic filtering—may yield different optimal thresholds or sharper dose-response curves. Systematic comparison of quality signals is needed to validate or improve upon the KenLM baseline.

**From scope extensions:** Our experiments studied perplexity and deduplication independently. Joint optimization across both dimensions may reveal interaction effects and a more efficient Pareto frontier. The computational cost of full grid search (100+ configurations) is substantial but may be justified given the potential gains.

## Closing

Data curation has long been treated as a pipeline preprocessing step—important but unoptimized. Our findings suggest it deserves the same systematic attention as architectural choices or training hyperparameters. The optimal perplexity threshold of approximately p50 provides a validated starting point, but more importantly, the dose-response methodology offers a framework for continued optimization as corpora and architectures evolve.

We hope this work encourages the community to treat curation parameters as first-class optimization targets, transforming data preparation from craft to science.
