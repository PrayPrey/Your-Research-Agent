# Emergence Uniformity Cannot Distinguish Spurious Features on Frozen Pretrained Representations

**Anonymous Authors**

---

## Abstract

This work investigates whether the coefficient of variation (CV) of linear probe accuracy trajectories can distinguish spurious from core features in pretrained representations. The hypothesis posits that spurious features emerge uniformly across sample subsets (low CV) while core features emerge differentially (high CV). Experiments on the Waterbirds dataset using frozen CLIP ViT-B/16 features yield AUC = 0.0 for CV-based classification of spurious versus core features. Both background (spurious) and bird type (core) features exhibit nearly identical CV values (0.0393 and 0.0360, respectively), providing no discriminative signal. The failure stems from feature saturation: the pretrained model has already learned both concepts, eliminating emergence dynamics. Linear probes converge immediately at all regularization strengths, producing flat trajectories. This negative result clarifies that emergence uniformity is a training-time phenomenon that cannot be recovered from frozen pretrained features and motivates future work toward training-time measurement with unfrozen representations.

---

## 1. Introduction

Spurious correlations cause deep neural networks to rely on dataset biases rather than causal features. On the Waterbirds benchmark, models exploit the 95% correlation between background type (water/land) and bird label, achieving approximately 95% average accuracy while failing on the worst group (waterbirds on land backgrounds) with substantially lower accuracy. Mitigating spurious correlation reliance without group annotations remains an open problem.

Existing methods such as Group DRO (Sagawa et al., 2020) require group annotations during training. Two-stage approaches including Just Train Twice (Liu et al., 2021) and Learning from Failure (Nam et al., 2020) exploit early-training signals to identify minority groups without annotations but introduce computational overhead and hyperparameter sensitivity.

This work tests a hypothesis derived from simplicity bias literature: that spurious features, being simpler, emerge not only earlier but also more uniformly across training samples than core features. Specifically, the coefficient of variation (CV) of probe accuracy improvement rates across random sample subsets should be lower for spurious features than for core features. If validated, this signal could enable single-run, annotation-free spurious feature detection.

The hypothesis was tested by training logistic regression probes on frozen CLIP ViT-B/16 features extracted from Waterbirds images. Regularization strength (C) was swept as a proxy for training progression. CV was computed across five random 20% subsets of training data.

The main finding is negative: CV-based detection achieves AUC = 0.0 on Waterbirds. Both feature types show nearly identical CV values (~0.04), with the direction marginally reversed from the hypothesis (CV of spurious features slightly higher than CV of core features). The root cause is feature saturation in pretrained models—CLIP has already learned both background and bird type concepts, eliminating any emergence dynamics that probing could detect.

### Contributions

1. A negative result with clear attribution: CV-based spurious detection fails on frozen pretrained features, achieving AUC = 0.0 on Waterbirds with CLIP ViT-B/16.

2. Mechanistic explanation: Feature saturation in pretrained models eliminates emergence dynamics; probes converge immediately regardless of regularization strength.

3. Methodological clarification: Emergence-based detection requires training-time measurement, not post-hoc probing on frozen representations.

---

## 2. Related Work

### 2.1 Spurious Correlations and Group Robustness

Sagawa et al. (2020) introduced Group DRO, which minimizes worst-case loss over predefined groups with strong regularization, achieving substantial improvements on Waterbirds and CelebA benchmarks. However, Group DRO requires group annotations during training.

Just Train Twice (Liu et al., 2021) trains an initial ERM model for few epochs, identifies misclassified examples (which correlate with minority groups), and upweights them in a second training run. Learning from Failure (Nam et al., 2020) explicitly trains a biased network and uses its failures to guide debiasing. Both methods exploit the observation that spurious features are learned early but require two-stage training.

Deep Feature Reweighting (Kirichenko et al., 2022) demonstrates that pretrained ERM features are sufficient for strong worst-group accuracy when the last layer is retrained on group-balanced data. This finding directly relates to the present negative result: if pretrained features already separate spurious and core concepts, there may be no emergence dynamics left to observe.

### 2.2 Simplicity Bias and Learning Dynamics

Shah et al. (2020) established that SGD exhibits simplicity bias: networks learn the simplest predictive features first and may never learn more complex features even when they have higher predictive power. Gradient Starvation (Pezeshki et al., 2021) provides a dynamical systems perspective: cross-entropy minimization on features with different frequencies causes some features to receive diminishing gradient signal.

The present work extends this literature by testing whether emergence uniformity (variance across sample subsets) differs between spurious and core features. The negative result suggests that while emergence timing may differ during training, this signal is not recoverable from pretrained representations.

### 2.3 Linear Probing for Representation Analysis

