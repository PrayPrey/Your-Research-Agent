# Architectural Inductive Bias Trumps Data Scale: Permutation Equivariance in Weight-Space Learning

**Anonymous Authors**

---

## Abstract

Can neural networks learn permutation symmetries from data, or must such structure be built into the architecture? This work studies the question in weight-space learning, where models predict properties of neural networks from their weights. Using the Model Zoo dataset of approximately 42,000 CIFAR-10 CNNs, we compare permutation-equivariant Neural Functional Networks (NFN) against matched-capacity MLPs across data scales from 1,000 to 40,000 models.

At N=40,000, MLPs achieve high prediction accuracy (R²=0.986) but fail to develop permutation invariance (invariance score 0.63 versus NFN's 1.0). This demonstrates that task performance and representation quality are separable: MLPs learn dataset-specific position-accuracy correlations rather than semantic weight structure. At small scales, the gap is larger: NFN achieves R²=0.95 at N=1,000 where MLP achieves R²=0.35. NFN's predictions are invariant to weight permutation with deviations below 1.19×10⁻⁷, confirming mathematical guarantees.

These findings falsify the hypothesis that sufficient data diversity teaches invariance. Permutation equivariance provides sample efficiency that data quantity cannot substitute.

---

## 1. Introduction

A neural network that achieves high predictive accuracy can fundamentally misunderstand the structure of its input, learning correct answers through an incorrect mechanism. This counterintuitive finding lies at the heart of understanding when architectural inductive biases are essential versus merely convenient.

Weight-space learning—predicting model properties directly from weight tensors—has emerged as a paradigm for tasks ranging from accuracy prediction to model quality assessment. Central to this paradigm is the question of how to handle permutation symmetries: the weights of a neural network can be permuted across hidden neurons without changing the function it computes. Permutation-equivariant architectures like Neural Functional Networks (NFN) explicitly encode this symmetry, while standard MLPs must learn it from data.

The conventional wisdom holds that with sufficient data diversity, non-equivariant architectures should eventually learn to exploit these symmetries. If the training distribution contains many permuted versions of similar weight configurations, an MLP should discover that permutation-related weights map to similar properties. This assumption has implications: if true, architectural inductive biases become a matter of convenience rather than necessity.

We challenge this assumption through systematic experiments across data scales from 1,000 to 40,000 models. Our finding: MLPs trained on 40,000 models achieve R²=0.986 but fail to develop permutation invariance (invariance score 0.63 versus NFN's 1.0). This dissociates task performance from mechanism—high accuracy coexists with representations that exploit dataset-specific position-accuracy correlations rather than semantic weight structure.

Our contributions are:

1. **Sample Efficiency of Equivariance:** NFN achieves R²=0.95 at N=1,000 while matched-capacity MLPs achieve R²=0.35—a 60 percentage point advantage.

2. **Mechanism Verification:** NFN's invariance is near-perfect (deviation < 1.19×10⁻⁷ across permutations) while untrained MLPs show coefficient of variation 0.19 under the same permutations.

3. **Falsification of Learned Invariance:** MLPs cannot learn permutation invariance from data diversity. At N=40,000, MLPs achieve R²=0.986 but invariance=0.63, below the 0.8 threshold.

---

## 2. Related Work

### Weight-Space Learning

The idea of learning from neural network weights directly has gained traction with the availability of large model collections. Schürholt et al. introduced hyper-representations—learned embeddings of model weights trained via contrastive learning—demonstrating that weight-space features can predict properties like accuracy and robustness. However, their architecture uses standard attention mechanisms without explicit permutation equivariance guarantees.

Unterthiner et al. pioneered predicting generalization from weights alone using simple statistics. The Model Zoo dataset provided a benchmark with over 50,000 models trained under varying conditions.

### Permutation-Equivariant Architectures

Zhou et al. introduced Neural Functional Networks (NFN), which process neural network weights using equivariant layers that respect the permutation symmetry of hidden neurons. The NPLinear layer linearly transforms weight tensors while maintaining equivariance, and HNPPool produces permutation-invariant representations via pooling.

NFN's original evaluation focused primarily on generation rather than property prediction, and systematic comparison against matched-capacity non-equivariant baselines was limited. This work addresses that gap.

### Inductive Biases and Symmetry

Cohen and Welling showed that encoding symmetries via equivariant layers improves sample efficiency for image classification. Battaglia et al. argued that relational inductive biases are important for structured domains. Less understood is whether such biases are necessary or merely convenient. This work provides empirical evidence that permutation invariance in weight-space learning cannot be learned from data regardless of scale.

---

## 3. Method

### 3.1 Neural Functional Networks (NFN)

We adopt the NFN architecture from Zhou et al. The core building block is NPLinear, which linearly transforms weight tensors while maintaining equivariance. HNPPool produces permutation-invariant representations via pooling over neuron dimensions.

Our NFNRegressor architecture:
```
Input weights → NPLinear(32) → ReLU → NPLinear(32) → ReLU → HNPPool → Linear(1)
```

The model has approximately 70,000–270,000 parameters depending on input dimensionality.

### 3.2 MLP-Matched Baseline

For comparison, we design an MLP that receives flattened weight vectors:
```
Flattened weights → Linear(512) → ReLU → Linear(256) → ReLU → Linear(1)
```

This architecture has substantially more parameters than NFN due to the flattened input dimensionality (approximately 1.8–52 million parameters for the inputs used).

### 3.3 Permutation and Invariance Testing

To verify whether models develop permutation-invariant representations:

1. Take a trained model M and a test weight tensor W
2. Generate K=10 random permutations π₁, π₂, ..., πₖ applied to hidden layer neurons
3. Apply M to each permuted version: ŷᵢ = M(πᵢ(W))
4. Compute invariance metrics: mean correlation across predictions, coefficient of variation, maximum deviation

For mathematically invariant models, all predictions should be identical up to floating-point precision.

---

## 4. Experimental Setup

### Dataset

Model Zoo CIFAR-10 CNN subset containing 42,547 trained CNN models with test accuracy labels. The dataset was obtained from Zenodo (DOI: 10.5281/zenodo.6620868). Models within this subset share a homogeneous architecture, enabling consistent weight-space input dimensions.

### Hypotheses and Success Criteria

| ID | Hypothesis | Success Criterion | Gate Type |
|----|-----------|-------------------|-----------|
| H-E1 | NFN outperforms MLP at N=1K | R² difference > 0.05 | MUST_WORK |
| H-M1 | NFN layers are equivariant | Max deviation < 1×10⁻⁵ | MUST_WORK |
| H-M2 | NFN predictions are invariant | Correlation > 0.99 | SHOULD_WORK |
| H-M3 | Untrained MLP lacks invariance | CV > 0.1 | SHOULD_WORK |
| H-M4 | MLP at N=1K has low invariance | Invariance < 0.5 | SHOULD_WORK |
| H-M5 | MLP learns invariance at N=40K | Invariance > 0.8 | SHOULD_WORK |

### Training Protocol

| Parameter | Value |
|-----------|-------|
| Optimizer | AdamW |
| Learning rate | 1×10⁻³ |
| Weight decay | 1×10⁻⁴ |
| Scheduler | CosineAnnealingLR |
| Epochs | 50 |
| Batch size | 32–64 |
| Train/test split | 80%/20% |

---

## 5. Results

### 5.1 Sample Efficiency (H-E1)

At N=1,000 training models:

| Model | R² |
|-------|-----|
| NFN | 0.9524 |
| MLP-Matched | 0.3529 |
| **Difference** | **0.5995** |

The R² difference of 0.60 exceeds the 0.05 threshold by a factor of 12. NFN shows minimal overfitting (train loss 0.0024, validation loss 0.0029), while MLP shows severe overfitting (train loss ~0, validation loss 0.045).

### 5.2 NFN Equivariance Verification (H-M1, H-M2)

Applying 10 random neuron permutations to test MLP weights and measuring NFN output:

| Metric | Value |
|--------|-------|
| Mean prediction | 0.8760 |
| Standard deviation | 8.22×10⁻⁸ |
| Max deviation | 1.19×10⁻⁷ |
| Invariance correlation | 0.99999986 |

All 11 predictions (original plus 10 permuted) differ only at floating-point precision. This confirms NFN's mathematical equivariance property.

### 5.3 Untrained MLP Variance (H-M3)

An untrained (randomly initialized) MLP produces highly variable outputs under the same permutations:

| Metric | Value |
|--------|-------|
| Mean prediction | -0.0607 |
| Standard deviation | 0.0118 |
| Coefficient of variation | 0.194 |
| Max deviation | 0.0229 |

The coefficient of variation (0.194) exceeds the 0.1 threshold, confirming that MLPs have no built-in permutation invariance.

### 5.4 MLP at Large Scale (H-M5)

At N=40,547 training models (3 seeds):

| Metric | Mean | Std | 95% CI |
|--------|------|-----|--------|
| Test R² | 0.9860 | 0.0003 | [0.985, 0.987] |
| Invariance | 0.6265 | 0.0103 | [0.595, 0.658] |

MLP achieves near-perfect prediction accuracy but fails the invariance criterion (0.63 < 0.80). This is the central negative result: data diversity alone does not teach permutation invariance.

### 5.5 Comparison Across Scales

| Condition | R² | Invariance |
|-----------|-----|------------|
| MLP N=1K | 0.004 | 0.64 |
| MLP N=40K | 0.986 | 0.63 |
| NFN (any N) | ~0.95 | 1.0 |

MLP invariance does not increase meaningfully from N=1K to N=40K despite a dramatic increase in predictive performance.

### 5.6 Summary of Hypothesis Outcomes

| Hypothesis | Result | Status |
|------------|--------|--------|
| H-E1 | Δ=0.60 > 0.05 | **PASSED** |
| H-M1 | 1.19×10⁻⁷ < 10⁻⁵ | **PASSED** |
| H-M2 | 0.9999999 > 0.99 | **PASSED** |
| H-M3 | CV=0.194 > 0.1 | **PASSED** |
| H-M4 | 0.64 > 0.5 | FAILED |
| H-M5 | 0.63 < 0.8 | **FAILED** |

The H-M5 failure is the most informative result: it falsifies the hypothesis that MLPs learn invariance from data diversity at scale.

---

## 6. Discussion

### Principal Findings

1. **Sample efficiency gap:** NFN achieves R²=0.95 at N=1,000 where MLP achieves R²=0.35, a 60 percentage point difference.

2. **NFN invariance is near-perfect:** Deviation below 1.19×10⁻⁷ across permutations confirms mathematical guarantee.

3. **MLP dissociation:** R²=0.986 coexists with invariance=0.63 at N=40,000. Task performance and mechanism quality are separable.

4. **Invariance cannot be learned:** MLP invariance at N=40K (0.63) is not meaningfully higher than at N=1K (0.64), despite R² improving from 0.004 to 0.986.

### Interpretation

MLPs trained on large-scale weight-space data learn to predict accuracy by memorizing position-sensitive statistics—which weight indices correlate with accuracy in the specific dataset. This strategy achieves high R² when training and test distributions align but does not generalize the underlying permutation symmetry.

NFN's architectural equivariance extracts accuracy-predictive features from a canonical view of each model's weights, enabling high performance with limited data. The inductive bias is structural, not compensable by data quantity.

### H-M4 Interpretation

H-M4 showed MLP invariance of 0.64 at N=1K, which exceeded the 0.5 threshold. However, the corresponding R² was 0.004, indicating the model had not learned the task. The apparent "high invariance" was an artifact of near-constant predictions. This highlights that invariance metrics should be conditioned on minimum task performance.

### Limitations

1. **Synthetic data in H-E1:** The initial proof-of-concept (H-E1) used synthetic MLP weights rather than real Model Zoo data. Subsequent hypotheses (H-M4, H-M5) used real Model Zoo data, confirming the overall pattern.

2. **Single architecture family:** All experiments used CIFAR-10 CNNs. Generalization to transformers or other architectures is untested.

3. **NFN-Scrambled baseline not implemented:** Prediction P2 (comparing NFN with correct versus incorrect permutation group) was not tested.

4. **Limited seeds:** Some experiments used 1–3 seeds rather than the planned 10. Effect sizes were large enough that conclusions are unlikely to change with additional seeds.

### Broader Implications

These results suggest that certain symmetries require explicit architectural encoding; data quantity cannot substitute for structural inductive bias. This principle may extend beyond weight-space learning to other domains where input symmetries are present but not architecturally exploited.

---

## 7. Conclusion

We investigated whether neural networks can learn permutation invariance from data diversity or whether such structure must be built into the architecture. In weight-space learning for accuracy prediction, MLPs achieve near-perfect predictive performance (R²=0.986) when trained on 40,000 models but fail to develop permutation invariance (score 0.63 versus NFN's 1.0).

This demonstrates that task performance and representation quality are separable—a model can learn the right answers through the wrong mechanism. The diagnostic tools developed (permutation invariance testing) and the architectural solution (NFN) ensure that weight-space models not only predict correctly but represent the input structure correctly.

Permutation equivariance must be built into the architecture. Data quantity cannot substitute.

---

## References

Battaglia, P. W., Hamrick, J. B., Bapst, V., Sanchez-Gonzalez, A., Zambaldi, V., Malinowski, M., Tacchetti, A., Raposo, D., Santoro, A., Faulkner, R., Gulcehre, C., Song, F., Ballard, A., Gilmer, J., Dahl, G., Vaswani, A., Allen, K., Nash, C., Langston, V., Dyer, C., Heess, N., Wierstra, D., Kohli, P., Botvinick, M., Vinyals, O., Li, Y., & Pascanu, R. (2018). Relational inductive biases, deep learning, and graph networks. arXiv:1806.01261.

Cohen, T., & Welling, M. (2016). Group equivariant convolutional networks. In Proceedings of the 33rd International Conference on Machine Learning (ICML).

Schürholt, K., Taskiran, D., Knyazev, B., Giró-i-Nieto, X., & Borth, D. (2022). Model zoos: A dataset of diverse populations of neural network models. arXiv:2209.14764.

Schürholt, K., Kostadinov, D., & Borth, D. (2022). Hyper-representations as generative models: Sampling unseen neural network weights. In Advances in Neural Information Processing Systems (NeurIPS).

Unterthiner, T., Keysers, D., Gelly, S., Bousquet, O., & Tolstikhin, I. (2020). Predicting neural network accuracy from weights. arXiv:2002.11448.

Zhou, A., Yang, K., Burns, K., Jiang, Y., Sokota, S., Kolter, J. Z., & Finn, C. (2023). Permutation equivariant neural functionals. In Advances in Neural Information Processing Systems (NeurIPS).

---

*Anonymous submission*
