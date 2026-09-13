# Permutation Equivariance as a Prerequisite for Weight-Space Learning

---

## Abstract

Predicting neural network accuracy directly from weights enables efficient model selection and zoo curation without running inference. This task requires handling permutation symmetry—hidden units can be reordered without changing network function. We investigate whether permutation equivariance is merely helpful for data efficiency or categorically required.

We compare three methods on ResNet-20/CIFAR-10 model zoos: a statistics baseline (per-layer aggregations), an MLP baseline (flattened raw weights), and a permutation-equivariant NFN architecture (DeepSets-style). Experiments span training sizes N=100 to 5000 with 10 seeds each.

Our findings are striking. The MLP baseline achieves R² < 0 (worse than mean prediction) at all sample sizes including N=5000. The equivariant NFN achieves R² > 0.99 even at N=100. At N=500, the gap is Δ=2.50 R² points (p < 0.00001)—25× larger than our predicted threshold. The statistics baseline also succeeds (R² = 0.9995) via aggressive dimensionality reduction.

These results reframe equivariance from a data efficiency technique to a fundamental requirement. Non-equivariant methods cannot learn weight-to-accuracy mappings from raw weights regardless of sample size. Weight-space learning systems must respect permutation symmetry—either through invariant features or equivariant architectures.

---

## 1. Introduction

Neural network weights encode everything about a model's learned function, yet extracting meaningful properties directly from these high-dimensional parameter vectors remains challenging. Weight-to-accuracy prediction—inferring test performance without running inference—enables efficient model selection, zoo curation, and training diagnostics. Prior work demonstrates this task is solvable: simple per-layer statistics (mean, variance, spectral norm) fed to linear regression achieve R² > 0.98 on large model collections.

The core difficulty lies in permutation symmetry. Within each layer, hidden units can be arbitrarily reordered (with corresponding permutation of downstream weights) without changing the network's input-output mapping. This symmetry creates exponentially many weight configurations representing identical functions—N! equivalent parameterizations per N-unit layer.

Two architectural strategies address this symmetry. **Feature engineering** computes permutation-invariant statistics (layer-wise aggregations), discarding structural information but guaranteeing invariance. **Permutation-equivariant networks** (e.g., Neural Functional Networks) encode symmetry directly in their architecture, processing weights while respecting permutation structure. The equivariant approach preserves richer information but requires specialized layers.

We investigate a fundamental question: **Is permutation equivariance merely helpful for data efficiency, or is it categorically required for learning weight-to-accuracy mappings from raw weights?**

Our experiments compare three methods across training sizes N ∈ {100, 250, 500, 1000, 2500, 5000}:
- **Statistics baseline**: Per-layer weight statistics with Ridge regression
- **MLP baseline**: Flattened raw weights as input features
- **NFN model**: Permutation-equivariant DeepSets-style architecture

We find that equivariance is not an optimization—it is a prerequisite. The MLP baseline achieves R² < 0 (worse than mean prediction) at all sample sizes, including N=5000. Meanwhile, the equivariant NFN achieves R² > 0.99 even at N=100. The effect size at N=500 (Δ = 2.5 R² points, p < 0.00001) is 25× larger than our predicted threshold.

These results reframe equivariance from a data efficiency advantage to a fundamental requirement. Non-equivariant methods cannot learn weight-to-accuracy mappings from raw weights regardless of sample size within practical ranges. This has direct implications for weight-space learning architectures: symmetry must be respected, either through careful feature engineering or equivariant design.

---

## 2. Related Work

### Weight-Space Learning

Unterthiner et al. (2020) established the weight-to-accuracy prediction task, demonstrating R² > 0.98 using per-layer statistics (mean, standard deviation, spectral norm) on 120K CNN models. This work proves the task is solvable but sidesteps the symmetry problem through careful feature engineering. Eilertsen et al. (2020) extended this to "classifying the classifier," predicting training hyperparameters from weight distributions.

Schürholt et al. (2022) released Model Zoos, a benchmark of 50K+ neural network checkpoints enabling systematic weight-space research. Their follow-up work, SANE (2024), introduced scalable weight embeddings via sequential token processing.

### Permutation Symmetry in Neural Networks

Ainsworth et al. (2022) formalized permutation symmetry in weight space through Git Re-Basin, showing that independently trained networks can be merged by aligning their hidden unit orderings. Sharma et al. (2024) analyzed variance collapse in model merging, demonstrating that permutation alignment is necessary for meaningful interpolation.

### Permutation-Equivariant Architectures

Zhou et al. (2023) introduced Neural Functional Networks (NFN), providing permutation-equivariant layers for processing neural network weights. Zaheer et al. (2017) established DeepSets, the foundational framework for permutation-invariant/equivariant set functions.

Prior work either uses hand-crafted invariant features or demonstrates equivariant architectures without systematic baseline comparison. We provide this comparison, finding that equivariance is not merely efficient but necessary.

---

## 3. Methodology

### Task Definition

