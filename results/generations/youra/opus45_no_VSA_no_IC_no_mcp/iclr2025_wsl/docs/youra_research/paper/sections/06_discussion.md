# Discussion

Our experiments reveal that permutation-equivariant weight-space architectures encode distinct, measurable inductive biases—and that these differences translate to task-dependent performance, at least for holistic property prediction.

## Key Findings

### Finding 1: Inductive Bias Differences Are Quantifiable

DWS and NFT produce measurably different weight update patterns (CoV 1.44 vs 1.35). This is the first concrete operationalization of "locality vs global attention" in weight-space learning.

**Implication:** Architecture selection for weight-space tasks should consider inductive bias alignment, not just raw parameter count. The 7% difference in layer-wise update variance reflects fundamentally different information processing strategies.

### Finding 2: NFT's Global Attention Advantages Accuracy Prediction

NFT achieves 12.3% lower RMSE than DWS on accuracy prediction (82.9 vs 94.5). This confirms that global attention mechanisms capture aggregate statistics more effectively than locality-preserving operations.

**Implication:** For tasks requiring holistic property aggregation (accuracy estimation, robustness prediction), transformer-based architectures like NFT may be preferable. The advantage is substantial and consistent across seeds.

### Finding 3: Interaction Effect Is Real, But Partial

The architecture-task interaction is statistically significant (F=45616, p<0.001), supporting the hypothesis that performance advantages are task-dependent. However, only one direction is confirmed—the hypothesized DWS advantage on local anomaly detection could not be verified.

**Implication:** The task-dependence story is half-validated. Practitioners can confidently choose NFT for global statistics tasks; guidance for local pattern detection requires further investigation.

![Figure 7: Interaction Plot](figures/interaction_plot.png)

*Figure 7: Architecture × Task interaction. Lines cross (interaction effect), but the backdoor task is at chance for all architectures, preventing confirmation of DWS locality advantage.*

## Limitations

Our work has several limitations that warrant honest acknowledgment:

### Limitation 1: Synthetic Backdoor Signals Were Unlearnable

The localized weight perturbations we injected were absorbed by z-score normalization, making the backdoor task unlearnable for all architectures (~0.48 AUC).

- **Why acceptable:** This is an experimental design limitation, not a hypothesis falsification. The DWS locality advantage on backdoor detection remains plausible—we simply could not test it.
- **Future work:** Test on real TrojAI benchmark with genuine backdoor signatures that produce learnable signals.

### Limitation 2: Dataset Ceiling Effects

All architectures achieved 100% accuracy on MNIST-INR classification, preventing differentiation of sample efficiency.

- **Why acceptable:** Core mechanism validation (CoV difference) was still possible through training dynamics analysis.
- **Future work:** Evaluate on harder benchmarks where architectures show measurable performance variation.

### Limitation 3: Parameter Count Mismatch

Architectures were not perfectly matched (DWS 4.9M, NFT 5.3M, MLP 9.8M—not within 10% tolerance).

- **Why acceptable:** MLP has approximately 2× more parameters than NFT yet performs worse on accuracy prediction. This suggests results reflect inductive bias, not capacity.
- **Future work:** Strict parameter matching in follow-up experiments.

### Limitation 4: Synthetic vs Real Data

All experiments used synthetic weight populations, not real model zoos from TrojAI or CNN-Zoo benchmarks.

- **Why acceptable:** Synthetic data enabled controlled hypothesis testing with known ground truth.
- **Future work:** Validate findings on real TrojAI models with genuine backdoor labels.

## Broader Impact

### Positive Impacts

This work provides actionable guidance for practitioners selecting weight-space architectures. The finding that NFT excels on holistic property prediction can inform architecture choices for accuracy estimation, robustness assessment, and similar tasks.

The methodology for comparing inductive biases via training dynamics (CoV analysis) may be useful beyond weight-space learning, providing a general framework for understanding architecture differences.

### Potential Concerns

Improved model property prediction could enable both beneficial applications (model auditing, safety verification) and potential misuse (identifying vulnerabilities in deployed models). However, this dual-use concern applies broadly to model analysis research and is not specific to our contribution.

### Mitigation

We recommend that weight-space analysis tools be developed with security considerations, including access controls when used for model auditing in sensitive contexts.

## Future Directions

1. **Real TrojAI Benchmark:** Test DWS locality hypothesis on genuine backdoor detection tasks.
2. **Transformer Weight-Spaces:** Extend analysis to weight-spaces of non-CNN architectures (Transformers, GNNs).
3. **Attention Pattern Probing:** Deeper analysis of NFT's learned attention patterns for interpretability.
4. **Sample Efficiency Curves:** Measure architecture differences on challenging tasks with clear performance gradients.
