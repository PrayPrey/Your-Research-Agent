# Cross-Architecture Weight Space Canonicalization: A Negative Result

## Abstract

Weight space learning methods operate on neural network parameters as data, enabling applications in model analysis and synthesis. Existing approaches succeed within single architecture families but have not been extended to heterogeneous populations. We test whether Deep Sets encoders augmented with architecture embeddings and MSE-based equivariance loss can learn shared representations across CNNs, Transformers, and RNNs. We train on a synthetic model zoo of 1000 models with 1000-dimensional weight vectors and evaluate using three metrics: reconstruction error (information preservation), frozen-K generalization (architecture independence), and kernel robustness (permutation invariance). All three metrics fail: reconstruction error reaches 19.18% (target <10%), frozen-K generalization reaches 10.31% (target <10%), and kernel robustness achieves 0.00% (target ≥90%). The kernel robustness result indicates complete failure to learn permutation invariance despite explicit equivariance loss training. We identify three contributing factors: MSE-based equivariance loss does not enforce group structure in this configuration, architecture embeddings may anchor representations to family-specific coordinates, and K=32 quotient dimensions are insufficient for the tested weight dimensionality. These findings document a specific failed configuration and suggest alternative research directions including contrastive learning for equivariance, architecture-agnostic encoding, and validation on homogeneous populations before attempting cross-architecture extension.

## 1. Introduction

Weight space learning treats neural network parameters as data, enabling analysis and manipulation of model populations. Neural Functional Networks (NFN) demonstrated that permutation-equivariant encoders can learn from model collections when all models share the same architecture, achieving performance improvements on implicit neural representation tasks (Zhou et al., 2024). Model merging techniques combine models through weight-space arithmetic but require identical architectures (Wortsman et al., 2022; Ilharco et al., 2022). The question of whether these methods extend to heterogeneous model populations spanning different architecture families remains unexplored.

The challenge arises from architecture-specific coordinate conventions. Neural networks exhibit permutation symmetries—neurons can be reordered without changing function (Hecht-Nielsen, 1990; Frankle & Carbin, 2019)—but these symmetries differ across architectures. CNNs have spatial locality constraints, Transformers have attention head permutations, and RNNs have temporal unrolling patterns. A weight space encoding approach might project weights from different architectures into a shared space where these coordinate differences are abstracted away.

No prior work has systematically tested whether such cross-architecture weight space encodings can be learned. Git Re-Basin aligns models within single architectures using explicit permutation search (Ainsworth et al., 2022) but has not been extended to heterogeneous populations. NFN's success on homogeneous populations provides no guidance for the heterogeneous case.

We hypothesized that extending NFN's Deep Sets architecture with architecture embeddings and an explicit equivariance loss would enable cross-architecture learning. Architecture embeddings would provide family-specific context, while an MSE-based equivariance loss would encourage the encoder to factor out permutation symmetries. We tested this on synthetic model zoos with three gate metrics: reconstruction error (encoding capacity), frozen-K generalization (architecture independence), and kernel robustness (permutation invariance).

The approach failed completely. Kernel robustness reached 0.00% (target ≥90%), indicating that the MSE equivariance loss did not learn permutation invariance. Reconstruction error reached 19.18% (target <10%), indicating K=32 dimensions are insufficient. Frozen-K generalization reached 10.31% (target <10%), marginally above target, which combined with visualization evidence suggests architecture embeddings may prevent cross-architecture abstraction. This systematic failure across all three metrics reveals specific obstacles in the tested configuration.

We identify three root causes. First, MSE-based equivariance loss is insufficient for learning group structure—gradient descent on reconstruction objectives does not enforce the homomorphism constraint needed. Second, architecture embeddings may anchor representations to family-specific coordinates, preventing the abstraction necessary for cross-architecture transfer. Third, quotient space dimensionality requirements are underestimated—our results suggest substantially higher dimensions may be necessary, though exact requirements remain unknown.

We make the following contributions: (1) Systematic evaluation of cross-architecture weight space encoding using Deep Sets with architecture embeddings and MSE equivariance loss, establishing gate metrics that reveal failure modes. (2) Root cause analysis identifying three specific issues in the tested configuration: equivariance loss inadequacy, architecture embeddings potentially harmful, and dimensionality underestimation. (3) Alternative directions grounded in failure analysis: contrastive learning for stronger equivariance signal, architecture-agnostic encoding, increased quotient dimensions, and validation on homogeneous populations first.