Linear probes are standard tools for analyzing pretrained representations (Alain & Bengio, 2017). The CLIP evaluation protocol (Radford et al., 2021) uses logistic regression with regularization-strength sweeps to assess representation quality.

The present experiment adapted this protocol by treating regularization strength (C) as an epoch proxy and computing CV across sample subsets. The failure reveals a category error: C-sweep produces representation quality scores, not learning trajectory data. Convex optimization converges in a single pass regardless of C; there is no emergence to measure.

---

## 3. Method

### 3.1 Hypothesis

The hypothesis under test (H-E1) states: the coefficient of variation (CV) of linear probe accuracy trajectories can distinguish spurious from core features with AUC ≥ 0.75.

The underlying reasoning: spurious features, being simpler and correlating with labels regardless of subgroup, should be learned uniformly across sample subsets (low CV). Core features, relevant to specific subgroups, should emerge differentially (high CV).

### 3.2 Feature Extraction

CLIP ViT-B/16 (Radford et al., 2021) served as the feature extractor. For each Waterbirds image, the 512-dimensional embedding from the final layer was extracted and L2-normalized. Features were cached to disk for reproducibility.

### 3.3 CV Measurement Protocol

For each concept (background and bird type), logistic regression probes were trained with regularization strength C ∈ {0.001, 0.01, 0.1, 1, 10, 100}. The solver was L-BFGS with a maximum of 1000 iterations.

To measure emergence uniformity, probes were trained on 5 random 20% subsets of training data (seed = 42). For each concept:

1. Train probes on each subset across all C values
2. Record accuracy at each (subset, C) combination
3. Compute improvement rate: accuracy at maximum C minus accuracy at minimum C
4. Calculate CV of improvement rates across subsets: CV = std(rates) / mean(rates)

### 3.4 Evaluation

Waterbirds provides ground truth: background is the spurious feature (95% correlated with label) and bird type is the core feature. Binary classification was evaluated using ROC-AUC, with the gate criterion set at AUC ≥ 0.75.

### 3.5 Experimental Configuration

| Parameter | Value |
|-----------|-------|
| Dataset | Waterbirds (train split) |
| Train samples | 4,795 |
| Feature extractor | CLIP ViT-B/16 (frozen) |
| Embedding dimension | 512 |
| Probe | Logistic Regression (L-BFGS) |
| C sweep | [0.001, 0.01, 0.1, 1, 10, 100] |
| Number of subsets | 5 |
| Subset fraction | 20% |
| Random seed | 42 |
| Gate threshold | AUC ≥ 0.75 |

---

## 4. Experimental Setup

### 4.1 Dataset

Waterbirds (Sagawa et al., 2020) is a standard spurious correlation benchmark. The training split contains 4,795 samples with a 95% correlation between background type (water/land) and bird label (waterbird/landbird). Four groups exist: landbird-land (majority), landbird-water (minority), waterbird-water (majority), and waterbird-land (minority).

### 4.2 Research Questions

1. Does CV distinguish spurious from core feature types?
2. What classification performance does CV achieve (measured by AUC)?
3. Are probe accuracy trajectories informative for emergence dynamics?

---

## 5. Results

### 5.1 Main Finding

The CV-based detection mechanism achieves AUC = 0.0, decisively failing the ≥ 0.75 gate.

### 5.2 CV Values

| Feature Type | CV Value | Expected Direction |
|--------------|----------|-------------------|
| Background (spurious) | 0.0393 | Low (< 0.15) |
| Bird Type (core) | 0.0360 | High (> 0.20) |
| Difference | 0.0033 | — |

Both feature types exhibit nearly identical CV values (~0.04). The hypothesized separation does not manifest.

### 5.3 Direction Reversal

The hypothesis predicted CV(spurious) < CV(core). The observed values show CV(spurious) = 0.0393 > CV(core) = 0.0360, a marginal reversal of the expected direction. With only two feature types, this reversal yields AUC = 0.0.

### 5.4 Gate Evaluation

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| AUC | 0.0 | ≥ 0.75 | FAIL |
| Best F1 | 0.667 | — | — |

### 5.5 Probe Trajectory Analysis

Both background and bird type probes show flat trajectories across the C sweep. Accuracy is near 100% at all regularization strengths for both feature types. There is no observable emergence pattern—features are already fully learned in the CLIP representation.

---

## 6. Discussion

### 6.1 Root Cause Analysis

The hypothesis failure has a clear mechanistic explanation: feature saturation in pretrained models.

CLIP ViT-B/16 was trained on approximately 400 million image-text pairs. Both background (land/water) and bird type are elementary visual concepts well within CLIP's training distribution. Consequently:

