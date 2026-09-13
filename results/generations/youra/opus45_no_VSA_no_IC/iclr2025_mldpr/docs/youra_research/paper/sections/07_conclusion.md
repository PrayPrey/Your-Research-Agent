# Conclusion

We set out to answer whether fine-tuning on narrow benchmarks leaves detectable fingerprints in model representations, and whether such fingerprints could predict generalization failure. The answer is both simpler and more complex than we anticipated.

**Fingerprints are massively detectable.** A simple linear classifier identifies training benchmark origin with 99.51% accuracy — an effect size (Cohen's d = 698) orders of magnitude larger than typical findings in representation learning. This establishes benchmark fingerprints as a real, measurable phenomenon, not a subtle artifact.

**But fingerprint strength does not predict generalization gap.** The BFS-gap correlation (r = 0.022, p = 0.967) is effectively zero. Models with indistinguishably strong fingerprints exhibit varying generalization gaps, suggesting that detectability and deployment risk are decoupled phenomena.

This paradox — that we can identify a model's training benchmark with near-perfect accuracy yet learn nothing about how well it will generalize — points to deeper questions about what fine-tuning actually changes in representations. The fingerprint exists, but it may be orthogonal to the features that matter for transfer.

## Future Directions

**Calibrated fingerprint metrics.** BFS saturation at >0.999 limited our correlation analysis. Temperature-scaled confidence, entropy-based measures, or margin scores may enable variance where raw confidence fails.

**Layer-wise fingerprint analysis.** We examined only the penultimate layer. Fingerprints may emerge differently in earlier convolutional layers versus later semantic layers, with different implications for generalization.

**Intervention studies.** The ultimate test of the fingerprint-gap hypothesis requires intervention: can we reduce fingerprint strength during training, and does generalization improve? Representation regularization or adversarial benchmark debiasing could provide causal evidence.

**Expanded benchmark coverage.** Our proof-of-concept used 2 benchmarks; the full 5-benchmark study with fine-grained visual classification datasets would strengthen the existence finding and potentially reveal correlations obscured by domain heterogeneity.

That 99.5% classification accuracy tells us models encode benchmarks in ways we can easily detect. What it doesn't tell us — yet — is whether and how that encoding harms deployment. Closing that gap is the next chapter.