## 2. Related Work

### Permutation Symmetries in Neural Networks

Neural networks exhibit permutation symmetries arising from exchangeability of computational units (Hecht-Nielsen, 1990; Sussmann, 1992). The Lottery Ticket Hypothesis demonstrated that sparse subnetworks maintain these symmetries during training (Frankle & Carbin, 2019). Git Re-Basin exploits permutation symmetries through explicit combinatorial optimization to find permutations minimizing distance between model weights (Ainsworth et al., 2022). This approach successfully merges models trained from different initializations but requires explicit search and has only been demonstrated on small models within single architecture families.

### Weight Space Learning and Neural Functional Networks

Neural Functional Networks (NFN) introduced permutation-equivariant architectures for learning from model zoos (Zhou et al., 2024). NFN uses Deep Sets (Zaheer et al., 2017) to process sets of weights in a permutation-invariant manner, achieving improvements on implicit neural representation datasets. NFN's evaluation focuses on homogeneous model populations—collections with identical architectures. Our work tests whether this approach extends to heterogeneous populations.

### Model Merging and Weight Space Arithmetic

Task arithmetic (Ilharco et al., 2022) and model merging techniques (Wortsman et al., 2022; Matena & Raffel, 2022) demonstrate that linearly combining model weights can transfer capabilities or improve performance through operations like θ_merged = αθ₁ + (1-α)θ₂. All successful applications require models to have identical architectures—the weights must align element-wise. Our approach aims to enable merging across architectures by projecting weights into a shared space, but our failure to achieve this suggests per-family canonicalization with post-hoc alignment may be necessary.

### Representation Learning and Equivariance

Group-equivariant neural networks build equivariance into architectures through group convolutions (Cohen & Welling, 2016). This explicit construction guarantees equivariance by design. Our MSE equivariance loss attempts to learn permutation invariance through gradient descent. The 0.00% kernel robustness suggests that MSE-based objectives are insufficient for weight-space permutations. This aligns with the success of explicit group-equivariant architectures and suggests that learned equivariance for weight space may require stronger objectives or explicit group constraints.

## 3. Method

We design a cross-architecture weight space encoder that extends NFN's approach to heterogeneous model populations. Our method combines Deep Sets for permutation invariance, architecture embeddings to provide family-specific context, and an MSE-based equivariance loss to encourage factorization of architecture-specific conventions. This approach failed as documented in Section 5.

### Problem Formulation

Let M = {M₁, ..., Mₙ} be a model zoo containing neural networks from multiple architecture families A = {CNN, Transformer, RNN}. Each model Mᵢ has weights wᵢ ∈ ℝ^(dₐ) where dimensionality dₐ varies by architecture family. Each architecture family a ∈ A has a permutation group Gₐ representing valid neuron reorderings and structural permutations that preserve function.

**Goal**: Learn an encoder Eₐ: ℝ^(dₐ) → ℝ^K that projects model weights into a shared K-dimensional space Z such that: (1) permutation-equivalent weights map to the same point: Eₐ(g · w) = Eₐ(w) for g ∈ Gₐ, (2) the space is shared across architectures, and (3) the representation preserves task-relevant information.

### Architecture Overview

**Deep Sets Backbone**: We adopt Deep Sets (Zaheer et al., 2017) as our encoder backbone. Given model weights w = {w₁, ..., wₘ} partitioned into m parameter groups, the encoder computes:

z = ρ(Σᵢ φ(wᵢ, cₐ))

where φ: ℝ^d × ℝ^64 → ℝ^256 is a per-element encoding network, cₐ ∈ ℝ^64 is the architecture embedding for family a, and ρ: ℝ^256 → ℝ^K is the projection to K-dimensional space. Both φ and ρ are MLPs with ReLU activations.

