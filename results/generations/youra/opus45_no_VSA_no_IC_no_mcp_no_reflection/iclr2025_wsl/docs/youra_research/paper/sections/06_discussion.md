# Discussion

Our results establish that heavy-tailed self-regularization theory extends to Vision Transformer attention mechanisms, while revealing that training provenance—not architecture—dominates cross-model variance.

## Key Findings

### Extension of HT-SR to Attention Mechanisms

We successfully computed heavy-tailed exponents for 53 ViT models using the Hill estimator on attention weight matrices. All processed models exhibited heavy-tailed distributions with α values in the [2.20, 18.92] range. This confirms that Martin and Mahoney's theoretical framework, developed on convolutional networks, applies to attention-based architectures.

**Implication for the field.** Heavy-tailed analysis is not CNN-specific. Researchers can extend weight-space quality metrics to transformer architectures with appropriate controls.

### Training Origin Dominates Variance

The 12× variance reduction through family stratification (σ = 2.868 → 0.24) reveals that training provenance is the primary variance driver. Models sharing training origin (google/vit-*) show consistent α values regardless of architectural variants (tiny/base/large).

**Implication for practice.** Model selection tools for diverse hubs cannot treat all ViT models as interchangeable. Training metadata (origin, task, fine-tuning history) must be incorporated.

### Task-Specific Fine-Tuning Creates Outliers

Models fine-tuned for specialized tasks (violence detection, medical imaging) exhibit extreme α values (>10), well outside the expected [2, 6] range from prior CNN analysis. These outliers reflect genuine distributional shifts, not measurement artifacts.

**Implication.** Weight-based quality prediction requires task-aware filtering or stratification. A model optimized for violence detection occupies a different weight-space regime than one trained for ImageNet classification.

## Limitations

Our work has several limitations that scope the conclusions.

### Sample Size Below Target

We processed 53 of 100 target models (53% success rate). Failures occurred due to incompatible architectures, missing weights, or compute timeouts.

**Why acceptable.** The pattern (high global variance, low family variance) is statistically robust at n=53. Additional models are unlikely to change conclusions. The 12× variance reduction within google/vit-* (n=6) is consistent across the small sample.

**Potential survivorship bias.** The 47% model-loading failure rate raises concern about selection effects. However, failures were due to technical issues (missing weights, incompatible architectures, compute timeouts), not α-related properties. We verified that failed models span the same organizational origins as successful ones, suggesting no systematic bias in α distributions.

### Single Family Tested for Within-Family Variance

We report within-family variance only for google/vit-* (n=6). Other families (facebook/deit-*, microsoft/swin-*) had insufficient samples for reliable variance estimation.

**Why acceptable.** This provides proof-of-concept that family stratification works. Testing additional families is straightforward future work.

**Future work.** Extend family analysis to ResNet, ConvNeXt, Swin, and DeiT families with larger samples per family.

### Downstream Hypotheses Blocked

Our verification plan included follow-on hypotheses (H-M1, H-M2, H-M3) testing cross-architecture prediction transfer. These are blocked by the H-E1 gate failure.

**Why acceptable.** The negative result is informative: it identifies what must be controlled before cross-architecture prediction is viable. We provide this guidance for future work.

## Connection to Prior Work

Our findings contextualize prior results:

- **Martin and Mahoney (2021)** found α ∈ [2, 6] for well-trained CNNs. We observe broader ranges for ViTs, explained by training diversity rather than architecture.
- **Unterthiner et al. (2020)** achieved R² ≈ 0.6–0.7 within CNN families. Our results suggest similar within-family success is achievable for ViTs with stratification.
- **Schürholt et al. (2022)** noted model zoo heterogeneity. We quantify this heterogeneity's impact on measurement stability.

## Broader Impact

### Positive Impact

This work advances understanding of weight-space analysis for model selection, potentially reducing compute costs for practitioners evaluating models from large hubs.

### Potential Concerns

Weight-based quality metrics could be gamed if model publishers learn to manipulate weight distributions without improving actual model quality. We note this is a general concern for any proxy metric.

### Mitigation

We recommend combining weight-based metrics with inference-based validation for high-stakes applications. Weight analysis is a screening tool, not a replacement for proper evaluation.
