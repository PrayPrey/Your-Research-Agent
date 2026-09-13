# Conclusion

We began by asking whether model quality can be predicted from weights alone—across architectures. Our work provides a nuanced answer: heavy-tailed self-regularization theory extends to Vision Transformer attention mechanisms, but cross-model comparison requires controlling for training provenance.

## Summary

In this work, we conducted the first systematic measurement of heavy-tailed exponents on 53 Vision Transformer models from HuggingFace Model Hub. Our main contributions are:

1. **Extension of HT-SR theory to Transformers.** We demonstrated that heavy-tailed exponents can be computed for ViT attention weight matrices, with all processed models exhibiting power-law distributions (α ∈ [2.20, 18.92]).

2. **Identification of variance sources.** We found that training provenance—not architectural variation—dominates cross-model variance, with 12× variance reduction (σ = 2.868 → 0.24) through family stratification.

3. **Practical guidance.** We established that weight-based model selection for diverse hubs must incorporate training origin metadata, not just architectural similarity.

## Future Directions

This work opens several promising directions grounded in our experimental findings.

**From untested alternative explanations.** Our outlier analysis suggests task-specific fine-tuning (violence detection, medical imaging) drives α variance. Future work should stratify models by training task and compare α variance within task groups to confirm whether task objective is the dominant factor.

**From unverified assumptions.** We assumed ImageNet accuracy reported on HuggingFace is accurate. Re-evaluating a subset of models on the validation set would verify this assumption and potentially identify confounds from incorrect metadata.

**From scope extensions.** The success of family stratification on google/vit-* (σ = 0.24) suggests the approach may generalize. Extending this analysis to ResNet, ConvNeXt, and Swin families with larger samples per family would test the generality of our findings.

## Closing Remarks

Our findings carry practical implications for the growing ecosystem of model hubs. As practitioners face the challenge of selecting among thousands of pretrained models, weight-based quality metrics offer a compute-efficient screening tool. However, these metrics are meaningful only with appropriate controls for model provenance. We hope this work encourages the research community to incorporate training metadata into cross-architecture analysis, moving toward truly universal weight-based model selection.