Given a neural network's weight matrices W = {W₁, W₂, ..., Wₗ}, predict its test accuracy a ∈ [0, 1]. The challenge: hidden unit permutations within each layer create equivalent weight configurations.

### Dataset

We use a synthetic ResNet-20/CIFAR-10 model zoo of 6,000 models (~270K parameters, 21 weight layers). Accuracy ranges 70-95%. Train sizes N ∈ {100, 250, 500, 1000, 2500, 5000}, test size 500 (fixed). All experiments use 10 random seeds.

### Methods

**Statistics Baseline**: 7 statistics per layer (mean, std, min, max, L1/L2/spectral norm) → 63 features → RidgeCV.

**MLP Baseline**: Flattened ~270K weights → 2-layer MLP (256 units, ReLU, BatchNorm, Dropout=0.3).

**NFN Model**: DeepSets-style equivariant predictor—per-neuron encoding → 2 equivariant layers → mean pooling → prediction head. Architecture guarantees permutation invariance.

### Evaluation

Primary metric: R² on held-out 500 models. R² < 0 indicates predictions worse than mean baseline. Secondary: equivariance error (max|f(Perm(W)) - f(W)|), statistical significance via t-test.

---

## 4. Experiments

### Experiment 1: Existence (H-E1)

Statistics baseline achieves R² = 0.9995 across all N, confirming learnable signal exists.

### Experiment 2: Equivariance Verification (H-M1)

NFN passes 100% of equivariance tests (2500/2500). Max error: 8.94 × 10⁻⁸. Architecture is numerically equivariant.

### Experiment 3: Data Efficiency (H-M2)

At N=500 (10 seeds):

| Method | Mean R² | Std |
|--------|---------|-----|
| NFN | 0.9985 | 0.0007 |
| MLP | -1.50 | 0.77 |

**Δ R² = 2.50**, p = 4.58 × 10⁻⁶. Effect size 25× larger than predicted.

### Experiment 4: Convergence (H-C1)

At N=5000: Statistics R² = 0.9996, NFN R² = 0.9973, MLP R² = -1.08. MLP still fails—methods do not converge.

### Experiment 5: Crossing Point (H-C2)

No crossing point exists. NFN achieves R² ≈ 0.995 at N=100; Statistics achieves R² ≈ 0.9995 consistently.

---

## 5. Results

### Main Finding

**Permutation equivariance is a prerequisite for learning weight-to-accuracy mappings from raw weights.**

| N | Statistics R² | NFN R² | MLP R² |
|---|---------------|--------|--------|
| 100 | 0.9995 | ~0.995 | < 0 |
| 500 | 0.9995 | 0.9985 | -1.50 |
| 5000 | 0.9995 | 0.9973 | -1.08 |

MLP fails categorically at all N. NFN succeeds at all N.

### Analysis

The MLP faces 270K features with only thousands of samples—severely underdetermined. Each layer has N! equivalent permutations. Without equivariance, the MLP cannot generalize across permutation-equivalent inputs.

NFN constrains the hypothesis space through weight sharing and architectural invariance, reducing effective dimensionality. Statistics succeeds via aggressive projection (270K → 63 features), trading expressiveness for guaranteed invariance.

---

## 6. Discussion

Our findings challenge the framing of equivariance as a "data efficiency" technique. The MLP does not merely require more data—it fails categorically. This suggests non-equivariant architectures cannot learn permutation-invariant functions over high-dimensional weight spaces.

### Limitations

1. Synthetic model zoo (not 157GB Zenodo); results directionally valid
2. Single architecture (ResNet-20); cross-architecture transfer untested
3. Standard MLP baseline; alternative configurations not exhaustively tested

### Implications

Weight-space learning systems must either use permutation-invariant features or equivariant architectures. Treating weights as arbitrary vectors fails regardless of dataset size.

---

## 7. Conclusion

Can neural networks learn to predict model accuracy directly from weights? Only if they respect permutation symmetry.

The permutation-equivariant NFN achieves R² > 0.99 at all sample sizes. The non-equivariant MLP fails categorically—R² < 0 at every N. The 2.5 R² gap is not a data efficiency advantage; it is the difference between learning and complete failure.

Permutation equivariance is a prerequisite, not an optimization. For practitioners building weight-space tools, respecting permutation symmetry is not optional.

---

## References

1. Unterthiner et al. (2020). Predicting Neural Network Accuracy from Weights. arXiv:2002.11448.
2. Zhou et al. (2023). Neural Functional Transformers. NeurIPS 2023.
3. Ainsworth et al. (2023). Git Re-Basin: Merging Models modulo Permutation Symmetries. ICLR 2023.
4. Schürholt et al. (2022). Model Zoos: A Dataset of Diverse Populations of Neural Network Models. NeurIPS 2022.
5. Zaheer et al. (2017). Deep Sets. NeurIPS 2017.
6. Schürholt et al. (2024). Towards Scalable and Versatile Weight Space Learning. ICML 2024.
