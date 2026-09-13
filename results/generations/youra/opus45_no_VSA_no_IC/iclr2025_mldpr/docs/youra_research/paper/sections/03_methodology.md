# Methodology

## Problem Formulation

We frame benchmark fingerprint detection as a representation classification problem. Given a set of models fine-tuned on different benchmarks, can we predict which benchmark was used from the model's representations alone?

Let $\mathcal{M} = \{m_1, m_2, \ldots, m_n\}$ be a set of models, each fine-tuned from the same pretrained backbone on one of $k$ benchmarks $\mathcal{B} = \{b_1, b_2, \ldots, b_k\}$. For each model $m_i$, we extract representations $\mathbf{r}_i \in \mathbb{R}^d$ from the penultimate layer (avgpool) when processing images from a held-out probe dataset. A fingerprint exists if the training benchmark can be predicted from these representations with above-chance accuracy.

## Feature Extraction

We use ResNet-50 pretrained on ImageNet-1K as the base architecture (He et al., 2016). For each benchmark condition, we fine-tune the model using standard transfer learning:

- **Optimizer:** SGD with momentum 0.9
- **Learning rate:** 0.01 with cosine annealing
- **Epochs:** 10 (proof-of-concept) / 30 (full experiment)
- **Batch size:** 32

After fine-tuning, we extract 2048-dimensional features from the average pooling layer for all images in the probe dataset. This layer captures high-level semantic information while preserving fine-tuning effects.

## Fingerprint Detection

We train a logistic regression classifier to predict benchmark origin from extracted features:

$$\hat{y} = \text{argmax}_b \, P(b \mid \mathbf{r}) = \text{argmax}_b \, \sigma(\mathbf{W}_b^T \mathbf{r} + c_b)$$

where $\mathbf{W} \in \mathbb{R}^{d \times k}$ and $\mathbf{c} \in \mathbb{R}^k$ are learned parameters. We use 80/20 model-level cross-validation (training on some models, testing on held-out models from the same benchmarks) to ensure the classifier generalizes to unseen fine-tuning runs.

**Rationale:** Linear classifiers are interpretable and cannot memorize model-specific patterns. If fingerprints are systematic, linear separation should suffice; if linear probing fails, fingerprints may be more subtle or nonexistent.

## Benchmark Fingerprint Score (BFS)

For each model, we compute the BFS as the classifier's confidence for the correct benchmark:

$$\text{BFS}(m_i) = P(b^* \mid \mathbf{r}_i)$$

where $b^*$ is the true training benchmark. BFS ranges from $1/k$ (chance) to 1 (perfect confidence). We hypothesize that higher BFS indicates stronger benchmark-specific encoding, which should correlate with larger cross-dataset generalization gaps.

## Cross-Dataset Evaluation

To measure generalization gap, we evaluate each fine-tuned model on both its training benchmark (in-domain) and a cross-benchmark dataset (out-of-domain). For the proof-of-concept:

- Models fine-tuned on CIFAR-100 are evaluated on Flowers102
- Models fine-tuned on Flowers102 are evaluated on CIFAR-100

Gap is computed as: $\text{Gap} = \text{Acc}_{\text{in-domain}} - \text{Acc}_{\text{cross-domain}}$

## Statistical Analysis

### Fingerprint Detection
- **Primary metric:** Classification accuracy
- **Threshold:** > 60% (for $k=5$ benchmarks, chance = 20%)
- **Significance:** Bootstrap 95% CI, one-sample t-test against chance
- **Effect size:** Cohen's d

### BFS-Gap Correlation
- **Metric:** Pearson correlation coefficient
- **Threshold:** r > 0.3, p < 0.05
- **Sample size:** All fine-tuned models (minimum n=6)

### Baselines
1. **Shuffled labels:** Shuffle benchmark labels to verify signal is real
2. **Random features:** Replace representations with random vectors

## Experimental Scope

This proof-of-concept study uses 2 benchmarks (Flowers102, CIFAR-100) with 3 seeds each, yielding 6 models. The full experiment plan includes 5 fine-grained benchmarks (CUB-200, Stanford Dogs, Flowers102, Stanford Cars, FGVC Aircraft) evaluated on held-out NABirds. The reduced scope maintains statistical validity while limiting compute requirements.