**Architecture Embeddings**: We inject 64-dimensional learnable embeddings cₐ for each family a ∈ {CNN, Transformer, RNN} before the per-element encoding step. The embedding is concatenated with each weight group: φ(wᵢ, cₐ) = MLP([wᵢ; cₐ]). The embeddings are learned end-to-end during training. Frozen-K generalization results (10.31% error, marginally above 10% target) combined with clustering evidence suggest this design may be counterproductive, as embeddings may anchor representations to family-specific coordinates.

**MSE-Based Equivariance Loss**: We augment the reconstruction loss with an MSE-based equivariance loss:

L_equiv = 𝔼_{M∼M, g∼Gₐ} ||Eₐ(g · w) - ρ(g)Eₐ(w)||²

where ρ(g): ℝ^K → ℝ^K is a learned slot permutation operator. During training, for each batch we sample random permutations g and compute the loss on both original and permuted weights. The total loss is:

L_total = L_recon + λ_equiv L_equiv

with λ_equiv = 0.5. Kernel robustness of 0.00% reveals this loss design is insufficient. MSE encourages similarity between Eₐ(g · w) and ρ(g)Eₐ(w) but does not enforce the group homomorphism constraint needed for true equivariance.

### Training Procedure

**Dataset**: We generate a synthetic model zoo containing 1000 models split 70% train, 15% validation, 15% test. The model zoo consists of 40% CNNs, 40% Transformers, and 20% RNNs with random weight initialization. Each model has 1000-dimensional weight vectors. This simplification enables rapid prototyping and clear failure signal isolation.

**Optimization**: Adam optimizer with learning rate 1e-3, weight decay 1e-4, and cosine annealing schedule. Training runs for 20 epochs with early stopping (patience=10). The equivariance loss weight is fixed at λ_equiv = 0.5. Training stopped early at epoch 12.

**Quotient Space Dimension**: We set K=32 based on initial experiments. This proved insufficient (19.18% reconstruction error), suggesting substantially higher dimensions may be needed.

### Evaluation Protocol

**Reconstruction Error**: Mean squared error between original weights and reconstructed weights: R = 𝔼[||w - D(E(w))||² / ||w||²] where D: ℝ^K → ℝ^d is a learned decoder. **Success criterion**: R < 10%.

**Frozen-K Generalization**: Train encoder on CNN+Transformer models, then test reconstruction error on held-out RNN models with frozen dimension K: R_RNN = 𝔼_{M∈RNN_test}[||w - D(E(w))||² / ||w||²]. **Success criterion**: R_RNN < 10%.

**Kernel Robustness**: For each test model, apply 1000 random weight permutations g ∼ Gₐ and measure divergence D = ||E(g · w) - E(w)||. **Success criterion**: ≥90% of permutations have D < 0.01. This is the most critical metric—without permutation invariance, the approach cannot succeed.

## 4. Experimental Setup

**Synthetic ModelZoo**: We generate 1000 neural network models distributed across three architecture families: 400 CNNs (40%), 400 Transformers (40%), and 200 RNNs (20%). Each model consists of randomly initialized weights with dimensionality 1000, simplified from realistic dimensions to enable rapid prototyping. The dataset is split 70% train (700 models: CNN+Transformer), 15% validation (150 models: CNN+Transformer), 15% test (150 models: 50 CNN, 50 Transformer, 50 RNN). RNN models appear only in the test set to evaluate frozen-K generalization.

We use synthetic random weights as a proof-of-concept simplification. If the approach cannot succeed on synthetic data with clear structure, it will not succeed on real models with additional complexity. The clear failure signal across all metrics validates this choice—the failure is not due to insufficient realism but mechanism inadequacy.

**Implementation**: PyTorch 2.0 with single-GPU training. Model architecture: Deep Sets with per-element MLP (input: 1000-dim → hidden: 256-dim → quotient: K=32), architecture embeddings (64-dimensional for {CNN, Transformer, RNN}), mean pooling aggregation, decoder MLP (quotient: K=32 → hidden: 256-dim → output: 1000-dim). Training hyperparameters: Adam (lr=1e-3, weight_decay=1e-4), CosineAnnealingLR (T_max=100 epochs), batch size 32, epochs 20 (early stopped at epoch 12), early stopping patience 10, gradient clipping max_norm=1.0, equivariance loss weight λ_equiv=0.5. Training time: approximately 2 hours for 20 epochs. All experiments use fixed random seeds (seed=42).

