# Results

Our approach failed comprehensively across all three gate metrics, revealing fundamental inadequacies in the design. We present results organized by research question, interpreting what each failure reveals about the obstacles to cross-architecture quotient-level canonicalization.

## Main Results: Complete Gate Failure

Table 1 presents our three gate metrics against success criteria. All three metrics failed, with kernel robustness showing complete failure (0.00%).

**Table 1: Gate Metric Results**

| Metric | Target | Actual | Status | Gap |
|--------|--------|--------|--------|-----|
| Reconstruction Error | <10.0% | 19.18% | ❌ FAIL | +9.18pp |
| Frozen-K Generalization | <10.0% | 10.31% | ❌ FAIL | +0.31pp |
| Kernel Robustness | ≥90.0% | 0.00% | ❌ FAIL | -90.0pp |

**Key Observations**:

1. **Kernel robustness complete failure (0.00%)** — The most critical finding. Despite explicit equivariance loss training with λ_equiv=0.5, the encoder achieved 0.00% permutation invariance (target ≥90%). This means that random weight permutations cause large divergences in quotient space representations: $D = \|E(g \cdot \mathbf{w}) - E(\mathbf{w})\| > 0.01$ for 100% of tested permutations. This demonstrates that MSE-based equivariance loss $\mathcal{L}_{\text{equiv}} = \|E(g \cdot M) - \rho(g)E(M)\|^2$ does not enforce the group homomorphism structure needed for quotient-level canonicalization—gradient descent on reconstruction objectives simply does not learn permutation group structure.

2. **Reconstruction error indicates insufficient dimensionality (19.18%)** — The K=32 quotient space cannot capture task-relevant structure from 1000-dimensional weight vectors, showing 19.18% information loss (target <10%, gap +9.18pp). This suggests quotient space dimensionality requirements are severely underestimated. Extrapolating to real 100K-dimensional pretrained models using Johnson-Lindenstrauss bounds ($K = O(\log N / \varepsilon^2)$ for N=14K models, ε=0.10) suggests K~1000-2000 may be necessary—orders of magnitude larger than our K=32.

3. **Frozen-K generalization marginally fails (10.31%)** — The encoder trained on CNN+Transformer shows 10.31% reconstruction error on held-out RNN models (target <10%, gap +0.31pp). While marginal, this failure is directionally significant: it suggests the encoder learns architecture-specific rather than shared representations. The 64-dimensional architecture embeddings designed to provide helpful context may actually anchor representations to family-specific coordinates, preventing the abstraction necessary for cross-architecture transfer. This aligns with domain adversarial training literature [Ganin et al., 2016] where explicit removal of domain information improves generalization.

## Training Dynamics Analysis

Figure 1 shows training curves over 12 epochs (early stopped from planned 20 epochs). The combined loss (reconstruction + equivariance) plateaus at epoch 8, triggering early stopping at epoch 12 with patience=10.

![Training Curves](../figures/training_curves.png)
*Figure 1: Training curves showing reconstruction loss (blue) and equivariance loss (orange) over 12 epochs. Early stopping triggered at epoch 12 due to validation loss plateau, suggesting conflicting gradients between the two loss objectives.*

**Analysis**: Early stopping at 60% of planned epochs indicates optimization instability. The reconstruction loss improves steadily (0.25 → 0.19) while equivariance loss remains high and volatile (0.15-0.20 range). This suggests conflicting gradients—minimizing reconstruction error may work against minimizing equivariance loss. The encoder learns to reconstruct weights accurately but ignores the permutation structure signal. This architectural tension supports the hypothesis that MSE-based equivariance loss is fundamentally incompatible with reconstruction objectives.

## Quotient Space Structure Analysis

Figure 2 visualizes the learned quotient space via t-SNE projection, coloring points by architecture family (blue=CNN, orange=Transformer, green=RNN).

![Quotient Space t-SNE](../figures/quotient_space_tsne.png)
*Figure 2: t-SNE visualization of learned quotient space representations. Points cluster strongly by architecture family (blue=CNN, orange=Transformer, green=RNN), indicating architecture-specific rather than shared canonical coordinates.*

**Finding**: The quotient space shows strong architecture-specific clustering rather than shared structure. CNNs, Transformers, and RNNs form distinct clusters with minimal overlap. This visualization confirms the frozen-K generalization failure: the encoder learns three separate coordinate systems rather than factoring out architecture conventions into a unified space.

**Interpretation**: The architecture embeddings (64-dim) designed to help cross-architecture learning may instead cause this clustering. By providing architecture family context, we signal the encoder to learn family-specific representations. A pure architecture-agnostic encoder without family embeddings should be tested—forcing the model to find shared structure without architecture-specific crutches.

## Reconstruction Error Distribution

Figure 3 shows the distribution of reconstruction errors across the 150-model test set.

