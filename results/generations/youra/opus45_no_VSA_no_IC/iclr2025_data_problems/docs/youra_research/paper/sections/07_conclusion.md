# Conclusion

We began by observing a puzzle: leading data attribution methods—TRAK, TracIn, and Kronfluence—can disagree as dramatically as their difference from random chance, yet researchers routinely treat them as interchangeable. This work demonstrates that the disagreement is not noise but signal: different attribution algorithms embed different mathematical operations that create characteristic *fingerprints*—systematic patterns of sensitivity to memorization, feature transfer, and spurious association.

## Summary

Our contributions address both the characterization and the boundaries of attribution method fingerprinting:

**Contrastive mode probing.** We introduced a methodology for measuring attribution method sensitivity to specific influence modes using carefully constructed test cases. This provides a principled framework for comparing methods beyond accuracy benchmarks.

**Quantified dissociation.** We demonstrated that methods are not merely "different" but *radically* different: inter-method variance exceeds intra-method variance with F=1423.55, and effect sizes are extremely large (Cohen's d=20.64). The fingerprints are stable within methods (Cronbach's α > 0.96), enabling reliable characterization.

**Scope boundaries.** We discovered that fingerprints transfer within architectural families (ResNet-ViT r=0.80) but invert across fundamentally different architectures (ConvNeXt shows negative correlations). This bounds the generalization of our framework and motivates architecture-aware calibration.

These findings transform the question from "which attribution method wins" to "what does each method measure"—enabling practitioners to match methods to use cases rather than seeking a nonexistent universal solution.

## Future Directions

Our results open several grounded directions for future work:

**Per-architecture calibration.** The ConvNeXt inversion suggests that cross-family fingerprinting requires learned transforms. Developing calibration methods that normalize mode profiles across architecture classes would extend the applicability of fingerprinting to heterogeneous model deployments.

**LLM-scale validation.** Our experiments used vision models as a computational proxy. Validating the fingerprinting framework on LLaMA, Mistral, and Qwen at 7B+ scale would confirm mechanism transfer to the language domain and characterize any modality-specific effects.

**Method ensemble strategies.** Given that methods emphasize different influence aspects, combining complementary fingerprints may provide more complete influence characterization than any single method. Investigating how to aggregate attributions across methods based on their mode profiles is a natural extension.

**Automatic method selection.** Building on characterized fingerprints, developing a recommendation system that matches attribution methods to application requirements (fairness audit vs. memorization detection vs. feature understanding) would provide practical guidance for practitioners.

## Closing Remarks

The diversity of attribution methods is a feature, not a bug. Different methods "see" influence through different mathematical lenses, just as different cameras capture the same scene with different emphases. By characterizing these lenses, we move from treating method disagreement as a problem to leveraging it as a tool—choosing methods that measure what we care about for the task at hand. As data attribution becomes increasingly central to model governance, data valuation, and fairness auditing, understanding *what* our methods measure becomes as important as improving *how well* they measure it.