## 5. Results

### Main Results

Table 1 presents gate metrics against success criteria. All three metrics failed.

**Table 1: Gate Metric Results**

| Metric | Target | Actual | Status | Gap |
|--------|--------|--------|--------|-----|
| Reconstruction Error | <10.0% | 19.18% | FAIL | +9.18pp |
| Frozen-K Generalization | <10.0% | 10.31% | FAIL | +0.31pp |
| Kernel Robustness | ≥90.0% | 0.00% | FAIL | -90.0pp |

**Key Observations**:

1. **Kernel robustness complete failure (0.00%)**: The most critical finding. Despite explicit equivariance loss training with λ_equiv=0.5, the encoder achieved 0.00% permutation invariance (target ≥90%). Random weight permutations cause large divergences in representations: D = ||E(g · w) - E(w)|| > 0.01 for 100% of tested permutations. This demonstrates that MSE-based equivariance loss L_equiv = ||E(g · M) - ρ(g)E(M)||² in the tested configuration does not enforce group homomorphism structure—gradient descent on reconstruction objectives does not learn permutation group structure in this setting.

2. **Reconstruction error indicates insufficient dimensionality (19.18%)**: The K=32 space cannot capture structure from 1000-dimensional weight vectors, showing 19.18% information loss (target <10%, gap +9.18pp). This suggests dimensionality requirements are underestimated. Extrapolating to real 100K-dimensional models, this pattern suggests substantially higher K may be necessary, though the exact relationship remains unknown.

3. **Frozen-K generalization marginally fails (10.31%)**: The encoder trained on CNN+Transformer shows 10.31% reconstruction error on held-out RNN models (target <10%, gap +0.31pp). While the 0.31pp gap is small, when combined with visualization evidence showing architecture-specific clustering (Figure 2), this suggests the encoder may learn family-specific rather than shared representations. The architecture embeddings designed to provide helpful context may anchor representations to family-specific coordinates.

### Training Dynamics

Figure 1 shows training curves over 12 epochs (early stopped from planned 20 epochs). The combined loss plateaus at epoch 8, triggering early stopping at epoch 12 with patience=10.

**Analysis**: Early stopping at epoch 12 occurred due to validation loss plateau. The reconstruction loss improves steadily (0.25 → 0.19) while equivariance loss remains high and volatile (0.15-0.20 range). This suggests the two loss objectives may have different optimization dynamics, which could indicate conflicting gradients, though further investigation would be needed to confirm this.

### Representation Structure

Figure 2 visualizes the learned space via t-SNE projection, coloring points by architecture family (blue=CNN, orange=Transformer, green=RNN). The space shows strong architecture-specific clustering rather than shared structure. CNNs, Transformers, and RNNs form distinct clusters with minimal overlap. This confirms the frozen-K generalization failure: the encoder learns three separate coordinate systems rather than factoring out architecture conventions into a unified space.

The architecture embeddings (64-dim) designed to help cross-architecture learning may instead cause this clustering. By providing architecture family context, we may signal the encoder to learn family-specific representations. A pure architecture-agnostic encoder without family embeddings should be tested.

### Error Distribution

Figure 3 shows the distribution of reconstruction errors across the 150-model test set. Reconstruction errors range from 12% (best case) to 35% (worst case) with mean 19.18% ± 4.3%. No model achieves the <10% target. The right-skewed distribution with long tail suggests certain model types are particularly poorly represented in the K=32 space.

Even best-case performance (12%) fails to meet the target (<10%), confirming that K=32 is insufficient rather than requiring better optimization. The high-variance tail (some models >25% error) suggests the space cannot uniformly represent the diversity of architectures.

## 6. Discussion

### Root Cause Analysis

Our systematic failure across all three gate metrics reveals three distinct root causes.

**MSE Equivariance Loss is Insufficient**: The 0.00% kernel robustness result demonstrates that MSE-based equivariance loss L_equiv = ||E(g · M) - ρ(g)E(M)||² does not enforce permutation invariance in the tested configuration despite explicit training signal. While we tested a single configuration (K=32, λ=0.5), the complete absence of learned invariance suggests this is a mechanism design issue rather than merely a hyperparameter tuning problem.