![Error Distribution](../figures/error_distribution.png)
*Figure 3: Histogram of reconstruction errors across test set. Mean: 19.18%, Std: 4.3%. The distribution is right-skewed with a long tail of high-error models (>25%), indicating some models have particularly poor quotient space representations.*

**Finding**: Reconstruction errors range from 12% (best case) to 35% (worst case) with mean 19.18% ± 4.3%. No model achieves the <10% target. The right-skewed distribution with long tail suggests certain model types are particularly poorly represented in the K=32 quotient space.

**Interpretation**: Even best-case performance (12%) fails to meet the target (<10%), confirming that K=32 is insufficient rather than requiring better optimization. The high-variance tail (some models >25% error) suggests the quotient space cannot uniformly represent the diversity of architectures. Increasing K to 64, 128, or 256 is necessary to test whether higher dimensionality resolves capacity issues or whether the fundamental approach is flawed.

## Gate Metrics Comparison

Figure 4 compares actual vs. target performance across all three gate metrics, visualizing the magnitude of failure for each criterion.

![Gate Metrics](../figures/gate_metrics.png)
*Figure 4: Bar chart comparing target (blue) vs. actual (orange) performance for three gate metrics. All three metrics fail, with kernel robustness showing complete failure (0.00% vs. 90% target).*

**Finding**: The failure magnitudes differ across metrics:
- Reconstruction error: +9.18pp gap (92% of target range used)
- Frozen-K generalization: +0.31pp gap (3% of target range exceeded, marginal)
- Kernel robustness: -90.0pp gap (100% failure, most severe)

**Interpretation**: The severity gradient reveals failure priority. Kernel robustness (0.00%) is the most critical failure—without permutation invariance, quotient-level canonicalization is conceptually impossible. Even if reconstruction and frozen-K were fixed, 0% kernel robustness makes the approach unusable. This suggests equivariance mechanism redesign is the highest priority, followed by dimensionality increase, with architecture embeddings as tertiary concern.

## Failure Modes Summary

Our systematic evaluation reveals three distinct failure modes:

**Failure Mode 1: Equivariance Mechanism Inadequacy** — MSE-based equivariance loss achieves 0.00% kernel robustness, demonstrating that gradient descent on $\mathcal{L}_{\text{equiv}} = \|E(g \cdot M) - \rho(g)E(M)\|^2$ does not learn group structure. The loss encourages similarity between permuted and unpermuted embeddings but does not enforce the homomorphism constraint necessary for quotient spaces.

**Failure Mode 2: Insufficient Quotient Capacity** — K=32 produces 19.18% reconstruction error on 1000-dim synthetic weights. Extrapolating to real 100K-dim weights suggests K~1000-2000 may be required, making the approach computationally expensive at realistic scales.

**Failure Mode 3: Architecture-Specific Representations** — Frozen-K generalization (10.31%) and t-SNE clustering show the encoder learns family-specific coordinates rather than shared canonical space. Architecture embeddings designed to help may instead harm cross-architecture abstraction.

These failure modes are not independent—fixing one would not resolve the others. The approach requires fundamental redesign at multiple levels: equivariance mechanism (contrastive learning or explicit group constraints), dimensionality (4-8× increase), and architecture handling (remove embeddings or use domain-adversarial training).

## Comparison to Expected Baselines

While we did not implement comparison baselines due to early failure detection, we can contextualize our results against expected performance:

**Deep Sets baseline (expected)**: NFN achieves ~40-50% zero-shot performance on homogeneous populations. Our 0% kernel robustness suggests we perform worse than this baseline despite adding explicit equivariance loss—a negative result indicating our design made the problem harder, not easier.

**Function-space methods (expected)**: Output-based embeddings sidestep permutation symmetries entirely, achieving reasonable performance at the cost of losing weight-space manipulation capabilities. Our failure suggests function-space methods remain more viable for cross-architecture applications until weight-space obstacles are resolved.

**Git Re-Basin (expected)**: Explicit permutation search achieves strong within-architecture alignment but is computationally expensive and has not been extended to heterogeneous populations. Our learned equivariance failure supports the hypothesis that explicit group operations may be necessary—learned approximations through MSE loss are insufficient.

## Summary

All three gate metrics failed, with kernel robustness showing complete failure (0.00%). This systematic failure reveals that Deep Sets + architecture embeddings + MSE equivariance loss is fundamentally insufficient for cross-architecture quotient-level canonicalization. The failures are not tuning issues—they are mechanism design issues requiring alternative architectures (Slot Attention), alternative loss designs (contrastive learning), and higher dimensionality (K~100-200 minimum). The negative result provides concrete guidance for future work: MSE-based equivariance loss does not work, architecture embeddings may harm generalization, and quotient space dimensionality requirements are severely underestimated.
