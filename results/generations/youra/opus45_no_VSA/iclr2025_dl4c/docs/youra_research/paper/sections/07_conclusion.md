# Conclusion

We began by asking whether RL training transfers to improved test-time refinement. Despite RL fine-tuning being standard practice for code generation and test-time refinement becoming the dominant inference paradigm, no prior work had systematically measured their interaction. Our work addresses this gap by providing the first factorial experimental framework for measuring Training×Refinement interaction.

## Summary

Our main contributions are:

1. **Factorial experimental framework.** We designed a 2×2 factorial experiment (CE/RL × single-shot/refined) with GLMM statistical analysis that directly estimates the interaction term. All four conditions execute successfully, demonstrating the methodology is implementation-ready.

2. **I(F;E) metric operationalization.** We implemented feedback-edit mutual information measurement via the MINE neural estimator, providing a mechanistic probe beyond aggregate accuracy. The estimator runs correctly and produces bounded estimates, ready for full-scale experiments.

3. **Diversity manipulation infrastructure.** Our FeedbackDiversityController achieves 1.1-bit entropy separation between high-diversity (H=2.0 bits) and low-diversity (H=0.9 bits) conditions, enabling controlled ablation of diversity's role in superadditivity.

4. **Validated experimental code.** Three of four sub-hypotheses have code-validated infrastructure. All code paths execute without runtime errors, producing expected artifacts (results.json, figures).

## Future Directions

This work opens several research directions grounded in our validated infrastructure:

**Full-scale empirical validation.** Our smoke tests validate methodology, not hypothesis truth. Full experiments with 10+ epochs on HumanEval+ (164 problems) with 3 seeds will determine whether the superadditive interaction exists. Expected runtime: ~24 hours on GPU.

**Scale analysis.** Our findings are limited to CodeT5+-220M. Extending to larger models (770M, 3B) would reveal whether the interaction effect depends on model capacity. If superadditivity holds across scales, the mechanism is fundamental; if it diminishes with scale, larger models may already have sufficient feedback-conditioning from pretraining.

**Training objective optimization.** If superadditivity is confirmed, the natural next step is designing RL objectives that explicitly optimize for refinement synergy rather than single-shot accuracy. Our I(F;E) metric could serve as an auxiliary training signal.

By providing validated infrastructure for measuring Training×Refinement interaction, we enable the research community to systematically investigate how training and inference investments combine—a question with both scientific interest and practical implications for compute allocation.
