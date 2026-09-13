# Conclusion

We began by observing that models lose 10-14% accuracy on ImageNet-V2, raising natural concerns about whether benchmark rankings transfer to independently-collected test sets. Our work shows that—contrary to expectation—rankings are remarkably stable. The model you would choose based on ImageNet performance is, with 96% confidence, the same model you would choose based on ImageNet-V2.

## Summary

In this work, we addressed the question of ranking stability under distribution shift by conducting the first systematic Kendall-τ analysis between ImageNet and ImageNet-V2 leaderboards.

Our main contributions are:

1. **Ranking stability measurement.** Across 96 models, we find Kendall-τ = 0.9647 with 95% CI [0.9454, 0.9795], substantially above our pre-registered threshold of 0.90. Rankings are highly preserved.

2. **Uniform degradation mechanism.** We show that accuracy drops are approximately uniform (mean 11.68%, SD 1.87%), explaining why rankings remain stable despite substantial accuracy loss.

3. **Practical validation.** Our results indicate that benchmark-based model selection generalizes to ImageNet-V2-like distributions, providing practical guidance for practitioners.

## Future Directions

This work opens several promising directions grounded in our experimental findings:

**Testing Alternative Distribution Shifts.** Our analysis is limited to ImageNet-V2, which was designed to replicate the original data collection. Distribution shifts with different characteristics—ObjectNet, ImageNet-Sketch, ImageNet-R—may show different ranking stability patterns. The methodology we developed applies directly to these settings.

**Architecture-Stratified Analysis.** Our aggregate τ = 0.96 may mask architecture-specific effects. ViT-based models may behave differently from CNNs under distribution shift, given their different inductive biases. Stratified analysis could reveal whether certain architecture families are more susceptible to ranking shifts.

**Developing Theory.** What properties of a distribution shift determine whether rankings are preserved? Our finding of uniform degradation on V2 suggests that "difficulty-preserving" shifts maintain rankings. A theoretical framework characterizing such shifts would provide guidance for benchmark design.

## Closing Remarks

The distinction between accuracy degradation and ranking instability is subtle but practically important. A model selection decision—choosing Model A over Model B—depends on relative performance, not absolute accuracy. Our finding that rankings are preserved (τ = 0.96) despite accuracy drops (~12%) validates the continued use of ImageNet as a model selection benchmark, at least for ImageNet-V2-like distribution shifts.

As the machine learning community develops new benchmarks and evaluation paradigms, we hope this work encourages attention to ranking stability as a distinct and measurable property, complementing the traditional focus on absolute accuracy.
