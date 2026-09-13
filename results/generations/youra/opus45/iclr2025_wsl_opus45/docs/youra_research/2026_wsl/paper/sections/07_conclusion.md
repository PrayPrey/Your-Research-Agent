# Conclusion

We began by observing that practitioners accumulate LoRA adapters with no principled way to understand their relationships---selection relies on metadata tags and manual curation rather than the geometric structure the adapters themselves contain. Our work demonstrates that this geometric structure exists and is detectable: LoRA adapter $B$ matrix column spaces encode task-specific signatures that cluster by semantic similarity.

## Summary

In this work, we addressed the challenge of understanding LoRA adapter relationships by applying controlled experimental methodology from weight-space learning to parameter-efficient adapters. Our key insight is that the low-rank constraint of LoRA provides natural geometric handles for adapter analysis---the $B$ matrix column space defines a transformation subspace whose alignment can be measured via Grassmann distance.

Our main contributions are:

1. **Existence proof:** We demonstrated that within-category LoRA adapters exhibit significantly smaller Grassmann distances than between-category adapters (Cohen's $d = 0.77$, $p < 10^{-27}$), establishing that task-category clustering in adapter geometry is real and statistically robust.

2. **Mechanism validation:** We showed that geometric similarity correlates with semantic similarity as defined by FLAN taxonomy (Spearman $\rho = 0.39$, $p < 10^{-28}$), confirming that the clustering reflects meaningful task relationships.

3. **Negative finding:** We found that task-category clustering is distributed uniformly across all transformer layer types, refuting the hypothesis of layer-specific specialization and revealing that geometric signatures are a global network property.

## Future Directions

Our findings open several avenues for future research:

**Robustness and convergence.** The P3 control failure (within-task variance ratio = 0.89) indicates that training stochasticity significantly influences adapter geometry. Future work should investigate whether longer training (5--10 epochs) or seed ensembling yields more stable geometric signatures, potentially improving fine-grained task discrimination.

**Generalization across scales.** Our experiments used TinyLlama-1.1B. Replication on larger models (Llama-2-7B, Mistral-7B) would establish whether the effect scales with model size or changes qualitatively. The moderate correlation with FLAN taxonomy ($\rho = 0.39$) suggests that continuous task similarity metrics might yield stronger signals.

**Practical applications.** The validated effect size ($d = 0.77$) is sufficient for practical applications. We envision adapter retrieval systems that use Grassmann distance to identify geometrically similar adapters for transfer or initialization---turning adapter collections into searchable knowledge bases rather than opaque repositories.

## Closing Remarks

LoRA adapters are not opaque artifacts. Their $B$ matrix column spaces carry geometric fingerprints of their training tasks, detectable without inference and meaningful at the category level. As parameter-efficient fine-tuning continues to proliferate, geometric understanding of adapters offers a principled foundation for managing, comparing, and leveraging the growing ecosystem of specialized models.
