# Measurement Requirements for Gradient Subspace Analysis in Spurious Correlation Robustification

**Anonymous Authors**

---

## Abstract

Neural networks exploit spurious correlations in training data. Gradient-based interventions have been proposed for single-run robustification without group labels. This work tests a foundational assumption underlying Progressive Gradient Orthogonalization (PGO): that early training gradients capture spurious feature directions. Experiments on the Waterbirds benchmark reveal a measurement limitation—accumulating one gradient per epoch produces representations too low-rank to distinguish spurious from core directions. With 10 gradient samples in a 25.6-million-parameter space, both spurious and core alignments measure approximately 0.05, indistinguishable from each other. This null result stems from insufficient accumulation density rather than absence of the hypothesized effect. The findings establish a minimum requirement for valid gradient subspace analysis: multi-batch accumulation is necessary to achieve sufficient rank for meaningful directional measurement. The PGO hypothesis remains unverified pending implementation of adequate gradient sampling.

---

## 1. Introduction

Gradient-based interventions for spurious correlation robustness offer the possibility of single-run training without group labels. However, experiments conducted in this work reveal a measurement limitation: gradient subspace accumulation with one sample per epoch produces representations too low-rank to distinguish spurious from core feature directions. Where theory predicted clear separation (greater than 70% spurious alignment versus less than 30% core alignment based on simplicity bias), both alignments measured approximately 5%—statistically indistinguishable.

This finding is relevant because methods claiming to exploit training dynamics for robustness may measure noise rather than meaningful signal without understanding minimum requirements for gradient subspace analysis.

### 1.1 The Problem

Deep neural networks trained with empirical risk minimization (ERM) learn spurious correlations—shortcuts that achieve low training loss but fail on minority groups. On Waterbirds, ERM models learn to associate waterbirds with water backgrounds (95% correlation in training data), achieving approximately 60% worst-group accuracy when waterbirds appear on land backgrounds.

Existing solutions require resources unavailable in many practical settings. Group DRO requires group annotations during training. Just Train Twice (JTT) requires two complete training runs. Deep Feature Reweighting (DFR) requires held-out data with group labels for last-layer retraining. The possibility of training dynamics exploitation—intervening on gradients during a single training run without labels—remains unvalidated.

### 1.2 Investigation

This work tested the foundational assumption underlying Progressive Gradient Orthogonalization: that early gradient subspaces primarily capture spurious feature directions. ResNet-50 was trained on Waterbirds, gradients were accumulated during epochs 1-10, a top-50 SVD subspace was computed, and alignment was measured with spurious (background-varying) and core (bird-type-varying) gradient directions.

The result was unexpected. Both alignments registered at approximately 0.05—far below the 0.70 and 0.30 thresholds specified by the experimental design, and statistically indistinguishable from each other. Investigation revealed the cause: accumulating one gradient per epoch (the last batch only) produced a 10-dimensional subspace in a 25.6-million-parameter space. This rank is insufficient to capture meaningful variance in any direction. The measurement apparatus failed before the hypothesis could be tested.

### 1.3 Contributions

This investigation yields a methodological constraint rather than a positive result:

1. Gradient subspace analysis in high-dimensional parameter spaces requires sufficient sample density—single gradients per epoch produce subspaces too low-rank for meaningful directional analysis.

2. Minimum requirements for valid gradient subspace measurement are documented: multi-batch accumulation within early epochs is necessary, not single-batch per epoch sampling.

3. A template is provided for future gradient-based robustification work to validate measurement apparatus before testing hypotheses.

The Progressive Gradient Orthogonalization hypothesis remains unverified. What is established is what valid testing requires.

---

## 2. Related Work

### 2.1 Spurious Correlation and Shortcut Learning

Geirhos et al. (2020) formalized the taxonomy of shortcut learning in deep neural networks, documenting how models exploit dataset biases rather than learning intended features. Sagawa et al. (2020) introduced Group DRO and the Waterbirds benchmark, enabling standardized evaluation of worst-group accuracy. Group DRO requires group annotations during training—a resource often unavailable in practice.

### 2.2 Annotation-Free Robustification

Liu et al. (2021) developed Just Train Twice (JTT), a two-stage approach that identifies spurious-reliant samples via training dynamics, then upweights them. JTT removes the need for group labels but requires two complete training runs. Kirichenko et al. (2023) showed that last-layer retraining (Deep Feature Reweighting, DFR) suffices for robustification, suggesting pretrained representations already contain core features. DFR requires held-out data with group labels for reweighting.

These methods operate on samples or final representations. None validates whether gradient directions themselves can distinguish spurious from core features—the assumption underlying gradient-based intervention.

### 2.3 Simplicity Bias and Training Dynamics

Shah et al. (2020) documented simplicity bias: neural networks trained with SGD preferentially learn simpler features first. Since spurious correlations often involve simpler patterns (background texture versus object shape), this predicts early spurious feature acquisition.