1. No emergence dynamics exist to measure
2. Linear probes converge immediately regardless of regularization strength
3. CV captures only sampling noise, not differential learning

### 6.2 Theoretical Interpretation

The negative result clarifies a distinction between two phenomena:

- **Feature emergence**: A training-time phenomenon occurring as a model learns representations
- **Feature separability**: A property of the final representation

C-sweep probing on frozen features measures separability, not emergence. The hypothesis conflated these by assuming that regularization strength (C) in convex optimization would serve as a proxy for training epochs in non-convex neural network optimization.

### 6.3 Limitations

1. **Single hypothesis tested**: Only the existence hypothesis (H-E1) was evaluated. The proposed intervention mechanism (gradient regularization based on CV) remains untested.

2. **Single dataset and extractor**: Results are from Waterbirds with CLIP ViT-B/16. Other datasets (CelebA, ColoredMNIST) and feature extractors (DINOv2, ImageNet-pretrained ResNet) were not evaluated.

3. **C-sweep as epoch proxy**: Using regularization strength as an epoch proxy may fundamentally fail to capture learning dynamics. Convex optimization does not exhibit the staged learning that neural network training does.

4. **Two-sample AUC limitation**: With only two feature types (background and bird type), AUC is binary (0 or 1). Marginal CV differences combined with directional reversal yield the worst possible AUC.

### 6.4 Implications for Future Work

The negative result identifies necessary conditions for emergence-based detection to succeed:

1. **Training-time measurement**: CV must be computed during model training, not on frozen pretrained representations

2. **Unfrozen representations**: The model must be learning features during the measurement period

3. **Alternative signals**: Loss curves, gradient norms, or other training-time metrics may provide emergence signals that post-hoc probing cannot

---

## 7. Conclusion

This work tested whether coefficient of variation (CV) of linear probe accuracy trajectories on frozen CLIP features could distinguish spurious from core features. The hypothesis was decisively refuted: AUC = 0.0 on Waterbirds, with both feature types showing nearly identical CV values (~0.04).

The root cause is feature saturation in pretrained models. CLIP has already learned both background and bird type concepts. There are no emergence dynamics to measure—probes converge immediately at all regularization strengths.

The key insight is that emergence uniformity is a training-time phenomenon that cannot be recovered from frozen pretrained representations. The analogy: one cannot measure how fast someone learned by examining their final exam score.

If emergence uniformity proves measurable during training with unfrozen representations, it could still enable single-run, annotation-free spurious correlation mitigation. Future work should focus on training-time CV measurement, intermediate layer probing during training, and loss-based emergence signals.

---

## References

Alain, G., & Bengio, Y. (2017). Understanding intermediate layers using linear classifier probes. arXiv preprint arXiv:1610.01644.

Idrissi, B. Y., Arjovsky, M., Pezeshki, M., & Lopez-Paz, D. (2022). Simple data balancing achieves competitive worst-group-accuracy. In Conference on Causal Learning and Reasoning (pp. 336–351). PMLR.

Kirichenko, P., Izmailov, P., & Wilson, A. G. (2022). Last layer re-training is sufficient for robustness to spurious correlations. In International Conference on Machine Learning (pp. 11184–11203). PMLR.

Liu, E. Z., Haghgoo, B., Chen, A. S., Raghunathan, A., Koh, P. W., Sagawa, S., Liang, P., & Finn, C. (2021). Just train twice: Improving group robustness without training group information. In International Conference on Machine Learning (pp. 6781–6792). PMLR.

Nam, J., Cha, H., Ahn, S., Lee, J., & Shin, J. (2020). Learning from failure: De-biasing classifier from biased classifier. In Advances in Neural Information Processing Systems (Vol. 33, pp. 20673–20684).

Pezeshki, M., Kaba, O., Bengio, Y., Courville, A., Precup, D., & Lajoie, G. (2021). Gradient starvation: A learning proclivity in neural networks. In Advances in Neural Information Processing Systems (Vol. 34, pp. 1256–1272).

Radford, A., Kim, J. W., Hallacy, C., Ramesh, A., Goh, G., Agarwal, S., Sastry, G., Askell, A., Mishkin, P., Clark, J., et al. (2021). Learning transferable visual models from natural language supervision. In International Conference on Machine Learning (pp. 8748–8763). PMLR.

Sagawa, S., Koh, P. W., Hashimoto, T. B., & Liang, P. (2020). Distributionally robust neural networks for group shifts: On the importance of regularization for worst-case generalization. In International Conference on Learning Representations.

Shah, H., Tamuly, K., Raghunathan, A., Jain, P., & Netrapalli, P. (2020). The pitfalls of simplicity bias in neural networks. In Advances in Neural Information Processing Systems (Vol. 33, pp. 9573–9585).
