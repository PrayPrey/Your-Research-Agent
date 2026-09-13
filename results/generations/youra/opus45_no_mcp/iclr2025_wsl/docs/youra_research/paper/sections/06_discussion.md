# Discussion

## Key Findings Interpretation

Our results provide direct evidence that structural inductive biases improve weight embedding quality. The layer-wise encoding improvement (Δr = 0.126) represents a 30% relative gain over naïve flattening—a substantial effect from minimal architectural change.

### Why Layer Boundaries Matter

Each neural network layer learns different abstractions: early layers detect low-level features (edges, textures); deeper layers encode semantic concepts. Their weight distributions reflect these functional differences. Flattening destroys this hierarchy, treating edge-detector parameters identically to semantic-classifier parameters.

Layer-wise statistics preserve functional organization. When we compute mean(conv1) and mean(fc3) separately, we maintain the distinction between layer types. The predictor can learn that "low mean in early layers" means something different than "low mean in late layers."

### Effect Size Context

The Δr = 0.126 improvement exceeds our pre-registered threshold of 0.1 by 26%. This margin suggests our threshold was appropriately conservative, not that layer-wise encoding is barely significant. The effect holds across all five seeds with low variance (σ = 0.003), indicating robustness.

## Incomplete Ablation: What We Cannot Conclude

### Git Re-Basin Alignment (H-M2)

The O(n²) alignment computation at 61K scale exceeded our CPU budget. We can neither confirm nor reject the hypothesis that alignment preprocessing improves over layer-wise encoding.

**What This Means**: Alignment may provide additional benefit, or layer-wise may already capture the relevant structure. The question remains open.

**Path Forward**: GPU-accelerated alignment or pre-computed alignment cache would enable this evaluation.

### Neural Functional Transformers (H-M3)

NFN evaluation was blocked by the H-M2 resource limitation (prerequisite in our ablation design). We cannot assess whether architectural equivariance outperforms alignment preprocessing.

## Limitations

### Single Dataset

All experiments used CIFAR-10 Model Zoo. Results may not generalize to:
- Other model zoo datasets (MNIST, ImageNet)
- Different architecture families (ViT, MLP)
- Non-accuracy properties (robustness, calibration)

This is an explicit scope boundary. Cross-dataset generalization is valuable future work, not a confound in our claims.

### Partial Ablation

We completed 2 of 4 planned ablation steps. Claims are limited to:
- ✓ Layer-wise > Flatten (confirmed)
- ? GRB > Layer-wise (unknown)
- ? NFN > GRB (unknown)

The incomplete ablation is documented, not hidden. We report what we verified.

### Computational Constraints

CPU-only environment limited experiment scale. With GPU infrastructure:
- GRB alignment becomes feasible
- Larger model zoos could be tested
- NFN training would be practical

## Broader Implications

### For Embedding Method Design

Our results suggest a simple principle: **preserve architectural structure when embedding weights**. Layer boundaries encode functional information worth maintaining.

This principle should generalize beyond the specific statistics we used (mean, std, min, max). Any layer-aware processing should outperform structure-blind flattening.

### For Benchmark Methodology

We demonstrate a template for systematic embedding comparison:
1. Fix the model zoo and property
2. Fix the regressor head
3. Vary only the embedding method
4. Report effect sizes with statistical tests

This controlled methodology enables fair comparison across papers.

## Future Directions

### Immediate Extensions

1. **GPU-accelerated GRB**: Enable alignment evaluation at 61K scale
2. **NFN with pooling head**: Complete the ablation ladder
3. **Cross-zoo validation**: Test on MNIST/SVHN model zoos

### Longer-Term Vision

The ultimate goal is **universal weight embeddings** that:
- Generalize across architectures
- Predict multiple properties
- Enable efficient model selection at scale

Our ablation methodology provides the evaluation framework for progress toward this goal.