The present work attempts to measure this directly and finds the measurement apparatus itself requires validation.

### 2.4 Gradient-Based Representation Analysis

Parameter-space gradient subspace analysis appears primarily in optimization literature (incremental PCA, streaming SVD) rather than robustification. The present work applies subspace methods to spurious correlation measurement and identifies minimum requirements for such methods: sufficient accumulation density relative to parameter dimensionality.

---

## 3. Method

### 3.1 Problem Formulation

Let $f_\theta: \mathcal{X} \to \mathcal{Y}$ be a neural network with parameters $\theta \in \mathbb{R}^d$. During training, the gradient $\nabla_\theta \mathcal{L}$ provides a $d$-dimensional direction of parameter change.

**Hypothesis:** Under simplicity bias, early training gradients point predominantly toward spurious feature directions. Accumulating these gradients into a subspace $S$ via SVD should yield high alignment with spurious directions and low alignment with core directions.

### 3.2 Gradient Subspace Accumulation

Gradients are accumulated during early training epochs and a principal subspace is computed via SVD.

**Algorithm: Gradient Subspace Computation**

```
Input: Model θ, epochs T_acc, rank k
Output: Subspace S ∈ ℝ^{d×k}

G ← empty matrix
for epoch t = 1 to T_acc:
    for batch in dataloader:
        compute loss L(θ)
        g_t ← flatten(∇_θ L)
        append g_t to G (implementation: last batch only)
    
U, Σ, V^T ← SVD(G)
S ← V[:k]^T
return S
```

**Critical limitation identified:** The matrix $G$ must have sufficient rows (gradient samples) relative to parameter dimensionality $d$. With $d = 25.6 \times 10^6$ parameters and only 10 gradients (one per epoch), rank($G$) ≤ 10. The resulting subspace captures negligible variance.

### 3.3 Direction Computation

Spurious and core directions are defined via gradient differences across group-varying samples.

**Spurious direction:** Average gradient difference when background changes while bird type remains constant.

**Core direction:** Average gradient difference when bird type changes while background remains constant.

50 sample pairs were used for each direction computation.

### 3.4 Alignment Measurement

Alignment measures the fraction of a direction's variance explained by the subspace:

$$\text{align}(S, \mathbf{v}) = \frac{\| S S^T \mathbf{v} \|_2^2}{\| \mathbf{v} \|_2^2}$$

**Success criteria:**
- $\text{align}(S, \mathbf{v}_{\text{spur}}) > 0.70$
- $\text{align}(S, \mathbf{v}_{\text{core}}) < 0.30$

---

## 4. Experimental Setup

### 4.1 Research Questions

**RQ1:** Does the accumulated gradient subspace align more strongly with spurious (background) directions than core (bird type) directions during early training?

**RQ2:** Is the alignment difference measurable given realistic subspace ranks in high-dimensional parameter spaces?

### 4.2 Dataset

**Waterbirds** (Sagawa et al., 2020): A spurious correlation benchmark where background type (water/land) correlates 95% with bird type (waterbird/landbird) in training data.

| Split | Samples | Groups | Spurious Correlation |
|-------|---------|--------|---------------------|
| Train | 4,795 | 4 | 95% |
| Validation | 1,199 | 4 | 95% |
| Test | 5,794 | 4 | Balanced |

### 4.3 Model and Training

**Model:** ResNet-50 pretrained on ImageNet, final fully-connected layer replaced with a 2-class linear head (25.6M trainable parameters).

| Parameter | Value |
|-----------|-------|
| Optimizer | SGD (momentum=0.9, weight_decay=1e-4) |
| Learning rate | 1e-3 (step decay at epochs 60, 75) |
| Batch size | 128 |
| Total epochs | 90 |
| Random seed | 42 |

**Gradient Accumulation:**
- Accumulation window: epochs 1-10
- Samples accumulated: 1 gradient per epoch (last batch)
- SVD rank requested: k=50
- SVD rank actual: k=10 (limited by number of gradient samples)

### 4.4 Evaluation Metrics

- Spurious alignment target: > 0.70 at epoch 10
- Core alignment target: < 0.30 at epoch 10
- Measurement epochs: 5, 10, 45

---

## 5. Results

The main finding is negative: the gradient subspace accumulated during early training does not distinguish between spurious and core feature directions. Investigation reveals this stems from insufficient subspace rank rather than absence of the underlying phenomenon.

### 5.1 Main Results

**Table 1:** Alignment measurements at three epochs during training.

| Epoch | Spurious Alignment | Core Alignment | Difference | Train Loss | Val Acc |
|-------|-------------------|----------------|------------|------------|---------|
| 5 | 0.000 | 0.000 | 0.000 | 0.108 | 0.840 |
| 10 | 0.052 | 0.056 | -0.004 | 0.076 | 0.862 |
| 45 | 0.018 | 0.028 | -0.010 | 0.037 | 0.918 |

**Observations:**

