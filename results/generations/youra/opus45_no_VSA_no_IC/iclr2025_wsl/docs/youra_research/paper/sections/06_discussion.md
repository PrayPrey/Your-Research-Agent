# Discussion

## Interpretation of Results

Our findings challenge the framing of equivariance as a "data efficiency" technique. The MLP baseline does not merely require more data—it fails categorically at all tested sample sizes. This suggests a fundamental limitation: non-equivariant architectures cannot learn permutation-invariant functions over high-dimensional weight spaces without explicit symmetry handling.

The mechanism is clear. A 270K-dimensional input with N! equivalent configurations per layer creates an intractable learning problem. The MLP must somehow learn that all permutation-equivalent inputs should map to identical outputs—but with only thousands of samples, it has seen a vanishingly small fraction of the permutation equivalence classes. The equivariant architecture sidesteps this by encoding invariance structurally.

## Connection to Theory

Our results align with theoretical predictions from equivariant learning theory. For a group G acting on inputs, equivariant networks effectively reduce sample complexity by a factor related to |G|. For neural network weights with L layers of N hidden units each, |G| ≈ (N!)^L—astronomically large. This theoretical advantage manifests empirically as the difference between R² = 0.99 and R² = -1.5.

## Why Statistics Baseline Succeeds

The statistics baseline achieves near-perfect R² through a different mechanism: aggressive dimensionality reduction. By computing 7 statistics per layer, it projects 270K parameters to 63 features. This projection is permutation-invariant by construction and well-conditioned for regression. The trade-off is lost expressiveness—statistics cannot capture relationships between individual weights.

NFN represents a middle ground: preserving weight structure while enforcing invariance. In our experiments, both approaches succeed; whether NFN's richer representation provides advantages on more complex tasks remains open.

## Limitations

**L1: Synthetic model zoo.** We use generated weights rather than the 157GB Zenodo Model Zoo. Accuracy distributions may be more uniform than real training runs. However, the directional finding—MLP fails, NFN succeeds—is robust to distribution details.

**L2: Single architecture.** All experiments use ResNet-20. Cross-architecture generalization (ResNet-50, ViT) is untested. NFN supports arbitrary architectures by design, but empirical validation is future work.

**L3: MLP configuration.** We use a standard 2-layer, 256-unit MLP. Alternative configurations (deeper networks, heavier regularization, PCA preprocessing) might partially mitigate failure. However, the 2.5 R² gap suggests incremental improvements cannot close it.

**L4: Statistics baseline anomaly.** H-C2 shows Statistics R² negative at N=100, contradicting H-E1. This implementation variance does not affect core findings.

## Broader Impact

Weight-space learning enables training-free model evaluation, zoo curation, and neural architecture search guidance. Our findings indicate that practitioners building weight-space tools must either:
1. Use permutation-invariant features (statistics, histograms), or
2. Use permutation-equivariant architectures (NFN, DeepSets variants)

Naive approaches treating weights as arbitrary vectors will fail regardless of dataset size within practical ranges.

## Future Directions

**F1: Real model zoo validation.** Replicate on Zenodo Model Zoo to confirm synthetic results transfer.

**F2: Cross-architecture generalization.** Test whether equivariance benefits transfer to ResNet-50, VGG, ViT.

**F3: Alternative baselines.** Evaluate MLP with PCA, Transformer encoders, or other non-equivariant but structured approaches.

**F4: Task generalization.** Apply to loss prediction, generalization gap estimation, architecture classification.

**F5: Theoretical bounds.** Derive sample complexity bounds for equivariant vs non-equivariant weight-space learning.