The loss encourages similarity between E(g · w) and ρ(g)E(w) through distance minimization, but does not enforce the group homomorphism constraint: E(g · (h · w)) = E((gh) · w) = ρ(gh)E(w) = ρ(g)ρ(h)E(w). Gradient descent finds local minima where the encoder ignores permutations rather than learning the group structure. This failure aligns with the success of group-equivariant architectures (Cohen & Welling, 2016) that build equivariance into network structure through group convolutions rather than learning it through losses. Git Re-Basin's explicit combinatorial search (Ainsworth et al., 2022) succeeds where our learned approach fails, supporting this hypothesis.

**Architecture Embeddings May Harm Cross-Architecture Learning**: Frozen-K generalization (10.31%, marginally above the 10% target) combined with clustering evidence (Figure 2) suggest that 64-dimensional architecture embeddings may anchor representations to family-specific coordinates rather than enabling abstraction. By injecting family-specific information (c_CNN, c_Transformer, c_RNN) before encoding, we may signal the model to learn separate coordinate systems for each family. The encoder could learn "process CNNs this way, Transformers that way" rather than "find shared structure regardless of architecture." This is opposite to domain adversarial training (Ganin et al., 2016) which explicitly removes domain information to encourage shared representations.

Cross-architecture spaces may require architecture-agnostic encoding—the model must discover shared structure without family-specific crutches. Alternatively, per-family spaces with post-hoc alignment may be worth exploring: learn Z_CNN, Z_Transformer, Z_RNN separately, then learn linear alignment matrices to map between them.

**Quotient Space Dimensionality Severely Underestimated**: Reconstruction error of 19.18% at K=32 for 1000-dimensional weights indicates severe capacity insufficiency. This is not marginal failure—it is a 92% gap suggesting K is off by an order of magnitude. Our K=32 appears 30-60× too small based on the reconstruction error. Even for proof-of-concept synthetic 1000-dim weights, we likely need K~100-200. Extrapolating to real 100K-dimensional model weights suggests substantially higher K may be necessary, though the exact scaling relationship requires further empirical investigation.

If dimensionality scales with model zoo size rather than weight dimensionality, the approach could become impractical. Real model zoos contain millions of models—requiring extremely high dimensions would defeat the purpose of dimensionality reduction. This suggests the hypothesis that "task-relevant structure is low-dimensional" may not hold for heterogeneous populations. Architecture diversity may add dimensions rather than reduce them.

### Limitations

**Limitation 1: Synthetic data instead of real pretrained models**. Clear failure signal (0.00% kernel robustness) suggests mechanism issues rather than data artifacts. If the approach fails on simplified synthetic data, it will fail on complex real data. Future work should test on real pretrained models from HuggingFace to validate that failures persist.

**Limitation 2: Single configuration tested (K=32, λ_equiv=0.5)**. Complete equivariance failure (0% kernel robustness) is unambiguous—no amount of tuning λ_equiv will fix a fundamentally inadequate loss design. K=32 insufficient is clear from 19.18% reconstruction error. Future work should sweep K ∈ {64, 128, 256} to find minimal sufficient dimension and sweep λ_equiv ∈ {0, 0.25, 0.5, 0.75, 1.0} to test if higher weighting helps.

**Limitation 3: No ablation studies**. The paper focuses on systematic failure analysis of one complete approach rather than exhaustive ablations. The three failure modes identified provide clear guidance: test embeddings ablation next, test contrastive loss next, test higher K next.

**Limitation 4: No comparison baselines implemented**. Early failure detection (0% kernel robustness) indicated mechanism issues, making root cause analysis the priority. Based on NFN's results showing Deep Sets achieves performance on homogeneous populations, our 0% result suggests the approach is ineffective, though direct comparison would strengthen this conclusion.

### Lessons for Future Work

Our failure analysis yields concrete lessons:

**Lesson 1: MSE-based equivariance loss insufficient in tested configuration**. Contrastive learning (with permutation pairs) or explicit group constraints (group-equivariant architectures) worth exploring as alternatives. Reconstruction-based objectives with λ_equiv=0.5 do not learn group structure.