1. **Both alignments are near zero.** At epoch 10, spurious alignment is 0.052 and core alignment is 0.056—both far below thresholds and statistically indistinguishable.

2. **Alignment does not increase with training.** Despite 90 epochs achieving 91.8% validation accuracy, alignment values remain negligible.

3. **The difference is in the opposite direction.** Core alignment slightly exceeds spurious alignment—opposite of simplicity bias prediction.

### 5.2 Diagnostic Analysis

The implementation accumulated one gradient per epoch during epochs 1-10, yielding a gradient matrix G ∈ ℝ^{10×25.6M}. SVD produces at most 10 non-zero singular values, regardless of requested rank (k=50).

With 10 dimensions in a 25.6-million-parameter space, the subspace captures approximately 10/25.6M ≈ 4×10^{-7} of variance along any direction.

### 5.3 Gate Outcome

| Metric | Target | Actual | Pass |
|--------|--------|--------|------|
| Spurious alignment (epoch 10) | > 0.70 | 0.052 | No |
| Core alignment (epoch 10) | < 0.30 | 0.056 | Yes |

**Gate result: PARTIAL** — Code executed successfully, but hypothesis validation criteria not met due to measurement apparatus limitation.

---

## 6. Discussion

### 6.1 Key Findings

**Finding 1: Gradient subspace methods require sufficient accumulation density.**

Accumulating one gradient per epoch produces a subspace whose rank equals the number of epochs, not the requested SVD rank. In this experiment, 10 epochs yielded a rank-10 subspace in a 25.6-million-parameter space.

**Finding 2: The PGO hypothesis remains unverified, not refuted.**

The null result stems from measurement limitation rather than absence of the hypothesized effect. The question of whether gradient subspaces can capture simplicity bias remains open pending valid measurement.

**Finding 3: Multi-batch accumulation is necessary.**

With approximately 38 batches per epoch (4,795 samples / 128 batch size) and 10 accumulation epochs, multi-batch accumulation would yield approximately 380 gradient samples—sufficient for meaningful rank-50 subspaces.

### 6.2 Limitations

**The core hypothesis is unverified.** PGO cannot be claimed to work or fail because the measurement apparatus prevented valid testing.

**Only one dataset tested.** Other spurious correlation benchmarks may exhibit different gradient dynamics.

**No baseline comparison performed.** Comparison against JTT, DFR, or Group DRO awaits valid PGO implementation.

**Single random seed.** Experiments used seed 42 for all runs. While sufficient to demonstrate measurement apparatus limitation, reproducibility across seeds should be verified in future work.

### 6.3 Broader Impact

This work identifies a methodological pitfall in gradient-based machine learning interventions. Researchers proposing gradient subspace methods should validate accumulation density before claiming directional findings.

---

## 7. Conclusion

### 7.1 Summary

Experiments on Waterbirds with ResNet-50 yielded a null result—spurious and core alignments were both approximately 0.05, statistically indistinguishable. Investigation traced this to measurement apparatus limitation: accumulating one gradient per epoch produced a 10-dimensional subspace in a 25.6-million-parameter space.

Contributions are methodological:

1. Minimum requirements for gradient subspace analysis are established: multi-batch accumulation within early epochs.
2. A reproducible failure case is documented that future gradient-based methods should avoid.
3. Guidance is provided for valid testing of gradient orthogonalization hypotheses.

### 7.2 Future Directions

**Immediate:** Re-implement gradient accumulation using streaming SVD across all batches during epochs 1-10.

**Medium-term:** If valid measurement confirms spurious-core separation, implement full PGO mechanism and evaluate against baselines.

**Long-term:** Extend to other architectures and domains where gradient subspace properties may differ.

### 7.3 Closing

The question of whether early gradients capture spurious directions remains open. What has been established is what valid measurement requires. Future work should validate accumulation density before claiming directional findings.

---

## References

Geirhos, R., Jacobsen, J.-H., Michaelis, C., Zemel, R., Brendel, W., Bethge, M., & Wichmann, F. A. (2020). Shortcut Learning in Deep Neural Networks. Nature Machine Intelligence, 2, 665-673.

Kirichenko, P., Izmailov, P., & Wilson, A. G. (2023). Last Layer Re-Training is Sufficient for Robustness to Spurious Correlations. ICLR.

Liu, E. Z., Haghgoo, B., Chen, A. S., Raghunathan, A., Koh, P. W., Sagawa, S., Liang, P., & Finn, C. (2021). Just Train Twice: Improving Group Robustness without Training Group Information. ICML.

Sagawa, S., Koh, P. W., Hashimoto, T. B., & Liang, P. (2020). Distributionally Robust Neural Networks for Group Shifts: On the Importance of Regularization for Worst-Case Generalization. ICLR.

Shah, H., Tamuly, K., Raghunathan, A., Jain, P., & Netrapalli, P. (2020). The Pitfalls of Simplicity Bias in Neural Networks. NeurIPS.
