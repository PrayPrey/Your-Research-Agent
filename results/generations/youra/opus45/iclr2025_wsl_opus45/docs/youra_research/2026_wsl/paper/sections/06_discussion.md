# Discussion

Our experiments establish that LoRA adapter $B$ matrix column spaces encode detectable task-specific geometric signatures. Here we interpret the key findings, acknowledge limitations honestly, and discuss broader implications.

## Key Findings

### Geometric Signatures Are Real and Robust

The existence proof (RQ1) demonstrates that task-category clustering in adapter geometry is not an artifact of experimental confounds or statistical noise. With Cohen's $d = 0.77$ and $p < 10^{-27}$ across 780 pairwise comparisons, the effect is both statistically and practically significant. This validates the core hypothesis: LoRA adapters trained on semantically similar tasks occupy closer regions of Grassmann geometry.

The correlation with FLAN taxonomy (RQ2, $\rho = 0.39$) confirms that this clustering reflects meaningful task relationships, not arbitrary structure. Semantic similarity---as operationalized by established task taxonomies---manifests in geometric similarity of learned transformation subspaces.

### Task Geometry Is a Global Property

The layer-type analysis (RQ3) yielded a surprising negative result: all seven layer types show nearly identical clustering strength ($d = 0.745$--$0.783$), with no significant difference between attention and MLP modules. This refutes our initial hypothesis of layer-specific specialization.

We interpret this finding as evidence that task-relevant information is **distributed uniformly** across the transformer architecture. Fine-tuning on a specific task induces coordinated changes across all layers rather than localized modifications to particular components. This aligns with recent work on distributed representations in transformers [Elhage et al., 2022] and suggests that LoRA's low-rank constraint does not concentrate task information in specific layers.

### Training Stochasticity Is Significant

The P3 control failure (ratio = 0.89 vs. threshold 0.5) reveals that training dynamics contribute substantially to adapter geometry. Adapters trained on the same task with different random seeds exhibit geometric variation comparable to adapters trained on different tasks within the same category.

This does not invalidate our main findings---the task-category signal remains highly significant---but it bounds the precision of geometric signatures. Adapter geometry encodes **both** task structure and training trajectory, making it suitable for coarse-grained category detection but potentially limited for fine-grained task discrimination.

## Limitations

We acknowledge several limitations that should guide interpretation and future work:

### Single Model Family

Our experiments use only TinyLlama-1.1B. While the LLaMA architecture is widely adopted, we cannot claim generalization to other model families (GPT, Mistral, Phi) or larger scales (7B, 70B). The effect may strengthen, weaken, or change qualitatively with model size.

**Mitigation:** The methodology is directly applicable to other models. We prioritized depth of analysis over breadth, but replication studies across architectures are an important next step.

### Coarse-Grained Taxonomy

The FLAN binary taxonomy (same vs. different category) provides only coarse similarity labels. Within-category tasks vary considerably---GSM8K (arithmetic) and StrategyQA (commonsense reasoning) are both "reasoning" but require different capabilities. This coarseness likely explains the moderate correlation ($\rho = 0.39$) rather than strong correlation.

**Mitigation:** Future work could use continuous task embeddings (e.g., SBERT on task descriptions) or hierarchical taxonomies to capture finer-grained similarity.

### Short Training Duration

Three epochs may be insufficient for full convergence, potentially contributing to the high within-task variance (P3 failure). Longer training might yield more stable geometric signatures as adapters converge to task-specific optima.

**Mitigation:** Ablation studies varying training duration (3, 5, 10 epochs) could identify the convergence point for stable signatures.

### LoRA Rank Specificity

We test only $r = 32$. The geometric signal may depend on rank---too low might lack capacity for task-specific structure; too high might diffuse the signal across more dimensions.

**Mitigation:** Rank ablation ($r \in \{8, 16, 32, 64, 128\}$) could identify optimal settings for geometric detectability.

## Implications

### For Research

Our findings open a new research direction: **weight-space learning for parameter-efficient adapters**. While prior work focused on full model populations, we demonstrate that LoRA's low-rank constraint provides natural geometric handles for adapter analysis. This connects PEFT research with Riemannian geometry and representation learning.

The negative finding on layer uniformity contributes to understanding how transformers encode task information---as a distributed, network-wide property rather than layer-localized specialization.

### For Practice

Practitioners managing adapter collections gain a principled similarity metric. Grassmann distance can be computed directly from adapter weights without inference, enabling:

- **Adapter retrieval:** Given a new task, identify geometrically similar existing adapters as initialization candidates
- **Collection organization:** Automatically cluster adapters by geometric similarity
- **Redundancy detection:** Identify adapters that encode similar transformations

The practical utility is bounded by the P3 finding: geometric similarity is reliable for category-level grouping but may not distinguish fine-grained task variations.

## Broader Impact

This work has no direct negative societal impacts. The research focuses on understanding adapter structure rather than deploying models in high-stakes applications.

**Potential positive impacts:** Improved adapter management could reduce redundant fine-tuning, saving computational resources and energy. Better understanding of adapter geometry may also aid interpretability research.

**Potential misuse:** We do not foresee specific misuse vectors for geometric adapter analysis, as the technique reveals structure in existing adapters rather than enabling new capabilities.