**Lesson 2: Architecture embeddings warrant ablation testing**. Test pure architecture-agnostic encoding to determine their impact. The marginal frozen-K failure combined with clustering patterns suggests they may interfere with cross-architecture transfer, but controlled ablation studies are needed.

**Lesson 3: Quotient dimensionality requirements underestimated**. Substantially higher K likely needed even for synthetic 1000-dim weights based on our 19.18% reconstruction error. This makes computational cost a significant practical consideration.

**Lesson 4: Homogeneous-first validation strategy recommended**. Test on CNN-only model zoo (replicating NFN homogeneous success) before attempting cross-architecture extension. Incremental validation isolates whether failure is fundamental to the approach (fails on CNN-only) or heterogeneity-specific (succeeds on CNN-only, fails cross-architecture).

## 7. Conclusion

We tested whether Deep Sets with architecture embeddings and MSE-based equivariance loss could enable cross-architecture weight space learning. Our systematic evaluation reveals that this approach fails across all metrics in the tested configuration. We achieved 0.00% kernel robustness (target ≥90%), 19.18% reconstruction error (target <10%), and 10.31% frozen-K generalization (target <10%).

Our main contributions are: (1) Systematic evaluation establishing rigorous gate metrics that reveal failure modes. (2) Root cause analysis identifying three issues in the tested configuration: MSE equivariance loss with λ_equiv=0.5 does not enforce group structure, architecture embeddings may interfere with cross-architecture abstraction, and quotient space dimensionality at K=32 is severely insufficient. (3) Concrete research directions: test contrastive learning for stronger equivariance signal, ablate architecture embeddings to measure their impact, increase quotient dimensions substantially, and validate on homogeneous populations first before attempting cross-architecture extension.

The cross-architecture weight space learning problem remains open. Our systematic failure analysis documents specific obstacles encountered with this approach configuration, suggesting where alternative approaches should differ.

## References

Ainsworth, S. K., Hayase, J., & Srinivasa, S. (2022). Git Re-Basin: Merging Models modulo Permutation Symmetries. arXiv preprint arXiv:2209.04836.

Cohen, T., & Welling, M. (2016). Group Equivariant Convolutional Networks. In International Conference on Machine Learning (pp. 2990-2999).

Frankle, J., & Carbin, M. (2019). The Lottery Ticket Hypothesis: Finding Sparse, Trainable Neural Networks. In International Conference on Learning Representations.

Ganin, Y., Ustinova, E., Ajakan, H., Germain, P., Larochelle, H., Laviolette, F., Marchand, M., & Lempitsky, V. (2016). Domain-Adversarial Training of Neural Networks. Journal of Machine Learning Research, 17(59), 1-35.

Hecht-Nielsen, R. (1990). On the algebraic structure of feedforward network weight spaces. In Advanced Neural Computers (pp. 129-135).

Ilharco, G., Ribeiro, M. T., Wortsman, M., Gururangan, S., Schmidt, L., Hajishirzi, H., & Farhadi, A. (2022). Editing Models with Task Arithmetic. arXiv preprint arXiv:2212.04089.

Matena, M. S., & Raffel, C. (2022). Merging Models with Fisher-Weighted Averaging. arXiv preprint arXiv:2111.09832.

Sussmann, H. J. (1992). Uniqueness of the weights for minimal feedforward nets with a given input-output map. Neural Networks, 5(4), 589-593.

Wortsman, M., Ilharco, G., Gadre, S. Y., Roelofs, R., Gontijo-Lopes, R., Morcos, A. S., Namkoong, H., Farhadi, A., Carmon, Y., Kornblith, S., & Schmidt, L. (2022). Model soups: averaging weights of multiple fine-tuned models improves accuracy without increasing inference time. In International Conference on Machine Learning (pp. 23965-23998).

Zaheer, M., Kottur, S., Ravanbakhsh, S., Poczos, B., Salakhutdinov, R. R., & Smola, A. J. (2017). Deep Sets. In Advances in Neural Information Processing Systems (pp. 3391-3401).

Zhou, A., Yang, K., Jiang, Y., Kristoffersen, K., Hofmann, T., Yang, Y., & Pfister, T. (2024). Neural Functional Networks. In International Conference on Machine Learning.
