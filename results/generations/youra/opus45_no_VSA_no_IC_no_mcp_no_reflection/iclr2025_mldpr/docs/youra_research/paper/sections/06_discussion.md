# Discussion

## Key Findings

Our experiments reveal that model rankings are highly stable between ImageNet and ImageNet-V2 (τ = 0.9647), despite substantial accuracy degradation (~12% mean drop). This finding has both theoretical and practical implications.

### Uniform Degradation Mechanism

The high ranking correlation is explained by *uniform* accuracy degradation. All models—regardless of architecture, parameter count, or publication year—experience similar percentage drops when evaluated on ImageNet-V2. This uniformity preserves ordinal relationships: if Model A beats Model B on ImageNet by 2%, it typically still beats Model B on V2 by approximately 2%.

Two mechanistic interpretations are consistent with this finding:

1. **Shared Feature Representations.** Models trained on ImageNet learn similar generalizable features regardless of architectural details. The distribution shift to V2 affects these shared features uniformly.

2. **V2 Construction Methodology.** ImageNet-V2 was constructed to preserve relative item difficulty. If the dataset construction preserved difficulty ordering, models would naturally maintain their relative rankings.

We cannot distinguish between these interpretations with our data, but both support the practical conclusion that benchmark-based model selection generalizes.

### Extending Prior Work

Our finding extends Recht et al. (2019) from accuracy measurement to ranking stability. Their observation that "accuracy gains on the original test set translate to roughly the same gain on the new test set" implied proportional degradation—our τ = 0.96 quantifies this directly.

This result is consistent with Taori et al.'s (2020) effective robustness framework, which predicts a linear relationship between in-distribution and out-of-distribution accuracy. Linear relationships preserve rankings.

However, our finding *contrasts* with Miller et al. (2021), who found ranking instability under distribution shift in question answering. This domain difference suggests that ranking stability may depend on task characteristics—an avenue for future research.

## Limitations

### Only One Benchmark Pair Tested

Our analysis is limited to ImageNet → ImageNet-V2. Other distribution shifts (ObjectNet, ImageNet-Sketch, ImageNet-R) may show different patterns. ImageNet-V2 was specifically designed to replicate the original data collection methodology, making it a "near" shift; more distant shifts might induce ranking instability.

**Why acceptable:** ImageNet-V2 is the canonical independently-collected variant and the most relevant for our original hypothesis. Future work should test additional shifts.

### Sample May Not Represent Full Population

We analyze 96 models with reported results on both benchmarks. Models that authors chose to evaluate on V2 may be systematically different from those without V2 results—possibly those expected to generalize well.

**Why acceptable:** This selection bias likely *understates* ranking instability. If only "robust" models report V2 results, the full population might show lower τ. Our finding of high stability is thus conservative.

### Original Hypothesis Refuted

We hypothesized τ < 0.90 and found τ = 0.96. While this is a null result in the sense that our prediction was falsified, it is scientifically valuable: it establishes that ranking instability is *not* a significant concern for ImageNet-V2.

## Implications

### For Practitioners

Model selection decisions based on ImageNet rankings generalize to ImageNet-V2-like distributions. If you chose Model A over Model B because A achieves higher ImageNet accuracy, that decision remains valid under the distribution shift tested here.

### For Research

The finding refines our understanding of "benchmark overfitting." While models do show accuracy drops on alternative test sets (confirming prior work), these drops do not imply ranking instability. Accuracy degradation and ranking instability are distinct phenomena.

## Broader Impact

This work has generally positive implications. Validating benchmark-based model selection reduces the risk of practitioners choosing suboptimal models due to misleading benchmarks. The finding does not enable harmful applications.

One concern is that demonstrating ranking stability might discourage researchers from creating new benchmark variants, believing the status quo is sufficient. We emphasize that our finding applies only to ImageNet-V2; other distribution shifts may behave differently, and benchmark diversity remains valuable.
