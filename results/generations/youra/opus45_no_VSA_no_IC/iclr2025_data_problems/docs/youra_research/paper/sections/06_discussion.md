# Discussion

Our experiments validate the fingerprinting hypothesis while revealing important scope limitations. We discuss key findings, practical implications, and honest limitations.

## Key Findings

### Attribution Methods Are Radically Different

The F-ratio of 1423.55 far exceeds what we anticipated (threshold: 4.0). This indicates that method choice is not a minor implementation detail—different methods measure fundamentally different aspects of training data influence. The practical implication is significant: practitioners cannot treat TRAK, TracIn, and Kronfluence as interchangeable tools. A memorization audit using TRAK may identify completely different influential examples than the same audit using Kronfluence.

This finding reframes the DATE-LM benchmark result: the lack of a single dominating method is not a failure to find the "best" method, but an inherent consequence of methods measuring different phenomena. There may be no universal "best" because "influence" is multidimensional.

### Fingerprints Enable Method Selection

The stability of mode profiles (α > 0.96) means fingerprints are reliable signatures, not noisy artifacts. This opens a path toward principled method selection:

- **Memorization detection:** Methods with high memorization sensitivity (TRAK shows the strongest response)
- **Feature understanding:** Methods emphasizing feature transfer for interpretability studies
- **Robustness auditing:** Methods sensitive to spurious associations for shortcut detection

Rather than asking "which method is best," practitioners can ask "which method measures what I care about."

### Architecture Dependence Bounds Generalization

The ConvNeXt inversion is our most significant negative result. The near-perfect negative correlation (r = -0.99 vs ViT) suggests that fingerprints are not purely method-intrinsic—architecture class fundamentally shapes how gradient-based attribution operates.

We hypothesize this stems from ConvNeXt's depthwise separable convolutions, which factorize spatial and channel operations differently than standard convolutions or attention. This creates different gradient flow patterns that invert mode sensitivities. The positive transfer between ResNet and ViT (r = 0.80) suggests that despite architectural differences (convolution vs attention), similar gradient aggregation patterns preserve fingerprints.

**Scope refinement:** Our original claim of "transfer across model families" must be qualified to "transfer within architectural families." Cross-family fingerprinting requires architecture-aware calibration—a direction for future work.

## Limitations

We acknowledge several limitations of this work:

### L1: Architecture-Dependent Transfer

As discussed, mode profiles do not transfer universally. Results apply to within-family comparisons; cross-family (CNN↔Modern CNN) requires calibration. This limitation directly constrains the generalizability of our fingerprinting framework.

**Mitigation:** The fingerprinting methodology remains valid—practitioners should apply it within architectural families or develop calibration transforms for cross-family comparison.

### L2: CPU-Only Execution

Due to CUDA driver incompatibility, all experiments ran on CPU with reduced scale (5 epochs, 100 probes/mode vs. planned 200 epochs, 1000 probes/mode). While effect sizes far exceed thresholds (F=1423 >> 4, α=0.96 >> 0.8), suggesting conclusions are robust, absolute magnitudes may shift at full scale.

**Mitigation:** Effect size margins are large enough that directional conclusions should hold. GPU-scale replication is straightforward future work.

### L3: Vision Proxy for LLM Hypothesis

The original motivation involved LLM attribution (LLaMA, Mistral, Qwen at 7B scale), but validation used vision models due to computational constraints. The mechanism—gradient-based attribution methods embedding different inductive biases—should transfer theoretically, and Kronfluence has been demonstrated at 52B scale [Anthropic, 2023].

**Mitigation:** The vision-validated mechanism provides proof-of-concept. LLM-scale validation is a priority for future work.

### L4: Limited Mode Coverage

We operationalized three influence modes (memorization, feature transfer, spurious association). Other modes may exist (e.g., curriculum effects, batch normalization artifacts) that our probes do not capture.

**Mitigation:** Our framework is extensible—additional probe types can characterize additional modes. The three modes chosen cover the most commonly discussed influence types in the literature.

## Broader Impact

### Positive Impacts

Our fingerprinting framework can improve data attribution practice by enabling informed method selection. This supports:
- **Fairness audits:** Choosing methods sensitive to group-specific memorization
- **Data valuation:** Understanding what "influence" a method measures before assigning data value
- **Model debugging:** Matching attribution method to failure mode being investigated

### Potential Concerns

The finding that methods produce different results could be misused to "shop" for attribution methods that produce desired conclusions. We emphasize that method differences are not a bug but a feature—they reveal the multidimensional nature of influence. Responsible practice requires acknowledging which aspects of influence a chosen method emphasizes.

## Future Work

**Per-architecture calibration:** Develop linear or affine transforms that normalize mode profiles across architecture classes, enabling cross-family fingerprinting.

**LLM-scale validation:** Apply the fingerprinting framework to LLaMA-7B, Mistral-7B, and Qwen-7B to validate mechanism transfer to language models.

**Method ensemble strategies:** Investigate whether combining methods with complementary fingerprints provides more complete influence characterization than any single method.

**Automatic method selection:** Build a recommendation system that matches attribution methods to application requirements based on mode profile matching.
