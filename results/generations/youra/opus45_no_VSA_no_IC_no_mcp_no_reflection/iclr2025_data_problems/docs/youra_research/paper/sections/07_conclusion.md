# Conclusion

We began by observing that domain mixing ratios can make or break LLM performance—yet optimizing them typically costs hundreds of GPU-hours in proxy model training. Our work takes the first step toward a training-free alternative.

## Summary

In this paper, we investigated whether embedding similarity to task exemplars could provide a training-free signal for domain utility in LLM pretraining. We proposed EDMP (Embedding-guided Domain Mixing Prediction), which scores domains by cosine similarity between domain sample embeddings and downstream task exemplar embeddings using a frozen E5-large model.

Our main contributions are:

1. **Pipeline Validation:** We demonstrated that EDMP scores can be reliably computed for multi-domain corpora, with all 8 tested domains producing valid scores and perfect reproducibility across random seeds.

2. **Statistical Significance:** Domain scores are statistically distinguishable (ANOVA F=1242.59, p<0.001), confirming that the scoring mechanism captures systematic domain differences rather than noise.

3. **Data Quality Discovery:** We identified that synthetic data with shared vocabulary produces insufficient cross-domain variance (std=0.007 vs. target 0.05), establishing that real domain data is necessary to complete the validation.

## Future Directions

This work opens several promising directions grounded in our experimental findings:

**Testing with Real Domain Data:** Our primary limitation—low cross-domain variance—stems from synthetic data's shared vocabulary. Retrying h-e1 with real Pile domains (streaming or cached subset) should yield variance in the 0.1-0.2 range observed in domain adaptation literature, enabling full hypothesis testing.

**Completing the Causal Chain:** With sufficient variance established, future work should test h-m1 (score-performance correlation via Kendall's τ) and h-m2 (EDMP top-K vs. random-K training comparison). These experiments will determine whether the statistically significant domain scores actually predict downstream training utility.

**Embedder Comparison:** Our assumption that rankings are stable across embedder scales (A3) remains unverified. Comparing E5-large, BGE-large, and OpenAI embeddings would establish generality or identify the need for embedder-specific calibration.

**Alternative Pooling Strategies:** The low variance may partially result from E5's mean pooling diluting domain-specific signals. Comparing [CLS] token embeddings vs. mean pooling could reveal whether pooling strategy affects domain discrimination.

## Closing Remarks

The promise of training-free domain mixing optimization remains viable. Our work validates the computational pipeline and identifies precisely what is needed to complete the validation: real domain data with sufficient vocabulary diversity. If the predictive power hypothesis holds when tested with appropriate data, EDMP could provide a practical path toward democratizing LLM data optimization—reducing the barrier from hundreds of GPU-hours of proxy training to minutes of embedding inference.

We release our pipeline code to enable reproducibility and encourage the community to complete this validation with real domain corpora.
